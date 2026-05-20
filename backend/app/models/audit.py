"""AuditTrail model — 21 CFR Part 11 compliant audit logging."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Index, String, Text, func
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class AuditTrail(Base):
    """Immutable audit log entry satisfying 21 CFR Part 11 requirements.

    Records are append-only; no UPDATE or DELETE should ever be issued
    against this table in production.
    """

    __tablename__ = "audit_trail"
    __table_args__ = (
        Index("ix_audit_trail_entity_type", "entity_type"),
        Index("ix_audit_trail_entity_id", "entity_id"),
        Index("ix_audit_trail_action", "action"),
        Index("ix_audit_trail_performed_by", "performed_by"),
        Index("ix_audit_trail_timestamp", "timestamp"),
        Index(
            "ix_audit_trail_entity_lookup",
            "entity_type",
            "entity_id",
        ),
    )

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )

    # ── What changed ─────────────────────────────────────────────────────
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(255), nullable=False)
    action: Mapped[str] = mapped_column(String(100), nullable=False)

    # ── Who ──────────────────────────────────────────────────────────────
    performed_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )

    # ── Before / After ───────────────────────────────────────────────────
    old_values: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    new_values: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # ── Request Context ──────────────────────────────────────────────────
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(512), nullable=True)

    # ── Part 11 Fields ───────────────────────────────────────────────────
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    electronic_signature: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # ── Timestamp ────────────────────────────────────────────────────────
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return (
            f"<AuditTrail #{self.id} {self.action} on "
            f"{self.entity_type}:{self.entity_id}>"
        )
