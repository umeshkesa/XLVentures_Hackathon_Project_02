"""Memory Manager events — recorded during memory operations."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import UUID4, BaseModel, Field

from adip.memory.enums import MemoryLifecycleStatus, MemoryOperation, MemoryType

EVENT_VERSION: str = "1.0.0"


class MemoryEvent(BaseModel):
    """Base event with standard enterprise fields."""
    event_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique event identifier",
    )
    memory_id: UUID4 = Field(
        description="The memory record this event relates to",
    )
    memory_type: MemoryType = Field(
        description="Category of the memory record",
    )
    operation: MemoryOperation = Field(
        description="The memory operation that triggered this event",
    )
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="When the event occurred",
    )
    correlation_id: str = Field(
        default="",
        description="Correlation ID for tracing across services",
    )
    payload: dict[str, Any] = Field(
        default_factory=dict,
        description="Event-specific data",
    )


class MemoryCreated(MemoryEvent):
    """Emitted when a new memory record is created."""


class MemoryActivated(MemoryEvent):
    """Emitted when a memory record transitions to ACTIVE."""


class MemoryUpdated(MemoryEvent):
    """Emitted when an existing memory record is updated."""
    previous_version: int = Field(
        default=0,
        ge=0,
        description="The version number before the update",
    )


class MemoryDeleted(MemoryEvent):
    """Emitted when a memory record is deleted."""


class MemoryExpired(MemoryEvent):
    """Emitted when a memory record expires and is evicted."""
    tier: str = Field(
        default="",
        description="The storage tier the record was in",
    )


class MemoryRetrieved(MemoryEvent):
    """Emitted when a memory record is retrieved (read)."""
    retrieval_latency_ms: float = Field(
        default=0.0,
        ge=0.0,
        description="Time taken to retrieve the record in milliseconds",
    )


class MemoryCached(MemoryEvent):
    """Emitted when a record is written to the cache tier."""
    ttl_seconds: int | None = Field(
        default=None,
        ge=1,
        description="TTL assigned to the cached record",
    )


class MemoryEvicted(MemoryEvent):
    """Emitted when a record is evicted from a storage tier."""
    tier: str = Field(
        default="",
        description="The storage tier the record was evicted from",
    )
    reason: str = Field(
        default="",
        description="Why the record was evicted (e.g. TTL, capacity)",
    )


class MemoryArchived(MemoryEvent):
    """Emitted when a record is moved to cold (archive) storage."""
    source_tier: str = Field(
        default="",
        description="The storage tier the record was moved from",
    )


class MemoryRestored(MemoryEvent):
    """Emitted when a record is restored from cold storage."""
    target_tier: str = Field(
        default="",
        description="The storage tier the record was restored to",
    )


class MemoryLifecycleChanged(MemoryEvent):
    """Emitted when a record's lifecycle state changes."""
    old_status: MemoryLifecycleStatus = Field(
        description="The lifecycle status before the change",
    )
    new_status: MemoryLifecycleStatus = Field(
        description="The lifecycle status after the change",
    )
    reason: str = Field(
        default="",
        description="Why the lifecycle state changed",
    )
