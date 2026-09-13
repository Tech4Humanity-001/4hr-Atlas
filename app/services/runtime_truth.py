from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.runtime import RuntimeEvent

STATES = {"INTENDED", "ACCEPTED", "STARTED", "EXECUTING", "PARTIAL", "VALIDATING", "REAL", "DEGRADED", "BLOCKED", "QUARANTINED", "RECOVERING"}
TRANSITIONS = {
    "INTENDED": {"ACCEPTED", "BLOCKED", "QUARANTINED"},
    "ACCEPTED": {"STARTED", "BLOCKED", "QUARANTINED"},
    "STARTED": {"EXECUTING", "PARTIAL", "BLOCKED", "QUARANTINED"},
    "EXECUTING": {"PARTIAL", "VALIDATING", "BLOCKED", "QUARANTINED"},
    "PARTIAL": {"VALIDATING", "RECOVERING", "BLOCKED", "QUARANTINED"},
    "VALIDATING": {"REAL", "PARTIAL", "DEGRADED", "QUARANTINED"},
    "REAL": {"DEGRADED", "RECOVERING"},
    "DEGRADED": {"RECOVERING", "QUARANTINED"},
    "BLOCKED": {"RECOVERING", "QUARANTINED"},
    "RECOVERING": {"STARTED", "EXECUTING", "BLOCKED", "QUARANTINED"},
    "QUARANTINED": {"RECOVERING"},
}
AUTHORIZED_EVENTS = {"ACCEPT", "VALIDATE", "OUTCOME", "RECOVER", "QUARANTINE"}


def _canonical(data: dict) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), default=str)


def _hash_event(previous_hash: str | None, data: dict) -> str:
    return hashlib.sha256(((previous_hash or "") + _canonical(data)).encode()).hexdigest()


def _last(db: Session, intent_id: str) -> RuntimeEvent | None:
    return db.scalar(select(RuntimeEvent).where(RuntimeEvent.intent_id == intent_id).order_by(RuntimeEvent.id.desc()).limit(1))


def append_event(db: Session, *, intent_id: str, actor_id: str, runtime_id: str, event: str, state_after: str,
                 model_id: str | None = None, authority_ref: str | None = None, evidence_refs: list | None = None,
                 provenance: dict | None = None, payload: dict | None = None, claim: str | None = None,
                 parent_receipt: str | None = None, state_before: str | None = None) -> RuntimeEvent:
    if state_after not in STATES:
        raise ValueError(f"Unknown state: {state_after}")
    if event not in {"INTENT", "ACCEPT", "START", "EXECUTE", "EVIDENCE", "VALIDATE", "OUTCOME", "RECOVER", "CLAIM", "BLOCK", "QUARANTINE", "TELEMETRY"}:
        raise ValueError(f"Unknown event: {event}")
    if event in AUTHORIZED_EVENTS and not authority_ref:
        raise ValueError(f"Authority required for event: {event}")
    previous = _last(db, intent_id)
    before = state_before if state_before is not None else (previous.state_after if previous else None)
    if before and state_after != before and state_after not in TRANSITIONS.get(before, set()):
        raise ValueError(f"Invalid transition {before} -> {state_after}")
    if before is None and event != "INTENT":
        raise ValueError("First event must be INTENT")
    if previous and previous.payload.get("owner") and previous.payload.get("owner") != actor_id:
        raise ValueError("Actor is not the current intent owner")
    event_payload = dict(payload or {})
    if event == "INTENT":
        event_payload.setdefault("owner", actor_id)
    owner = event_payload.get("owner") or (previous.payload.get("owner") if previous else actor_id)
    if owner != actor_id and event != "TELEMETRY":
        raise ValueError("Actor does not match intent owner")
    receipt_id = uuid4().hex
    event_id = uuid4().hex
    timestamp = datetime.now(timezone.utc)
    body = {"event_id": event_id, "intent_id": intent_id, "receipt_id": receipt_id, "actor_id": actor_id,
            "runtime_id": runtime_id, "model_id": model_id, "event": event, "state_before": before,
            "state_after": state_after, "timestamp": timestamp.isoformat(), "authority_ref": authority_ref,
            "parent_receipt": parent_receipt, "evidence_refs": evidence_refs or [], "provenance": provenance or {},
            "payload": event_payload, "replayable": True, "claim": claim}
    event_hash = _hash_event(previous.event_hash if previous else None, body)
    row = RuntimeEvent(event_id=event_id, intent_id=intent_id, receipt_id=receipt_id, actor_id=actor_id,
        runtime_id=runtime_id, model_id=model_id, event=event, state_before=before, state_after=state_after,
        timestamp=timestamp, authority_ref=authority_ref, parent_receipt=parent_receipt,
        evidence_refs=evidence_refs or [], provenance=provenance or {}, payload=event_payload, replayable=True,
        previous_hash=previous.event_hash if previous else None, event_hash=event_hash, claim=claim)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def create_intent(db: Session, *, actor_id: str, runtime_id: str, intent_id: str | None = None, model_id: str | None = None,
                  authority_ref: str | None = None, payload: dict | None = None) -> RuntimeEvent:
    return append_event(db, intent_id=intent_id or uuid4().hex, actor_id=actor_id, runtime_id=runtime_id,
                         model_id=model_id, authority_ref=authority_ref, event="INTENT", state_after="INTENDED", payload=payload)


