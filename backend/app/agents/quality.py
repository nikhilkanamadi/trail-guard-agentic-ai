"""Quality review agent — aggregate scoring, escalation, and HITL decision."""

from __future__ import annotations

from typing import Any, Dict, List

from app.agents.base import AgentFinding, AgentResult, BaseAgent
from app.models.finding import FindingSeverity

# ── Scoring constants ─────────────────────────────────────────────────────────
CRITICAL_PENALTY = 15
MAJOR_PENALTY = 5
MINOR_PENALTY = 1

MAX_CRITICAL_DEDUCTION = 60
MAX_MAJOR_DEDUCTION = 25
MAX_MINOR_DEDUCTION = 10

ESCALATION_CRITICAL_THRESHOLD = 1   # any critical → escalate
ESCALATION_MAJOR_THRESHOLD = 5      # ≥ 5 major → escalate
ESCALATION_SCORE_THRESHOLD = 50     # score < 50 → escalate


def _compute_score(critical: int, major: int, minor: int) -> float:
    deduction = (
        min(critical * CRITICAL_PENALTY, MAX_CRITICAL_DEDUCTION)
        + min(major * MAJOR_PENALTY, MAX_MAJOR_DEDUCTION)
        + min(minor * MINOR_PENALTY, MAX_MINOR_DEDUCTION)
    )
    return max(0.0, 100.0 - deduction)


def _build_recommendation(score: float, escalate: bool, critical: int, major: int) -> str:
    if critical > 0:
        return (
            f"IMMEDIATE ACTION REQUIRED: {critical} critical finding(s) demand urgent remediation "
            "before this document can be used in regulatory submissions. Escalate to compliance team."
        )
    if escalate and major >= ESCALATION_MAJOR_THRESHOLD:
        return (
            f"ESCALATION RECOMMENDED: {major} major findings detected. "
            "Coordinate with the clinical team to resolve all major findings prior to filing."
        )
    if score < 70:
        return (
            f"Document quality score is {score:.1f}/100 — below acceptable threshold. "
            "Address all major findings before submission."
        )
    if score >= 95:
        return f"Document quality is excellent ({score:.1f}/100). Minor review recommended before final submission."
    return f"Document quality score: {score:.1f}/100. Review and resolve outstanding findings."


class QualityReviewAgent(BaseAgent):
    """Aggregates agent findings into a quality score and escalation decision."""

    def __init__(self) -> None:
        super().__init__("quality_review", version="1.0.0")

    async def _execute(
        self,
        document_text: str,
        document_metadata: Dict[str, Any],
        study_metadata: Dict[str, Any],
        **kwargs: Any,
    ) -> AgentResult:
        upstream_findings: List[AgentFinding] = kwargs.get("findings", [])

        # ── Count by severity ────────────────────────────────────────────────
        counts: Dict[str, int] = {
            "critical": 0, "major": 0, "minor": 0, "info": 0
        }
        for f in upstream_findings:
            sev = f.severity.value if hasattr(f.severity, "value") else str(f.severity)
            if sev in counts:
                counts[sev] += 1

        critical = counts["critical"]
        major = counts["major"]
        minor = counts["minor"]
        info = counts["info"]
        total = len(upstream_findings)

        # ── Score ────────────────────────────────────────────────────────────
        score = _compute_score(critical, major, minor)

        # ── Escalation decision ──────────────────────────────────────────────
        escalate = (
            critical >= ESCALATION_CRITICAL_THRESHOLD
            or major >= ESCALATION_MAJOR_THRESHOLD
            or score < ESCALATION_SCORE_THRESHOLD
        )

        recommendation = _build_recommendation(score, escalate, critical, major)

        # ── Summary finding ──────────────────────────────────────────────────
        severity_for_summary = (
            FindingSeverity.CRITICAL if critical > 0
            else FindingSeverity.MAJOR if major > 0
            else FindingSeverity.MINOR if minor > 0
            else FindingSeverity.INFO
        )

        summary_finding = self._make_finding(
            finding_type="quality_summary",
            severity=FindingSeverity.INFO,
            category="Quality Review",
            title=f"Quality Review Complete — Score: {score:.1f}/100",
            description=(
                f"Pipeline completed. Total findings: {total} "
                f"(Critical: {critical}, Major: {major}, Minor: {minor}, Info: {info}). "
                f"Escalation required: {'YES' if escalate else 'No'}. "
                f"{recommendation}"
            ),
            suggested_remediation=recommendation,
            confidence_score=1.0,
        )

        return AgentResult(
            agent_name=self.name,
            status="completed",
            findings=[summary_finding],
            metadata={
                "overall_score": round(score, 2),
                "critical_count": critical,
                "major_count": major,
                "minor_count": minor,
                "info_count": info,
                "total_findings": total,
                "escalation_required": escalate,
                "recommendation": recommendation,
            },
        )
