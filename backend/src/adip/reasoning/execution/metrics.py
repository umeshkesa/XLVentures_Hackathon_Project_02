"""ReasoningMetricsCollector — metrics collection for reasoning.

Tracks hypotheses, alternatives, constraints, contradictions,
goals, and average scores during reasoning operations.
Deterministic placeholder implementation.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import structlog

from adip.reasoning.execution.models import ReasoningMetrics

log = structlog.get_logger(__name__)


class ReasoningMetricsCollector:
    """Collects and aggregates reasoning pipeline metrics.

    Deterministic placeholder that tracks counts and statistics
    for reasoning operations.
    """

    def __init__(self) -> None:
        self._hypotheses_count = 0
        self._alternatives_count = 0
        self._constraints_count = 0
        self._contradictions_count = 0
        self._goals_count = 0
        self._scores: list[float] = []
        self._trace_count = 0
        self._reasonings_count = 0
        self._sessions_count = 0
        self._latencies: list[float] = []
        self._reasonings_per_domain: dict[str, int] = {}
        self._reasonings_per_strategy: dict[str, int] = {}
        self._decisions_per_strategy: dict[str, int] = {}
        self._hypotheses_per_strategy: dict[str, int] = {}
        self._inferences_per_domain: dict[str, int] = {}
        self._contradictions_per_severity: dict[str, int] = {}
        self._review_count = 0
        self._readiness_ready = 0
        self._readiness_not_ready = 0
        self._readiness_more_info = 0
        self._quality_scores: list[float] = []

    def increment_hypotheses(self, count: int = 1) -> None:
        """Increment hypotheses count.

        Args:
            count: Number to increment by (default 1).
        """
        self._hypotheses_count += count

    def increment_alternatives(self, count: int = 1) -> None:
        """Increment alternatives count.

        Args:
            count: Number to increment by (default 1).
        """
        self._alternatives_count += count

    def increment_constraints(self, count: int = 1) -> None:
        """Increment constraints count.

        Args:
            count: Number to increment by (default 1).
        """
        self._constraints_count += count

    def increment_contradictions(self, count: int = 1) -> None:
        """Increment contradictions count.

        Args:
            count: Number to increment by (default 1).
        """
        self._contradictions_count += count

    def increment_goals(self, count: int = 1) -> None:
        """Increment goals count.

        Args:
            count: Number to increment by (default 1).
        """
        self._goals_count += count

    def record_score(self, score: float) -> None:
        """Record a reasoning score.

        Args:
            score: The score to record (0.0–1.0).
        """
        self._scores.append(max(0.0, min(1.0, score)))

    def record_trace(self) -> None:
        """Increment trace count."""
        self._trace_count += 1

    def increment_reasonings(self, count: int = 1) -> None:
        """Increment reasonings count.

        Args:
            count: Number to increment by (default 1).
        """
        self._reasonings_count += count

    def increment_sessions(self, count: int = 1) -> None:
        """Increment sessions count.

        Args:
            count: Number to increment by (default 1).
        """
        self._sessions_count += count

    def record_latency(self, latency_ms: float) -> None:
        """Record a latency measurement.

        Args:
            latency_ms: Latency in milliseconds.
        """
        self._latencies.append(max(0.0, latency_ms))

    def increment_reasonings_per_domain(self, domain: str) -> None:
        """Increment reasonings count for a domain.

        Args:
            domain: The domain name.
        """
        self._reasonings_per_domain[domain] = self._reasonings_per_domain.get(domain, 0) + 1

    def increment_reasonings_per_strategy(self, strategy: str) -> None:
        """Increment reasonings count for a strategy.

        Args:
            strategy: The strategy name.
        """
        self._reasonings_per_strategy[strategy] = self._reasonings_per_strategy.get(strategy, 0) + 1

    def increment_decisions_per_strategy(self, strategy: str) -> None:
        """Increment decisions count for a strategy.

        Args:
            strategy: The strategy name.
        """
        self._decisions_per_strategy[strategy] = self._decisions_per_strategy.get(strategy, 0) + 1

    def increment_hypotheses_per_strategy(self, strategy: str) -> None:
        """Increment hypotheses count for a strategy.

        Args:
            strategy: The strategy name.
        """
        self._hypotheses_per_strategy[strategy] = self._hypotheses_per_strategy.get(strategy, 0) + 1

    def increment_inferences_per_domain(self, domain: str) -> None:
        """Increment inferences count for a domain.

        Args:
            domain: The domain name.
        """
        self._inferences_per_domain[domain] = self._inferences_per_domain.get(domain, 0) + 1

    def increment_contradictions_per_severity(self, severity: str) -> None:
        """Increment contradictions count for a severity level.

        Args:
            severity: The severity name.
        """
        self._contradictions_per_severity[severity] = self._contradictions_per_severity.get(severity, 0) + 1

    def increment_reviews(self, count: int = 1) -> None:
        self._review_count += count

    def increment_readiness_ready(self) -> None:
        self._readiness_ready += 1

    def increment_readiness_not_ready(self) -> None:
        self._readiness_not_ready += 1

    def increment_readiness_more_info(self) -> None:
        self._readiness_more_info += 1

    def record_quality_score(self, score: float) -> None:
        self._quality_scores.append(max(0.0, min(1.0, score)))

    def snapshot(self) -> ReasoningMetrics:
        """Create a snapshot of current metrics.

        Returns:
            A ReasoningMetrics model with current values.
        """
        avg_score = sum(self._scores) / len(self._scores) if self._scores else 0.0
        avg_latency = sum(self._latencies) / len(self._latencies) if self._latencies else 0.0
        return ReasoningMetrics(
            metrics_id=str(uuid.uuid4()),
            hypotheses_count=self._hypotheses_count,
            alternatives_count=self._alternatives_count,
            constraints_count=self._constraints_count,
            contradictions_count=self._contradictions_count,
            goals_count=self._goals_count,
            average_score=round(avg_score, 4),
            trace_count=self._trace_count,
            collected_at=datetime.now(UTC),
            reasonings_count=self._reasonings_count,
            sessions_count=self._sessions_count,
            average_latency_ms=round(avg_latency, 4),
            reasonings_per_domain=dict(self._reasonings_per_domain),
            reasonings_per_strategy=dict(self._reasonings_per_strategy),
            decisions_per_strategy=dict(self._decisions_per_strategy),
            hypotheses_per_strategy=dict(self._hypotheses_per_strategy),
            inferences_per_domain=dict(self._inferences_per_domain),
            contradictions_per_severity=dict(self._contradictions_per_severity),
            review_count=self._review_count,
            readiness_ready=self._readiness_ready,
            readiness_not_ready=self._readiness_not_ready,
            readiness_more_info=self._readiness_more_info,
            average_quality=round(avg_quality, 4) if (avg_quality := (sum(self._quality_scores) / len(self._quality_scores) if self._quality_scores else 0.0)) else 0.0,
        )

    def reset(self) -> None:
        """Reset all metrics to defaults."""
        self._hypotheses_count = 0
        self._alternatives_count = 0
        self._constraints_count = 0
        self._contradictions_count = 0
        self._goals_count = 0
        self._scores.clear()
        self._trace_count = 0
        self._reasonings_count = 0
        self._sessions_count = 0
        self._latencies.clear()
        self._reasonings_per_domain.clear()
        self._reasonings_per_strategy.clear()
        self._decisions_per_strategy.clear()
        self._hypotheses_per_strategy.clear()
        self._inferences_per_domain.clear()
        self._contradictions_per_severity.clear()
        self._review_count = 0
        self._readiness_ready = 0
        self._readiness_not_ready = 0
        self._readiness_more_info = 0
        self._quality_scores.clear()
