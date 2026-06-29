"""Backward compatibility tests for Memory Manager Phase 3 refactoring.

Ensures that existing Phase 1/2 contracts still work after the
Phase 3 orchestration refactoring.
"""

from __future__ import annotations

from uuid import UUID

from adip.memory.contracts.models import (
    CacheMemory,
    ConversationMemory,
    LearningMemory,
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
    MemoryLifecycleStatus,
    MemoryOperation,
    MemoryTier,
    MemoryType,
    RetentionPolicy,
)
from adip.memory.execution.adapters import (
    ChromaAdapter,
    PlaceholderStorageAdapter,
    PostgresAdapter,
    RedisAdapter,
)
from adip.memory.execution.audit_manager import AuditManager
from adip.memory.execution.cache_manager import CacheManager
from adip.memory.execution.lifecycle import MemoryLifecycleManager
from adip.memory.execution.metrics import MetricsCollector
from adip.memory.execution.models import MemoryTrace
from adip.memory.execution.policy_engine import MemoryPolicyEngine
from adip.memory.execution.router import MemoryRouter
from adip.memory.execution.validator import MemoryValidator
from adip.memory.execution.version_manager import VersionManager
from adip.memory.services.manager import DefaultMemoryManager
from adip.memory.services.service import DefaultMemoryService


class TestBackwardCompatibleMemoryRecord:
    """MemoryRecord still works with all original fields."""

    def test_memory_record_minimal(self) -> None:
        record = MemoryRecord(memory_type=MemoryType.SESSION, owner_id="u1")
        assert isinstance(record.memory_id, UUID)
        assert record.memory_type == MemoryType.SESSION
        assert record.owner_id == "u1"
        assert record.version == 1

    def test_memory_record_all_fields(self) -> None:
        record = MemoryRecord(
            memory_type=MemoryType.WORKFLOW,
            owner_id="user-1",
            namespace="ns1",
            version=2,
            tags=["important"],
            metadata={"key": "value"},
        )
        assert record.namespace == "ns1"
        assert record.version == 2
        assert "important" in record.tags
        assert record.metadata["key"] == "value"

    def test_session_memory(self) -> None:
        session = SessionMemory(session_id="s1", owner_id="u1", state={"x": 1})
        assert session.session_id == "s1"
        assert session.memory_type == MemoryType.SESSION

    def test_conversation_memory(self) -> None:
        conv = ConversationMemory(conversation_id="c1", owner_id="u1")
        assert conv.conversation_id == "c1"

    def test_workflow_memory(self) -> None:
        wf = WorkflowMemory(workflow_id="w1", owner_id="u1")
        assert wf.workflow_id == "w1"

    def test_planning_memory(self) -> None:
        plan = PlanningMemory(plan_id="p1", owner_id="u1")
        assert plan.plan_id == "p1"

    def test_recommendation_memory(self) -> None:
        rec = RecommendationMemory(recommendation_id="r1", owner_id="u1")
        assert rec.recommendation_id == "r1"

    def test_learning_memory(self) -> None:
        learn = LearningMemory(lesson_id="l1", owner_id="u1")
        assert learn.lesson_id == "l1"

    def test_user_memory(self) -> None:
        user = UserMemory(user_id="u1", owner_id="u1")
        assert user.user_id == "u1"

    def test_cache_memory(self) -> None:
        cache = CacheMemory(cache_key="k1", owner_id="u1")
        assert cache.cache_key == "k1"


class TestBackwardCompatibleEnums:
    def test_memory_type(self) -> None:
        assert MemoryType.SESSION.value == "SESSION"
        assert MemoryType.CACHE.value == "CACHE"

    def test_memory_tier(self) -> None:
        assert MemoryTier.HOT.value == "HOT"
        assert MemoryTier.COLD.value == "COLD"

    def test_memory_operation(self) -> None:
        assert MemoryOperation.CREATE.value == "CREATE"
        assert MemoryOperation.ARCHIVE.value == "ARCHIVE"

    def test_retention_policy(self) -> None:
        assert RetentionPolicy.TEMPORARY.value == "TEMPORARY"
        assert RetentionPolicy.PERMANENT.value == "PERMANENT"

    def test_lifecycle_status(self) -> None:
        assert MemoryLifecycleStatus.CREATED.value == "CREATED"
        assert MemoryLifecycleStatus.DELETED.value == "DELETED"


