from datetime import date, timedelta

from app.services.atlas_action_plan import build_action_plan
from app.models.atlas import Opportunity, WinScore


def test_action_plan_ranks_high_score_and_urgent_work(db_session):
    urgent = Opportunity(id="TEST-URGENT", title="Urgent", funder="Test", status="open", geography=["AU"], close_date=(date.today() + timedelta(days=7)).isoformat())
    urgent.win_score = WinScore(opportunity_id=urgent.id, score=80, decision="PURSUE", evidence_requirements=[{"class": "case_studies", "status": "MISSING"}])
    later = Opportunity(id="TEST-LATER", title="Later", funder="Test", status="open", geography=["AU"], close_date=(date.today() + timedelta(days=90)).isoformat())
    later.win_score = WinScore(opportunity_id=later.id, score=60, decision="WATCH", evidence_requirements=[])
    db_session.add_all([urgent, later])
    db_session.commit()

    plan = build_action_plan(db_session, limit=10)
    assert plan["items"][0]["opportunity_id"] == "TEST-URGENT"
    assert plan["items"][0]["next_action"] == "Build submission evidence"
    assert "case_studies" in plan["items"][0]["missing_evidence"]
