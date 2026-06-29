"""Tests for MemorySession model."""

from __future__ import annotations

from uuid import UUID

from adip.memory.enums import MemoryDomain
from adip.memory.orchestration.session import MemorySession


class TestMemorySession:
    def test_default_creation(self) -> None:
        session = MemorySession()
        assert isinstance(session.session_id, UUID)
        assert session.owner_id == ""
        assert session.memory_domain == MemoryDomain.SYSTEM
        assert session.started_at is not None
        assert session.completed_at is None
        assert session.operations == []
        assert session.created_records == []
        assert session.updated_records == []
        assert session.deleted_records == []
        assert session.policy_used == ""
        assert session.statistics == {}

    def test_complete_sets_timestamp(self) -> None:
        session = MemorySession()
        assert session.completed_at is None
        session.complete()
        assert session.completed_at is not None

    def test_record_operation_create(self) -> None:
        session = MemorySession()
        session.record_operation("store", "mem-1")
        assert "store" in session.operations
        assert "mem-1" in session.created_records

    def test_record_operation_delete(self) -> None:
        session = MemorySession()
        session.record_operation("remove", "mem-2")
        assert "remove" in session.operations
        assert "mem-2" in session.deleted_records

    def test_record_operation_update(self) -> None:
        session = MemorySession()
        session.record_operation("update", "mem-3")
        assert "update" in session.operations
        assert "mem-3" in session.updated_records

    def test_record_operation_no_duplicate_ids(self) -> None:
        session = MemorySession()
        session.record_operation("store", "mem-1")
        session.record_operation("delete", "mem-1")
        assert "mem-1" in session.created_records
        assert "mem-1" not in session.deleted_records  # already in created, not re-added

    def test_record_operation_without_id(self) -> None:
        session = MemorySession()
        session.record_operation("find")
        assert "find" in session.operations
        assert session.created_records == []
        assert session.deleted_records == []

    def test_custom_domain(self) -> None:
        session = MemorySession(owner_id="user-1", memory_domain=MemoryDomain.PLANNER)
        assert session.owner_id == "user-1"
        assert session.memory_domain == MemoryDomain.PLANNER

    def test_serialization(self) -> None:
        session = MemorySession(owner_id="u1")
        data = session.model_dump()
        assert data["owner_id"] == "u1"
        assert "session_id" in data
