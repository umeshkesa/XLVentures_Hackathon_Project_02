"""Validation tests for Memory Manager events."""

from __future__ import annotations

import uuid

from adip.memory.contracts.events import (
    EVENT_VERSION,
    MemoryArchived,
    MemoryCached,
    MemoryCreated,
    MemoryDeleted,
    MemoryEvent,
    MemoryEvicted,
    MemoryExpired,
    MemoryRetrieved,
    MemoryUpdated,
)
from adip.memory.enums import MemoryOperation, MemoryType


class TestMemoryEvent:
    def test_base_event_defaults(self) -> None:
        event = MemoryEvent(
            memory_id=uuid.uuid4(),
            memory_type=MemoryType.SESSION,
            operation=MemoryOperation.CREATE,
        )
        assert event.memory_type == MemoryType.SESSION
        assert event.operation == MemoryOperation.CREATE
        assert event.correlation_id == ""
        assert event.payload == {}

    def test_event_id_unique(self) -> None:
        e1 = MemoryEvent(
            memory_id=uuid.uuid4(),
            memory_type=MemoryType.SESSION,
            operation=MemoryOperation.CREATE,
        )
        e2 = MemoryEvent(
            memory_id=uuid.uuid4(),
            memory_type=MemoryType.SESSION,
            operation=MemoryOperation.CREATE,
        )
        assert e1.event_id != e2.event_id


class TestMemoryCreated:
    def test_creation(self) -> None:
        mem_id = uuid.uuid4()
        event = MemoryCreated(
            memory_id=mem_id,
            memory_type=MemoryType.PLANNING,
            operation=MemoryOperation.CREATE,
        )
        assert event.memory_id == mem_id
        assert event.memory_type == MemoryType.PLANNING
        assert event.operation == MemoryOperation.CREATE

    def test_is_memory_event(self) -> None:
        assert issubclass(MemoryCreated, MemoryEvent)


class TestMemoryUpdated:
    def test_creation(self) -> None:
        event = MemoryUpdated(
            memory_id=uuid.uuid4(),
            memory_type=MemoryType.WORKFLOW,
            operation=MemoryOperation.UPDATE,
            previous_version=2,
        )
        assert event.previous_version == 2
        assert event.operation == MemoryOperation.UPDATE

    def test_default_previous_version(self) -> None:
        event = MemoryUpdated(
            memory_id=uuid.uuid4(),
            memory_type=MemoryType.WORKFLOW,
            operation=MemoryOperation.UPDATE,
        )
        assert event.previous_version == 0

    def test_is_memory_event(self) -> None:
        assert issubclass(MemoryUpdated, MemoryEvent)


class TestMemoryDeleted:
    def test_creation(self) -> None:
        event = MemoryDeleted(
            memory_id=uuid.uuid4(),
            memory_type=MemoryType.USER,
            operation=MemoryOperation.DELETE,
        )
        assert event.memory_type == MemoryType.USER

    def test_is_memory_event(self) -> None:
        assert issubclass(MemoryDeleted, MemoryEvent)


class TestMemoryExpired:
    def test_creation(self) -> None:
        event = MemoryExpired(
            memory_id=uuid.uuid4(),
            memory_type=MemoryType.CACHE,
            operation=MemoryOperation.DELETE,
            tier="HOT",
        )
        assert event.tier == "HOT"

    def test_is_memory_event(self) -> None:
        assert issubclass(MemoryExpired, MemoryEvent)


class TestMemoryRetrieved:
    def test_creation(self) -> None:
        event = MemoryRetrieved(
            memory_id=uuid.uuid4(),
            memory_type=MemoryType.SESSION,
            operation=MemoryOperation.READ,
            retrieval_latency_ms=15.3,
        )
        assert event.retrieval_latency_ms == 15.3

    def test_is_memory_event(self) -> None:
        assert issubclass(MemoryRetrieved, MemoryEvent)


class TestMemoryCached:
    def test_creation(self) -> None:
        event = MemoryCached(
            memory_id=uuid.uuid4(),
            memory_type=MemoryType.CACHE,
            operation=MemoryOperation.CREATE,
            ttl_seconds=300,
        )
        assert event.ttl_seconds == 300

    def test_is_memory_event(self) -> None:
        assert issubclass(MemoryCached, MemoryEvent)


class TestMemoryEvicted:
    def test_creation(self) -> None:
        event = MemoryEvicted(
            memory_id=uuid.uuid4(),
            memory_type=MemoryType.CACHE,
            operation=MemoryOperation.DELETE,
            tier="HOT",
            reason="TTL expired",
        )
        assert event.tier == "HOT"
        assert event.reason == "TTL expired"

    def test_is_memory_event(self) -> None:
        assert issubclass(MemoryEvicted, MemoryEvent)


class TestMemoryArchived:
    def test_creation(self) -> None:
        event = MemoryArchived(
            memory_id=uuid.uuid4(),
            memory_type=MemoryType.PLANNING,
            operation=MemoryOperation.ARCHIVE,
            source_tier="WARM",
        )
        assert event.source_tier == "WARM"

    def test_is_memory_event(self) -> None:
        assert issubclass(MemoryArchived, MemoryEvent)


class TestEventVersion:
    def test_event_version_constant(self) -> None:
        assert EVENT_VERSION == "1.0.0"

    def test_event_version_inherited(self) -> None:
        event = MemoryCreated(
            memory_id=uuid.uuid4(),
            memory_type=MemoryType.SESSION,
            operation=MemoryOperation.CREATE,
        )
        assert hasattr(event, "event_version") is False  # no event_version on MemoryEvent
