from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class RuntimeEvent(Base):
    __tablename__ = "runtime_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    event_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, default=lambda: uuid4().hex)
    intent_id: Mapped[str] = mapped_column(String(64), index=True)
    receipt_id: Mapped[str] = mapped_column(String(64), index=True)
    actor_id: Mapped[str] = mapped_column(String(255))
    runtime_id: Mapped[str] = mapped_column(String(255))
    model_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    event: Mapped[str] = mapped_column(String(64), index=True)
    state_before: Mapped[str | None] = mapped_column(String(32), nullable=True)
    state_after: Mapped[str] = mapped_column(String(32))
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    authority_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
    parent_receipt: Mapped[str | None] = mapped_column(String(64), nullable=True)
    evidence_refs: Mapped[list] = mapped_column(JSON, default=list)
    provenance: Mapped[dict] = mapped_column(JSON, default=dict)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    replayable: Mapped[bool] = mapped_column(Boolean, default=True)
    previous_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)
    event_hash: Mapped[str] = mapped_column(String(128), index=True)
    claim: Mapped[str | None] = mapped_column(Text, nullable=True)
