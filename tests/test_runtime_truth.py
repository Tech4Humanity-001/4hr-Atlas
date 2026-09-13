from sqlalchemy import create_engine,select
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.models.runtime import RuntimeEvent
from app.services.runtime_truth import append_event,create_intent,record_evidence,record_outcome,record_telemetry,recover,replay,validate,verify_ledger

def session():
 e=create_engine("sqlite:///:memory:",future=True);Base.metadata.create_all(e);return sessionmaker(bind=e,future=True)()
def test_001_intent_identity():
 d=session();e=create_intent(d,actor_id="a",runtime_id="r");assert e.intent_id

def test_002_missing_authority_blocks():
 d=session();e=create_intent(d,actor_id="a",runtime_id="r");x=append_event(d,intent_id=e.intent_id,actor_id="a",runtime_id="r",event="ACCEPT",state_after="ACCEPTED");assert x.state_after=="BLOCKED" and x.payload["recovery_required"]

def test_003_ownership():
 d=session();e=create_intent(d,actor_id="a",runtime_id="r")
 try: append_event(d,intent_id=e.intent_id,actor_id="b",runtime_id="r",event="ACCEPT",state_after="ACCEPTED",authority_ref="auth")
 except ValueError as x: assert "owner" in str(x).lower()
 else: raise AssertionError

def test_004_receipt():
 d=session();e=create_intent(d,actor_id="a",runtime_id="r");x=append_event(d,intent_id=e.intent_id,actor_id="a",runtime_id="r",event="ACCEPT",state_after="ACCEPTED",authority_ref="auth");assert x.receipt_id

def test_005_evidence():
 d=session();e=create_intent(d,actor_id="a",runtime_id="r");append_event(d,intent_id=e.intent_id,actor_id="a",runtime_id="r",event="ACCEPT",state_after="ACCEPTED",authority_ref="auth");append_event(d,intent_id=e.intent_id,actor_id="a",runtime_id="r",event="START",state_after="STARTED");append_event(d,intent_id=e.intent_id,actor_id="a",runtime_id="r",event="EXECUTE",state_after="EXECUTING");x=record_evidence(d,intent_id=e.intent_id,actor_id="a",runtime_id="r",evidence_refs=["e://1"]);assert x.evidence_refs

def test_006_validation():
 d=session();e=create_intent(d,actor_id="a",runtime_id="r");append_event(d,intent_id=e.intent_id,actor_id="a",runtime_id="r",event="ACCEPT",state_after="ACCEPTED",authority_ref="auth");append_event(d,intent_id=e.intent_id,actor_id="a",runtime_id="r",event="START",state_after="STARTED");append_event(d,intent_id=e.intent_id,actor_id="a",runtime_id="r",event="EXECUTE",state_after="EXECUTING");record_evidence(d,intent_id=e.intent_id,actor_id="a",runtime_id="r",evidence_refs=["e://1"]);x=validate(d,intent_id=e.intent_id,actor_id="a",runtime_id="r",valid=True,evidence_refs=["e://1"],authority_ref="auth");assert x.state_after=="REAL"

def test_007_claim_separation():
 d=session();e=create_intent(d,actor_id="a",runtime_id="r")
 try: append_event(d,intent_id=e.intent_id,actor_id="a",runtime_id="r",event="CLAIM",state_after="REAL",claim="done")
 except ValueError as x: assert "Claim cannot" in str(x)
 else: raise AssertionError

def test_008_outcome_requires_achievement_and_evidence():
 d=session();e=create_intent(d,actor_id="a",runtime_id="r",payload={"distribution":"api"});
 try: record_outcome(d,intent_id=e.intent_id,actor_id="a",runtime_id="r",authority_ref="auth",outcome={"result":"completed"},evidence_refs=[])
 except ValueError as x: assert "evidence" in str(x).lower()
 else: raise AssertionError

def test_009_telemetry():
 d=session();e=create_intent(d,actor_id="a",runtime_id="r",payload={"distribution":"api"});append_event(d,intent_id=e.intent_id,actor_id="a",runtime_id="r",event="ACCEPT",state_after="ACCEPTED",authority_ref="auth");append_event(d,intent_id=e.intent_id,actor_id="a",runtime_id="r",event="START",state_after="STARTED");append_event(d,intent_id=e.intent_id,actor_id="a",runtime_id="r",event="EXECUTE",state_after="EXECUTING");record_evidence(d,intent_id=e.intent_id,actor_id="a",runtime_id="r",evidence_refs=["e://1"]);validate(d,intent_id=e.intent_id,actor_id="a",runtime_id="r",valid=True,evidence_refs=["e://1"],authority_ref="auth");o=record_outcome(d,intent_id=e.intent_id,actor_id="a",runtime_id="r",authority_ref="auth",outcome={"result":"completed","achieved":True},evidence_refs=["e://1"]);assert o.state_after=="DEGRADED";t=record_telemetry(d,intent_id=e.intent_id,actor_id="a",runtime_id="r",telemetry={"material_change_observed":True});assert t.state_after=="REAL"

