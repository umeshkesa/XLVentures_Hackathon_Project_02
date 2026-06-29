"""KnowledgeConfidenceCalculator — computes confidence and quality scores.

Produces KnowledgeConfidence from raw retrieval scores, metadata,
version information, and provenance. Placeholder implementation
using deterministic heuristics — no ML or statistical models.
"""

from __future__ import annotations

import structlog

from adip.knowledge.contracts.models import KnowledgeConfidence, KnowledgeResult

log = structlog.get_logger(__name__)


class KnowledgeConfidenceCalculator:
    """Computes confidence, quality, freshness, and completeness scores."""

    def calculate(
        self,
        results: list[KnowledgeResult],
        version: int = 1,
    ) -> KnowledgeConfidence:
        """Calculate confidence metrics for a set of retrieval results.

        Uses deterministic placeholder heuristics:
        - quality: average retrieval score across results
        - freshness: decays with version distance from latest
        - completeness: proportion of results with high scores
        - overall: weighted average of all sub-scores
        """
        log.info("confidence.calculate", results=len(results), version=version)

        if not results:
            return KnowledgeConfidence()

        avg_score = sum(r.score for r in results) / len(results)
        quality_score = min(1.0, avg_score * 1.2)

        freshness_base = max(0.0, 1.0 - (version - 1) * 0.1)
        freshness_score = min(1.0, freshness_base)

        high_scorers = sum(1 for r in results if r.score >= 0.7)
        completeness_score = min(1.0, high_scorers / max(1, len(results)))

        overall_confidence = (
            quality_score * 0.4
            + freshness_score * 0.3
            + completeness_score * 0.3
        )

        confidence = KnowledgeConfidence(
            overall_confidence=round(overall_confidence, 4),
            quality_score=round(quality_score, 4),
            freshness_score=round(freshness_score, 4),
            completeness_score=round(completeness_score, 4),
        )
        log.info(
            "confidence.calculate.complete",
            overall=confidence.overall_confidence,
            quality=confidence.quality_score,
        )
        return confidence
