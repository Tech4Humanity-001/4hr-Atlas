"""Course engine: reusable, idempotent vertical slice."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from sqlalchemy.orm import Session
from app.core.config import ROOT
from app.models.course import Course, CourseCredential, CourseQuestion, LearnerProgress

SEED_PATH = ROOT / "data" / "course_seed.json"

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

def course_payload(db: Session, course: Course) -> dict:
    qs=db.query(CourseQuestion).filter_by(course_id=course.id).order_by(CourseQuestion.ordinal).all()
    return {"id":course.id,"subtopic_id":course.subtopic_id,"theme_id":course.theme_id,"topic_id":course.topic_id,
            "title":course.title,"intro":course.intro,"lesson":course.lesson,"source_url":course.source_url,
            "question_count":len(qs),"status":"READY"}

def start_assessment(db: Session, learner_id: str, course: Course) -> dict:
    p=get_or_create_progress(db, learner_id, course.id)
    p.assessment_started=True
    db.commit()
    qs=db.query(CourseQuestion).filter_by(course_id=course.id).order_by(CourseQuestion.ordinal).all()
    return {"course_id":course.id,"question_count":len(qs),
            "questions":[{"id":q.id,"ordinal":q.ordinal,"difficulty":q.difficulty,"prompt":q.prompt,"choices":q.choices} for q in qs]}

def answer_question(db: Session, learner_id: str, course: Course, question_id: str, answer: str) -> dict:
    q=db.get(CourseQuestion, question_id)
    if not q or q.course_id != course.id:
        raise ValueError("Unknown course question")
    p=get_or_create_progress(db, learner_id, course.id)
    answered=list(p.answered or [])
    if any(x["question_id"]==q.id for x in answered):
        raise ValueError("Question already answered")
    correct=answer.strip().casefold()==q.answer.strip().casefold()
    answered.append({"question_id":q.id,"correct":correct,"answer":answer,"difficulty":q.difficulty})
    p.answered=answered
    p.score=round(100*sum(1 for x in answered if x["correct"])/len(answered),2)
    if len(answered)==db.query(CourseQuestion).filter_by(course_id=course.id).count():
        p.mastery=p.lesson_complete and p.score>=80
        if p.mastery and not p.credential_id:
            digest=hashlib.sha256(f"{learner_id}:{course.id}:{p.score}".encode()).hexdigest()[:24]
            cid=f"ATL-CRED-{digest.upper()}"
            db.add(CourseCredential(id=cid,learner_id=learner_id,course_id=course.id,score=p.score,
                                    evidence={"questions":len(answered),"correct":sum(x["correct"] for x in answered),
                                              "lesson_complete":p.lesson_complete,"rule":"lesson_complete AND score >= 80"}))
            p.credential_id=cid
    db.commit()
    return {"correct":correct,"score":p.score,"answered":len(answered),
            "remaining":db.query(CourseQuestion).filter_by(course_id=course.id).count()-len(answered),
            "mastery":p.mastery,"credential_id":p.credential_id,"explanation":q.explanation}

def complete_lesson(db: Session, learner_id: str, course: Course) -> dict:
    p=get_or_create_progress(db, learner_id, course.id)
    p.lesson_complete=True
    if len(p.answered or [])==db.query(CourseQuestion).filter_by(course_id=course.id).count() and p.score>=80:
        p.mastery=True
    db.commit()
    return {"course_id":course.id,"lesson_complete":True,"mastery":p.mastery,"score":p.score,"credential_id":p.credential_id}
