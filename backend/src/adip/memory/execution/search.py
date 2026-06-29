"""MemorySearchService — placeholder search over memory records.

Supports filtering by Memory ID, Owner, Namespace, Tags, Memory Type,
Lifecycle Status, and Version.  Delegates to storage adapters.
"""

from __future__ import annotations

import structlog

from adip.memory.contracts.models import MemoryRecord
from adip.memory.enums import MemoryType
from adip.memory.execution.models import SearchQuery

log = structlog.get_logger(__name__)


class MemorySearchService:
    """Placeholder search service for memory records.

    Currently returns deterministic results from the underlying
    storage adapters.  Future phases will add full-text and
    vector search capabilities.
    """

    def __init__(self) -> None:
        self._results: list[MemoryRecord] = []

    async def search(self, query: SearchQuery) -> list[MemoryRecord]:
        """Execute a search and return matching records.

        This is a placeholder that returns whatever records have been
        pre-loaded via ``index_records``.
        """
        results = list(self._results)
        if query.memory_type:
            results = [r for r in results if r.memory_type == query.memory_type]
        if query.owner_id:
            results = [r for r in results if r.owner_id == query.owner_id]
        if query.namespace:
            results = [r for r in results if r.namespace == query.namespace]
        if query.tags:
            results = [
                r for r in results
                if any(t in r.tags for t in query.tags)
            ]
        if query.lifecycle_status:
            results = [
                r for r in results
                if r.metadata.get("lifecycle_status") == query.lifecycle_status.value
            ]

        sliced = results[query.offset:query.offset + query.limit]
        log.debug(
            "search.executed",
            total_matches=len(results),
            returned=len(sliced),
        )
        return sliced

    async def search_by_id(self, memory_id: str) -> MemoryRecord | None:
        """Search for a single record by its ID."""
        for r in self._results:
            if str(r.memory_id) == memory_id:
                return r
        return None

    async def search_by_owner(
        self,
        owner_id: str,
        limit: int = 20,
        offset: int = 0,
    ) -> list[MemoryRecord]:
        """Search for records belonging to an owner."""
        return await self.search(
            SearchQuery(owner_id=owner_id, limit=limit, offset=offset),
        )

    async def search_by_type(
        self,
        memory_type: MemoryType,
        limit: int = 20,
        offset: int = 0,
    ) -> list[MemoryRecord]:
        """Search for records of a specific memory type."""
        return await self.search(
            SearchQuery(memory_type=memory_type, limit=limit, offset=offset),
        )

    def index_records(self, records: list[MemoryRecord]) -> None:
        """Load records into the search index (for testing)."""
        self._results = list(records)
        log.debug("search.indexed", count=len(records))
