from __future__ import annotations
import hashlib,json
from datetime import datetime,timezone
from uuid import uuid4
from sqlalchemy import select
from app.models.runtime import RuntimeEvent
STATES={"INTENDED","ACCEPTED","STARTED","EXECUTING","PARTIAL","VALIDATING","REAL","DEGRADED","BLOCKED","QUARANTINED","RECOVERING"}
TRANSITIONS={"INTENDED":{"ACCEPTED","BLOCKED","QUARANTINED"},"ACCEPTED":{"STARTED","BLOCKED","QUARANTINED"},"STARTED":{"EXECUTING","PARTIAL","BLOCKED","QUARANTINED"},"EXECUTING":{"PARTIAL","VALIDATING","BLOCKED","QUARANTINED"},"PARTIAL":{"VALIDATING","RECOVERING","BLOCKED","QUARANTINED"},"VALIDATING":{"REAL","PARTIAL","DEGRADED","QUARANTINED"},"REAL":{"DEGRADED","RECOVERING"},"DEGRADED":{"RECOVERING","QUARANTINED"},"BLOCKED":{"RECOVERING","QUARANTINED"},"RECOVERING":{"STARTED","EXECUTING","BLOCKED","QUARANTINED"},"QUARANTINED":{"RECOVERING"}}
AUTHORIZED_EVENTS={"ACCEPT","VALIDATE","OUTCOME","RECOVER","QUARANTINE"}
EVENTS={"INTENT","ACCEPT","START","EXECUTE","EVIDENCE","VALIDATE","OUTCOME","RECOVER","CLAIM","BLOCK","QUARANTINE","TELEMETRY"}
def _canonical(d): return json.dumps(d,sort_keys=True,separators=(",",":"),default=str)
def _hash_event(prev,data): return hashlib.sha256(((prev or "")+_canonical(data)).encode()).hexdigest()
def _last(db,intent_id): return db.scalar(select(RuntimeEvent).where(RuntimeEvent.intent_id==intent_id).order_by(RuntimeEvent.id.desc()).limit(1))
def _intent(db,intent_id):
 x=db.scalar(select(RuntimeEvent).where(RuntimeEvent.intent_id==intent_id).order_by(RuntimeEvent.id.asc()).limit(1))
 if not x: raise ValueError("Unknown intent")
 return x
def _policy(payload,intent):
 dep=intent.get("dependency")
 if dep is not None and payload.get("dependency_ready") is not True: return f"Dependency not ready: {dep}"
 if intent.get("freshness_required") is True and payload.get("freshness_ok") is not True: return "Freshness revalidation required before consequential action"
def append_event(db:Session,*,intent_id,actor_id,runtime_id,event,state_after,model_id=None,authority_ref=None,evidence_refs=None,provenance=None,payload=None,claim=None,parent_receipt=None,state_before=None):
 if state_after not in STATES: raise ValueError(f"Unknown state: {state_after}")
 if event not in EVENTS: raise ValueError(f"Unknown event: {event}")
 if event in AUTHORIZED_EVENTS and not authority_ref: raise ValueError(f"Authority required for event: {event}")
 previous=_last(db,intent_id); before=state_before if state_before is not None else (previous.state_after if previous else None)
 if previous and state_before is not None and state_before!=previous.state_after: raise ValueError(f"State-before mismatch: expected {previous.state_after}, got {state_before}")
 if before is None and event!="INTENT": raise ValueError("First event must be INTENT")
 if previous and previous.payload.get("owner") and previous.payload.get("owner")!=actor_id: raise ValueError("Actor is not the current intent owner")
 p=dict(payload or {})
 if event=="INTENT": p.setdefault("owner",actor_id)
 elif previous: p.setdefault("owner",previous.payload.get("owner",actor_id))
 owner=p.get("owner") or actor_id
 if owner!=actor_id and event!="TELEMETRY": raise ValueError("Actor does not match intent owner")
 ip=_intent(db,intent_id).payload if previous else p
 if event in {"START","EXECUTE"}:
  reason=_policy(p,ip)
  if reason:
   state_after="BLOCKED"; p={**p,"blocked_reason":reason,"recovery_required":True}
 if before and state_after!=before and state_after not in TRANSITIONS.get(before,set()): raise ValueError(f"Invalid transition {before} -> {state_after}")
 if event=="OUTCOME":
  dest=p.get("destination") or p.get("consumer") or ip.get("distribution")
  if not dest: raise ValueError("Outcome destination or consumer is required")
  p.setdefault("destination",dest)
 receipt_id=uuid4().hex; event_id=uuid4().hex; timestamp=datetime.now(timezone.utc)
 body={"event_id":event_id,"intent_id":intent_id,"receipt_id":receipt_id,"actor_id":actor_id,"runtime_id":runtime_id,"model_id":model_id,"event":event,"state_before":before,"state_after":state_after,"timestamp":timestamp.isoformat(),"authority_ref":authority_ref,"parent_receipt":parent_receipt,"evidence_refs":evidence_refs or [],"provenance":provenance or {},"payload":p,"replayable":True,"claim":claim}
 row=RuntimeEvent(event_id=event_id,intent_id=intent_id,receipt_id=receipt_id,actor_id=actor_id,runtime_id=runtime_id,model_id=model_id,event=event,state_before=before,state_after=state_after,timestamp=timestamp,authority_ref=authority_ref,parent_receipt=parent_receipt,evidence_refs=evidence_refs or [],provenance=provenance or {},payload=p,replayable=True,previous_hash=previous.event_hash if previous else None,event_hash=_hash_event(previous.event_hash if previous else None,body),claim=claim)
 db.add(row);db.commit();db.refresh(row);return row
