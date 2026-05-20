"""Consistency agent — checks terminology, dosing, dates, and unit consistency."""

from __future__ import annotations

import re
from collections import Counter
from typing import Any, Dict, List, Set, Tuple

from app.agents.base import AgentFinding, AgentResult, BaseAgent
from app.models.finding import FindingSeverity

# ── Dosing patterns ───────────────────────────────────────────────────────────
DOSE_AMOUNT_PATTERN = re.compile(
    r"(\d+(?:\.\d+)?)\s*(mg|µg|mcg|g|ug|ml|mL|mg/kg|µg/kg|mcg/kg|IU|ng)",
    re.IGNORECASE,
)
DOSE_FREQUENCY_PATTERN = re.compile(
    r"\b(once daily|twice daily|three times daily|BID|TID|QD|QID|every \d+ (?:hours?|days?|weeks?))\b",
    re.IGNORECASE,
)

# ── Date patterns ─────────────────────────────────────────────────────────────
STUDY_START_PATTERN = re.compile(
    r"(?:study start|first patient|first subject|enrollment start|FPI)[^\d]*(\d{4}-\d{2}-\d{2}|\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})",
    re.IGNORECASE,
)
STUDY_END_PATTERN = re.compile(
    r"(?:study end|last patient|last subject|enrollment end|LPI|completion)[^\d]*(\d{4}-\d{2}-\d{2}|\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})",
    re.IGNORECASE,
)

# ── Unit patterns ─────────────────────────────────────────────────────────────
MG_PATTERN = re.compile(r"\b\d+(?:\.\d+)?\s*mg\b", re.IGNORECASE)
MG_KG_PATTERN = re.compile(r"\b\d+(?:\.\d+)?\s*mg/kg\b", re.IGNORECASE)

# ── Drug synonym detection: common INN/brand pairs ───────────────────────────
# Agents checks for multiple names for the same class of compound within a document.
# We detect this by looking for two or more distinct token patterns near "compound", "drug", "treatment"
DRUG_CONTEXT_PATTERN = re.compile(
    r"(?:compound|investigational\s+(?:drug|product)|study\s+drug|IMP|study\s+medication)\s*[:\-]?\s*([A-Z][a-zA-Z\-]+(?:\s+[A-Z][a-zA-Z\-]+)?)",
)


def _try_parse_date(date_str: str) -> int | None:
    """Return a sortable integer (YYYYMMDD) from common date formats, or None."""
    for fmt_re, parser in [
        (re.compile(r"(\d{4})-(\d{2})-(\d{2})"), lambda m: int(m.group(1)) * 10000 + int(m.group(2)) * 100 + int(m.group(3))),
        (re.compile(r"(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{4})"), lambda m: int(m.group(3)) * 10000 + int(m.group(2)) * 100 + int(m.group(1))),
    ]:
        m = fmt_re.fullmatch(date_str.strip())
        if m:
            try:
                return parser(m)
            except ValueError:
                return None
    return None