def test_010_ledger():
 d=session();e=create_intent(d,actor_id="a",runtime_id="r");append_event(d,intent_id=e.intent_id,actor_id="a",runtime_id="r",event="ACCEPT",state_after="ACCEPTED",authority_ref="auth");assert verify_ledger(d,e.intent_id)

def test_011_projection_replay():
 d=session();e=create_intent(d,actor_id="a",runtime_id="r");assert replay(d,e.intent_id)["state"]=="INTENDED"

def test_012_recovery():
 d=session();e=create_intent(d,actor_id="a",runtime_id="r");append_event(d,intent_id=e.intent_id,actor_id="a",runtime_id="r",event="BLOCK",state_after="BLOCKED");old=list(d.scalars(select(RuntimeEvent).where(RuntimeEvent.intent_id==e.intent_id)));r=recover(d,intent_id=e.intent_id,actor_id="a",runtime_id="r",authority_ref="recovery");now=list(d.scalars(select(RuntimeEvent).where(RuntimeEvent.intent_id==e.intent_id)));assert len(now)==len(old)+1 and r.parent_receipt==old[-1].receipt_id

def test_013_provider_neutrality():
 d=session();e=create_intent(d,actor_id="a",runtime_id="codex");x=append_event(d,intent_id=e.intent_id,actor_id="a",runtime_id="claude",event="ACCEPT",state_after="ACCEPTED",authority_ref="auth");assert x.runtime_id=="claude"

def test_014_provenance():
 d=session();e=create_intent(d,actor_id="a",runtime_id="r");x=append_event(d,intent_id=e.intent_id,actor_id="a",runtime_id="r",event="ACCEPT",state_after="ACCEPTED",authority_ref="auth",provenance={"source":"cccc","source_event_id":"x"});assert x.provenance["source_event_id"]=="x"

def test_015_quarantine():
 d=session();e=create_intent(d,actor_id="a",runtime_id="r");x=append_event(d,intent_id=e.intent_id,actor_id="a",runtime_id="r",event="QUARANTINE",state_after="QUARANTINED",authority_ref="security");assert x.state_after=="QUARANTINED"

def test_016_dependency_recovery():
 d=session();e=create_intent(d,actor_id="a",runtime_id="r",payload={"dependency":"db"});x=append_event(d,intent_id=e.intent_id,actor_id="a",runtime_id="r",event="START",state_after="STARTED");assert x.state_after=="BLOCKED";r=recover(d,intent_id=e.intent_id,actor_id="a",runtime_id="r",authority_ref="recovery");assert r.state_after=="RECOVERING"

def test_017_freshness():
 d=session();e=create_intent(d,actor_id="a",runtime_id="r",payload={"freshness_required":True});r=recover(d,intent_id=e.intent_id,actor_id="a",runtime_id="r",authority_ref="recovery");x=append_event(d,intent_id=e.intent_id,actor_id="a",runtime_id="r",event="START",state_after="STARTED",payload={"freshness_ok":True});assert x.state_after=="STARTED"

def test_018_distribution():
 d=session();e=create_intent(d,actor_id="a",runtime_id="r",payload={"distribution":"api"});append_event(d,intent_id=e.intent_id,actor_id="a",runtime_id="r",event="ACCEPT",state_after="ACCEPTED",authority_ref="auth");append_event(d,intent_id=e.intent_id,actor_id="a",runtime_id="r",event="START",state_after="STARTED");append_event(d,intent_id=e.intent_id,actor_id="a",runtime_id="r",event="EXECUTE",state_after="EXECUTING");record_evidence(d,intent_id=e.intent_id,actor_id="a",runtime_id="r",evidence_refs=["e://1"]);validate(d,intent_id=e.intent_id,actor_id="a",runtime_id="r",valid=True,evidence_refs=["e://1"],authority_ref="auth");o=record_outcome(d,intent_id=e.intent_id,actor_id="a",runtime_id="r",authority_ref="auth",outcome={"achieved":True},evidence_refs=["e://1"]);assert o.payload["destination"]=="api"

def test_019_state_binding_and_hash_integrity():
 d=session();e=create_intent(d,actor_id="a",runtime_id="r");append_event(d,intent_id=e.intent_id,actor_id="a",runtime_id="r",event="ACCEPT",state_after="ACCEPTED",authority_ref="auth");
 try: append_event(d,intent_id=e.intent_id,actor_id="a",runtime_id="r",event="START",state_after="STARTED",state_before="INTENDED")
 except ValueError as x: assert "State-before mismatch" in str(x)
 else: raise AssertionError
 assert verify_ledger(d,e.intent_id);row=d.scalar(select(RuntimeEvent).where(RuntimeEvent.intent_id==e.intent_id).order_by(RuntimeEvent.id.desc()).limit(1));row.event_id="tampered";d.commit();assert not verify_ledger(d,e.intent_id)
