"""KnowledgeCache — synchronous in-memory cache for KnowledgeContext.

Implements the KnowledgeCache interface with TTL support and
deterministic placeholder behaviour.
"""

from __future__ import annotations

import structlog

from adip.knowledge.contracts.models import KnowledgeContext

log = structlog.get_logger(__name__)


class KnowledgeCache:
    """In-memory cache for KnowledgeContext objects."""

    def __init__(self) -> None:
        self._store: dict[str, KnowledgeContext] = {}
        self._ttls: dict[str, int] = {}

    def get(self, cache_key: str) -> KnowledgeContext | None:
        """Retrieve a cached KnowledgeContext by key."""
        if cache_key not in self._store:
            return None
        log.info("cache.get", key=cache_key)
        return self._store[cache_key]

    def set(self, cache_key: str, context: KnowledgeContext, ttl_seconds: int = 300) -> None:
        """Cache a KnowledgeContext with an optional TTL."""
        log.info("cache.set", key=cache_key, ttl=ttl_seconds)
        self._store[cache_key] = context
        self._ttls[cache_key] = ttl_seconds

    def invalidate(self, cache_key: str) -> bool:
        """Invalidate a single cache entry."""
        existed = cache_key in self._store
        if existed:
            del self._store[cache_key]
            self._ttls.pop(cache_key, None)
            log.info("cache.invalidate", key=cache_key)
        return existed

    def clear(self) -> int:
        """Clear all cache entries. Returns the number cleared."""
        count = len(self._store)
        self._store.clear()
        self._ttls.clear()
        log.info("cache.clear", cleared=count)
        return count

    def size(self) -> int:
        """Return the number of cached entries."""
        return len(self._store)
