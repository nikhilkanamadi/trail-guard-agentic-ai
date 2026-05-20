"""ValidationRun model — tracks each validation pipeline execution."""

from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, TimestampMixin, UUIDPrimaryKeyMixin


class ValidationRunType(str, enum.Enum):
    """How the validation was initiated."""

    FULL = "full"
    INCREMENTAL = "incremental"
    TARGETED = "targeted"
    REVALIDATION = "revalidation"


class ValidationRunStatus(str, enum.Enum):
    """Pipeline execution states."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMED_OUT = "timed_out"
    AWAITING_REVIEW = "awaiting_review"


class ValidationRun(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """A single execution of the validation pipeline against a document."""

    __tablename__ = "validation_runs"
    __table_args__ = (
        Index("ix_validation_runs_document_id", "document_id"),
        Index("ix_validation_runs_study_id", "study_id"),
        Index("ix_validation_runs_status", "status"),
        Index("ix_validation_runs_run_type", "run_type"),
        Index(
            "ix_validation_runs_started_at",
            "started_at",
        ),
    )

    # ── Foreign Keys ─────────────────────────────────────────────────────
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
    )
    study_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("studies.id", ondelete="CASCADE"),
        nullable=False,
    )

    # ── Run Metadata ─────────────────────────────────────────────────────
    run_type: Mapped[ValidationRunType] = mapped_column(
        String(50), nullable=False, default=ValidationRunType.FULL
    )
    status: Mapped[ValidationRunStatus] = mapped_column(
        String(50), nullable=False, default=ValidationRunStatus.PENDING
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # ── Findings Aggregate ───────────────────────────────────────────────
    total_findings: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    critical_findings: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    major_findings: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    minor_findings: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    overall_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    # ── Traceability ─────────────────────────────────────────────────────
    triggered_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    celery_task_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    agent_trace: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # ── Relationships ────────────────────────────────────────────────────
    document: Mapped["Document"] = relationship(
        "Document", back_populates="validation_runs"
    )
    study: Mapped["Study"] = relationship("Study", back_populates="validation_runs")
    findings: Mapped[list["Finding"]] = relationship(
        "Finding",
        back_populates="validation_run",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<ValidationRun {self.id} [{self.status}] score={self.overall_score}>"
