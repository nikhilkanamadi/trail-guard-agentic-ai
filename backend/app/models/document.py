"""Document model — TMF document metadata and storage tracking."""

from __future__ import annotations

import enum
import uuid
from datetime import date, datetime

from sqlalchemy import (
    BigInteger,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, TimestampMixin, UUIDPrimaryKeyMixin


class DocumentStatus(str, enum.Enum):
    """Lifecycle states for a document."""

    UPLOADED = "uploaded"
    PROCESSING = "processing"
    VALIDATED = "validated"
    FAILED = "failed"
    SUPERSEDED = "superseded"
    ARCHIVED = "archived"
    DELETED = "deleted"


class Document(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """A single document stored against a study in the TMF hierarchy."""

    __tablename__ = "documents"
    __table_args__ = (
        Index("ix_documents_study_id", "study_id"),
        Index("ix_documents_document_type", "document_type"),
        Index("ix_documents_tmf_zone", "tmf_zone"),
        Index("ix_documents_tmf_section", "tmf_section"),
        Index("ix_documents_status", "status"),
        Index("ix_documents_file_hash", "file_hash"),
        Index("ix_documents_uploaded_by", "uploaded_by"),
    )

    # ── Foreign Keys ─────────────────────────────────────────────────────
    study_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("studies.id", ondelete="CASCADE"),
        nullable=False,
    )
    uploaded_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # ── TMF Classification ───────────────────────────────────────────────
    document_type: Mapped[str] = mapped_column(String(100), nullable=False)
    tmf_zone: Mapped[int] = mapped_column(Integer, nullable=False)
    tmf_section: Mapped[str] = mapped_column(String(100), nullable=False)
    tmf_artifact: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # ── Document Metadata ────────────────────────────────────────────────
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    version: Mapped[str] = mapped_column(String(50), nullable=False, default="1.0")
    version_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    language: Mapped[str] = mapped_column(String(10), nullable=False, default="en")
    country_code: Mapped[str | None] = mapped_column(String(3), nullable=True)
    site_id: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # ── Storage ──────────────────────────────────────────────────────────
    file_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    file_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(255), nullable=False)
    page_count: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # ── Status ───────────────────────────────────────────────────────────
    status: Mapped[DocumentStatus] = mapped_column(
        String(50), nullable=False, default=DocumentStatus.UPLOADED
    )

    # ── Relationships ────────────────────────────────────────────────────
    study: Mapped["Study"] = relationship("Study", back_populates="documents")
    uploader: Mapped["User | None"] = relationship(
        "User", back_populates="uploaded_documents"
    )
    validation_runs: Mapped[list["ValidationRun"]] = relationship(
        "ValidationRun",
        back_populates="document",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    findings: Mapped[list["Finding"]] = relationship(
        "Finding",
        back_populates="document",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Document {self.title} v{self.version} [{self.status}]>"
