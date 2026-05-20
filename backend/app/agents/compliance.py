"""Compliance agent — checks documents against ICH-GCP, FDA 21 CFR Part 11, EU CTR."""

from __future__ import annotations

import re
from typing import Any, Dict, List, Set

from app.agents.base import AgentFinding, AgentResult, BaseAgent
from app.models.finding import FindingSeverity

# ── Required sections by document type ──────────────────────────────────────
REQUIRED_SECTIONS: Dict[str, Dict[str, str]] = {
    "Protocol": {
        "objectives": "ICH E6(R2) Section 6.2",
        "endpoints": "ICH E6(R2) Section 6.2",
        "inclusion criteria": "ICH E6(R2) Section 6.5",
        "exclusion criteria": "ICH E6(R2) Section 6.5",
        "statistical": "ICH E6(R2) Section 6.9",
        "safety monitoring": "ICH E6(R2) Section 6.10",
        "informed consent": "ICH E6(R2) Section 6.4.1",
    },
    "Informed Consent Form": {
        "voluntary participation": "FDA 21 CFR 50.25(a)(6)",
        "right to withdraw": "FDA 21 CFR 50.25(a)(6)",
        "risks": "FDA 21 CFR 50.25(a)(2)",
        "benefits": "FDA 21 CFR 50.25(a)(3)",
        "contact": "FDA 21 CFR 50.25(a)(7)",
        "confidentiality": "ICH E6(R2) Section 4.8.2",
    },
    "Investigator Brochure": {
        "pharmacology": "ICH E6(R2) Section 7.2",
        "toxicology": "ICH E6(R2) Section 7.3",
        "clinical": "ICH E6(R2) Section 7.4",
        "summary": "ICH E6(R2) Section 7.1",
    },
    "Clinical Study Report": {
        "study objectives": "ICH E3 Section 2",
        "patient disposition": "ICH E3 Section 10",
        "efficacy": "ICH E3 Section 11",
        "safety": "ICH E3 Section 12",
        "conclusions": "ICH E3 Section 16",
    },
    "Statistical Analysis Plan": {
        "primary endpoint": "ICH E9 Section 2",
        "sample size": "ICH E9 Section 3.5",
        "analysis population": "ICH E9 Section 5.2",
        "missing data": "ICH E9 Section 4.7",
    },
}

# ── FDA 21 CFR Part 11 electronic records keywords ──────────────────────────
PART11_KEYWORDS = [
    "electronic signature",
    "audit trail",
    "system validation",
    "access control",
    "electronic records",
    "21 cfr part 11",
    "part 11",
    "esignature",
    "e-signature",
]

# ── Version control evidence keywords ────────────────────────────────────────
VERSION_KEYWORDS = ["version", "ver.", "amendment", "revision", "supersedes", "change log"]

# ── Date format patterns ──────────────────────────────────────────────────────
DATE_PATTERNS = [
    re.compile(r"\d{4}-\d{2}-\d{2}"),          # ISO: 2024-01-15
    re.compile(r"\d{1,2}/\d{1,2}/\d{4}"),       # US: 01/15/2024
    re.compile(r"\d{1,2}\s+\w{3,9}\s+\d{4}"),  # EU: 15 January 2024
]

MIXED_DATE_FORMATS = re.compile(
    r"(\d{4}-\d{2}-\d{2})|(\d{1,2}/\d{1,2}/\d{2,4})|(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d{4})",
    re.IGNORECASE,
)