class TestBackwardCompatibleExecutionComponents:
    def test_audit_manager(self) -> None:
        audit = AuditManager()
        assert audit.get_records() == []

    def test_cache_manager(self) -> None:
        cache = CacheManager()
        assert cache.size() == 0

    def test_lifecycle_manager(self) -> None:
        lcm = MemoryLifecycleManager()
        record = MemoryRecord(memory_type=MemoryType.SESSION, owner_id="u1")
        lcm.initialize(record)
        assert lcm.get_current(record) == MemoryLifecycleStatus.CREATED

    def test_metrics_collector(self) -> None:
        metrics = MetricsCollector()
        snap = metrics.snapshot()
        assert snap.reads == 0

    def test_policy_engine(self) -> None:
        engine = MemoryPolicyEngine()
        record = MemoryRecord(memory_type=MemoryType.SESSION, owner_id="u1")
        import asyncio
        decision = asyncio.run(engine.validate(record, MemoryPolicy()))
        assert decision.valid is True

    def test_router(self) -> None:
        router = MemoryRouter()
        record = MemoryRecord(memory_type=MemoryType.SESSION, owner_id="u1")
        assert router.route(record) == MemoryTier.HOT

    def test_validator(self) -> None:
        validator = MemoryValidator()
        record = MemoryRecord(memory_type=MemoryType.SESSION, owner_id="u1")
        assert validator.validate(record) == []

    def test_version_manager(self) -> None:
        vm = VersionManager()
        record = MemoryRecord(memory_type=MemoryType.SESSION, owner_id="u1")
        vm.record_creation(record)
        assert vm.get_latest_version(str(record.memory_id)) == 1

    def test_memory_trace_new_fields_default(self) -> None:
        trace = MemoryTrace(
            stage_name="test",
            operation=MemoryOperation.CREATE,
        )
        assert trace.memory_domain == ""
        assert trace.session_id == ""
        assert trace.correlation_id == ""

    def test_memory_trace_new_fields_custom(self) -> None:
        trace = MemoryTrace(
            stage_name="test",
            operation=MemoryOperation.CREATE,
            memory_domain="PLANNER",
            session_id="session-1",
            correlation_id="corr-1",
        )
        assert trace.memory_domain == "PLANNER"
        assert trace.session_id == "session-1"
        assert trace.correlation_id == "corr-1"

    def test_placeholder_adapter(self) -> None:
        adapter = PlaceholderStorageAdapter(MemoryTier.HOT)
        import asyncio
        assert asyncio.run(adapter.health()) is True

    def test_redis_adapter(self) -> None:
        adapter = RedisAdapter()
        import asyncio
        assert asyncio.run(adapter.health()) is True

    def test_postgres_adapter(self) -> None:
        adapter = PostgresAdapter()
        import asyncio
        assert asyncio.run(adapter.health()) is True

    def test_chroma_adapter(self) -> None:
        adapter = ChromaAdapter()
        import asyncio
        assert asyncio.run(adapter.health()) is True


class TestBackwardCompatibleDefaultMemoryManager:
    async def test_create(self) -> None:
        mgr = DefaultMemoryManager()
        record = SessionMemory(session_id="s1", owner_id="u1")
        result = await mgr.create(record)
        assert result.memory_id == record.memory_id

    async def test_read(self) -> None:
        mgr = DefaultMemoryManager()
        record = SessionMemory(session_id="s1", owner_id="u1")
        created = await mgr.create(record)
        fetched = await mgr.read(str(created.memory_id))
        assert fetched is not None

    async def test_update(self) -> None:
        mgr = DefaultMemoryManager()
        record = SessionMemory(session_id="s1", owner_id="u1")
        created = await mgr.create(record)
        created.metadata["x"] = "y"
        updated = await mgr.update(created)
        assert updated.metadata["x"] == "y"

    async def test_delete(self) -> None:
        mgr = DefaultMemoryManager()
        record = SessionMemory(session_id="s1", owner_id="u1")
        created = await mgr.create(record)
        assert await mgr.delete(str(created.memory_id)) is True

    async def test_search(self) -> None:
        mgr = DefaultMemoryManager()
        await mgr.create(SessionMemory(session_id="s1", owner_id="u1"))
        results = await mgr.search(owner_id="u1")
        assert len(results) == 1

    async def test_get_context(self) -> None:
        mgr = DefaultMemoryManager()
        await mgr.create(SessionMemory(session_id="s1", owner_id="u1"))
        ctx = await mgr.get_context(session_id="s1")
        assert ctx.session is not None

    async def test_get_metrics(self) -> None:
        mgr = DefaultMemoryManager()
        metrics = await mgr.get_metrics()
        assert isinstance(metrics, MemoryMetrics)

    def test_clear(self) -> None:
        mgr = DefaultMemoryManager()
        mgr.clear()

    async def test_internal_trace_access(self) -> None:
        mgr = DefaultMemoryManager()
        await mgr.create(SessionMemory(session_id="s1", owner_id="u1"))
        traces = mgr._trace.get_traces("manager.create")
        assert len(traces) == 1

    async def test_internal_lifecycle_access(self) -> None:
        mgr = DefaultMemoryManager()
        record = SessionMemory(session_id="s1", owner_id="u1")
        created = await mgr.create(record)
        history = mgr._lifecycle.get_history(created)
        assert len(history) >= 1


class TestBackwardCompatibleDefaultMemoryService:
    async def test_store(self) -> None:
        mgr = DefaultMemoryManager()
        svc = DefaultMemoryService(manager=mgr)
        record = SessionMemory(session_id="s1", owner_id="u1")
        result = await svc.store(record)
        assert result is not None

    async def test_retrieve(self) -> None:
        mgr = DefaultMemoryManager()
        svc = DefaultMemoryService(manager=mgr)
        stored = await svc.store(SessionMemory(session_id="s1", owner_id="u1"))
        fetched = await svc.retrieve(str(stored.memory_id))
        assert fetched is not None

    async def test_remove(self) -> None:
        mgr = DefaultMemoryManager()
        svc = DefaultMemoryService(manager=mgr)
        stored = await svc.store(SessionMemory(session_id="s1", owner_id="u1"))
        assert await svc.remove(str(stored.memory_id)) is True

    async def test_find(self) -> None:
        mgr = DefaultMemoryManager()
        svc = DefaultMemoryService(manager=mgr)
        await svc.store(SessionMemory(session_id="s1", owner_id="u1"))
        results = await svc.find(memory_type=MemoryType.SESSION)
        assert len(results) == 1

    async def test_context(self) -> None:
        mgr = DefaultMemoryManager()
        svc = DefaultMemoryService(manager=mgr)
        await svc.store(SessionMemory(session_id="s1", owner_id="u1"))
        ctx = await svc.context(session_id="s1")
        assert ctx.session is not None
