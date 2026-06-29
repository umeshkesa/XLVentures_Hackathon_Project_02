"""ExplanationQualityManager — evaluates explanation quality.

Deterministic placeholder that computes quality scores for
explanation packages based on completeness, citation coverage,
trace coverage, readability, consistency, audience suitability,
and policy compliance.
"""

from __future__ import annotations

from typing import Any

import structlog

from adip.explainability.contracts.models import ExplanationCitation, ExplanationPackage
from adip.explainability.execution.models import QualityScore, TraceRecord

log = structlog.get_logger(__name__)


class ExplanationQualityManager:
    """Evaluates quality of explanation packages.

    Deterministic placeholder that computes a multi-dimensional
    quality score for explanation packages.
    """

    def evaluate(
        self,
        package: ExplanationPackage | None,
        citations: list[ExplanationCitation],
        traces: list[TraceRecord],
        correlation_id: str = "",
    ) -> QualityScore:
        """Evaluate the quality of an explanation.

        Calculates completeness, citation coverage, trace coverage,
        readability, consistency, audience suitability, policy compliance,
        and overall weighted score.

        Args:
            package: The explanation package to evaluate.
            citations: The citations associated with the package.
            traces: The trace records associated with the package.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            QualityScore with computed dimension scores.
        """
        completeness = 0.8 if package else 0.0
        citation_coverage = min(1.0, len(citations) / 5.0) if citations else 0.0
        trace_coverage = min(1.0, len(traces) / 3.0) if traces else 0.0
        readability = 0.7
        consistency = 0.8 if (package and package.primary_narrative) else 0.0
        audience_suitability = 0.7
        policy_compliance = 1.0

        overall = (
            0.20 * completeness
            + 0.15 * citation_coverage
            + 0.10 * trace_coverage
            + 0.15 * readability
            + 0.15 * consistency
            + 0.15 * audience_suitability
            + 0.10 * policy_compliance
        )
        overall = round(max(0.0, min(1.0, overall)), 4)

        score = QualityScore(
            completeness=round(completeness, 4),
            citation_coverage=round(citation_coverage, 4),
            trace_coverage=round(trace_coverage, 4),
            readability=readability,
            consistency=round(consistency, 4),
            overall=overall,
            metadata={
                "correlation_id": correlation_id,
                "citation_count": len(citations),
                "trace_count": len(traces),
                "audience_suitability": audience_suitability,
                "policy_compliance": policy_compliance,
            },
        )
        log.info(
            "Quality evaluated",
            completeness=score.completeness,
            citation_coverage=score.citation_coverage,
            trace_coverage=score.trace_coverage,
            readability=score.readability,
            consistency=score.consistency,
            audience_suitability=audience_suitability,
            policy_compliance=policy_compliance,
            overall=score.overall,
        )
        return score

    def evaluate_audience_suitability(
        self,
        narratives: list[Any],
        target_audiences: list[str],
        correlation_id: str = "",
    ) -> float:
        """Calculate the ratio of narratives that match target audiences.

        Args:
            narratives: List of narrative objects.
            target_audiences: List of target audience identifiers.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            Audience suitability score between 0.0 and 1.0.
        """
        if not target_audiences:
            log.info("quality.audience_suitability", score=1.0, correlation_id=correlation_id)
            return 1.0
        matched = sum(
            1 for n in narratives
            if hasattr(n, "audience") and n.audience in target_audiences
        )
        score = matched / len(target_audiences) if target_audiences else 0.0
        score = round(max(0.0, min(1.0, score)), 4)
        log.info("quality.audience_suitability", score=score, matched=matched, total=len(target_audiences), correlation_id=correlation_id)
        return score

    def evaluate_policy_compliance(
        self,
        package: Any,
        policy_violations: list[str],
        correlation_id: str = "",
    ) -> float:
        """Evaluate policy compliance score.

        Returns 1.0 if no violations, 0.5 if any violations,
        0.0 if package is None.

        Args:
            package: The explanation package or None.
            policy_violations: List of policy violation descriptions.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            Policy compliance score between 0.0 and 1.0.
        """
        if package is None:
            log.info("quality.policy_compliance", score=0.0, correlation_id=correlation_id)
            return 0.0
        score = 1.0 if not policy_violations else 0.5
        log.info("quality.policy_compliance", score=score, violations=len(policy_violations), correlation_id=correlation_id)
        return score