def record_evidence(db: Session, *, intent_id: str, actor_id: str, runtime_id: str, evidence_refs: list,
                    payload: dict | None = None) -> RuntimeEvent:
    current = _last(db, intent_id)
    if not current:
        raise ValueError("Unknown intent")
    return append_event(db, intent_id=intent_id, actor_id=actor_id, runtime_id=runtime_id, event="EVIDENCE",
                        state_after="VALIDATING", state_before=current.state_after, evidence_refs=evidence_refs, payload=payload)


def validate(db: Session, *, intent_id: str, actor_id: str, runtime_id: str, valid: bool, evidence_refs: list | None = None,
             validation: dict | None = None, authority_ref: str | None = None) -> RuntimeEvent:
    current = _last(db, intent_id)
    if not current:
        raise ValueError("Unknown intent")
    return append_event(db, intent_id=intent_id, actor_id=actor_id, runtime_id=runtime_id, event="VALIDATE",
                        state_after="REAL" if valid else "PARTIAL", authority_ref=authority_ref,
                        evidence_refs=evidence_refs or current.evidence_refs, payload=validation or {"valid": valid})


def recover(db: Session, *, intent_id: str, actor_id: str, runtime_id: str, authority_ref: str | None = None,
            payload: dict | None = None) -> RuntimeEvent:
    current = _last(db, intent_id)
    if not current:
        raise ValueError("Unknown intent")
    return append_event(db, intent_id=intent_id, actor_id=actor_id, runtime_id=runtime_id, event="RECOVER",
                        state_after="RECOVERING", authority_ref=authority_ref, payload=payload,
                        parent_receipt=current.receipt_id)


def replay(db: Session, intent_id: str) -> dict:
    events = list(db.scalars(select(RuntimeEvent).where(RuntimeEvent.intent_id == intent_id).order_by(RuntimeEvent.id)))
    if not events:
        raise ValueError("Unknown intent")
    state = events[0].state_after
    for event in events[1:]:
        if event.state_before != state:
            raise ValueError("Ledger replay failed: state discontinuity")
        state = event.state_after
    return {"intent_id": intent_id, "state": state, "event_count": len(events), "receipts": [e.receipt_id for e in events]}


def verify_ledger(db: Session, intent_id: str) -> bool:
    events = list(db.scalars(select(RuntimeEvent).where(RuntimeEvent.intent_id == intent_id).order_by(RuntimeEvent.id)))
    previous = None
    for e in events:
        body = {"event_id": e.event_id, "intent_id": e.intent_id, "receipt_id": e.receipt_id, "actor_id": e.actor_id,
                "runtime_id": e.runtime_id, "model_id": e.model_id, "event": e.event, "state_before": e.state_before,
                "state_after": e.state_after, "timestamp": e.timestamp.isoformat(), "authority_ref": e.authority_ref,
                "parent_receipt": e.parent_receipt, "evidence_refs": e.evidence_refs or [], "provenance": e.provenance or {},
                "payload": e.payload or {}, "replayable": e.replayable, "claim": e.claim}
        if e.previous_hash != previous or e.event_hash != _hash_event(previous, body):
            return False
        previous = e.event_hash
    return True
