"""Execution-layer models for the Memory Manager subsystem.

These models support the internal Memory Platform: lifecycle tracking,
audit records, policy decisions, version history, cache entries,
search operations, and execution traces. They are not exposed through
the public MemoryManager / MemoryService API.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import UUID4, BaseModel, Field

from adip.memory.enums import (
    MemoryLifecycleStatus,
    MemoryOperation,
    MemoryTier,
    MemoryType,
)

# ─────────────────────────────────────────────────────────────────────────────
# Lifecycle
# ─────────────────────────────────────────────────────────────────────────────


class MemoryLifecycleHistory(BaseModel):
    """A single lifecycle transition recorded for audit / observability."""

    history_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique identifier for this history entry",
    )
    memory_id: UUID4 = Field(
        description="The memory record that transitioned",
    )
    previous_state: MemoryLifecycleStatus = Field(
        description="Lifecycle status before the transition",
    )
    new_state: MemoryLifecycleStatus = Field(
        description="Lifecycle status after the transition",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the transition occurred",
    )
    reason: str = Field(
        default="",
        description="Why the transition occurred",
    )
    actor: str = Field(
        default="system",
        description="Who or what triggered the transition",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional transition metadata",
    )


# ─────────────────────────────────────────────────────────────────────────────
# Policy
# ─────────────────────────────────────────────────────────────────────────────


class PolicyDecision(BaseModel):
    """Outcome of a policy validation check."""

    valid: bool = Field(
        description="Whether the policy check passed",
    )
    violations: list[str] = Field(
        default_factory=list,
        description="List of specific policy violations",
    )
    warnings: list[str] = Field(
        default_factory=list,
        description="Non-blocking policy warnings",
    )
    policy_name: str = Field(
        default="",
        description="Name of the policy that was checked",
    )


# ─────────────────────────────────────────────────────────────────────────────
# Audit
# ─────────────────────────────────────────────────────────────────────────────


class AuditRecord(BaseModel):
    """A single audit trail entry for a memory operation."""

    audit_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique identifier for this audit record",
    )
    memory_id: UUID4 = Field(
        description="The memory record involved",
    )
    memory_type: MemoryType = Field(
        description="Category of memory",
    )
    operation: MemoryOperation = Field(
        description="The operation that was performed",
    )
    tier: MemoryTier | None = Field(
        default=None,
        description="The storage tier involved",
    )
    namespace: str = Field(
        default="",
        description="The namespace of the record",
    )
    owner_id: str = Field(
        default="",
        description="The owner of the record",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the operation occurred",
    )
    correlation_id: str = Field(
        default="",
        description="Correlation ID for tracing",
    )
    details: dict[str, Any] = Field(
        default_factory=dict,
        description="Operation-specific details",
    )


# ─────────────────────────────────────────────────────────────────────────────
# Version history
# ─────────────────────────────────────────────────────────────────────────────


class VersionHistory(BaseModel):
    """A single version entry for a memory record."""

    version_number: int = Field(
        ge=1,
        description="The version number of this entry",
    )
    memory_id: UUID4 = Field(
        description="The memory record this version belongs to",
    )
    snapshot: dict[str, Any] = Field(
        default_factory=dict,
        description="Serialised snapshot of the record at this version",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When this version was created",
    )
    reason: str = Field(
        default="",
        description="Why this version was created",
    )


# ─────────────────────────────────────────────────────────────────────────────
# Cache
# ─────────────────────────────────────────────────────────────────────────────


class CacheEntry(BaseModel):
    """An entry in the in-memory cache."""

    cache_key: str = Field(
        description="The cache lookup key",
    )
    memory_id: UUID4 = Field(
        description="The memory record ID this entry points to",
    )
    data: dict[str, Any] = Field(
        default_factory=dict,
        description="The cached data",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When this cache entry was created",
    )
    expires_at: datetime | None = Field(
        default=None,
        description="When this cache entry expires",
    )
    access_count: int = Field(
        default=0,
        ge=0,
        description="Number of times this entry has been accessed",
    )


# ─────────────────────────────────────────────────────────────────────────────
# Search
# ─────────────────────────────────────────────────────────────────────────────


class SearchQuery(BaseModel):
    """Internal representation of a search query."""

    memory_type: MemoryType | None = Field(
        default=None,
        description="Filter by memory type",
    )
    owner_id: str = Field(
        default="",
        description="Filter by owner",
    )
    namespace: str = Field(
        default="",
        description="Filter by namespace",
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Filter by tags",
    )
    lifecycle_status: MemoryLifecycleStatus | None = Field(
        default=None,
        description="Filter by lifecycle status",
    )
    query: str = Field(
        default="",
        description="Free-text query",
    )
    limit: int = Field(
        default=20,
        ge=1,
        le=1000,
        description="Max results",
    )
    offset: int = Field(
        default=0,
        ge=0,
        description="Pagination offset",
    )


# ─────────────────────────────────────────────────────────────────────────────
# Trace
# ─────────────────────────────────────────────────────────────────────────────


class MemoryTrace(BaseModel):
    """Execution trace recorded by a Memory Manager pipeline stage."""

    stage_name: str = Field(
        description="Name of the pipeline stage",
    )
    operation: MemoryOperation = Field(
        description="The operation being performed",
    )
    lifecycle_state: MemoryLifecycleStatus | None = Field(
        default=None,
        description="Current lifecycle state of the record",
    )
    tier: MemoryTier | None = Field(
        default=None,
        description="The storage tier involved",
    )
    namespace: str = Field(
        default="",
        description="The namespace of the record",
    )
    started_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the stage began",
    )
    completed_at: datetime | None = Field(
        default=None,
        description="When the stage finished",
    )
    duration_ms: float | None = Field(
        default=None,
        ge=0.0,
        description="Wall-clock duration in milliseconds",
    )
    input_summary: dict[str, Any] = Field(
        default_factory=dict,
        description="Summary of inputs",
    )
    output_summary: dict[str, Any] = Field(
        default_factory=dict,
        description="Summary of outputs",
    )
    success: bool = Field(
        default=True,
        description="Whether the stage completed without error",
    )
    warnings: list[str] = Field(
        default_factory=list,
        description="Non-fatal warnings",
    )
    errors: list[str] = Field(
        default_factory=list,
        description="Fatal errors",
    )
    memory_domain: str = Field(
        default="",
        description="The MemoryDomain this trace belongs to",
    )
    session_id: str = Field(
        default="",
        description="The session this trace belongs to",
    )
    correlation_id: str = Field(
        default="",
        description="Correlation ID for tracing",
    )
