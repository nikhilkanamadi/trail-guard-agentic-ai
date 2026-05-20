"""Ingestion agent — parse, classify, extract metadata, generate embeddings."""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, List

from app.agents.base import AgentFinding, AgentResult, BaseAgent
from app.models.finding import FindingSeverity

logger = logging.getLogger(__name__)

# ── TMF Reference Model zone mapping ────────────────────────────────────
TMF_ZONE_MAP: Dict[int, str] = {
    1: "Trial Management",
    2: "Central Trial Documents",
    3: "Regulatory",
    4: "IRB/IEC",
    5: "Site Management",
    6: "IP and Trial Supplies",
    7: "Safety Reporting",
    8: "Central and Local Testing",
    9: "Third Parties",
    10: "Data Management",
    11: "Statistics",
}

# ── Document type classification heuristics ──────────────────────────────
DOCUMENT_TYPE_KEYWORDS: Dict[str, List[str]] = {
    "Protocol": ["protocol", "study design", "objectives", "endpoints", "inclusion criteria"],
    "Informed Consent Form": ["informed consent", "voluntary participation", "consent form", "ICF"],
    "Investigator Brochure": ["investigator brochure", "pharmacology", "toxicology", "clinical experience"],
    "Case Report Form": ["case report form", "CRF", "data collection", "visit schedule"],
    "Statistical Analysis Plan": ["statistical analysis", "SAP", "primary analysis", "sample size"],
    "Clinical Study Report": ["clinical study report", "CSR", "efficacy results", "safety results"],
    "Monitoring Report": ["monitoring visit", "site visit", "monitoring report", "source data"],
    "Regulatory Submission": ["IND", "NDA", "BLA", "regulatory submission", "marketing authorization"],
    "Safety Report": ["SUSAR", "safety report", "adverse event", "serious adverse event", "SAE"],
    "Lab Report": ["laboratory", "lab report", "reference ranges", "central lab"],
}


class IngestionAgent(BaseAgent):
    """Parses documents, classifies them, and extracts structured metadata."""

    def __init__(self) -> None:
        super().__init__("ingestion", version="1.0.0")

    async def _execute(
        self,
        document_text: str,
        document_metadata: Dict[str, Any],
        study_metadata: Dict[str, Any],
        **kwargs: Any,
    ) -> AgentResult:
        findings: List[AgentFinding] = []
        extracted_metadata: Dict[str, Any] = {}

        # ── Parse document ───────────────────────────────────────────────
        parsed = self._parse_document(document_text)
        extracted_metadata["word_count"] = parsed["word_count"]
        extracted_metadata["page_estimate"] = parsed["page_estimate"]
        extracted_metadata["sections_detected"] = parsed["sections"]

        if parsed["word_count"] < 50:
            findings.append(self._make_finding(
                finding_type="low_content",
                severity=FindingSeverity.MAJOR,
                category="Document Quality",
                title="Document has very low content",
                description=f"The document contains only {parsed['word_count']} words, which is unusually short for a clinical trial document. It may be corrupt, incomplete, or a placeholder.",
                suggested_remediation="Verify the document file is complete and re-upload if necessary.",
                confidence_score=0.95,
            ))

        # ── Classify document ────────────────────────────────────────────
        classified_type = self._classify_document(document_text)
        extracted_metadata["classified_type"] = classified_type

        declared_type = document_metadata.get("document_type", "")
        if classified_type and declared_type and classified_type.lower() != declared_type.lower():
            findings.append(self._make_finding(
                finding_type="type_mismatch",
                severity=FindingSeverity.MINOR,
                category="Classification",
                title="Document type mismatch",
                description=f"The declared document type is '{declared_type}' but content analysis suggests it is a '{classified_type}'.",
                suggested_remediation=f"Verify the correct document type. Consider reclassifying as '{classified_type}'.",
                confidence_score=0.75,
            ))

        # ── Extract metadata ─────────────────────────────────────────────
        doc_meta = self._extract_metadata(document_text)
        extracted_metadata.update(doc_meta)

        # ── Validate TMF zone ────────────────────────────────────────────
        tmf_zone = document_metadata.get("tmf_zone")
        if tmf_zone and tmf_zone not in TMF_ZONE_MAP:
            findings.append(self._make_finding(
                finding_type="invalid_tmf_zone",
                severity=FindingSeverity.MAJOR,
                category="TMF Classification",
                title="Invalid TMF zone",
                description=f"TMF zone {tmf_zone} is not a valid zone in the TMF Reference Model (valid: 1-11).",
                suggested_remediation="Assign a valid TMF Reference Model zone (1-11).",
                confidence_score=1.0,
            ))

        return AgentResult(
            agent_name=self.name,
            status="completed",
            findings=findings,
            metadata=extracted_metadata,
        )

    # ── Internal methods ─────────────────────────────────────────────────

    def _parse_document(self, text: str) -> Dict[str, Any]:
        """Extract basic structural information from document text."""
        words = text.split()
        word_count = len(words)

        # Estimate pages (≈300 words per page)
        page_estimate = max(1, word_count // 300)

        # Detect section headings (numbered or uppercase lines)
        section_pattern = re.compile(
            r"^(?:\d+\.[\d.]*\s+[A-Z].*|[A-Z][A-Z\s]{4,})$", re.MULTILINE
        )
        sections = section_pattern.findall(text)

        return {
            "word_count": word_count,
            "page_estimate": page_estimate,
            "sections": sections[:50],  # cap to avoid huge payloads
        }

    def _classify_document(self, text: str) -> str | None:
        """Classify the document type based on keyword heuristics."""
        text_lower = text.lower()
        scores: Dict[str, int] = {}

        for doc_type, keywords in DOCUMENT_TYPE_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw.lower() in text_lower)
            if score > 0:
                scores[doc_type] = score

        if not scores:
            return None

        return max(scores, key=scores.get)  # type: ignore[arg-type]

    def _extract_metadata(self, text: str) -> Dict[str, Any]:
        """Extract structured metadata using regex patterns."""
        metadata: Dict[str, Any] = {}

        # Protocol number
        protocol_match = re.search(
            r"(?:protocol\s*(?:number|no\.?|#)?[:\s]*)([\w\-]+)",
            text,
            re.IGNORECASE,
        )
        if protocol_match:
            metadata["extracted_protocol_number"] = protocol_match.group(1).strip()

        # Version
        version_match = re.search(
            r"(?:version|ver\.?)[:\s]*([\d]+(?:\.[\d]+)*)",
            text,
            re.IGNORECASE,
        )
        if version_match:
            metadata["extracted_version"] = version_match.group(1)

        # Date patterns
        date_match = re.search(
            r"(?:date|dated)[:\s]*(\d{1,2}[\s/-]\w{3,9}[\s/-]\d{2,4}|\d{4}-\d{2}-\d{2})",
            text,
            re.IGNORECASE,
        )
        if date_match:
            metadata["extracted_date"] = date_match.group(1).strip()

        # Sponsor name
        sponsor_match = re.search(
            r"(?:sponsor|sponsored\s+by)[:\s]*([A-Z][\w\s&,]+?)(?:\n|$)",
            text,
            re.IGNORECASE,
        )
        if sponsor_match:
            metadata["extracted_sponsor"] = sponsor_match.group(1).strip()

        # Phase
        phase_match = re.search(
            r"(?:phase)\s*(I{1,3}[ab]?|[1-4][ab]?)",
            text,
            re.IGNORECASE,
        )
        if phase_match:
            metadata["extracted_phase"] = f"Phase {phase_match.group(1)}"

        return metadata
