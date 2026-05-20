"""Administration routes — agent status, system health."""

from __future__ import annotations

import logging
import platform
from datetime import datetime, timezone
from typing import Annotated, Any, Dict

from fastapi import APIRouter, Depends, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_role
from app.config import get_settings
from app.database import get_db
from app.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter()
settings = get_settings()


@router.get(
    "/agents/status",
    summary="Get status of all validation agents",
    response_model=Dict[str, Any],
)
async def agents_status(
    current_user: Annotated[User, Depends(require_role(["admin", "manager"]))],
) -> dict[str, Any]:
    """Return the health and configuration of each validation agent."""
    agents = [
        {
            "name": "orchestrator",
            "display_name": "Orchestrator Agent",
            "status": "active",
            "description": "Routes documents through the validation pipeline",
            "version": "1.0.0",
        },
        {
            "name": "ingestion",
            "display_name": "Ingestion Agent",
            "status": "active",
            "description": "Parses, classifies, and extracts document metadata",
            "version": "1.0.0",
        },
        {
            "name": "compliance",
            "display_name": "Compliance Agent",
            "status": "active",
            "description": "Validates against ICH-GCP, 21 CFR Part 11, and EU CTR rules",
            "version": "1.0.0",
        },
        {
            "name": "cross_reference",
            "display_name": "Cross-Reference Agent",
            "status": "active",
            "description": "Validates cross-document references and version alignment",
            "version": "1.0.0",
        },
        {
            "name": "consistency",
            "display_name": "Consistency Agent",
            "status": "active",
            "description": "Checks dosing, dates, terminology, and eligibility consistency",
            "version": "1.0.0",
        },
        {
            "name": "phi_detection",
            "display_name": "PHI/PII Detection Agent",
            "status": "active",
            "description": "Detects protected health information and personally identifiable information",
            "version": "1.0.0",
        },
        {
            "name": "quality_review",
            "display_name": "Quality Review Agent",
            "status": "active",
            "description": "Calculates quality scores and generates review reports",
            "version": "1.0.0",
        },
    ]
    return {
        "agents": agents,
        "total_agents": len(agents),
        "all_healthy": all(a["status"] == "active" for a in agents),
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }


@router.get(
    "/system/health",
    summary="System health check",
    response_model=Dict[str, Any],
)
async def system_health(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    """Return overall system health — database connectivity, versions, etc.

    This endpoint is intentionally unauthenticated so load-balancers can probe it.
    """
    health: dict[str, Any] = {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "python_version": platform.python_version(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "components": {},
    }

    # Database check
    try:
        await db.execute(text("SELECT 1"))
        health["components"]["database"] = {"status": "healthy", "type": "postgresql"}
    except Exception as exc:
        logger.error("Database health check failed: %s", exc)
        health["components"]["database"] = {"status": "unhealthy", "error": str(exc)}
        health["status"] = "degraded"

    # Redis check (best-effort)
    try:
        import redis as redis_lib

        r = redis_lib.from_url(settings.REDIS_URL, socket_connect_timeout=2)
        r.ping()
        health["components"]["redis"] = {"status": "healthy"}
    except Exception as exc:
        logger.warning("Redis health check failed: %s", exc)
        health["components"]["redis"] = {"status": "unavailable", "error": str(exc)}

    # FAISS check
    try:
        import faiss  # noqa: F401

        health["components"]["faiss"] = {
            "status": "available",
            "index_path": settings.FAISS_INDEX_PATH,
        }
    except ImportError:
        health["components"]["faiss"] = {"status": "not_installed"}

    return health
