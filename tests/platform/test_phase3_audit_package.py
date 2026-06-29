"""Phase 3 smoke tests — audit package and version manager."""

from __future__ import annotations

from adip.platform.contracts.models import (
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
from adip.platform.orchestration.version_manager import DefaultPlatformVersionManager


class TestAuditPackageGenerator:
    """Verify audit package creation."""

    def setup(self) -> tuple:
        validation = PlatformValidationResult(
            platform_valid=True,
            bootstrap_valid=True,
            contracts_valid=True,
            diagnostics_valid=True,
            health_status="healthy",
            message="All good",
        )
        compatibility = PlatformCompatibilityReport(
            platform="OK",
            rest_api="OK",
            energy_domain="OK",
            pairs_validated=12,
            pairs_ok=12,
            messages=["OK: planner → workflow"],
        )
        diagnostics = PlatformDiagnosticsResult(
            all_valid=True,
            service_count=17,
            module_count=17,
        )
        health = PlatformHealth(
            overall_status=ModuleHealthStatus.HEALTHY,
            modules={},
            healthy_count=17,
            total_modules=17,
        )
        manifest = PlatformManifest(
            platform_version="1.0.0",
            modules=[],
            services=[],
            total_services=17,
            total_modules=17,
        )
        return validation, compatibility, diagnostics, health, manifest

    def test_create_audit_package(self) -> None:
        validation, compatibility, diagnostics, health, manifest = self.setup()
        generator = DefaultIntegrationAuditPackageGenerator()
        package = generator.create_audit_package(validation, compatibility, diagnostics, health, manifest)
        assert package.audit_id is not None
        assert len(package.audit_id) > 0
        assert package.validation.platform_valid is True
        assert package.compatibility.platform == "OK"
        assert package.diagnostics.all_valid is True
        assert package.health.healthy_count == 17
        assert package.manifest.total_services == 17

    def test_audit_package_has_checksum(self) -> None:
        validation, compatibility, diagnostics, health, manifest = self.setup()
        generator = DefaultIntegrationAuditPackageGenerator()
        package = generator.create_audit_package(validation, compatibility, diagnostics, health, manifest)
        assert len(package.checksum) > 0
        assert isinstance(package.checksum, str)

    def test_audit_package_version(self) -> None:
        validation, compatibility, diagnostics, health, manifest = self.setup()
        generator = DefaultIntegrationAuditPackageGenerator(version="2.0.0")
        package = generator.create_audit_package(validation, compatibility, diagnostics, health, manifest)
        assert package.version == "2.0.0"

    def test_audit_package_immutable_content(self) -> None:
        validation, compatibility, diagnostics, health, manifest = self.setup()
        generator = DefaultIntegrationAuditPackageGenerator()
        package = generator.create_audit_package(validation, compatibility, diagnostics, health, manifest)
        original = package.checksum
        package.checksum = "tampered"
        assert package.checksum == "tampered"


class TestVersionManager:
    """Verify platform version tracking."""

    def test_get_version_default(self) -> None:
        vm = DefaultPlatformVersionManager()
        record = vm.get_version("planner")
        assert record.module == "planner"
        assert record.version == "1.0.0"
        assert record.status == "active"

    def test_get_version_unknown_module(self) -> None:
        vm = DefaultPlatformVersionManager()
        record = vm.get_version("nonexistent")
        assert record.module == "nonexistent"
        assert record.version == "0.0.0"
        assert record.status == "unknown"

    def test_list_versions_all_modules(self) -> None:
        vm = DefaultPlatformVersionManager()
        versions = vm.list_versions()
        assert len(versions) == len(ModuleName)

    def test_update_version(self) -> None:
        vm = DefaultPlatformVersionManager()
        record = vm.update_version("planner", "2.0.0")
        assert record.version == "2.0.0"
        assert record.status == "active"
        fetched = vm.get_version("planner")
        assert fetched.version == "2.0.0"

    def test_list_versions_after_update(self) -> None:
        vm = DefaultPlatformVersionManager()
        vm.update_version("energy", "3.0.0")
        versions = {v.module: v.version for v in vm.list_versions()}
        assert versions["energy"] == "3.0.0"
