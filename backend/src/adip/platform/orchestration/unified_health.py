"""DefaultUnifiedHealth — aggregates unified health across the platform."""

from __future__ import annotations

import structlog

from adip.platform.contracts.models import ModuleHealth, PlatformHealth
from adip.platform.enums import ModuleHealthStatus, ModuleName
from adip.platform.interfaces import ServiceRegistry, UnifiedHealth

logger = structlog.get_logger(__name__)


class DefaultUnifiedHealth(UnifiedHealth):
    """Aggregates unified health across all platform modules.

    Builds on the Phase 1 HealthAggregator but provides a separate
    interface for Phase 3 validation workflows.
    """

    def get_unified_health(self, registry: ServiceRegistry) -> PlatformHealth:
        descriptors = registry.get_service_descriptors()
        module_map: dict[str, ModuleHealth] = {}

        for desc in descriptors:
            mod = desc.module.value
            if mod not in module_map:
                module_map[mod] = ModuleHealth(
                    module=desc.module,
                    status=ModuleHealthStatus.HEALTHY,
                    is_registered=True,
                    version=desc.version,
                    message="Module is registered and healthy",
                )

        for module in ModuleName:
            if module.value not in module_map:
                module_map[module.value] = ModuleHealth(
                    module=module,
                    status=ModuleHealthStatus.UNKNOWN,
                    is_registered=False,
                    message="Module is not registered",
                )

        healthy = sum(1 for h in module_map.values() if h.status == ModuleHealthStatus.HEALTHY)
        unknown = sum(1 for h in module_map.values() if h.status == ModuleHealthStatus.UNKNOWN)
        total = len(module_map)

        if healthy == total:
            overall = ModuleHealthStatus.HEALTHY
        elif healthy > 0:
            overall = ModuleHealthStatus.DEGRADED
        else:
            overall = ModuleHealthStatus.UNKNOWN

        logger.debug("unified_health.aggregated", healthy=healthy, unknown=unknown, total=total, overall=overall.value)

        return PlatformHealth(
            overall_status=overall,
            modules=module_map,
            healthy_count=healthy,
            degraded_count=0,
            unhealthy_count=unknown,
            total_modules=total,
        )
