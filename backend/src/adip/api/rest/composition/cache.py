"""Composition Cache — placeholder interfaces for dashboard and summary caching.

No caching implementation. Only abstract interfaces for future use.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


class CompositionCache(ABC):
    """Abstract interface for composition cache storage.

    Implementations may use Redis, in-memory, or other backends.
    """

    @abstractmethod
    async def get(self, key: str) -> Any:
        """Get a cached value by key."""
        ...

    @abstractmethod
    async def set(self, key: str, value: Any, ttl_seconds: int = 300) -> None:
        """Set a cached value with TTL."""
        ...

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Delete a cached value by key."""
        ...

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if a key exists in cache."""
        ...


class DashboardCache(CompositionCache):
    """Placeholder cache for dashboard data."""

    async def get(self, key: str) -> Any:
        logger.debug("dashboard_cache.miss", key=key)
        return None

    async def set(self, key: str, value: Any, ttl_seconds: int = 300) -> None:
        logger.debug("dashboard_cache.set", key=key, ttl=ttl_seconds)

    async def delete(self, key: str) -> None:
        logger.debug("dashboard_cache.delete", key=key)

    async def exists(self, key: str) -> bool:
        return False


class SummaryCache(CompositionCache):
    """Placeholder cache for summary/overview data."""

    async def get(self, key: str) -> Any:
        logger.debug("summary_cache.miss", key=key)
        return None

    async def set(self, key: str, value: Any, ttl_seconds: int = 300) -> None:
        logger.debug("summary_cache.set", key=key, ttl=ttl_seconds)

    async def delete(self, key: str) -> None:
        logger.debug("summary_cache.delete", key=key)

    async def exists(self, key: str) -> bool:
        return False
