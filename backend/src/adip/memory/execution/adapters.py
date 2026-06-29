"""Placeholder storage adapters — no real database connectivity.

Each adapter returns deterministic placeholder responses suitable for
testing and pipeline development.  Future phases will replace these
with real Redis / PostgreSQL / ChromaDB implementations.
"""

from __future__ import annotations

from datetime import UTC, datetime

import structlog

from adip.memory.contracts.models import MemoryRecord
from adip.memory.enums import MemoryTier, MemoryType

log = structlog.get_logger(__name__)


class PlaceholderStorageAdapter:
    """Base placeholder with an in-memory dict for deterministic responses.

    All adapters inherit from this so they share the same storage API
    contract.
    """

    def __init__(self, tier: MemoryTier) -> None:
        self._tier = tier
        self._store: dict[str, MemoryRecord] = {}
        log.info("adapter.initialized", tier=tier.value)

    async def create(self, record: MemoryRecord) -> MemoryRecord:
        """Store a new record. Returns a copy with updated timestamps."""
        key = str(record.memory_id)
        self._store[key] = record.model_copy(deep=True)
        self._store[key].created_at = datetime.now(UTC)
        self._store[key].updated_at = datetime.now(UTC)
        log.debug("adapter.create", tier=self._tier.value, memory_id=key)
        return self._store[key].model_copy(deep=True)

    async def read(self, memory_id: str) -> MemoryRecord | None:
        """Retrieve a record by ID."""
        record = self._store.get(memory_id)
        if record is None:
            log.debug("adapter.read.miss", tier=self._tier.value, memory_id=memory_id)
            return None
        log.debug("adapter.read.hit", tier=self._tier.value, memory_id=memory_id)
        return record.model_copy(deep=True)

    async def update(self, record: MemoryRecord) -> MemoryRecord:
        """Replace an existing record."""
        key = str(record.memory_id)
        self._store[key] = record.model_copy(deep=True)
        self._store[key].updated_at = datetime.now(UTC)
        log.debug("adapter.update", tier=self._tier.value, memory_id=key)
        return self._store[key].model_copy(deep=True)

    async def delete(self, memory_id: str) -> bool:
        """Remove a record. Returns True if it existed."""
        existed = memory_id in self._store
        if existed:
            del self._store[memory_id]
        log.debug("adapter.delete", tier=self._tier.value, memory_id=memory_id, existed=existed)
        return existed

    async def search(
        self,
        memory_type: MemoryType | None = None,
        owner_id: str | None = None,
        namespace: str | None = None,
        tags: list[str] | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[MemoryRecord]:
        """Filter in-memory records by the given criteria."""
        results: list[MemoryRecord] = []
        for rec in self._store.values():
            if memory_type is not None and rec.memory_type != memory_type:
                continue
            if owner_id is not None and rec.owner_id != owner_id:
                continue
            if namespace is not None and rec.namespace != namespace:
                continue
            if tags:
                if not any(t in rec.tags for t in tags):
                    continue
            results.append(rec.model_copy(deep=True))
        sliced = results[offset:offset + limit]
        log.debug(
            "adapter.search",
            tier=self._tier.value,
            total_matches=len(results),
            returned=len(sliced),
        )
        return sliced

    async def archive(self, memory_id: str) -> MemoryRecord | None:
        """Mark a record as archived (placeholder)."""
        record = self._store.get(memory_id)
        if record is None:
            return None
        record.metadata["archived"] = True
        record.metadata["archived_at"] = datetime.now(UTC).isoformat()
        log.debug("adapter.archive", tier=self._tier.value, memory_id=memory_id)
        return record.model_copy(deep=True)

    async def restore(self, memory_id: str) -> MemoryRecord | None:
        """Restore a previously archived record (placeholder)."""
        record = self._store.get(memory_id)
        if record is None:
            return None
        record.metadata.pop("archived", None)
        record.metadata.pop("archived_at", None)
        log.debug("adapter.restore", tier=self._tier.value, memory_id=memory_id)
        return record.model_copy(deep=True)

    async def health(self) -> bool:
        """Placeholder health check — always returns True."""
        return True

    def clear(self) -> None:
        """Clear all stored records (for testing)."""
        self._store.clear()
        log.debug("adapter.clear", tier=self._tier.value)


class RedisAdapter(PlaceholderStorageAdapter):
    """Placeholder Redis (HOT tier) adapter."""

    def __init__(self) -> None:
        super().__init__(tier=MemoryTier.HOT)


class PostgresAdapter(PlaceholderStorageAdapter):
    """Placeholder PostgreSQL (WARM tier) adapter."""

    def __init__(self) -> None:
        super().__init__(tier=MemoryTier.WARM)


class ChromaAdapter(PlaceholderStorageAdapter):
    """Placeholder ChromaDB (COLD tier) adapter."""

    def __init__(self) -> None:
        super().__init__(tier=MemoryTier.COLD)