class ConsistencyAgent(BaseAgent):
    """Checks terminology, dosing, date, and unit consistency across a document."""

    def __init__(self) -> None:
        super().__init__("consistency", version="1.0.0")

    async def _execute(
        self,
        document_text: str,
        document_metadata: Dict[str, Any],
        study_metadata: Dict[str, Any],
        **kwargs: Any,
    ) -> AgentResult:
        findings: List[AgentFinding] = []

        self.emit_progress("drug_names", 20)
        findings.extend(self._check_drug_name_consistency(document_text))

        self.emit_progress("dosing", 45)
        findings.extend(self._check_dosing_consistency(document_text))

        self.emit_progress("dates", 65)
        findings.extend(self._check_date_ordering(document_text))

        self.emit_progress("units", 85)
        findings.extend(self._check_unit_consistency(document_text))

        return AgentResult(
            agent_name=self.name,
            status="completed",
            findings=findings,
            metadata={"checks_run": 4},
        )

    def _check_drug_name_consistency(self, text: str) -> List[AgentFinding]:
        findings: List[AgentFinding] = []
        matches = DRUG_CONTEXT_PATTERN.findall(text)
        unique_names = set(m.strip() for m in matches if len(m.strip()) > 3)
        if len(unique_names) > 1:
            findings.append(self._make_finding(
                finding_type="drug_name_inconsistency",
                severity=FindingSeverity.MINOR,
                category="Terminology Consistency",
                title="Multiple investigational product names detected",
                description=(
                    f"The document uses multiple names to refer to the investigational product: "
                    f"{', '.join(sorted(unique_names)[:5])}. "
                    "A single, consistent name (INN or protocol code) should be used throughout."
                ),
                regulatory_reference="ICH E6(R2) Section 6.1.3 — Identification of investigational product",
                suggested_remediation=(
                    "Standardise to one name for the investigational product throughout the document. "
                    "Define abbreviations and trade names in a glossary."
                ),
                confidence_score=0.72,
            ))
        return findings

    def _check_dosing_consistency(self, text: str) -> List[AgentFinding]:
        findings: List[AgentFinding] = []
        dose_matches = DOSE_AMOUNT_PATTERN.findall(text)
        # Group by unit and check for wildly different values (> 2× variance)
        by_unit: Dict[str, List[float]] = {}
        for amount_str, unit in dose_matches:
            unit_norm = unit.lower()
            try:
                amount = float(amount_str)
            except ValueError:
                continue
            by_unit.setdefault(unit_norm, []).append(amount)

        for unit, values in by_unit.items():
            unique_vals = set(values)
            if len(unique_vals) > 1:
                ratio = max(unique_vals) / max(min(unique_vals), 0.001)
                if ratio > 3:
                    findings.append(self._make_finding(
                        finding_type="dosing_inconsistency",
                        severity=FindingSeverity.MAJOR,
                        category="Dosing Consistency",
                        title=f"Large variation in {unit} dose values",
                        description=(
                            f"The document contains widely varying dose values in {unit}: "
                            f"{', '.join(str(v) for v in sorted(unique_vals)[:6])}. "
                            f"The highest value is {ratio:.0f}× the lowest. "
                            "Verify these represent different arms/cohorts and are clearly labelled."
                        ),
                        regulatory_reference="ICH E6(R2) Section 6.6 — Treatment of subjects",
                        suggested_remediation=(
                            "Clearly label each dose value with its associated cohort, arm, or visit. "
                            "Add a dosing table summarising the regimen for each treatment group."
                        ),
                        confidence_score=0.82,
                    ))
        return findings

    def _check_date_ordering(self, text: str) -> List[AgentFinding]:
        findings: List[AgentFinding] = []
        start_matches = [m.group(1) for m in STUDY_START_PATTERN.finditer(text)]
        end_matches = [m.group(1) for m in STUDY_END_PATTERN.finditer(text)]
        if not start_matches or not end_matches:
            return findings

        start_val = _try_parse_date(start_matches[0])
        end_val = _try_parse_date(end_matches[0])
        if start_val and end_val and start_val >= end_val:
            findings.append(self._make_finding(
                finding_type="invalid_date_ordering",
                severity=FindingSeverity.MAJOR,
                category="Date Consistency",
                title="Study start date is not before study end date",
                description=(
                    f"The detected study start date ({start_matches[0]}) is not before "
                    f"the study end date ({end_matches[0]}). "
                    "This may indicate a transcription error in one of the dates."
                ),
                regulatory_reference="ICH E6(R2) Section 6.3 — Trial timeline",
                suggested_remediation=(
                    "Verify both dates with the approved protocol and correct the erroneous entry."
                ),
                confidence_score=0.85,
            ))
        return findings

    def _check_unit_consistency(self, text: str) -> List[AgentFinding]:
        findings: List[AgentFinding] = []
        has_mg = bool(MG_PATTERN.search(text))
        has_mg_kg = bool(MG_KG_PATTERN.search(text))
        if has_mg and has_mg_kg:
            findings.append(self._make_finding(
                finding_type="mixed_dose_units",
                severity=FindingSeverity.MINOR,
                category="Dosing Consistency",
                title="Mixed dosing units: mg and mg/kg used together",
                description=(
                    "The document uses both absolute (mg) and weight-based (mg/kg) dose expressions. "
                    "Using both without clear delineation may cause confusion about the intended dose."
                ),
                regulatory_reference="ICH E6(R2) Section 6.6 — Description of investigational product",
                suggested_remediation=(
                    "Clarify when each unit applies (e.g. flat dosing vs. weight-adjusted). "
                    "If both are valid, add a dosing table that maps patient weight ranges to absolute doses."
                ),
                confidence_score=0.78,
            ))
        return findings
