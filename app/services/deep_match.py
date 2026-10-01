"""Atlas deep-match engine: text → themes/topics + opportunity scoring helpers."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any, Optional


TODAY = date.today()

WIN_DIMENSION_KEYS = [
    "eligibility_confidence",
    "strategic_research_fit",
    "evidence_strength",
    "demonstrated_capability_trl",
    "funder_relationship",
    "partner_strength",
    "differentiation",
    "evaluator_language_alignment",
    "deadline_feasibility",
    "application_effort",
    "co_contribution_exposure",
    "competitive_intensity",
    "commercial_ip_leverage",
    "probability_of_award",
]


@dataclass
class MatchResult:
    theme_ids: list[str] = field(default_factory=list)
    topic_hints: list[str] = field(default_factory=list)
    scores: dict[str, int] = field(default_factory=dict)
    rationale: str = ""


def deep_match_text(text: str, themes: list[dict[str, Any]], top_n: int = 4) -> MatchResult:
    """Map free text / opportunity blob to taxonomy themes using keywords + search profiles."""
    blob = (text or "").lower()
    scored: list[tuple[int, str]] = []
    topic_hints: list[str] = []

    for theme in themes:
        tid = theme["id"] if "id" in theme else theme.get("theme_id")
        kws = theme.get("keywords") or theme.get("top_keywords") or []
        score = 0
        for kw in kws:
            k = str(kw).lower().replace("-", " ")
            if k and k in blob:
                score += 1
        profile = theme.get("search_profile") or theme.get("grant_search_profile") or {}
        for q in profile.get("queries") or []:
            for token in str(q).lower().split():
                if len(token) > 4 and token in blob:
                    score += 2
        if score > 0:
            scored.append((score, tid))
        for t in theme.get("topics") or []:
            name = t.get("name") or t.get("topic") or ""
            if any(len(w) > 4 and w in blob for w in name.lower().split()):
                topic_hints.append(name)

    scored.sort(reverse=True)
    theme_ids = [t for _, t in scored[:top_n]] or (["THE-01"] if themes else [])
    rationale = "Matched: " + ", ".join(f"{t}({s})" for s, t in scored[:top_n])
    return MatchResult(
        theme_ids=theme_ids,
        topic_hints=list(dict.fromkeys(topic_hints))[:6],
        scores={t: s for s, t in scored},
        rationale=rationale,
    )


def compute_win_score(
    *,
    geography: list[str],
    theme_ids: list[str],
    status: str,
    close_date: Optional[str],
    funder_type: Optional[str] = None,
    decision_hint: Optional[str] = None,
) -> dict[str, Any]:
    days = None
    if close_date:
        try:
            days = (date.fromisoformat(close_date) - TODAY).days
        except ValueError:
            days = None

    elig = 80 if "AU" in geography else 40
    if funder_type == "university" and "US" in geography:
        elig = 35

    fit = min(95, 70 + min(20, len(theme_ids) * 5))

    if days is None:
        dfeas = 50 if status == "rolling" else 40
    elif days < 0:
        dfeas = 5
    elif days <= 14:
        dfeas = 25
    elif days <= 45:
        dfeas = 60
    else:
        dfeas = 80

    dims = {
        "eligibility_confidence": elig,
        "strategic_research_fit": fit,
        "evidence_strength": 25,
        "demonstrated_capability_trl": 30,
        "funder_relationship": 20,
        "partner_strength": 35 if decision_hint == "PARTNER" else 25,
        "differentiation": 70,
        "evaluator_language_alignment": 40,
        "deadline_feasibility": dfeas,
        "application_effort": 45,
        "co_contribution_exposure": 60,
        "competitive_intensity": 40,
        "commercial_ip_leverage": 55,
        "probability_of_award": 0,
    }
    dims["probability_of_award"] = int(
        0.25 * dims["eligibility_confidence"]
        + 0.25 * dims["strategic_research_fit"]
        + 0.15 * dims["deadline_feasibility"]
        + 0.15 * dims["evidence_strength"]
        + 0.10 * dims["partner_strength"]
        + 0.10 * dims["differentiation"]
    )
    score = round(sum(dims.values()) / len(dims), 1)

    if days is not None and days < 0 and status != "rolling":
        decision = "WATCH"
    elif elig >= 70 and fit >= 75 and dfeas >= 50:
        decision = "PURSUE"
    elif fit >= 80 and elig < 60:
        decision = "PARTNER"
    else:
        decision = decision_hint or "WATCH"

    if score >= 55 and dims["eligibility_confidence"] >= 70 and dims["deadline_feasibility"] >= 50:
        decision = "PURSUE"
    elif dims["strategic_research_fit"] >= 75 and dims["eligibility_confidence"] < 55:
        decision = "PARTNER"

    return {
        "score": score,
        "decision": decision,
        "dimensions": dims,
        "rationale": {"theme_ids": theme_ids, "days_remaining": days},
        "evidence_requirements": [
            {"class": "entity", "status": "PARTIAL"},
            {"class": "CV/bio", "status": "PARTIAL"},
            {"class": "case_studies", "status": "MISSING"},
            {"class": "TRL/test", "status": "MISSING"},
            {
                "class": "partner_letters",
                "status": "MISSING" if decision == "PARTNER" else "N/A",
            },
        ],
    }


def assign_queues(opp: dict[str, Any], win: dict[str, Any]) -> list[str]:
    queues: list[str] = []
    decision = win.get("decision")
    days = win.get("rationale", {}).get("days_remaining")
    status = opp.get("status")

    if days is not None and 0 <= days <= 30 and status in ("open", "upcoming"):
        queues.append("FAST_TRACK")
    if decision == "PURSUE":
        queues.extend(["SUBMISSION_BUILD", "RED_TEAM"])
        ev = win.get("evidence_requirements") or []
        if any(e.get("status") == "MISSING" for e in ev):
            queues.append("BLOCKED_EVIDENCE")
    if decision == "PARTNER":
        queues.append("PARTNER_APPROVAL")
    if status == "open" and decision in ("PURSUE", "PARTNER"):
        queues.append("NEEDS_TROY")
    return queues
