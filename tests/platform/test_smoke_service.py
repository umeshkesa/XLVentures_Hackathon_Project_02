"""Smoke tests for the DefaultPlatformService (ONLY public API)."""

from __future__ import annotations

import pytest

from adip.platform.contracts.models import PlatformRequest
from adip.platform.enums import ModuleName, PipelineStage
from adip.platform.orchestration.coordinator import DefaultPlatformCoordinator
from adip.platform.orchestration.exception_mapper import DefaultExceptionMapper
from adip.platform.orchestration.health_aggregator import DefaultHealthAggregator
from adip.platform.orchestration.manager import DefaultPlatformManager
from adip.platform.orchestration.manifest_builder import DefaultManifestBuilder
from adip.platform.orchestration.metrics_collector import DefaultPlatformMetricsCollector
from adip.platform.orchestration.registry import DefaultServiceRegistry
from adip.platform.orchestration.trace_manager import DefaultTraceManager
from adip.platform.services.service import DefaultPlatformService


@pytest.fixture
def platform_service() -> DefaultPlatformService:
    registry = DefaultServiceRegistry()
    health = DefaultHealthAggregator()
    trace = DefaultTraceManager()
    metrics = DefaultPlatformMetricsCollector()
    exceptions = DefaultExceptionMapper()
    manifest = DefaultManifestBuilder()
    coordinator = DefaultPlatformCoordinator(
        registry=registry,
        health_aggregator=health,
        trace_manager=trace,
        metrics_collector=metrics,
        exception_mapper=exceptions,
        manifest_builder=manifest,
    )
    manager = DefaultPlatformManager(coordinator)
    return DefaultPlatformService(manager)


class TestPlatformService:
    """Smoke tests for DefaultPlatformService."""

    async def test_execute_pipeline_success(self, platform_service: DefaultPlatformService) -> None:
        request = PlatformRequest(correlation_id="svc-test")
        response = await platform_service.execute_pipeline(request)
        assert response.success
        assert response.correlation_id == "svc-test"

    async def test_execute_pipeline_with_stages(self, platform_service: DefaultPlatformService) -> None:
        request = PlatformRequest(
            pipeline=[PipelineStage.PLANNER, PipelineStage.MEMORY],
        )
        response = await platform_service.execute_pipeline(request)
        assert response.success
        assert len(response.stages_completed) == 2

    async def test_get_health(self, platform_service: DefaultPlatformService) -> None:
        health = await platform_service.get_health()
        assert health.overall_status is not None
        assert len(health.modules) == len(ModuleName)

    async def test_get_metrics(self, platform_service: DefaultPlatformService) -> None:
        metrics = await platform_service.get_metrics()
        assert metrics.total_requests >= 0

    async def test_get_manifest(self, platform_service: DefaultPlatformService) -> None:
        manifest = await platform_service.get_manifest()
        assert manifest.platform_version == "1.0.0"

    async def test_get_trace(self, platform_service: DefaultPlatformService) -> None:
        trace = await platform_service.get_trace("nonexistent")
        assert trace is None

    async def test_list_traces(self, platform_service: DefaultPlatformService) -> None:
        traces = await platform_service.list_traces()
        assert traces == []
