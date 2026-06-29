"""MemoryCoordinator — central internal orchestrator for the Memory Platform.

MemoryCoordinator is the heart of Phase 3 orchestration.  It receives
requests from MemoryManager and coordinates all internal components:

    • Route memory requests
    • Resolve MemoryDomain, MemoryTier, Namespace
    • Apply MemoryPolicy
    • Validate Lifecycle
    • Coordinate multiple stores
    • Coordinate versioning
    • Coordinate auditing
    • Aggregate metrics
    • Aggregate traces
    • Prepare transaction support

MemoryCoordinator contains orchestration only — no business logic.
"""

from __future__ import annotations

from typing import Any

import structlog

from adip.memory.contracts.models import (
    CacheMemory,
    ConversationMemory,
    LearningMemory,
    MemoryContext,
    MemoryMetrics,
    MemoryPolicy,
    MemoryRecord,
    PlanningMemory,
    RecommendationMemory,
    SessionMemory,
    UserMemory,
    WorkflowMemory,
)
from adip.memory.enums import (
    MemoryDomain,
    MemoryLifecycleStatus,
    MemoryOperation,
    MemoryTier,
    MemoryType,
)
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
from adip.memory.orchestration.hooks import IntegrationHooks
from adip.memory.orchestration.metrics_aggregator import MetricsAggregator
from adip.memory.orchestration.pipeline import MemoryOperationPipeline
from adip.memory.orchestration.tracing import AggregatedTracing

log = structlog.get_logger(__name__)


