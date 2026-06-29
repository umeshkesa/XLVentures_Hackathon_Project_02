"""Phase 3.5 smoke tests — Platform Quality Manager."""

from __future__ import annotations

from adip.platform.enums import ModuleName
from adip.platform.orchestration.quality_manager import DefaultPlatformQualityManager
from adip.platform.orchestration.registry import DefaultServiceRegistry


class TestPlatformQualityManager:
    """Verify platform quality evaluation."""

    def setup(self) -> DefaultServiceRegistry:
        registry = DefaultServiceRegistry()
        for module in ModuleName:
            registry.register(f"{module.value}_service", object(), module)
        return registry

    def test_quality_full_registry(self) -> None:
        registry = self.setup()
        qm = DefaultPlatformQualityManager()
        result = qm.evaluate_quality(registry)
        assert result.overall_score > 0
        assert result.architecture_completeness > 0
        assert result.integration_completeness > 0
        assert result.documentation_completeness > 0
        assert result.test_coverage > 0

    def test_quality_empty_registry(self) -> None:
        registry = DefaultServiceRegistry()
        qm = DefaultPlatformQualityManager()
        result = qm.evaluate_quality(registry)
        assert result.overall_score >= 0
        assert result.architecture_completeness == 0
        assert result.integration_completeness == 0
