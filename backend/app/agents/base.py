"""Base agent class — defines the contract every validation agent must satisfy."""

from __future__ import annotations

import abc
import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.models.finding import FindingSeverity


@dataclass
class AgentFinding:
    """Lightweight DTO emitted by agents before it is persisted."""

    agent_name: str
    finding_type: str
    severity: FindingSeverity
    category: str
    title: str
    description: str
    page_number: Optional[int] = None
    section_reference: Optional[str] = None
    regulatory_reference: Optional[str] = None
    suggested_remediation: Optional[str] = None
    confidence_score: float = 1.0


@dataclass
class AgentResult:
    """Standard return value from every agent execution."""

    agent_name: str
    status: str = "completed"  # completed | failed | skipped
    findings: List[AgentFinding] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    execution_time_ms: float = 0.0
    error: Optional[str] = None


class BaseAgent(abc.ABC):
    """Abstract base for all TrialGuard validation agents.

    Subclasses implement ``_execute`` with their domain logic.
    The public ``execute`` wrapper handles timing, error handling, and
    progress emission.
    """

    def __init__(self, name: str, *, version: str = "1.0.0") -> None:
        self.name = name
        self.version = version
        self.logger = logging.getLogger(f"agents.{name}")
        self._progress_callbacks: List[Any] = []

    # ── Public API ───────────────────────────────────────────────────────

    async def execute(
        self,
        document_text: str,
        document_metadata: Dict[str, Any],
        study_metadata: Dict[str, Any],
        **kwargs: Any,
    ) -> AgentResult:
        """Run the agent with standardised timing and error handling.

        Parameters
        ----------
        document_text:
            Full extracted text of the document.
        document_metadata:
            Dict with keys like ``document_type``, ``tmf_zone``, ``version``, etc.
        study_metadata:
            Dict with keys like ``protocol_number``, ``phase``, ``therapeutic_area``, etc.
        """
        start = time.monotonic()
        try:
            self.emit_progress("started", 0)
            result = await self._execute(
                document_text, document_metadata, study_metadata, **kwargs
            )
            result.execution_time_ms = (time.monotonic() - start) * 1000
            self.emit_progress("completed", 100)
            self.logger.info(
                "%s finished in %.1f ms — %d findings",
                self.name,
                result.execution_time_ms,
                len(result.findings),
            )
            return result
        except Exception as exc:
            elapsed = (time.monotonic() - start) * 1000
            self.logger.exception("Agent %s failed after %.1f ms", self.name, elapsed)
            self.emit_progress("failed", -1)
            return AgentResult(
                agent_name=self.name,
                status="failed",
                execution_time_ms=elapsed,
                error=str(exc),
            )

    def emit_progress(self, stage: str, percent: int) -> None:
        """Notify registered listeners about execution progress."""
        for cb in self._progress_callbacks:
            try:
                cb(self.name, stage, percent)
            except Exception:
                self.logger.debug("Progress callback error", exc_info=True)

    def on_progress(self, callback: Any) -> None:
        """Register a progress callback ``fn(agent_name, stage, percent)``."""
        self._progress_callbacks.append(callback)

    # ── Subclass contract ────────────────────────────────────────────────

    @abc.abstractmethod
    async def _execute(
        self,
        document_text: str,
        document_metadata: Dict[str, Any],
        study_metadata: Dict[str, Any],
        **kwargs: Any,
    ) -> AgentResult:
        """Override with domain-specific validation logic."""
        ...

    # ── Helpers ──────────────────────────────────────────────────────────

    def _make_finding(
        self,
        finding_type: str,
        severity: FindingSeverity,
        category: str,
        title: str,
        description: str,
        **kwargs: Any,
    ) -> AgentFinding:
        """Convenience factory for creating an AgentFinding."""
        return AgentFinding(
            agent_name=self.name,
            finding_type=finding_type,
            severity=severity,
            category=category,
            title=title,
            description=description,
            **kwargs,
        )
