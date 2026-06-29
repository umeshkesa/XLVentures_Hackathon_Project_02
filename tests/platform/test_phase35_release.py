"""Phase 3.5 smoke tests — Release Checklist and Diagnostics Enhancement."""

from __future__ import annotations

from adip.platform.contracts.models import PlatformHealth
from adip.platform.enums import ModuleHealthStatus, ModuleName
from adip.platform.orchestration.diagnostics import DefaultPlatformDiagnostics
from adip.platform.orchestration.registry import DefaultServiceRegistry
from adip.platform.orchestration.release_checklist import (
    DefaultPlatformReleaseChecklistRunner,
)


class TestReleaseChecklist:
    """Verify release checklist execution."""

    def setup(self) -> DefaultServiceRegistry:
        registry = DefaultServiceRegistry()
        for module in ModuleName:
            registry.register(f"{module.value}_service", object(), module)
        return registry

    def test_checklist_passes_full(self) -> None:
        registry = self.setup()
        runner = DefaultPlatformReleaseChecklistRunner()
        diagnostics = DefaultPlatformDiagnostics().run_diagnostics(registry)
        health = PlatformHealth(
            overall_status=ModuleHealthStatus.HEALTHY,
            modules={}, healthy_count=17, total_modules=17,
        )
        result = runner.run_checklist(registry, diagnostics, health)
        assert result.platform_ready is True
        assert result.services_registered is True
        assert result.imports_valid is True
        assert result.tests_passing is True
        assert result.routers_registered is True
        assert result.no_circular_dependencies is True

    def test_checklist_fails_empty(self) -> None:
        registry = DefaultServiceRegistry()
        runner = DefaultPlatformReleaseChecklistRunner()
        diagnostics = DefaultPlatformDiagnostics().run_diagnostics(registry)
        health = PlatformHealth(
            overall_status=ModuleHealthStatus.UNKNOWN,
            modules={}, healthy_count=0, total_modules=17,
        )
        result = runner.run_checklist(registry, diagnostics, health)
        assert result.platform_ready is False
        assert result.services_registered is False


class TestDiagnosticsEnhancement:
    """Verify Phase 3.5 diagnostics enhancements."""

    def test_diagnostics_includes_new_fields(self) -> None:
        registry = DefaultServiceRegistry()
        diag = DefaultPlatformDiagnostics()
        result = diag.run_diagnostics(registry)
        assert hasattr(result, "missing_exports")
        assert hasattr(result, "invalid_imports")
        assert hasattr(result, "contract_violations")

    def test_diagnostics_full_passes_new_fields(self) -> None:
        registry = DefaultServiceRegistry()
        for module in ModuleName:
            registry.register(f"{module.value}_service", object(), module)
        diag = DefaultPlatformDiagnostics()
        result = diag.run_diagnostics(registry)
        assert result.all_valid is True
        assert len(result.missing_exports) == 0
        assert len(result.invalid_imports) == 0
        assert len(result.contract_violations) == 0
