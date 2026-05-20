"""Celery pipeline task — runs the full validation lifecycle for one document.

Lifecycle:
    1. Load run + document from DB, mark status=RUNNING
    2. Write audit_trail entry: pipeline_started
    3. Execute OrchestratorAgent (ingestion → parallel validators → quality)
       - Each sub-agent publishes Redis Pub/Sub progress events
       - Dynamic routing skips irrelevant agents based on document_type
    4. Checkpoint agent_trace into validation_runs
    5a. escalation_required → status=AWAITING_REVIEW (HITL pause)
    5b. otherwise → persist findings, update aggregates, status=COMPLETED
    6. Write audit_trail entry: pipeline_completed | pipeline_escalated | pipeline_failed
"""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Any

import redis as redis_sync
from celery import Task
from sqlalchemy import select

from app.agents.orchestrator import OrchestratorAgent
from app.config import get_settings
from app.database import async_session_factory
from app.models.audit import AuditTrail
from app.models.document import Document
from app.models.finding import Finding, FindingSeverity
from app.models.study import Study
from app.models.validation import ValidationRun, ValidationRunStatus
from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)
settings = get_settings()


# ── Celery task ───────────────────────────────────────────────────────────────

@celery_app.task(
    bind=True,
    name="pipeline.dispatch",
    max_retries=3,
    default_retry_delay=30,
    acks_late=True,
)
def dispatch_pipeline(self: Task, run_id: str) -> dict[str, Any]:
    """Execute the full validation pipeline for a single validation run."""
    try:
        return asyncio.run(_run_pipeline(self, run_id))
    except Exception as exc:
        logger.exception("Pipeline task failed for run %s", run_id)
        asyncio.run(_mark_failed(run_id, str(exc)))
        raise self.retry(exc=exc)


# ── Async pipeline implementation ─────────────────────────────────────────────

async def _run_pipeline(task: Task, run_id: str) -> dict[str, Any]:
    async with async_session_factory() as db:
        # Load run
        run: ValidationRun = (
            await db.execute(select(ValidationRun).where(ValidationRun.id == run_id))
        ).scalar_one()

        # Mark running
        run.status = ValidationRunStatus.RUNNING
        run.started_at = datetime.now(timezone.utc)
        run.celery_task_id = task.request.id
        await db.flush()

        # Load document and study
        doc: Document = (
            await db.execute(select(Document).where(Document.id == run.document_id))
        ).scalar_one()
        study: Study = (
            await db.execute(select(Study).where(Study.id == run.study_id))
        ).scalar_one()

        # Audit trail: started
        db.add(AuditTrail(
            entity_type="validation_run",
            entity_id=str(run_id),
            action="pipeline_started",
            new_values={
                "status": "running",
                "document_type": doc.document_type,
                "document_id": str(doc.id),
                "celery_task_id": task.request.id,
            },
        ))
        await db.flush()

        # Build inputs
        doc_text = _load_document_text(doc)
        doc_meta = _build_doc_metadata(doc)
        study_meta = _build_study_metadata(study)

        # Instantiate orchestrator and wire Redis progress callbacks
        orchestrator = OrchestratorAgent()
        redis_client = redis_sync.from_url(settings.REDIS_URL)
        _wire_progress(orchestrator, redis_client, run_id)

        # Execute pipeline
        result = await orchestrator.execute(doc_text, doc_meta, study_meta)

        trace = result.metadata.get("agent_trace", {})
        run.agent_trace = trace

        # Read quality review metadata from trace
        quality_stage = next(
            (s for s in trace.get("stages", []) if s.get("agent") == "quality_review"),
            {},
        )
        escalation_required = quality_stage.get("metadata", {}).get(
            "escalation_required", False
        )

        if escalation_required:
            # HITL pause — human reviewer must approve before findings are committed
            run.status = ValidationRunStatus.AWAITING_REVIEW
            db.add(AuditTrail(
                entity_type="validation_run",
                entity_id=str(run_id),
                action="pipeline_escalated",
                new_values={
                    "reason": "critical or high-volume findings require human review",
                    "overall_score": trace.get("overall_score"),
                },
            ))
        else:
            _persist_findings(db, run, result.findings)
            run.status = ValidationRunStatus.COMPLETED
            run.completed_at = datetime.now(timezone.utc)
            db.add(AuditTrail(
                entity_type="validation_run",
                entity_id=str(run_id),
                action="pipeline_completed",
                new_values={
                    "status": "completed",
                    "total_findings": run.total_findings,
                    "overall_score": run.overall_score,
                },
            ))

        await db.flush()

        # Publish terminal event
        _publish(redis_client, run_id, "orchestrator", str(run.status), 100)

        return {"run_id": run_id, "status": str(run.status)}


