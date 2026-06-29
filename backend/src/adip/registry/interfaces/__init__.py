"""Abstract interfaces for the Registry Framework.

All interfaces follow dependency inversion — consumers depend on
abstractions, not concrete implementations.

Architecture:
    RegistryService  →  RegistryManager  →  RegistryCoordinator
                                             ├── RegistryValidator
                                             ├── RegistrySearcher
                                             ├── RegistryVersionManager
                                             ├── RegistryLifecycleManager
                                             └── RegistryHealthChecker

BaseRegistry serves as the abstract foundation that all specialised
registries (Capability, Agent, Tool, Rule, Plugin, Workflow) inherit
from.

RegistryService is the enterprise facade for external callers.
RegistryManager is the internal orchestrator.
RegistryCoordinator coordinates all sub-components.

PHASE 3.5 — INTERFACE FREEZE
These interfaces are now frozen and stable. No new abstract methods
will be added. No existing abstract methods will be removed or have
their signatures changed. The AI Decision Layer and all downstream
consumers can safely depend on these contracts without risk of
breaking changes.

Interface stability guarantees:
    • No new abstract methods added.
    • No existing methods removed.
    • No method signatures changed.
    • No new required abstract interfaces added to the hierarchy.
"""

from __future__ import annotations

import abc
from typing import Any, ClassVar

from adip.registry.contracts.models import (
    RegistryDecision,
    RegistryEntry,
    RegistryFilter,
    RegistryHealth,
    RegistryMetadata,
    RegistryMetrics,
    RegistryNamespace,
    RegistrySearchResult,
    RegistryVersion,
)
from adip.registry.enums import (
    RegistryLifecycleStatus,
    RegistryScope,
    RegistryType,
)

# ─────────────────────────────────────────────────────────────────────────────
# Interface Freeze Marker
# ─────────────────────────────────────────────────────────────────────────────

# Set to True once Phase 3.5 finalises the interfaces.
# Downstream code may check this at import time to verify compatibility.
REGISTRY_INTERFACES_FROZEN: bool = True


# ─────────────────────────────────────────────────────────────────────────────
# BaseRegistry — abstract foundation for all registries
# ─────────────────────────────────────────────────────────────────────────────


class BaseRegistry(abc.ABC):
    """Abstract foundation for all ADIP registries.

    Every specialised registry (Capability, Agent, Tool, Rule, Plugin,
    Workflow, Model, Connector, Policy) inherits from this base and
    implements the core contract.

    Responsibilities:
        • Registration — add new entries to the registry.
        • Deregistration — remove entries from the registry.
        • Lookup — retrieve entries by identifier or name.
        • Search — query entries by filter criteria.
        • Filtering — apply structured filters to entry listings.
        • Version Management — track and retrieve entry versions.
        • Health — report the operational health of the registry.
        • Metrics — report aggregated operational metrics.

    This interface is frozen as of Phase 3.5.
    """

    __frozen__: ClassVar[bool] = True

    @abc.abstractmethod
    async def register(self, entry: RegistryEntry) -> RegistryEntry:
        """Register a new entry in the registry."""
        ...

    @abc.abstractmethod
    async def deregister(self, entry_id: str) -> bool:
        """Deregister and remove an entry from the registry."""
        ...

    @abc.abstractmethod
    async def lookup(self, entry_id: str) -> RegistryEntry | None:
        """Look up an entry by its unique identifier."""
        ...

    @abc.abstractmethod
    async def lookup_by_name(self, name: str, namespace: str = "default") -> RegistryEntry | None:
        """Look up an entry by its name within a namespace."""
        ...

    @abc.abstractmethod
    async def search(self, filter: RegistryFilter) -> list[RegistrySearchResult]:
        """Search for entries matching the given filter criteria."""
        ...

    @abc.abstractmethod
    async def list_entries(
        self,
        registry_type: RegistryType | None = None,
        scope: RegistryScope | None = None,
        status: RegistryLifecycleStatus | None = None,
        namespace: str = "",
        limit: int = 20,
        offset: int = 0,
    ) -> list[RegistryEntry]:
        """List entries with optional filtering."""
        ...

    @abc.abstractmethod
    async def get_version_history(self, entry_id: str) -> list[RegistryVersion]:
        """Retrieve the version history for an entry."""
        ...

    @abc.abstractmethod
    async def get_version(self, entry_id: str, version: str) -> RegistryVersion | None:
        """Retrieve a specific version of an entry."""
        ...

    @abc.abstractmethod
    async def health(self) -> RegistryHealth:
        """Return the current health status of the registry."""
        ...

    @abc.abstractmethod
    async def metrics(self) -> RegistryMetrics:
        """Return aggregated metrics for the registry."""
        ...


