"""DefaultPlatformBootstrap — initialises and wires all platform modules.

Creates all sub-components (registry, health, trace, metrics, etc.),
registers adapter placeholders for every ADIP domain module,
and returns the fully-configured DefaultPlatformService.

Usage::

    bootstrap = DefaultPlatformBootstrap()
    service = await bootstrap.initialize()
    response = await service.execute_pipeline(PlatformRequest(...))
"""

from __future__ import annotations

import structlog

from adip.platform.enums import ModuleName
from adip.platform.interfaces import PlatformBootstrap, PlatformService, ServiceRegistry
from adip.platform.orchestration.coordinator import DefaultPlatformCoordinator
from adip.platform.orchestration.exception_mapper import DefaultExceptionMapper
from adip.platform.orchestration.health_aggregator import DefaultHealthAggregator
from adip.platform.orchestration.manager import DefaultPlatformManager
from adip.platform.orchestration.manifest_builder import DefaultManifestBuilder
from adip.platform.orchestration.metrics_collector import DefaultPlatformMetricsCollector
from adip.platform.orchestration.registry import DefaultServiceRegistry
from adip.platform.orchestration.shared_context import DefaultContextManager
from adip.platform.orchestration.trace_manager import DefaultTraceManager
from adip.platform.services.service import DefaultPlatformService

logger = structlog.get_logger(__name__)


class _PlaceholderService:
    """Minimal placeholder that wraps an adapter for the bootstrap wiring."""

    def __init__(self, domain: str) -> None:
        self._domain = domain
        logger.debug("placeholder_service.created", domain=domain)

    def handle_operation(self, operation: str, params: dict | None = None) -> dict:
        logger.info("placeholder.operation", domain=self._domain, operation=operation)
        return {
            "domain": self._domain,
            "operation": operation,
            "params": params or {},
            "status": "ok",
        }


# ── Module → service-name mappings ──────────────────────────────────
_MODULE_SERVICE_NAMES: dict[ModuleName, list[str]] = {
    ModuleName.PLANNER: ["planner_service", "planner_adapter"],
    ModuleName.WORKFLOW: ["workflow_service", "workflow_adapter"],
    ModuleName.MEMORY: ["memory_service", "memory_adapter"],
    ModuleName.KNOWLEDGE: ["knowledge_service", "knowledge_adapter"],
    ModuleName.RULES: ["rules_service", "rules_adapter"],
    ModuleName.PLUGINS: ["plugins_service", "plugins_adapter"],
    ModuleName.REGISTRY: ["registry_service", "registry_adapter"],
    ModuleName.EVIDENCE: ["evidence_service", "evidence_adapter"],
    ModuleName.REASONING: ["reasoning_service", "reasoning_adapter"],
    ModuleName.RECOMMENDATION: ["recommendation_service", "recommendation_adapter"],
    ModuleName.EXPLAINABILITY: ["explainability_service", "explainability_adapter"],
    ModuleName.DECISION_REVIEW: ["decision_review_service", "decision_review_adapter"],
    ModuleName.ACTION_MANAGER: ["action_manager_service", "action_manager_adapter"],
    ModuleName.ACTION_ENGINE: ["action_engine_service", "action_engine_adapter"],
    ModuleName.ENERGY: ["energy_service", "energy_adapter"],
    ModuleName.API: ["api_service", "api_adapter"],
    ModuleName.AUTH: ["auth_service", "auth_adapter"],
}


class DefaultPlatformBootstrap(PlatformBootstrap):
    """Bootstraps the entire ADIP platform.

    Creates every sub-component, registers placeholder services for
    all 17 modules, and returns the fully-wired DefaultPlatformService.
    """

    def __init__(self) -> None:
        self._service: PlatformService | None = None
        self._registry: ServiceRegistry | None = None
        logger.debug("platform_bootstrap.initialized")

    async def initialize(self) -> PlatformService:
        registry = DefaultServiceRegistry()
        trace = DefaultTraceManager()
        metrics = DefaultPlatformMetricsCollector()
        health = DefaultHealthAggregator()
        exceptions = DefaultExceptionMapper()
        manifest = DefaultManifestBuilder()
        context_mgr = DefaultContextManager()

        coordinator = DefaultPlatformCoordinator(
            registry=registry,
            health_aggregator=health,
            trace_manager=trace,
            metrics_collector=metrics,
            exception_mapper=exceptions,
            manifest_builder=manifest,
        )
        manager = DefaultPlatformManager(coordinator=coordinator)
        service = DefaultPlatformService(manager=manager)

        self._register_modules(registry)

        self._service = service
        self._registry = registry

        logger.info("platform_bootstrap.initialized_complete", modules=len(_MODULE_SERVICE_NAMES))
        return service

    async def get_service(self) -> PlatformService:
        if self._service is None:
            return await self.initialize()
        return self._service

    def get_registry(self) -> ServiceRegistry:
        return self._registry

    @staticmethod
    def _register_modules(registry: ServiceRegistry) -> None:
        """Register placeholder services for all 17 ADIP modules."""
        for module, service_names in _MODULE_SERVICE_NAMES.items():
            svc = _PlaceholderService(module.value)
            for name in service_names:
                registry.register(name=name, service=svc, module=module)

        logger.debug("platform_bootstrap.modules_registered", count=len(_MODULE_SERVICE_NAMES))
