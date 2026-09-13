from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from app.api.deps import verify_api_key
from app.db.session import get_db
from app.models.atlas import (
    ControlRoomQueueItem,
    Opportunity,
    Theme,
    WinScore,
)
from app.services.deep_match import assign_queues, compute_win_score, deep_match_text
from app.services.estate_context import build_estate_context
from app.services.seed import seed_opportunities, seed_taxonomy

router = APIRouter()


class MatchRequest(BaseModel):
    text: str = Field(..., min_length=3)
    top_n: int = 4


class MatchResponse(BaseModel):
    theme_ids: list[str]
    topic_hints: list[str]
    scores: dict[str, int]
    rationale: str


class OpportunityOut(BaseModel):
    id: str
    title: str
    funder: str
    status: str
    geography: list[str] = []
    close_date: Optional[str] = None
    value_max_aud: Optional[float] = None
    theme_ids: list[str] = []
    decision: Optional[str] = None
    score: Optional[float] = None
    source_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


@router.get("/health")
def health(db: Session = Depends(get_db)) -> dict[str, Any]:
    try:
        n = db.query(Theme).count()
        o = db.query(Opportunity).count()
        db_ok = True
    except Exception as e:
        n, o, db_ok = 0, 0, False
        return {"status": "degraded", "db": False, "error": str(e)}
    return {
        "status": "ok" if db_ok else "degraded",
        "db": db_ok,
        "themes": n,
        "opportunities": o,
    }


@router.get("/estate-context")
def estate_context(db: Session = Depends(get_db)) -> dict[str, Any]:
    """Return the live Atlas first-read context for connected AI contexts."""
    return build_estate_context(db)


@router.post("/admin/seed", dependencies=[Depends(verify_api_key)])
def admin_seed(db: Session = Depends(get_db)) -> dict[str, int]:
    nt = seed_taxonomy(db)
    no = seed_opportunities(db)
    return {"themes_seeded": nt, "opportunities_seeded": no}


@router.post("/match", response_model=MatchResponse)
def match(req: MatchRequest, db: Session = Depends(get_db)) -> MatchResponse:
    themes = db.query(Theme).all()
    payload = [
        {
            "id": t.id,
            "keywords": t.keywords or [],
            "search_profile": t.search_profile or {},
            "topics": [{"name": tp.name} for tp in t.topics],
        }
        for t in themes
    ]
    if not payload:
        raise HTTPException(400, "No themes loaded — run POST /admin/seed")
    m = deep_match_text(req.text, payload, top_n=req.top_n)
    return MatchResponse(
        theme_ids=m.theme_ids,
        topic_hints=m.topic_hints,
        scores=m.scores,
        rationale=m.rationale,
    )


