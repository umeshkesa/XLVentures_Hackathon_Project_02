"""Metrics — tracks recommendation pipeline metrics.

Tracks candidates, rankings, scores, policy violations, average
feasibility, and average cost across recommendation operations.
Deterministic placeholder implementation.
"""

from __future__ import annotations

import structlog

from adip.recommendation.execution.models import RecommendationMetrics

log = structlog.get_logger(__name__)


class RecommendationMetricsCollector:
    """Collects metrics for the recommendation pipeline.

    Deterministic placeholder that tracks counters and accumulators
    for recommendation operations.
    """

    def __init__(self) -> None:
        self._candidates_generated = 0
        self._rankings_performed = 0
        self._scores_calculated = 0
        self._policy_violations = 0
        self._feasibility_scores: list[float] = []
        self._cost_estimates: list[float] = []
        self._confidence_scores: list[float] = []
        self._portfolios_created = 0
        self._quality_assessments = 0
        self._justifications_created = 0
        self._approval_readiness_ready = 0
        self._approval_readiness_review_required = 0
        self._approval_readiness_blocked = 0
        self._quality_scores: list[float] = []
        self._portfolio_quality_assessments = 0
        self._trace_count = 0

    def increment_candidates(self, count: int = 1) -> None:
        self._candidates_generated += max(0, count)

    def increment_rankings(self, count: int = 1) -> None:
        self._rankings_performed += max(0, count)

    def increment_scores(self, count: int = 1) -> None:
        self._scores_calculated += max(0, count)

    def increment_policy_violations(self, count: int = 1) -> None:
        self._policy_violations += max(0, count)

    def increment_portfolios(self, count: int = 1) -> None:
        self._portfolios_created += max(0, count)

    def increment_quality(self, count: int = 1) -> None:
        self._quality_assessments += max(0, count)

    def increment_justifications(self, count: int = 1) -> None:
        self._justifications_created += max(0, count)

    def increment_approval_readiness(self, status: str = "") -> None:
        if status == "READY":
            self._approval_readiness_ready += 1
        elif status == "REQUIRES_REVIEW" or status == "REVIEW_REQUIRED":
            self._approval_readiness_review_required += 1
        elif status == "BLOCKED":
            self._approval_readiness_blocked += 1

    def increment_portfolio_quality(self, count: int = 1) -> None:
        self._portfolio_quality_assessments += max(0, count)

    def record_quality(self, quality: float) -> None:
        self._quality_scores.append(max(0.0, min(1.0, quality)))

    def record_feasibility(self, score: float) -> None:
        self._feasibility_scores.append(max(0.0, min(1.0, score)))

    def record_cost(self, cost: float) -> None:
        self._cost_estimates.append(max(0.0, cost))

    def record_confidence(self, confidence: float) -> None:
        self._confidence_scores.append(max(0.0, min(1.0, confidence)))

    def record_trace(self) -> None:
        self._trace_count += 1

    def snapshot(self) -> RecommendationMetrics:
        """Create a snapshot of current metrics.

        Returns:
            RecommendationMetrics with current values.
        """
        return RecommendationMetrics(
            candidates_generated=self._candidates_generated,
            rankings_performed=self._rankings_performed,
            scores_calculated=self._scores_calculated,
            policy_violations=self._policy_violations,
            average_feasibility=round(
                sum(self._feasibility_scores) / len(self._feasibility_scores), 4
            ) if self._feasibility_scores else 0.0,
            average_cost=round(
                sum(self._cost_estimates) / len(self._cost_estimates), 2
            ) if self._cost_estimates else 0.0,
            average_confidence=round(
                sum(self._confidence_scores) / len(self._confidence_scores), 4
            ) if self._confidence_scores else 0.0,
            portfolios_created=self._portfolios_created,
            quality_assessments=self._quality_assessments,
            justifications_created=self._justifications_created,
            approval_readiness_ready=self._approval_readiness_ready,
            approval_readiness_review_required=self._approval_readiness_review_required,
            approval_readiness_blocked=self._approval_readiness_blocked,
            average_quality=round(sum(self._quality_scores) / len(self._quality_scores), 4) if self._quality_scores else 0.0,
            portfolio_quality_assessments=self._portfolio_quality_assessments,
            trace_count=self._trace_count,
        )

    def reset(self) -> None:
        """Reset all metrics counters."""
        self.__init__()
