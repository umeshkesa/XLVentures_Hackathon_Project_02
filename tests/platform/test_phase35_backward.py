"""Phase 3.5 smoke tests — Backward Compatibility."""

from __future__ import annotations

from adip.platform.contracts.models import (
    IntegrationAuditPackage,
    PlatformCompatibilityReport,
    PlatformDiagnosticsResult,
    PlatformHealth,
    PlatformManifest,
    PlatformValidationResult,
)
from adip.platform.enums import ModuleHealthStatus, ModuleName
from adip.platform.orchestration.audit_package import (
    DefaultIntegrationAuditPackageGenerator,
)
from adip.platform.orchestration.registry import DefaultServiceRegistry


class TestBackwardCompatibility:
    """Verify Phase 3.5 doesn't break Phase 1-3 contracts."""

    def test_audit_package_backward_compat(self) -> None:
        """Old-style audit package still works without new optional fields."""
        validation = PlatformValidationResult(
            platform_valid=True, bootstrap_valid=True, contracts_valid=True,
            diagnostics_valid=True, health_status="healthy", message="OK",
        )
        compatibility = PlatformCompatibilityReport(platform="OK", pairs_validated=12, pairs_ok=12)
        diagnostics = PlatformDiagnosticsResult(all_valid=True, service_count=17, module_count=17)
        health = PlatformHealth(overall_status=ModuleHealthStatus.HEALTHY, modules={}, healthy_count=17, total_modules=17)
        manifest = PlatformManifest(platform_version="1.0.0", total_services=17, total_modules=17)

        generator = DefaultIntegrationAuditPackageGenerator()
        package = generator.create_audit_package(validation, compatibility, diagnostics, health, manifest)
        assert isinstance(package, IntegrationAuditPackage)
        assert package.quality is None
        assert package.compliance is None
        assert package.readiness is None

    async def test_service_still_works_with_old_patterns(self) -> None:
        """Original PlatformService still works unchanged."""
        from adip.platform.contracts.models import PlatformRequest
        from adip.platform.orchestration.coordinator import DefaultPlatformCoordinator
        from adip.platform.orchestration.exception_mapper import DefaultExceptionMapper
        from adip.platform.orchestration.health_aggregator import DefaultHealthAggregator
        from adip.platform.orchestration.manifest_builder import DefaultManifestBuilder
        from adip.platform.orchestration.metrics_collector import DefaultPlatformMetricsCollector
        from adip.platform.orchestration.trace_manager import DefaultTraceManager
        from adip.platform.services.service import DefaultPlatformService

        registry = DefaultServiceRegistry()
        for module in ModuleName:
            registry.register(f"{module.value}_service", object(), module)

        coordinator = DefaultPlatformCoordinator(
            registry=registry,
            health_aggregator=DefaultHealthAggregator(),
            trace_manager=DefaultTraceManager(),
            metrics_collector=DefaultPlatformMetricsCollector(),
            exception_mapper=DefaultExceptionMapper(),
            manifest_builder=DefaultManifestBuilder(),
        )
        from adip.platform.orchestration.manager import DefaultPlatformManager
        manager = DefaultPlatformManager(coordinator)
        service = DefaultPlatformService(manager)

        request = PlatformRequest(correlation_id="backward-compat-test")
        response = await service.execute_pipeline(request)
        assert response.success
