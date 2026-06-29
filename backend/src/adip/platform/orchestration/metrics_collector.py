"""DefaultPlatformMetricsCollector — unified metrics across the platform."""

from __future__ import annotations

import structlog

from adip.platform.contracts.models import PlatformMetrics
from adip.platform.enums import PipelineStage
from adip.platform.interfaces import PlatformMetricsCollector

logger = structlog.get_logger(__name__)


class DefaultPlatformMetricsCollector(PlatformMetricsCollector):
    """Default platform metrics collector.

    Maintains in-memory counters for pipeline executions,
    stage errors, and aggregated timing.
    """

    def __init__(self) -> None:
        self._total_requests: int = 0
        self._successful_requests: int = 0
        self._failed_requests: int = 0
        self._partial_requests: int = 0
        self._total_duration_ms: float = 0.0
        self._per_stage_counts: dict[str, int] = {}
        self._per_stage_errors: dict[str, int] = {}
        logger.debug("metrics_collector.initialized")

    def record_request(
        self,
        success: bool,
        duration_ms: float,
        stages: list[PipelineStage],
    ) -> None:
        """Record a pipeline request execution."""
        self._total_requests += 1
        self._total_duration_ms += duration_ms

        if success:
            self._successful_requests += 1
        else:
            self._failed_requests += 1

        for stage in stages:
            key = stage.value
            self._per_stage_counts[key] = self._per_stage_counts.get(key, 0) + 1

        logger.debug(
            "metrics_collector.request_recorded",
            success=success,
            duration_ms=duration_ms,
            stage_count=len(stages),
        )

    def record_stage_error(self, stage: PipelineStage) -> None:
        """Record a stage error."""
        key = stage.value
        self._per_stage_errors[key] = self._per_stage_errors.get(key, 0) + 1
        logger.debug("metrics_collector.stage_error", stage=stage.value)

    def get_snapshot(self) -> PlatformMetrics:
        """Get a snapshot of current metrics."""
        avg = self._total_duration_ms / max(self._total_requests, 1)
        return PlatformMetrics(
            total_requests=self._total_requests,
            successful_requests=self._successful_requests,
            failed_requests=self._failed_requests,
            partial_requests=self._partial_requests,
            average_duration_ms=round(avg, 2),
            total_duration_ms=round(self._total_duration_ms, 2),
            per_stage_counts=dict(self._per_stage_counts),
            per_stage_errors=dict(self._per_stage_errors),
        )

    def reset(self) -> None:
        """Reset all metrics."""
        self._total_requests = 0
        self._successful_requests = 0
        self._failed_requests = 0
        self._partial_requests = 0
        self._total_duration_ms = 0.0
        self._per_stage_counts.clear()
        self._per_stage_errors.clear()
        logger.debug("metrics_collector.reset")
