"""Full Atlas schema models."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Theme(Base):
    __tablename__ = "themes"

    id: Mapped[str] = mapped_column(String(16), primary_key=True)  # THE-01
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    subtopic_count: Mapped[int] = mapped_column(Integer, default=0)
    high_priority_count: Mapped[int] = mapped_column(Integer, default=0)
    keywords: Mapped[Optional[dict]] = mapped_column(JSON, default=list)
    search_profile: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    topics: Mapped[list["Topic"]] = relationship(back_populates="theme", cascade="all, delete-orphan")


class Topic(Base):
    __tablename__ = "topics"
    __table_args__ = (UniqueConstraint("theme_id", "topic_id", name="uq_theme_topic"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    theme_id: Mapped[str] = mapped_column(String(16), ForeignKey("themes.id"), nullable=False)
    topic_id: Mapped[str] = mapped_column(String(32), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    subtopic_count: Mapped[int] = mapped_column(Integer, default=0)

    theme: Mapped["Theme"] = relationship(back_populates="topics")
    subtopics: Mapped[list["Subtopic"]] = relationship(back_populates="topic", cascade="all, delete-orphan")


class Subtopic(Base):
    __tablename__ = "subtopics"
    __table_args__ = (UniqueConstraint("topic_id", "subtopic_id", name="uq_topic_subtopic"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    topic_id: Mapped[int] = mapped_column(Integer, ForeignKey("topics.id"), nullable=False)
    subtopic_id: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(512), nullable=False)
    priority: Mapped[Optional[str]] = mapped_column(String(32))
    idea_id: Mapped[Optional[str]] = mapped_column(String(64))

    topic: Mapped["Topic"] = relationship(back_populates="subtopics")


class Opportunity(Base):
    __tablename__ = "opportunities"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    funder: Mapped[str] = mapped_column(String(255), nullable=False)
    funder_type: Mapped[Optional[str]] = mapped_column(String(64))
    programme: Mapped[Optional[str]] = mapped_column(String(255))
    geography: Mapped[Optional[dict]] = mapped_column(JSON, default=list)
    eligible_countries: Mapped[Optional[dict]] = mapped_column(JSON, default=list)
    status: Mapped[str] = mapped_column(String(32), default="unknown", index=True)
    open_date: Mapped[Optional[str]] = mapped_column(String(32))
    close_date: Mapped[Optional[str]] = mapped_column(String(32), index=True)
    value_min_aud: Mapped[Optional[float]] = mapped_column(Float)
    value_max_aud: Mapped[Optional[float]] = mapped_column(Float)
    value_total_pool_aud: Mapped[Optional[float]] = mapped_column(Float)
    currency_original: Mapped[Optional[str]] = mapped_column(String(8))
    value_notes: Mapped[Optional[str]] = mapped_column(Text)
    match_rationale: Mapped[Optional[str]] = mapped_column(Text)
    source_url: Mapped[Optional[str]] = mapped_column(Text)
    application_url: Mapped[Optional[str]] = mapped_column(Text)
    last_verified: Mapped[Optional[str]] = mapped_column(String(32))
    is_pattern: Mapped[bool] = mapped_column(Boolean, default=False)
    portal: Mapped[Optional[str]] = mapped_column(String(128))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    topic_hints: Mapped[Optional[dict]] = mapped_column(JSON, default=list)
    actions: Mapped[Optional[dict]] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    theme_links: Mapped[list["OpportunityTheme"]] = relationship(
        back_populates="opportunity", cascade="all, delete-orphan"
    )
    win_score: Mapped[Optional["WinScore"]] = relationship(
        back_populates="opportunity", uselist=False, cascade="all, delete-orphan"
    )
    funder_intel: Mapped[Optional["FunderIntelligence"]] = relationship(
        back_populates="opportunity", uselist=False, cascade="all, delete-orphan"
    )
    partner_state: Mapped[Optional["PartnerPipelineState"]] = relationship(
        back_populates="opportunity", uselist=False, cascade="all, delete-orphan"
    )


class OpportunityTheme(Base):
    __tablename__ = "opportunity_themes"
    __table_args__ = (UniqueConstraint("opportunity_id", "theme_id", name="uq_opp_theme"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    opportunity_id: Mapped[str] = mapped_column(String(64), ForeignKey("opportunities.id"), nullable=False)
    theme_id: Mapped[str] = mapped_column(String(16), ForeignKey("themes.id"), nullable=False)
    rank: Mapped[int] = mapped_column(Integer, default=0)

    opportunity: Mapped["Opportunity"] = relationship(back_populates="theme_links")


class WinScore(Base):
    __tablename__ = "win_scores"

    opportunity_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("opportunities.id"), primary_key=True
    )
    score: Mapped[float] = mapped_column(Float, nullable=False)
    decision: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    dimensions: Mapped[dict] = mapped_column(JSON, nullable=False)
    rationale: Mapped[Optional[dict]] = mapped_column(JSON)
    evidence_requirements: Mapped[Optional[dict]] = mapped_column(JSON)
    scored_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    opportunity: Mapped["Opportunity"] = relationship(back_populates="win_score")


class FunderIntelligence(Base):
    __tablename__ = "funder_intelligence"

    opportunity_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("opportunities.id"), primary_key=True
    )
    funder: Mapped[str] = mapped_column(String(255), nullable=False)
    funder_type: Mapped[Optional[str]] = mapped_column(String(64))
    portal: Mapped[Optional[str]] = mapped_column(String(128))
    geography: Mapped[Optional[dict]] = mapped_column(JSON)
    prior_winners_note: Mapped[Optional[str]] = mapped_column(Text)
    evaluator_language_hints: Mapped[Optional[dict]] = mapped_column(JSON)
    clarification_channel: Mapped[Optional[str]] = mapped_column(Text)
    extras: Mapped[Optional[dict]] = mapped_column(JSON)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    opportunity: Mapped["Opportunity"] = relationship(back_populates="funder_intel")


class PartnerPipelineState(Base):
    __tablename__ = "partner_pipeline_states"

    # DISCOVERED → QUALIFIED → INTRO_AVAILABLE → OUTREACH_APPROVAL → CONTACTED → …
    opportunity_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("opportunities.id"), primary_key=True
    )
    stage: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    opportunity: Mapped["Opportunity"] = relationship(back_populates="partner_state")


class ControlRoomQueueItem(Base):
    __tablename__ = "control_room_queue_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    queue: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    opportunity_id: Mapped[str] = mapped_column(String(64), ForeignKey("opportunities.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(512))
    decision: Mapped[Optional[str]] = mapped_column(String(16))
    close_date: Mapped[Optional[str]] = mapped_column(String(32))
    days_remaining: Mapped[Optional[int]] = mapped_column(Integer)
    score: Mapped[Optional[float]] = mapped_column(Float)
    payload: Mapped[Optional[dict]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
