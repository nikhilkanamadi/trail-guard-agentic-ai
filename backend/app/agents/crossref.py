"""Cross-reference agent — validates internal references and numeric consistency."""

from __future__ import annotations

import re
from collections import defaultdict
from typing import Any, Dict, List

from app.agents.base import AgentFinding, AgentResult, BaseAgent
from app.models.finding import FindingSeverity

# ── Patterns ─────────────────────────────────────────────────────────────────
SECTION_REF_PATTERN = re.compile(
    r"(?:section|sec\.?|see)\s+(\d+(?:\.\d+)*)", re.IGNORECASE
)
SECTION_HEADING_PATTERN = re.compile(
    r"^(\d+(?:\.\d+)*)\s+\S", re.MULTILINE
)
FIGURE_REF_PATTERN = re.compile(r"\bfigure\s+(\d+(?:\.\d+)?)\b", re.IGNORECASE)
FIGURE_LABEL_PATTERN = re.compile(r"^figure\s+(\d+(?:\.\d+)?)[\.\s:\-]", re.IGNORECASE | re.MULTILINE)
TABLE_REF_PATTERN = re.compile(r"\btable\s+(\d+(?:\.\d+)?)\b", re.IGNORECASE)
TABLE_LABEL_PATTERN = re.compile(r"^table\s+(\d+(?:\.\d+)?)[\.\s:\-]", re.IGNORECASE | re.MULTILINE)
PROTOCOL_NUMBER_PATTERN = re.compile(
    r"(?:protocol\s*(?:number|no\.?|#)?[:\s]*)([\w\-]+)", re.IGNORECASE
)
# Numbers ≥ 10 that appear multiple times — potential sample sizes, patient counts, etc.
SIGNIFICANT_NUMBER_PATTERN = re.compile(r"\b(\d{2,5})\b")


