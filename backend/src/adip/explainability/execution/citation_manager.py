"""CitationManager — builds and manages explanation citations.

Deterministic placeholder that creates ExplanationCitation
instances for evidence, reasoning, and recommendation sources.
"""

from __future__ import annotations

import structlog

from adip.explainability.contracts.models import ExplanationCitation
from adip.explainability.enums import CitationType

log = structlog.get_logger(__name__)


class CitationManager:
    """Builds and manages citations for explanation narratives.

    Deterministic placeholder that creates ExplanationCitation
    instances for evidence, reasoning, and recommendation sources.
    """

    def __init__(self) -> None:
        self._citations: list[ExplanationCitation] = []

    def build_citations(
        self,
        narrative_id: str,
        evidence_ids: list[str] | None = None,
        reasoning_ids: list[str] | None = None,
        recommendation_ids: list[str] | None = None,
        correlation_id: str = "",
    ) -> list[ExplanationCitation]:
        """Build citations for a narrative from source IDs.

        Creates one EVIDENCE citation per evidence_id, one
        REASONING citation per reasoning_id, and one RECOMMENDATION
        citation per recommendation_id.

        Args:
            narrative_id: The narrative identifier.
            evidence_ids: Optional list of evidence source IDs.
            reasoning_ids: Optional list of reasoning source IDs.
            recommendation_ids: Optional list of recommendation source IDs.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            List of built ExplanationCitation instances.
        """
        citations: list[ExplanationCitation] = []
        for eid in (evidence_ids or []):
            citations.append(self.build_evidence_citation(narrative_id, eid))
        for rid in (reasoning_ids or []):
            citations.append(self.build_reasoning_citation(narrative_id, rid))
        for rec_id in (recommendation_ids or []):
            citations.append(self.build_recommendation_citation(narrative_id, rec_id))
        log.info(
            "Citations built",
            narrative_id=narrative_id,
            count=len(citations),
            evidence_count=len(evidence_ids or []),
            reasoning_count=len(reasoning_ids or []),
            recommendation_count=len(recommendation_ids or []),
        )
        return citations

    def build_evidence_citation(self, narrative_id: str, source_id: str) -> ExplanationCitation:
        """Build a single evidence citation.

        Args:
            narrative_id: The narrative identifier.
            source_id: The evidence source identifier.

        Returns:
            An ExplanationCitation of type EVIDENCE.
        """
        citation = ExplanationCitation(
            narrative_id=narrative_id,  # type: ignore[arg-type]
            citation_type=CitationType.EVIDENCE,
            source_id=source_id,
            source_type="evidence",
            excerpt=f"Placeholder evidence excerpt from source {source_id}.",
            relevance_score=0.85,
            metadata={"source_id": source_id},
        )
        self._citations.append(citation)
        return citation

    def build_reasoning_citation(self, narrative_id: str, source_id: str) -> ExplanationCitation:
        """Build a single reasoning citation.

        Args:
            narrative_id: The narrative identifier.
            source_id: The reasoning source identifier.

        Returns:
            An ExplanationCitation of type REASONING.
        """
        citation = ExplanationCitation(
            narrative_id=narrative_id,  # type: ignore[arg-type]
            citation_type=CitationType.REASONING,
            source_id=source_id,
            source_type="reasoning",
            excerpt=f"Placeholder reasoning excerpt from source {source_id}.",
            relevance_score=0.90,
            metadata={"source_id": source_id},
        )
        self._citations.append(citation)
        return citation

    def build_recommendation_citation(self, narrative_id: str, source_id: str) -> ExplanationCitation:
        """Build a single recommendation citation.

        Args:
            narrative_id: The narrative identifier.
            source_id: The recommendation source identifier.

        Returns:
            An ExplanationCitation of type RECOMMENDATION.
        """
        citation = ExplanationCitation(
            narrative_id=narrative_id,  # type: ignore[arg-type]
            citation_type=CitationType.RECOMMENDATION,
            source_id=source_id,
            source_type="recommendation",
            excerpt=f"Placeholder recommendation excerpt from source {source_id}.",
            relevance_score=0.80,
            metadata={"source_id": source_id},
        )
        self._citations.append(citation)
        return citation

    def get_by_narrative(self, narrative_id: str) -> list[ExplanationCitation]:
        """Get all citations for a narrative.

        Args:
            narrative_id: The narrative identifier.

        Returns:
            List of ExplanationCitation instances for the narrative.
        """
        return [c for c in self._citations if str(c.narrative_id) == narrative_id]

    def get_by_type(self, citation_type: CitationType) -> list[ExplanationCitation]:
        """Get all citations of a specific type.

        Args:
            citation_type: The citation type to filter by.

        Returns:
            List of ExplanationCitation instances of the given type.
        """
        return [c for c in self._citations if c.citation_type == citation_type]

    def get_all(self) -> list[ExplanationCitation]:
        """Get all built citations.

        Returns:
            List of all ExplanationCitation instances.
        """
        return list(self._citations)

    def clear(self) -> None:
        """Clear all built citations."""
        self._citations.clear()
        log.info("Citations cleared")

    def count(self) -> int:
        """Get the total number of built citations.

        Returns:
            The number of citations.
        """
        return len(self._citations)
