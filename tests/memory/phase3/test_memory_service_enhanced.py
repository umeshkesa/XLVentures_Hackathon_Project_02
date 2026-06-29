"""Tests for enhanced DefaultMemoryService with sessions and correlation IDs."""

from __future__ import annotations

from typing import Any

import pytest

from adip.memory.contracts.models import MemoryContext, MemoryRecord, SessionMemory
from adip.memory.services.manager import DefaultMemoryManager
from adip.memory.services.service import DefaultMemoryService


class TestMemoryServiceSessions:
    def test_service_creates_sessions(self) -> None:
        mgr = DefaultMemoryManager()
        svc = DefaultMemoryService(manager=mgr)
        sessions = svc.get_sessions()
        assert sessions == []

    async def test_store_creates_session(self) -> None:
        mgr = DefaultMemoryManager()
        svc = DefaultMemoryService(manager=mgr)
        record = SessionMemory(session_id="s1", owner_id="u1")
        await svc.store(record)
        sessions = svc.get_sessions()
        assert len(sessions) == 1
        session = sessions[0]
        assert session.owner_id == "u1"
        assert "store" in session.operations
        assert len(session.created_records) == 1

    async def test_retrieve_creates_session(self) -> None:
        mgr = DefaultMemoryManager()
        svc = DefaultMemoryService(manager=mgr)
        record = SessionMemory(session_id="s1", owner_id="u1")
        stored = await svc.store(record)
        await svc.retrieve(str(stored.memory_id))
        sessions = svc.get_sessions()
        assert len(sessions) == 2

    async def test_remove_creates_session(self) -> None:
        mgr = DefaultMemoryManager()
        svc = DefaultMemoryService(manager=mgr)
        record = SessionMemory(session_id="s1", owner_id="u1")
        stored = await svc.store(record)
        await svc.remove(str(stored.memory_id))
        sessions = svc.get_sessions()
        assert len(sessions) == 2

    async def test_find_creates_session(self) -> None:
        mgr = DefaultMemoryManager()
        svc = DefaultMemoryService(manager=mgr)
        await svc.find()
        assert len(svc.get_sessions()) == 1

    def test_get_session_by_id(self) -> None:
        mgr = DefaultMemoryManager()
        svc = DefaultMemoryService(manager=mgr)

        # Access internal to verify
        from adip.memory.orchestration.session import MemorySession
        session = MemorySession(owner_id="test-user")
        svc._sessions.append(session)

        found = svc.get_session(str(session.session_id))
        assert found is not None
        assert found.owner_id == "test-user"

    def test_get_session_nonexistent(self) -> None:
        mgr = DefaultMemoryManager()
        svc = DefaultMemoryService(manager=mgr)
        assert svc.get_session("nonexistent") is None

    async def test_sessions_completed(self) -> None:
        mgr = DefaultMemoryManager()
        svc = DefaultMemoryService(manager=mgr)
        record = SessionMemory(session_id="s1", owner_id="u1")
        await svc.store(record)
        session = svc.get_sessions()[0]
        assert session.completed_at is not None

    async def test_full_lifecycle_with_sessions(self) -> None:
        mgr = DefaultMemoryManager()
        svc = DefaultMemoryService(manager=mgr)

        record = SessionMemory(session_id="s1", owner_id="u1", state={"count": 0})
        stored = await svc.store(record)
        fetched = await svc.retrieve(str(stored.memory_id))
        assert fetched is not None

        removed = await svc.remove(str(stored.memory_id))
        assert removed is True

        sessions = svc.get_sessions()
        assert len(sessions) == 3  # store, retrieve, remove

        # Verify retrieve session recorded the operation
        retrieve_session = sessions[1]
        assert "retrieve" in retrieve_session.operations

        # Verify remove session recorded the operation
        remove_session = sessions[2]
        assert "remove" in remove_session.operations


class TestMemoryServiceErrorLogging:
    async def test_store_raises_on_manager_error(self) -> None:
        class FailingManager(DefaultMemoryManager):
            async def create(self, record: MemoryRecord) -> MemoryRecord:
                raise ValueError("Manager failure")

        svc = DefaultMemoryService(manager=FailingManager())
        record = SessionMemory(session_id="s1", owner_id="u1")
        with pytest.raises(ValueError, match="Manager failure"):
            await svc.store(record)

    async def test_retrieve_raises_on_manager_error(self) -> None:
        class FailingManager(DefaultMemoryManager):
            async def read(self, memory_id: str) -> MemoryRecord | None:
                raise RuntimeError("Manager read failure")

        svc = DefaultMemoryService(manager=FailingManager())
        with pytest.raises(RuntimeError, match="Manager read failure"):
            await svc.retrieve("nonexistent")

    async def test_remove_raises_on_manager_error(self) -> None:
        class FailingManager(DefaultMemoryManager):
            async def delete(self, memory_id: str) -> bool:
                raise RuntimeError("Manager delete failure")

        svc = DefaultMemoryService(manager=FailingManager())
        with pytest.raises(RuntimeError, match="Manager delete failure"):
            await svc.remove("nonexistent")

    async def test_find_raises_on_manager_error(self) -> None:
        class FailingManager(DefaultMemoryManager):
            async def search(self, **kwargs: Any) -> list[MemoryRecord]:
                raise RuntimeError("Manager search failure")

        svc = DefaultMemoryService(manager=FailingManager())
        with pytest.raises(RuntimeError, match="Manager search failure"):
            await svc.find()

    async def test_context_raises_on_manager_error(self) -> None:
        class FailingManager(DefaultMemoryManager):
            async def get_context(self, **identifiers: str) -> MemoryContext:
                raise RuntimeError("Manager context failure")

        svc = DefaultMemoryService(manager=FailingManager())
        with pytest.raises(RuntimeError, match="Manager context failure"):
            await svc.context(session_id="s1")
