"""Phase 3.5 smoke tests — Platform Readiness Report."""

from __future__ import annotations

from adip.platform.contracts.models import PlatformHealth, PlatformValidationResult
from adip.platform.enums import ModuleHealthStatus, ModuleName
from adip.platform.orchestration.readiness import DefaultPlatformReadinessChecker
from adip.platform.orchestration.registry import DefaultServiceRegistry


class TestPlatformReadinessChecker:
    """Verify platform readiness report generation."""

    def setup(self) -> DefaultServiceRegistry:
        registry = DefaultServiceRegistry()
        for module in ModuleName:
            registry.register(f"{module.value}_service", object(), module)
        return registry

    def test_readiness_fully_ready(self) -> None:
        registry = self.setup()
        checker = DefaultPlatformReadinessChecker()
        validation = PlatformValidationResult(
            platform_valid=True, bootstrap_valid=True, contracts_valid=True,
            diagnostics_valid=True, health_status="healthy", message="OK",
        )
        health = PlatformHealth(
            overall_status=ModuleHealthStatus.HEALTHY,
            modules={}, healthy_count=17, total_modules=17,
        )
        report = checker.check_readiness(registry, validation, health)
        assert report.overall_ready is True
        assert report.bootstrap_status == "passed"
        assert report.health_status == "healthy"
        assert report.compatibility_status == "passed"

    def test_readiness_not_ready(self) -> None:
        registry = DefaultServiceRegistry()
        checker = DefaultPlatformReadinessChecker()
        validation = PlatformValidationResult(
            platform_valid=False, bootstrap_valid=False, contracts_valid=False,
            diagnostics_valid=False, health_status="degraded", message="Fail",
        )
        health = PlatformHealth(
            overall_status=ModuleHealthStatus.UNKNOWN,
            modules={}, healthy_count=0, total_modules=17,
        )
        report = checker.check_readiness(registry, validation, health)
        assert report.overall_ready is False

    def test_readiness_has_build_metadata(self) -> None:
        registry = self.setup()
        checker = DefaultPlatformReadinessChecker(platform_version="2.0.0", build_metadata={"env": "test"})
        validation = PlatformValidationResult(
            platform_valid=True, bootstrap_valid=True, contracts_valid=True,
            diagnostics_valid=True, health_status="healthy", message="OK",
        )
        health = PlatformHealth(
            overall_status=ModuleHealthStatus.HEALTHY,
            modules={}, healthy_count=17, total_modules=17,
        )
        report = checker.check_readiness(registry, validation, health)
        assert report.version == "2.0.0"
        assert report.build_metadata["env"] == "test"
