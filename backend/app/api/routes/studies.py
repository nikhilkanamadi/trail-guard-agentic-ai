"""Study CRUD routes with pagination, filtering, and TMF overview."""

from __future__ import annotations

import logging
import uuid
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.database import get_db
from app.models.document import Document
from app.models.study import Study
from app.models.user import User
from app.schemas.study import (
    StudyCreate,
    StudyList,
    StudyRead,
    StudyUpdate,
    TMFArtifactSummary,
    TMFOverview,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "",
    response_model=StudyRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new study",
)
async def create_study(
    payload: StudyCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Study:
    """Register a new clinical trial in the system."""
    # Unique-constraint guard
    existing = await db.execute(
        select(Study).where(Study.study_identifier == payload.study_identifier)
    )
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Study with ID '{payload.study_identifier}' already exists",
        )

    study = Study(**payload.model_dump())
    db.add(study)
    await db.flush()
    await db.refresh(study)
    logger.info("Study created: %s by %s", study.study_identifier, current_user.email)
    return study


@router.get(
    "",
    response_model=StudyList,
    summary="List studies (paginated + filtered)",
)
async def list_studies(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    sponsor_name: Optional[str] = Query(None),
    therapeutic_area: Optional[str] = Query(None),
    phase: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    search: Optional[str] = Query(None, description="Search in study ID, protocol, sponsor"),
) -> StudyList:
    """Retrieve a paginated, optionally filtered list of studies."""
    query = select(Study)

    if sponsor_name:
        query = query.where(Study.sponsor_name.ilike(f"%{sponsor_name}%"))
    if therapeutic_area:
        query = query.where(Study.therapeutic_area.ilike(f"%{therapeutic_area}%"))
    if phase:
        query = query.where(Study.phase == phase)
    if status_filter:
        query = query.where(Study.status == status_filter)
    if search:
        pattern = f"%{search}%"
        query = query.where(
            Study.study_identifier.ilike(pattern)
            | Study.protocol_number.ilike(pattern)
            | Study.sponsor_name.ilike(pattern)
        )

    # Total count
    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar_one()

    # Paginated results
    query = query.order_by(Study.created_at.desc()).offset((page - 1) * size).limit(size)
    result = await db.execute(query)
    items = list(result.scalars().all())

    return StudyList(items=items, total=total, page=page, size=size)


@router.get(
    "/{study_id}",
    response_model=StudyRead,
    summary="Get study by ID",
)
async def get_study(
    study_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Study:
    """Retrieve a single study by its UUID."""
    result = await db.execute(select(Study).where(Study.id == study_id))
    study = result.scalar_one_or_none()
    if study is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Study not found")
    return study


@router.put(
    "/{study_id}",
    response_model=StudyRead,
    summary="Update a study",
)
async def update_study(
    study_id: uuid.UUID,
    payload: StudyUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Study:
    """Partially update study metadata."""
    result = await db.execute(select(Study).where(Study.id == study_id))
    study = result.scalar_one_or_none()
    if study is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Study not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(study, field, value)

    await db.flush()
    await db.refresh(study)
    logger.info("Study updated: %s by %s", study.study_identifier, current_user.email)
    return study


@router.get(
    "/{study_id}/tmf-overview",
    response_model=TMFOverview,
    summary="TMF completeness overview",
)
async def tmf_overview(
    study_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> TMFOverview:
    """Return a summary of TMF artifact coverage for the given study."""
    # Verify study exists
    study_result = await db.execute(select(Study).where(Study.id == study_id))
    if study_result.scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Study not found")

    # Aggregate documents by TMF zone/section
    docs_result = await db.execute(
        select(Document).where(
            Document.study_id == study_id,
            Document.status != "deleted",
        )
    )
    documents = list(docs_result.scalars().all())

    artifact_map: dict[tuple[int, str, str | None], list[Document]] = {}
    for doc in documents:
        key = (doc.tmf_zone, doc.tmf_section, doc.tmf_artifact)
        artifact_map.setdefault(key, []).append(doc)

    artifacts = []
    for (zone, section, artifact), docs in sorted(artifact_map.items()):
        latest = max(docs, key=lambda d: d.created_at)
        artifacts.append(
            TMFArtifactSummary(
                tmf_zone=zone,
                tmf_section=section,
                tmf_artifact=artifact,
                document_count=len(docs),
                latest_version=latest.version,
                latest_status=latest.status,
            )
        )

    # TMF Reference Model defines ~270 expected artifacts; calculate completeness
    expected_artifact_count = 270
    completeness = min(
        (len(artifact_map) / expected_artifact_count) * 100, 100.0
    )

    return TMFOverview(
        study_id=study_id,
        total_documents=len(documents),
        artifacts=artifacts,
        completeness_percentage=round(completeness, 2),
    )
