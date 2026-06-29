"""Registry Framework domain models.

Defines the core data contracts for the registry platform including
entries, metadata, versions, health, metrics, sessions, decisions,
search results, filters, namespaces, confidence, explainability,
and pipeline version.

All models are Pydantic v2 BaseModel subclasses with full type
annotations, validation, and documentation.

Architecture:
    RegistryService  →  RegistryManager  →  RegistryCoordinator
                                              ├── RegistryValidator
                                              ├── RegistrySearcher
                                              ├── RegistryVersionManager
                                              ├── RegistryLifecycleManager
                                              └── RegistryHealthChecker

Registry entries are generalised records that any specialised registry
(Capability, Agent, Tool, Rule, Plugin, Workflow) can extend.

Phase 3.5: Interfaces frozen. Models stable. Pipeline versioned.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import UUID4, BaseModel, Field

from adip.registry.enums import RegistryLifecycleStatus, RegistryScope, RegistryType

# ─────────────────────────────────────────────────────────────────────────────
# RegistryEntry
# ─────────────────────────────────────────────────────────────────────────────


class RegistryEntry(BaseModel):
    """A generalised entry in any ADIP registry.

    Each entry represents a registered item — a capability, agent,
    tool, rule, plugin, workflow, or future registry type. Specialised
    registries extend this base with their own domain-specific fields.
    """

    entry_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique entry identifier",
    )
    name: str = Field(
        default="",
        description="Human-readable entry name",
    )
    version: str = Field(
        default="1.0.0",
        description="Entry version (semver)",
    )
    registry_type: RegistryType = Field(
        default=RegistryType.CAPABILITY,
        description="The type of registry this entry belongs to",
    )
    scope: RegistryScope = Field(
        default=RegistryScope.GLOBAL,
        description="The scope of this entry",
    )
    status: RegistryLifecycleStatus = Field(
        default=RegistryLifecycleStatus.REGISTERED,
        description="Current lifecycle status",
    )
    owner_id: str = Field(
        default="",
        description="The user or system that owns this entry",
    )
    namespace: str = Field(
        default="default",
        description="Logical namespace for multi-tenant isolation",
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Tags for classification and discovery",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata key-value pairs",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the entry was registered",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the entry was last updated",
    )


# ─────────────────────────────────────────────────────────────────────────────
# RegistryMetadata
# ─────────────────────────────────────────────────────────────────────────────


class RegistryMetadata(BaseModel):
    """Metadata associated with a registry entry.

    Provides structured metadata fields that are common across
    all registry types while allowing extensibility via the
    properties field.
    """

    description: str = Field(
        default="",
        description="Human-readable description of the entry",
    )
    display_name: str = Field(
        default="",
        description="Display-friendly name for UIs",
    )
    icon: str = Field(
        default="",
        description="Icon or emblem reference",
    )
    category: str = Field(
        default="",
        description="Functional category for grouping",
    )
    source: str = Field(
        default="",
        description="Origin source (filesystem, registry, manual, api)",
    )
    documentation_url: str = Field(
        default="",
        description="Link to external documentation",
    )
    support_contact: str = Field(
        default="",
        description="Contact point for support",
    )
    license: str = Field(
        default="",
        description="License identifier (MIT, Apache-2.0, etc.)",
    )
    properties: dict[str, Any] = Field(
        default_factory=dict,
        description="Extensible properties for registry-specific metadata",
    )


# ─────────────────────────────────────────────────────────────────────────────
# RegistryVersion
# ─────────────────────────────────────────────────────────────────────────────


class RegistryVersion(BaseModel):
    """Version record for a registry entry.

    Tracks the version history of an entry including the version
    number, release notes, and a reference to the associated
    entry snapshot at that version.
    """

    version_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique version record identifier",
    )
    entry_id: UUID4 = Field(
        description="The entry this version belongs to",
    )
    version: str = Field(
        default="1.0.0",
        description="Semantic version string",
    )
    previous_version: str = Field(
        default="",
        description="The previous version (empty if first)",
    )
    release_notes: str = Field(
        default="",
        description="Release notes for this version",
    )
    snapshot: dict[str, Any] = Field(
        default_factory=dict,
        description="Serialised entry state at this version",
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
# RegistryHealth
# ─────────────────────────────────────────────────────────────────────────────


class RegistryHealth(BaseModel):
    """Health status of a registry.

    Provides operational health information for monitoring and
    observability of the registry platform.
    """

    overall_status: str = Field(
        default="UNKNOWN",
        description="Overall health status (HEALTHY, DEGRADED, UNHEALTHY, UNKNOWN)",
    )
    entries_total: int = Field(
        default=0,
        ge=0,
        description="Total number of registered entries",
    )
    active_entries: int = Field(
        default=0,
        ge=0,
        description="Number of entries in ACTIVE status",
    )
    validator_status: str = Field(
        default="UNKNOWN",
        description="Status of the registry validator",
    )
    searcher_status: str = Field(
        default="UNKNOWN",
        description="Status of the registry searcher",
    )
    version_manager_status: str = Field(
        default="UNKNOWN",
        description="Status of the version manager",
    )
    lifecycle_manager_status: str = Field(
        default="UNKNOWN",
        description="Status of the lifecycle manager",
    )
    cache_status: str = Field(
        default="UNKNOWN",
        description="Status of the registry cache",
    )
    index_status: str = Field(
        default="UNKNOWN",
        description="Status of the index manager",
    )
    dependency_graph_status: str = Field(
        default="UNKNOWN",
        description="Status of the dependency graph",
    )
    policy_status: str = Field(
        default="UNKNOWN",
        description="Status of the policy engine",
    )
    error_count: int = Field(
        default=0,
        ge=0,
        description="Total number of registry errors",
    )
    average_latency_ms: float = Field(
        default=0.0,
        ge=0.0,
        description="Average operation latency in milliseconds",
    )
    uptime_seconds: float = Field(
        default=0.0,
        ge=0.0,
        description="Registry uptime in seconds",
    )
    last_check: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the health was last checked",
    )


# ─────────────────────────────────────────────────────────────────────────────
# RegistryMetrics
# ─────────────────────────────────────────────────────────────────────────────


class RegistryMetrics(BaseModel):
    """Aggregated metrics for a registry.

    Tracks operational metrics for monitoring, alerting, and
    capacity planning.
    """

    registry_type: RegistryType = Field(
        default=RegistryType.CAPABILITY,
        description="The registry type these metrics relate to",
    )
    entries_total: int = Field(
        default=0,
        ge=0,
        description="Total number of entries in this registry",
    )
    registrations_total: int = Field(
        default=0,
        ge=0,
        description="Total registration operations",
    )
    deregistrations_total: int = Field(
        default=0,
        ge=0,
        description="Total deregistration operations",
    )
    lookups_total: int = Field(
        default=0,
        ge=0,
        description="Total lookup operations",
    )
    searches_total: int = Field(
        default=0,
        ge=0,
        description="Total search operations",
    )
    versions_total: int = Field(
        default=0,
        ge=0,
        description="Total version records",
    )
    active_entries: int = Field(
        default=0,
        ge=0,
        description="Entries currently in ACTIVE status",
    )
    cache_hits: int = Field(
        default=0,
        ge=0,
        description="Total cache hit count",
    )
    cache_misses: int = Field(
        default=0,
        ge=0,
        description="Total cache miss count",
    )
    average_latency_ms: float = Field(
        default=0.0,
        ge=0.0,
        description="Average operation latency in milliseconds",
    )
    errors_total: int = Field(
        default=0,
        ge=0,
        description="Total error count",
    )
    validation_failures_total: int = Field(
        default=0,
        ge=0,
        description="Total validation failure count",
    )
    updates_total: int = Field(
        default=0,
        ge=0,
        description="Total update operations",
    )
    cache_hit_ratio: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Cache hit ratio (0.0–1.0)",
    )
    search_strategy_usage: dict[str, int] = Field(
        default_factory=dict,
        description="Search strategy usage counts",
    )
    namespace_usage: dict[str, int] = Field(
        default_factory=dict,
        description="Entry count broken down by namespace",
    )
    registry_types: dict[str, int] = Field(
        default_factory=dict,
        description="Entry count broken down by registry type",
    )
    entries_per_scope: dict[str, int] = Field(
        default_factory=dict,
        description="Entry count broken down by scope",
    )
    entries_per_status: dict[str, int] = Field(
        default_factory=dict,
        description="Entry count broken down by lifecycle status",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When these metrics were captured",
    )


# ─────────────────────────────────────────────────────────────────────────────
# RegistrySession
# ─────────────────────────────────────────────────────────────────────────────


class RegistrySession(BaseModel):
    """Operational session for a registry operation sequence.

    Tracks a sequence of registry operations within a single
    session context for auditing, correlation, and explainability.
    Enhanced in Phase 3 with search_strategy, version_used,
    lifecycle_state, and statistics fields.
    """

    session_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique session identifier",
    )
    registry_type: RegistryType = Field(
        default=RegistryType.CAPABILITY,
        description="The registry type this session relates to",
    )
    operation: str = Field(
        default="",
        description="The primary operation being performed",
    )
    user_id: str = Field(
        default="",
        description="The user or system that initiated the session",
    )
    namespace: str = Field(
        default="default",
        description="The namespace context for this session",
    )
    correlation_id: str = Field(
        default="",
        description="Correlation ID for distributed tracing",
    )
    entries_affected: list[str] = Field(
        default_factory=list,
        description="Names or IDs of entries affected in this session",
    )
    search_strategy: str = Field(
        default="",
        description="The search strategy used during this session",
    )
    version_used: str = Field(
        default="",
        description="The version used for operations in this session",
    )
    lifecycle_state: str = Field(
        default="",
        description="The lifecycle state of the entry during this session",
    )
    statistics: dict[str, int | float] = Field(
        default_factory=dict,
        description="Operational statistics for this session",
    )
    started_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the session started",
    )
    completed_at: datetime | None = Field(
        default=None,
        description="When the session completed (None if still active)",
    )
    status: str = Field(
        default="ACTIVE",
        description="Session status (ACTIVE, COMPLETED, FAILED, TIMEOUT)",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional session context",
    )


# ─────────────────────────────────────────────────────────────────────────────
# RegistryDecision
# ─────────────────────────────────────────────────────────────────────────────


class RegistryDecision(BaseModel):
    """Decision record for a registry operation.

    Captures the outcome of a registry operation including
    whether it was allowed, the reasoning, and any associated
    metadata for explainability. Enhanced in Phase 3 with
    registry_type, pipeline stage results, and confidence.
    """

    decision_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique decision identifier",
    )
    registry_type: RegistryType = Field(
        default=RegistryType.CAPABILITY,
        description="The registry type this decision relates to",
    )
    entry_id: UUID4 = Field(
        description="The entry this decision relates to",
    )
    operation: str = Field(
        default="",
        description="The operation that triggered this decision",
    )
    allowed: bool = Field(
        default=True,
        description="Whether the operation was allowed",
    )
    reasoning: list[str] = Field(
        default_factory=list,
        description="Human-readable reasoning steps for this decision",
    )
    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Confidence score for this decision (0.0–1.0)",
    )
    validation_result: list[str] = Field(
        default_factory=list,
        description="Results from the validation pipeline stage",
    )
    validation_results: list[str] = Field(
        default_factory=list,
        description="[DEPRECATED] Use validation_result instead",
    )
    policy_result: list[str] = Field(
        default_factory=list,
        description="Results from the policy engine pipeline stage",
    )
    version_result: str = Field(
        default="",
        description="Result from the version management pipeline stage",
    )
    dependency_result: str = Field(
        default="",
        description="Result from the dependency graph pipeline stage",
    )
    search_result: str = Field(
        default="",
        description="Result summary from the search pipeline stage (strategy, count)",
    )
    performed_by: str = Field(
        default="",
        description="The user or system that performed the operation",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the decision was made",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional decision metadata",
    )


# ─────────────────────────────────────────────────────────────────────────────
# RegistrySearchResult
# ─────────────────────────────────────────────────────────────────────────────


class RegistrySearchResult(BaseModel):
    """A single result from a registry search operation.

    Wraps a matched entry with relevance information for ranking
    and explainability.
    """

    entry: RegistryEntry = Field(
        description="The matched registry entry",
    )
    score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Relevance score for ranking (1.0 = exact match)",
    )
    matched_fields: list[str] = Field(
        default_factory=list,
        description="Fields that contributed to the match",
    )
    rank: int = Field(
        default=0,
        ge=0,
        description="Rank position in the result set (0 = highest)",
    )


# ─────────────────────────────────────────────────────────────────────────────
# RegistryFilter
# ─────────────────────────────────────────────────────────────────────────────


class RegistryFilter(BaseModel):
    """Filter criteria for registry search and listing operations.

    Provides composable filter conditions for querying the registry
    by type, scope, status, namespace, tags, and custom metadata.
    """

    registry_type: RegistryType | None = Field(
        default=None,
        description="Filter by registry type",
    )
    scope: RegistryScope | None = Field(
        default=None,
        description="Filter by scope",
    )
    status: RegistryLifecycleStatus | None = Field(
        default=None,
        description="Filter by lifecycle status",
    )
    namespace: str = Field(
        default="",
        description="Filter by namespace (empty = all namespaces)",
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Filter by tags (entries matching any tag)",
    )
    owner_id: str = Field(
        default="",
        description="Filter by owner (empty = all owners)",
    )
    query: str = Field(
        default="",
        description="Free-text search query",
    )
    metadata_filter: dict[str, Any] = Field(
        default_factory=dict,
        description="Filter by metadata key-value pairs",
    )
    limit: int = Field(
        default=20,
        ge=1,
        le=1000,
        description="Maximum number of results to return",
    )
    offset: int = Field(
        default=0,
        ge=0,
        description="Number of results to skip for pagination",
    )


# ─────────────────────────────────────────────────────────────────────────────
# RegistryNamespace
# ─────────────────────────────────────────────────────────────────────────────


class RegistryNamespace(BaseModel):
    """A namespace within the registry for logical isolation.

    Namespaces provide multi-tenant and multi-domain isolation
    within a single registry instance. Each namespace has its
    own configuration, policies, and entry scope.
    """

    namespace_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique namespace identifier",
    )
    name: str = Field(
        default="",
        description="Namespace name (unique within the registry)",
    )
    registry_type: RegistryType = Field(
        default=RegistryType.CAPABILITY,
        description="The registry type this namespace belongs to",
    )
    description: str = Field(
        default="",
        description="Human-readable description of this namespace",
    )
    scope: RegistryScope = Field(
        default=RegistryScope.DOMAIN,
        description="Default scope for entries in this namespace",
    )
    allowed_scopes: list[RegistryScope] = Field(
        default_factory=lambda: list(RegistryScope),
        description="Scopes permitted within this namespace",
    )
    owner_id: str = Field(
        default="",
        description="The user or system that owns this namespace",
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Tags for classification and discovery",
    )
    max_entries: int = Field(
        default=0,
        ge=0,
        description="Maximum entries allowed (0 = unlimited)",
    )
    enabled: bool = Field(
        default=True,
        description="Whether this namespace is enabled",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the namespace was created",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the namespace was last updated",
    )


# ─────────────────────────────────────────────────────────────────────────────
# RegistryConfidence
# ─────────────────────────────────────────────────────────────────────────────


class RegistryConfidence(BaseModel):
    """Confidence assessment for a registry decision.

    Evaluates confidence across six dimensions: metadata
    completeness, validation quality, version correctness,
    namespace validity, policy compliance, and dependency
    integrity. Each dimension is a score between 0.0 and 1.0.
    """

    overall_confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Overall confidence score (0.0–1.0)",
    )
    metadata_completeness: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Confidence based on metadata completeness",
    )
    validation_quality: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Confidence based on validation pass/fail",
    )
    version_correctness: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Confidence based on version correctness",
    )
    namespace_validity: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Confidence based on namespace validity",
    )
    policy_compliance: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Confidence based on policy compliance",
    )
    dependency_integrity: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Confidence based on dependency integrity",
    )
    search_result_quality: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Confidence based on search result quality",
    )


# ─────────────────────────────────────────────────────────────────────────────
# RegistryExplainabilityMetadata
# ─────────────────────────────────────────────────────────────────────────────


class RegistryExplainabilityMetadata(BaseModel):
    """Explainability metadata for registry operations.

    Stores human-readable explanations for why each registry
    operation decision was made. Each field captures the
    reasoning behind a specific aspect of the operation.
    Will feed the Explainability Engine in future phases.
    """

    why_registered: str = Field(
        default="",
        description="Explanation for why the entry was registered",
    )
    why_updated: str = Field(
        default="",
        description="Explanation for why the entry was updated",
    )
    why_removed: str = Field(
        default="",
        description="Explanation for why the entry was removed",
    )
    why_version_selected: str = Field(
        default="",
        description="Explanation for why a specific version was selected",
    )
    why_search_strategy_selected: str = Field(
        default="",
        description="Explanation for why a specific search strategy was selected",
    )
    why_dependency_selected: str = Field(
        default="",
        description="Explanation for why a dependency was selected",
    )
    why_validation_failed: str = Field(
        default="",
        description="Explanation for why validation failed",
    )
    why_search_strategy_used: str = Field(
        default="",
        description="Explanation for why a specific search strategy was used",
    )


# ─────────────────────────────────────────────────────────────────────────────
# RegistryPipelineVersion
# ─────────────────────────────────────────────────────────────────────────────


class RegistryPipelineVersion(BaseModel):
    """Pipeline version metadata for the Registry Framework.

    Tracks the current pipeline and compatibility versions to
    support future pipeline evolution. The pipeline_version
    increments with each breaking change. The compatibility_version
    indicates the minimum version a consumer must support.

    Phase 3.5 introduces this as a foundation for future
    pipeline evolution and the AI Decision Layer.
    """

    pipeline_version: str = Field(
        default="1.0.0",
        description="Current registry pipeline version",
    )
    compatibility_version: str = Field(
        default="1.0.0",
        description="Minimum compatible pipeline version for consumers",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When this pipeline version was recorded",
    )
