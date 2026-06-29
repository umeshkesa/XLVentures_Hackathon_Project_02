"""Memory Stores — typed store implementations for each memory type.

Each store:
  1. Validates the incoming memory record
  2. Applies MemoryPolicy via the PolicyEngine
  3. Routes to the correct storage adapter via MemoryRouter
  4. Updates lifecycle state
  5. Records audit trail
  6. Returns the result
"""

from __future__ import annotations

import structlog

from adip.memory.contracts.models import (
    CacheMemory,
    ConversationMemory,
    LearningMemory,
    MemoryPolicy,
    MemoryRecord,
    PlanningMemory,
    RecommendationMemory,
    SessionMemory,
    UserMemory,
    WorkflowMemory,
)
from adip.memory.enums import (
    MemoryLifecycleStatus,
    MemoryOperation,
    MemoryType,
)
from adip.memory.execution.adapters import (
    ChromaAdapter,
    PlaceholderStorageAdapter,
    PostgresAdapter,
    RedisAdapter,
)
from adip.memory.execution.audit_manager import AuditManager
from adip.memory.execution.lifecycle import MemoryLifecycleManager
from adip.memory.execution.metrics import MetricsCollector
from adip.memory.execution.policy_engine import MemoryPolicyEngine
from adip.memory.execution.router import MemoryRouter
from adip.memory.execution.trace import TraceManager
from adip.memory.execution.validator import MemoryValidator
from adip.memory.execution.version_manager import VersionManager

log = structlog.get_logger(__name__)


