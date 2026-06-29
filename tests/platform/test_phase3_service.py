"""Phase 3 smoke tests — PlatformIntegrationService (ONLY public API)."""

from __future__ import annotations

from adip.platform.enums import ModuleHealthStatus, ModuleName
from adip.platform.orchestration.integration_service import (
    DefaultPlatformIntegrationService,
)
from adip.platform.orchestration.registry import DefaultServiceRegistry


class _StubManager:
    """Stub manager that returns deterministic results."""

    async def validate_platform(self):
        from adip.platform.contracts.models import PlatformValidationResult
        return PlatformValidationResult(platform_valid=True, bootstrap_valid=True, contracts_valid=True, diagnostics_valid=True, health_status="healthy", message="OK")

    async def get_compatibility_report(self):
        from adip.platform.contracts.models import PlatformCompatibilityReport
        return PlatformCompatibilityReport(platform="OK", rest_api="OK", energy_domain="OK", pairs_validated=12, pairs_ok=12)

    async def run_diagnostics(self):
        from adip.platform.contracts.models import PlatformDiagnosticsResult
        return PlatformDiagnosticsResult(all_valid=True, service_count=17, module_count=17)

    async def get_unified_health(self):
        from adip.platform.contracts.models import PlatformHealth
        return PlatformHealth(overall_status=ModuleHealthStatus.HEALTHY, modules={}, healthy_count=17, total_modules=17)

    async def get_platform_manifest(self):
        from adip.platform.contracts.models import PlatformManifest
        return PlatformManifest(platform_version="1.0.0", services=[], modules=[], total_services=17, total_modules=17)

    async def create_audit_package(self):
        from adip.platform.contracts.models import (
            IntegrationAuditPackage,
            PlatformCompatibilityReport,
            PlatformDiagnosticsResult,
            PlatformHealth,
            PlatformManifest,
            PlatformValidationResult,
        )
        return IntegrationAuditPackage(
            audit_id="test-audit-001",
            validation=PlatformValidationResult(platform_valid=True, bootstrap_valid=True, contracts_valid=True, diagnostics_valid=True, health_status="healthy", message="OK"),
            compatibility=PlatformCompatibilityReport(platform="OK", rest_api="OK", energy_domain="OK", pairs_validated=12, pairs_ok=12),
            diagnostics=PlatformDiagnosticsResult(all_valid=True, service_count=17, module_count=17),
            health=PlatformHealth(overall_status=ModuleHealthStatus.HEALTHY, modules={}, healthy_count=17, total_modules=17),
            manifest=PlatformManifest(platform_version="1.0.0", total_services=17, total_modules=17),
            checksum="abc123",
        )


