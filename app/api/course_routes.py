from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.course import Course, CourseCredential
from app.services.course_engine import answer_question, complete_activity, complete_lesson, complete_remediation, course_payload, get_or_create_progress, get_or_create_state, start_assessment

router=APIRouter(prefix="/courses",tags=["courses"])

class AnswerIn(BaseModel):
    learner_id:str=Field(min_length=1,max_length=128)
    question_id:str
    answer:str

class LearnerIn(BaseModel):
    learner_id:str=Field(min_length=1,max_length=128)

def _course(db,subtopic_id):
    c=db.query(Course).filter_by(subtopic_id=subtopic_id).one_or_none()
    if not c: raise HTTPException(404,"Course not found")
    return c

@router.get("/{subtopic_id}")
def get_course(subtopic_id:str,db:Session=Depends(get_db)):
    return course_payload(db,_course(db,subtopic_id))

@router.post("/{subtopic_id}/lesson/complete")
def lesson_complete(subtopic_id:str,body:LearnerIn,db:Session=Depends(get_db)):
    return complete_lesson(db,body.learner_id,_course(db,subtopic_id))

@router.post("/{subtopic_id}/activity/complete")
def activity_complete(subtopic_id:str,body:LearnerIn,db:Session=Depends(get_db)):
    return complete_activity(db,body.learner_id,_course(db,subtopic_id))

@router.post("/{subtopic_id}/assessment/start")
def assessment_start(subtopic_id:str,body:LearnerIn,db:Session=Depends(get_db)):
    try:return start_assessment(db,body.learner_id,_course(db,subtopic_id))
    except ValueError as exc: raise HTTPException(409,str(exc)) from exc

@router.post("/{subtopic_id}/assessment/answer")
def assessment_answer(subtopic_id:str,body:AnswerIn,db:Session=Depends(get_db)):
    try:return answer_question(db,body.learner_id,_course(db,subtopic_id),body.question_id,body.answer)
    except ValueError as exc: raise HTTPException(409,str(exc)) from exc

@router.post("/{subtopic_id}/remediation/complete")
def remediation_complete(subtopic_id:str,body:AnswerIn,db:Session=Depends(get_db)):
    try:return complete_remediation(db,body.learner_id,_course(db,subtopic_id),body.question_id)
    except ValueError as exc: raise HTTPException(409,str(exc)) from exc

@router.get("/{subtopic_id}/progress")
def progress(subtopic_id:str,learner_id:str=Query(...),db:Session=Depends(get_db)):
    c=_course(db,subtopic_id); p=get_or_create_progress(db,learner_id,c.id); s=get_or_create_state(db,learner_id,c.id); db.commit()
    return {"course_id":c.id,"learner_id":learner_id,"lesson_complete":p.lesson_complete,
            "activity_complete":s.activity_complete,"assessment_started":p.assessment_started,
            "answered":len(p.answered or []),"score":p.score,"mastery":p.mastery,
            "credential_id":p.credential_id,"remediation_seen":len(s.remediation_seen or [])}

@router.get("/{subtopic_id}/credential")
def credential(subtopic_id:str,learner_id:str=Query(...),db:Session=Depends(get_db)):
    c=_course(db,subtopic_id)
    cred=db.query(CourseCredential).filter_by(course_id=c.id,learner_id=learner_id).one_or_none()
    if not cred: raise HTTPException(404,"Credential not issued")
    return {"id":cred.id,"course_id":c.id,"learner_id":learner_id,"score":cred.score,
            "evidence":cred.evidence,"issued_at":cred.issued_at.isoformat() if cred.issued_at else None}