"""Turn live Atlas state into an immediately actionable work plan."""
from __future__ import annotations

from datetime import date
from typing import Any

from sqlalchemy.orm import Session

from app.models.atlas import Opportunity


def build_action_plan(db: Session, limit: int = 10) -> dict[str, Any]:
    today = date.today()
    candidates = []
    for o in db.query(Opportunity).all():
        if o.status not in ("open", "upcoming", "rolling"):
            continue
        days = None
        if o.close_date:
            try:
                days = (date.fromisoformat(o.close_date) - today).days
            except ValueError:
                pass
        score = o.win_score.score if o.win_score else 0
        decision = o.win_score.decision if o.win_score else "UNSCORED"
        if days is not None and days < 0:
            continue
        urgency = 100 if days is not None and days <= 14 else 75 if days is not None and days <= 30 else 50
        priority = round((score * 0.65) + (urgency * 0.35), 1)
        missing = [
            e.get("class") for e in (o.win_score.evidence_requirements or [])
            if e.get("status") == "MISSING"
        ] if o.win_score else ["win_score"]
        candidates.append({
            "opportunity_id": o.id,
            "title": o.title,
            "funder": o.funder,
            "decision": decision,
            "win_score": score,
            "days_remaining": days,
            "priority": priority,
            "missing_evidence": missing,
            "next_action": "Build submission evidence" if decision == "PURSUE" else "Find/confirm partner" if decision == "PARTNER" else "Review and decide",
            "source_url": o.source_url,
            "application_url": o.application_url,
        })
    candidates.sort(key=lambda x: (-x["priority"], x["days_remaining"] if x["days_remaining"] is not None else 9999))
    return {
        "generated_at": date.today().isoformat(),
        "count": min(limit, len(candidates)),
        "items": candidates[:limit],
    }
