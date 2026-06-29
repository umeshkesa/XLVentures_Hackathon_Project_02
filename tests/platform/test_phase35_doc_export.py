"""Phase 3.5 smoke tests — Documentation Metadata and Platform Export."""

from __future__ import annotations

from adip.platform.contracts.models import (
    PlatformCompatibilityReport,
    PlatformManifest,
)
from adip.platform.enums import ModuleName
from adip.platform.orchestration.doc_metadata import (
    DefaultDocumentationMetadataGenerator,
)
from adip.platform.orchestration.export_package import (
    DefaultPlatformExportPackageBuilder,
)
from adip.platform.orchestration.registry import DefaultServiceRegistry


class TestDocumentationMetadata:
    """Verify documentation metadata generation."""

    def setup(self) -> DefaultServiceRegistry:
        registry = DefaultServiceRegistry()
        for module in ModuleName:
            registry.register(f"{module.value}_service", object(), module)
        return registry

    def test_generate_metadata(self) -> None:
        registry = self.setup()
        dmg = DefaultDocumentationMetadataGenerator()
        meta = dmg.generate_metadata(registry)
        assert len(meta.modules) == len(ModuleName)
        assert len(meta.services) == len(ModuleName)
        assert len(meta.domains) == len(ModuleName)
        assert meta.coverage_pct == 1.0

    def test_metadata_counts(self) -> None:
        registry = self.setup()
        dmg = DefaultDocumentationMetadataGenerator()
        meta = dmg.generate_metadata(registry)
        assert meta.total_items > 0
        assert meta.total_documented > 0
        assert meta.total_documented == meta.total_items


class TestPlatformExportPackage:
    """Verify platform export package building."""

    def setup(self) -> DefaultServiceRegistry:
        registry = DefaultServiceRegistry()
        for module in ModuleName:
            registry.register(f"{module.value}_service", object(), module)
        return registry

    def test_build_export_package(self) -> None:
        registry = self.setup()
        builder = DefaultPlatformExportPackageBuilder()
        manifest = PlatformManifest(platform_version="1.0.0", total_services=17, total_modules=17)
        compatibility = PlatformCompatibilityReport(platform="OK", pairs_validated=12, pairs_ok=12)
        pkg = builder.build_export_package(registry, manifest, compatibility)
        assert pkg.manifest.total_modules == 17
        assert pkg.compatibility_report.platform == "OK"
        assert len(pkg.module_inventory) == len(ModuleName)
        assert pkg.architecture_report["total_modules"] == 17
