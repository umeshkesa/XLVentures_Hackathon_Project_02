"""Import verification tests for platform integration module."""

from __future__ import annotations


class TestImports:
    def test_import_enums(self) -> None:
        from adip.platform.enums import (
            ModuleHealthStatus,
            ModuleName,
            PipelineStage,
            PipelineStatus,
        )
        assert ModuleName
        assert PipelineStage
        assert PipelineStatus
        assert ModuleHealthStatus

    def test_import_models(self) -> None:
        from adip.platform.contracts.models import (
            ModuleHealth,
            PlatformHealth,
            PlatformManifest,
            PlatformMetrics,
            PlatformRequest,
            PlatformResponse,
            PlatformTrace,
            PlatformTraceEntry,
            ServiceDescriptor,
        )
        assert PlatformRequest
        assert PlatformResponse
        assert PlatformHealth
        assert PlatformMetrics
        assert PlatformTrace
        assert PlatformManifest
        assert ServiceDescriptor
        assert ModuleHealth
        assert PlatformTraceEntry

    def test_import_interfaces(self) -> None:
        from adip.platform.interfaces import (
            ExceptionMapper,
            HealthAggregator,
            ManifestBuilder,
            PlatformCoordinator,
            PlatformManager,
            PlatformMetricsCollector,
            PlatformService,
            ServiceRegistry,
            TraceManager,
        )
        assert PlatformService
        assert PlatformManager
        assert PlatformCoordinator
        assert ServiceRegistry
        assert HealthAggregator
        assert TraceManager
        assert PlatformMetricsCollector
        assert ExceptionMapper
        assert ManifestBuilder

    def test_import_orchestration(self) -> None:
        from adip.platform.orchestration import (
            DefaultExceptionMapper,
            DefaultHealthAggregator,
            DefaultManifestBuilder,
            DefaultPlatformCoordinator,
            DefaultPlatformManager,
            DefaultPlatformMetricsCollector,
            DefaultServiceRegistry,
            DefaultTraceManager,
        )
        assert DefaultServiceRegistry
        assert DefaultHealthAggregator
        assert DefaultTraceManager
        assert DefaultPlatformMetricsCollector
        assert DefaultExceptionMapper
        assert DefaultManifestBuilder
        assert DefaultPlatformCoordinator
        assert DefaultPlatformManager

    def test_import_hooks(self) -> None:
        from adip.platform.services.hooks import PlatformHooks, hooks
        assert PlatformHooks
        assert hooks is not None

    def test_import_service(self) -> None:
        from adip.platform.services.service import DefaultPlatformService
        assert DefaultPlatformService

    def test_import_root(self) -> None:
        import adip.platform
        assert adip.platform.__doc__ is not None
