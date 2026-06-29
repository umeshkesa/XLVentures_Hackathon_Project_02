"""Phase 3 smoke tests — compatibility report generator."""

from __future__ import annotations

from adip.platform.enums import ModuleName
from adip.platform.orchestration.compatibility_report import (
    DefaultPlatformCompatibilityReportGenerator,
)
from adip.platform.orchestration.registry import DefaultServiceRegistry


class TestCompatibilityReportGenerator:
    """Verify compatibility report generation."""

    def setup(self) -> DefaultServiceRegistry:
        registry = DefaultServiceRegistry()
        for module in ModuleName:
            registry.register(f"{module.value}_service", object(), module)
        return registry

    def test_generate_report_full(self) -> None:
        registry = self.setup()
        generator = DefaultPlatformCompatibilityReportGenerator()
        report = generator.generate_report(registry)
        assert report.platform == "OK"
        assert report.rest_api == "OK"
        assert report.energy_domain == "OK"
        assert report.pairs_validated == 12
        assert report.pairs_ok == 12

    def test_generate_report_partial(self) -> None:
        registry = DefaultServiceRegistry()
        registry.register("planner_service", object(), ModuleName.PLANNER)
        generator = DefaultPlatformCompatibilityReportGenerator()
        report = generator.generate_report(registry)
        assert report.platform == "ERROR"
        assert report.pairs_ok < 12

    def test_generate_report_empty(self) -> None:
        registry = DefaultServiceRegistry()
        generator = DefaultPlatformCompatibilityReportGenerator()
        report = generator.generate_report(registry)
        assert report.platform == "ERROR"
        assert report.pairs_ok == 0
        assert len(report.messages) == 12

    def test_generate_report_messages_format(self) -> None:
        registry = self.setup()
        generator = DefaultPlatformCompatibilityReportGenerator()
        report = generator.generate_report(registry)
        for msg in report.messages:
            assert msg.startswith("OK:") or msg.startswith("ERROR:")