class BaseMemoryStore:
    """Shared logic for all memory stores."""

    def __init__(
        self,
        router: MemoryRouter,
        lifecycle: MemoryLifecycleManager,
        policy_engine: MemoryPolicyEngine,
        validator: MemoryValidator,
        audit: AuditManager,
        version_manager: VersionManager,
        metrics: MetricsCollector,
        trace: TraceManager,
        adapters: dict[str, PlaceholderStorageAdapter] | None = None,
    ) -> None:
        self._router = router
        self._lifecycle = lifecycle
        self._policy = policy_engine
        self._validator = validator
        self._audit = audit
        self._versions = version_manager
        self._metrics = metrics
        self._trace = trace
        self._adapters = adapters or {
            "HOT": RedisAdapter(),
            "WARM": PostgresAdapter(),
            "COLD": ChromaAdapter(),
        }

    async def _resolve_adapter(
        self,
        record: MemoryRecord,
        policy: MemoryPolicy | None = None,
    ) -> PlaceholderStorageAdapter:
        tier = self._router.route(record, policy)
        return self._adapters[tier.value]

    async def _save(
        self,
        record: MemoryRecord,
        policy: MemoryPolicy | None = None,
    ) -> MemoryRecord:
        trace = self._trace.start("store.save", MemoryOperation.CREATE, str(record.memory_id))

        self._validator.validate(record)
        self._lifecycle.initialize(record)
        self._lifecycle.transition(record, MemoryLifecycleStatus.ACTIVE, reason="Record created")

        policy = policy or MemoryPolicy()
        decision = await self._policy.validate(record, policy)
        if not decision.valid:
            raise ValueError(f"Policy violations: {'; '.join(decision.violations)}")

        adapter = await self._resolve_adapter(record, policy)
        result = await adapter.create(record)

        self._versions.record_creation(result)
        self._audit.record(result, MemoryOperation.CREATE, tier=adapter._tier.value)
        self._metrics.increment_writes()

        self._trace.complete(trace, {"memory_id": str(result.memory_id)}, {})
        return result

    async def _fetch(
        self,
        memory_id: str,
        policy: MemoryPolicy | None = None,
    ) -> MemoryRecord | None:
        trace = self._trace.start("store.fetch", MemoryOperation.READ, memory_id)

        record = None
        for adapter in self._adapters.values():
            record = await adapter.read(memory_id)
            if record is not None:
                break

        if record is not None:
            self._audit.record(record, MemoryOperation.READ)
            self._metrics.increment_reads()
        else:
            self._metrics.increment_cache_misses()

        self._trace.complete(trace, {"memory_id": memory_id}, {"found": record is not None})
        return record

    async def _remove(
        self,
        memory_id: str,
        policy: MemoryPolicy | None = None,
    ) -> bool:
        trace = self._trace.start("store.remove", MemoryOperation.DELETE, memory_id)

        deleted = False
        for adapter in self._adapters.values():
            if await adapter.delete(memory_id):
                deleted = True
                break

        if deleted:
            self._metrics.increment_writes()
            self._audit.record_raw(memory_id, MemoryOperation.DELETE)

        self._trace.complete(trace, {"memory_id": memory_id}, {"deleted": deleted})
        return deleted

    async def _search(
        self,
        memory_type: MemoryType | None = None,
        owner_id: str | None = None,
        namespace: str | None = None,
        tags: list[str] | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[MemoryRecord]:
        trace = self._trace.start("store.search", MemoryOperation.SEARCH, "search")

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
        self._trace.complete(trace, {"filter": str(memory_type)}, {"count": len(results)})
        return results


class SessionMemoryStore(BaseMemoryStore):
    """Store for SessionMemory records."""

    async def save(self, memory: SessionMemory, policy: MemoryPolicy | None = None) -> SessionMemory:
        result = await self._save(memory, policy)
        return SessionMemory(**result.model_dump())

    async def get(self, session_id: str, policy: MemoryPolicy | None = None) -> SessionMemory | None:
        # Search by session_id across all adapters
        results = await self._search(memory_type=MemoryType.SESSION, limit=100)
        for r in results:
            if isinstance(r, SessionMemory) and r.session_id == session_id:
                return r
            if hasattr(r, "session_id") and getattr(r, "session_id", None) == session_id:
                return SessionMemory(**r.model_dump())
        return None

    async def delete(self, session_id: str) -> bool:
        results = await self._search(memory_type=MemoryType.SESSION, limit=100)
        for r in results:
            sid = getattr(r, "session_id", None)
            if sid == session_id:
                return await self._remove(str(r.memory_id))
        return False


class ConversationMemoryStore(BaseMemoryStore):
    """Store for ConversationMemory records."""

    async def save(self, memory: ConversationMemory, policy: MemoryPolicy | None = None) -> ConversationMemory:
        result = await self._save(memory, policy)
        return ConversationMemory(**result.model_dump())

    async def get(self, conversation_id: str) -> ConversationMemory | None:
        results = await self._search(memory_type=MemoryType.CONVERSATION, limit=100)
        for r in results:
            if getattr(r, "conversation_id", None) == conversation_id:
                return ConversationMemory(**r.model_dump())
        return None

    async def delete(self, conversation_id: str) -> bool:
        results = await self._search(memory_type=MemoryType.CONVERSATION, limit=100)
        for r in results:
            if getattr(r, "conversation_id", None) == conversation_id:
                return await self._remove(str(r.memory_id))
        return False


class WorkflowMemoryStore(BaseMemoryStore):
    """Store for WorkflowMemory records."""

    async def save(self, memory: WorkflowMemory, policy: MemoryPolicy | None = None) -> WorkflowMemory:
        result = await self._save(memory, policy)
        return WorkflowMemory(**result.model_dump())

    async def get(self, workflow_id: str) -> WorkflowMemory | None:
        results = await self._search(memory_type=MemoryType.WORKFLOW, limit=100)
        for r in results:
            if getattr(r, "workflow_id", None) == workflow_id:
                return WorkflowMemory(**r.model_dump())
        return None

    async def delete(self, workflow_id: str) -> bool:
        results = await self._search(memory_type=MemoryType.WORKFLOW, limit=100)
        for r in results:
            if getattr(r, "workflow_id", None) == workflow_id:
                return await self._remove(str(r.memory_id))
        return False


class PlanningMemoryStore(BaseMemoryStore):
    """Store for PlanningMemory records."""

    async def save(self, memory: PlanningMemory, policy: MemoryPolicy | None = None) -> PlanningMemory:
        result = await self._save(memory, policy)
        return PlanningMemory(**result.model_dump())

    async def get(self, plan_id: str) -> PlanningMemory | None:
        results = await self._search(memory_type=MemoryType.PLANNING, limit=100)
        for r in results:
            if getattr(r, "plan_id", None) == plan_id:
                return PlanningMemory(**r.model_dump())
        return None

    async def delete(self, plan_id: str) -> bool:
        results = await self._search(memory_type=MemoryType.PLANNING, limit=100)
        for r in results:
            if getattr(r, "plan_id", None) == plan_id:
                return await self._remove(str(r.memory_id))
        return False


class RecommendationMemoryStore(BaseMemoryStore):
    """Store for RecommendationMemory records."""

    async def save(self, memory: RecommendationMemory, policy: MemoryPolicy | None = None) -> RecommendationMemory:
        result = await self._save(memory, policy)
        return RecommendationMemory(**result.model_dump())

    async def get(self, recommendation_id: str) -> RecommendationMemory | None:
        results = await self._search(memory_type=MemoryType.RECOMMENDATION, limit=100)
        for r in results:
            if getattr(r, "recommendation_id", None) == recommendation_id:
                return RecommendationMemory(**r.model_dump())
        return None

    async def delete(self, recommendation_id: str) -> bool:
        results = await self._search(memory_type=MemoryType.RECOMMENDATION, limit=100)
        for r in results:
            if getattr(r, "recommendation_id", None) == recommendation_id:
                return await self._remove(str(r.memory_id))
        return False


class LearningMemoryStore(BaseMemoryStore):
    """Store for LearningMemory records."""

    async def save(self, memory: LearningMemory, policy: MemoryPolicy | None = None) -> LearningMemory:
        result = await self._save(memory, policy)
        return LearningMemory(**result.model_dump())

    async def get(self, lesson_id: str) -> LearningMemory | None:
        results = await self._search(memory_type=MemoryType.LEARNING, limit=100)
        for r in results:
            if getattr(r, "lesson_id", None) == lesson_id:
                return LearningMemory(**r.model_dump())
        return None

    async def delete(self, lesson_id: str) -> bool:
        results = await self._search(memory_type=MemoryType.LEARNING, limit=100)
        for r in results:
            if getattr(r, "lesson_id", None) == lesson_id:
                return await self._remove(str(r.memory_id))
        return False


class UserMemoryStore(BaseMemoryStore):
    """Store for UserMemory records."""

    async def save(self, memory: UserMemory, policy: MemoryPolicy | None = None) -> UserMemory:
        result = await self._save(memory, policy)
        return UserMemory(**result.model_dump())

    async def get(self, user_id: str) -> UserMemory | None:
        results = await self._search(memory_type=MemoryType.USER, limit=100)
        for r in results:
            if getattr(r, "user_id", None) == user_id:
                return UserMemory(**r.model_dump())
        return None

    async def delete(self, user_id: str) -> bool:
        results = await self._search(memory_type=MemoryType.USER, limit=100)
        for r in results:
            if getattr(r, "user_id", None) == user_id:
                return await self._remove(str(r.memory_id))
        return False


class CacheStore(BaseMemoryStore):
    """Store for CacheMemory records."""

    async def set(self, memory: CacheMemory, policy: MemoryPolicy | None = None) -> CacheMemory:
        result = await self._save(memory, policy)
        return CacheMemory(**result.model_dump())

    async def get(self, cache_key: str) -> CacheMemory | None:
        results = await self._search(memory_type=MemoryType.CACHE, limit=100)
        for r in results:
            if getattr(r, "cache_key", None) == cache_key:
                return CacheMemory(**r.model_dump())
        return None

    async def delete(self, cache_key: str) -> bool:
        results = await self._search(memory_type=MemoryType.CACHE, limit=100)
        for r in results:
            if getattr(r, "cache_key", None) == cache_key:
                return await self._remove(str(r.memory_id))
        return False

    async def clear(self) -> int:
        count = 0
        results = await self._search(memory_type=MemoryType.CACHE, limit=1000)
        for r in results:
            if await self._remove(str(r.memory_id)):
                count += 1
        return count
