"""Metrics — tracks explanation pipeline metrics.

Tracks explanations, narratives, citations, audience distribution,
template usage, quality scores, reviews, versions, readiness,
lineage, snapshots, and confidence across explanation operations.
Deterministic placeholder implementation.
"""

from __future__ import annotations

from datetime import UTC, datetime

import structlog

from adip.explainability.execution.models import ExplainabilityMetrics

log = structlog.get_logger(__name__)


class ExplainabilityMetricsCollector:
    """Collects metrics for the explanation pipeline.

    Deterministic placeholder that tracks counters and accumulators
    for explanation operations, including Phase 3.5 components.
    """

    def __init__(self) -> None:
        self._explanations_total = 0
        self._narratives_total = 0
        self._citations_total = 0
        self._audience_counts: dict[str, int] = {}
        self._template_counts: dict[str, int] = {}
        self._quality_scores: list[float] = []
        self._reviews_total = 0
        self._versions_total = 0
        self._readiness_by_status: dict[str, int] = {}
        self._lineage_entries_total = 0
        self._snapshots_total = 0
        self._confidence_scores: list[float] = []
        self._compliance_total = 0
        self._audits_total = 0
        self._exports_total = 0
        self._justifications_total = 0

    def increment_explanations(self, count: int = 1) -> None:
        """Increment the total explanation count.

        Args:
            count: The number to increment by (default 1).
        """
        self._explanations_total += max(0, count)

    def increment_narratives(self, count: int = 1) -> None:
        """Increment the total narrative count.

        Args:
            count: The number to increment by (default 1).
        """
        self._narratives_total += max(0, count)

    def increment_citations(self, count: int = 1) -> None:
        """Increment the total citation count.

        Args:
            count: The number to increment by (default 1).
        """
        self._citations_total += max(0, count)

    def record_audience(self, audience: str) -> None:
        """Record an audience usage.

        Args:
            audience: The audience identifier.
        """
        self._audience_counts[audience] = self._audience_counts.get(audience, 0) + 1

    def record_template(self, template_type: str) -> None:
        """Record a template usage.

        Args:
            template_type: The template type identifier.
        """
        self._template_counts[template_type] = self._template_counts.get(template_type, 0) + 1

    def record_quality(self, quality: float) -> None:
        """Record a quality score.

        Args:
            quality: The quality score to record (clamped to 0.0-1.0).
        """
        self._quality_scores.append(max(0.0, min(1.0, quality)))

    def increment_reviews(self, count: int = 1) -> None:
        """Increment the total review count.

        Args:
            count: The number to increment by (default 1).
        """
        self._reviews_total += max(0, count)

    def increment_versions(self, count: int = 1) -> None:
        """Increment the total version count.

        Args:
            count: The number to increment by (default 1).
        """
        self._versions_total += max(0, count)

    def increment_readiness(self, status: str) -> None:
        """Record a readiness assessment.

        Args:
            status: The readiness status string.
        """
        self._readiness_by_status[status] = self._readiness_by_status.get(status, 0) + 1

    def increment_lineage_entries(self, count: int = 1) -> None:
        """Increment the total lineage entry count.

        Args:
            count: The number to increment by (default 1).
        """
        self._lineage_entries_total += max(0, count)

    def increment_snapshots(self, count: int = 1) -> None:
        """Increment the total snapshot count.

        Args:
            count: The number to increment by (default 1).
        """
        self._snapshots_total += max(0, count)

    def record_confidence(self, score: float) -> None:
        """Record a confidence score.

        Args:
            score: The confidence score to record (clamped to 0.0-1.0).
        """
        self._confidence_scores.append(max(0.0, min(1.0, score)))

    def increment_compliance(self, count: int = 1) -> None:
        """Increment the total compliance check count.

        Args:
            count: The number to increment by (default 1).
        """
        self._compliance_total += max(0, count)

    def increment_readiness_ready(self, count: int = 1) -> None:
        """Increment the READY readiness count.

        Args:
            count: The number to increment by (default 1).
        """
        self._readiness_by_status["READY"] = self._readiness_by_status.get("READY", 0) + max(0, count)

    def increment_readiness_review(self, count: int = 1) -> None:
        """Increment the REVIEW_REQUIRED readiness count.

        Args:
            count: The number to increment by (default 1).
        """
        self._readiness_by_status["REVIEW_REQUIRED"] = self._readiness_by_status.get("REVIEW_REQUIRED", 0) + max(0, count)

    def increment_readiness_incomplete(self, count: int = 1) -> None:
        """Increment the INCOMPLETE readiness count.

        Args:
            count: The number to increment by (default 1).
        """
        self._readiness_by_status["INCOMPLETE"] = self._readiness_by_status.get("INCOMPLETE", 0) + max(0, count)

    def increment_readiness_non_compliant(self, count: int = 1) -> None:
        """Increment the NON_COMPLIANT readiness count.

        Args:
            count: The number to increment by (default 1).
        """
        self._readiness_by_status["NON_COMPLIANT"] = self._readiness_by_status.get("NON_COMPLIANT", 0) + max(0, count)

    def increment_audits(self, count: int = 1) -> None:
        """Increment the total audit count.

        Args:
            count: The number to increment by (default 1).
        """
        self._audits_total += max(0, count)

    def increment_exports(self, count: int = 1) -> None:
        """Increment the total export count.

        Args:
            count: The number to increment by (default 1).
        """
        self._exports_total += max(0, count)

    def increment_justifications(self, count: int = 1) -> None:
        """Increment the total justification count.

        Args:
            count: The number to increment by (default 1).
        """
        self._justifications_total += max(0, count)

    def snapshot(self) -> ExplainabilityMetrics:
        """Create a snapshot of current metrics.

        Returns:
            ExplainabilityMetrics with current values.
        """
        avg_quality = (
            round(sum(self._quality_scores) / len(self._quality_scores), 4)
            if self._quality_scores
            else 0.0
        )
        avg_completeness = avg_quality
        avg_confidence = (
            round(sum(self._confidence_scores) / len(self._confidence_scores), 4)
            if self._confidence_scores
            else 0.0
        )

        return ExplainabilityMetrics(
            explanations_total=self._explanations_total,
            narratives_total=self._narratives_total,
            citations_total=self._citations_total,
            audience_distribution=dict(self._audience_counts),
            template_usage=dict(self._template_counts),
            average_quality=avg_quality,
            average_completeness=avg_completeness,
            reviews_total=self._reviews_total,
            versions_total=self._versions_total,
            readiness_by_status=dict(self._readiness_by_status),
            lineage_entries_total=self._lineage_entries_total,
            snapshots_total=self._snapshots_total,
            average_confidence=avg_confidence,
            compliance_total=self._compliance_total,
            readiness_ready=self._readiness_by_status.get("READY", 0),
            readiness_review=self._readiness_by_status.get("REVIEW_REQUIRED", 0),
            readiness_incomplete=self._readiness_by_status.get("INCOMPLETE", 0),
            readiness_non_compliant=self._readiness_by_status.get("NON_COMPLIANT", 0),
            audits_total=self._audits_total,
            exports_total=self._exports_total,
            justifications_total=self._justifications_total,
            collected_at=datetime.now(UTC),
        )

    def reset(self) -> None:
        """Reset all metrics counters."""
        self.__init__()
        log.info("Metrics collector reset")
