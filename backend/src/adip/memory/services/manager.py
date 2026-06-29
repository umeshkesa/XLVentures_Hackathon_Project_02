"""DefaultMemoryManager — lightweight orchestrator for memory operations.

Delegates all coordination to MemoryCoordinator.  Remains the
central API that ADIP modules call for memory operations.
"""

from __future__ import annotations

from typing import Any

import structlog

from adip.memory.contracts.models import (
    MemoryContext,
    MemoryMetrics,
    MemoryPolicy,
    MemoryRecord,
)
from adip.memory.enums import MemoryOperation, MemoryTier, MemoryType
from adip.memory.execution.adapters import PlaceholderStorageAdapter
from adip.memory.execution.audit_manager import AuditManager
from adip.memory.execution.cache_manager import CacheManager
from adip.memory.execution.lifecycle import MemoryLifecycleManager
from adip.memory.execution.metrics import MetricsCollector
from adip.memory.execution.policy_engine import MemoryPolicyEngine
from adip.memory.execution.router import MemoryRouter
from adip.memory.execution.search import MemorySearchService
from adip.memory.execution.trace import TraceManager
from adip.memory.execution.validator import MemoryValidator
from adip.memory.execution.version_manager import VersionManager
from adip.memory.interfaces import MemoryManager
from adip.memory.orchestration.coordinator import MemoryCoordinator
from adip.memory.orchestration.hooks import IntegrationHooks
from adip.memory.orchestration.metrics_aggregator import MetricsAggregator
from adip.memory.orchestration.pipeline import MemoryOperationPipeline
from adip.memory.orchestration.tracing import AggregatedTracing

log = structlog.get_logger(__name__)


