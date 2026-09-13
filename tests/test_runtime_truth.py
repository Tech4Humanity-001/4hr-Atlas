from sqlalchemy import create_engine,select
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.models.runtime import RuntimeEvent
from app.services.runtime_truth import append_event,create_intent,record_evidence,record_outcome,record_telemetry,recover,replay,validate,verify_ledger

def session():
 e=create_engine("sqlite:///:memory:",future=True);Base.metadata.create_all(e);return sessionmaker(bind=e,future=True)()
def test_identity_authority_ownership():
 d=session();e=create_intent(d,actor_id="a",runtime_id="r",authority_ref="auth",payload={"owner":"a"});assert e.intent_id and e.authority_ref=="auth";x=append_event(d,intent_id=e.intent_id,actor_id="a",runtime_id="r",event="ACCEPT",state_after="ACCEPTED",authority_ref="auth");assert x.payload["owner"]=="a"
def test_receipt_evidence_validation_claim_outcome_telemetry():
 d=session();e=create_intent(d,actor_id="a",runtime_id="r");append_event(d,intent_id=e.intent_id,actor_id="a",runtime_id="r",event="ACCEPT",state_after="ACCEPTED",authority_ref="auth");append_event(d,intent_id=e.intent_id,actor_id="a",runtime_id="r",event="START",state_after="STARTED");append_event(d,intent_id=e.intent_id,actor_id="a",runtime_id="r",event="EXECUTE",state_after="EXECUTING",claim="done");ev=record_evidence(d,intent_id=e.intent_id,actor_id="a",runtime_id="r",evidence_refs=["test://receipt"]);assert ev.evidence_refs==["test://receipt"];out=validate(d,intent_id=e.intent_id,actor_id="a",runtime_id="r",valid=True,evidence_refs=["test://receipt"],authority_ref="auth");assert out.state_after=="REAL";o=record_outcome(d,intent_id=e.intent_id,actor_id="a",runtime_id="r",authority_ref="auth",outcome={"result":"completed","destination":"api"},evidence_refs=["test://receipt"]);assert o.event=="OUTCOME" and o.state_after=="REAL";t=record_telemetry(d,intent_id=e.intent_id,actor_id="a",runtime_id="r",telemetry={"latency_ms":1});assert t.event=="TELEMETRY" and t.state_after=="REAL"
def test_ledger_and_projection():
 d=session();e=create_intent(d,actor_id="a",runtime_id="r");append_event(d,intent_id=e.intent_id,actor_id="a",runtime_id="r",event="ACCEPT",state_after="ACCEPTED",authority_ref="auth");assert verify_ledger(d,e.intent_id);assert replay(d,e.intent_id)["state"]=="ACCEPTED"
def test_recovery_preserves_history_and_replays():
 d=session();e=create_intent(d,actor_id="a",runtime_id="r");append_event(d,intent_id=e.intent_id,actor_id="a",runtime_id="r",event="BLOCK",state_after="BLOCKED");old=list(d.scalars(select(RuntimeEvent).where(RuntimeEvent.intent_id==e.intent_id)));r=recover(d,intent_id=e.intent_id,actor_id="a",runtime_id="r",authority_ref="recovery");now=list(d.scalars(select(RuntimeEvent).where(RuntimeEvent.intent_id==e.intent_id)));assert len(now)==len(old)+1 and r.parent_receipt==old[-1].receipt_id and replay(d,e.intent_id)["state"]=="RECOVERING"
def test_provider_neutrality_and_provenance():
 d=session();e=create_intent(d,actor_id="a",runtime_id="codex");x=append_event(d,intent_id=e.intent_id,actor_id="a",runtime_id="claude",event="ACCEPT",state_after="ACCEPTED",authority_ref="auth",provenance={"provider":"anthropic"});assert x.runtime_id=="claude" and x.provenance["provider"]=="anthropic"
def test_quarantine():
 d=session();e=create_intent(d,actor_id="a",runtime_id="r");x=append_event(d,intent_id=e.intent_id,actor_id="a",runtime_id="r",event="QUARANTINE",state_after="QUARANTINED",authority_ref="security",payload={"reason":"poisoned"});assert x.state_after=="QUARANTINED"