def create_intent(db,*,actor_id,runtime_id,intent_id=None,model_id=None,authority_ref=None,payload=None): return append_event(db,intent_id=intent_id or uuid4().hex,actor_id=actor_id,runtime_id=runtime_id,model_id=model_id,authority_ref=authority_ref,event="INTENT",state_after="INTENDED",payload=payload)
def record_evidence(db,*,intent_id,actor_id,runtime_id,evidence_refs,payload=None):
 c=_last(db,intent_id)
 if not c: raise ValueError("Unknown intent")
 return append_event(db,intent_id=intent_id,actor_id=actor_id,runtime_id=runtime_id,event="EVIDENCE",state_after="VALIDATING",state_before=c.state_after,evidence_refs=evidence_refs,payload=payload)
def validate(db,*,intent_id,actor_id,runtime_id,valid,evidence_refs=None,validation=None,authority_ref=None):
 c=_last(db,intent_id)
 if not c: raise ValueError("Unknown intent")
 return append_event(db,intent_id=intent_id,actor_id=actor_id,runtime_id=runtime_id,event="VALIDATE",state_after="REAL" if valid else "PARTIAL",authority_ref=authority_ref,evidence_refs=evidence_refs or c.evidence_refs,payload=validation or {"valid":valid})
def record_outcome(db,*,intent_id,actor_id,runtime_id,outcome,authority_ref,evidence_refs=None):
 c=_last(db,intent_id)
 if not c: raise ValueError("Unknown intent")
 return append_event(db,intent_id=intent_id,actor_id=actor_id,runtime_id=runtime_id,event="OUTCOME",state_after=c.state_after,authority_ref=authority_ref,evidence_refs=evidence_refs or c.evidence_refs,payload=outcome)
def record_telemetry(db,*,intent_id,actor_id,runtime_id,telemetry,state_after=None,evidence_refs=None):
 c=_last(db,intent_id)
 if not c: raise ValueError("Unknown intent")
 return append_event(db,intent_id=intent_id,actor_id=actor_id,runtime_id=runtime_id,event="TELEMETRY",state_after=state_after or c.state_after,evidence_refs=evidence_refs or [],payload=telemetry)
def recover(db,*,intent_id,actor_id,runtime_id,authority_ref=None,payload=None):
 c=_last(db,intent_id)
 if not c: raise ValueError("Unknown intent")
 return append_event(db,intent_id=intent_id,actor_id=actor_id,runtime_id=runtime_id,event="RECOVER",state_after="RECOVERING",authority_ref=authority_ref,payload=payload,parent_receipt=c.receipt_id)
def replay(db,intent_id):
 events=list(db.scalars(select(RuntimeEvent).where(RuntimeEvent.intent_id==intent_id).order_by(RuntimeEvent.id)))
 if not events: raise ValueError("Unknown intent")
 state=events[0].state_after
 for e in events[1:]:
  if e.state_before!=state: raise ValueError("Ledger replay failed: state discontinuity")
  state=e.state_after
 return {"intent_id":intent_id,"state":state,"event_count":len(events),"receipts":[e.receipt_id for e in events]}
def verify_ledger(db,intent_id):
 events=list(db.scalars(select(RuntimeEvent).where(RuntimeEvent.intent_id==intent_id).order_by(RuntimeEvent.id)));previous=None
 for e in events:
  body={"event_id":e.event_id,"intent_id":e.intent_id,"receipt_id":e.receipt_id,"actor_id":e.actor_id,"runtime_id":e.runtime_id,"model_id":e.model_id,"event":e.event,"state_before":e.state_before,"state_after":e.state_after,"timestamp":e.timestamp.isoformat(),"authority_ref":e.authority_ref,"parent_receipt":e.parent_receipt,"evidence_refs":e.evidence_refs or [],"provenance":e.provenance or {},"payload":e.payload or {},"replayable":e.replayable,"claim":e.claim}
  if e.previous_hash!=previous or e.event_hash!=_hash_event(previous,body): return False
  previous=e.event_hash
 return True