class MemoryCoordinator:
    """Central internal orchestrator for all memory operations.

    Coordinates Phase 2 execution components without containing
    business logic.  Every memory operation flows through this
    coordinator.
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

    # ── Domain resolution ──────────────────────────────────────────────────

    def resolve_domain(self, record: MemoryRecord) -> MemoryDomain:
        """Resolve the MemoryDomain from the record."""
        return record.memory_domain

    def resolve_tier(self, record: MemoryRecord) -> MemoryTier:
        """Resolve the storage tier for a record."""
        return self._router.route(record, self._default_policy)

    def resolve_namespace(self, record: MemoryRecord) -> str:
        """Resolve the namespace for a record."""
        return record.namespace

    # ── Create ─────────────────────────────────────────────────────────────

    async def create(
        self,
        record: MemoryRecord,
        policy: MemoryPolicy | None = None,
        correlation_id: str = "",
        session_id: str = "",
    ) -> MemoryRecord:
        policy = policy or self._default_policy
        domain = self.resolve_domain(record)

        self._pipeline.record_stage("MemoryCoordinator", MemoryOperation.CREATE, str(record.memory_id))

        await self._hooks.on_before_operation(MemoryOperation.CREATE, record)

        self._validator.validate(record)
        self._pipeline.record_stage("MemoryValidator", MemoryOperation.CREATE, str(record.memory_id))

        self._lifecycle.initialize(record)
        self._lifecycle.transition(record, MemoryLifecycleStatus.ACTIVE, reason="Coordinator create")
        self._pipeline.record_stage("LifecycleManager", MemoryOperation.CREATE, str(record.memory_id))

        decision = await self._policy.validate(record, policy)
        if not decision.valid:
            self._metrics.increment_policy_violations()
            self._metrics_aggregator.increment_policy_violations()
            raise ValueError(f"Policy violations: {'; '.join(decision.violations)}")
        self._pipeline.record_stage("MemoryPolicyEngine", MemoryOperation.CREATE, str(record.memory_id))

        tier = self.resolve_tier(record)
        record.memory_tier = tier
        self._pipeline.record_stage("MemoryRouter", MemoryOperation.CREATE, str(record.memory_id))

        adapter = self._adapters[tier.value]
        result = await adapter.create(record)
        self._pipeline.record_stage("MemoryStore", MemoryOperation.CREATE, str(record.memory_id))
        self._pipeline.record_stage("StorageAdapter", MemoryOperation.CREATE, str(record.memory_id))

        self._versions.record_creation(result)
        self._audit.record(result, MemoryOperation.CREATE, tier=tier.value, correlation_id=correlation_id)
        self._metrics.increment_writes()
        self._metrics.increment_routing_decisions()
        self._metrics.increment_lifecycle_transitions()

        self._metrics_aggregator.increment_operations()
        self._metrics_aggregator.increment_writes()
        self._metrics_aggregator.increment_routing_decisions()
        self._metrics_aggregator.increment_lifecycle_transitions()
        self._metrics_aggregator.record_operation_for_domain(domain)
        self._metrics_aggregator.record_tier_utilization(tier.value)

        self._aggregated_tracing.record_stage(
            stage_name="coordinator.create",
            operation=MemoryOperation.CREATE,
            memory_id=str(result.memory_id),
            session_id=session_id,
            correlation_id=correlation_id,
            domain=domain.value,
            namespace=result.namespace,
            tier=tier.value,
            lifecycle_state=MemoryLifecycleStatus.ACTIVE.value,
        )

        await self._hooks.on_after_operation(MemoryOperation.CREATE, record, result)

        log.info(
            "coordinator.create",
            memory_id=str(result.memory_id),
            tier=tier.value,
            domain=domain.value,
            correlation_id=correlation_id,
        )
        return result

    # ── Read ───────────────────────────────────────────────────────────────

    async def read(
        self,
        memory_id: str,
        correlation_id: str = "",
        session_id: str = "",
    ) -> MemoryRecord | None:
        self._pipeline.record_stage("MemoryCoordinator", MemoryOperation.READ, memory_id)

        await self._hooks.on_before_operation(MemoryOperation.READ)

        record: MemoryRecord | None = None
        for adapter in self._adapters.values():
            record = await adapter.read(memory_id)
            if record is not None:
                break

        if record is not None:
            self._audit.record(record, MemoryOperation.READ, correlation_id=correlation_id)
            self._metrics.increment_reads()
            self._metrics_aggregator.increment_operations()
            self._metrics_aggregator.increment_reads()
            self._metrics_aggregator.record_operation_for_domain(record.memory_domain)
        else:
            self._metrics.increment_cache_misses()
            self._metrics_aggregator.increment_cache_misses()

        self._aggregated_tracing.record_stage(
            stage_name="coordinator.read",
            operation=MemoryOperation.READ,
            memory_id=memory_id,
            session_id=session_id,
            correlation_id=correlation_id,
            success=record is not None,
        )

        await self._hooks.on_after_operation(MemoryOperation.READ, result=record)

        return record

    # ── Update ─────────────────────────────────────────────────────────────

    async def update(
        self,
        record: MemoryRecord,
        policy: MemoryPolicy | None = None,
        correlation_id: str = "",
        session_id: str = "",
    ) -> MemoryRecord:
        policy = policy or self._default_policy
        domain = self.resolve_domain(record)

        self._pipeline.record_stage("MemoryCoordinator", MemoryOperation.UPDATE, str(record.memory_id))

        await self._hooks.on_before_operation(MemoryOperation.UPDATE, record)

        self._validator.validate(record)

        existing = await self.read(str(record.memory_id), correlation_id=correlation_id, session_id=session_id)
        if existing is None:
            raise ValueError(f"Record {record.memory_id} not found for update")

        self._lifecycle.transition(record, MemoryLifecycleStatus.UPDATED, reason="Coordinator update")

        decision = await self._policy.validate(record, policy)
        if not decision.valid:
            self._metrics.increment_policy_violations()
            self._metrics_aggregator.increment_policy_violations()
            raise ValueError(f"Policy violations: {'; '.join(decision.violations)}")

        tier = self.resolve_tier(record)
        record.memory_tier = tier

        adapter = self._adapters[tier.value]
        result = await adapter.update(record)

        self._versions.increment(result)
        self._audit.record(result, MemoryOperation.UPDATE, tier=tier.value, correlation_id=correlation_id)
        self._metrics.increment_writes()
        self._metrics.increment_lifecycle_transitions()

        self._metrics_aggregator.increment_operations()
        self._metrics_aggregator.increment_writes()
        self._metrics_aggregator.increment_updates()
        self._metrics_aggregator.increment_lifecycle_transitions()
        self._metrics_aggregator.record_operation_for_domain(domain)
        self._metrics_aggregator.record_tier_utilization(tier.value)

        self._aggregated_tracing.record_stage(
            stage_name="coordinator.update",
            operation=MemoryOperation.UPDATE,
            memory_id=str(result.memory_id),
            session_id=session_id,
            correlation_id=correlation_id,
            domain=domain.value,
            namespace=result.namespace,
            tier=tier.value,
            lifecycle_state=MemoryLifecycleStatus.UPDATED.value,
        )

        await self._hooks.on_after_operation(MemoryOperation.UPDATE, record, result)

        log.info(
            "coordinator.update",
            memory_id=str(result.memory_id),
            tier=tier.value,
            correlation_id=correlation_id,
        )
        return result

    # ── Delete ─────────────────────────────────────────────────────────────

    async def delete(
        self,
        memory_id: str,
        correlation_id: str = "",
        session_id: str = "",
    ) -> bool:
        self._pipeline.record_stage("MemoryCoordinator", MemoryOperation.DELETE, memory_id)

        await self._hooks.on_before_operation(MemoryOperation.DELETE)

        record = None
        for adapter in self._adapters.values():
            record = await adapter.read(memory_id)
            if record is not None:
                break

        if record is None:
            self._aggregated_tracing.record_stage(
                stage_name="coordinator.delete",
                operation=MemoryOperation.DELETE,
                memory_id=memory_id,
                session_id=session_id,
                correlation_id=correlation_id,
                success=False,
            )
            await self._hooks.on_after_operation(MemoryOperation.DELETE, result=False)
            return False

        self._lifecycle.transition(record, MemoryLifecycleStatus.DELETED, reason="Coordinator delete")

        deleted = False
        for adapter in self._adapters.values():
            if await adapter.delete(memory_id):
                deleted = True

        if deleted:
            self._audit.record_raw(
                memory_id, MemoryOperation.DELETE,
                memory_type=record.memory_type,
                correlation_id=correlation_id,
            )
            self._metrics.increment_writes()
            self._metrics.increment_lifecycle_transitions()
            self._metrics_aggregator.increment_operations()
            self._metrics_aggregator.increment_writes()
            self._metrics_aggregator.increment_deletes()
            self._metrics_aggregator.increment_lifecycle_transitions()
            self._metrics_aggregator.record_operation_for_domain(record.memory_domain)

        self._aggregated_tracing.record_stage(
            stage_name="coordinator.delete",
            operation=MemoryOperation.DELETE,
            memory_id=memory_id,
            session_id=session_id,
            correlation_id=correlation_id,
            success=deleted,
        )

        await self._hooks.on_after_operation(MemoryOperation.DELETE, result=deleted)

        log.info("coordinator.delete", memory_id=memory_id, deleted=deleted, correlation_id=correlation_id)
        return deleted

    # ── Search ─────────────────────────────────────────────────────────────

    async def search(
        self,
        memory_type: MemoryType | None = None,
        owner_id: str | None = None,
        namespace: str | None = None,
        tags: list[str] | None = None,
        limit: int = 20,
        offset: int = 0,
        correlation_id: str = "",
        session_id: str = "",
    ) -> list[MemoryRecord]:
        self._pipeline.record_stage("MemoryCoordinator", MemoryOperation.SEARCH, "search")

        results: list[MemoryRecord] = []
        for adapter in self._adapters.values():
            batch = await adapter.search(
                memory_type=memory_type,
                owner_id=owner_id,
                namespace=namespace,
                tags=tags,
                limit=limit,
                offset=offset,
            )
            results.extend(batch)

        self._metrics.increment_searches()
        self._metrics_aggregator.increment_operations()
        self._metrics_aggregator.increment_searches()

        self._aggregated_tracing.record_stage(
            stage_name="coordinator.search",
            operation=MemoryOperation.SEARCH,
            session_id=session_id,
            correlation_id=correlation_id,
            success=True,
        )

        return results

    # ── Context ────────────────────────────────────────────────────────────

    async def get_context(
        self,
        **identifiers: str,
    ) -> MemoryContext:
        context = MemoryContext()

        session_id = identifiers.get("session_id", "")
        conversation_id = identifiers.get("conversation_id", "")
        workflow_id = identifiers.get("workflow_id", "")
        plan_id = identifiers.get("plan_id", "")
        recommendation_id = identifiers.get("recommendation_id", "")
        lesson_id = identifiers.get("lesson_id", "")
        user_id = identifiers.get("user_id", "")
        cache_key = identifiers.get("cache_key", "")

        if session_id:
            results = await self.search(memory_type=MemoryType.SESSION, limit=100)
            for r in results:
                if hasattr(r, "session_id") and getattr(r, "session_id", None) == session_id:
                    context.session = SessionMemory(**r.model_dump())
                    break

        if conversation_id:
            results = await self.search(memory_type=MemoryType.CONVERSATION, limit=100)
            for r in results:
                if getattr(r, "conversation_id", None) == conversation_id:
                    context.conversation = ConversationMemory(**r.model_dump())
                    break

        if workflow_id:
            results = await self.search(memory_type=MemoryType.WORKFLOW, limit=100)
            for r in results:
                if getattr(r, "workflow_id", None) == workflow_id:
                    context.workflow = WorkflowMemory(**r.model_dump())
                    break

        if plan_id:
            results = await self.search(memory_type=MemoryType.PLANNING, limit=100)
            for r in results:
                if getattr(r, "plan_id", None) == plan_id:
                    context.planning = PlanningMemory(**r.model_dump())
                    break

        if recommendation_id:
            results = await self.search(memory_type=MemoryType.RECOMMENDATION, limit=100)
            for r in results:
                if getattr(r, "recommendation_id", None) == recommendation_id:
                    context.recommendation = RecommendationMemory(**r.model_dump())
                    break

        if lesson_id:
            results = await self.search(memory_type=MemoryType.LEARNING, limit=100)
            for r in results:
                if getattr(r, "lesson_id", None) == lesson_id:
                    context.learning = LearningMemory(**r.model_dump())
                    break

        if user_id:
            results = await self.search(memory_type=MemoryType.USER, limit=100)
            for r in results:
                if getattr(r, "user_id", None) == user_id:
                    context.user = UserMemory(**r.model_dump())
                    break

        if cache_key:
            results = await self.search(memory_type=MemoryType.CACHE, limit=100)
            for r in results:
                if getattr(r, "cache_key", None) == cache_key:
                    context.cache = CacheMemory(**r.model_dump())
                    break

        context.metadata["identifiers"] = dict(identifiers)
        self._metrics.increment_searches()
        return context

    # ── Archive / Restore ──────────────────────────────────────────────────

    async def archive(
        self,
        memory_id: str,
        correlation_id: str = "",
        session_id: str = "",
    ) -> MemoryRecord | None:
        self._pipeline.record_stage("MemoryCoordinator", MemoryOperation.ARCHIVE, memory_id)

        record = None
        for adapter in self._adapters.values():
            record = await adapter.read(memory_id)
            if record is not None:
                break

        if record is None:
            return None

        self._lifecycle.transition(record, MemoryLifecycleStatus.ARCHIVED, reason="Coordinator archive")

        result = None
        for adapter in self._adapters.values():
            result = await adapter.archive(memory_id)
            if result is not None:
                break

        if result:
            self._audit.record(result, MemoryOperation.ARCHIVE, correlation_id=correlation_id)
            self._metrics.increment_writes()
            self._metrics_aggregator.increment_operations()
            self._metrics_aggregator.increment_archives()
            self._metrics_aggregator.record_operation_for_domain(result.memory_domain)

        self._aggregated_tracing.record_stage(
            stage_name="coordinator.archive",
            operation=MemoryOperation.ARCHIVE,
            memory_id=memory_id,
            session_id=session_id,
            correlation_id=correlation_id,
            success=result is not None,
        )

        await self._hooks.on_after_operation(MemoryOperation.ARCHIVE, result=result)

        log.info("coordinator.archive", memory_id=memory_id, correlation_id=correlation_id)
        return result

    async def restore(
        self,
        memory_id: str,
        correlation_id: str = "",
        session_id: str = "",
    ) -> MemoryRecord | None:
        self._pipeline.record_stage("MemoryCoordinator", MemoryOperation.ARCHIVE, memory_id)

        await self._hooks.on_before_operation(MemoryOperation.ARCHIVE)

        result = None
        for adapter in self._adapters.values():
            result = await adapter.restore(memory_id)
            if result is not None:
                break

        if result:
            self._lifecycle.transition(result, MemoryLifecycleStatus.ACTIVE, reason="Coordinator restore")
            self._audit.record(result, MemoryOperation.ARCHIVE, correlation_id=correlation_id)
            self._metrics.increment_writes()
            self._metrics_aggregator.increment_operations()
            self._metrics_aggregator.increment_restores()
            self._metrics_aggregator.record_operation_for_domain(result.memory_domain)

        self._aggregated_tracing.record_stage(
            stage_name="coordinator.restore",
            operation=MemoryOperation.ARCHIVE,
            memory_id=memory_id,
            session_id=session_id,
            correlation_id=correlation_id,
            success=result is not None,
        )

        await self._hooks.on_after_operation(MemoryOperation.ARCHIVE, result=result)

        log.info("coordinator.restore", memory_id=memory_id, correlation_id=correlation_id)
        return result

    # ── Metrics ────────────────────────────────────────────────────────────

    def get_metrics(self) -> MemoryMetrics:
        return self._metrics.snapshot()

    def get_aggregated_metrics(self) -> dict[str, Any]:
        return self._metrics_aggregator.snapshot()

    def get_pipeline_stages(self) -> list[dict[str, Any]]:
        return self._pipeline.get_executed_stages()

    def get_aggregated_traces(
        self,
        stage_name: str | None = None,
        session_id: str | None = None,
    ) -> list[dict[str, Any]]:
        return self._aggregated_tracing.get_traces(stage_name=stage_name, session_id=session_id)

    # ── Health ─────────────────────────────────────────────────────────────

    async def health(self) -> dict[str, Any]:
        """Return the current health status of all coordinator components."""
        storage_health: dict[str, str] = {}
        for tier_name, adapter in self._adapters.items():
            try:
                ok = await adapter.health()
                storage_health[tier_name] = "HEALTHY" if ok else "UNHEALTHY"
            except Exception:
                storage_health[tier_name] = "UNHEALTHY"

        return {
            "coordinator_status": "HEALTHY",
            "router_status": "HEALTHY",
            "lifecycle_status": "HEALTHY",
            "policy_status": "HEALTHY",
            "cache_status": "HEALTHY",
            "storage_status": storage_health,
        }

    # ── Testing helpers ────────────────────────────────────────────────────

    def clear(self) -> None:
        """Clear all adapter stores (for testing)."""
        for adapter in self._adapters.values():
            adapter.clear()
