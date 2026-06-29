"""Abstract interfaces for the Memory Manager.

All interfaces follow dependency inversion — consumers depend on
abstractions, not concrete implementations.

Architecture:
    MemoryManager  →  MemoryRouter  →  StorageAdapter
                                         ├── RedisAdapter (hot)
                                         ├── PostgresAdapter (warm)
                                         └── ChromaAdapter (cold)

    MemoryService is the enterprise facade for external callers.
    MemoryStore interfaces are specialised by memory type
    (SessionMemoryStore, ConversationMemoryStore, etc.).
"""

from __future__ import annotations

import abc

from adip.memory.contracts.models import (
    CacheMemory,
    ConversationMemory,
    LearningMemory,
    MemoryContext,
    MemoryMetrics,
    MemoryPolicy,
    MemoryRecord,
    PlanningMemory,
    RecommendationMemory,
    SessionMemory,
    UserMemory,
    WorkflowMemory,
)
from adip.memory.enums import MemoryTier, MemoryType

# ─────────────────────────────────────────────────────────────────────────────
# Storage Adapter Contracts
# ─────────────────────────────────────────────────────────────────────────────


class StorageAdapter(abc.ABC):
    """Abstract interface for a storage backend.

    Every storage tier (Redis, PostgreSQL, ChromaDB) implements this
    adapter so the Memory Router can interact with them uniformly.
    """

    @abc.abstractmethod
    async def write(self, record: MemoryRecord) -> MemoryRecord:
        """Persist a memory record."""
        ...

    @abc.abstractmethod
    async def read(self, memory_id: str) -> MemoryRecord | None:
        """Retrieve a memory record by its identifier."""
        ...

    @abc.abstractmethod
    async def delete(self, memory_id: str) -> bool:
        """Delete a memory record. Returns True if found and deleted."""
        ...

    @abc.abstractmethod
    async def search(
        self,
        memory_type: MemoryType | None = None,
        owner_id: str | None = None,
        namespace: str | None = None,
        tags: list[str] | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[MemoryRecord]:
        """Search for records matching the given filters."""
        ...

    @abc.abstractmethod
    async def health(self) -> bool:
        """Return True if the storage backend is reachable and healthy."""
        ...


class RedisAdapter(StorageAdapter):
    """Contract for Redis (HOT tier) storage.

    Future implementation uses Redis for low-latency, ephemeral
    storage with built-in TTL support.
    """


class PostgresAdapter(StorageAdapter):
    """Contract for PostgreSQL (WARM tier) storage.

    Future implementation uses PostgreSQL for durable, relational
    storage with ACID guarantees.
    """


class ChromaAdapter(StorageAdapter):
    """Contract for ChromaDB (COLD tier) storage.

    Future implementation uses ChromaDB for vector-based storage
    and semantic search over archived records.
    """


# ─────────────────────────────────────────────────────────────────────────────
# Memory Router
# ─────────────────────────────────────────────────────────────────────────────


class MemoryRouter(abc.ABC):
    """Routes memory operations to the appropriate storage tier.

    Decides whether a record should go to HOT (Redis), WARM
    (PostgreSQL), or COLD (ChromaDB) based on memory type,
    policy, and current tier load.
    """

    @abc.abstractmethod
    async def route_write(
        self,
        record: MemoryRecord,
        policy: MemoryPolicy | None = None,
    ) -> StorageAdapter:
        """Determine which storage adapter should handle a write."""
        ...

    @abc.abstractmethod
    async def route_read(self, memory_id: str) -> StorageAdapter:
        """Determine which storage adapter holds a given record."""
        ...

    @abc.abstractmethod
    async def get_tier_for_type(
        self,
        memory_type: MemoryType,
    ) -> MemoryTier:
        """Return the default storage tier for a memory type."""
        ...


# ─────────────────────────────────────────────────────────────────────────────
# Memory Store Interfaces (one per memory type)
# ─────────────────────────────────────────────────────────────────────────────


class SessionMemoryStore(abc.ABC):
    """Store interface for ``SessionMemory`` records."""

    @abc.abstractmethod
    async def save(self, memory: SessionMemory) -> SessionMemory:
        ...

    @abc.abstractmethod
    async def get(self, session_id: str) -> SessionMemory | None:
        ...

    @abc.abstractmethod
    async def delete(self, session_id: str) -> bool:
        ...


class ConversationMemoryStore(abc.ABC):
    """Store interface for ``ConversationMemory`` records."""

    @abc.abstractmethod
    async def save(self, memory: ConversationMemory) -> ConversationMemory:
        ...

    @abc.abstractmethod
    async def get(self, conversation_id: str) -> ConversationMemory | None:
        ...

    @abc.abstractmethod
    async def delete(self, conversation_id: str) -> bool:
        ...


class WorkflowMemoryStore(abc.ABC):
    """Store interface for ``WorkflowMemory`` records."""

    @abc.abstractmethod
    async def save(self, memory: WorkflowMemory) -> WorkflowMemory:
        ...

    @abc.abstractmethod
    async def get(self, workflow_id: str) -> WorkflowMemory | None:
        ...

    @abc.abstractmethod
    async def delete(self, workflow_id: str) -> bool:
        ...


class PlanningMemoryStore(abc.ABC):
    """Store interface for ``PlanningMemory`` records."""

    @abc.abstractmethod
    async def save(self, memory: PlanningMemory) -> PlanningMemory:
        ...

    @abc.abstractmethod
    async def get(self, plan_id: str) -> PlanningMemory | None:
        ...

    @abc.abstractmethod
    async def delete(self, plan_id: str) -> bool:
        ...


class RecommendationMemoryStore(abc.ABC):
    """Store interface for ``RecommendationMemory`` records."""

    @abc.abstractmethod
    async def save(self, memory: RecommendationMemory) -> RecommendationMemory:
        ...

    @abc.abstractmethod
    async def get(
        self, recommendation_id: str,
    ) -> RecommendationMemory | None:
        ...

    @abc.abstractmethod
    async def delete(self, recommendation_id: str) -> bool:
        ...


class LearningMemoryStore(abc.ABC):
    """Store interface for ``LearningMemory`` records."""

    @abc.abstractmethod
    async def save(self, memory: LearningMemory) -> LearningMemory:
        ...

    @abc.abstractmethod
    async def get(self, lesson_id: str) -> LearningMemory | None:
        ...

    @abc.abstractmethod
    async def delete(self, lesson_id: str) -> bool:
        ...


class UserMemoryStore(abc.ABC):
    """Store interface for ``UserMemory`` records."""

    @abc.abstractmethod
    async def save(self, memory: UserMemory) -> UserMemory:
        ...

    @abc.abstractmethod
    async def get(self, user_id: str) -> UserMemory | None:
        ...

    @abc.abstractmethod
    async def delete(self, user_id: str) -> bool:
        ...


class CacheStore(abc.ABC):
    """Store interface for ``CacheMemory`` records."""

    @abc.abstractmethod
    async def set(self, memory: CacheMemory) -> CacheMemory:
        ...

    @abc.abstractmethod
    async def get(self, cache_key: str) -> CacheMemory | None:
        ...

    @abc.abstractmethod
    async def delete(self, cache_key: str) -> bool:
        ...

    @abc.abstractmethod
    async def clear(self) -> int:
        """Clear all cache entries. Returns number of cleared entries."""
        ...


# ─────────────────────────────────────────────────────────────────────────────
# MemoryManager — core orchestrator
# ─────────────────────────────────────────────────────────────────────────────


class MemoryManager(abc.ABC):
    """Central orchestrator for all memory operations.

    Every ADIP module that needs to read or write memory goes
    through this interface.  The MemoryManager:
      1. Validates the operation against MemoryPolicy
      2. Routes to the correct storage tier via MemoryRouter
      3. Records events for audit and observability
      4. Updates MemoryMetrics
    """

    @abc.abstractmethod
    async def create(self, record: MemoryRecord) -> MemoryRecord:
        """Store a new memory record."""
        ...

    @abc.abstractmethod
    async def read(self, memory_id: str) -> MemoryRecord | None:
        """Retrieve a memory record by ID."""
        ...

    @abc.abstractmethod
    async def update(self, record: MemoryRecord) -> MemoryRecord:
        """Update an existing memory record."""
        ...

    @abc.abstractmethod
    async def delete(self, memory_id: str) -> bool:
        """Delete a memory record."""
        ...

    @abc.abstractmethod
    async def search(
        self,
        memory_type: MemoryType | None = None,
        owner_id: str | None = None,
        namespace: str | None = None,
        tags: list[str] | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[MemoryRecord]:
        """Search for memory records matching the given filters."""
        ...

    @abc.abstractmethod
    async def get_context(self, **identifiers: str) -> MemoryContext:
        """Retrieve all memory for a given scope as a MemoryContext.

        Keyword arguments identify the scope (e.g. session_id,
        conversation_id, workflow_id, user_id).
        """
        ...

    @abc.abstractmethod
    async def get_metrics(self) -> MemoryMetrics:
        """Return aggregated MemoryManager metrics."""
        ...


# ─────────────────────────────────────────────────────────────────────────────
# MemoryService — enterprise facade
# ─────────────────────────────────────────────────────────────────────────────


class MemoryService(abc.ABC):
    """Enterprise facade for memory operations.

    Provides validation, authorisation, audit, and observability
    wrapping around the ``MemoryManager``.  External modules (API
    layer, other managers) interact with this facade rather than
    with MemoryManager directly.
    """

    @abc.abstractmethod
    async def store(self, record: MemoryRecord) -> MemoryRecord:
        """Validate, authorise, audit, and store a memory record."""
        ...

    @abc.abstractmethod
    async def retrieve(self, memory_id: str) -> MemoryRecord | None:
        """Retrieve a memory record with authorisation and audit."""
        ...

    @abc.abstractmethod
    async def remove(self, memory_id: str) -> bool:
        """Delete a memory record with authorisation and audit."""
        ...

    @abc.abstractmethod
    async def find(
        self,
        memory_type: MemoryType | None = None,
        owner_id: str | None = None,
        namespace: str | None = None,
        tags: list[str] | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[MemoryRecord]:
        """Search for memory records with authorisation."""
        ...

    @abc.abstractmethod
    async def context(
        self,
        **identifiers: str,
    ) -> MemoryContext:
        """Retrieve the aggregated memory context for a scope."""
        ...
