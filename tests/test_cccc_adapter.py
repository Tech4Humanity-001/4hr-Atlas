from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.services.cccc_adapter import ingest_cccc_event

def test_cccc_event_is_ingested_with_provenance():
    engine=create_engine("sqlite:///:memory:",future=True);Base.metadata.create_all(engine);db=sessionmaker(bind=engine,future=True)()
    from app.services.runtime_truth import create_intent
    intent=create_intent(db,actor_id="a",runtime_id="cccc")
    event=ingest_cccc_event(db,intent_id=intent.intent_id,actor_id="a",runtime_id="claude",event="ACCEPT",state_after="ACCEPTED",authority_ref="auth",source_event_id="cccc-1",source_runtime_id="cccc-runtime")
    assert event.provenance=={"source":"cccc","source_event_id":"cccc-1","source_runtime_id":"cccc-runtime"}
