import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.services.deep_match import assign_queues, compute_win_score, deep_match_text


THEMES = [
    {
        "id": "THE-01",
        "keywords": ["cognition", "working memory", "explainable", "human"],
        "search_profile": {"queries": ["human-centered AI cognition working memory"]},
        "topics": [{"name": "Cognitive Performance"}],
    },
    {
        "id": "THE-05",
        "keywords": ["neural", "brain", "bci", "neuro"],
        "search_profile": {"queries": ["brain-computer interface neural integrity"]},
        "topics": [{"name": "Neurotechnology and BCI"}],
    },
]


def test_deep_match_cognition():
    m = deep_match_text("explainable AI human cognition working memory performance", THEMES)
    assert "THE-01" in m.theme_ids
    assert m.scores.get("THE-01", 0) > 0


def test_deep_match_neural():
    m = deep_match_text("brain neural BCI neurotechnology interface", THEMES)
    assert "THE-05" in m.theme_ids


def test_win_score_pursue_au():
    w = compute_win_score(
        geography=["AU"],
        theme_ids=["THE-01", "THE-05"],
        status="open",
        close_date="2026-11-04",
    )
    assert w["decision"] in ("PURSUE", "WATCH", "PARTNER")
    assert "dimensions" in w
    assert len(w["dimensions"]) == 14
    assert 0 <= w["score"] <= 100


def test_win_score_partner_uk():
    w = compute_win_score(
        geography=["UK"],
        theme_ids=["THE-01"],
        status="open",
        close_date="2026-10-20",
        funder_type="research_council",
    )
    assert w["dimensions"]["eligibility_confidence"] < 70
    assert w["decision"] in ("PARTNER", "WATCH")


def test_assign_queues_fast_track():
    win = {
        "decision": "PURSUE",
        "rationale": {"days_remaining": 10},
        "evidence_requirements": [{"status": "MISSING"}],
    }
    q = assign_queues({"status": "open", "close_date": "2026-08-28"}, win)
    assert "FAST_TRACK" in q
    assert "SUBMISSION_BUILD" in q
    assert "BLOCKED_EVIDENCE" in q