class CrossReferenceAgent(BaseAgent):
    """Validates cross-references and numeric consistency within a document."""

    def __init__(self) -> None:
        super().__init__("cross_reference", version="1.0.0")

    async def _execute(
        self,
        document_text: str,
        document_metadata: Dict[str, Any],
        study_metadata: Dict[str, Any],
        **kwargs: Any,
    ) -> AgentResult:
        findings: List[AgentFinding] = []

        self.emit_progress("section_refs", 25)
        findings.extend(self._check_section_references(document_text))

        self.emit_progress("figure_table_refs", 50)
        findings.extend(self._check_figure_table_references(document_text))

        self.emit_progress("protocol_consistency", 75)
        findings.extend(self._check_protocol_number_consistency(document_text))

        self.emit_progress("numeric_consistency", 90)
        findings.extend(self._check_numeric_consistency(document_text))

        return AgentResult(
            agent_name=self.name,
            status="completed",
            findings=findings,
            metadata={"checks_run": 4},
        )

    def _check_section_references(self, text: str) -> List[AgentFinding]:
        findings: List[AgentFinding] = []
        referenced = {m.group(1) for m in SECTION_REF_PATTERN.finditer(text)}
        defined = {m.group(1) for m in SECTION_HEADING_PATTERN.finditer(text)}

        # Only flag if both referenced and defined sets are non-trivial (document has structure)
        if len(defined) < 3:
            return findings

        dangling = sorted(referenced - defined)[:5]  # cap to top 5
        for ref in dangling:
            findings.append(self._make_finding(
                finding_type="dangling_section_reference",
                severity=FindingSeverity.MINOR,
                category="Cross-Reference",
                title=f"Section {ref} referenced but not found",
                description=(
                    f"The document references 'Section {ref}' but no section with that number "
                    "was detected in the document structure. This may indicate a copy-paste error "
                    "or a reference to an external document that should be cited explicitly."
                ),
                regulatory_reference="ICH E3 — Integrated cross-reference accuracy",
                suggested_remediation=f"Verify that Section {ref} exists or update the reference to the correct section number.",
                confidence_score=0.78,
            ))
        return findings

    def _check_figure_table_references(self, text: str) -> List[AgentFinding]:
        findings: List[AgentFinding] = []

        fig_refs = {m.group(1) for m in FIGURE_REF_PATTERN.finditer(text)}
        fig_labels = {m.group(1) for m in FIGURE_LABEL_PATTERN.finditer(text)}
        tbl_refs = {m.group(1) for m in TABLE_REF_PATTERN.finditer(text)}
        tbl_labels = {m.group(1) for m in TABLE_LABEL_PATTERN.finditer(text)}

        for ref in sorted(fig_refs - fig_labels)[:3]:
            findings.append(self._make_finding(
                finding_type="missing_figure",
                severity=FindingSeverity.MINOR,
                category="Cross-Reference",
                title=f"Figure {ref} referenced but label not found",
                description=(
                    f"The text references 'Figure {ref}' but no corresponding figure label was detected. "
                    "The figure may be missing or labelled incorrectly."
                ),
                regulatory_reference="ICH E3 — Figure and table cross-reference accuracy",
                suggested_remediation=f"Ensure Figure {ref} is present and labelled consistently.",
                confidence_score=0.75,
            ))

        for ref in sorted(tbl_refs - tbl_labels)[:3]:
            findings.append(self._make_finding(
                finding_type="missing_table",
                severity=FindingSeverity.MINOR,
                category="Cross-Reference",
                title=f"Table {ref} referenced but label not found",
                description=(
                    f"The text references 'Table {ref}' but no corresponding table label was detected. "
                    "The table may be missing or labelled differently."
                ),
                regulatory_reference="ICH E3 — Table cross-reference accuracy",
                suggested_remediation=f"Ensure Table {ref} exists and its label matches the in-text reference.",
                confidence_score=0.75,
            ))
        return findings

    def _check_protocol_number_consistency(self, text: str) -> List[AgentFinding]:
        findings: List[AgentFinding] = []
        matches = [m.group(1).strip() for m in PROTOCOL_NUMBER_PATTERN.finditer(text)]
        unique = set(matches)
        if len(unique) > 1:
            findings.append(self._make_finding(
                finding_type="protocol_number_inconsistency",
                severity=FindingSeverity.MAJOR,
                category="Document Consistency",
                title="Protocol number appears inconsistently",
                description=(
                    f"Multiple protocol number values were detected in the document: "
                    f"{', '.join(sorted(unique))}. The protocol number must be identical throughout."
                ),
                regulatory_reference="ICH E6(R2) Section 6.1 — Protocol identification",
                suggested_remediation=(
                    "Review all occurrences of the protocol number and standardise to the correct value."
                ),
                confidence_score=0.90,
            ))
        return findings

    def _check_numeric_consistency(self, text: str) -> List[AgentFinding]:
        """Flag numbers that appear near contradictory contextual keywords."""
        findings: List[AgentFinding] = []

        # Look for sample size stated in multiple ways with different values
        sample_patterns = [
            re.compile(r"(?:sample size|n\s*=|subjects?|patients?|participants?)\s*(?:of|:|=)?\s*(\d+)", re.IGNORECASE),
        ]
        counts: Dict[str, List[int]] = defaultdict(list)
        for pattern in sample_patterns:
            for m in pattern.finditer(text):
                num = int(m.group(1))
                if num >= 10:
                    counts["sample_size"].append(num)

        if counts["sample_size"]:
            unique_counts = set(counts["sample_size"])
            if len(unique_counts) > 1:
                findings.append(self._make_finding(
                    finding_type="sample_size_inconsistency",
                    severity=FindingSeverity.MAJOR,
                    category="Data Integrity",
                    title="Inconsistent sample size values",
                    description=(
                        f"Different sample size values were found in the document: "
                        f"{', '.join(str(n) for n in sorted(unique_counts))}. "
                        "A single, consistent planned sample size must be stated throughout."
                    ),
                    regulatory_reference="ICH E9 Section 3.5 — Sample size determination",
                    suggested_remediation=(
                        "Reconcile all sample size references to a single agreed value. "
                        "Ensure the SAP, protocol, and CSR are aligned."
                    ),
                    confidence_score=0.88,
                ))
        return findings
