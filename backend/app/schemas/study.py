"""Pydantic v2 schemas for the Study model."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class StudyBase(BaseModel):
    """Shared study attributes."""

    study_identifier: str = Field(
        ..., min_length=1, max_length=100,
        description="Internal study identifier",
        examples=["TG-2024-ONC-0042"],
    )
    sponsor_name: str = Field(..., min_length=1, max_length=255, examples=["AstraZeneca"])
    protocol_number: str = Field(..., min_length=1, max_length=100, examples=["AZ-ONC-2024-001"])
    therapeutic_area: str = Field(..., min_length=1, max_length=255, examples=["Oncology"])
    phase: str = Field(..., examples=["Phase 3"])
    status: str = Field(default="planning", examples=["active"])
    countries: Optional[List[str] | Dict[str, Any]] = Field(
        None, examples=[["US", "DE", "JP"]]
    )
    description: Optional[str] = Field(None, examples=["Phase 3 oncology trial for ..."])


class StudyCreate(StudyBase):
    """Payload for creating a new study."""

    pass


class StudyUpdate(BaseModel):
    """Partial update payload."""

    sponsor_name: Optional[str] = Field(None, min_length=1, max_length=255)
    protocol_number: Optional[str] = Field(None, min_length=1, max_length=100)
    therapeutic_area: Optional[str] = Field(None, min_length=1, max_length=255)
    phase: Optional[str] = None
    status: Optional[str] = None
    countries: Optional[List[str] | Dict[str, Any]] = None
    description: Optional[str] = None


class StudyRead(StudyBase):
    """Study response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class StudyList(BaseModel):
    """Paginated study list response."""

    items: List[StudyRead]
    total: int
    page: int
    size: int


class TMFArtifactSummary(BaseModel):
    """Summary of a single TMF artifact type within a study."""

    tmf_zone: int
    tmf_section: str
    tmf_artifact: Optional[str] = None
    document_count: int
    latest_version: Optional[str] = None
    latest_status: Optional[str] = None


class TMFOverview(BaseModel):
    """TMF completeness overview for a study."""

    study_id: uuid.UUID
    total_documents: int
    artifacts: List[TMFArtifactSummary]
    completeness_percentage: float
