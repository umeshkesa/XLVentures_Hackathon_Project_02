"""CacheManager — in-memory cache for frequently accessed records.

Supports lookup, insert, evict, invalidate, and TTL validation.
All operations are deterministic and storage-independent.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import structlog

from adip.memory.execution.models import CacheEntry

log = structlog.get_logger(__name__)


class CacheManager:
    """Manages an in-memory cache of memory records.

    Default capacity: 10 000 entries.  Oldest entries are evicted
    when capacity is exceeded.
    """

    def __init__(self, capacity: int = 10_000) -> None:
        self._capacity = capacity
        self._entries: dict[str, CacheEntry] = {}
        log.info("cache.initialized", capacity=capacity)

    # ── Public API ─────────────────────────────────────────────────────────

    def lookup(self, key: str) -> dict[str, Any] | None:
        """Retrieve data by cache key.  Returns None on miss or expiry."""
        entry = self._entries.get(key)
        if entry is None:
            log.debug("cache.miss", key=key)
            return None

        if entry.expires_at and entry.expires_at < datetime.now(UTC):
            del self._entries[key]
            log.debug("cache.expired", key=key)
            return None

        entry.access_count += 1
        log.debug("cache.hit", key=key, access_count=entry.access_count)
        return dict(entry.data)

    def insert(
        self,
        key: str,
        data: dict[str, Any],
        ttl_seconds: int | None = None,
    ) -> CacheEntry:
        """Insert or update a cache entry."""
        expires_at = None
        if ttl_seconds is not None:
            expires_at = datetime.now(UTC).replace(microsecond=0)  # stable base
            from datetime import timedelta
            expires_at = expires_at + timedelta(seconds=ttl_seconds)

        import uuid

        entry = CacheEntry(
            cache_key=key,
            memory_id=self._entries[key].memory_id if key in self._entries else uuid.uuid4(),
            data=data,
            expires_at=expires_at,
        )

        self._entries[key] = entry
        self._evict_if_needed()

        log.debug("cache.insert", key=key, ttl_seconds=ttl_seconds)
        return entry

    def evict(self, key: str) -> bool:
        """Remove a specific entry.  Returns True if it existed."""
        existed = key in self._entries
        if existed:
            del self._entries[key]
            log.debug("cache.evict", key=key)
        return existed

    def invalidate(self, namespace: str = "") -> int:
        """Remove all entries (or entries whose key starts with namespace)."""
        if not namespace:
            count = len(self._entries)
            self._entries.clear()
            log.debug("cache.invalidate.all", count=count)
            return count

        keys_to_remove = [k for k in self._entries if k.startswith(namespace)]
        for k in keys_to_remove:
            del self._entries[k]
        log.debug("cache.invalidate.namespace", namespace=namespace, count=len(keys_to_remove))
        return len(keys_to_remove)

    def size(self) -> int:
        """Return the number of entries currently in the cache."""
        return len(self._entries)

    def is_valid_ttl(self, ttl_seconds: int) -> bool:
        """Return True if the TTL value is acceptable."""
        return 1 <= ttl_seconds <= 86400 * 365  # 1 second to 1 year

    # ── Internal ───────────────────────────────────────────────────────────

    def _evict_if_needed(self) -> None:
        """Evict the oldest entries when over capacity."""
        while len(self._entries) > self._capacity:
            oldest_key = min(
                self._entries.keys(),
                key=lambda k: self._entries[k].created_at,
            )
            del self._entries[oldest_key]
            log.debug("cache.evict.oldest", key=oldest_key)
