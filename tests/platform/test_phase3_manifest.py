"""Phase 3 smoke tests — platform manifest generator."""

from __future__ import annotations

from adip.platform.enums import ModuleName
from adip.platform.orchestration.manifest import DefaultPlatformManifestGenerator
from adip.platform.orchestration.registry import DefaultServiceRegistry


class TestPlatformManifestGenerator:
    """Verify platform manifest generation."""

    def setup(self) -> DefaultServiceRegistry:
        registry = DefaultServiceRegistry()
        for module in ModuleName:
            registry.register(f"{module.value}_service", object(), module)
        return registry

    def test_generate_manifest_full(self) -> None:
        registry = self.setup()
        generator = DefaultPlatformManifestGenerator()
        manifest = generator.generate_manifest(registry)
        assert manifest.total_services == len(ModuleName)
        assert manifest.total_modules == len(ModuleName)
        assert manifest.platform_version == "1.0.0"

    def test_generate_manifest_custom_version(self) -> None:
        registry = self.setup()
        generator = DefaultPlatformManifestGenerator(platform_version="2.0.0")
        manifest = generator.generate_manifest(registry)
        assert manifest.platform_version == "2.0.0"

    def test_generate_manifest_empty(self) -> None:
        registry = DefaultServiceRegistry()
        generator = DefaultPlatformManifestGenerator()
        manifest = generator.generate_manifest(registry)
        assert manifest.total_services == 0
        assert manifest.total_modules == 0

    def test_generate_manifest_metadata(self) -> None:
        registry = self.setup()
        generator = DefaultPlatformManifestGenerator()
        manifest = generator.generate_manifest(registry)
        assert "generator" in manifest.metadata
        assert manifest.metadata["generator"] == "DefaultPlatformManifestGenerator"
