"""Finding routes — list, update, resolve, escalate, false-positive."""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.database import get_db
from app.models.finding import Finding, FindingStatus
from app.models.user import User
from app.schemas.finding import (
    FindingEscalateRequest,
    FindingFalsePositiveRequest,
    FindingList,
    FindingRead,
    FindingResolveRequest,
    FindingUpdate,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "",
    response_model=FindingList,
    summary="List findings (filtered + paginated)",
)
async def list_findings(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    severity: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    agent_name: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    document_id: Optional[uuid.UUID] = Query(None),
    validation_run_id: Optional[uuid.UUID] = Query(None),
) -> FindingList:
    """Retrieve findings with optional filters on severity, status, agent, etc."""
    query = select(Finding)

    if severity:
        query = query.where(Finding.severity == severity)
    if status_filter:
        query = query.where(Finding.status == status_filter)
    if agent_name:
        query = query.where(Finding.agent_name == agent_name)
    if category:
        query = query.where(Finding.category == category)
    if document_id:
        query = query.where(Finding.document_id == document_id)
    if validation_run_id:
        query = query.where(Finding.validation_run_id == validation_run_id)

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar_one()

    query = (
        query.order_by(Finding.severity.asc(), Finding.created_at.desc())
        .offset((page - 1) * size)
        .limit(size)
    )
    result = await db.execute(query)
    items = list(result.scalars().all())

    return FindingList(items=items, total=total, page=page, size=size)


@router.put(
    "/{finding_id}",
    response_model=FindingRead,
    summary="Update a finding",
)
async def update_finding(
    finding_id: uuid.UUID,
    payload: FindingUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Finding:
    """Partially update finding metadata (severity, status, notes)."""
    result = await db.execute(select(Finding).where(Finding.id == finding_id))
    finding = result.scalar_one_or_none()
    if finding is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Finding not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(finding, field, value)

    await db.flush()
    await db.refresh(finding)
    logger.info("Finding %s updated by %s", finding_id, current_user.email)
    return finding


@router.post(
    "/{finding_id}/resolve",
    response_model=FindingRead,
    summary="Resolve a finding",
)
async def resolve_finding(
    finding_id: uuid.UUID,
    payload: FindingResolveRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Finding:
    """Mark a finding as resolved with notes."""
    result = await db.execute(select(Finding).where(Finding.id == finding_id))
    finding = result.scalar_one_or_none()
    if finding is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Finding not found")

    if finding.status == FindingStatus.RESOLVED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Finding is already resolved",
        )

    finding.status = FindingStatus.RESOLVED
    finding.resolved_by = current_user.id
    finding.resolved_at = datetime.now(timezone.utc)
    finding.resolution_notes = payload.resolution_notes

    await db.flush()
    await db.refresh(finding)
    logger.info("Finding %s resolved by %s", finding_id, current_user.email)
    return finding


@router.post(
    "/{finding_id}/escalate",
    response_model=FindingRead,
    summary="Escalate a finding",
)
async def escalate_finding(
    finding_id: uuid.UUID,
    payload: FindingEscalateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Finding:
    """Escalate a finding for management review."""
    result = await db.execute(select(Finding).where(Finding.id == finding_id))
    finding = result.scalar_one_or_none()
    if finding is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Finding not found")

    finding.status = FindingStatus.ESCALATED
    finding.resolution_notes = f"ESCALATED: {payload.reason}"

    await db.flush()
    await db.refresh(finding)
    logger.info("Finding %s escalated by %s: %s", finding_id, current_user.email, payload.reason)
    return finding


@router.post(
    "/{finding_id}/false-positive",
    response_model=FindingRead,
    summary="Mark finding as false positive",
)
async def mark_false_positive(
    finding_id: uuid.UUID,
    payload: FindingFalsePositiveRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Finding:
    """Mark a finding as a false positive with justification."""
    result = await db.execute(select(Finding).where(Finding.id == finding_id))
    finding = result.scalar_one_or_none()
    if finding is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Finding not found")

    finding.status = FindingStatus.FALSE_POSITIVE
    finding.resolved_by = current_user.id
    finding.resolved_at = datetime.now(timezone.utc)
    finding.resolution_notes = f"FALSE POSITIVE: {payload.justification}"

    await db.flush()
    await db.refresh(finding)
    logger.info(
        "Finding %s marked false-positive by %s",
        finding_id,
        current_user.email,
    )
    return finding
