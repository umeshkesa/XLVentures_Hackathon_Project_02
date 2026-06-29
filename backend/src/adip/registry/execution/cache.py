"""RegistryCache — placeholder cache for registry entries and metadata.

Supports caching entries, search results, versions, and metadata
with configurable TTL.
"""

from __future__ import annotations

import time
from typing import Any

import structlog

from adip.registry.contracts.models import RegistryEntry, RegistryMetadata, RegistrySearchResult
from adip.registry.execution.models import VersionRecord

log = structlog.get_logger(__name__)


class _CacheItem:
    """Internal cache item with TTL tracking."""

    def __init__(self, value: Any, ttl_seconds: int) -> None:
        self.value = value
        self.expires_at = time.time() + ttl_seconds

    def is_expired(self) -> bool:
        return time.time() > self.expires_at


class RegistryCache:
    """Placeholder cache for registry data.

    Caches entries, search results, versions, and metadata.
    All cache stores are in-memory dictionaries with TTL support.
    """

    def __init__(self) -> None:
        self._entries: dict[str, _CacheItem] = {}
        self._search_results: dict[str, _CacheItem] = {}
        self._versions: dict[str, _CacheItem] = {}
        self._metadata: dict[str, _CacheItem] = {}
        self._hits: int = 0
        self._misses: int = 0
        self._sets: int = 0

    # ── Entry cache ───────────────────────────────────────────────

    def get_entry(self, entry_id: str) -> RegistryEntry | None:
        """Retrieve a cached entry by ID."""
        item = self._entries.get(entry_id)
        if item is None or item.is_expired():
            if item is None:
                self._misses += 1
            else:
                del self._entries[entry_id]
                self._misses += 1
            return None
        self._hits += 1
        return item.value

    def set_entry(self, entry: RegistryEntry, ttl_seconds: int = 300) -> None:
        """Cache an entry with a TTL."""
        self._entries[str(entry.entry_id)] = _CacheItem(entry, ttl_seconds)
        self._sets += 1

    def invalidate_entry(self, entry_id: str) -> bool:
        """Invalidate a cached entry."""
        return self._entries.pop(entry_id, None) is not None

    # ── Search result cache ───────────────────────────────────────

    def get_search_results(self, cache_key: str) -> list[RegistrySearchResult] | None:
        """Retrieve cached search results by key."""
        item = self._search_results.get(cache_key)
        if item is None or item.is_expired():
            if item is None:
                self._misses += 1
            else:
                del self._search_results[cache_key]
                self._misses += 1
            return None
        self._hits += 1
        return item.value

    def set_search_results(self, cache_key: str, results: list[RegistrySearchResult], ttl_seconds: int = 60) -> None:
        """Cache search results with a TTL."""
        self._search_results[cache_key] = _CacheItem(results, ttl_seconds)
        self._sets += 1

    # ── Version cache ─────────────────────────────────────────────

    def get_version(self, cache_key: str) -> VersionRecord | None:
        """Retrieve a cached version by key."""
        item = self._versions.get(cache_key)
        if item is None or item.is_expired():
            if item is None:
                self._misses += 1
            else:
                del self._versions[cache_key]
                self._misses += 1
            return None
        self._hits += 1
        return item.value

    def set_version(self, cache_key: str, version: VersionRecord, ttl_seconds: int = 600) -> None:
        """Cache a version with a TTL."""
        self._versions[cache_key] = _CacheItem(version, ttl_seconds)
        self._sets += 1

    # ── Metadata cache ────────────────────────────────────────────

    def get_metadata(self, cache_key: str) -> RegistryMetadata | None:
        """Retrieve cached metadata by key."""
        item = self._metadata.get(cache_key)
        if item is None or item.is_expired():
            if item is None:
                self._misses += 1
            else:
                del self._metadata[cache_key]
                self._misses += 1
            return None
        self._hits += 1
        return item.value

    def set_metadata(self, cache_key: str, metadata: RegistryMetadata, ttl_seconds: int = 300) -> None:
        """Cache metadata with a TTL."""
        self._metadata[cache_key] = _CacheItem(metadata, ttl_seconds)
        self._sets += 1

    # ── Stats & maintenance ───────────────────────────────────────

    def cache_hits(self) -> int:
        return self._hits

    def cache_misses(self) -> int:
        return self._misses

    def clear(self) -> int:
        """Clear all cached items. Returns total count."""
        total = (
            len(self._entries)
            + len(self._search_results)
            + len(self._versions)
            + len(self._metadata)
        )
        self._entries.clear()
        self._search_results.clear()
        self._versions.clear()
        self._metadata.clear()
        self._hits = 0
        self._misses = 0
        self._sets = 0
        return total

    def size(self) -> int:
        """Return total number of cached items (excluding expired)."""
        count = 0
        for store in [self._entries, self._search_results, self._versions, self._metadata]:
            count += sum(1 for item in store.values() if not item.is_expired())
        return count
