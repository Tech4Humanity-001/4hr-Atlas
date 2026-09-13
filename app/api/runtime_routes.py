from __future__ import annotations
from fastapi import APIRouter,Depends,HTTPException
from pydantic import BaseModel,Field
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.runtime_truth import append_event,create_intent,record_evidence,record_outcome,record_telemetry,recover,replay,validate,verify_ledger
router=APIRouter(prefix="/runtime",tags=["runtime-truth"])
class IntentIn(BaseModel):
 actor_id:str;runtime_id:str;model_id:str|None=None;authority_ref:str|None=None;intent_id:str|None=None;payload:dict=Field(default_factory=dict)
class EventIn(BaseModel):
 actor_id:str;runtime_id:str;event:str;state_after:str;model_id:str|None=None;authority_ref:str|None=None;evidence_refs:list=Field(default_factory=list);provenance:dict=Field(default_factory=dict);payload:dict=Field(default_factory=dict);claim:str|None=None;parent_receipt:str|None=None
class EvidenceIn(BaseModel):
 actor_id:str;runtime_id:str;evidence_refs:list;payload:dict=Field(default_factory=dict)
class ValidateIn(BaseModel):
 actor_id:str;runtime_id:str;valid:bool;authority_ref:str|None=None;evidence_refs:list=Field(default_factory=list);validation:dict=Field(default_factory=dict)
class OutcomeIn(BaseModel):
 actor_id:str;runtime_id:str;authority_ref:str|None=None;outcome:dict=Field(default_factory=dict);evidence_refs:list=Field(default_factory=list)
class TelemetryIn(BaseModel):
 actor_id:str;runtime_id:str;telemetry:dict=Field(default_factory=dict);state_after:str|None=None;evidence_refs:list=Field(default_factory=list)
class RecoverIn(BaseModel):
 actor_id:str;runtime_id:str;authority_ref:str|None=None;payload:dict=Field(default_factory=dict)
def _event(e): return {"event_id":e.event_id,"intent_id":e.intent_id,"receipt_id":e.receipt_id,"event":e.event,"state_before":e.state_before,"state_after":e.state_after,"timestamp":e.timestamp.isoformat(),"event_hash":e.event_hash,"previous_hash":e.previous_hash,"evidence_refs":e.evidence_refs,"authority_ref":e.authority_ref,"replayable":e.replayable}
@router.get("/health")
def runtime_health(db:Session=Depends(get_db)): return {"status":"ok","ledger":"runtime_events"}
@router.post("/intents")
def intents(body:IntentIn,db:Session=Depends(get_db)): return _event(create_intent(db,**body.model_dump()))
@router.post("/intents/{intent_id}/events")
def events(intent_id:str,body:EventIn,db:Session=Depends(get_db)):
 try:return _event(append_event(db,intent_id=intent_id,**body.model_dump()))
 except ValueError as exc:raise HTTPException(status_code=409,detail=str(exc)) from exc
@router.post("/intents/{intent_id}/evidence")
def evidence(intent_id:str,body:EvidenceIn,db:Session=Depends(get_db)):
 try:return _event(record_evidence(db,intent_id=intent_id,**body.model_dump()))
 except ValueError as exc:raise HTTPException(status_code=409,detail=str(exc)) from exc
@router.post("/intents/{intent_id}/validate")
def validation(intent_id:str,body:ValidateIn,db:Session=Depends(get_db)):
 try:return _event(validate(db,intent_id=intent_id,**body.model_dump()))
 except ValueError as exc:raise HTTPException(status_code=409,detail=str(exc)) from exc
@router.post("/intents/{intent_id}/outcome")
def outcome(intent_id:str,body:OutcomeIn,db:Session=Depends(get_db)):
 try:return _event(record_outcome(db,intent_id=intent_id,actor_id=body.actor_id,runtime_id=body.runtime_id,authority_ref=body.authority_ref,outcome=body.outcome,evidence_refs=body.evidence_refs))
 except ValueError as exc:raise HTTPException(status_code=409,detail=str(exc)) from exc
@router.post("/intents/{intent_id}/telemetry")
def telemetry(intent_id:str,body:TelemetryIn,db:Session=Depends(get_db)):
 try:return _event(record_telemetry(db,intent_id=intent_id,actor_id=body.actor_id,runtime_id=body.runtime_id,telemetry=body.telemetry,state_after=body.state_after,evidence_refs=body.evidence_refs))
 except ValueError as exc:raise HTTPException(status_code=409,detail=str(exc)) from exc
@router.post("/intents/{intent_id}/recover")
def recovery(intent_id:str,body:RecoverIn,db:Session=Depends(get_db)):
 try:return _event(recover(db,intent_id=intent_id,**body.model_dump()))
 except ValueError as exc:raise HTTPException(status_code=409,detail=str(exc)) from exc
@router.get("/intents/{intent_id}")
def intent_state(intent_id:str,db:Session=Depends(get_db)):
 try:
  result=replay(db,intent_id);result["ledger_valid"]=verify_ledger(db,intent_id);return result
 except ValueError as exc:raise HTTPException(status_code=404,detail=str(exc)) from exc
@router.get("/intents/{intent_id}/ledger")
def intent_ledger(intent_id:str,db:Session=Depends(get_db)):
 from sqlalchemy import select
 from app.models.runtime import RuntimeEvent
 rows=list(db.scalars(select(RuntimeEvent).where(RuntimeEvent.intent_id==intent_id).order_by(RuntimeEvent.id)))
 if not rows:raise HTTPException(status_code=404,detail="Unknown intent")
 return {"intent_id":intent_id,"ledger_valid":verify_ledger(db,intent_id),"events":[_event(e) for e in rows]}
@router.post("/intents/{intent_id}/replay")
def intent_replay(intent_id:str,db:Session=Depends(get_db)):
 try:return replay(db,intent_id)
 except ValueError as exc:raise HTTPException(status_code=409,detail=str(exc)) from exc
