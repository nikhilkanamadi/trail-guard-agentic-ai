"""Pydantic v2 schemas for the User model."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserBase(BaseModel):
    """Shared user attributes."""

    email: EmailStr = Field(..., description="Unique email address", examples=["jane.doe@example.com"])
    full_name: str = Field(..., min_length=1, max_length=255, examples=["Jane Doe"])
    role: str = Field(default="viewer", examples=["reviewer"])
    organization: Optional[str] = Field(None, max_length=255, examples=["Clinical Research Org"])
    department: Optional[str] = Field(None, max_length=255, examples=["Clinical Operations"])


class UserCreate(UserBase):
    """Payload for creating a new user (includes password)."""

    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Plain-text password (will be hashed server-side)",
    )

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserUpdate(BaseModel):
    """Partial update payload."""

    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    role: Optional[str] = None
    organization: Optional[str] = None
    department: Optional[str] = None
    is_active: Optional[bool] = None
    mfa_enabled: Optional[bool] = None


class UserRead(UserBase):
    """User response schema (excludes password)."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    is_active: bool
    mfa_enabled: bool
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class UserList(BaseModel):
    """Paginated user list response."""

    items: List[UserRead]
    total: int
    page: int
    size: int


# ── Auth-specific schemas ────────────────────────────────────────────────

class LoginRequest(BaseModel):
    """Login payload."""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """JWT token response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Access token lifetime in seconds")


class TokenRefreshRequest(BaseModel):
    """Refresh token payload."""

    refresh_token: str
