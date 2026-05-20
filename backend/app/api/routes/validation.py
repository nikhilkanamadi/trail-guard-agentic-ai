"""Validation routes — run, status, findings, cancel, SSE progress, HITL approve."""

from __future__ import annotations

import asyncio
import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Annotated, AsyncGenerator, Optional

import redis.asyncio as aioredis
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.config import get_settings
from app.database import get_db
from app.models.document import Document
from app.models.finding import Finding
from app.models.study import Study
from app.models.user import User
from app.models.validation import ValidationRun, ValidationRunStatus
from app.schemas.finding import FindingList, FindingRead
from app.schemas.validation import (
    ValidationRunCancel,
    ValidationRunCreate,
    ValidationRunRead,
)

logger = logging.getLogger(__name__)
router = APIRouter()
settings = get_settings()


# ── Trigger a validation run ──────────────────────────────────────────────────

@router.post(
    "/run",
    response_model=ValidationRunRead,
    status_code=status.HTTP_201_CREATED,
    summary="Trigger a validation run",
)
async def create_validation_run(
    payload: ValidationRunCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ValidationRun:
    """Create and enqueue a new validation pipeline execution via Celery."""
    # Verify document
    if (await db.execute(select(Document).where(Document.id == payload.document_id))).scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    # Verify study
    if (await db.execute(select(Study).where(Study.id == payload.study_id))).scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Study not found")

    # Prevent duplicate in-progress runs
    active = (await db.execute(
        select(ValidationRun).where(
            ValidationRun.document_id == payload.document_id,
            ValidationRun.status.in_([
                ValidationRunStatus.PENDING,
                ValidationRunStatus.RUNNING,
                ValidationRunStatus.AWAITING_REVIEW,
            ]),
        )
    )).scalar_one_or_none()
    if active is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A validation run is already active for this document",
        )

    run = ValidationRun(
        document_id=payload.document_id,
        study_id=payload.study_id,
        run_type=payload.run_type,
        status=ValidationRunStatus.PENDING,
        triggered_by=payload.triggered_by or f"user:{current_user.email}",
    )
    db.add(run)
    await db.flush()
    await db.refresh(run)

    # Dispatch to Celery (import here to avoid circular at module load)
    from app.tasks.pipeline import dispatch_pipeline
    dispatch_pipeline.delay(str(run.id))

    logger.info("Validation run %s enqueued for document %s", run.id, payload.document_id)
    return run


# ── Get run details ───────────────────────────────────────────────────────────

