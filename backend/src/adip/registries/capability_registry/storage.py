"""Storage port and in-memory adapter for capabilities."""

from __future__ import annotations

import asyncio
import uuid
from typing import Protocol

from adip.registries.capability_registry.models import Capability


class CapabilityStorage(Protocol):
    """Persistence extension point consumed by the registry service."""

    async def add(self, capability: Capability) -> bool:
        """Store a capability, returning false when its ID already exists."""
        ...

    async def get(self, capability_id: uuid.UUID) -> Capability | None:
        """Return a capability by ID."""
        ...

    async def replace(self, capability: Capability) -> bool:
        """Replace a capability, returning false when it does not exist."""
        ...

    async def remove(self, capability_id: uuid.UUID) -> bool:
        """Remove a capability, returning whether it existed."""
        ...

    async def list_all(self) -> list[Capability]:
        """Return a snapshot of all capabilities."""
        ...


class InMemoryCapabilityStorage:
    """Concurrency-safe, process-local capability storage adapter."""

    def __init__(self) -> None:
        self._capabilities: dict[uuid.UUID, Capability] = {}
        self._lock = asyncio.Lock()

    async def add(self, capability: Capability) -> bool:
        """Store a capability if its ID is not already present."""
        async with self._lock:
            if capability.id in self._capabilities:
                return False
            self._capabilities[capability.id] = capability
            return True

    async def get(self, capability_id: uuid.UUID) -> Capability | None:
        """Return a capability by ID."""
        async with self._lock:
            return self._capabilities.get(capability_id)

    async def replace(self, capability: Capability) -> bool:
        """Replace an existing capability atomically."""
        async with self._lock:
            if capability.id not in self._capabilities:
                return False
            self._capabilities[capability.id] = capability
            return True

    async def remove(self, capability_id: uuid.UUID) -> bool:
        """Remove a capability by ID."""
        async with self._lock:
            return self._capabilities.pop(capability_id, None) is not None

    async def list_all(self) -> list[Capability]:
        """Return an isolated snapshot of current registry values."""
        async with self._lock:
            return list(self._capabilities.values())
