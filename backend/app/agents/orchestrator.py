"""Orchestrator agent — routes documents through the validation pipeline."""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Any, Dict, List

from app.agents.base import AgentFinding, AgentResult, BaseAgent
from app.agents.compliance import ComplianceAgent
from app.agents.consistency import ConsistencyAgent
from app.agents.crossref import CrossReferenceAgent
from app.agents.ingestion import IngestionAgent
from app.agents.phi import PHIDetectionAgent
from app.agents.quality import QualityReviewAgent

logger = logging.getLogger(__name__)

# Maps document_type (lowercase, normalised) → agents to activate in Stage 2.
# Any type not listed falls back to _DEFAULT_AGENTS.
_AGENT_MATRIX: dict[str, list[str]] = {
    "protocol":                    ["compliance", "cross_reference", "consistency"],
    "protocol_amendment":          ["compliance", "cross_reference", "consistency"],
    "informed_consent":            ["compliance", "cross_reference", "consistency", "phi"],
    "investigator_brochure":       ["compliance", "cross_reference", "consistency"],
    "clinical_study_report":       ["compliance", "cross_reference", "consistency"],
    "case_report_form":            ["compliance", "phi"],
    "serious_adverse_event":       ["compliance", "phi", "consistency"],
    "delegation_log":              ["compliance", "consistency"],
    "monitoring_report":           ["compliance", "consistency"],
    "irb_approval":                ["compliance"],
    "regulatory_correspondence":   ["compliance"],
    "investigator_cv":             ["compliance"],
}
_DEFAULT_AGENTS: list[str] = ["compliance", "cross_reference", "consistency", "phi"]


class OrchestratorAgent(BaseAgent):
    """Central coordinator that executes agents in the correct order.

    Pipeline stages:
        1. Ingestion      — parse, classify, extract metadata
        2. Parallel block  — compliance, cross-ref, consistency, PHI (run concurrently)
        3. Quality review  — aggregate scores and decide on escalation
    """

    def __init__(self) -> None:
        super().__init__("orchestrator", version="1.0.0")
        self.ingestion = IngestionAgent()
        self.compliance = ComplianceAgent()
        self.cross_reference = CrossReferenceAgent()
        self.consistency = ConsistencyAgent()
        self.phi_detection = PHIDetectionAgent()
        self.quality_review = QualityReviewAgent()

    async def _execute(
        self,
        document_text: str,
        document_metadata: Dict[str, Any],
        study_metadata: Dict[str, Any],
        **kwargs: Any,
    ) -> AgentResult:
        all_findings: List[AgentFinding] = []
        agent_trace: Dict[str, Any] = {"stages": []}

        # ── Stage 1: Ingestion ───────────────────────────────────────────
        self.emit_progress("ingestion", 10)
        ingestion_result = await self.ingestion.execute(
            document_text, document_metadata, study_metadata, **kwargs
        )
        all_findings.extend(ingestion_result.findings)
        agent_trace["stages"].append({
            "agent": "ingestion",
            "status": ingestion_result.status,
            "findings_count": len(ingestion_result.findings),
            "execution_time_ms": ingestion_result.execution_time_ms,
            "metadata": ingestion_result.metadata,
        })

        if ingestion_result.status == "failed":
            self.logger.error("Ingestion failed — aborting pipeline")
            return AgentResult(
                agent_name=self.name,
                status="failed",
                findings=all_findings,
                metadata={"agent_trace": agent_trace},
                error="Ingestion stage failed",
            )

        # Enrich metadata with ingestion output
        enriched_meta = {**document_metadata, **ingestion_result.metadata}

        # ── Stage 2: Parallel validation ─────────────────────────────────
        self.emit_progress("validation", 30)
        doc_type = document_metadata.get("document_type", "").lower().replace(" ", "_")
        active_names = _AGENT_MATRIX.get(doc_type, _DEFAULT_AGENTS)
        _agent_map = {
            "compliance": self.compliance,
            "cross_reference": self.cross_reference,
            "consistency": self.consistency,
            "phi": self.phi_detection,
        }
        parallel_agents = [_agent_map[n] for n in active_names if n in _agent_map]
        self.logger.info(
            "Document type '%s' → activating agents: %s",
            doc_type,
            [a.name for a in parallel_agents],
        )
        parallel_results = await asyncio.gather(
            *[
                agent.execute(document_text, enriched_meta, study_metadata, **kwargs)
                for agent in parallel_agents
            ],
            return_exceptions=True,
        )

        for agent, result in zip(parallel_agents, parallel_results):
            if isinstance(result, Exception):
                self.logger.error("Agent %s raised: %s", agent.name, result)
                agent_trace["stages"].append({
                    "agent": agent.name,
                    "status": "failed",
                    "error": str(result),
                })
                continue

            all_findings.extend(result.findings)
            agent_trace["stages"].append({
                "agent": agent.name,
                "status": result.status,
                "findings_count": len(result.findings),
                "execution_time_ms": result.execution_time_ms,
            })

        # ── Stage 3: Quality review ──────────────────────────────────────
        self.emit_progress("quality_review", 80)
        quality_result = await self.quality_review.execute(
            document_text,
            enriched_meta,
            study_metadata,
            findings=all_findings,
            **kwargs,
        )
        all_findings.extend(quality_result.findings)
        agent_trace["stages"].append({
            "agent": "quality_review",
            "status": quality_result.status,
            "findings_count": len(quality_result.findings),
            "execution_time_ms": quality_result.execution_time_ms,
            "metadata": quality_result.metadata,
        })

        # ── Aggregate ────────────────────────────────────────────────────
        agent_trace["total_findings"] = len(all_findings)
        agent_trace["overall_score"] = quality_result.metadata.get("overall_score", 0)

        return AgentResult(
            agent_name=self.name,
            status="completed",
            findings=all_findings,
            metadata={"agent_trace": agent_trace},
        )
