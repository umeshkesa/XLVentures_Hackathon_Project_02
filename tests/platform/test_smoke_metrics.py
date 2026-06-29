"""Smoke tests for platform metrics collection."""

from __future__ import annotations

import pytest

from adip.platform.enums import PipelineStage
from adip.platform.orchestration.metrics_collector import DefaultPlatformMetricsCollector


class TestMetricsCollection:
    """Verify platform-wide metrics collection."""

    def test_initial_state(self) -> None:
        """Verify initial metrics are all zero."""
        metrics = DefaultPlatformMetricsCollector()
        snapshot = metrics.get_snapshot()
        assert snapshot.total_requests == 0
        assert snapshot.successful_requests == 0
        assert snapshot.failed_requests == 0
        assert snapshot.average_duration_ms == 0.0
        assert snapshot.per_stage_counts == {}
        assert snapshot.per_stage_errors == {}

    def test_record_successful_request(self) -> None:
        """Verify recording a successful request increments counters."""
        metrics = DefaultPlatformMetricsCollector()
        metrics.record_request(
            success=True,
            duration_ms=100.0,
            stages=[PipelineStage.PLANNER, PipelineStage.MEMORY],
        )
        snapshot = metrics.get_snapshot()
        assert snapshot.total_requests == 1
        assert snapshot.successful_requests == 1
        assert snapshot.failed_requests == 0
        assert snapshot.average_duration_ms == 100.0
        assert snapshot.total_duration_ms == 100.0
        assert snapshot.per_stage_counts["planner"] == 1
        assert snapshot.per_stage_counts["memory"] == 1

    def test_record_failed_request(self) -> None:
        """Verify recording a failed request increments failed counter."""
        metrics = DefaultPlatformMetricsCollector()
        metrics.record_request(
            success=False,
            duration_ms=50.0,
            stages=[PipelineStage.PLANNER],
        )
        snapshot = metrics.get_snapshot()
        assert snapshot.total_requests == 1
        assert snapshot.successful_requests == 0
        assert snapshot.failed_requests == 1

    def test_record_stage_error(self) -> None:
        """Verify stage errors are tracked."""
        metrics = DefaultPlatformMetricsCollector()
        metrics.record_stage_error(PipelineStage.PLANNER)
        metrics.record_stage_error(PipelineStage.PLANNER)
        metrics.record_stage_error(PipelineStage.MEMORY)
        snapshot = metrics.get_snapshot()
        assert snapshot.per_stage_errors["planner"] == 2
        assert snapshot.per_stage_errors["memory"] == 1

    def test_multiple_requests(self) -> None:
        """Verify multiple requests accumulate correctly."""
        metrics = DefaultPlatformMetricsCollector()
        metrics.record_request(success=True, duration_ms=100.0, stages=[PipelineStage.PLANNER])
        metrics.record_request(success=True, duration_ms=200.0, stages=[PipelineStage.PLANNER, PipelineStage.MEMORY])
        metrics.record_request(success=False, duration_ms=50.0, stages=[PipelineStage.ENERGY])
        snapshot = metrics.get_snapshot()
        assert snapshot.total_requests == 3
        assert snapshot.successful_requests == 2
        assert snapshot.failed_requests == 1
        assert snapshot.average_duration_ms == pytest.approx(116.67, rel=0.1)
        assert snapshot.per_stage_counts["planner"] == 2

    def test_reset(self) -> None:
        """Verify reset clears all metrics."""
        metrics = DefaultPlatformMetricsCollector()
        metrics.record_request(success=True, duration_ms=100.0, stages=[PipelineStage.PLANNER])
        metrics.record_stage_error(PipelineStage.PLANNER)
        metrics.reset()
        snapshot = metrics.get_snapshot()
        assert snapshot.total_requests == 0
        assert snapshot.per_stage_counts == {}
        assert snapshot.per_stage_errors == {}
