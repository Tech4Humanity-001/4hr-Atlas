"""Seed taxonomy + opportunities into Atlas DB."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.atlas import (
    FunderIntelligence,
    Opportunity,
    OpportunityTheme,
    PartnerPipelineState,
    Theme,
    Topic,
    WinScore,
)
from app.services.deep_match import compute_win_score, deep_match_text


def _load(path: str) -> Any:
    p = Path(path)
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def seed_taxonomy(db: Session) -> int:
    settings = get_settings()
    data = _load(settings.taxonomy_index_path)
    if not data:
        return 0
    n = 0
    for t in data:
        tid = t.get("theme_id") or t.get("id")
        theme = db.get(Theme, tid)
        if not theme:
            theme = Theme(id=tid)
            db.add(theme)
        theme.name = t.get("theme") or t.get("name") or tid
        theme.subtopic_count = t.get("subtopic_count") or 0
        theme.high_priority_count = t.get("high_priority_count") or 0
        theme.keywords = t.get("top_keywords") or t.get("keywords") or []
        theme.search_profile = t.get("grant_search_profile") or t.get("search_profile") or {}
        # topics
        existing = {x.topic_id: x for x in theme.topics}
        for tp in t.get("topics") or []:
            tpid = tp.get("topic_id")
            if tpid in existing:
                existing[tpid].name = tp.get("topic") or tp.get("name") or tpid
                existing[tpid].subtopic_count = tp.get("subtopic_count") or 0
            else:
                theme.topics.append(
                    Topic(
                        topic_id=tpid,
                        name=tp.get("topic") or tp.get("name") or tpid,
                        subtopic_count=tp.get("subtopic_count") or 0,
                    )
                )
        n += 1
    db.commit()
    return n


def seed_opportunities(db: Session) -> int:
    settings = get_settings()
    data = _load(settings.opportunities_seed_path)
    if not data:
        return 0
    themes_rows = db.query(Theme).all()
    themes_payload = [
        {
            "id": th.id,
            "keywords": th.keywords or [],
            "search_profile": th.search_profile or {},
            "topics": [{"topic_id": tp.topic_id, "name": tp.name} for tp in th.topics],
        }
        for th in themes_rows
    ]
    n = 0
    for row in data:
        oid = row["opportunity_id"]
        opp = db.get(Opportunity, oid)
        if not opp:
            opp = Opportunity(id=oid)
            db.add(opp)
        for field in (
            "title", "funder", "funder_type", "programme", "status", "open_date",
            "close_date", "value_min_aud", "value_max_aud", "value_total_pool_aud",
            "currency_original", "value_notes", "match_rationale", "source_url",
            "application_url", "last_verified", "portal", "notes",
        ):
            if field in row:
                setattr(opp, field, row[field])
        opp.geography = row.get("geography") or []
        opp.eligible_countries = row.get("eligible_countries") or []
        opp.topic_hints = row.get("topic_hints") or []
        opp.actions = row.get("actions") or []
        opp.is_pattern = bool(row.get("is_pattern"))

        # theme links — prefer provided theme_ids, else deep-match
        theme_ids = row.get("theme_ids") or []
        if not theme_ids:
            blob = " ".join([
                row.get("title") or "",
                row.get("match_rationale") or "",
                " ".join(row.get("topic_hints") or []),
            ])
            match = deep_match_text(blob, themes_payload)
            theme_ids = match.theme_ids
            if not opp.match_rationale:
                opp.match_rationale = match.rationale

        opp.theme_links.clear()
        for rank, tid in enumerate(theme_ids):
            if db.get(Theme, tid):
                opp.theme_links.append(OpportunityTheme(theme_id=tid, rank=rank))

        # WIN_SCORE
        win = compute_win_score(
            geography=opp.geography or [],
            theme_ids=theme_ids,
            status=opp.status or "unknown",
            close_date=opp.close_date,
            funder_type=opp.funder_type,
            decision_hint=(row.get("win_score_seed") or {}).get("suggested_decision"),
        )
        if opp.win_score:
            opp.win_score.score = win["score"]
            opp.win_score.decision = win["decision"]
            opp.win_score.dimensions = win["dimensions"]
            opp.win_score.rationale = win["rationale"]
            opp.win_score.evidence_requirements = win["evidence_requirements"]
        else:
            opp.win_score = WinScore(
                score=win["score"],
                decision=win["decision"],
                dimensions=win["dimensions"],
                rationale=win["rationale"],
                evidence_requirements=win["evidence_requirements"],
            )

        # Funder intel
        stage = "OUTREACH_APPROVAL" if win["decision"] == "PARTNER" else "DISCOVERED"
        if opp.funder_intel:
            opp.funder_intel.funder = opp.funder
            opp.funder_intel.funder_type = opp.funder_type
            opp.funder_intel.portal = opp.portal
            opp.funder_intel.geography = opp.geography
            opp.funder_intel.evaluator_language_hints = opp.topic_hints
            opp.funder_intel.clarification_channel = opp.source_url
        else:
            opp.funder_intel = FunderIntelligence(
                funder=opp.funder,
                funder_type=opp.funder_type,
                portal=opp.portal,
                geography=opp.geography,
                evaluator_language_hints=opp.topic_hints,
                clarification_channel=opp.source_url,
                prior_winners_note="Populate from portal award lists on refresh",
            )

        if opp.partner_state:
            opp.partner_state.stage = stage
        else:
            opp.partner_state = PartnerPipelineState(stage=stage)

        n += 1
    db.commit()
    return n