@router.get("/themes")
def list_themes(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    out = []
    for t in db.query(Theme).order_by(Theme.id).all():
        out.append({
            "id": t.id,
            "name": t.name,
            "subtopic_count": t.subtopic_count,
            "high_priority_count": t.high_priority_count,
            "topics": [{"id": tp.topic_id, "name": tp.name} for tp in t.topics],
        })
    return out


@router.get("/opportunities", response_model=list[OpportunityOut])
def list_opportunities(
    status: Optional[str] = None,
    theme: Optional[str] = None,
    decision: Optional[str] = None,
    geo: Optional[str] = None,
    db: Session = Depends(get_db),
) -> list[OpportunityOut]:
    q = db.query(Opportunity)
    if status:
        q = q.filter(Opportunity.status == status)
    rows = q.all()
    result: list[OpportunityOut] = []
    for o in rows:
        tids = [l.theme_id for l in sorted(o.theme_links, key=lambda x: x.rank)]
        if theme and theme not in tids:
            continue
        if geo and geo not in (o.geography or []):
            continue
        dec = o.win_score.decision if o.win_score else None
        sc = o.win_score.score if o.win_score else None
        if decision and dec != decision:
            continue
        result.append(
            OpportunityOut(
                id=o.id,
                title=o.title,
                funder=o.funder,
                status=o.status,
                geography=o.geography or [],
                close_date=o.close_date,
                value_max_aud=o.value_max_aud,
                theme_ids=tids,
                decision=dec,
                score=sc,
                source_url=o.source_url,
            )
        )
    return result


@router.get("/opportunities/{opp_id}")
def get_opportunity(opp_id: str, db: Session = Depends(get_db)) -> dict[str, Any]:
    o = db.get(Opportunity, opp_id)
    if not o:
        raise HTTPException(404, "Not found")
    return {
        "id": o.id,
        "title": o.title,
        "funder": o.funder,
        "funder_type": o.funder_type,
        "programme": o.programme,
        "geography": o.geography,
        "status": o.status,
        "open_date": o.open_date,
        "close_date": o.close_date,
        "value_max_aud": o.value_max_aud,
        "value_notes": o.value_notes,
        "theme_ids": [l.theme_id for l in sorted(o.theme_links, key=lambda x: x.rank)],
        "topic_hints": o.topic_hints,
        "match_rationale": o.match_rationale,
        "win_score": {
            "score": o.win_score.score,
            "decision": o.win_score.decision,
            "dimensions": o.win_score.dimensions,
            "evidence_requirements": o.win_score.evidence_requirements,
        } if o.win_score else None,
        "funder_intelligence": {
            "funder": o.funder_intel.funder,
            "portal": o.funder_intel.portal,
            "evaluator_language_hints": o.funder_intel.evaluator_language_hints,
            "clarification_channel": o.funder_intel.clarification_channel,
        } if o.funder_intel else None,
        "partner_pipeline_stage": o.partner_state.stage if o.partner_state else None,
        "source_url": o.source_url,
        "application_url": o.application_url,
        "actions": o.actions,
    }


@router.post("/opportunities/{opp_id}/rescore")
def rescore(opp_id: str, db: Session = Depends(get_db)) -> dict[str, Any]:
    o = db.get(Opportunity, opp_id)
    if not o:
        raise HTTPException(404, "Not found")
    tids = [l.theme_id for l in o.theme_links]
    win = compute_win_score(
        geography=o.geography or [],
        theme_ids=tids,
        status=o.status,
        close_date=o.close_date,
        funder_type=o.funder_type,
    )
    if o.win_score:
        o.win_score.score = win["score"]
        o.win_score.decision = win["decision"]
        o.win_score.dimensions = win["dimensions"]
        o.win_score.rationale = win["rationale"]
        o.win_score.evidence_requirements = win["evidence_requirements"]
    else:
        o.win_score = WinScore(
            opportunity_id=o.id,
            score=win["score"],
            decision=win["decision"],
            dimensions=win["dimensions"],
            rationale=win["rationale"],
            evidence_requirements=win["evidence_requirements"],
        )
    db.commit()
    return win


@router.post("/control-room/rebuild")
def rebuild_control_room(db: Session = Depends(get_db)) -> dict[str, Any]:
    db.query(ControlRoomQueueItem).delete()
    summary: dict[str, int] = {}
    for o in db.query(Opportunity).all():
        if not o.win_score:
            continue
        win = {
            "decision": o.win_score.decision,
            "score": o.win_score.score,
            "rationale": o.win_score.rationale or {},
            "evidence_requirements": o.win_score.evidence_requirements or [],
        }
        for q in assign_queues(
            {"status": o.status, "close_date": o.close_date},
            win,
        ):
            days = (win.get("rationale") or {}).get("days_remaining")
            db.add(
                ControlRoomQueueItem(
                    queue=q,
                    opportunity_id=o.id,
                    title=o.title,
                    decision=o.win_score.decision,
                    close_date=o.close_date,
                    days_remaining=days,
                    score=o.win_score.score,
                )
            )
            summary[q] = summary.get(q, 0) + 1
    db.commit()
    return {"summary": summary}


@router.get("/control-room/queues")
def control_room_queues(db: Session = Depends(get_db)) -> dict[str, Any]:
    items = db.query(ControlRoomQueueItem).all()
    queues: dict[str, list] = {}
    for it in items:
        queues.setdefault(it.queue, []).append({
            "opportunity_id": it.opportunity_id,
            "title": it.title,
            "decision": it.decision,
            "close_date": it.close_date,
            "days_remaining": it.days_remaining,
            "score": it.score,
        })
    return {"queues": queues, "summary": {k: len(v) for k, v in queues.items()}}
