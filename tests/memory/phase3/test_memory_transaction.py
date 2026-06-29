"""Tests for MemoryTransaction model."""

from __future__ import annotations

from uuid import UUID

from adip.memory.orchestration.transaction import MemoryTransaction


class TestMemoryTransaction:
    def test_default_creation(self) -> None:
        tx = MemoryTransaction(session_id="session-1")
        assert isinstance(tx.transaction_id, UUID)
        assert tx.session_id == "session-1"
        assert tx.status == "PENDING"
        assert tx.operations == []
        assert tx.rollback_metadata == {}
        assert tx.completed_at is None

    def test_complete_committed(self) -> None:
        tx = MemoryTransaction(session_id="session-1")
        tx.complete("COMMITTED")
        assert tx.status == "COMMITTED"
        assert tx.completed_at is not None

    def test_complete_failed(self) -> None:
        tx = MemoryTransaction(session_id="session-1")
        tx.complete("FAILED")
        assert tx.status == "FAILED"

    def test_default_complete_status(self) -> None:
        tx = MemoryTransaction(session_id="session-1")
        tx.complete()
        assert tx.status == "COMMITTED"

    def test_serialization(self) -> None:
        tx = MemoryTransaction(session_id="session-1", operations=[{"op": "create"}])
        data = tx.model_dump()
        assert data["status"] == "PENDING"
        assert data["session_id"] == "session-1"
        assert len(data["operations"]) == 1
