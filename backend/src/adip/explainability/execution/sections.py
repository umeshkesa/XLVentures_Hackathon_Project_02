"""ExplanationSections — builds standard explanation sections.

Deterministic placeholder that constructs 8 standard sections
from an ExplanationPackage for structured output.
"""

from __future__ import annotations

import structlog

from adip.explainability.contracts.models import ExplanationPackage
from adip.explainability.execution.models import ExplanationSection

log = structlog.get_logger(__name__)


class ExplanationSections:
    """Builds standard explanation sections from a package.

    Deterministic placeholder that constructs 8 standard sections:
    summary, evidence, reasoning, recommendation, alternatives,
    risks, confidence, and references.
    """

    def build(
        self,
        package: ExplanationPackage,
        correlation_id: str = "",
    ) -> list[ExplanationSection]:
        """Build 8 standard sections from an explanation package.

        Args:
            package: The explanation package to build sections from.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            List of 8 ExplanationSection instances.
        """
        sections: list[ExplanationSection] = []

        sections.append(ExplanationSection(
            section_type="summary",
            title="Summary",
            content=package.primary_narrative.content if package.primary_narrative else "No primary narrative available.",
            order=0,
            audience=package.primary_narrative.audience.value if package.primary_narrative else "",
            citations=[],
            metadata={"correlation_id": correlation_id},
        ))

        sections.append(ExplanationSection(
            section_type="evidence",
            title="Evidence",
            content=f"Package contains {len(package.evidence_citations)} evidence citations supporting the explanation.",
            order=1,
            audience="",
            citations=[str(c.citation_id) for c in package.evidence_citations],
            metadata={"correlation_id": correlation_id, "citation_count": len(package.evidence_citations)},
        ))

        sections.append(ExplanationSection(
            section_type="reasoning",
            title="Reasoning",
            content=package.reasoning_summary or "No reasoning summary available.",
            order=2,
            audience="",
            citations=[],
            metadata={"correlation_id": correlation_id},
        ))

        sections.append(ExplanationSection(
            section_type="recommendation",
            title="Recommendation",
            content=package.recommendation_summary or "No recommendation summary available.",
            order=3,
            audience="",
            citations=[],
            metadata={"correlation_id": correlation_id},
        ))

        supporting_content = "; ".join(
            [n.summary for n in package.supporting_narratives]
        ) if package.supporting_narratives else "No alternative narratives available."
        sections.append(ExplanationSection(
            section_type="alternatives",
            title="Alternatives",
            content=supporting_content,
            order=4,
            audience="",
            citations=[],
            metadata={"correlation_id": correlation_id, "alternative_count": len(package.supporting_narratives)},
        ))

        risks_content = "Risks: " + str(package.metadata.get("risks", "No risks identified."))
        sections.append(ExplanationSection(
            section_type="risks",
            title="Risks",
            content=risks_content,
            order=5,
            audience="",
            citations=[],
            metadata={"correlation_id": correlation_id},
        ))

        sections.append(ExplanationSection(
            section_type="confidence",
            title="Confidence",
            content=f"Overall confidence score: {package.overall_confidence:.2f}",
            order=6,
            audience="",
            citations=[],
            metadata={"correlation_id": correlation_id, "confidence": package.overall_confidence},
        ))

        refs_content = "; ".join(
            [f"{c.citation_type.value}: {c.source_id}" for c in package.evidence_citations]
        ) if package.evidence_citations else "No references available."
        sections.append(ExplanationSection(
            section_type="references",
            title="References",
            content=refs_content,
            order=7,
            audience="",
            citations=[str(c.citation_id) for c in package.evidence_citations],
            metadata={"correlation_id": correlation_id, "reference_count": len(package.evidence_citations)},
        ))

        log.info("Standard sections built", count=len(sections), correlation_id=correlation_id)
        return sections
