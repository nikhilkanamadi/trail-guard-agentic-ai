"""FastAPI application entry point for TrialGuard AI."""

from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.config import get_settings

settings = get_settings()

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL, logging.INFO),
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="TrialGuard AI",
    version="1.0.0",
    description=(
        "Agentic Clinical Trial Document Validation Platform. "
        "Automates validation, compliance checking, and quality review of clinical trial documents "
        "against ICH-GCP E6(R2), FDA 21 CFR Part 11, EU CTR 536/2014, HIPAA, and GDPR."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# ── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(api_router)


# ── Lifecycle ─────────────────────────────────────────────────────────────────
@app.on_event("startup")
async def on_startup() -> None:
    logger.info("TrialGuard AI started — environment: %s", settings.ENVIRONMENT)


@app.on_event("shutdown")
async def on_shutdown() -> None:
    logger.info("TrialGuard AI shutting down")


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/", tags=["Health"], summary="Health check")
async def health_check() -> dict:
    return {
        "status": "ok",
        "service": "TrialGuard AI",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
    }


# ── Exception handlers ────────────────────────────────────────────────────────
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={"detail": "Resource not found", "path": str(request.url.path)},
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled server error on %s", request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error — please contact support"},
    )
