"""Pydantic v2 schemas for the ValidationRun model."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ValidationRunCreate(BaseModel):
    """Payload to trigger a new validation run."""

    document_id: uuid.UUID
    study_id: uuid.UUID
    run_type: str = Field(default="full", examples=["full"])
    triggered_by: Optional[str] = Field(None, examples=["user:jane.doe@example.com"])


class ValidationRunRead(BaseModel):
    """Validation run response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    document_id: uuid.UUID
    study_id: uuid.UUID
    run_type: str
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    total_findings: int
    critical_findings: int
    major_findings: int
    minor_findings: int
    overall_score: Optional[float] = None
    triggered_by: Optional[str] = None
    celery_task_id: Optional[str] = None
    agent_trace: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime


class ValidationRunList(BaseModel):
    """Paginated validation run list."""

    items: List[ValidationRunRead]
    total: int
    page: int
    size: int


class ValidationRunCancel(BaseModel):
    """Response after cancelling a validation run."""

    id: uuid.UUID
    status: str
    message: str