# ─────────────────────────────────────────────────────────────────────────────
# RegistryService — enterprise facade (ONLY public API)
# ─────────────────────────────────────────────────────────────────────────────


class RegistryService(abc.ABC):
    """Enterprise facade for registry operations.

    Provides validation, authorisation, audit, and observability
    wrapping around the RegistryManager. External modules interact
    with this facade rather than with RegistryManager directly.

    This interface is frozen as of Phase 3.5.
    """

    __frozen__: ClassVar[bool] = True

    @abc.abstractmethod
    async def register_entry(self, entry: RegistryEntry) -> RegistryEntry:
        """Validate, authorise, and register a new entry."""
        ...

    @abc.abstractmethod
    async def get_entry(self, entry_id: str) -> RegistryEntry | None:
        """Retrieve a registry entry by its identifier."""
        ...

    @abc.abstractmethod
    async def update_entry(self, entry: RegistryEntry) -> RegistryEntry:
        """Update an existing entry with authorisation."""
        ...

    @abc.abstractmethod
    async def delete_entry(self, entry_id: str) -> bool:
        """Delete a registry entry with authorisation and audit."""
        ...

    @abc.abstractmethod
    async def search_entries(self, filter: RegistryFilter) -> list[RegistrySearchResult]:
        """Search for entries matching the given filter criteria."""
        ...

    @abc.abstractmethod
    async def activate_entry(self, entry_id: str) -> RegistryEntry:
        """Activate a registry entry (transition to ACTIVE status)."""
        ...

    @abc.abstractmethod
    async def suspend_entry(self, entry_id: str) -> RegistryEntry:
        """Suspend a registry entry (transition to SUSPENDED status)."""
        ...

    @abc.abstractmethod
    async def deprecate_entry(self, entry_id: str, reason: str = "") -> RegistryEntry:
        """Deprecate a registry entry (transition to DEPRECATED status)."""
        ...

    @abc.abstractmethod
    async def health(self) -> RegistryHealth:
        """Return the current health status of the registry platform."""
        ...

    @abc.abstractmethod
    async def get_metrics(self) -> RegistryMetrics:
        """Return aggregated registry platform metrics."""
        ...


# ─────────────────────────────────────────────────────────────────────────────
# RegistryManager — internal orchestrator
# ─────────────────────────────────────────────────────────────────────────────