def test_dependency_freshness_distribution_enforced():
 d=session();e=create_intent(d,actor_id="a",runtime_id="r",payload={"dependency":"db","freshness_required":True,"distribution":"api"});x=append_event(d,intent_id=e.intent_id,actor_id="a",runtime_id="r",event="START",state_after="STARTED");assert x.state_after=="BLOCKED" and x.payload["recovery_required"] is True;r=recover(d,intent_id=e.intent_id,actor_id="a",runtime_id="r",authority_ref="recovery");assert r.state_after=="RECOVERING";x=append_event(d,intent_id=e.intent_id,actor_id="a",runtime_id="r",event="START",state_after="STARTED",payload={"dependency_ready":True,"freshness_ok":True});assert x.state_after=="STARTED";x=append_event(d,intent_id=e.intent_id,actor_id="a",runtime_id="r",event="EXECUTE",state_after="EXECUTING",payload={"dependency_ready":True,"freshness_ok":True});assert x.state_after=="EXECUTING";v=record_evidence(d,intent_id=e.intent_id,actor_id="a",runtime_id="r",evidence_refs=["test://result"]);q=validate(d,intent_id=e.intent_id,actor_id="a",runtime_id="r",valid=True,evidence_refs=v.evidence_refs,authority_ref="auth");o=record_outcome(d,intent_id=e.intent_id,actor_id="a",runtime_id="r",authority_ref="auth",outcome={"result":"completed"});assert q.state_after=="REAL" and o.payload["destination"]=="api"
def test_outcome_requires_distribution():
 d=session();e=create_intent(d,actor_id="a",runtime_id="r");
 try: record_outcome(d,intent_id=e.intent_id,actor_id="a",runtime_id="r",authority_ref="auth",outcome={"result":"completed"})
 except ValueError as x: assert "destination or consumer" in str(x)
 else: raise AssertionError("undelivered outcome accepted")
def test_invalid_transition_is_rejected():
 d=session();e=create_intent(d,actor_id="a",runtime_id="r");
 try: append_event(d,intent_id=e.intent_id,actor_id="a",runtime_id="r",event="VALIDATE",state_after="REAL",authority_ref="auth")
 except ValueError as x: assert "Invalid transition" in str(x)
 else: raise AssertionError("invalid transition accepted")
def test_authority_is_required_for_sensitive_events():
 d=session();e=create_intent(d,actor_id="a",runtime_id="r");
 try: append_event(d,intent_id=e.intent_id,actor_id="a",runtime_id="r",event="ACCEPT",state_after="ACCEPTED")
 except ValueError as x: assert "Authority required" in str(x)
 else: raise AssertionError("unauthorised event accepted")
def test_owner_is_enforced():
 d=session();e=create_intent(d,actor_id="a",runtime_id="r");
 try: append_event(d,intent_id=e.intent_id,actor_id="b",runtime_id="r",event="ACCEPT",state_after="ACCEPTED",authority_ref="auth")
 except ValueError as x: assert "owner" in str(x).lower()
 else: raise AssertionError("non-owner actor accepted")
def test_event_id_is_bound_to_hash_chain():
 d=session();e=create_intent(d,actor_id="a",runtime_id="r");append_event(d,intent_id=e.intent_id,actor_id="a",runtime_id="r",event="ACCEPT",state_after="ACCEPTED",authority_ref="auth");assert verify_ledger(d,e.intent_id);r=d.scalar(select(RuntimeEvent).where(RuntimeEvent.intent_id==e.intent_id).order_by(RuntimeEvent.id.desc()).limit(1));r.event_id="tampered-event-id";d.commit();assert not verify_ledger(d,e.intent_id)
def test_state_before_cannot_override_ledger():
 d=session();e=create_intent(d,actor_id="a",runtime_id="r");append_event(d,intent_id=e.intent_id,actor_id="a",runtime_id="r",event="ACCEPT",state_after="ACCEPTED",authority_ref="auth");
 try: append_event(d,intent_id=e.intent_id,actor_id="a",runtime_id="r",event="START",state_after="STARTED",state_before="INTENDED")
 except ValueError as x: assert "State-before mismatch" in str(x)
 else: raise AssertionError("state-before override accepted")
