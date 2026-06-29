"""Standalone service for registering and discovering capabilities."""

from __future__ import annotations

import uuid
from collections.abc import Iterable

from adip.registries.capability_registry.exceptions import (
    CapabilityAlreadyRegisteredError,
    CapabilityNotFoundError,
)
from adip.registries.capability_registry.models import (
    Capability,
    CapabilityQuery,
    CapabilityUpdate,
)
from adip.registries.capability_registry.storage import CapabilityStorage


class CapabilityRegistry:
    """Manage and match domain-neutral capability metadata."""

    def __init__(self, storage: CapabilityStorage) -> None:
        self._storage = storage

    async def register(self, capability: Capability) -> Capability:
        """Register a capability and reject duplicate stable IDs."""
        if not await self._storage.add(capability):
            raise CapabilityAlreadyRegisteredError(capability.id)
        return capability

    async def unregister(self, capability_id: uuid.UUID) -> bool:
        """Unregister a capability, returning whether it existed."""
        return await self._storage.remove(capability_id)

    async def update(
        self,
        capability_id: uuid.UUID,
        changes: CapabilityUpdate,
    ) -> Capability:
        """Replace supplied fields while preserving the capability ID."""
        current = await self._storage.get(capability_id)
        if current is None:
            raise CapabilityNotFoundError(capability_id)
        values = changes.model_dump(exclude_none=True)
        updated = current.model_copy(update=values) if values else current
        if not await self._storage.replace(updated):
            raise CapabilityNotFoundError(capability_id)
        return updated

    async def lookup(self, capability_id: uuid.UUID) -> Capability | None:
        """Look up a capability by stable ID."""
        return await self._storage.get(capability_id)

    async def list(self, *, offset: int = 0, limit: int | None = None) -> list[Capability]:
        """List capabilities in deterministic priority/name order."""
        if offset < 0:
            raise ValueError("offset must be greater than or equal to 0")
        if limit is not None and limit < 1:
            raise ValueError("limit must be greater than or equal to 1")
        capabilities = self._sort(await self._storage.list_all())
        end = offset + limit if limit is not None else None
        return capabilities[offset:end]

    async def search(self, query: CapabilityQuery) -> list[Capability]:
        """Return capabilities matching every supplied metadata constraint."""
        capabilities = await self._storage.list_all()
        return self._sort(
            capability for capability in capabilities if self._matches(capability, query)
        )

    @staticmethod
    def _matches(capability: Capability, query: CapabilityQuery) -> bool:
        if query.category is not None and capability.category != query.category:
            return False
        if not query.tags.issubset(capability.tags):
            return False
        if not query.inputs.issubset(capability.inputs):
            return False
        if not query.outputs.issubset(capability.outputs):
            return False
        if query.text is not None:
            searchable = " ".join(
                (
                    capability.name,
                    capability.description,
                    capability.category,
                    *sorted(capability.tags),
                    *sorted(capability.inputs),
                    *sorted(capability.outputs),
                )
            ).casefold()
            if query.text not in searchable:
                return False
        return True

    @staticmethod
    def _sort(capabilities: Iterable[Capability]) -> list[Capability]:
        return sorted(
            capabilities,
            key=lambda item: (-item.priority, item.name.casefold(), str(item.id)),
        )