class RegistryManager(abc.ABC):
    """Internal orchestrator for all registry operations.

    Every ADIP module that needs registry operations goes through
    this interface. The RegistryManager:
      1. Validates the operation
      2. Delegates to RegistryCoordinator for orchestration
      3. Records events for audit and observability

    This interface is frozen as of Phase 3.5.
    """

    __frozen__: ClassVar[bool] = True

    @abc.abstractmethod
    async def create_entry(self, entry: RegistryEntry) -> RegistryEntry:
        """Store a new registry entry."""
        ...

    @abc.abstractmethod
    async def read_entry(self, entry_id: str) -> RegistryEntry | None:
        """Retrieve a registry entry by ID."""
        ...

    @abc.abstractmethod
    async def update_entry(self, entry: RegistryEntry) -> RegistryEntry:
        """Update an existing registry entry."""
        ...

    @abc.abstractmethod
    async def delete_entry(self, entry_id: str) -> bool:
        """Delete a registry entry."""
        ...

    @abc.abstractmethod
    async def search_entries(
        self,
        query: str = "",
        registry_type: RegistryType | None = None,
        scope: RegistryScope | None = None,
        status: RegistryLifecycleStatus | None = None,
        tags: list[str] | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[RegistrySearchResult]:
        """Search for entries matching the given filters."""
        ...

    @abc.abstractmethod
    async def activate_entry(self, entry_id: str) -> RegistryEntry:
        """Activate a registry entry (transition to ACTIVE status)."""
        ...

    @abc.abstractmethod
    async def suspend_entry(self, entry_id: str) -> RegistryEntry:
        """Suspend a registry entry (transition to SUSPENDED status)."""
        ...

    @abc.abstractmethod
    async def deprecate_entry(self, entry_id: str, reason: str = "") -> RegistryEntry:
        """Deprecate a registry entry (transition to DEPRECATED status)."""
        ...

    @abc.abstractmethod
    async def get_health(self) -> RegistryHealth:
        """Return the current health status."""
        ...

    @abc.abstractmethod
    async def get_metrics(self) -> RegistryMetrics:
        """Return aggregated metrics."""
        ...


# ─────────────────────────────────────────────────────────────────────────────
# RegistryCoordinator — sub-component orchestrator
# ─────────────────────────────────────────────────────────────────────────────


class RegistryCoordinator(abc.ABC):
    """Sub-component orchestrator for registry operations.

    Coordinates RegistryValidator, RegistrySearcher,
    RegistryVersionManager, RegistryLifecycleManager, and
    RegistryHealthChecker. Contains orchestration only —
    no business logic.

    This interface is frozen as of Phase 3.5.
    """

    __frozen__: ClassVar[bool] = True

    @abc.abstractmethod
    async def register_entry(self, entry: RegistryEntry) -> RegistryEntry:
        """Orchestrate the full entry registration pipeline."""
        ...

    @abc.abstractmethod
    async def get_entry(self, entry_id: str) -> RegistryEntry | None:
        """Retrieve a registry entry by ID."""
        ...

    @abc.abstractmethod
    async def update_entry(self, entry: RegistryEntry) -> RegistryEntry:
        """Update an existing registry entry."""
        ...

    @abc.abstractmethod
    async def delete_entry(self, entry_id: str) -> bool:
        """Delete a registry entry."""
        ...

    @abc.abstractmethod
    async def search(self, filter: RegistryFilter) -> list[RegistrySearchResult]:
        """Search for entries matching the given filter."""
        ...

    @abc.abstractmethod
    async def activate_entry(self, entry_id: str) -> RegistryEntry:
        """Activate a registry entry."""
        ...

    @abc.abstractmethod
    async def suspend_entry(self, entry_id: str) -> RegistryEntry:
        """Suspend a registry entry."""
        ...

    @abc.abstractmethod
    async def deprecate_entry(self, entry_id: str, reason: str = "") -> RegistryEntry:
        """Deprecate a registry entry."""
        ...

    @abc.abstractmethod
    async def health(self) -> RegistryHealth:
        """Return health status of all sub-components."""
        ...

    @abc.abstractmethod
    async def metrics(self) -> RegistryMetrics:
        """Return aggregated metrics from all sub-components."""
        ...


# ─────────────────────────────────────────────────────────────────────────────
# RegistryValidator
# ─────────────────────────────────────────────────────────────────────────────


class RegistryValidator(abc.ABC):
    """Validates registry entries and operations for correctness.

    Ensures entries have valid metadata, namespaces are properly
    configured, versions follow semantic versioning, lifecycle
    transitions are valid, and scopes are within permitted ranges.
    This interface is frozen as of Phase 3.5.
    """

    __frozen__: ClassVar[bool] = True

    @abc.abstractmethod
    async def validate_entry(self, entry: RegistryEntry) -> list[str]:
        """Validate a registry entry. Returns list of violations."""
        ...

    @abc.abstractmethod
    async def validate_metadata(self, metadata: RegistryMetadata) -> list[str]:
        """Validate registry metadata. Returns list of violations."""
        ...

    @abc.abstractmethod
    async def validate_namespace(self, namespace: RegistryNamespace) -> list[str]:
        """Validate a registry namespace. Returns list of violations."""
        ...

    @abc.abstractmethod
    async def validate_version(self, version: str) -> list[str]:
        """Validate a version string (semver). Returns list of violations."""
        ...

    @abc.abstractmethod
    async def validate_lifecycle_transition(
        self,
        current_status: RegistryLifecycleStatus,
        new_status: RegistryLifecycleStatus,
    ) -> list[str]:
        """Validate a lifecycle status transition. Returns list of violations."""
        ...

    @abc.abstractmethod
    async def validate_scope(self, scope: RegistryScope, entry: RegistryEntry) -> list[str]:
        """Validate a scope assignment for an entry. Returns list of violations."""
        ...


# ─────────────────────────────────────────────────────────────────────────────
# RegistrySearcher
# ─────────────────────────────────────────────────────────────────────────────


class RegistrySearcher(abc.ABC):
    """Searches the registry for entries matching criteria.

    Supports free-text search, filtered queries, and paginated
    result sets. Specialised searchers can be plugged in for
    registry-specific search behaviour.

    This interface is frozen as of Phase 3.5.
    """

    __frozen__: ClassVar[bool] = True

    @abc.abstractmethod
    async def search(self, filter: RegistryFilter) -> list[RegistrySearchResult]:
        """Execute a search against the registry."""
        ...

    @abc.abstractmethod
    async def search_by_name(self, name: str, namespace: str = "default") -> list[RegistrySearchResult]:
        """Search entries by name within a namespace."""
        ...

    @abc.abstractmethod
    async def search_by_tags(self, tags: list[str]) -> list[RegistrySearchResult]:
        """Search entries by tags (entries matching any tag)."""
        ...

    @abc.abstractmethod
    async def count(self, filter: RegistryFilter) -> int:
        """Count entries matching the given filter."""
        ...


# ─────────────────────────────────────────────────────────────────────────────
# RegistryVersionManager
# ─────────────────────────────────────────────────────────────────────────────


class RegistryVersionManager(abc.ABC):
    """Manages version history for registry entries.

    Tracks all versions of an entry, supports retrieving specific
    versions, comparing versions, and listing version history.

    This interface is frozen as of Phase 3.5.
    """

    __frozen__: ClassVar[bool] = True

    @abc.abstractmethod
    async def create_version(self, entry: RegistryEntry, release_notes: str = "") -> RegistryVersion:
        """Create a new version record for an entry."""
        ...

    @abc.abstractmethod
    async def get_version(self, entry_id: str, version: str) -> RegistryVersion | None:
        """Retrieve a specific version of an entry."""
        ...

    @abc.abstractmethod
    async def get_version_history(self, entry_id: str) -> list[RegistryVersion]:
        """Retrieve the version history for an entry."""
        ...

    @abc.abstractmethod
    async def compare_versions(
        self,
        entry_id: str,
        version_a: str,
        version_b: str,
    ) -> dict[str, Any]:
        """Compare two versions of an entry. Returns diff."""
        ...

    @abc.abstractmethod
    async def rollback(self, entry_id: str, version: str) -> RegistryEntry:
        """Rollback an entry to a previous version."""
        ...


# ─────────────────────────────────────────────────────────────────────────────
# RegistryLifecycleManager
# ─────────────────────────────────────────────────────────────────────────────


class RegistryLifecycleManager(abc.ABC):
    """Manages the lifecycle state machine for registry entries.

    Handles status transitions, transition validation, and history
    tracking for the RegistryLifecycleStatus state machine.

    This interface is frozen as of Phase 3.5.
    """

    __frozen__: ClassVar[bool] = True

    @abc.abstractmethod
    async def transition(
        self,
        entry: RegistryEntry,
        new_status: RegistryLifecycleStatus,
    ) -> RegistryEntry:
        """Transition an entry to a new lifecycle status."""
        ...

    @abc.abstractmethod
    async def get_valid_transitions(
        self,
        current_status: RegistryLifecycleStatus,
    ) -> list[RegistryLifecycleStatus]:
        """Return valid next states for a given status."""
        ...

    @abc.abstractmethod
    async def can_transition(
        self,
        entry: RegistryEntry,
        new_status: RegistryLifecycleStatus,
    ) -> bool:
        """Check whether a transition is allowed."""
        ...

    @abc.abstractmethod
    async def get_history(self, entry_id: str) -> list[dict[str, Any]]:
        """Retrieve lifecycle transition history for an entry."""
        ...


# ─────────────────────────────────────────────────────────────────────────────
# RegistryHealthChecker
# ─────────────────────────────────────────────────────────────────────────────


class RegistryHealthChecker(abc.ABC):
    """Monitors and reports the operational health of a registry.

    Checks all sub-components (validator, searcher, version manager,
    lifecycle manager, cache) and aggregates their status into a
    comprehensive health report.

    This interface is frozen as of Phase 3.5.
    """

    __frozen__: ClassVar[bool] = True

    @abc.abstractmethod
    async def check_health(self) -> RegistryHealth:
        """Perform a full health check of the registry."""
        ...

    @abc.abstractmethod
    async def is_healthy(self) -> bool:
        """Return whether the registry is healthy overall."""
        ...

    @abc.abstractmethod
    async def get_status_summary(self) -> dict[str, str]:
        """Return a summary of sub-component statuses."""
        ...


# ─────────────────────────────────────────────────────────────────────────────
# RegistryCache
# ─────────────────────────────────────────────────────────────────────────────


class RegistryCache(abc.ABC):
    """Cache layer for registry entries and metadata.

    Provides caching for frequently accessed registry entries to
    reduce lookup latency. Supports entry, search result, and
    metadata caching with configurable TTL.

    This interface is frozen as of Phase 3.5.
    """

    __frozen__: ClassVar[bool] = True

    @abc.abstractmethod
    async def get_entry(self, entry_id: str) -> RegistryEntry | None:
        """Retrieve a cached entry by ID."""
        ...

    @abc.abstractmethod
    async def set_entry(self, entry: RegistryEntry, ttl_seconds: int = 300) -> None:
        """Cache an entry with a TTL."""
        ...

    @abc.abstractmethod
    async def invalidate_entry(self, entry_id: str) -> bool:
        """Invalidate a cached entry."""
        ...

    @abc.abstractmethod
    async def clear(self) -> int:
        """Clear all cached entries. Returns count of cleared items."""
        ...
