"""RegistryManager — lightweight internal facade for registry operations.

Delegates all operations to RegistryCoordinator. Contains no business
logic — only delegation and structured logging.
"""

from __future__ import annotations

import structlog

from adip.registry.contracts.models import (
    RegistryDecision,
    RegistryEntry,
    RegistryFilter,
    RegistryHealth,
    RegistryMetrics,
    RegistrySearchResult,
)
from adip.registry.enums import RegistryLifecycleStatus, RegistryScope, RegistryType
from adip.registry.orchestration.coordinator import RegistryCoordinator

log = structlog.get_logger(__name__)


class RegistryManager:
    """Lightweight internal facade over RegistryCoordinator.

    All CRUD, search, lifecycle, health, and metrics operations
    delegate directly to the coordinator. No business logic lives here.
    """

    def __init__(self, coordinator: RegistryCoordinator | None = None) -> None:
        self.coordinator = coordinator or RegistryCoordinator()

    # ── Registration ────────────────────────────────────────────────

    def create_entry(
        self,
        entry: RegistryEntry,
        performed_by: str = "",
        correlation_id: str = "",
    ) -> RegistryDecision:
        """Register a new entry in the registry."""
        log.info("registry_manager.create_entry", name=entry.name)
        return self.coordinator.register_entry(
            entry,
            performed_by=performed_by,
            correlation_id=correlation_id,
        )

    # ── Read / Lookup ───────────────────────────────────────────────

    def read_entry(
        self,
        entry_id: str,
        correlation_id: str = "",
    ) -> RegistryEntry | None:
        """Retrieve a registry entry by its ID."""
        log.info("registry_manager.read_entry", entry_id=entry_id)
        return self.coordinator.get_entry(entry_id, correlation_id=correlation_id)

    # ── Update ──────────────────────────────────────────────────────

    def update_entry(
        self,
        entry: RegistryEntry,
        performed_by: str = "",
        correlation_id: str = "",
    ) -> RegistryDecision:
        """Update an existing registry entry."""
        log.info("registry_manager.update_entry", name=entry.name)
        return self.coordinator.update_entry(
            entry,
            performed_by=performed_by,
            correlation_id=correlation_id,
        )

    # ── Delete ──────────────────────────────────────────────────────

    def delete_entry(
        self,
        entry_id: str,
        performed_by: str = "",
        correlation_id: str = "",
    ) -> RegistryDecision:
        """Delete a registry entry."""
        log.info("registry_manager.delete_entry", entry_id=entry_id)
        return self.coordinator.delete_entry(
            entry_id,
            performed_by=performed_by,
            correlation_id=correlation_id,
        )

    # ── Search ──────────────────────────────────────────────────────

    def search_entries(
        self,
        query: str = "",
        registry_type: RegistryType | None = None,
        scope: RegistryScope | None = None,
        status: RegistryLifecycleStatus | None = None,
        tags: list[str] | None = None,
        namespace: str = "",
        limit: int = 20,
        offset: int = 0,
        correlation_id: str = "",
    ) -> list[RegistrySearchResult]:
        """Search for entries matching the given criteria."""
        log.info("registry_manager.search_entries", query=query)
        filter = RegistryFilter(
            query=query,
            registry_type=registry_type,
            scope=scope,
            status=status,
            tags=tags or [],
            namespace=namespace,
            limit=limit,
            offset=offset,
        )
        return self.coordinator.search(filter, correlation_id=correlation_id)

    # ── Lifecycle operations ────────────────────────────────────────

    def activate_entry(
        self,
        entry_id: str,
        performed_by: str = "",
        correlation_id: str = "",
    ) -> RegistryDecision:
        """Activate a registry entry."""
        log.info("registry_manager.activate_entry", entry_id=entry_id)
        return self.coordinator.activate_entry(
            entry_id,
            performed_by=performed_by,
            correlation_id=correlation_id,
        )

    def suspend_entry(
        self,
        entry_id: str,
        performed_by: str = "",
        correlation_id: str = "",
    ) -> RegistryDecision:
        """Suspend a registry entry."""
        log.info("registry_manager.suspend_entry", entry_id=entry_id)
        return self.coordinator.suspend_entry(
            entry_id,
            performed_by=performed_by,
            correlation_id=correlation_id,
        )

    def deprecate_entry(
        self,
        entry_id: str,
        performed_by: str = "",
        reason: str = "",
        correlation_id: str = "",
    ) -> RegistryDecision:
        """Deprecate a registry entry."""
        log.info("registry_manager.deprecate_entry", entry_id=entry_id)
        return self.coordinator.deprecate_entry(
            entry_id,
            performed_by=performed_by,
            reason=reason,
            correlation_id=correlation_id,
        )

    # ── Health & Metrics ────────────────────────────────────────────

    def get_health(self) -> RegistryHealth:
        """Return the current health status."""
        log.info("registry_manager.get_health")
        return self.coordinator.health()

    def get_metrics(self) -> RegistryMetrics:
        """Return aggregated metrics."""
        log.info("registry_manager.get_metrics")
        return self.coordinator.metrics()

    # ── Sub-component access ────────────────────────────────────────

    @property
    def coordinator(self) -> RegistryCoordinator:
        return self._coordinator

    @coordinator.setter
    def coordinator(self, value: RegistryCoordinator) -> None:
        self._coordinator = value
