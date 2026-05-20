"""Finding model — individual validation issues discovered by agents."""

from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, TimestampMixin, UUIDPrimaryKeyMixin


class FindingSeverity(str, enum.Enum):
    """Severity levels aligned with ICH-GCP impact classification."""

    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"
    INFO = "info"


class FindingStatus(str, enum.Enum):
    """Resolution lifecycle for a finding."""

    OPEN = "open"
    IN_REVIEW = "in_review"
    RESOLVED = "resolved"
    ESCALATED = "escalated"
    FALSE_POSITIVE = "false_positive"
    DEFERRED = "deferred"
    WONT_FIX = "wont_fix"


class Finding(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """A single validation finding produced by an agent."""

    __tablename__ = "findings"
    __table_args__ = (
        Index("ix_findings_validation_run_id", "validation_run_id"),
        Index("ix_findings_document_id", "document_id"),
        Index("ix_findings_severity", "severity"),
        Index("ix_findings_status", "status"),
        Index("ix_findings_agent_name", "agent_name"),
        Index("ix_findings_category", "category"),
        Index("ix_findings_finding_type", "finding_type"),
    )

    # ── Foreign Keys ─────────────────────────────────────────────────────
    validation_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("validation_runs.id", ondelete="CASCADE"),
        nullable=False,
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
    )

    # ── Agent & Classification ───────────────────────────────────────────
    agent_name: Mapped[str] = mapped_column(String(100), nullable=False)
    finding_type: Mapped[str] = mapped_column(String(100), nullable=False)
    severity: Mapped[FindingSeverity] = mapped_column(
        String(50), nullable=False, default=FindingSeverity.INFO
    )
    category: Mapped[str] = mapped_column(String(100), nullable=False)

    # ── Finding Detail ───────────────────────────────────────────────────
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    page_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    section_reference: Mapped[str | None] = mapped_column(String(255), nullable=True)
    regulatory_reference: Mapped[str | None] = mapped_column(
        String(500), nullable=True
    )
    suggested_remediation: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence_score: Mapped[float] = mapped_column(
        Float, nullable=False, default=1.0
    )

    # ── Resolution ───────────────────────────────────────────────────────
    status: Mapped[FindingStatus] = mapped_column(
        String(50), nullable=False, default=FindingStatus.OPEN
    )
    resolved_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    resolution_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ── Relationships ────────────────────────────────────────────────────
    validation_run: Mapped["ValidationRun"] = relationship(
        "ValidationRun", back_populates="findings"
    )
    document: Mapped["Document"] = relationship("Document", back_populates="findings")
    resolver: Mapped["User | None"] = relationship("User", foreign_keys=[resolved_by])

    def __repr__(self) -> str:
        return f"<Finding [{self.severity}] {self.title[:40]}>"
