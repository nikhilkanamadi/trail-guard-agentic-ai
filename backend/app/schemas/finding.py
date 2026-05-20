"""Pydantic v2 schemas for the Finding model."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class FindingBase(BaseModel):
    """Shared finding attributes."""

    agent_name: str = Field(..., max_length=100, examples=["compliance_agent"])
    finding_type: str = Field(..., max_length=100, examples=["missing_signature"])
    severity: str = Field(..., examples=["critical"])
    category: str = Field(..., max_length=100, examples=["ICH-GCP"])
    title: str = Field(..., min_length=1, max_length=500)
    description: str = Field(..., min_length=1)
    page_number: Optional[int] = Field(None, ge=0)
    section_reference: Optional[str] = Field(None, max_length=255)
    regulatory_reference: Optional[str] = Field(None, max_length=500)
    suggested_remediation: Optional[str] = None
    confidence_score: float = Field(default=1.0, ge=0.0, le=1.0)


class FindingCreate(FindingBase):
    """Payload for creating a finding (used internally by agents)."""

    validation_run_id: uuid.UUID
    document_id: uuid.UUID


class FindingUpdate(BaseModel):
    """Partial update — reviewers may adjust severity or status."""

    severity: Optional[str] = None
    status: Optional[str] = None
    resolution_notes: Optional[str] = None


class FindingRead(FindingBase):
    """Finding response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    validation_run_id: uuid.UUID
    document_id: uuid.UUID
    status: str
    resolved_by: Optional[uuid.UUID] = None
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class FindingList(BaseModel):
    """Paginated finding list."""

    items: List[FindingRead]
    total: int
    page: int
    size: int


class FindingResolveRequest(BaseModel):
    """Payload for resolving a finding."""

    resolution_notes: str = Field(..., min_length=1)


class FindingEscalateRequest(BaseModel):
    """Payload for escalating a finding."""

    reason: str = Field(..., min_length=1)


class FindingFalsePositiveRequest(BaseModel):
    """Payload for marking a finding as false positive."""

    justification: str = Field(..., min_length=1)
