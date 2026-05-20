"""Study model — clinical trial / protocol metadata."""

from __future__ import annotations

import enum
import uuid
from typing import List

from sqlalchemy import Index, String, Text
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, TimestampMixin, UUIDPrimaryKeyMixin


class StudyPhase(str, enum.Enum):
    """Standard clinical trial phases."""

    PHASE_1 = "Phase 1"
    PHASE_1A = "Phase 1a"
    PHASE_1B = "Phase 1b"
    PHASE_2 = "Phase 2"
    PHASE_2A = "Phase 2a"
    PHASE_2B = "Phase 2b"
    PHASE_3 = "Phase 3"
    PHASE_3A = "Phase 3a"
    PHASE_3B = "Phase 3b"
    PHASE_4 = "Phase 4"
    NOT_APPLICABLE = "Not Applicable"


class StudyStatus(str, enum.Enum):
    """Lifecycle states for a study."""

    PLANNING = "planning"
    ACTIVE = "active"
    ENROLLING = "enrolling"
    CLOSED = "closed"
    COMPLETED = "completed"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"
    WITHDRAWN = "withdrawn"


class Study(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Represents a single clinical trial / study."""

    __tablename__ = "studies"
    __table_args__ = (
        Index("ix_studies_study_identifier", "study_identifier", unique=True),
        Index("ix_studies_sponsor_name", "sponsor_name"),
        Index("ix_studies_protocol_number", "protocol_number"),
        Index("ix_studies_therapeutic_area", "therapeutic_area"),
        Index("ix_studies_phase", "phase"),
        Index("ix_studies_status", "status"),
    )

    study_identifier: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False
    )
    sponsor_name: Mapped[str] = mapped_column(String(255), nullable=False)
    protocol_number: Mapped[str] = mapped_column(String(100), nullable=False)
    therapeutic_area: Mapped[str] = mapped_column(String(255), nullable=False)
    phase: Mapped[StudyPhase] = mapped_column(String(50), nullable=False)
    status: Mapped[StudyStatus] = mapped_column(
        String(50), nullable=False, default=StudyStatus.PLANNING
    )
    countries: Mapped[dict | list | None] = mapped_column(JSON, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ── Relationships ────────────────────────────────────────────────────
    documents: Mapped[list["Document"]] = relationship(
        "Document",
        back_populates="study",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    validation_runs: Mapped[list["ValidationRun"]] = relationship(
        "ValidationRun",
        back_populates="study",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Study {self.study_identifier} – {self.protocol_number}>"
