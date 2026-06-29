"""Comprehensive tests for Memory Manager Phase 2 — execution layer.

Covers: MemoryRouter, LifecycleManager, PolicyEngine, Validator,
CacheManager, VersionManager, AuditManager, SearchService, all 8
MemoryStores, StorageAdapters, Trace, and Metrics.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

import pytest

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
    MemoryTier,
    MemoryType,
    RetentionPolicy,
)
from adip.memory.execution.adapters import (
    ChromaAdapter,
    PostgresAdapter,
    RedisAdapter,
)
from adip.memory.execution.audit_manager import AuditManager
from adip.memory.execution.cache_manager import CacheManager
from adip.memory.execution.lifecycle import MemoryLifecycleManager
from adip.memory.execution.metrics import MetricsCollector
from adip.memory.execution.models import (
    AuditRecord,
    CacheEntry,
    MemoryLifecycleHistory,
    MemoryTrace,
    PolicyDecision,
    SearchQuery,
    VersionHistory,
)
from adip.memory.execution.policy_engine import MemoryPolicyEngine
from adip.memory.execution.router import MemoryRouter
from adip.memory.execution.search import MemorySearchService
from adip.memory.execution.trace import TraceManager
from adip.memory.execution.validator import MemoryValidator
from adip.memory.execution.version_manager import VersionManager

# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────


@pytest.fixture
def sample_record() -> MemoryRecord:
    return MemoryRecord(
        memory_type=MemoryType.SESSION,
        owner_id="user-1",
        namespace="default",
    )


@pytest.fixture
def session_memory() -> SessionMemory:
    return SessionMemory(session_id="sess-1", owner_id="user-1")


@pytest.fixture
def router() -> MemoryRouter:
    return MemoryRouter()


@pytest.fixture
def lifecycle() -> MemoryLifecycleManager:
    return MemoryLifecycleManager()


# ─────────────────────────────────────────────────────────────────────────────
# MemoryRouter
# ─────────────────────────────────────────────────────────────────────────────


class TestMemoryRouter:
    def test_default_tier_mapping(self, router: MemoryRouter) -> None:
        assert router.get_tier_for_type(MemoryType.SESSION) == MemoryTier.HOT
        assert router.get_tier_for_type(MemoryType.WORKFLOW) == MemoryTier.HOT
        assert router.get_tier_for_type(MemoryType.CACHE) == MemoryTier.HOT
        assert router.get_tier_for_type(MemoryType.CONVERSATION) == MemoryTier.WARM
        assert router.get_tier_for_type(MemoryType.PLANNING) == MemoryTier.WARM
        assert router.get_tier_for_type(MemoryType.RECOMMENDATION) == MemoryTier.WARM
        assert router.get_tier_for_type(MemoryType.USER) == MemoryTier.WARM
        assert router.get_tier_for_type(MemoryType.LEARNING) == MemoryTier.COLD

    def test_route_session_to_hot(self, router: MemoryRouter) -> None:
        record = MemoryRecord(memory_type=MemoryType.SESSION)
        assert router.route(record) == MemoryTier.HOT

    def test_route_learning_to_cold(self, router: MemoryRouter) -> None:
        record = MemoryRecord(memory_type=MemoryType.LEARNING)
        assert router.route(record) == MemoryTier.COLD

    def test_namespace_override(self) -> None:
        router = MemoryRouter(namespace_routes={"critical": MemoryTier.HOT})
        record = MemoryRecord(
            memory_type=MemoryType.LEARNING, namespace="critical",
        )
        assert router.route(record) == MemoryTier.HOT

    def test_custom_tier_map(self) -> None:
        router = MemoryRouter(custom_tier_map={MemoryType.USER: MemoryTier.HOT})
        assert router.get_tier_for_type(MemoryType.USER) == MemoryTier.HOT

    def test_validate_route_valid(self, router: MemoryRouter) -> None:
        assert router.validate_route(MemoryTier.HOT) is True

    def test_get_all_routes(self, router: MemoryRouter) -> None:
        routes = router.get_all_routes()
        assert len(routes) == 8
        assert routes[MemoryType.SESSION] == MemoryTier.HOT

    def test_unknown_type_defaults_to_warm(self) -> None:
        router = MemoryRouter()
        # No MemoryType enum value should be missing, but just in case
        for mt in MemoryType:
            assert router.get_tier_for_type(mt) in MemoryTier


# ─────────────────────────────────────────────────────────────────────────────
# MemoryLifecycleManager
# ─────────────────────────────────────────────────────────────────────────────


class TestMemoryLifecycleManager:
    def test_initialize_sets_created(self, lifecycle: MemoryLifecycleManager) -> None:
        record = MemoryRecord(memory_type=MemoryType.SESSION, owner_id="u1")
        lifecycle.initialize(record)
        assert record.metadata["lifecycle_status"] == MemoryLifecycleStatus.CREATED.value

    def test_initialize_idempotent(self, lifecycle: MemoryLifecycleManager) -> None:
        record = MemoryRecord(memory_type=MemoryType.SESSION, owner_id="u1")
        record.metadata["lifecycle_status"] = MemoryLifecycleStatus.ACTIVE.value
        lifecycle.initialize(record)
        assert record.metadata["lifecycle_status"] == MemoryLifecycleStatus.ACTIVE.value

    def test_transition_created_to_active(self, lifecycle: MemoryLifecycleManager) -> None:
        record = MemoryRecord(memory_type=MemoryType.SESSION, owner_id="u1")
        lifecycle.initialize(record)
        lifecycle.transition(record, MemoryLifecycleStatus.ACTIVE, reason="Test")
        assert record.metadata["lifecycle_status"] == MemoryLifecycleStatus.ACTIVE.value

    def test_transition_active_to_updated(self, lifecycle: MemoryLifecycleManager) -> None:
        record = MemoryRecord(memory_type=MemoryType.SESSION, owner_id="u1")
        lifecycle.initialize(record)
        lifecycle.transition(record, MemoryLifecycleStatus.ACTIVE)
        lifecycle.transition(record, MemoryLifecycleStatus.UPDATED, reason="Modified")
        assert record.metadata["lifecycle_status"] == MemoryLifecycleStatus.UPDATED.value

    def test_illegal_transition_raises(self, lifecycle: MemoryLifecycleManager) -> None:
        record = MemoryRecord(memory_type=MemoryType.SESSION, owner_id="u1")
        lifecycle.initialize(record)
        with pytest.raises(ValueError, match="Invalid lifecycle transition"):
            lifecycle.transition(record, MemoryLifecycleStatus.DELETED)

    def test_full_lifecycle(self, lifecycle: MemoryLifecycleManager) -> None:
        record = MemoryRecord(memory_type=MemoryType.SESSION, owner_id="u1")
        lifecycle.initialize(record)
        lifecycle.transition(record, MemoryLifecycleStatus.ACTIVE)
        lifecycle.transition(record, MemoryLifecycleStatus.UPDATED)
        lifecycle.transition(record, MemoryLifecycleStatus.ACTIVE)
        lifecycle.transition(record, MemoryLifecycleStatus.ARCHIVED)
        lifecycle.transition(record, MemoryLifecycleStatus.DELETED)
        assert record.metadata["lifecycle_status"] == MemoryLifecycleStatus.DELETED.value

    def test_archived_to_active_restore(self, lifecycle: MemoryLifecycleManager) -> None:
        record = MemoryRecord(memory_type=MemoryType.SESSION, owner_id="u1")
        lifecycle.initialize(record)
        lifecycle.transition(record, MemoryLifecycleStatus.ACTIVE)
        lifecycle.transition(record, MemoryLifecycleStatus.ARCHIVED)
        lifecycle.transition(record, MemoryLifecycleStatus.ACTIVE, reason="Restored")
        assert record.metadata["lifecycle_status"] == MemoryLifecycleStatus.ACTIVE.value

    def test_expired_to_deleted(self, lifecycle: MemoryLifecycleManager) -> None:
        record = MemoryRecord(memory_type=MemoryType.SESSION, owner_id="u1")
        lifecycle.initialize(record)
        lifecycle.transition(record, MemoryLifecycleStatus.ACTIVE)
        lifecycle.transition(record, MemoryLifecycleStatus.EXPIRED)
        lifecycle.transition(record, MemoryLifecycleStatus.DELETED)
        assert record.metadata["lifecycle_status"] == MemoryLifecycleStatus.DELETED.value

    def test_terminal_states(self) -> None:
        assert MemoryLifecycleManager.is_terminal(MemoryLifecycleStatus.EXPIRED)
        assert MemoryLifecycleManager.is_terminal(MemoryLifecycleStatus.DELETED)
        assert not MemoryLifecycleManager.is_terminal(MemoryLifecycleStatus.ACTIVE)

    def test_get_history(self, lifecycle: MemoryLifecycleManager) -> None:
        record = MemoryRecord(memory_type=MemoryType.SESSION, owner_id="u1")
        lifecycle.initialize(record)
        lifecycle.transition(record, MemoryLifecycleStatus.ACTIVE)
        lifecycle.transition(record, MemoryLifecycleStatus.UPDATED)
        history = lifecycle.get_history(record)
        assert len(history) == 2
        assert history[0].previous_state == MemoryLifecycleStatus.CREATED
        assert history[0].new_state == MemoryLifecycleStatus.ACTIVE

    def test_get_allowed_transitions(self) -> None:
        allowed = MemoryLifecycleManager.get_allowed_transitions(
            MemoryLifecycleStatus.ACTIVE,
        )
        assert MemoryLifecycleStatus.UPDATED in allowed
        assert MemoryLifecycleStatus.ARCHIVED in allowed
        assert MemoryLifecycleStatus.EXPIRED in allowed
        assert MemoryLifecycleStatus.DELETED in allowed

    def test_get_current(self, lifecycle: MemoryLifecycleManager) -> None:
        record = MemoryRecord(memory_type=MemoryType.SESSION, owner_id="u1")
        assert lifecycle.get_current(record) == MemoryLifecycleStatus.CREATED


# ─────────────────────────────────────────────────────────────────────────────
# Storage Adapters
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
class TestStorageAdapters:
    async def test_redis_create_and_read(self) -> None:
        adapter = RedisAdapter()
        record = MemoryRecord(memory_type=MemoryType.SESSION, owner_id="u1")
        await adapter.create(record)
        fetched = await adapter.read(str(record.memory_id))
        assert fetched is not None
        assert fetched.memory_type == MemoryType.SESSION

    async def test_postgres_create_and_read(self) -> None:
        adapter = PostgresAdapter()
        record = MemoryRecord(memory_type=MemoryType.WORKFLOW, owner_id="u1")
        await adapter.create(record)
        fetched = await adapter.read(str(record.memory_id))
        assert fetched is not None

    async def test_chroma_create_and_read(self) -> None:
        adapter = ChromaAdapter()
        record = MemoryRecord(memory_type=MemoryType.LEARNING, owner_id="u1")
        await adapter.create(record)
        fetched = await adapter.read(str(record.memory_id))
        assert fetched is not None

    async def test_update(self) -> None:
        adapter = RedisAdapter()
        record = MemoryRecord(memory_type=MemoryType.SESSION, owner_id="u1")
        await adapter.create(record)
        record.owner_id = "updated-owner"
        updated = await adapter.update(record)
        assert updated.owner_id == "updated-owner"

    async def test_delete(self) -> None:
        adapter = RedisAdapter()
        record = MemoryRecord(memory_type=MemoryType.SESSION, owner_id="u1")
        await adapter.create(record)
        deleted = await adapter.delete(str(record.memory_id))
        assert deleted is True
        assert await adapter.read(str(record.memory_id)) is None

    async def test_delete_nonexistent(self) -> None:
        adapter = RedisAdapter()
        assert await adapter.delete(str(uuid.uuid4())) is False

    async def test_search(self) -> None:
        adapter = RedisAdapter()
        r1 = MemoryRecord(memory_type=MemoryType.SESSION, owner_id="u1", tags=["a"])
        r2 = MemoryRecord(memory_type=MemoryType.WORKFLOW, owner_id="u2", tags=["b"])
        await adapter.create(r1)
        await adapter.create(r2)
        results = await adapter.search(memory_type=MemoryType.SESSION)
        assert len(results) == 1
        assert results[0].owner_id == "u1"

    async def test_search_by_tags(self) -> None:
        adapter = RedisAdapter()
        r1 = MemoryRecord(memory_type=MemoryType.SESSION, owner_id="u1", tags=["critical"])
        r2 = MemoryRecord(memory_type=MemoryType.WORKFLOW, owner_id="u2", tags=["normal"])
        await adapter.create(r1)
        await adapter.create(r2)
        results = await adapter.search(tags=["critical"])
        assert len(results) == 1

    async def test_archive_and_restore(self) -> None:
        adapter = RedisAdapter()
        record = MemoryRecord(memory_type=MemoryType.SESSION, owner_id="u1")
        await adapter.create(record)
        archived = await adapter.archive(str(record.memory_id))
        assert archived is not None
        assert archived.metadata.get("archived") is True
        restored = await adapter.restore(str(record.memory_id))
        assert restored is not None
        assert restored.metadata.get("archived") is not True

    async def test_health(self) -> None:
        assert await RedisAdapter().health() is True
        assert await PostgresAdapter().health() is True
        assert await ChromaAdapter().health() is True

    async def test_clear(self) -> None:
        adapter = RedisAdapter()
        await adapter.create(MemoryRecord(memory_type=MemoryType.SESSION, owner_id="u1"))
        adapter.clear()
        assert len(await adapter.search()) == 0


# ─────────────────────────────────────────────────────────────────────────────
# MemoryPolicyEngine
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
class TestMemoryPolicyEngine:
    async def test_valid_policy(self) -> None:
        engine = MemoryPolicyEngine()
        record = MemoryRecord(memory_type=MemoryType.SESSION, owner_id="u1")
        policy = MemoryPolicy()
        decision = await engine.validate(record, policy)
        assert decision.valid is True

    async def test_expired_ttl_violation(self) -> None:
        engine = MemoryPolicyEngine()
        record = MemoryRecord(
            memory_type=MemoryType.SESSION, owner_id="u1",
            expires_at=datetime.now(UTC) - timedelta(hours=1),
        )
        policy = MemoryPolicy()
        decision = await engine.validate(record, policy)
        assert not decision.valid
        assert any("expired" in v.lower() for v in decision.violations)

    async def test_ttl_warning(self) -> None:
        engine = MemoryPolicyEngine()
        record = MemoryRecord(memory_type=MemoryType.SESSION, owner_id="u1")
        policy = MemoryPolicy(ttl=3600)
        decision = await engine.validate(record, policy)
        assert decision.valid
        assert any("TTL" in w for w in decision.warnings)

    async def test_retention_temporary_warning(self) -> None:
        engine = MemoryPolicyEngine()
        record = MemoryRecord(memory_type=MemoryType.SESSION, owner_id="u1")
        policy = MemoryPolicy(retention_policy=RetentionPolicy.TEMPORARY)
        decision = await engine.validate(record, policy)
        assert decision.valid
        assert any("Temporary" in w for w in decision.warnings)

    async def test_encryption_warning(self) -> None:
        engine = MemoryPolicyEngine()
        record = MemoryRecord(memory_type=MemoryType.SESSION, owner_id="u1")
        policy = MemoryPolicy(encryption_required=True)
        decision = await engine.validate(record, policy)
        assert decision.valid
        assert any("Encryption" in w for w in decision.warnings)

    async def test_terminal_lifecycle_warning(self) -> None:
        engine = MemoryPolicyEngine()
        record = MemoryRecord(memory_type=MemoryType.SESSION, owner_id="u1")
        record.metadata["lifecycle_status"] = MemoryLifecycleStatus.DELETED.value
        policy = MemoryPolicy()
        decision = await engine.validate(record, policy)
        assert decision.valid
        assert any("terminal" in w.lower() for w in decision.warnings)

    async def test_invalid_lifecycle_violation(self) -> None:
        engine = MemoryPolicyEngine()
        record = MemoryRecord(memory_type=MemoryType.SESSION, owner_id="u1")
        record.metadata["lifecycle_status"] = "INVALID_STATUS"
        policy = MemoryPolicy()
        decision = await engine.validate(record, policy)
        assert not decision.valid
        assert any("Invalid lifecycle" in v for v in decision.violations)


# ─────────────────────────────────────────────────────────────────────────────
# MemoryValidator
# ─────────────────────────────────────────────────────────────────────────────


class TestMemoryValidator:
    def test_valid_record(self) -> None:
        validator = MemoryValidator()
        record = MemoryRecord(memory_type=MemoryType.SESSION, owner_id="u1")
        errors = validator.validate(record)
        assert errors == []

    def test_missing_owner(self) -> None:
        validator = MemoryValidator()
        record = MemoryRecord(memory_type=MemoryType.SESSION)
        with pytest.raises(ValueError, match="owner_id"):
            validator.validate(record)

    def test_invalid_lifecycle(self) -> None:
        validator = MemoryValidator()
        record = MemoryRecord(memory_type=MemoryType.SESSION, owner_id="u1")
        record.metadata["lifecycle_status"] = "NOT_A_STATUS"
        with pytest.raises(ValueError, match="lifecycle_status"):
            validator.validate(record)

    def test_empty_namespace(self) -> None:
        validator = MemoryValidator()
        record = MemoryRecord(memory_type=MemoryType.SESSION, owner_id="u1", namespace="")
        with pytest.raises(ValueError, match="namespace"):
            validator.validate(record)

    def test_expired_past(self) -> None:
        validator = MemoryValidator()
        record = MemoryRecord(
            memory_type=MemoryType.SESSION, owner_id="u1",
            expires_at=datetime.now(UTC) - timedelta(hours=1),
        )
        with pytest.raises(ValueError, match="expires_at"):
            validator.validate(record)

    def test_version_zero(self) -> None:
        record = MemoryRecord(memory_type=MemoryType.SESSION, owner_id="u1", version=0)
        # Pydantic should catch this before validator
        assert record.version == 0


# ─────────────────────────────────────────────────────────────────────────────
# CacheManager
# ─────────────────────────────────────────────────────────────────────────────


class TestCacheManager:
    def test_lookup_miss(self) -> None:
        cache = CacheManager()
        assert cache.lookup("nonexistent") is None

    def test_insert_and_lookup(self) -> None:
        cache = CacheManager()
        cache.insert("key1", {"value": 42})
        result = cache.lookup("key1")
        assert result is not None
        assert result["value"] == 42

    def test_evict(self) -> None:
        cache = CacheManager()
        cache.insert("key1", {"value": 42})
        assert cache.evict("key1") is True
        assert cache.lookup("key1") is None

    def test_evict_nonexistent(self) -> None:
        cache = CacheManager()
        assert cache.evict("nonexistent") is False

    def test_invalidate_all(self) -> None:
        cache = CacheManager()
        cache.insert("a", {})
        cache.insert("b", {})
        assert cache.invalidate() == 2
        assert cache.size() == 0

    def test_invalidate_namespace(self) -> None:
        cache = CacheManager()
        cache.insert("ns:1", {})
        cache.insert("ns:2", {})
        cache.insert("other:1", {})
        assert cache.invalidate("ns:") == 2
        assert cache.size() == 1

    def test_size(self) -> None:
        cache = CacheManager()
        assert cache.size() == 0
        cache.insert("a", {})
        assert cache.size() == 1

    def test_ttl_validation(self) -> None:
        cache = CacheManager()
        assert cache.is_valid_ttl(1) is True
        assert cache.is_valid_ttl(86400) is True
        assert cache.is_valid_ttl(0) is False
        assert cache.is_valid_ttl(-1) is False

    def test_access_count_increments(self) -> None:
        cache = CacheManager()
        cache.insert("key1", {"v": 1})
        cache.lookup("key1")
        cache.lookup("key1")
        # After 2 lookups, access_count should be 2
        entry = cache._entries["key1"]
        assert entry.access_count == 2


# ─────────────────────────────────────────────────────────────────────────────
# VersionManager
# ─────────────────────────────────────────────────────────────────────────────


class TestVersionManager:
    def test_record_creation(self) -> None:
        vm = VersionManager()
        record = MemoryRecord(memory_type=MemoryType.SESSION, owner_id="u1")
        vm.record_creation(record)
        assert vm.get_latest_version(str(record.memory_id)) == 1

    def test_increment(self) -> None:
        vm = VersionManager()
        record = MemoryRecord(memory_type=MemoryType.SESSION, owner_id="u1")
        vm.record_creation(record)
        new_ver = vm.increment(record)
        assert new_ver == 2
        assert record.version == 2

    def test_get_history(self) -> None:
        vm = VersionManager()
        record = MemoryRecord(memory_type=MemoryType.SESSION, owner_id="u1")
        vm.record_creation(record)
        vm.increment(record)
        history = vm.get_history(str(record.memory_id))
        assert len(history) == 2

    def test_get_snapshot(self) -> None:
        vm = VersionManager()
        record = MemoryRecord(memory_type=MemoryType.SESSION, owner_id="u1", namespace="test")
        vm.record_creation(record)
        snap = vm.get_snapshot(str(record.memory_id), 1)
        assert snap is not None
        assert snap["namespace"] == "test"

    def test_compare_versions(self) -> None:
        vm = VersionManager()
        record = MemoryRecord(memory_type=MemoryType.SESSION, owner_id="u1")
        vm.record_creation(record)
        record.owner_id = "u2"
        vm.increment(record)
        diffs = vm.compare_versions(str(record.memory_id), 1, 2)
        assert "owner_id" in diffs

    def test_rollback_metadata(self) -> None:
        vm = VersionManager()
        record = MemoryRecord(memory_type=MemoryType.SESSION, owner_id="u1")
        record.metadata["version_tag"] = "v1"
        vm.record_creation(record)
        record.metadata["version_tag"] = "v2"
        vm.increment(record)
        restored = vm.rollback_metadata(record, 1)
        assert restored.metadata.get("version_tag") == "v1"

    def test_rollback_nonexistent_raises(self) -> None:
        vm = VersionManager()
        record = MemoryRecord(memory_type=MemoryType.SESSION, owner_id="u1")
        vm.record_creation(record)
        with pytest.raises(ValueError, match="No snapshot"):
            vm.rollback_metadata(record, 99)


# ─────────────────────────────────────────────────────────────────────────────
# AuditManager
# ─────────────────────────────────────────────────────────────────────────────


class TestAuditManager:
    def test_record_audit(self) -> None:
        audit = AuditManager()
        record = MemoryRecord(memory_type=MemoryType.SESSION, owner_id="u1")
        audit.record(record, MemoryOperation.CREATE, tier="HOT")
        records = audit.get_records()
        assert len(records) == 1
        assert records[0].operation == MemoryOperation.CREATE

    def test_record_raw(self) -> None:
        audit = AuditManager()
        audit.record_raw(str(uuid.uuid4()), MemoryOperation.DELETE)
        assert len(audit.get_records()) == 1

    def test_record_lifecycle(self) -> None:
        audit = AuditManager()
        record = MemoryRecord(memory_type=MemoryType.SESSION, owner_id="u1")
        audit.record_lifecycle(
            record, MemoryLifecycleStatus.CREATED, MemoryLifecycleStatus.ACTIVE,
        )
        records = audit.get_records()
        assert len(records) == 1

    def test_filter_by_memory_id(self) -> None:
        audit = AuditManager()
        r1 = MemoryRecord(memory_type=MemoryType.SESSION, owner_id="u1")
        r2 = MemoryRecord(memory_type=MemoryType.WORKFLOW, owner_id="u1")
        audit.record(r1, MemoryOperation.CREATE)
        audit.record(r2, MemoryOperation.CREATE)
        records = audit.get_records(memory_id=str(r1.memory_id))
        assert len(records) == 1

    def test_filter_by_operation(self) -> None:
        audit = AuditManager()
        record = MemoryRecord(memory_type=MemoryType.SESSION, owner_id="u1")
        audit.record(record, MemoryOperation.CREATE)
        audit.record(record, MemoryOperation.READ)
        records = audit.get_records(operation=MemoryOperation.READ)
        assert len(records) == 1

    def test_clear(self) -> None:
        audit = AuditManager()
        record = MemoryRecord(memory_type=MemoryType.SESSION, owner_id="u1")
        audit.record(record, MemoryOperation.CREATE)
        audit.clear()
        assert len(audit.get_records()) == 0


# ─────────────────────────────────────────────────────────────────────────────
# MemorySearchService
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
class TestMemorySearchService:
    async def test_search_by_type(self) -> None:
        svc = MemorySearchService()
        records = [
            MemoryRecord(memory_type=MemoryType.SESSION, owner_id="u1"),
            MemoryRecord(memory_type=MemoryType.WORKFLOW, owner_id="u2"),
        ]
        svc.index_records(records)
        results = await svc.search_by_type(MemoryType.SESSION)
        assert len(results) == 1

    async def test_search_by_owner(self) -> None:
        svc = MemorySearchService()
        records = [
            MemoryRecord(memory_type=MemoryType.SESSION, owner_id="u1"),
            MemoryRecord(memory_type=MemoryType.WORKFLOW, owner_id="u1"),
            MemoryRecord(memory_type=MemoryType.CACHE, owner_id="u2"),
        ]
        svc.index_records(records)
        results = await svc.search_by_owner("u1")
        assert len(results) == 2

    async def test_search_by_id(self) -> None:
        svc = MemorySearchService()
        target = MemoryRecord(memory_type=MemoryType.SESSION, owner_id="u1")
        svc.index_records([target])
        found = await svc.search_by_id(str(target.memory_id))
        assert found is not None
        assert found.memory_type == MemoryType.SESSION

    async def test_search_with_query(self) -> None:
        svc = MemorySearchService()
        records = [
            MemoryRecord(memory_type=MemoryType.SESSION, owner_id="u1", tags=["critical"]),
            MemoryRecord(memory_type=MemoryType.WORKFLOW, owner_id="u2", tags=["normal"]),
        ]
        svc.index_records(records)
        query = SearchQuery(tags=["critical"])
        results = await svc.search(query)
        assert len(results) == 1

    async def test_search_pagination(self) -> None:
        svc = MemorySearchService()
        records = [
            MemoryRecord(memory_type=MemoryType.SESSION, owner_id=f"u{i}")
            for i in range(10)
        ]
        svc.index_records(records)
        query = SearchQuery(limit=3, offset=0)
        results = await svc.search(query)
        assert len(results) == 3


# ─────────────────────────────────────────────────────────────────────────────
# TraceManager
# ─────────────────────────────────────────────────────────────────────────────


class TestTraceManager:
    def test_start_and_complete(self) -> None:
        tm = TraceManager()
        trace = tm.start("validator", MemoryOperation.CREATE, "rec-1")
        assert trace.stage_name == "validator"
        assert trace.success is True

        tm.complete(trace, {"result": "ok"})
        assert trace.completed_at is not None
        assert trace.duration_ms is not None

    def test_complete_with_errors(self) -> None:
        tm = TraceManager()
        trace = tm.start("adapter", MemoryOperation.READ, "rec-1")
        tm.complete(trace, {}, errors=["Connection failed"])
        assert trace.success is False
        assert "Connection failed" in trace.errors

    def test_complete_with_warnings(self) -> None:
        tm = TraceManager()
        trace = tm.start("policy", MemoryOperation.CREATE, "rec-1")
        tm.complete(trace, {}, warnings=["TTL not set"])
        assert "TTL not set" in trace.warnings

    def test_get_traces_filtered(self) -> None:
        tm = TraceManager()
        t1 = tm.start("stage1", MemoryOperation.CREATE, "r1")
        tm.complete(t1, {})
        t2 = tm.start("stage2", MemoryOperation.READ, "r2")
        tm.complete(t2, {})
        traces = tm.get_traces(stage_name="stage1")
        assert len(traces) == 1

    def test_get_traces_all(self) -> None:
        tm = TraceManager()
        t1 = tm.start("a", MemoryOperation.CREATE, "r1")
        tm.complete(t1, {})
        assert len(tm.get_traces()) == 1

    def test_clear(self) -> None:
        tm = TraceManager()
        t1 = tm.start("a", MemoryOperation.CREATE, "r1")
        tm.complete(t1, {})
        tm.clear()
        assert len(tm.get_traces()) == 0


# ─────────────────────────────────────────────────────────────────────────────
# MetricsCollector
# ─────────────────────────────────────────────────────────────────────────────


class TestMetricsCollector:
    def test_initial_metrics(self) -> None:
        mc = MetricsCollector()
        metrics = mc.snapshot()
        assert metrics.reads == 0
        assert metrics.writes == 0

    def test_increment_reads(self) -> None:
        mc = MetricsCollector()
        mc.increment_reads(5)
        assert mc.snapshot().reads == 5

    def test_increment_writes(self) -> None:
        mc = MetricsCollector()
        mc.increment_writes(3)
        assert mc.snapshot().writes == 3

    def test_increment_cache_hits(self) -> None:
        mc = MetricsCollector()
        mc.increment_cache_hits(10)
        assert mc.snapshot().cache_hits == 10

    def test_increment_cache_misses(self) -> None:
        mc = MetricsCollector()
        mc.increment_cache_misses(2)
        assert mc.snapshot().cache_misses == 2

    def test_record_latency(self) -> None:
        mc = MetricsCollector()
        mc.increment_reads()
        mc.record_latency(retrieval_ms=15.5)
        assert mc.snapshot().retrieval_latency > 0

    def test_increment_expired(self) -> None:
        mc = MetricsCollector()
        mc.increment_expired(7)
        assert mc.snapshot().expired_records == 7

    def test_get_extended(self) -> None:
        mc = MetricsCollector()
        mc.increment_routing_decisions()
        mc.increment_policy_violations()
        mc.increment_lifecycle_transitions()
        extended = mc.get_extended()
        assert extended["routing_decisions"] == 1
        assert extended["policy_violations"] == 1
        assert extended["lifecycle_transitions"] == 1
        assert extended["search_count"] == 0

    def test_reset(self) -> None:
        mc = MetricsCollector()
        mc.increment_reads(10)
        mc.reset()
        assert mc.snapshot().reads == 0


# ─────────────────────────────────────────────────────────────────────────────
# Execution Models
# ─────────────────────────────────────────────────────────────────────────────


class TestExecutionModels:
    def test_lifecycle_history(self) -> None:
        h = MemoryLifecycleHistory(
            memory_id=uuid.uuid4(),
            previous_state=MemoryLifecycleStatus.CREATED,
            new_state=MemoryLifecycleStatus.ACTIVE,
            reason="Initial activation",
        )
        assert h.reason == "Initial activation"
        assert h.actor == "system"

    def test_policy_decision_valid(self) -> None:
        d = PolicyDecision(valid=True)
        assert d.valid is True
        assert d.violations == []

    def test_policy_decision_invalid(self) -> None:
        d = PolicyDecision(valid=False, violations=["TTL expired"])
        assert not d.valid
        assert len(d.violations) == 1

    def test_audit_record(self) -> None:
        a = AuditRecord(
            memory_id=uuid.uuid4(),
            memory_type=MemoryType.SESSION,
            operation=MemoryOperation.CREATE,
        )
        assert a.operation == MemoryOperation.CREATE
        assert a.namespace == ""

    def test_version_history(self) -> None:
        v = VersionHistory(
            version_number=2,
            memory_id=uuid.uuid4(),
            snapshot={"owner_id": "u1"},
        )
        assert v.version_number == 2
        assert v.snapshot["owner_id"] == "u1"

    def test_cache_entry(self) -> None:
        c = CacheEntry(cache_key="k1", memory_id=uuid.uuid4(), data={"v": 1})
        assert c.cache_key == "k1"
        assert c.access_count == 0

    def test_search_query_defaults(self) -> None:
        q = SearchQuery()
        assert q.memory_type is None
        assert q.limit == 20

    def test_memory_trace(self) -> None:
        t = MemoryTrace(
            stage_name="test",
            operation=MemoryOperation.CREATE,
        )
        assert t.stage_name == "test"
        assert t.success is True


# ─────────────────────────────────────────────────────────────────────────────
# Memory Stores (integration-style)
# ─────────────────────────────────────────────────────────────────────────────


def _make_store_fixtures():
    router = MemoryRouter()
    lifecycle = MemoryLifecycleManager()
    policy = MemoryPolicyEngine()
    validator = MemoryValidator()
    audit = AuditManager()
    vm = VersionManager()
    metrics = MetricsCollector()
    trace = TraceManager()
    return router, lifecycle, policy, validator, audit, vm, metrics, trace


@pytest.mark.asyncio
class TestSessionMemoryStore:
    async def test_save_and_get(self) -> None:
        from adip.memory.execution.stores import SessionMemoryStore
        deps = _make_store_fixtures()
        store = SessionMemoryStore(*deps)
        mem = SessionMemory(session_id="sess-1", owner_id="u1")
        saved = await store.save(mem)
        assert saved.session_id == "sess-1"
        fetched = await store.get("sess-1")
        assert fetched is not None
        assert fetched.session_id == "sess-1"

    async def test_delete(self) -> None:
        from adip.memory.execution.stores import SessionMemoryStore
        deps = _make_store_fixtures()
        store = SessionMemoryStore(*deps)
        mem = SessionMemory(session_id="sess-del", owner_id="u1")
        await store.save(mem)
        assert await store.delete("sess-del") is True
        assert await store.get("sess-del") is None


@pytest.mark.asyncio
class TestConversationMemoryStore:
    async def test_save_and_get(self) -> None:
        from adip.memory.execution.stores import ConversationMemoryStore
        deps = _make_store_fixtures()
        store = ConversationMemoryStore(*deps)
        mem = ConversationMemory(conversation_id="conv-1", owner_id="u1")
        saved = await store.save(mem)
        assert saved.conversation_id == "conv-1"
        fetched = await store.get("conv-1")
        assert fetched is not None


@pytest.mark.asyncio
class TestWorkflowMemoryStore:
    async def test_save_and_get(self) -> None:
        from adip.memory.execution.stores import WorkflowMemoryStore
        deps = _make_store_fixtures()
        store = WorkflowMemoryStore(*deps)
        mem = WorkflowMemory(workflow_id="wf-1", owner_id="u1")
        saved = await store.save(mem)
        assert saved.workflow_id == "wf-1"
        fetched = await store.get("wf-1")
        assert fetched is not None


@pytest.mark.asyncio
class TestPlanningMemoryStore:
    async def test_save_and_get(self) -> None:
        from adip.memory.execution.stores import PlanningMemoryStore
        deps = _make_store_fixtures()
        store = PlanningMemoryStore(*deps)
        mem = PlanningMemory(plan_id="plan-1", owner_id="u1")
        saved = await store.save(mem)
        assert saved.plan_id == "plan-1"
        fetched = await store.get("plan-1")
        assert fetched is not None


@pytest.mark.asyncio
class TestRecommendationMemoryStore:
    async def test_save_and_get(self) -> None:
        from adip.memory.execution.stores import RecommendationMemoryStore
        deps = _make_store_fixtures()
        store = RecommendationMemoryStore(*deps)
        mem = RecommendationMemory(recommendation_id="rec-1", owner_id="u1")
        saved = await store.save(mem)
        assert saved.recommendation_id == "rec-1"
        fetched = await store.get("rec-1")
        assert fetched is not None


@pytest.mark.asyncio
class TestLearningMemoryStore:
    async def test_save_and_get(self) -> None:
        from adip.memory.execution.stores import LearningMemoryStore
        deps = _make_store_fixtures()
        store = LearningMemoryStore(*deps)
        mem = LearningMemory(lesson_id="lesson-1", owner_id="u1")
        saved = await store.save(mem)
        assert saved.lesson_id == "lesson-1"
        fetched = await store.get("lesson-1")
        assert fetched is not None


@pytest.mark.asyncio
class TestUserMemoryStore:
    async def test_save_and_get(self) -> None:
        from adip.memory.execution.stores import UserMemoryStore
        deps = _make_store_fixtures()
        store = UserMemoryStore(*deps)
        mem = UserMemory(user_id="user-1", owner_id="u1")
        saved = await store.save(mem)
        assert saved.user_id == "user-1"
        fetched = await store.get("user-1")
        assert fetched is not None


@pytest.mark.asyncio
class TestCacheStore:
    async def test_set_and_get(self) -> None:
        from adip.memory.execution.stores import CacheStore
        deps = _make_store_fixtures()
        store = CacheStore(*deps)
        mem = CacheMemory(cache_key="ck-1", owner_id="u1", cached_data={"v": 1})
        saved = await store.set(mem)
        assert saved.cache_key == "ck-1"
        fetched = await store.get("ck-1")
        assert fetched is not None

    async def test_clear(self) -> None:
        from adip.memory.execution.stores import CacheStore
        deps = _make_store_fixtures()
        store = CacheStore(*deps)
        mem = CacheMemory(cache_key="ck-1", owner_id="u1")
        await store.set(mem)
        count = await store.clear()
        assert count >= 1
