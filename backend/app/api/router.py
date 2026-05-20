"""Main API router — aggregates every resource router under /api/v1."""

from fastapi import APIRouter

from app.api.routes import admin, audit, auth, documents, findings, studies, validation

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(studies.router, prefix="/studies", tags=["Studies"])
api_router.include_router(documents.router, prefix="/documents", tags=["Documents"])
api_router.include_router(validation.router, prefix="/validation", tags=["Validation"])
api_router.include_router(findings.router, prefix="/findings", tags=["Findings"])
api_router.include_router(audit.router, prefix="/audit", tags=["Audit Trail"])
api_router.include_router(admin.router, prefix="/admin", tags=["Administration"])
