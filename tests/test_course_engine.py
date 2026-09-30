import os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
os.environ["APP_ENV"]="test"
os.environ["DATABASE_URL"]="sqlite://"
os.environ["DEBUG"]="true"
os.environ["TAXONOMY_INDEX_PATH"]=str(ROOT/"data"/"taxonomy_grant_index.json")
os.environ["OPPORTUNITIES_SEED_PATH"]=str(ROOT/"data"/"opportunities.json")
from app.core.config import get_settings
get_settings.cache_clear()
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import app.db.session as session_mod
engine=create_engine("sqlite://",connect_args={"check_same_thread":False},poolclass=StaticPool)
session_mod.engine=engine
session_mod.SessionLocal=sessionmaker(bind=engine,autoflush=False,future=True)
from app.db.base import Base
from app import models
from app.main import app
from app.services.course_engine import seed_courses
from fastapi.testclient import TestClient
Base.metadata.create_all(bind=engine)
db=session_mod.SessionLocal(); assert seed_courses(db)==1; db.close()
def _db():
    db=session_mod.SessionLocal()
    try: yield db
    finally: db.close()
from app.db import session as sess
app.dependency_overrides[sess.get_db]=_db
client=TestClient(app)

def test_complete_course_vertical_slice():
    learner="test-learner"
    r=client.get("/api/v1/courses/SUB-0001"); assert r.status_code==200
    assert r.json()["question_count"]==5
    r=client.post("/api/v1/courses/SUB-0001/lesson/complete",json={"learner_id":learner}); assert r.status_code==200
    r=client.post("/api/v1/courses/SUB-0001/assessment/start",json={"learner_id":learner}); assert r.status_code==200
    q=r.json()["questions"][0]; assert q["ordinal"]==1
    for _ in range(5):
        rr=client.post("/api/v1/courses/SUB-0001/assessment/answer",json={"learner_id":learner,"question_id":q["id"],"answer":"WRONG"})
        assert rr.status_code==200
        body=rr.json()
        if body["remaining"]==0: break
        q=body["next_question"]
    # A fresh learner with all correct answers proves scoring/credential persistence.
    learner="mastered"
    client.post("/api/v1/courses/SUB-0001/lesson/complete",json={"learner_id":learner})
    q=client.post("/api/v1/courses/SUB-0001/assessment/start",json={"learner_id":learner}).json()["questions"][0]
    answers={
      1:"Which support combinations improve working memory without reducing independent recall",
      2:"Context-aware cueing at task boundaries can improve multi-step accuracy while preserving unaided recall",
      3:"Unaided recall and retained human capability",
      4:"Controlled task experiments",
      5:"To check that learners/users can question, pause or recover from assistance and later perform without it",
    }
    for _ in range(5):
        rr=client.post("/api/v1/courses/SUB-0001/assessment/answer",json={"learner_id":learner,"question_id":q["id"],"answer":answers[q["ordinal"]]})
        assert rr.status_code==200
        body=rr.json()
        if body["remaining"]==0: break
        q=body["next_question"]
    p=client.get("/api/v1/courses/SUB-0001/progress",params={"learner_id":learner})
    assert p.json()["score"]==100.0 and p.json()["mastery"] is True and p.json()["credential_id"]
    c=client.get("/api/v1/courses/SUB-0001/credential",params={"learner_id":learner})
    assert c.status_code==200


def test_adaptive_next_question_changes_difficulty():
    learner="adaptive"
    client.post("/api/v1/courses/SUB-0001/lesson/complete",json={"learner_id":learner})
    q=client.post("/api/v1/courses/SUB-0001/assessment/start",json={"learner_id":learner}).json()["questions"][0]
    assert q["difficulty"]==1
    rr=client.post("/api/v1/courses/SUB-0001/assessment/answer",json={"learner_id":learner,"question_id":q["id"],"answer":"Which support combinations improve working memory without reducing independent recall"})
    assert rr.status_code==200
    assert rr.json()["next_question"]["difficulty"]==2


def test_course_learner_ui_route():
    r=client.get("/course/SUB-0001")
    assert r.status_code==200
    assert "Working Memory Optimisation" in r.text
    assert "/api/v1/courses/SUB-0001/assessment/start" in r.text
