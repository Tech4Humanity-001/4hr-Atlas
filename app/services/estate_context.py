"""Build the live Atlas estate context returned to connected AI contexts."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.models.atlas import (
    ControlRoomQueueItem,
    FunderIntelligence,
    Opportunity,
    PartnerPipelineState,
    Subtopic,
    Theme,
    Topic,
    WinScore,
)

CONTEXT_VERSION = "0.1"
ESTATE_ID = "t4h-atlas"


def build_estate_context(db: Session) -> dict[str, Any]:
    """Return a compact, live snapshot suitable for an AI first-read."""
    themes = db.query(Theme).count()
    topics = db.query(Topic).count()
    subtopics = db.query(Subtopic).count()
    opportunities = db.query(Opportunity).count()
    win_scores = db.query(WinScore).count()
    funder_intelligence = db.query(FunderIntelligence).count()
    partner_pipeline = db.query(PartnerPipelineState).count()
    control_room_items = db.query(ControlRoomQueueItem).count()

    return {
        "estate_id": ESTATE_ID,
        "estate_name": "T4H Atlas ENH",
        "context_version": CONTEXT_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "connected",
        "truth_source": "live_atlas_database",
        "purpose": "Research spine and opportunity decision system for Tech 4 Humanity.",
        "capabilities": [
            "taxonomy",
            "deep_match",
            "opportunity_discovery",
            "WIN_SCORE",
            "funder_intelligence",
            "partner_pipeline",
            "control_room",
        ],
        "live_state": {
            "themes": themes,
            "topics": topics,
            "subtopics": subtopics,
            "opportunities": opportunities,
            "win_scores": win_scores,
            "funder_intelligence": funder_intelligence,
            "partner_pipeline_states": partner_pipeline,
            "control_room_queue_items": control_room_items,
        },
        "entry": {
            "required_first_read": True,
            "next": "Load relevant Atlas evidence and current work before substantive estate work.",
        },
        "evidence": {
            "repository": "Tech4Humanity-001/4hr-Atlas",
            "source_paths": [
                "data/taxonomy_grant_index.json",
                "data/opportunities.json",
                "app/models/atlas.py",
                "app/services/deep_match.py",
                "app/api/routes.py",
            ],
        },
    }
