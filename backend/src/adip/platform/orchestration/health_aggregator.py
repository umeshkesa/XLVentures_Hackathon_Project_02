"""DefaultHealthAggregator — aggregates health across all platform modules."""

from __future__ import annotations

import structlog

from adip.platform.contracts.models import ModuleHealth, PlatformHealth
from adip.platform.enums import ModuleHealthStatus, ModuleName
from adip.platform.interfaces import HealthAggregator, ServiceRegistry

logger = structlog.get_logger(__name__)


class DefaultHealthAggregator(HealthAggregator):
    """Default health aggregator.

    Iterates all registered services in the registry and produces
    a PlatformHealth snapshot. All module health is determined by
    service registration status (deterministic placeholder — no
    real health checks).
    """

    def aggregate(self, registry: ServiceRegistry) -> PlatformHealth:
        """Aggregate health from all registered services."""
        descriptors = registry.get_service_descriptors()
        modules_map: dict[str, ModuleHealth] = {}
        module_names_set: set[str] = set()

        for desc in descriptors:
            module_name = desc.module.value
            module_names_set.add(module_name)

            if module_name not in modules_map:
                modules_map[module_name] = ModuleHealth(
                    module=desc.module,
                    status=ModuleHealthStatus.HEALTHY,
                    is_registered=True,
                    version=desc.version,
                    message="Module is registered and healthy",
                )

        # Add entries for modules that are not registered
        for module in ModuleName:
            if module.value not in modules_map:
                modules_map[module.value] = ModuleHealth(
                    module=module,
                    status=ModuleHealthStatus.UNKNOWN,
                    is_registered=False,
                    message="Module is not registered",
                )

        healthy = sum(1 for h in modules_map.values() if h.status == ModuleHealthStatus.HEALTHY)
        degraded = sum(1 for h in modules_map.values() if h.status == ModuleHealthStatus.DEGRADED)
        unhealthy = sum(1 for h in modules_map.values() if h.status == ModuleHealthStatus.UNHEALTHY)
        total = len(modules_map)

        if unhealthy > 0:
            overall = ModuleHealthStatus.UNHEALTHY
        elif degraded > 0:
            overall = ModuleHealthStatus.DEGRADED
        elif healthy == total:
            overall = ModuleHealthStatus.HEALTHY
        else:
            overall = ModuleHealthStatus.DEGRADED

        logger.debug(
            "health_aggregator.aggregated",
            healthy=healthy,
            degraded=degraded,
            unhealthy=unhealthy,
            total=total,
            overall=overall.value,
        )

        return PlatformHealth(
            overall_status=overall,
            modules=modules_map,
            healthy_count=healthy,
            degraded_count=degraded,
            unhealthy_count=unhealthy,
            total_modules=total,
        )
