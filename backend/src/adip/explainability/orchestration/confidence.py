"""ExplanationConfidenceCalculator — calculates explanation confidence.

Computes 5-dimension confidence scores for explanation results
based on citation coverage, trace completeness, narrative
completeness, evidence coverage, and consistency.
Deterministic placeholder implementation.
"""

from __future__ import annotations

import structlog

from adip.explainability.contracts.models import ExplanationConfidence, ExplanationPackage
from adip.explainability.execution.models import QualityScore

log = structlog.get_logger(__name__)


class ExplanationConfidenceCalculator:
    """Calculates explanation confidence scores.

    Deterministic placeholder that computes a 5-dimension confidence
    assessment:
    - citation_coverage (20%)
    - trace_completeness (20%)
    - narrative_completeness (20%)
    - evidence_coverage (20%)
    - consistency (20%)
    """

    def calculate(
        self,
        package: ExplanationPackage,
        quality: QualityScore,
        correlation_id: str = "",
    ) -> ExplanationConfidence:
        """Calculate a 5-dimension confidence score.

        Dimensions and weights:
        - citation_coverage (20%): quality.citation_coverage (0-1)
        - trace_completeness (20%): quality.trace_coverage (0-1)
        - narrative_completeness (20%): quality.completeness (0-1)
        - evidence_coverage (20%): quality.completeness * 0.9 (deterministic placeholder)
        - consistency (20%): quality.consistency (0-1)

        Args:
            package: The explanation package to assess.
            quality: The quality score from the quality manager.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            ExplanationConfidence with all 5 dimensions calculated.
        """
        citation_coverage = max(0.0, min(1.0, quality.citation_coverage))
        trace_completeness = max(0.0, min(1.0, quality.trace_coverage))
        narrative_completeness = max(0.0, min(1.0, quality.completeness))
        evidence_coverage = max(0.0, min(1.0, quality.completeness * 0.9))
        consistency = max(0.0, min(1.0, quality.consistency))

        overall = round(
            citation_coverage * 0.20
            + trace_completeness * 0.20
            + narrative_completeness * 0.20
            + evidence_coverage * 0.20
            + consistency * 0.20,
            4,
        )

        log.info(
            "confidence.calculate",
            overall=overall,
            citation_coverage=citation_coverage,
            trace_completeness=trace_completeness,
            narrative_completeness=narrative_completeness,
            evidence_coverage=evidence_coverage,
            consistency=consistency,
            correlation_id=correlation_id,
        )

        return ExplanationConfidence(
            overall_confidence=overall,
            narrative_quality=narrative_completeness,
            citation_accuracy=citation_coverage,
            completeness=trace_completeness,
            audience_coverage=evidence_coverage,
            evidence_coverage=evidence_coverage,
            consistency=consistency,
            metadata={
                "evidence_coverage": evidence_coverage,
                "consistency": consistency,
            },
        )
