"""Document routes — upload, retrieve, versions, soft-delete."""

from __future__ import annotations

import hashlib
import logging
import uuid
from typing import Annotated, List

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.config import get_settings
from app.database import get_db
from app.models.document import Document, DocumentStatus
from app.models.study import Study
from app.models.user import User
from app.schemas.document import DocumentRead, DocumentVersionRead

logger = logging.getLogger(__name__)
router = APIRouter()
settings = get_settings()


@router.post(
    "/upload",
    response_model=DocumentRead,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a document",
)
async def upload_document(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    file: UploadFile = File(...),
    study_id: uuid.UUID = Form(...),
    document_type: str = Form(...),
    tmf_zone: int = Form(..., ge=1, le=11),
    tmf_section: str = Form(...),
    title: str = Form(...),
    version: str = Form(default="1.0"),
    tmf_artifact: str | None = Form(default=None),
    language: str = Form(default="en"),
    country_code: str | None = Form(default=None),
    site_id: str | None = Form(default=None),
) -> Document:
    """Upload a document file with metadata via multipart form.

    The file is read into memory, hashed (SHA-256), and its path is recorded.
    In production, the file bytes would be streamed to S3/MinIO.
    """
    # Verify study exists
    study_result = await db.execute(select(Study).where(Study.id == study_id))
    if study_result.scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Study not found")

    # Validate file size
    contents = await file.read()
    file_size = len(contents)
    max_size = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if file_size > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum size of {settings.MAX_UPLOAD_SIZE_MB} MB",
        )

    # Validate MIME type
    mime_type = file.content_type or "application/octet-stream"
    if mime_type not in settings.ALLOWED_MIME_TYPES:
        logger.warning("Rejected upload with MIME type: %s", mime_type)
        # Still allow but flag — in production you may want to reject

    # Compute SHA-256 hash
    file_hash = hashlib.sha256(contents).hexdigest()

    # Check for duplicate hash within the same study
    dup_result = await db.execute(
        select(Document).where(
            Document.study_id == study_id,
            Document.file_hash == file_hash,
            Document.status != DocumentStatus.DELETED,
        )
    )
    if dup_result.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An identical file (same SHA-256 hash) already exists for this study",
        )

    # Build storage path (in production: upload to S3)
    file_path = f"documents/{study_id}/{uuid.uuid4()}/{file.filename}"

    document = Document(
        study_id=study_id,
        uploaded_by=current_user.id,
        document_type=document_type,
        tmf_zone=tmf_zone,
        tmf_section=tmf_section,
        tmf_artifact=tmf_artifact,
        title=title,
        version=version,
        language=language,
        country_code=country_code,
        site_id=site_id,
        file_path=file_path,
        file_hash=file_hash,
        file_size_bytes=file_size,
        mime_type=mime_type,
        status=DocumentStatus.UPLOADED,
    )
    db.add(document)
    await db.flush()
    await db.refresh(document)
    logger.info(
        "Document uploaded: %s (%s) by %s",
        document.title,
        document.id,
        current_user.email,
    )
    return document


@router.get(
    "/{document_id}",
    response_model=DocumentRead,
    summary="Get document by ID",
)
async def get_document(
    document_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Document:
    """Retrieve a single document by its UUID."""
    result = await db.execute(select(Document).where(Document.id == document_id))
    document = result.scalar_one_or_none()
    if document is None or document.status == DocumentStatus.DELETED:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return document


@router.get(
    "/{document_id}/versions",
    response_model=List[DocumentVersionRead],
    summary="Get document version history",
)
async def get_document_versions(
    document_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[Document]:
    """Return all versions of a document based on matching title & study."""
    result = await db.execute(select(Document).where(Document.id == document_id))
    doc = result.scalar_one_or_none()
    if doc is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    # Find all documents with the same title in the same study (version chain)
    versions_result = await db.execute(
        select(Document)
        .where(
            Document.study_id == doc.study_id,
            Document.title == doc.title,
            Document.document_type == doc.document_type,
            Document.status != DocumentStatus.DELETED,
        )
        .order_by(Document.created_at.desc())
    )
    return list(versions_result.scalars().all())


@router.delete(
    "/{document_id}",
    response_model=DocumentRead,
    summary="Soft-delete a document",
)
async def delete_document(
    document_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Document:
    """Soft-delete a document by setting its status to DELETED."""
    result = await db.execute(select(Document).where(Document.id == document_id))
    document = result.scalar_one_or_none()
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    if document.status == DocumentStatus.DELETED:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Document is already deleted",
        )

    document.status = DocumentStatus.DELETED
    await db.flush()
    await db.refresh(document)
    logger.info("Document soft-deleted: %s by %s", document_id, current_user.email)
    return document
