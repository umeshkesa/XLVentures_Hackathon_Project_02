"""Evidence metrics collection.

Tracks statistics and metrics for evidence processing.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from pydantic import BaseModel, Field


class EvidenceMetrics(BaseModel):
    """Snapshot of evidence processing metrics."""

    metrics_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique metrics identifier")
    evidence_count: int = Field(default=0, ge=0, description="Total evidence processed")
    bundle_count: int = Field(default=0, ge=0, description="Total bundles created")
    source_count: int = Field(default=0, ge=0, description="Number of unique sources")
    domain_count: int = Field(default=0, ge=0, description="Number of domains")
    classification_count: dict[str, int] = Field(default_factory=dict, description="Evidence per classification")
    priority_distribution: dict[str, int] = Field(default_factory=dict, description="Evidence per priority level")
    trust_distribution: dict[str, int] = Field(default_factory=dict, description="Evidence per trust range")
    correlations_count: int = Field(default=0, ge=0, description="Total correlations found")
    conflicts_count: int = Field(default=0, ge=0, description="Total conflicts detected")
    average_quality: float = Field(default=0.0, ge=0.0, le=1.0, description="Average quality score")
    trace_count: int = Field(default=0, ge=0, description="Total trace records")
    consensus_distribution: dict[str, int] = Field(default_factory=dict, description="Consensus level distribution")
    weight_distribution: dict[str, int] = Field(default_factory=dict, description="Weight value distribution")
    quality_distribution: dict[str, int] = Field(default_factory=dict, description="Quality score distribution")
    correlation_distribution: dict[str, int] = Field(default_factory=dict, description="Correlation score distribution")
    consistency_distribution: dict[str, int] = Field(default_factory=dict, description="Consistency level distribution")
    collected_at: datetime = Field(default_factory=lambda: datetime.now(UTC), description="When metrics were collected")


class EvidenceMetricsCollector:
    """Collects and aggregates evidence processing metrics.

    Deterministic placeholder that tracks counts and distributions.
    """

    def __init__(self) -> None:
        self._evidence_count = 0
        self._bundle_count = 0
        self._source_ids: set[str] = set()
        self._domain_ids: set[str] = set()
        self._classification_counts: dict[str, int] = {}
        self._priority_distribution: dict[str, int] = {}
        self._trust_distribution: dict[str, int] = {}
        self._correlations_count = 0
        self._conflicts_count = 0
        self._quality_scores: list[float] = []
        self._trace_count = 0
        self._consensus_distribution: dict[str, int] = {}
        self._weight_distribution: dict[str, int] = {}
        self._quality_distribution: dict[str, int] = {}
        self._correlation_distribution: dict[str, int] = {}
        self._consistency_distribution: dict[str, int] = {}

    def increment_evidence(self, domain: str | None = None, source_id: str | None = None) -> None:
        """Increment evidence count.

        Args:
            domain: Optional domain to track.
            source_id: Optional source ID to track.
        """
        self._evidence_count += 1
        if domain:
            self._domain_ids.add(domain)
        if source_id:
            self._source_ids.add(source_id)

    def increment_bundle(self) -> None:
        """Increment bundle count."""
        self._bundle_count += 1

    def increment_correlation(self) -> None:
        """Increment correlation count."""
        self._correlations_count += 1

    def increment_conflict(self) -> None:
        """Increment conflict count."""
        self._conflicts_count += 1

    def record_classification(self, classification: str) -> None:
        """Record a classification.

        Args:
            classification: The classification value.
        """
        self._classification_counts[classification] = (
            self._classification_counts.get(classification, 0) + 1
        )

    def record_priority(self, priority: str) -> None:
        """Record a priority assignment.

        Args:
            priority: The priority level.
        """
        self._priority_distribution[priority] = (
            self._priority_distribution.get(priority, 0) + 1
        )

    def record_trust_score(self, score: float) -> None:
        """Record a trust score.

        Args:
            score: The trust score (0.0–1.0).
        """
        if score < 0.3:
            bucket = "low"
        elif score < 0.7:
            bucket = "medium"
        else:
            bucket = "high"
        self._trust_distribution[bucket] = (
            self._trust_distribution.get(bucket, 0) + 1
        )

    def record_quality(self, score: float) -> None:
        """Record a quality assessment score.

        Args:
            score: The quality score (0.0–1.0).
        """
        self._quality_scores.append(score)

    def record_trace(self) -> None:
        """Increment trace count."""
        self._trace_count += 1

    def record_consensus(self, level: str) -> None:
        """Record a consensus level.

        Args:
            level: The consensus level (HIGH, MEDIUM, LOW).
        """
        self._consensus_distribution[level] = (
            self._consensus_distribution.get(level, 0) + 1
        )

    def record_weight(self, weight: float) -> None:
        """Record a weight value into a distribution bucket.

        Args:
            weight: The weight value (0.0–1.0).
        """
        if weight < 0.3:
            bucket = "low"
        elif weight < 0.7:
            bucket = "medium"
        else:
            bucket = "high"
        self._weight_distribution[bucket] = (
            self._weight_distribution.get(bucket, 0) + 1
        )

    def record_quality_distribution(self, score: float) -> None:
        """Record a quality score into a distribution bucket.

        Args:
            score: The quality score (0.0–1.0).
        """
        if score < 0.3:
            bucket = "low"
        elif score < 0.7:
            bucket = "medium"
        else:
            bucket = "high"
        self._quality_distribution[bucket] = (
            self._quality_distribution.get(bucket, 0) + 1
        )

    def record_correlation_distribution(self, score: float) -> None:
        """Record a correlation score into a distribution bucket.

        Args:
            score: The correlation score (0.0–1.0).
        """
        if score < 0.3:
            bucket = "low"
        elif score < 0.7:
            bucket = "medium"
        else:
            bucket = "high"
        self._correlation_distribution[bucket] = (
            self._correlation_distribution.get(bucket, 0) + 1
        )

    def record_consistency(self, level: str) -> None:
        """Record a consistency level.

        Args:
            level: The consistency level (HIGH, MEDIUM, LOW).
        """
        self._consistency_distribution[level] = (
            self._consistency_distribution.get(level, 0) + 1
        )

    def snapshot(self) -> EvidenceMetrics:
        """Create a snapshot of current metrics.

        Returns:
            An EvidenceMetrics model with current values.
        """
        avg_quality = (
            sum(self._quality_scores) / len(self._quality_scores)
            if self._quality_scores
            else 0.0
        )
        return EvidenceMetrics(
            evidence_count=self._evidence_count,
            bundle_count=self._bundle_count,
            source_count=len(self._source_ids),
            domain_count=len(self._domain_ids),
            classification_count=dict(self._classification_counts),
            priority_distribution=dict(self._priority_distribution),
            trust_distribution=dict(self._trust_distribution),
            correlations_count=self._correlations_count,
            conflicts_count=self._conflicts_count,
            average_quality=round(avg_quality, 4),
            trace_count=self._trace_count,
            consistency_distribution=dict(self._consistency_distribution),
            consensus_distribution=dict(self._consensus_distribution),
            weight_distribution=dict(self._weight_distribution),
            quality_distribution=dict(self._quality_distribution),
            correlation_distribution=dict(self._correlation_distribution),
        )

    def reset(self) -> None:
        """Reset all metrics to defaults."""
        self._evidence_count = 0
        self._bundle_count = 0
        self._source_ids.clear()
        self._domain_ids.clear()
        self._classification_counts.clear()
        self._priority_distribution.clear()
        self._trust_distribution.clear()
        self._correlations_count = 0
        self._conflicts_count = 0
        self._quality_scores.clear()
        self._trace_count = 0
        self._consensus_distribution.clear()
        self._weight_distribution.clear()
        self._quality_distribution.clear()
        self._correlation_distribution.clear()
        self._consistency_distribution.clear()
