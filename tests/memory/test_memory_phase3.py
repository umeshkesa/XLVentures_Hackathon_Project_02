"""Comprehensive tests for Memory Manager Phase 3 — orchestration.

Covers: DefaultMemoryManager (CRUD, search, context, metrics) and
DefaultMemoryService (store, retrieve, remove, find, context).
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

import pytest

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
    MemoryTier,
    MemoryType,
    RetentionPolicy,
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
from adip.memory.services.manager import DefaultMemoryManager
from adip.memory.services.service import DefaultMemoryService

# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────


@pytest.fixture
def manager() -> DefaultMemoryManager:
    return DefaultMemoryManager()


@pytest.fixture
def session_record() -> SessionMemory:
    return SessionMemory(
        session_id="sess-1",
        owner_id="user-1",
        state={"key": "value"},
    )


@pytest.fixture
def workflow_record() -> WorkflowMemory:
    return WorkflowMemory(
        workflow_id="wf-1",
        owner_id="user-1",
        execution_state={"step": 1},
    )


@pytest.fixture
def conversation_record() -> ConversationMemory:
    return ConversationMemory(
        conversation_id="conv-1",
        owner_id="user-1",
        messages=[{"role": "user", "content": "hello"}],
    )


@pytest.fixture
def planning_record() -> PlanningMemory:
    return PlanningMemory(
        plan_id="plan-1",
        owner_id="user-1",
        plan_data={"steps": ["a", "b"]},
    )


@pytest.fixture
def recommendation_record() -> RecommendationMemory:
    return RecommendationMemory(
        recommendation_id="rec-1",
        owner_id="user-1",
        recommendation_data={"item": "x"},
    )


@pytest.fixture
def learning_record() -> LearningMemory:
    return LearningMemory(
        lesson_id="lesson-1",
        owner_id="user-1",
        pattern="test pattern",
    )


@pytest.fixture
def user_record() -> UserMemory:
    return UserMemory(
        user_id="user-1",
        owner_id="user-1",
        preferences={"theme": "dark"},
    )


@pytest.fixture
def cache_record() -> CacheMemory:
    return CacheMemory(
        cache_key="cache:test",
        owner_id="user-1",
        cached_data={"value": 42},
    )


# ─────────────────────────────────────────────────────────────────────────────
# DefaultMemoryManager Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestDefaultMemoryManagerCreate:
    async def test_create_session(self, manager: DefaultMemoryManager, session_record: SessionMemory) -> None:
        result = await manager.create(session_record)
        assert result.memory_id == session_record.memory_id
        assert result.memory_type == MemoryType.SESSION
        assert result.session_id == "sess-1"
        assert result.metadata.get("lifecycle_status") == MemoryLifecycleStatus.ACTIVE.value

    async def test_create_workflow(self, manager: DefaultMemoryManager, workflow_record: WorkflowMemory) -> None:
        result = await manager.create(workflow_record)
        assert result.workflow_id == "wf-1"
        assert result.memory_type == MemoryType.WORKFLOW

    async def test_create_conversation(self, manager: DefaultMemoryManager, conversation_record: ConversationMemory) -> None:
        result = await manager.create(conversation_record)
        assert result.conversation_id == "conv-1"

    async def test_create_planning(self, manager: DefaultMemoryManager, planning_record: PlanningMemory) -> None:
        result = await manager.create(planning_record)
        assert result.plan_id == "plan-1"

    async def test_create_recommendation(self, manager: DefaultMemoryManager, recommendation_record: RecommendationMemory) -> None:
        result = await manager.create(recommendation_record)
        assert result.recommendation_id == "rec-1"

    async def test_create_learning(self, manager: DefaultMemoryManager, learning_record: LearningMemory) -> None:
        result = await manager.create(learning_record)
        assert result.lesson_id == "lesson-1"

    async def test_create_user(self, manager: DefaultMemoryManager, user_record: UserMemory) -> None:
        result = await manager.create(user_record)
        assert result.user_id == "user-1"

    async def test_create_cache(self, manager: DefaultMemoryManager, cache_record: CacheMemory) -> None:
        result = await manager.create(cache_record)
        assert result.cache_key == "cache:test"

    async def test_create_invalid_record_raises(self, manager: DefaultMemoryManager) -> None:
        record = MemoryRecord(memory_type=MemoryType.SESSION, owner_id="")  # empty owner_id
        with pytest.raises(ValueError, match="Memory validation failed"):
            await manager.create(record)

    async def test_create_and_verify_trace(self, manager: DefaultMemoryManager, session_record: SessionMemory) -> None:
        await manager.create(session_record)
        traces = manager._trace.get_traces("manager.create")
        assert len(traces) == 1
        assert traces[0].success is True

    async def test_create_and_verify_metrics(self, manager: DefaultMemoryManager, session_record: SessionMemory) -> None:
        await manager.create(session_record)
        metrics = await manager.get_metrics()
        assert metrics.writes >= 1


class TestDefaultMemoryManagerRead:
    async def test_read_existing(self, manager: DefaultMemoryManager, session_record: SessionMemory) -> None:
        created = await manager.create(session_record)
        fetched = await manager.read(str(created.memory_id))
        assert fetched is not None
        assert fetched.memory_type == MemoryType.SESSION

    async def test_read_nonexistent(self, manager: DefaultMemoryManager) -> None:
        fetched = await manager.read(str(uuid.uuid4()))
        assert fetched is None

    async def test_read_after_delete(self, manager: DefaultMemoryManager, session_record: SessionMemory) -> None:
        created = await manager.create(session_record)
        await manager.delete(str(created.memory_id))
        fetched = await manager.read(str(created.memory_id))
        assert fetched is None


class TestDefaultMemoryManagerUpdate:
    async def test_update_existing(self, manager: DefaultMemoryManager, session_record: SessionMemory) -> None:
        created = await manager.create(session_record)
        created.state["new_key"] = "new_value"
        updated = await manager.update(created)
        assert str(updated.memory_id) == str(created.memory_id)
        assert updated.metadata.get("lifecycle_status") == MemoryLifecycleStatus.UPDATED.value

    async def test_update_nonexistent_raises(self, manager: DefaultMemoryManager) -> None:
        record = MemoryRecord(memory_type=MemoryType.SESSION, owner_id="user-1")
        with pytest.raises(ValueError, match="not found for update"):
            await manager.update(record)

    async def test_update_increments_version(self, manager: DefaultMemoryManager, session_record: SessionMemory) -> None:
        created = await manager.create(session_record)
        v1 = created.version
        created.metadata["updated"] = True
        updated = await manager.update(created)
        assert updated.version > v1


class TestDefaultMemoryManagerDelete:
    async def test_delete_existing(self, manager: DefaultMemoryManager, session_record: SessionMemory) -> None:
        created = await manager.create(session_record)
        deleted = await manager.delete(str(created.memory_id))
        assert deleted is True

    async def test_delete_nonexistent(self, manager: DefaultMemoryManager) -> None:
        deleted = await manager.delete(str(uuid.uuid4()))
        assert deleted is False

    async def test_delete_updates_lifecycle(self, manager: DefaultMemoryManager, session_record: SessionMemory) -> None:
        created = await manager.create(session_record)
        mid = str(created.memory_id)
        history = manager._lifecycle.get_history(created)
        assert history[-1].new_state == MemoryLifecycleStatus.ACTIVE
        await manager.delete(mid)
        # After delete the record is gone, but we can check the lifecycle history
        # was recorded before deletion
        assert any(h.new_state == MemoryLifecycleStatus.DELETED for h in manager._lifecycle.get_history(created))


class TestDefaultMemoryManagerSearch:
    async def test_search_by_type(self, manager: DefaultMemoryManager, session_record: SessionMemory, workflow_record: WorkflowMemory) -> None:
        await manager.create(session_record)
        await manager.create(workflow_record)

        sessions = await manager.search(memory_type=MemoryType.SESSION)
        assert len(sessions) == 1
        assert sessions[0].memory_type == MemoryType.SESSION

        workflows = await manager.search(memory_type=MemoryType.WORKFLOW)
        assert len(workflows) == 1

    async def test_search_by_owner(self, manager: DefaultMemoryManager, session_record: SessionMemory, workflow_record: WorkflowMemory) -> None:
        await manager.create(session_record)
        await manager.create(workflow_record)

        results = await manager.search(owner_id="user-1")
        assert len(results) == 2

    async def test_search_by_namespace(self, manager: DefaultMemoryManager) -> None:
        r1 = SessionMemory(session_id="s1", owner_id="u1", namespace="ns1")
        r2 = SessionMemory(session_id="s2", owner_id="u1", namespace="ns2")
        await manager.create(r1)
        await manager.create(r2)

        results = await manager.search(namespace="ns1")
        assert len(results) == 1

    async def test_search_by_tags(self, manager: DefaultMemoryManager) -> None:
        r1 = SessionMemory(session_id="s1", owner_id="u1", tags=["important"])
        r2 = SessionMemory(session_id="s2", owner_id="u1", tags=["archived"])
        await manager.create(r1)
        await manager.create(r2)

        results = await manager.search(tags=["important"])
        assert len(results) == 1

    async def test_search_pagination(self, manager: DefaultMemoryManager) -> None:
        for i in range(5):
            await manager.create(SessionMemory(session_id=f"s{i}", owner_id="u1"))

        all_results = await manager.search(limit=10, offset=0)
        assert len(all_results) == 5

        page = await manager.search(limit=2, offset=0)
        assert len(page) == 2


class TestDefaultMemoryManagerContext:
    async def test_get_context_with_session(self, manager: DefaultMemoryManager, session_record: SessionMemory) -> None:
        await manager.create(session_record)
        context = await manager.get_context(session_id="sess-1")
        assert context.session is not None
        assert context.session.session_id == "sess-1"

    async def test_get_context_with_workflow(self, manager: DefaultMemoryManager, workflow_record: WorkflowMemory) -> None:
        await manager.create(workflow_record)
        context = await manager.get_context(workflow_id="wf-1")
        assert context.workflow is not None
        assert context.workflow.workflow_id == "wf-1"

    async def test_get_context_with_conversation(self, manager: DefaultMemoryManager, conversation_record: ConversationMemory) -> None:
        await manager.create(conversation_record)
        context = await manager.get_context(conversation_id="conv-1")
        assert context.conversation is not None

    async def test_get_context_with_planning(self, manager: DefaultMemoryManager, planning_record: PlanningMemory) -> None:
        await manager.create(planning_record)
        context = await manager.get_context(plan_id="plan-1")
        assert context.planning is not None

    async def test_get_context_with_recommendation(self, manager: DefaultMemoryManager, recommendation_record: RecommendationMemory) -> None:
        await manager.create(recommendation_record)
        context = await manager.get_context(recommendation_id="rec-1")
        assert context.recommendation is not None

    async def test_get_context_with_learning(self, manager: DefaultMemoryManager, learning_record: LearningMemory) -> None:
        await manager.create(learning_record)
        context = await manager.get_context(lesson_id="lesson-1")
        assert context.learning is not None

    async def test_get_context_with_user(self, manager: DefaultMemoryManager, user_record: UserMemory) -> None:
        await manager.create(user_record)
        context = await manager.get_context(user_id="user-1")
        assert context.user is not None

    async def test_get_context_with_cache(self, manager: DefaultMemoryManager, cache_record: CacheMemory) -> None:
        await manager.create(cache_record)
        context = await manager.get_context(cache_key="cache:test")
        assert context.cache is not None

    async def test_get_context_all_types(self, manager: DefaultMemoryManager) -> None:
        await manager.create(SessionMemory(session_id="s1", owner_id="u1"))
        await manager.create(WorkflowMemory(workflow_id="w1", owner_id="u1"))
        await manager.create(ConversationMemory(conversation_id="c1", owner_id="u1"))
        await manager.create(PlanningMemory(plan_id="p1", owner_id="u1"))
        await manager.create(RecommendationMemory(recommendation_id="r1", owner_id="u1"))
        await manager.create(LearningMemory(lesson_id="l1", owner_id="u1"))
        await manager.create(UserMemory(user_id="u1", owner_id="u1"))
        await manager.create(CacheMemory(cache_key="k1", owner_id="u1"))

        context = await manager.get_context(
            session_id="s1",
            workflow_id="w1",
            conversation_id="c1",
            plan_id="p1",
            recommendation_id="r1",
            lesson_id="l1",
            user_id="u1",
            cache_key="k1",
        )
        assert context.session is not None
        assert context.workflow is not None
        assert context.conversation is not None
        assert context.planning is not None
        assert context.recommendation is not None
        assert context.learning is not None
        assert context.user is not None
        assert context.cache is not None

    async def test_get_context_no_match(self, manager: DefaultMemoryManager) -> None:
        context = await manager.get_context(session_id="nonexistent")
        assert context.session is None

    async def test_get_context_empty_identifiers(self, manager: DefaultMemoryManager) -> None:
        context = await manager.get_context()
        assert context.session is None
        assert context.workflow is None
        assert context.metadata.get("identifiers") == {}


class TestDefaultMemoryManagerMetrics:
    async def test_initial_metrics(self, manager: DefaultMemoryManager) -> None:
        metrics = await manager.get_metrics()
        assert isinstance(metrics, MemoryMetrics)
        assert metrics.reads == 0
        assert metrics.writes == 0

    async def test_metrics_after_create(self, manager: DefaultMemoryManager, session_record: SessionMemory) -> None:
        await manager.create(session_record)
        metrics = await manager.get_metrics()
        assert metrics.writes >= 1

    async def test_metrics_after_read(self, manager: DefaultMemoryManager, session_record: SessionMemory) -> None:
        created = await manager.create(session_record)
        await manager.read(str(created.memory_id))
        metrics = await manager.get_metrics()
        assert metrics.reads >= 1

    async def test_metrics_after_delete(self, manager: DefaultMemoryManager, session_record: SessionMemory) -> None:
        created = await manager.create(session_record)
        await manager.delete(str(created.memory_id))
        metrics = await manager.get_metrics()
        assert metrics.writes >= 2  # create + delete


class TestDefaultMemoryManagerEdgeCases:
    async def test_create_multiple_records(self, manager: DefaultMemoryManager) -> None:
        for i in range(10):
            await manager.create(SessionMemory(session_id=f"s{i}", owner_id="u1"))
        results = await manager.search(owner_id="u1")
        assert len(results) == 10

    async def test_create_empty_record_raises(self, manager: DefaultMemoryManager) -> None:
        record = MemoryRecord(memory_type=MemoryType.SESSION, owner_id="")
        with pytest.raises(ValueError, match="owner_id is required"):
            await manager.create(record)

    async def test_read_returns_copy(self, manager: DefaultMemoryManager, session_record: SessionMemory) -> None:
        created = await manager.create(session_record)
        read1 = await manager.read(str(created.memory_id))
        read2 = await manager.read(str(created.memory_id))
        assert read1 is not None and read2 is not None
        assert str(read1.memory_id) == str(read2.memory_id)

    async def test_create_with_expiry(self, manager: DefaultMemoryManager) -> None:
        future = datetime.now(UTC) + timedelta(hours=1)
        record = SessionMemory(session_id="s1", owner_id="u1", expires_at=future)
        result = await manager.create(record)
        assert result.expires_at is not None
        assert result.expires_at > datetime.now(UTC)

    async def test_clear_adapters(self, manager: DefaultMemoryManager, session_record: SessionMemory) -> None:
        await manager.create(session_record)
        manager.clear()
        results = await manager.search()
        assert len(results) == 0


# ─────────────────────────────────────────────────────────────────────────────
# DefaultMemoryService Tests
# ─────────────────────────────────────────────────────────────────────────────


@pytest.fixture
def service(manager: DefaultMemoryManager) -> DefaultMemoryService:
    audit = AuditManager()
    return DefaultMemoryService(manager=manager, audit=audit)


class TestDefaultMemoryServiceStore:
    async def test_store_session(self, service: DefaultMemoryService, session_record: SessionMemory) -> None:
        result = await service.store(session_record)
        assert result.memory_type == MemoryType.SESSION
        assert result.session_id == "sess-1"

    async def test_store_then_retrieve(self, service: DefaultMemoryService, session_record: SessionMemory) -> None:
        stored = await service.store(session_record)
        fetched = await service.retrieve(str(stored.memory_id))
        assert fetched is not None
        assert fetched.memory_type == MemoryType.SESSION

    async def test_store_invalid_raises(self, service: DefaultMemoryService) -> None:
        record = SessionMemory(session_id="s1", owner_id="")
        with pytest.raises(ValueError):
            await service.store(record)


class TestDefaultMemoryServiceRetrieve:
    async def test_retrieve_existing(self, service: DefaultMemoryService, session_record: SessionMemory) -> None:
        stored = await service.store(session_record)
        fetched = await service.retrieve(str(stored.memory_id))
        assert fetched is not None

    async def test_retrieve_nonexistent(self, service: DefaultMemoryService) -> None:
        fetched = await service.retrieve(str(uuid.uuid4()))
        assert fetched is None

    async def test_retrieve_after_remove(self, service: DefaultMemoryService, session_record: SessionMemory) -> None:
        stored = await service.store(session_record)
        await service.remove(str(stored.memory_id))
        fetched = await service.retrieve(str(stored.memory_id))
        assert fetched is None


class TestDefaultMemoryServiceRemove:
    async def test_remove_existing(self, service: DefaultMemoryService, session_record: SessionMemory) -> None:
        stored = await service.store(session_record)
        result = await service.remove(str(stored.memory_id))
        assert result is True

    async def test_remove_nonexistent(self, service: DefaultMemoryService) -> None:
        result = await service.remove(str(uuid.uuid4()))
        assert result is False


class TestDefaultMemoryServiceFind:
    async def test_find_by_type(self, service: DefaultMemoryService) -> None:
        await service.store(SessionMemory(session_id="s1", owner_id="u1"))
        await service.store(WorkflowMemory(workflow_id="w1", owner_id="u1"))

        results = await service.find(memory_type=MemoryType.SESSION)
        assert len(results) == 1

    async def test_find_by_owner(self, service: DefaultMemoryService) -> None:
        await service.store(SessionMemory(session_id="s1", owner_id="u1"))
        await service.store(SessionMemory(session_id="s2", owner_id="u2"))

        results = await service.find(owner_id="u1")
        assert len(results) == 1

    async def test_find_all(self, service: DefaultMemoryService) -> None:
        await service.store(SessionMemory(session_id="s1", owner_id="u1"))
        await service.store(SessionMemory(session_id="s2", owner_id="u1"))

        results = await service.find()
        assert len(results) == 2


class TestDefaultMemoryServiceContext:
    async def test_context(self, service: DefaultMemoryService) -> None:
        await service.store(SessionMemory(session_id="s1", owner_id="u1"))
        ctx = await service.context(session_id="s1")
        assert ctx.session is not None

    async def test_context_no_match(self, service: DefaultMemoryService) -> None:
        ctx = await service.context(session_id="nonexistent")
        assert ctx.session is None


class TestDefaultMemoryServiceIntegration:
    async def test_full_lifecycle(self, service: DefaultMemoryService) -> None:
        record = SessionMemory(session_id="s1", owner_id="u1", state={"count": 0})

        stored = await service.store(record)
        assert stored is not None

        fetched = await service.retrieve(str(stored.memory_id))
        assert fetched is not None
        assert fetched.session_id == "s1"

        removed = await service.remove(str(stored.memory_id))
        assert removed is True

        refetched = await service.retrieve(str(stored.memory_id))
        assert refetched is None

    async def test_multiple_stores_and_search(self, service: DefaultMemoryService) -> None:
        for i in range(5):
            await service.store(SessionMemory(session_id=f"s{i}", owner_id="u1", tags=["test"]))

        results = await service.find(owner_id="u1")
        assert len(results) == 5

        tagged = await service.find(tags=["test"])
        assert len(tagged) == 5

    async def test_different_types_in_service(self, service: DefaultMemoryService) -> None:
        session = await service.store(SessionMemory(session_id="s1", owner_id="u1"))
        workflow = await service.store(WorkflowMemory(workflow_id="w1", owner_id="u1"))
        conversation = await service.store(ConversationMemory(conversation_id="c1", owner_id="u1"))

        assert session.memory_type == MemoryType.SESSION
        assert workflow.memory_type == MemoryType.WORKFLOW
        assert conversation.memory_type == MemoryType.CONVERSATION


# ─────────────────────────────────────────────────────────────────────────────
# Integration: DefaultMemoryManager with custom configuration
# ─────────────────────────────────────────────────────────────────────────────


class TestDefaultMemoryManagerCustomConfig:
    async def test_custom_router(self) -> None:
        router = MemoryRouter(custom_tier_map={MemoryType.SESSION: MemoryTier.COLD})
        mgr = DefaultMemoryManager(router=router)
        record = SessionMemory(session_id="s1", owner_id="u1")
        result = await mgr.create(record)
        assert result is not None

    async def test_custom_adapters(self) -> None:
        hot = PlaceholderStorageAdapter(MemoryTier.HOT)
        adapters = {"HOT": hot, "WARM": PlaceholderStorageAdapter(MemoryTier.WARM), "COLD": PlaceholderStorageAdapter(MemoryTier.COLD)}
        mgr = DefaultMemoryManager(adapters=adapters)
        record = SessionMemory(session_id="s1", owner_id="u1")
        result = await mgr.create(record)
        assert result is not None

    async def test_custom_policy(self) -> None:
        policy = MemoryPolicy(retention_policy=RetentionPolicy.PERMANENT, ttl=3600)
        mgr = DefaultMemoryManager(default_policy=policy)
        record = SessionMemory(session_id="s1", owner_id="u1")
        result = await mgr.create(record)
        assert result is not None

    async def test_all_custom_components(self) -> None:
        router = MemoryRouter()
        lifecycle = MemoryLifecycleManager()
        policy_engine = MemoryPolicyEngine()
        validator = MemoryValidator()
        audit = AuditManager()
        version_manager = VersionManager()
        metrics = MetricsCollector()
        trace = TraceManager()
        search_service = MemorySearchService()
        cache_manager = CacheManager()
        adapters = {"HOT": PlaceholderStorageAdapter(MemoryTier.HOT), "WARM": PlaceholderStorageAdapter(MemoryTier.WARM), "COLD": PlaceholderStorageAdapter(MemoryTier.COLD)}

        mgr = DefaultMemoryManager(
            router=router,
            lifecycle=lifecycle,
            policy_engine=policy_engine,
            validator=validator,
            audit=audit,
            version_manager=version_manager,
            metrics=metrics,
            trace=trace,
            search_service=search_service,
            cache_manager=cache_manager,
            adapters=adapters,
        )
        record = SessionMemory(session_id="s1", owner_id="u1")
        result = await mgr.create(record)
        assert result is not None
        assert result.session_id == "s1"