class DefaultMemoryManager(MemoryManager):
    """Lightweight orchestrator for all memory operations.

    Delegates all coordination to MemoryCoordinator.  Wires together:
    - MemoryCoordinator (orchestration)
    - Validation, Lifecycle, Policy, Routing, Adapting, Versioning,
      Auditing, Metrics, Tracing, Caching, Search (Phase 2)
    - MetricsAggregator, AggregatedTracing, IntegrationHooks, Pipeline (Phase 3)
    """

    def __init__(
        self,
        router: MemoryRouter | None = None,
        lifecycle: MemoryLifecycleManager | None = None,
        policy_engine: MemoryPolicyEngine | None = None,
        validator: MemoryValidator | None = None,
        audit: AuditManager | None = None,
        version_manager: VersionManager | None = None,
        metrics: MetricsCollector | None = None,
        trace: TraceManager | None = None,
        search_service: MemorySearchService | None = None,
        cache_manager: CacheManager | None = None,
        adapters: dict[str, PlaceholderStorageAdapter] | None = None,
        coordinator: MemoryCoordinator | None = None,
        metrics_aggregator: MetricsAggregator | None = None,
        aggregated_tracing: AggregatedTracing | None = None,
        hooks: IntegrationHooks | None = None,
        pipeline: MemoryOperationPipeline | None = None,
        default_policy: MemoryPolicy | None = None,
    ) -> None:
        self._router = router or MemoryRouter()
        self._lifecycle = lifecycle or MemoryLifecycleManager()
        self._policy = policy_engine or MemoryPolicyEngine()
        self._validator = validator or MemoryValidator()
        self._audit = audit or AuditManager()
        self._versions = version_manager or VersionManager()
        self._metrics = metrics or MetricsCollector()
        self._trace = trace or TraceManager()
        self._search = search_service or MemorySearchService()
        self._cache = cache_manager or CacheManager()
        self._default_policy = default_policy or MemoryPolicy()
        self._adapters = adapters or {
            "HOT": PlaceholderStorageAdapter(MemoryTier.HOT),
            "WARM": PlaceholderStorageAdapter(MemoryTier.WARM),
            "COLD": PlaceholderStorageAdapter(MemoryTier.COLD),
        }
        self._metrics_aggregator = metrics_aggregator or MetricsAggregator()
        self._aggregated_tracing = aggregated_tracing or AggregatedTracing()
        self._hooks = hooks or IntegrationHooks()
        self._pipeline = pipeline or MemoryOperationPipeline()
        self._coordinator = coordinator or MemoryCoordinator(
            router=self._router,
            lifecycle=self._lifecycle,
            policy_engine=self._policy,
            validator=self._validator,
            audit=self._audit,
            version_manager=self._versions,
            metrics=self._metrics,
            trace=self._trace,
            search_service=self._search,
            cache_manager=self._cache,
            adapters=self._adapters,
            metrics_aggregator=self._metrics_aggregator,
            aggregated_tracing=self._aggregated_tracing,
            hooks=self._hooks,
            pipeline=self._pipeline,
            default_policy=self._default_policy,
        )

    async def create(self, record: MemoryRecord) -> MemoryRecord:
        trace = self._trace.start("manager.create", MemoryOperation.CREATE, str(record.memory_id))
        try:
            result = await self._coordinator.create(record, policy=self._default_policy)
            self._trace.complete(trace, {"memory_id": str(result.memory_id)}, {})
            log.info("manager.create", memory_id=str(result.memory_id))
            return result
        except Exception as exc:
            self._trace.complete(trace, {"memory_id": str(record.memory_id)}, {}, errors=[str(exc)])
            raise

    async def read(self, memory_id: str) -> MemoryRecord | None:
        trace = self._trace.start("manager.read", MemoryOperation.READ, memory_id)
        try:
            result = await self._coordinator.read(memory_id)
            self._trace.complete(trace, {"memory_id": memory_id}, {"found": result is not None})
            return result
        except Exception as exc:
            self._trace.complete(trace, {"memory_id": memory_id}, {"found": False}, errors=[str(exc)])
            raise

    async def update(self, record: MemoryRecord) -> MemoryRecord:
        trace = self._trace.start("manager.update", MemoryOperation.UPDATE, str(record.memory_id))
        try:
            result = await self._coordinator.update(record, policy=self._default_policy)
            self._trace.complete(trace, {"memory_id": str(result.memory_id)}, {})
            log.info("manager.update", memory_id=str(result.memory_id))
            return result
        except Exception as exc:
            self._trace.complete(trace, {"memory_id": str(record.memory_id)}, {}, errors=[str(exc)])
            raise

    async def delete(self, memory_id: str) -> bool:
        trace = self._trace.start("manager.delete", MemoryOperation.DELETE, memory_id)
        try:
            deleted = await self._coordinator.delete(memory_id)
            self._trace.complete(trace, {"memory_id": memory_id}, {"deleted": deleted})
            log.info("manager.delete", memory_id=memory_id, deleted=deleted)
            return deleted
        except Exception as exc:
            self._trace.complete(trace, {"memory_id": memory_id}, {"deleted": False}, errors=[str(exc)])
            raise

    async def search(
        self,
        memory_type: MemoryType | None = None,
        owner_id: str | None = None,
        namespace: str | None = None,
        tags: list[str] | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[MemoryRecord]:
        trace = self._trace.start("manager.search", MemoryOperation.SEARCH, "search")
        try:
            results = await self._coordinator.search(
                memory_type=memory_type,
                owner_id=owner_id,
                namespace=namespace,
                tags=tags,
                limit=limit,
                offset=offset,
            )
            self._trace.complete(trace, {"filter": str(memory_type)}, {"count": len(results)})
            return results
        except Exception as exc:
            self._trace.complete(trace, {"filter": str(memory_type)}, {"count": 0}, errors=[str(exc)])
            raise

    async def get_context(self, **identifiers: str) -> MemoryContext:
        trace = self._trace.start("manager.get_context", MemoryOperation.SEARCH, "context")
        try:
            context = await self._coordinator.get_context(**identifiers)
            self._trace.complete(trace, {"identifiers": str(identifiers)}, {"context_built": True})
            return context
        except Exception as exc:
            self._trace.complete(trace, {"identifiers": str(identifiers)}, {"context_built": False}, errors=[str(exc)])
            raise

    async def get_metrics(self) -> MemoryMetrics:
        return self._coordinator.get_metrics()

    def get_aggregated_metrics(self) -> dict[str, Any]:
        return self._coordinator.get_aggregated_metrics()

    def get_pipeline_stages(self) -> list[dict[str, Any]]:
        return self._coordinator.get_pipeline_stages()

    async def archive(self, memory_id: str) -> MemoryRecord | None:
        return await self._coordinator.archive(memory_id)

    async def restore(self, memory_id: str) -> MemoryRecord | None:
        return await self._coordinator.restore(memory_id)

    async def health(self) -> dict[str, Any]:
        return await self._coordinator.health()

    def clear(self) -> None:
        """Clear all adapter stores (for testing)."""
        self._coordinator.clear()
