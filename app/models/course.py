"""Reusable Atlas course-engine persistence models."""
from __future__ import annotations
from datetime import datetime
from typing import Optional
from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint, JSON, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class Course(Base):
    __tablename__ = "courses"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    subtopic_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    theme_id: Mapped[str] = mapped_column(String(32), nullable=False)
    topic_id: Mapped[str] = mapped_column(String(32), nullable=False)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    intro: Mapped[str] = mapped_column(Text, nullable=False)
    lesson: Mapped[str] = mapped_column(Text, nullable=False)
    source_url: Mapped[Optional[str]] = mapped_column(Text)
    version: Mapped[str] = mapped_column(String(32), default="1")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class CourseQuestion(Base):
    __tablename__ = "course_questions"
    __table_args__ = (UniqueConstraint("course_id", "ordinal", name="uq_course_question_ordinal"),)
    id: Mapped[str] = mapped_column(String(96), primary_key=True)
    course_id: Mapped[str] = mapped_column(String(64), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    ordinal: Mapped[int] = mapped_column(Integer, nullable=False)
    difficulty: Mapped[int] = mapped_column(Integer, nullable=False)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    choices: Mapped[list] = mapped_column(JSON, nullable=False)
    answer: Mapped[str] = mapped_column(String(255), nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)

class LearnerProgress(Base):
    __tablename__ = "learner_course_progress"
    __table_args__ = (UniqueConstraint("learner_id", "course_id", name="uq_learner_course"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    learner_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    course_id: Mapped[str] = mapped_column(String(64), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    lesson_complete: Mapped[bool] = mapped_column(default=False)
    assessment_started: Mapped[bool] = mapped_column(default=False)
    answered: Mapped[list] = mapped_column(JSON, default=list)
    score: Mapped[float] = mapped_column(Float, default=0.0)
    mastery: Mapped[bool] = mapped_column(default=False)
    credential_id: Mapped[Optional[str]] = mapped_column(String(128))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class CourseCredential(Base):
    __tablename__ = "course_credentials"
    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    learner_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    course_id: Mapped[str] = mapped_column(String(64), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    evidence: Mapped[dict] = mapped_column(JSON, nullable=False)
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
