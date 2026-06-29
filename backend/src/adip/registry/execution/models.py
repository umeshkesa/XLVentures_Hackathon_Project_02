"""Registry Framework execution-layer models.

Defines internal models used by the registry execution pipeline
including trace records, audit records, version records, index
entries, and dependency graph nodes. These are separate from the
public domain models in contracts/models.py.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import UUID4, BaseModel, Field

from adip.registry.enums import RegistryLifecycleStatus

# ─────────────────────────────────────────────────────────────────────────────
# VersionRecord
# ─────────────────────────────────────────────────────────────────────────────


class VersionRecord(BaseModel):
    """Internal version record for a registry entry.

    Tracks the version history including entry snapshot and
    metadata at each version.
    """

    version_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique version record identifier",
    )
    entry_id: UUID4 = Field(
        description="The entry this version belongs to",
    )
    entry_name: str = Field(
        default="",
        description="Entry name at this version",
    )
    version: str = Field(
        default="1.0.0",
        description="Semantic version string",
    )
    previous_version: str = Field(
        default="",
        description="The previous version (empty if first)",
    )
    is_active: bool = Field(
        default=False,
        description="Whether this is the currently active version",
    )
    snapshot: dict[str, Any] = Field(
        default_factory=dict,
        description="Serialised entry state at this version",
    )
    release_notes: str = Field(
        default="",
        description="Release notes for this version",
    )
    created_by: str = Field(
        default="",
        description="The user or system that created this version",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When this version was recorded",
    )


# ─────────────────────────────────────────────────────────────────────────────
# IndexEntry
# ─────────────────────────────────────────────────────────────────────────────


class IndexEntry(BaseModel):
    """An entry in a registry index.

    Maps a key (name, tag, label, namespace, type) to the
    set of entry IDs that match it.
    """

    index_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique index entry identifier",
    )
    key: str = Field(
        default="",
        description="The index key",
    )
    entry_ids: list[str] = Field(
        default_factory=list,
        description="Entry IDs matching this key",
    )
    index_type: str = Field(
        default="",
        description="The type of index (name, tag, label, namespace, type)",
    )


# ─────────────────────────────────────────────────────────────────────────────
# SearchResult
# ─────────────────────────────────────────────────────────────────────────────


class SearchResult(BaseModel):
    """A single result from a registry search.

    Wraps an entry ID with relevance information for ranking.
    """

    entry_id: str = Field(
        description="The matched entry ID",
    )
    entry_name: str = Field(
        default="",
        description="The matched entry name",
    )
    score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Relevance score (1.0 = exact match)",
    )
    strategy: str = Field(
        default="",
        description="The search strategy that produced this result",
    )


# ─────────────────────────────────────────────────────────────────────────────
# AuditRecord
# ─────────────────────────────────────────────────────────────────────────────


class AuditRecord(BaseModel):
    """An audit record for a registry operation.

    Tracks all state-changing operations for compliance and
    observability.
    """

    audit_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique audit record identifier",
    )
    entry_id: UUID4 = Field(
        description="The entry this audit record relates to",
    )
    entry_name: str = Field(
        default="",
        description="Entry name at the time of the operation",
    )
    operation: str = Field(
        default="",
        description="The operation performed (register, update, remove, activate, deprecate)",
    )
    previous_status: str = Field(
        default="",
        description="The lifecycle status before the operation",
    )
    new_status: str = Field(
        default="",
        description="The lifecycle status after the operation",
    )
    performed_by: str = Field(
        default="",
        description="The user or system that performed the operation",
    )
    namespace: str = Field(
        default="default",
        description="The namespace context for this operation",
    )
    details: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional operation details",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the operation was performed",
    )


# ─────────────────────────────────────────────────────────────────────────────
# TraceRecord
# ─────────────────────────────────────────────────────────────────────────────


class TraceRecord(BaseModel):
    """A trace span for a registry pipeline stage.

    Records timing, status, and metadata for each stage of the
    registry execution pipeline.
    """

    trace_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique trace identifier",
    )
    stage_name: str = Field(
        default="",
        description="The pipeline stage name",
    )
    operation: str = Field(
        default="",
        description="The operation being traced",
    )
    entry_id: str | None = Field(
        default=None,
        description="The entry ID if applicable",
    )
    entry_name: str = Field(
        default="",
        description="The entry name if applicable",
    )
    registry_type: str = Field(
        default="",
        description="The registry type context",
    )
    namespace: str = Field(
        default="",
        description="The namespace context",
    )
    correlation_id: str = Field(
        default="",
        description="Correlation ID for distributed tracing",
    )
    started_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the stage started",
    )
    completed_at: datetime | None = Field(
        default=None,
        description="When the stage completed (None if in progress)",
    )
    duration_ms: float | None = Field(
        default=None,
        ge=0.0,
        description="Duration in milliseconds",
    )
    success: bool = Field(
        default=True,
        description="Whether the stage completed successfully",
    )
    warnings: list[str] = Field(
        default_factory=list,
        description="Warning messages from this stage",
    )
    errors: list[str] = Field(
        default_factory=list,
        description="Error messages from this stage",
    )


# ─────────────────────────────────────────────────────────────────────────────
# DependencyGraph
# ─────────────────────────────────────────────────────────────────────────────


class DependencyGraph(BaseModel):
    """A generic dependency graph for registry entries.

    Tracks dependencies between registry entries using an
    adjacency list representation.
    """

    graph_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique graph identifier",
    )
    nodes: dict[str, list[str]] = Field(
        default_factory=dict,
        description="Adjacency list: entry_name → list of dependency entry_names",
    )
    root_entries: list[str] = Field(
        default_factory=list,
        description="Entries with no dependencies",
    )
    leaf_entries: list[str] = Field(
        default_factory=list,
        description="Entries that nothing depends on",
    )
    circular_dependency_reports: list[list[str]] = Field(
        default_factory=list,
        description="Detected circular dependency chains",
    )
    dependency_depth: int = Field(
        default=0,
        ge=0,
        description="Maximum dependency depth",
    )
    load_order: list[str] = Field(
        default_factory=list,
        description="Topological load order",
    )
    unused_dependencies: list[str] = Field(
        default_factory=list,
        description="Declared dependencies not found as entries",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the graph was created",
    )


# ─────────────────────────────────────────────────────────────────────────────
# DependencyNode
# ─────────────────────────────────────────────────────────────────────────────


class DependencyNode(BaseModel):
    """A single node in the registry dependency graph."""

    entry_name: str = Field(
        default="",
        description="Entry name",
    )
    entry_id: str = Field(
        default="",
        description="Entry ID",
    )
    version: str = Field(
        default="1.0.0",
        description="Entry version",
    )
    dependencies: list[str] = Field(
        default_factory=list,
        description="Entry names this node depends on",
    )
    dependents: list[str] = Field(
        default_factory=list,
        description="Entry names that depend on this node",
    )
    resolved: bool = Field(
        default=False,
        description="Whether all dependencies are resolved",
    )
    level: int = Field(
        default=0,
        ge=0,
        description="Dependency depth level (0 = root)",
    )


# ─────────────────────────────────────────────────────────────────────────────
# LifecycleHistoryEntry
# ─────────────────────────────────────────────────────────────────────────────


class LifecycleHistoryEntry(BaseModel):
    """A single lifecycle transition record."""

    entry_id: UUID4 = Field(
        description="The entry that transitioned",
    )
    from_status: RegistryLifecycleStatus | None = Field(
        default=None,
        description="The previous lifecycle status",
    )
    to_status: RegistryLifecycleStatus = Field(
        description="The new lifecycle status",
    )
    reason: str = Field(
        default="",
        description="Reason for the transition",
    )
    changed_by: str = Field(
        default="",
        description="The user or system that performed the transition",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the transition occurred",
    )
