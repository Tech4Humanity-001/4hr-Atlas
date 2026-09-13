from __future__ import annotations
from app.services.runtime_truth import append_event

def ingest_cccc_event(db, *, intent_id: str, actor_id: str, runtime_id: str, event: str, state_after: str, source_event_id: str, source_runtime_id: str | None = None, model_id: str | None = None, authority_ref: str | None = None, evidence_refs: list | None = None, payload: dict | None = None, claim: str | None = None):
    provenance = {"source": "cccc", "source_event_id": source_event_id, "source_runtime_id": source_runtime_id or runtime_id}
    return append_event(db, intent_id=intent_id, actor_id=actor_id, runtime_id=runtime_id, event=event, state_after=state_after, model_id=model_id, authority_ref=authority_ref, evidence_refs=evidence_refs, provenance=provenance, payload=payload, claim=claim)
