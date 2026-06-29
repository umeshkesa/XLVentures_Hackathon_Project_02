"""ExplanationBuilder — constructs explanation packages.

Deterministic placeholder that builds ExplanationPackage
instances from requests, narratives, and citations.
"""

from __future__ import annotations

import structlog

from adip.explainability.contracts.models import (
    ExplanationCitation,
    ExplanationNarrative,
    ExplanationPackage,
    ExplanationRequest,
)
from adip.explainability.execution.models import ExplanationSection

log = structlog.get_logger(__name__)


class ExplanationBuilder:
    """Constructs explanation packages from narratives and citations.

    Deterministic placeholder that builds ExplanationPackage
    instances and generates section structures.
    """

    def build(
        self,
        request: ExplanationRequest,
        narratives: list[ExplanationNarrative],
        citations: list[ExplanationCitation],
        correlation_id: str = "",
    ) -> ExplanationPackage:
        """Build an explanation package from narratives and citations.

        Args:
            request: The explanation request.
            narratives: The narratives to include in the package.
            citations: The citations supporting the narratives.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The built ExplanationPackage.
        """
        primary = narratives[0] if narratives else None
        supporting = narratives[1:] if len(narratives) > 1 else []

        evidence_citations = [c for c in citations if c.citation_type.value == "EVIDENCE"]

        narrative_confidences = [0.85] * len(narratives)
        overall_confidence = round(sum(narrative_confidences) / len(narrative_confidences), 4) if narrative_confidences else 0.0

        package = ExplanationPackage(
            result_id=request.request_id,
            primary_narrative=primary,
            supporting_narratives=supporting,
            evidence_citations=evidence_citations,
            reasoning_summary="Placeholder reasoning summary for explanation package.",
            recommendation_summary="Placeholder recommendation summary for explanation package.",
            overall_confidence=overall_confidence,
            metadata={
                "correlation_id": correlation_id,
                "narrative_count": len(narratives),
                "citation_count": len(citations),
            },
        )
        log.info(
            "Package built",
            package_id=str(package.package_id),
            narratives=len(narratives),
            citations=len(citations),
            confidence=overall_confidence,
        )
        return package

    def build_sections(
        self,
        narratives: list[ExplanationNarrative],
        citations: list[ExplanationCitation],
        correlation_id: str = "",
    ) -> list[ExplanationSection]:
        """Build explanation sections from narratives and citations.

        Creates one section per narrative with associated citations.

        Args:
            narratives: The narratives to convert to sections.
            citations: The citations to associate with sections.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            List of ExplanationSection instances.
        """
        sections: list[ExplanationSection] = []
        for i, narrative in enumerate(narratives):
            narrative_citations = [c for c in citations if str(c.narrative_id) == str(narrative.narrative_id)]
            section = ExplanationSection(
                section_type=narrative.narrative_type.value.lower(),
                title=narrative.title,
                content=narrative.content,
                order=i,
                audience=narrative.audience.value,
                citations=[str(c.citation_id) for c in narrative_citations],
                metadata={"narrative_id": str(narrative.narrative_id), "correlation_id": correlation_id},
            )
            sections.append(section)
        log.info("Sections built", count=len(sections))
        return sections
