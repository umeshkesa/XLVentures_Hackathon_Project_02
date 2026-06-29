"""Smoke tests for platform manifest generation."""

from __future__ import annotations

from adip.platform.enums import ModuleName
from adip.platform.orchestration.manifest_builder import DefaultManifestBuilder
from adip.platform.orchestration.registry import DefaultServiceRegistry


class TestManifestGeneration:
    """Verify platform manifest generation."""

    def test_empty_manifest(self) -> None:
        """Verify manifest with no services is valid."""
        registry = DefaultServiceRegistry()
        builder = DefaultManifestBuilder()
        manifest = builder.build(registry)
        assert manifest.platform_version == "1.0.0"
        assert manifest.total_services == 0
        assert manifest.total_modules == 0
        assert manifest.services == []
        assert manifest.modules == []

    def test_manifest_with_services(self) -> None:
        """Verify manifest includes all registered services."""
        registry = DefaultServiceRegistry()
        registry.register("planner_service", object(), ModuleName.PLANNER)
        registry.register("energy_service", object(), ModuleName.ENERGY)
        builder = DefaultManifestBuilder()
        manifest = builder.build(registry)
        assert manifest.total_services == 2
        assert manifest.total_modules == 2

    def test_manifest_includes_metadata(self) -> None:
        """Verify manifest includes generator metadata."""
        registry = DefaultServiceRegistry()
        builder = DefaultManifestBuilder()
        manifest = builder.build(registry)
        assert "generator" in manifest.metadata
        assert "framework" in manifest.metadata

    def test_manifest_services_have_descriptors(self) -> None:
        """Verify each service has a full descriptor."""
        registry = DefaultServiceRegistry()
        registry.register("test_svc", 42, ModuleName.API, dependencies=["dep1"])
        builder = DefaultManifestBuilder()
        manifest = builder.build(registry)
        assert len(manifest.services) == 1
        svc = manifest.services[0]
        assert svc.name == "test_svc"
        assert svc.module == ModuleName.API
        assert svc.service_type == "int"
        assert svc.dependencies == ["dep1"]
