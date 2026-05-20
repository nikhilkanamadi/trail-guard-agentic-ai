"""PHI/PII detection agent — HIPAA Safe Harbor (45 CFR §164.514(b)(2))."""

from __future__ import annotations

import re
from typing import Any, Dict, List, NamedTuple

from app.agents.base import AgentFinding, AgentResult, BaseAgent
from app.models.finding import FindingSeverity


class _PHIPattern(NamedTuple):
    name: str
    pattern: re.Pattern[str]
    severity: FindingSeverity
    category: str
    description_template: str
    remediation: str
    regulatory_reference: str
    confidence: float


# ── HIPAA Safe Harbor identifiers ─────────────────────────────────────────────
PHI_PATTERNS: List[_PHIPattern] = [
    _PHIPattern(
        name="SSN",
        pattern=re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
        severity=FindingSeverity.CRITICAL,
        category="PHI — Social Security Number",
        description_template="Social Security Number(s) detected at {count} location(s). SSNs are direct identifiers under HIPAA Safe Harbor.",
        remediation="Redact all SSNs immediately. Replace with [REDACTED-SSN] placeholders.",
        regulatory_reference="HIPAA 45 CFR §164.514(b)(2)(i) — SSN identifier",
        confidence=0.99,
    ),
    _PHIPattern(
        name="DOB",
        pattern=re.compile(
            r"(?:date of birth|dob|born on|birth date)\s*[:\-]?\s*\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}",
            re.IGNORECASE,
        ),
        severity=FindingSeverity.CRITICAL,
        category="PHI — Date of Birth",
        description_template="Date of birth indicator(s) detected at {count} location(s). Birth dates are direct identifiers under HIPAA Safe Harbor.",
        remediation="Redact exact birth dates. Retain only age ranges (e.g., '55–65 years') as permitted by Safe Harbor.",
        regulatory_reference="HIPAA 45 CFR §164.514(b)(2)(i) — Dates directly related to individual",
        confidence=0.97,
    ),
    _PHIPattern(
        name="Patient Name",
        pattern=re.compile(
            r"(?:patient|subject|participant)\s*[:\-]\s*[A-Z][a-z]+ [A-Z][a-z]+",
        ),
        severity=FindingSeverity.MAJOR,
        category="PHI — Patient Name",
        description_template="Patient/subject name(s) detected at {count} location(s) in a label context.",
        remediation="Replace patient names with subject ID codes (e.g., Site-Subject format). Remove all personal identifiers.",
        regulatory_reference="HIPAA 45 CFR §164.514(b)(2)(i) — Names",
        confidence=0.88,
    ),
    _PHIPattern(
        name="Medical Record Number",
        pattern=re.compile(r"(?:MRN|medical record(?:\s+number)?|patient\s+id)\s*[:\-#]?\s*[A-Z0-9]{4,15}", re.IGNORECASE),
        severity=FindingSeverity.MAJOR,
        category="PHI — Medical Record Number",
        description_template="Medical record number(s) detected at {count} location(s).",
        remediation="Replace with de-identified subject IDs per study protocol. Remove MRN references entirely.",
        regulatory_reference="HIPAA 45 CFR §164.514(b)(2)(i) — Medical record numbers",
        confidence=0.91,
    ),
    _PHIPattern(
        name="Phone Number",
        pattern=re.compile(
            r"\b(?:\+1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"
        ),
        severity=FindingSeverity.MINOR,
        category="PHI — Phone Number",
        description_template="Phone number(s) detected at {count} location(s). Individual phone numbers are HIPAA identifiers.",
        remediation="Remove personal phone numbers. Retain only institutional/site contact numbers if necessary.",
        regulatory_reference="HIPAA 45 CFR §164.514(b)(2)(i) — Telephone numbers",
        confidence=0.82,
    ),
    _PHIPattern(
        name="Email Address",
        pattern=re.compile(r"\b[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}\b"),
        severity=FindingSeverity.MINOR,
        category="PHI — Email Address",
        description_template="Email address(es) detected at {count} location(s).",
        remediation="Remove personal email addresses. Use study/site contact addresses only where necessary.",
        regulatory_reference="HIPAA 45 CFR §164.514(b)(2)(i) — Electronic mail addresses",
        confidence=0.93,
    ),
    _PHIPattern(
        name="Device Serial Number",
        pattern=re.compile(r"(?:serial\s*(?:number|no\.?|#)|S/N)\s*[:\-]?\s*[A-Z0-9\-]{6,20}", re.IGNORECASE),
        severity=FindingSeverity.MINOR,
        category="PHI — Device Identifier",
        description_template="Device serial number(s) detected at {count} location(s).",
        remediation="Remove device serial numbers or replace with generic device identifiers.",
        regulatory_reference="HIPAA 45 CFR §164.514(b)(2)(i) — Device identifiers and serial numbers",
        confidence=0.80,
    ),
    _PHIPattern(
        name="Geographic Subdivision",
        pattern=re.compile(
            r"(?:street|st\.|avenue|ave\.|road|rd\.|drive|dr\.|lane|ln\.|boulevard|blvd\.)\s+[A-Z][a-zA-Z\s,]+",
            re.IGNORECASE,
        ),
        severity=FindingSeverity.MINOR,
        category="PHI — Geographic Subdivision",
        description_template="Street-level address(es) detected at {count} location(s). Subdivisions smaller than state are HIPAA identifiers.",
        remediation="Replace street-level addresses with city/state or remove entirely. Retain only postal codes if required.",
        regulatory_reference="HIPAA 45 CFR §164.514(b)(2)(i) — Geographic subdivisions smaller than state",
        confidence=0.76,
    ),
]


class PHIDetectionAgent(BaseAgent):
    """Detects Protected Health Information and PII in clinical documents."""

    def __init__(self) -> None:
        super().__init__("phi_detection", version="1.0.0")

    async def _execute(
        self,
        document_text: str,
        document_metadata: Dict[str, Any],
        study_metadata: Dict[str, Any],
        **kwargs: Any,
    ) -> AgentResult:
        findings: List[AgentFinding] = []
        total_phi_instances = 0

        for phi in PHI_PATTERNS:
            matches = phi.pattern.findall(document_text)
            count = len(matches)
            if count == 0:
                continue

            total_phi_instances += count
            findings.append(self._make_finding(
                finding_type=f"phi_{phi.name.lower().replace(' ', '_')}",
                severity=phi.severity,
                category=phi.category,
                title=f"PHI Detected: {phi.name} ({count} instance{'s' if count > 1 else ''})",
                description=phi.description_template.format(count=count),
                regulatory_reference=phi.regulatory_reference,
                suggested_remediation=phi.remediation,
                confidence_score=phi.confidence,
            ))

        if total_phi_instances == 0:
            self.logger.info("No PHI detected in document")

        return AgentResult(
            agent_name=self.name,
            status="completed",
            findings=findings,
            metadata={
                "total_phi_instances": total_phi_instances,
                "phi_types_found": len(findings),
                "hipaa_framework": "Safe Harbor (45 CFR §164.514(b)(2))",
            },
        )
