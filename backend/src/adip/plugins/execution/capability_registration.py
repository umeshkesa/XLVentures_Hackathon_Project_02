"""CapabilityRegistration — manages plugin capability registration.

Supports register, unregister, update, and discover operations
for plugin capabilities.

Deterministic placeholder — no external registry integration.
"""

from __future__ import annotations

from datetime import UTC, datetime

import structlog

from adip.plugins.contracts.models import Plugin, PluginCapability
from adip.plugins.execution.models import CapabilityRecord

log = structlog.get_logger(__name__)


class CapabilityRegistration:
    """Manages capability registration lifecycle.

    Provides in-memory capability tracking without external
    registry or service integration.
    """

    def __init__(self) -> None:
        self._records: dict[str, CapabilityRecord] = {}

    def register(self, plugin: Plugin, capability: PluginCapability) -> CapabilityRecord:
        """Register a capability for a plugin.

        Creates a CapabilityRecord linking the capability to its
        owning plugin.
        """
        cap_id = str(capability.capability_id)
        log.info(
            "cap_registration.register",
            plugin=plugin.name,
            capability=capability.name,
        )

        record = CapabilityRecord(
            capability_id=capability.capability_id,
            plugin_id=plugin.plugin_id,
            name=capability.name,
            version=capability.version,
            category=capability.category,
            status="registered",
        )
        self._records[cap_id] = record
        return record

    def unregister(self, capability_id: str) -> bool:
        """Unregister a capability.

        Marks the capability as unregistered rather than removing it.
        """
        log.info("cap_registration.unregister", capability_id=capability_id)
        record = self._records.get(capability_id)
        if record is None:
            return False
        record.status = "unregistered"
        record.updated_at = datetime.now(UTC)
        return True

    def update(self, capability: PluginCapability) -> bool:
        """Update a registered capability's record.

        Refreshes the tracking record with the latest capability data.
        """
        cap_id = str(capability.capability_id)
        log.info("cap_registration.update", capability_id=cap_id)

        existing = self._records.get(cap_id)
        if existing is None:
            return False

        existing.name = capability.name
        existing.version = capability.version
        existing.category = capability.category
        existing.updated_at = datetime.now(UTC)
        return True

    def discover(self, plugin: Plugin) -> list[CapabilityRecord]:
        """Discover all registered capabilities for a plugin.

        Returns capability records owned by the given plugin.
        """
        plugin_id = str(plugin.plugin_id)
        log.info("cap_registration.discover", plugin=plugin.name)

        return [
            r for r in self._records.values()
            if str(r.plugin_id) == plugin_id and r.status == "registered"
        ]

    def get_capability(self, capability_id: str) -> CapabilityRecord | None:
        """Get a capability record by its identifier."""
        return self._records.get(capability_id)

    def list_capabilities(
        self,
        category: str | None = None,
        plugin_id: str | None = None,
        status: str | None = None,
    ) -> list[CapabilityRecord]:
        """List capability records, optionally filtered."""
        results = list(self._records.values())

        if category:
            results = [r for r in results if r.category == category]
        if plugin_id:
            results = [r for r in results if str(r.plugin_id) == plugin_id]
        if status:
            results = [r for r in results if r.status == status]

        return results

    def count(self) -> int:
        """Return the total number of capability records."""
        return len(self._records)

    def count_by_plugin(self, plugin_id: str) -> int:
        """Return the number of capabilities registered for a plugin."""
        return sum(1 for r in self._records.values() if str(r.plugin_id) == plugin_id)

    def clear(self) -> int:
        """Clear all capability records. Returns the number cleared."""
        count = len(self._records)
        self._records.clear()
        return count