async def _mark_failed(run_id: str, error: str) -> None:
    async with async_session_factory() as db:
        run = (
            await db.execute(select(ValidationRun).where(ValidationRun.id == run_id))
        ).scalar_one_or_none()
        if run is None:
            return
        run.status = ValidationRunStatus.FAILED
        run.completed_at = datetime.now(timezone.utc)
        existing = run.agent_trace or {}
        existing["error"] = error
        run.agent_trace = existing
        db.add(AuditTrail(
            entity_type="validation_run",
            entity_id=str(run_id),
            action="pipeline_failed",
            new_values={"error": error},
        ))
        await db.flush()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _wire_progress(
    orchestrator: OrchestratorAgent,
    redis_client: redis_sync.Redis,
    run_id: str,
) -> None:
    """Register a Redis Pub/Sub progress callback on every agent in the pipeline."""
    def _cb(agent_name: str, stage: str, percent: int) -> None:
        _publish(redis_client, run_id, agent_name, stage, percent)

    agents_to_wire = [
        orchestrator,
        orchestrator.ingestion,
        orchestrator.compliance,
        orchestrator.cross_reference,
        orchestrator.consistency,
        orchestrator.phi_detection,
        orchestrator.quality_review,
    ]
    for agent in agents_to_wire:
        agent.on_progress(_cb)


def _publish(
    redis_client: redis_sync.Redis,
    run_id: str,
    agent: str,
    stage: str,
    percent: int,
) -> None:
    try:
        redis_client.publish(
            f"run:{run_id}:progress",
            json.dumps({"agent": agent, "stage": stage, "percent": percent}),
        )
    except Exception:
        pass  # progress loss is non-fatal


def _persist_findings(
    db: Any,
    run: ValidationRun,
    findings: list,
) -> None:
    """Write AgentFindings to the DB and update run aggregate counters."""
    critical = major = minor = 0
    for f in findings:
        sev = f.severity.value if hasattr(f.severity, "value") else str(f.severity)
        if sev == FindingSeverity.CRITICAL:
            critical += 1
        elif sev == FindingSeverity.MAJOR:
            major += 1
        elif sev == FindingSeverity.MINOR:
            minor += 1

        db.add(Finding(
            validation_run_id=run.id,
            document_id=run.document_id,
            agent_name=f.agent_name,
            finding_type=f.finding_type,
            severity=f.severity,
            category=f.category,
            title=f.title,
            description=f.description,
            page_number=f.page_number,
            section_reference=f.section_reference,
            regulatory_reference=f.regulatory_reference,
            suggested_remediation=f.suggested_remediation,
            confidence_score=f.confidence_score,
        ))

    run.total_findings = len(findings)
    run.critical_findings = critical
    run.major_findings = major
    run.minor_findings = minor
    run.overall_score = (
        run.agent_trace.get("overall_score") if run.agent_trace else None
    )


def _load_document_text(doc: Document) -> str:
    """Load document text from storage. Reads file_path if local; extend for S3."""
    try:
        with open(doc.file_path, "r", encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except OSError:
        return f"[Binary document: {doc.title} — OCR/extraction required]"


def _build_doc_metadata(doc: Document) -> dict[str, Any]:
    return {
        "document_id": str(doc.id),
        "document_type": doc.document_type,
        "title": doc.title,
        "version": doc.version,
        "tmf_zone": doc.tmf_zone,
        "tmf_section": doc.tmf_section,
        "tmf_artifact": doc.tmf_artifact,
        "language": doc.language,
        "country_code": doc.country_code,
        "site_id": doc.site_id,
        "mime_type": doc.mime_type,
        "file_size_bytes": doc.file_size_bytes,
        "page_count": doc.page_count,
    }


def _build_study_metadata(study: Study) -> dict[str, Any]:
    return {
        "study_id": str(study.id),
        "study_identifier": study.study_identifier,
        "protocol_number": study.protocol_number,
        "phase": study.phase,
        "therapeutic_area": study.therapeutic_area,
        "sponsor_name": study.sponsor_name,
        "status": study.status,
    }
