"""Tests for MemoryCoordinator — central internal orchestrator."""

from __future__ import annotations

import uuid

import pytest

from adip.memory.contracts.models import (
    MemoryMetrics,
    MemoryRecord,
    SessionMemory,
    WorkflowMemory,
)
from adip.memory.enums import MemoryDomain, MemoryLifecycleStatus, MemoryTier, MemoryType
from adip.memory.orchestration.coordinator import MemoryCoordinator


@pytest.fixture
def coordinator() -> MemoryCoordinator:
    return MemoryCoordinator()


@pytest.fixture
def session_record() -> SessionMemory:
    return SessionMemory(
        session_id="sess-1",
        owner_id="user-1",
        state={"key": "value"},
    )


class TestMemoryCoordinatorCreate:
    async def test_create_session(self, coordinator: MemoryCoordinator, session_record: SessionMemory) -> None:
        result = await coordinator.create(session_record)
        assert result.memory_id == session_record.memory_id
        assert result.memory_type == MemoryType.SESSION
        assert result.memory_tier == MemoryTier.HOT
        assert result.memory_domain == MemoryDomain.SYSTEM
        assert result.metadata.get("lifecycle_status") == MemoryLifecycleStatus.ACTIVE.value

    async def test_create_with_domain(self, coordinator: MemoryCoordinator) -> None:
        record = SessionMemory(
            session_id="s1",
            owner_id="u1",
            memory_domain=MemoryDomain.PLANNER,
        )
        result = await coordinator.create(record)
        assert result.memory_domain == MemoryDomain.PLANNER

    async def test_create_invalid_raises(self, coordinator: MemoryCoordinator) -> None:
        record = MemoryRecord(memory_type=MemoryType.SESSION, owner_id="")
        with pytest.raises(ValueError, match="Memory validation failed"):
            await coordinator.create(record)

    async def test_create_records_pipeline_stages(self, coordinator: MemoryCoordinator, session_record: SessionMemory) -> None:
        await coordinator.create(session_record)
        stages = coordinator.get_pipeline_stages()
        stage_names = [s["stage"] for s in stages]
        assert "MemoryCoordinator" in stage_names
        assert "MemoryValidator" in stage_names
        assert "LifecycleManager" in stage_names
        assert "MemoryPolicyEngine" in stage_names
        assert "MemoryRouter" in stage_names
        assert "MemoryStore" in stage_names
        assert "StorageAdapter" in stage_names


class TestMemoryCoordinatorRead:
    async def test_read_existing(self, coordinator: MemoryCoordinator, session_record: SessionMemory) -> None:
        created = await coordinator.create(session_record)
        fetched = await coordinator.read(str(created.memory_id))
        assert fetched is not None
        assert fetched.memory_type == MemoryType.SESSION

    async def test_read_nonexistent(self, coordinator: MemoryCoordinator) -> None:
        fetched = await coordinator.read(str(uuid.uuid4()))
        assert fetched is None

    async def test_read_after_delete(self, coordinator: MemoryCoordinator, session_record: SessionMemory) -> None:
        created = await coordinator.create(session_record)
        await coordinator.delete(str(created.memory_id))
        fetched = await coordinator.read(str(created.memory_id))
        assert fetched is None


class TestMemoryCoordinatorUpdate:
    async def test_update_existing(self, coordinator: MemoryCoordinator, session_record: SessionMemory) -> None:
        created = await coordinator.create(session_record)
        created.metadata["updated"] = "yes"
        updated = await coordinator.update(created)
        assert str(updated.memory_id) == str(created.memory_id)
        assert updated.metadata.get("lifecycle_status") == MemoryLifecycleStatus.UPDATED.value

    async def test_update_nonexistent_raises(self, coordinator: MemoryCoordinator) -> None:
        record = MemoryRecord(memory_type=MemoryType.SESSION, owner_id="user-1")
        with pytest.raises(ValueError, match="not found for update"):
            await coordinator.update(record)


class TestMemoryCoordinatorDelete:
    async def test_delete_existing(self, coordinator: MemoryCoordinator, session_record: SessionMemory) -> None:
        created = await coordinator.create(session_record)
        deleted = await coordinator.delete(str(created.memory_id))
        assert deleted is True

    async def test_delete_nonexistent(self, coordinator: MemoryCoordinator) -> None:
        deleted = await coordinator.delete(str(uuid.uuid4()))
        assert deleted is False


class TestMemoryCoordinatorSearch:
    async def test_search_by_type(self, coordinator: MemoryCoordinator) -> None:
        await coordinator.create(SessionMemory(session_id="s1", owner_id="u1"))
        await coordinator.create(WorkflowMemory(workflow_id="w1", owner_id="u1"))
        results = await coordinator.search(memory_type=MemoryType.SESSION)
        assert len(results) == 1

    async def test_search_pagination(self, coordinator: MemoryCoordinator) -> None:
        for i in range(5):
            await coordinator.create(SessionMemory(session_id=f"s{i}", owner_id="u1"))
        page = await coordinator.search(limit=2, offset=0)
        assert len(page) == 2


