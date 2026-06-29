"""Phase 3 smoke tests — platform diagnostics."""

from __future__ import annotations

from adip.platform.enums import ModuleName
from adip.platform.orchestration.diagnostics import DefaultPlatformDiagnostics
from adip.platform.orchestration.registry import DefaultServiceRegistry


class TestPlatformDiagnostics:
    """Verify platform diagnostics detects issues."""

    def setup(self) -> DefaultServiceRegistry:
        registry = DefaultServiceRegistry()
        for module in ModuleName:
            registry.register(f"{module.value}_service", object(), module)
        return registry

    def test_diagnostics_full_passes(self) -> None:
        registry = self.setup()
        diag = DefaultPlatformDiagnostics()
        result = diag.run_diagnostics(registry)
        assert result.all_valid is True
        assert result.service_count == len(ModuleName)
        assert result.module_count == len(ModuleName)

    def test_diagnostics_empty_registry(self) -> None:
        registry = DefaultServiceRegistry()
        diag = DefaultPlatformDiagnostics()
        result = diag.run_diagnostics(registry)
        assert result.all_valid is False
        assert len(result.missing_services) > 0

    def test_diagnostics_missing_services(self) -> None:
        registry = DefaultServiceRegistry()
        registry.register("planner_service", object(), ModuleName.PLANNER)
        diag = DefaultPlatformDiagnostics()
        result = diag.run_diagnostics(registry)
        assert len(result.missing_services) == len(ModuleName) - 1

    def test_diagnostics_partial_finds_warnings(self) -> None:
        registry = DefaultServiceRegistry()
        registry.register("planner_service", object(), ModuleName.PLANNER)
        diag = DefaultPlatformDiagnostics()
        result = diag.run_diagnostics(registry)
        assert len(result.warnings) > 0
