"""Pydantic v2 schemas for the AuditTrail model."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class AuditTrailRead(BaseModel):
    """Audit trail entry response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    entity_type: str
    entity_id: str
    action: str
    performed_by: Optional[uuid.UUID] = None
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    reason: Optional[str] = None
    electronic_signature: Optional[Dict[str, Any]] = None
    timestamp: datetime


class AuditTrailList(BaseModel):
    """Paginated audit trail response."""

    items: List[AuditTrailRead]
    total: int
    page: int
    size: int


class AuditTrailCreate(BaseModel):
    """Internal schema used by audit service to create entries."""

    entity_type: str = Field(..., max_length=100)
    entity_id: str = Field(..., max_length=255)
    action: str = Field(..., max_length=100)
    performed_by: Optional[uuid.UUID] = None
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    reason: Optional[str] = None
    electronic_signature: Optional[Dict[str, Any]] = None


class AuditTrailExport(BaseModel):
    """Export format metadata."""

    total_records: int
    export_format: str = "csv"
    download_url: Optional[str] = None
    generated_at: datetime
