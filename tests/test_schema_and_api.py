import sys
from pathlib import Path
import os

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

os.environ["APP_ENV"] = "test"
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["DEBUG"] = "true"
os.environ["TAXONOMY_INDEX_PATH"] = str(ROOT / "data" / "taxonomy_grant_index.json")
os.environ["OPPORTUNITIES_SEED_PATH"] = str(ROOT / "data" / "opportunities.json")

from app.core.config import get_settings
get_settings.cache_clear()

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.db.session as session_mod

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    future=True,
)
session_mod.engine = engine
session_mod.SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)

from app.db.base import Base
from app import models  # noqa
from app.main import app
from app.services.seed import seed_opportunities, seed_taxonomy
from fastapi.testclient import TestClient

Base.metadata.create_all(bind=engine)
db = session_mod.SessionLocal()
assert seed_taxonomy(db) >= 1
assert seed_opportunities(db) >= 1
db.close()


def _get_db():
    db = session_mod.SessionLocal()
    try:
        yield db
    finally:
        db.close()


from app.db import session as sess
from app.api import routes as routes_mod
# Override Depends(get_db) used in routes
app.dependency_overrides[sess.get_db] = _get_db

client = TestClient(app)


def test_health():
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["themes"] >= 1
    assert body["opportunities"] >= 1


def test_list_themes():
    r = client.get("/api/v1/themes")
    assert r.status_code == 200
    assert len(r.json()) >= 1


def test_list_opportunities_filter():
    r = client.get("/api/v1/opportunities", params={"status": "open"})
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_match_endpoint():
    r = client.post("/api/v1/match", json={"text": "human cognition AI working memory explainable"})
    assert r.status_code == 200
    body = r.json()
    assert "theme_ids" in body
    assert len(body["theme_ids"]) >= 1


def test_control_room_rebuild():
    r = client.post("/api/v1/control-room/rebuild")
    assert r.status_code == 200
    assert "summary" in r.json()
    r2 = client.get("/api/v1/control-room/queues")
    assert r2.status_code == 200
