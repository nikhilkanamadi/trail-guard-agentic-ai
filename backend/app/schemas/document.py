"""Pydantic v2 schemas for the Document model."""

from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class DocumentBase(BaseModel):
    """Shared document attributes."""

    document_type: str = Field(..., max_length=100, examples=["Protocol"])
    tmf_zone: int = Field(..., ge=1, le=11, description="TMF Reference Model zone 1-11")
    tmf_section: str = Field(..., max_length=100, examples=["01.01"])
    tmf_artifact: Optional[str] = Field(None, max_length=255, examples=["Final Protocol"])
    title: str = Field(..., min_length=1, max_length=500, examples=["Protocol v3.0 Final"])
    version: str = Field(default="1.0", max_length=50)
    version_date: Optional[date] = None
    language: str = Field(default="en", max_length=10)
    country_code: Optional[str] = Field(None, max_length=3, examples=["US"])
    site_id: Optional[str] = Field(None, max_length=100)


class DocumentCreate(DocumentBase):
    """Payload for creating a new document (metadata portion; file via multipart)."""

    study_id: uuid.UUID


class DocumentUpdate(BaseModel):
    """Partial update payload."""

    title: Optional[str] = Field(None, min_length=1, max_length=500)
    version: Optional[str] = Field(None, max_length=50)
    version_date: Optional[date] = None
    tmf_zone: Optional[int] = Field(None, ge=1, le=11)
    tmf_section: Optional[str] = Field(None, max_length=100)
    tmf_artifact: Optional[str] = None
    language: Optional[str] = None
    country_code: Optional[str] = None
    site_id: Optional[str] = None
    status: Optional[str] = None


class DocumentRead(DocumentBase):
    """Document response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    study_id: uuid.UUID
    uploaded_by: Optional[uuid.UUID] = None
    file_path: str
    file_hash: str
    file_size_bytes: int
    mime_type: str
    page_count: Optional[int] = None
    status: str
    created_at: datetime
    updated_at: datetime


class DocumentList(BaseModel):
    """Paginated document list response."""

    items: List[DocumentRead]
    total: int
    page: int
    size: int


class DocumentVersionRead(BaseModel):
    """Lightweight version info."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    version: str
    version_date: Optional[date] = None
    status: str
    file_hash: str
    created_at: datetime
