"""Phase 3 smoke tests — unified platform health."""

from __future__ import annotations

from adip.platform.enums import ModuleHealthStatus, ModuleName
from adip.platform.orchestration.registry import DefaultServiceRegistry
from adip.platform.orchestration.unified_health import DefaultUnifiedHealth


class TestUnifiedHealth:
    """Verify unified health aggregation."""

    def test_full_registry_healthy(self) -> None:
        registry = DefaultServiceRegistry()
        for module in ModuleName:
            registry.register(f"{module.value}_service", object(), module)
        health = DefaultUnifiedHealth()
        result = health.get_unified_health(registry)
        assert result.overall_status == ModuleHealthStatus.HEALTHY
        assert result.healthy_count == len(ModuleName)
        assert result.total_modules == len(ModuleName)

    def test_empty_registry_unknown(self) -> None:
        registry = DefaultServiceRegistry()
        health = DefaultUnifiedHealth()
        result = health.get_unified_health(registry)
        assert result.overall_status == ModuleHealthStatus.UNKNOWN
        assert result.healthy_count == 0

    def test_partial_registry_degraded(self) -> None:
        registry = DefaultServiceRegistry()
        registry.register("planner_service", object(), ModuleName.PLANNER)
        health = DefaultUnifiedHealth()
        result = health.get_unified_health(registry)
        assert result.overall_status == ModuleHealthStatus.DEGRADED
        assert result.healthy_count == 1

    def test_per_module_health_present(self) -> None:
        registry = DefaultServiceRegistry()
        registry.register("planner_service", object(), ModuleName.PLANNER)
        health = DefaultUnifiedHealth()
        result = health.get_unified_health(registry)
        assert "planner" in result.modules
        assert "energy" in result.modules
        assert result.modules["planner"].is_registered is True
        assert result.modules["energy"].is_registered is False
