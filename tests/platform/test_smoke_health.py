"""Smoke tests for platform health aggregation."""

from __future__ import annotations

from adip.platform.enums import ModuleHealthStatus, ModuleName
from adip.platform.orchestration.health_aggregator import DefaultHealthAggregator
from adip.platform.orchestration.registry import DefaultServiceRegistry


class TestHealthAggregation:
    """Verify health aggregation across all modules."""

    def test_all_modules_unknown_when_empty(self) -> None:
        """Verify all modules report unknown when registry is empty."""
        registry = DefaultServiceRegistry()
        aggregator = DefaultHealthAggregator()
        health = aggregator.aggregate(registry)
        assert len(health.modules) == len(ModuleName)
        assert all(h.status == ModuleHealthStatus.UNKNOWN for h in health.modules.values())
        assert health.healthy_count == 0
        assert health.total_modules == len(ModuleName)

    def test_healthy_when_registered(self) -> None:
        """Verify registered modules report healthy."""
        registry = DefaultServiceRegistry()
        registry.register("planner_service", object(), ModuleName.PLANNER)
        registry.register("energy_service", object(), ModuleName.ENERGY)

        aggregator = DefaultHealthAggregator()
        health = aggregator.aggregate(registry)

        assert health.modules["planner"].is_registered
        assert health.modules["planner"].status == ModuleHealthStatus.HEALTHY
        assert health.modules["energy"].is_registered
        assert health.modules["energy"].status == ModuleHealthStatus.HEALTHY
        # Unregistered modules should still be unknown
        unknown_modules = [k for k, v in health.modules.items() if v.status == ModuleHealthStatus.UNKNOWN]
        assert len(unknown_modules) == len(ModuleName) - 2

    def test_overall_healthy_when_all_registered(self) -> None:
        """Verify overall health is healthy when all modules registered."""
        registry = DefaultServiceRegistry()
        for module in ModuleName:
            registry.register(f"{module.value}_service", object(), module)
        aggregator = DefaultHealthAggregator()
        health = aggregator.aggregate(registry)
        assert health.overall_status == ModuleHealthStatus.HEALTHY
        assert health.healthy_count == len(ModuleName)

    def test_overall_unknown_when_none_registered(self) -> None:
        """Verify overall health is unknown when no modules registered."""
        registry = DefaultServiceRegistry()
        aggregator = DefaultHealthAggregator()
        health = aggregator.aggregate(registry)
        assert health.overall_status == ModuleHealthStatus.DEGRADED
        assert health.healthy_count == 0
