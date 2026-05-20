"""Audit trail routes — paginated query and export."""

from __future__ import annotations

import csv
import io
import logging
import uuid
from datetime import datetime, timezone
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_role
from app.database import get_db
from app.models.audit import AuditTrail
from app.models.user import User
from app.schemas.audit import AuditTrailList, AuditTrailRead

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/trail",
    response_model=AuditTrailList,
    summary="Query audit trail (filtered + paginated)",
)
async def list_audit_trail(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role(["admin", "manager"]))],
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    entity_type: Optional[str] = Query(None),
    entity_id: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    performed_by: Optional[uuid.UUID] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
) -> AuditTrailList:
    """Retrieve audit trail entries with optional filters."""
    query = select(AuditTrail)

    if entity_type:
        query = query.where(AuditTrail.entity_type == entity_type)
    if entity_id:
        query = query.where(AuditTrail.entity_id == entity_id)
    if action:
        query = query.where(AuditTrail.action == action)
    if performed_by:
        query = query.where(AuditTrail.performed_by == performed_by)
    if start_date:
        query = query.where(AuditTrail.timestamp >= start_date)
    if end_date:
        query = query.where(AuditTrail.timestamp <= end_date)

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar_one()

    query = (
        query.order_by(AuditTrail.timestamp.desc())
        .offset((page - 1) * size)
        .limit(size)
    )
    result = await db.execute(query)
    items = list(result.scalars().all())

    return AuditTrailList(items=items, total=total, page=page, size=size)


@router.get(
    "/trail/export",
    summary="Export audit trail as CSV",
    response_class=StreamingResponse,
)
async def export_audit_trail(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role(["admin"]))],
    entity_type: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
) -> StreamingResponse:
    """Export the audit trail as a downloadable CSV file.

    Restricted to admin users for data-governance compliance.
    """
    query = select(AuditTrail)
    if entity_type:
        query = query.where(AuditTrail.entity_type == entity_type)
    if start_date:
        query = query.where(AuditTrail.timestamp >= start_date)
    if end_date:
        query = query.where(AuditTrail.timestamp <= end_date)

    query = query.order_by(AuditTrail.timestamp.desc())
    result = await db.execute(query)
    entries = list(result.scalars().all())

    # Build CSV in-memory
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "id", "entity_type", "entity_id", "action", "performed_by",
        "ip_address", "user_agent", "reason", "timestamp",
    ])
    for entry in entries:
        writer.writerow([
            entry.id,
            entry.entity_type,
            entry.entity_id,
            entry.action,
            str(entry.performed_by) if entry.performed_by else "",
            entry.ip_address or "",
            entry.user_agent or "",
            entry.reason or "",
            entry.timestamp.isoformat(),
        ])

    output.seek(0)
    filename = f"audit_trail_export_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.csv"
    logger.info("Audit trail exported by %s (%d records)", current_user.email, len(entries))

    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