class ComplianceAgent(BaseAgent):
    """Checks clinical trial documents against regulatory requirements."""

    def __init__(self) -> None:
        super().__init__("compliance", version="1.0.0")

    async def _execute(
        self,
        document_text: str,
        document_metadata: Dict[str, Any],
        study_metadata: Dict[str, Any],
        **kwargs: Any,
    ) -> AgentResult:
        findings: List[AgentFinding] = []
        text_lower = document_text.lower()
        doc_type = document_metadata.get("classified_type") or document_metadata.get("document_type", "")

        self.emit_progress("section_check", 20)
        findings.extend(self._check_required_sections(doc_type, text_lower))

        self.emit_progress("part11_check", 50)
        findings.extend(self._check_part11(doc_type, text_lower))

        self.emit_progress("date_check", 70)
        findings.extend(self._check_date_formats(document_text))

        self.emit_progress("version_check", 85)
        findings.extend(self._check_version_control(text_lower, document_metadata))

        self.emit_progress("sponsor_check", 95)
        findings.extend(self._check_sponsor_pi(text_lower, document_metadata))

        return AgentResult(
            agent_name=self.name,
            status="completed",
            findings=findings,
            metadata={"doc_type": doc_type, "checks_run": 5},
        )

    def _check_required_sections(self, doc_type: str, text_lower: str) -> List[AgentFinding]:
        findings: List[AgentFinding] = []
        required = REQUIRED_SECTIONS.get(doc_type, {})
        missing = [
            (kw, ref) for kw, ref in required.items()
            if kw.lower() not in text_lower
        ]
        for kw, ref in missing:
            findings.append(self._make_finding(
                finding_type="missing_required_section",
                severity=FindingSeverity.MAJOR,
                category="Document Completeness",
                title=f"Missing required section: '{kw}'",
                description=(
                    f"The document ({doc_type}) does not appear to contain a required section "
                    f"addressing '{kw}'. This section is mandated by {ref}."
                ),
                regulatory_reference=ref,
                suggested_remediation=f"Add a dedicated section covering '{kw}' per {ref} requirements.",
                confidence_score=0.80,
            ))
        return findings

    def _check_part11(self, doc_type: str, text_lower: str) -> List[AgentFinding]:
        findings: List[AgentFinding] = []
        # Part 11 only applies to electronic records — check if text references electronic submission
        if "electronic" not in text_lower and "ectd" not in text_lower:
            return findings
        present = any(kw in text_lower for kw in PART11_KEYWORDS)
        if not present:
            findings.append(self._make_finding(
                finding_type="part11_compliance_gap",
                severity=FindingSeverity.MAJOR,
                category="Regulatory Compliance",
                title="Missing FDA 21 CFR Part 11 compliance language",
                description=(
                    "The document appears to describe electronic records or submissions but does not "
                    "reference FDA 21 CFR Part 11 requirements for electronic records and signatures "
                    "(audit trail, access control, system validation)."
                ),
                regulatory_reference="FDA 21 CFR Part 11",
                suggested_remediation=(
                    "Add a section confirming that the electronic system meets 21 CFR Part 11 requirements, "
                    "including audit trail, access control, and validated software."
                ),
                confidence_score=0.75,
            ))
        return findings

    def _check_date_formats(self, document_text: str) -> List[AgentFinding]:
        findings: List[AgentFinding] = []
        matches = MIXED_DATE_FORMATS.findall(document_text)
        formats_used: Set[str] = set()
        for m in matches:
            if m[0]:
                formats_used.add("ISO (YYYY-MM-DD)")
            if m[1]:
                formats_used.add("US (MM/DD/YYYY)")
            if m[2]:
                formats_used.add("Long (DD Month YYYY)")

        if len(formats_used) > 1:
            findings.append(self._make_finding(
                finding_type="inconsistent_date_format",
                severity=FindingSeverity.MINOR,
                category="Document Quality",
                title="Inconsistent date formats detected",
                description=(
                    f"Multiple date formats were found in the document: {', '.join(sorted(formats_used))}. "
                    "Regulatory submissions should use a single consistent date format throughout."
                ),
                regulatory_reference="ICH E6(R2) Section 8 — ALCOA+ (Consistent)",
                suggested_remediation="Standardise all dates to ISO 8601 format (YYYY-MM-DD) per ALCOA+ principles.",
                confidence_score=0.85,
            ))
        return findings

    def _check_version_control(
        self, text_lower: str, document_metadata: Dict[str, Any]
    ) -> List[AgentFinding]:
        findings: List[AgentFinding] = []
        has_version = any(kw in text_lower for kw in VERSION_KEYWORDS)
        if not has_version:
            findings.append(self._make_finding(
                finding_type="missing_version_control",
                severity=FindingSeverity.MINOR,
                category="Document Control",
                title="No version control information detected",
                description=(
                    "The document does not appear to include version identifiers, amendment history, "
                    "or revision control markers. Version control is required for TMF documents."
                ),
                regulatory_reference="ICH E6(R2) Section 8.1 — Document control",
                suggested_remediation=(
                    "Add a document control section listing version number, effective date, "
                    "author, and change history."
                ),
                confidence_score=0.72,
            ))
        return findings

    def _check_sponsor_pi(
        self, text_lower: str, document_metadata: Dict[str, Any]
    ) -> List[AgentFinding]:
        findings: List[AgentFinding] = []
        sponsor_present = any(kw in text_lower for kw in ["sponsor", "sponsoring", "funded by"])
        pi_present = any(kw in text_lower for kw in ["principal investigator", "investigator", "pi:"])
        if not sponsor_present:
            findings.append(self._make_finding(
                finding_type="missing_sponsor_identification",
                severity=FindingSeverity.MINOR,
                category="Document Identification",
                title="Sponsor not identified in document",
                description=(
                    "The document does not contain a clear sponsor identification. "
                    "ICH-GCP requires sponsor details to be present in trial documents."
                ),
                regulatory_reference="ICH E6(R2) Section 5 — Sponsor responsibilities",
                suggested_remediation="Add sponsor name, address, and contact information to the document header.",
                confidence_score=0.70,
            ))
        if not pi_present:
            findings.append(self._make_finding(
                finding_type="missing_pi_identification",
                severity=FindingSeverity.MINOR,
                category="Document Identification",
                title="Principal investigator not identified",
                description=(
                    "The document does not identify the principal investigator. "
                    "GCP requires PI identification in clinical trial documents."
                ),
                regulatory_reference="ICH E6(R2) Section 4 — Investigator responsibilities",
                suggested_remediation="Add the PI name, credentials, and institutional affiliation.",
                confidence_score=0.70,
            ))
        return findings
