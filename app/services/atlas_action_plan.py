"""Turn live Atlas state into an immediately actionable work plan."""
from __future__ import annotations

from datetime import date
from typing import Any

from sqlalchemy.orm import Session

from app.models.atlas import Opportunity
from app.services.deep_match import compute_win_score


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
        if days is not None and days < 0 and o.status != "rolling":
            continue

        theme_ids = [link.theme_id for link in o.theme_links]
        win = compute_win_score(
            geography=o.geography or [],
            theme_ids=theme_ids,
            status=o.status,
            close_date=o.close_date,
            funder_type=o.funder_type,
            decision_hint=o.win_score.decision if o.win_score else None,
        )
        score = win["score"]
        decision = win["decision"]
        urgency = 100 if days is not None and days <= 14 else 75 if days is not None and days <= 30 else 50
        priority = round((score * 0.65) + (urgency * 0.35), 1)
        missing = [
            evidence.get("class")
            for evidence in (win.get("evidence_requirements") or [])
            if evidence.get("status") == "MISSING"
        ]
        next_action = (
            "Build submission evidence" if decision == "PURSUE"
            else "Find/confirm partner" if decision == "PARTNER"
            else "Review and decide"
        )
        candidates.append({
            "opportunity_id": o.id,
            "title": o.title,
            "funder": o.funder,
            "decision": decision,
            "win_score": score,
            "days_remaining": days,
            "priority": priority,
            "missing_evidence": missing,
            "next_action": next_action,
            "source_url": o.source_url,
            "application_url": o.application_url,
        })

    candidates.sort(key=lambda item: (-item["priority"], item["days_remaining"] if item["days_remaining"] is not None else 9999))
    return {
        "generated_at": today.isoformat(),
        "count": min(limit, len(candidates)),
        "items": candidates[:limit],
    }
