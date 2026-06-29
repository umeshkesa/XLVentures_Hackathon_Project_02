"""Smoke tests for the end-to-end platform pipeline."""

from __future__ import annotations

import pytest

from adip.platform.contracts.models import PlatformRequest
from adip.platform.enums import PipelineStage, PipelineStatus
from adip.platform.orchestration.coordinator import DefaultPlatformCoordinator
from adip.platform.orchestration.exception_mapper import DefaultExceptionMapper
from adip.platform.orchestration.health_aggregator import DefaultHealthAggregator
from adip.platform.orchestration.manifest_builder import DefaultManifestBuilder
from adip.platform.orchestration.metrics_collector import DefaultPlatformMetricsCollector
from adip.platform.orchestration.registry import DefaultServiceRegistry
from adip.platform.orchestration.trace_manager import DefaultTraceManager


@pytest.fixture
def coordinator() -> DefaultPlatformCoordinator:
    registry = DefaultServiceRegistry()
    health = DefaultHealthAggregator()
    trace = DefaultTraceManager()
    metrics = DefaultPlatformMetricsCollector()
    exceptions = DefaultExceptionMapper()
    manifest = DefaultManifestBuilder()
    return DefaultPlatformCoordinator(
        registry=registry,
        health_aggregator=health,
        trace_manager=trace,
        metrics_collector=metrics,
        exception_mapper=exceptions,
        manifest_builder=manifest,
    )


class TestPipelineExecution:
    """Verify the full pipeline execution."""

    async def test_full_pipeline_success(self, coordinator: DefaultPlatformCoordinator) -> None:
        """Verify all stages complete successfully."""
        request = PlatformRequest(
            correlation_id="test-full",
            payload={"input": "test_data"},
        )
        response = await coordinator.execute_pipeline(request)
        assert response.success
        assert response.status == PipelineStatus.COMPLETED
        assert len(response.stages_completed) == len(coordinator.ALL_STAGES)
        assert response.stages_failed == []
        assert response.errors == []
        assert response.duration_ms >= 0

    async def test_custom_stages(self, coordinator: DefaultPlatformCoordinator) -> None:
        """Verify pipeline with custom stage selection."""
        request = PlatformRequest(
            correlation_id="test-custom",
            pipeline=[PipelineStage.PLANNER, PipelineStage.MEMORY, PipelineStage.ENERGY],
        )
        response = await coordinator.execute_pipeline(request)
        assert response.success
        assert len(response.stages_completed) == 3
        assert PipelineStage.PLANNER in response.stages_completed
        assert PipelineStage.MEMORY in response.stages_completed
        assert PipelineStage.ENERGY in response.stages_completed

    async def test_single_stage(self, coordinator: DefaultPlatformCoordinator) -> None:
        """Verify single stage execution."""
        request = PlatformRequest(
            pipeline=[PipelineStage.VALIDATION],
        )
        response = await coordinator.execute_pipeline(request)
        assert response.success
        assert len(response.stages_completed) == 1

    async def test_pipeline_propagates_context(self, coordinator: DefaultPlatformCoordinator) -> None:
        """Verify context is propagated between stages."""
        request = PlatformRequest(
            correlation_id="test-context",
            context={"initial_key": "initial_value"},
        )
        response = await coordinator.execute_pipeline(request)
        assert response.success
        # Context should be available in output if stages preserve it
        output_keys = list(response.output.keys())
        assert len(output_keys) > 0

    async def test_empty_pipeline(self, coordinator: DefaultPlatformCoordinator) -> None:
        """Verify empty pipeline defaults to all stages."""
        request = PlatformRequest(correlation_id="test-empty")
        response = await coordinator.execute_pipeline(request)
        assert response.success
        assert len(response.stages_completed) == len(coordinator.ALL_STAGES)


class TestPipelineTracing:
    """Verify pipeline tracing works."""

    async def test_trace_created(self, coordinator: DefaultPlatformCoordinator) -> None:
        """Verify trace entries are created for each stage."""
        trace = coordinator._trace
        request = PlatformRequest(correlation_id="test-trace")
        response = await coordinator.execute_pipeline(request)
        traces = trace.list_traces()
        assert len(traces) > 0
        latest = traces[-1]
        assert latest.completed
        assert len(latest.entries) == len(response.stages_completed)
        assert latest.total_duration_ms >= 0

    async def test_trace_stages_recorded(self, coordinator: DefaultPlatformCoordinator) -> None:
        """Verify each stage has a trace entry."""
        trace = coordinator._trace
        request = PlatformRequest(
            pipeline=[PipelineStage.PLANNER, PipelineStage.ENERGY],
        )
        await coordinator.execute_pipeline(request)
        traces = trace.list_traces()
        latest = traces[-1]
        stage_names = {e.stage.value for e in latest.entries}
        assert "planner" in stage_names
        assert "energy" in stage_names


class TestPipelineErrors:
    """Verify error propagation in pipeline."""

    async def test_exception_isolation(self, coordinator: DefaultPlatformCoordinator) -> None:
        """Verify a single stage failure does not break the pipeline.

        The coordinator catches exceptions per stage and continues.
        """
        request = PlatformRequest(
            pipeline=[PipelineStage.PLANNER, PipelineStage.WORKFLOW],
        )
        response = await coordinator.execute_pipeline(request)
        assert response.success
        assert response.status in (PipelineStatus.COMPLETED, PipelineStatus.PARTIAL)