class TestPlatformIntegrationService:
    """Verify the ONLY public API for platform validation."""

    async def test_validate_platform(self) -> None:
        service = DefaultPlatformIntegrationService(_StubManager())
        result = await service.validate_platform()
        assert result.platform_valid is True
        assert result.health_status == "healthy"

    async def test_get_compatibility_report(self) -> None:
        service = DefaultPlatformIntegrationService(_StubManager())
        report = await service.get_compatibility_report()
        assert report.platform == "OK"
        assert report.rest_api == "OK"

    async def test_run_diagnostics(self) -> None:
        service = DefaultPlatformIntegrationService(_StubManager())
        result = await service.run_diagnostics()
        assert result.all_valid is True
        assert result.service_count == 17

    async def test_get_unified_health(self) -> None:
        service = DefaultPlatformIntegrationService(_StubManager())
        health = await service.get_unified_health()
        assert health.overall_status == ModuleHealthStatus.HEALTHY
        assert health.healthy_count == 17

    async def test_get_platform_manifest(self) -> None:
        service = DefaultPlatformIntegrationService(_StubManager())
        manifest = await service.get_platform_manifest()
        assert manifest.platform_version == "1.0.0"
        assert manifest.total_services == 17

    async def test_create_audit_package(self) -> None:
        service = DefaultPlatformIntegrationService(_StubManager())
        package = await service.create_audit_package()
        assert package.audit_id == "test-audit-001"
        assert package.checksum == "abc123"

    async def test_with_auth_callback(self) -> None:
        called = []

        def auth_cb(cid: str) -> None:
            called.append(cid)

        service = DefaultPlatformIntegrationService(_StubManager(), auth_callback=auth_cb)
        await service.validate_platform()
        assert len(called) > 0

    async def test_with_audit_callback(self) -> None:
        events = []

        def audit_cb(op: str, details: dict) -> None:
            events.append((op, details))

        service = DefaultPlatformIntegrationService(_StubManager(), audit_callback=audit_cb)
        await service.validate_platform()
        await service.get_compatibility_report()
        assert len(events) == 2
        assert events[0][0] == "validate_platform"

    async def test_coordinator_integration(self) -> None:
        """End-to-end through coordinator with real registry."""
        registry = DefaultServiceRegistry()
        for module in ModuleName:
            registry.register(f"{module.value}_service", object(), module)

        from adip.platform.orchestration.audit_package import (
            DefaultIntegrationAuditPackageGenerator,
        )
        from adip.platform.orchestration.bootstrap_validator import DefaultBootstrapValidator
        from adip.platform.orchestration.compatibility_report import (
            DefaultPlatformCompatibilityReportGenerator,
        )
        from adip.platform.orchestration.compliance_manager import DefaultPlatformComplianceManager
        from adip.platform.orchestration.contract_validator import (
            DefaultCrossModuleContractValidator,
        )
        from adip.platform.orchestration.diagnostics import DefaultPlatformDiagnostics
        from adip.platform.orchestration.doc_metadata import DefaultDocumentationMetadataGenerator
        from adip.platform.orchestration.export_package import DefaultPlatformExportPackageBuilder
        from adip.platform.orchestration.integration_coordinator import (
            DefaultPlatformIntegrationCoordinator,
        )
        from adip.platform.orchestration.integration_manager import (
            DefaultPlatformIntegrationManager,
        )
        from adip.platform.orchestration.manifest import DefaultPlatformManifestGenerator
        from adip.platform.orchestration.pipeline_version import (
            DefaultPlatformPipelineVersionManager,
        )
        from adip.platform.orchestration.quality_manager import DefaultPlatformQualityManager
        from adip.platform.orchestration.readiness import DefaultPlatformReadinessChecker
        from adip.platform.orchestration.release_checklist import (
            DefaultPlatformReleaseChecklistRunner,
        )
        from adip.platform.orchestration.snapshot import DefaultPlatformSnapshotManager
        from adip.platform.orchestration.unified_health import DefaultUnifiedHealth
        from adip.platform.orchestration.version_manager import DefaultPlatformVersionManager

        coordinator = DefaultPlatformIntegrationCoordinator(
            registry=registry,
            bootstrap_validator=DefaultBootstrapValidator(),
            contract_validator=DefaultCrossModuleContractValidator(),
            diagnostics=DefaultPlatformDiagnostics(),
            compatibility_report=DefaultPlatformCompatibilityReportGenerator(),
            unified_health=DefaultUnifiedHealth(),
            manifest_generator=DefaultPlatformManifestGenerator(),
            audit_package_generator=DefaultIntegrationAuditPackageGenerator(),
            version_manager=DefaultPlatformVersionManager(),
            readiness_checker=DefaultPlatformReadinessChecker(),
            quality_manager=DefaultPlatformQualityManager(),
            compliance_manager=DefaultPlatformComplianceManager(),
            snapshot_manager=DefaultPlatformSnapshotManager(),
            pipeline_version_manager=DefaultPlatformPipelineVersionManager(),
            doc_metadata_generator=DefaultDocumentationMetadataGenerator(),
            export_package_builder=DefaultPlatformExportPackageBuilder(),
            release_checklist_runner=DefaultPlatformReleaseChecklistRunner(),
        )
        manager = DefaultPlatformIntegrationManager(coordinator)
        service = DefaultPlatformIntegrationService(manager)

        # Exercise all public API methods
        v = await service.validate_platform()
        assert v.platform_valid is True

        c = await service.get_compatibility_report()
        assert c.platform == "OK"

        d = await service.run_diagnostics()
        assert d.all_valid is True

        h = await service.get_unified_health()
        assert h.overall_status == ModuleHealthStatus.HEALTHY

        m = await service.get_platform_manifest()
        assert m.total_modules == len(ModuleName)

        p = await service.create_audit_package()
        assert len(p.audit_id) > 0
        assert len(p.checksum) > 0

        q = await service.get_platform_quality()
        assert q.overall_score > 0

        comp = await service.check_platform_compliance()
        assert comp.overall_compliant is True

        r = await service.get_platform_readiness()
        assert r.overall_ready is True

        snap = await service.get_platform_snapshot()
        assert len(snap.snapshot_id) > 0

        vhist = await service.get_pipeline_version_history()
        assert len(vhist) >= 0

        pv = await service.create_pipeline_version("1.0.0")
        assert pv.is_active is True

        doc = await service.get_documentation_metadata()
        assert doc.coverage_pct > 0

        ex = await service.export_platform_package()
        assert ex.manifest.total_modules == len(ModuleName)

        rl = await service.run_release_checklist()
        assert rl.platform_ready is True