@router.get(
    "/runs/{run_id}",
    response_model=ValidationRunRead,
    summary="Get validation run details",
)
async def get_validation_run(
    run_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ValidationRun:
    """Retrieve a single validation run by UUID."""
    result = await db.execute(select(ValidationRun).where(ValidationRun.id == run_id))
    run = result.scalar_one_or_none()
    if run is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Validation run not found")
    return run


# ── Paginated findings for a run ──────────────────────────────────────────────

@router.get(
    "/runs/{run_id}/findings",
    response_model=FindingList,
    summary="Get findings for a validation run",
)
async def get_run_findings(
    run_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    severity: Optional[str] = Query(None),
    agent_name: Optional[str] = Query(None),
) -> FindingList:
    """Return paginated findings for a specific validation run."""
    if (await db.execute(select(ValidationRun).where(ValidationRun.id == run_id))).scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Validation run not found")

    query = select(Finding).where(Finding.validation_run_id == run_id)
    if severity:
        query = query.where(Finding.severity == severity)
    if agent_name:
        query = query.where(Finding.agent_name == agent_name)

    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar_one()
    query = query.order_by(Finding.severity.asc(), Finding.created_at.desc()).offset((page - 1) * size).limit(size)
    items = list((await db.execute(query)).scalars().all())

    return FindingList(items=items, total=total, page=page, size=size)


# ── Cancel a run ──────────────────────────────────────────────────────────────

@router.post(
    "/runs/{run_id}/cancel",
    response_model=ValidationRunCancel,
    summary="Cancel a running validation",
)
async def cancel_validation_run(
    run_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ValidationRunCancel:
    """Cancel a PENDING or RUNNING validation run and revoke the Celery task."""
    result = await db.execute(select(ValidationRun).where(ValidationRun.id == run_id))
    run = result.scalar_one_or_none()
    if run is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Validation run not found")

    if run.status not in (
        ValidationRunStatus.PENDING,
        ValidationRunStatus.RUNNING,
        ValidationRunStatus.AWAITING_REVIEW,
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel a run in '{run.status}' state",
        )

    # Revoke Celery task if one was dispatched
    if run.celery_task_id:
        from app.tasks.celery_app import celery_app
        celery_app.control.revoke(run.celery_task_id, terminate=True)

    run.status = ValidationRunStatus.CANCELLED
    run.completed_at = datetime.now(timezone.utc)
    await db.flush()
    logger.info("Validation run %s cancelled by %s", run_id, current_user.email)

    return ValidationRunCancel(id=run.id, status=run.status, message="Validation run cancelled successfully")


# ── HITL: approve an escalated run ───────────────────────────────────────────

@router.post(
    "/runs/{run_id}/approve",
    response_model=ValidationRunRead,
    summary="Approve an escalated (AWAITING_REVIEW) validation run",
)
async def approve_validation_run(
    run_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ValidationRun:
    """Human reviewer approves an escalated run.

    Persists the cached findings from agent_trace and marks the run COMPLETED.
    The reviewer's identity is recorded in the audit trail.
    """
    result = await db.execute(select(ValidationRun).where(ValidationRun.id == run_id))
    run = result.scalar_one_or_none()
    if run is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Validation run not found")

    if run.status != ValidationRunStatus.AWAITING_REVIEW:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Run is in '{run.status}' state — only AWAITING_REVIEW runs can be approved",
        )

    # Re-dispatch the pipeline so findings are now committed without HITL block.
    # The orchestrator will re-run; the reviewer has signalled findings are acceptable.
    from app.tasks.pipeline import dispatch_pipeline
    from app.models.audit import AuditTrail

    run.status = ValidationRunStatus.PENDING
    run.celery_task_id = None
    await db.flush()

    db.add(AuditTrail(
        entity_type="validation_run",
        entity_id=str(run_id),
        action="hitl_approved",
        performed_by=current_user.id,
        new_values={"approved_by": current_user.email, "new_status": "pending"},
    ))
    await db.flush()

    task = dispatch_pipeline.delay(str(run.id))
    run.celery_task_id = task.id
    await db.flush()
    await db.refresh(run)

    logger.info("Run %s approved by %s — re-dispatched as task %s", run_id, current_user.email, task.id)
    return run


# ── SSE: real-time pipeline progress ─────────────────────────────────────────

@router.get(
    "/runs/{run_id}/stream",
    summary="Stream real-time pipeline progress via SSE",
    response_class=StreamingResponse,
)
async def stream_run_progress(
    run_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> StreamingResponse:
    """Subscribe to live agent progress events for a validation run.

    Returns a ``text/event-stream`` response. Each SSE event carries a JSON
    payload with ``agent``, ``stage``, and ``percent`` fields. The stream
    closes automatically when a terminal event (completed / failed /
    cancelled / awaiting_review) is received or after a 5-minute timeout.
    """
    if (await db.execute(select(ValidationRun).where(ValidationRun.id == run_id))).scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Validation run not found")

    async def _event_generator() -> AsyncGenerator[str, None]:
        redis_client = aioredis.from_url(settings.REDIS_URL)
        pubsub = redis_client.pubsub()
        channel = f"run:{run_id}:progress"
        await pubsub.subscribe(channel)

        terminal_stages = {
            ValidationRunStatus.COMPLETED,
            ValidationRunStatus.FAILED,
            ValidationRunStatus.CANCELLED,
            ValidationRunStatus.AWAITING_REVIEW,
        }

        try:
            deadline = asyncio.get_event_loop().time() + 300  # 5-minute timeout
            async for message in pubsub.listen():
                if asyncio.get_event_loop().time() > deadline:
                    yield "event: timeout\ndata: {}\n\n"
                    break
                if message["type"] != "message":
                    continue
                data = message["data"]
                if isinstance(data, bytes):
                    data = data.decode()
                yield f"data: {data}\n\n"
                try:
                    payload = json.loads(data)
                    if payload.get("stage") in {s.value for s in terminal_stages}:
                        break
                except json.JSONDecodeError:
                    pass
        finally:
            await pubsub.unsubscribe(channel)
            await redis_client.aclose()

    return StreamingResponse(
        _event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