class TestMemoryCoordinatorArchiveRestore:
    async def test_archive(self, coordinator: MemoryCoordinator, session_record: SessionMemory) -> None:
        created = await coordinator.create(session_record)
        archived = await coordinator.archive(str(created.memory_id))
        assert archived is not None

    async def test_archive_nonexistent(self, coordinator: MemoryCoordinator) -> None:
        archived = await coordinator.archive(str(uuid.uuid4()))
        assert archived is None

    async def test_restore(self, coordinator: MemoryCoordinator, session_record: SessionMemory) -> None:
        created = await coordinator.create(session_record)
        await coordinator.archive(str(created.memory_id))
        restored = await coordinator.restore(str(created.memory_id))
        assert restored is not None

    async def test_restore_nonexistent(self, coordinator: MemoryCoordinator) -> None:
        restored = await coordinator.restore(str(uuid.uuid4()))
        assert restored is None

    async def test_archive_tracks_metrics(self, coordinator: MemoryCoordinator, session_record: SessionMemory) -> None:
        created = await coordinator.create(session_record)
        await coordinator.archive(str(created.memory_id))
        agg = coordinator.get_aggregated_metrics()
        assert agg["archives_total"] >= 1

    async def test_archive_traces_recorded(self, coordinator: MemoryCoordinator, session_record: SessionMemory) -> None:
        created = await coordinator.create(session_record)
        await coordinator.archive(
            str(created.memory_id),
            correlation_id="corr-archive",
            session_id="sess-archive",
        )
        traces = coordinator.get_aggregated_traces(stage_name="coordinator.archive")
        archive_traces = [t for t in traces if t["stage_name"] == "coordinator.archive"]
        assert len(archive_traces) >= 1
        trace = archive_traces[0]
        assert trace["correlation_id"] == "corr-archive"
        assert trace["session_id"] == "sess-archive"
        assert trace["success"] is True

    async def test_restore_tracks_metrics(self, coordinator: MemoryCoordinator, session_record: SessionMemory) -> None:
        created = await coordinator.create(session_record)
        await coordinator.archive(str(created.memory_id))
        await coordinator.restore(str(created.memory_id))
        agg = coordinator.get_aggregated_metrics()
        assert agg["restores_total"] >= 1

    async def test_restore_traces_recorded(self, coordinator: MemoryCoordinator, session_record: SessionMemory) -> None:
        created = await coordinator.create(session_record)
        await coordinator.archive(str(created.memory_id))
        await coordinator.restore(
            str(created.memory_id),
            correlation_id="corr-restore",
            session_id="sess-restore",
        )
        traces = coordinator.get_aggregated_traces(stage_name="coordinator.restore")
        restore_traces = [t for t in traces if t["stage_name"] == "coordinator.restore"]
        assert len(restore_traces) >= 1
        trace = restore_traces[0]
        assert trace["correlation_id"] == "corr-restore"


class TestMemoryCoordinatorHealth:
    async def test_health(self, coordinator: MemoryCoordinator) -> None:
        health = await coordinator.health()
        assert health["coordinator_status"] == "HEALTHY"
        assert health["router_status"] == "HEALTHY"
        assert health["lifecycle_status"] == "HEALTHY"
        assert health["policy_status"] == "HEALTHY"
        assert health["cache_status"] == "HEALTHY"
        assert "HOT" in health["storage_status"]
        assert "WARM" in health["storage_status"]
        assert "COLD" in health["storage_status"]


class TestMemoryCoordinatorMetrics:
    async def test_initial_metrics(self, coordinator: MemoryCoordinator) -> None:
        metrics = coordinator.get_metrics()
        assert isinstance(metrics, MemoryMetrics)
        assert metrics.reads == 0
        assert metrics.writes == 0

    async def test_metrics_after_create(self, coordinator: MemoryCoordinator) -> None:
        await coordinator.create(SessionMemory(session_id="s1", owner_id="u1"))
        metrics = coordinator.get_metrics()
        assert metrics.writes >= 1

    async def test_aggregated_metrics(self, coordinator: MemoryCoordinator) -> None:
        await coordinator.create(SessionMemory(session_id="s1", owner_id="u1"))
        agg = coordinator.get_aggregated_metrics()
        assert agg["operations_total"] >= 1
        assert agg["writes_total"] >= 1
        assert "SYSTEM" in agg["operations_per_domain"]

    async def test_aggregated_metric_updates(self, coordinator: MemoryCoordinator) -> None:
        created = await coordinator.create(SessionMemory(session_id="s1", owner_id="u1"))
        created.metadata["x"] = "y"
        await coordinator.update(created)
        agg = coordinator.get_aggregated_metrics()
        assert agg["updates_total"] >= 1

    async def test_aggregated_metric_deletes(self, coordinator: MemoryCoordinator) -> None:
        created = await coordinator.create(SessionMemory(session_id="s1", owner_id="u1"))
        await coordinator.delete(str(created.memory_id))
        agg = coordinator.get_aggregated_metrics()
        assert agg["deletes_total"] >= 1


class TestMemoryCoordinatorClear:
    async def test_clear_removes_all(self, coordinator: MemoryCoordinator) -> None:
        await coordinator.create(SessionMemory(session_id="s1", owner_id="u1"))
        coordinator.clear()
        results = await coordinator.search()
        assert len(results) == 0
