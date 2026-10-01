"""Reusable Atlas course engine with a persisted learner vertical slice."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from sqlalchemy.orm import Session
from app.core.config import ROOT
from app.models.course import Course, CourseCredential, CourseLearnerState, CourseQuestion, LearnerProgress

SEED_PATH = ROOT / "data" / "course_seed.json"

def _seed_item(subtopic_id: str) -> dict:
    payload = json.loads(SEED_PATH.read_text(encoding="utf-8"))
    try:
        return next(item for item in payload if item["subtopic_id"] == subtopic_id)
    except StopIteration as exc:
        raise ValueError(f"No course content for {subtopic_id}") from exc

def seed_courses(db: Session) -> int:
    payload = json.loads(SEED_PATH.read_text(encoding="utf-8"))
    created = 0
    for item in payload:
        course = db.query(Course).filter_by(subtopic_id=item["subtopic_id"]).one_or_none()
        if not course:
            course = Course(id=item["course_id"], subtopic_id=item["subtopic_id"], theme_id=item["theme_id"],
                            topic_id=item["topic_id"], title=item["title"], intro=item["intro"],
                            lesson=item["lesson"], source_url=item.get("source_url"), version=item.get("version","1"))
            db.add(course)
            created += 1
        else:
            for key in ("title","intro","lesson","source_url","version","theme_id","topic_id"):
                if key in item:
                    setattr(course, key, item[key])
        existing = {q.ordinal: q for q in db.query(CourseQuestion).filter_by(course_id=item["course_id"]).all()}
        for q in item["questions"]:
            row = existing.get(q["ordinal"])
            if not row:
                db.add(CourseQuestion(id=f'{item["course_id"]}-Q{q["ordinal"]}', course_id=item["course_id"],
                                      ordinal=q["ordinal"], difficulty=q["difficulty"], prompt=q["prompt"],
                                      choices=q["choices"], answer=q["answer"], explanation=q["explanation"]))
            else:
                row.difficulty=q["difficulty"]; row.prompt=q["prompt"]; row.choices=q["choices"]
                row.answer=q["answer"]; row.explanation=q["explanation"]
    db.commit()
    return created

def get_or_create_progress(db: Session, learner_id: str, course_id: str) -> LearnerProgress:
    p=db.query(LearnerProgress).filter_by(learner_id=learner_id, course_id=course_id).one_or_none()
    if not p:
        p=LearnerProgress(learner_id=learner_id, course_id=course_id, answered=[])
        db.add(p); db.flush()
    return p

def get_or_create_state(db: Session, learner_id: str, course_id: str) -> CourseLearnerState:
    state=db.query(CourseLearnerState).filter_by(learner_id=learner_id, course_id=course_id).one_or_none()
    if not state:
        state=CourseLearnerState(learner_id=learner_id, course_id=course_id, remediation_seen=[])
        db.add(state); db.flush()
    return state

def course_payload(db: Session, course: Course) -> dict:
    qs=db.query(CourseQuestion).filter_by(course_id=course.id).order_by(CourseQuestion.ordinal).all()
    item=_seed_item(course.subtopic_id)
    return {"id":course.id,"subtopic_id":course.subtopic_id,"theme_id":course.theme_id,"topic_id":course.topic_id,
            "title":course.title,"intro":course.intro,"lesson":course.lesson,"source_url":course.source_url,
            "activity":item.get("activity",{}),"question_count":len(qs),"status":"READY"}

def complete_activity(db: Session, learner_id: str, course: Course) -> dict:
    state=get_or_create_state(db, learner_id, course.id)
    state.activity_complete=True
    db.commit()
    return {"course_id":course.id,"learner_id":learner_id,"activity_complete":True}

def complete_remediation(db: Session, learner_id: str, course: Course, question_id: str) -> dict:
    q=db.get(CourseQuestion, question_id)
    if not q or q.course_id != course.id:
        raise ValueError("Unknown course question")
    state=get_or_create_state(db, learner_id, course.id)
    seen=list(state.remediation_seen or [])
    if question_id not in seen:
        seen.append(question_id)
        state.remediation_seen=seen
    db.commit()
    return {"course_id":course.id,"learner_id":learner_id,"question_id":question_id,"remediation_seen":True}

def start_assessment(db: Session, learner_id: str, course: Course) -> dict:
    state=get_or_create_state(db, learner_id, course.id)
    if not state.activity_complete:
        raise ValueError("Complete the practice activity before starting the assessment")
    p=get_or_create_progress(db, learner_id, course.id)
    p.assessment_started=True
    db.commit()
    qs=db.query(CourseQuestion).filter_by(course_id=course.id).order_by(CourseQuestion.ordinal).all()
    answered_ids={x["question_id"] for x in (p.answered or [])}
    remaining=[q for q in qs if q.id not in answered_ids]
    first=remaining[0] if remaining else None
    return {"course_id":course.id,"question_count":len(qs),"answered":len(answered_ids),
            "questions":[{"id":first.id,"ordinal":first.ordinal,"difficulty":first.difficulty,"prompt":first.prompt,"choices":first.choices}] if first else []}

def answer_question(db: Session, learner_id: str, course: Course, question_id: str, answer: str) -> dict:
    q=db.get(CourseQuestion, question_id)
    if not q or q.course_id != course.id:
        raise ValueError("Unknown course question")
    p=get_or_create_progress(db, learner_id, course.id)
    if not p.lesson_complete:
        raise ValueError("Complete the lesson before answering the assessment")
    answered=list(p.answered or [])
    if any(x["question_id"]==q.id for x in answered):
        raise ValueError("Question already answered")
    correct=answer.strip().casefold()==q.answer.strip().casefold()
    answered.append({"question_id":q.id,"correct":correct,"answer":answer,"difficulty":q.difficulty})
    p.answered=answered
    p.score=round(100*sum(1 for x in answered if x["correct"])/len(answered),2)
    total=db.query(CourseQuestion).filter_by(course_id=course.id).count()
    next_question=None
    if len(answered)<total:
        answered_ids={x["question_id"] for x in answered}
        remaining=[row for row in db.query(CourseQuestion).filter_by(course_id=course.id).all() if row.id not in answered_ids]
        target=max(1,min(3,q.difficulty + (1 if correct else -1)))
        next_question=min(remaining,key=lambda row:(abs(row.difficulty-target),row.ordinal))
    if len(answered)==total:
        p.mastery=p.lesson_complete and p.score>=80
        if p.mastery and not p.credential_id:
            digest=hashlib.sha256(f"{learner_id}:{course.id}:{p.score}".encode()).hexdigest()[:24]
            cid=f"ATL-CRED-{digest.upper()}"
            db.add(CourseCredential(id=cid,learner_id=learner_id,course_id=course.id,score=p.score,
                                    evidence={"questions":len(answered),"correct":sum(x["correct"] for x in answered),
                                              "lesson_complete":p.lesson_complete,"activity_complete":get_or_create_state(db, learner_id, course.id).activity_complete,
                                              "rule":"lesson_complete AND activity_complete AND score >= 80"}))
            p.credential_id=cid
    db.commit()
    result={"correct":correct,"score":p.score,"answered":len(answered),"remaining":total-len(answered),
            "mastery":p.mastery,"credential_id":p.credential_id,"explanation":q.explanation,
            "remediation":{"required":not correct,"question_id":q.id,
                           "instruction":f"Review the lesson section relevant to this question. {q.explanation}"}}
    if next_question:
        result["next_question"]={"id":next_question.id,"ordinal":next_question.ordinal,
                                 "difficulty":next_question.difficulty,"prompt":next_question.prompt,
                                 "choices":next_question.choices}
    return result

def complete_lesson(db: Session, learner_id: str, course: Course) -> dict:
    p=get_or_create_progress(db, learner_id, course.id)
    p.lesson_complete=True
    if len(p.answered or [])==db.query(CourseQuestion).filter_by(course_id=course.id).count() and p.score>=80:
        p.mastery=True
    db.commit()
    return {"course_id":course.id,"lesson_complete":True,"mastery":p.mastery,"score":p.score,"credential_id":p.credential_id}