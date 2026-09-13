from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.models.runtime import RuntimeEvent
from app.services.runtime_truth import append_event, create_intent, record_evidence, recover, replay, validate, verify_ledger


def session():
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, future=True)()


def test_identity_authority_ownership():
    db = session()
    e = create_intent(db, actor_id="a", runtime_id="r", authority_ref="auth", payload={"owner": "a"})
    assert e.intent_id and e.actor_id == "a" and e.authority_ref == "auth"


def test_receipt_evidence_validation_claim_outcome_telemetry():
    db = session()
    e = create_intent(db, actor_id="a", runtime_id="r")
    append_event(db, intent_id=e.intent_id, actor_id="a", runtime_id="r", event="ACCEPT", state_after="ACCEPTED")
    append_event(db, intent_id=e.intent_id, actor_id="a", runtime_id="r", event="START", state_after="STARTED")
    append_event(db, intent_id=e.intent_id, actor_id="a", runtime_id="r", event="EXECUTE", state_after="EXECUTING", claim="done")
    ev = record_evidence(db, intent_id=e.intent_id, actor_id="a", runtime_id="r", evidence_refs=["test://receipt"])
    assert ev.evidence_refs == ["test://receipt"]
    out = validate(db, intent_id=e.intent_id, actor_id="a", runtime_id="r", valid=True, evidence_refs=["test://receipt"])
    assert out.state_after == "REAL"
    telemetry = append_event(db, intent_id=e.intent_id, actor_id="a", runtime_id="r", event="TELEMETRY", state_after="DEGRADED", payload={"latency_ms": 1})
    assert telemetry.payload["latency_ms"] == 1


def test_ledger_and_projection():
    db = session()
    e = create_intent(db, actor_id="a", runtime_id="r")
    append_event(db, intent_id=e.intent_id, actor_id="a", runtime_id="r", event="ACCEPT", state_after="ACCEPTED")
    assert verify_ledger(db, e.intent_id)
    assert replay(db, e.intent_id)["state"] == "ACCEPTED"


def test_recovery_preserves_history_and_replays():
    db = session()
    e = create_intent(db, actor_id="a", runtime_id="r")
    append_event(db, intent_id=e.intent_id, actor_id="a", runtime_id="r", event="BLOCK", state_after="BLOCKED")
    old = list(db.scalars(select(RuntimeEvent).where(RuntimeEvent.intent_id == e.intent_id)))
    rec = recover(db, intent_id=e.intent_id, actor_id="a", runtime_id="r", authority_ref="recovery")
    now = list(db.scalars(select(RuntimeEvent).where(RuntimeEvent.intent_id == e.intent_id)))
    assert len(now) == len(old) + 1
    assert rec.parent_receipt == old[-1].receipt_id
    assert replay(db, e.intent_id)["state"] == "RECOVERING"


def test_provider_neutrality_and_provenance():
    db = session()
    e = create_intent(db, actor_id="a", runtime_id="codex")
    x = append_event(db, intent_id=e.intent_id, actor_id="a", runtime_id="claude", event="ACCEPT", state_after="ACCEPTED", provenance={"provider": "anthropic"})
    assert x.runtime_id == "claude" and x.provenance["provider"] == "anthropic"


def test_quarantine():
    db = session()
    e = create_intent(db, actor_id="a", runtime_id="r")
    x = append_event(db, intent_id=e.intent_id, actor_id="a", runtime_id="r", event="QUARANTINE", state_after="QUARANTINED", payload={"reason": "poisoned"})
    assert x.state_after == "QUARANTINED"


def test_dependency_freshness_distribution():
    db = session()
    e = create_intent(db, actor_id="a", runtime_id="r", payload={"dependency": "db", "freshness_required": True, "distribution": "api"})
    assert e.payload["dependency"] == "db"
    assert e.payload["freshness_required"] is True
    assert e.payload["distribution"] == "api"


def test_invalid_transition_is_rejected():
    db = session()
    e = create_intent(db, actor_id="a", runtime_id="r")
    try:
        append_event(db, intent_id=e.intent_id, actor_id="a", runtime_id="r", event="VALIDATE", state_after="REAL")
    except ValueError as exc:
        assert "Invalid transition" in str(exc)
    else:
        raise AssertionError("invalid transition accepted")
