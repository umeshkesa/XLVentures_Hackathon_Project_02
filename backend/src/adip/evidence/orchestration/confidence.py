"""EvidenceConfidenceCalculator — deterministic confidence heuristics.

Calculates EvidenceConfidence for evidence decisions based on
seven dimensions: quality, trust, correlation, freshness,
completeness, consensus, and weight distribution.

Placeholder implementation using simple deterministic heuristics.
No machine learning or probabilistic models are used.
"""

from __future__ import annotations

import structlog

from adip.evidence.contracts.models import (
    Evidence,
    EvidenceConfidence,
    EvidenceExplainabilityMetadata,
)

log = structlog.get_logger(__name__)


class EvidenceConfidenceCalculator:
    """Calculates deterministic confidence scores for evidence decisions.

    Each dimension is scored 0.0–1.0 based on simple heuristics:
    - Quality: based on the quality score if provided
    - Trust: based on the trust score if provided
    - Correlation: 1.0 if correlated, 0.5 if not
    - Freshness: based on freshness score if provided
    - Completeness: based on metadata field completeness
    - Consensus: based on consensus level if provided
    - Weight Distribution: based on weight distribution metric if provided
    Overall confidence is the average of all seven dimensions.
    """

    def calculate(
        self,
        evidence: Evidence | None = None,
        validation_violations: list[str] | None = None,
        is_normalized: bool = True,
        is_correlated: bool = False,
        trust_score: float | None = None,
        quality_score: float | None = None,
        is_classified: bool = True,
        freshness_score: float | None = None,
        consensus_level: str | None = None,
        weight_distribution_score: float | None = None,
        explanation: EvidenceExplainabilityMetadata | None = None,
    ) -> EvidenceConfidence:
        """Calculate a confidence assessment for an evidence decision.

        Args:
            evidence: The evidence being evaluated (optional).
            validation_violations: List of validation violations.
            is_normalized: Whether the evidence was normalized.
            is_correlated: Whether correlation was performed.
            trust_score: Optional trust score (0.0–1.0).
            quality_score: Optional quality score (0.0–1.0).
            is_classified: Whether classification was performed.
            freshness_score: Optional freshness score (0.0–1.0).
            consensus_level: Optional consensus level (HIGH/MEDIUM/LOW).
            weight_distribution_score: Optional weight distribution score (0.0–1.0).
            explanation: Optional explainability metadata to enrich.

        Returns:
            An EvidenceConfidence with scores for all seven dimensions.
        """
        log.info("evidence_confidence.calculate")

        quality = self._calculate_quality(quality_score)
        trust = self._calculate_trust(trust_score)
        correlation = self._calculate_correlation(is_correlated)
        freshness = self._calculate_freshness(freshness_score)
        completeness = self._calculate_completeness(evidence)
        consensus = self._calculate_consensus_score(consensus_level)
        weight_distribution = self._calculate_weight_distribution(
            weight_distribution_score,
        )

        scores = [
            quality,
            trust,
            correlation,
            freshness,
            completeness,
            consensus,
            weight_distribution,
        ]
        overall_confidence = sum(scores) / len(scores) if scores else 0.0

        return EvidenceConfidence(
            overall_confidence=round(overall_confidence, 4),
            quality=quality,
            trust=trust,
            correlation=correlation,
            freshness=freshness,
            completeness=completeness,
            consensus=consensus,
            weight_distribution=weight_distribution,
        )

    def _calculate_quality(self, quality_score: float | None) -> float:
        """Score based on quality score."""
        if quality_score is None:
            return 0.0
        return max(0.0, min(1.0, quality_score))

    def _calculate_trust(self, trust_score: float | None) -> float:
        """Score based on trust score."""
        if trust_score is None:
            return 0.5
        return max(0.0, min(1.0, trust_score))

    def _calculate_correlation(self, is_correlated: bool) -> float:
        """Score based on correlation status."""
        return 1.0 if is_correlated else 0.5

    def _calculate_freshness(self, freshness_score: float | None) -> float:
        """Score based on freshness score."""
        if freshness_score is None:
            return 0.5
        return max(0.0, min(1.0, freshness_score))

    def _calculate_completeness(self, evidence: Evidence | None) -> float:
        """Score based on metadata field completeness."""
        if evidence is None:
            return 0.0
        fields = [
            bool(evidence.metadata.title),
            bool(evidence.metadata.description),
            bool(evidence.metadata.tags),
            bool(evidence.metadata.category),
            bool(evidence.metadata.source),
            bool(evidence.source.source_id),
            bool(evidence.source.source_type),
            bool(evidence.provenance.owner),
        ]
        filled = sum(1 for f in fields if f)
        return round(filled / len(fields), 4) if fields else 0.0

    def _calculate_consensus_score(self, consensus_level: str | None) -> float:
        """Score based on consensus level."""
        if consensus_level is None:
            return 0.5
        level_map = {"HIGH": 1.0, "MEDIUM": 0.6, "LOW": 0.2}
        return level_map.get(consensus_level.upper(), 0.5)

    def _calculate_weight_distribution(
        self,
        weight_distribution_score: float | None,
    ) -> float:
        """Score based on weight distribution score."""
        if weight_distribution_score is None:
            return 0.5
        return max(0.0, min(1.0, weight_distribution_score))
