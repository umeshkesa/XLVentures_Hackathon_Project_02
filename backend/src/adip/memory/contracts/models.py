"""Memory Manager domain models — strongly typed memory records.

Every memory operation within ADIP flows through the Memory Manager.
No module accesses storage directly.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import UUID4, BaseModel, Field

from adip.memory.enums import MemoryDomain, MemoryTier, MemoryType, RetentionPolicy

# ─────────────────────────────────────────────────────────────────────────────
# MemoryRecord — base model
# ─────────────────────────────────────────────────────────────────────────────


class MemoryRecord(BaseModel):
    """Base record for all memory stored in the Memory Manager.

    Every concrete memory type inherits from this record to ensure
    consistent identity, ownership, versioning, and metadata across
    all storage tiers.
    """

    memory_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique identifier for this memory record",
    )
    memory_type: MemoryType = Field(
        description="Category of memory (session, conversation, etc.)",
    )
    memory_tier: MemoryTier = Field(
        default=MemoryTier.HOT,
        description="Storage tier this record resides in",
    )
    memory_domain: MemoryDomain = Field(
        default=MemoryDomain.SYSTEM,
        description="Which platform module owns this memory",
    )
    owner_id: str = Field(
        default="",
        description="Owner or creator of this record (user ID, system ID)",
    )
    namespace: str = Field(
        default="default",
        description="Logical namespace for grouping records",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the record was first created",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the record was last modified",
    )
    expires_at: datetime | None = Field(
        default=None,
        description="When the record expires and may be evicted",
    )
    version: int = Field(
        default=1,
        ge=0,
        description="Version number for optimistic concurrency",
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Arbitrary tags for filtering and discovery",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary key-value metadata",
    )


# ─────────────────────────────────────────────────────────────────────────────
# Concrete memory types
# ─────────────────────────────────────────────────────────────────────────────


class SessionMemory(MemoryRecord):
    """Active session / request state.

    Holds temporary execution context scoped to a single session.
    Typically short-lived and stored in HOT tier with TTL.
    """

    memory_type: MemoryType = MemoryType.SESSION
    session_id: str = Field(
        default="",
        description="Identifier for the session this memory belongs to",
    )
    state: dict[str, Any] = Field(
        default_factory=dict,
        description="Current session state data",
    )
    ttl_seconds: int | None = Field(
        default=None,
        ge=1,
        description="Time-to-live in seconds before automatic eviction",
    )


class ConversationMemory(MemoryRecord):
    """Conversation history with summaries and interaction metadata.

    Stores the full history of a conversational interaction along
    with generated summaries and metadata about each turn.
    """

    memory_type: MemoryType = MemoryType.CONVERSATION
    conversation_id: str = Field(
        default="",
        description="Unique identifier for this conversation",
    )
    messages: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Ordered list of message objects in the conversation",
    )
    summary: str = Field(
        default="",
        description="Generated summary of the conversation so far",
    )
    turn_count: int = Field(
        default=0,
        ge=0,
        description="Number of turns in this conversation",
    )
    participants: list[str] = Field(
        default_factory=list,
        description="List of participant identifiers",
    )


class WorkflowMemory(MemoryRecord):
    """Workflow execution state, checkpoints, and runtime metadata.

    Captures the execution state of a workflow so it can be resumed
    or inspected after a failure or pause.
    """

    memory_type: MemoryType = MemoryType.WORKFLOW
    workflow_id: str = Field(
        default="",
        description="Identifier of the associated workflow instance",
    )
    execution_state: dict[str, Any] = Field(
        default_factory=dict,
        description="Current execution state of the workflow",
    )
    checkpoints: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Ordered list of execution checkpoints",
    )
    runtime_metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional runtime metadata",
    )


class PlanningMemory(MemoryRecord):
    """Execution plans, plan versions, planning traces, and confidence history.

    Stores artefacts produced by the Planner — plans, traces,
    confidence scores — for later retrieval, comparison, and audit.
    """

    memory_type: MemoryType = MemoryType.PLANNING
    plan_id: str = Field(
        default="",
        description="Identifier of the associated execution plan",
    )
    plan_version: int = Field(
        default=1,
        ge=1,
        description="Version number of the plan",
    )
    planning_traces: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Traces recorded during the planning phase",
    )
    confidence_history: list[float] = Field(
        default_factory=list,
        description="Historical confidence scores for this plan",
    )
    plan_data: dict[str, Any] = Field(
        default_factory=dict,
        description="Serialised execution plan data",
    )


class RecommendationMemory(MemoryRecord):
    """Recommendations, decisions, outcomes, and feedback.

    Records what was recommended, what decision was made, what
    outcome occurred, and any feedback provided — enabling future
    improvement of recommendation quality.
    """

    memory_type: MemoryType = MemoryType.RECOMMENDATION
    recommendation_id: str = Field(
        default="",
        description="Identifier for this recommendation instance",
    )
    recommendation_data: dict[str, Any] = Field(
        default_factory=dict,
        description="The recommendation payload",
    )
    decision: str = Field(
        default="",
        description="The decision made (accepted, rejected, modified)",
    )
    outcome: dict[str, Any] = Field(
        default_factory=dict,
        description="The outcome that resulted from the decision",
    )
    feedback: dict[str, Any] = Field(
        default_factory=dict,
        description="User or system feedback on the recommendation",
    )


class LearningMemory(MemoryRecord):
    """Lessons learned, historical patterns, and continuous improvement metadata.

    Stores insights and patterns discovered over time that can be
    applied to improve future planning, execution, and recommendations.
    """

    memory_type: MemoryType = MemoryType.LEARNING
    lesson_id: str = Field(
        default="",
        description="Identifier for this lesson or insight",
    )
    pattern: str = Field(
        default="",
        description="Description of the observed pattern",
    )
    context: dict[str, Any] = Field(
        default_factory=dict,
        description="Context in which the pattern was observed",
    )
    recommendation: str = Field(
        default="",
        description="Recommended action based on this lesson",
    )
    applicability: list[str] = Field(
        default_factory=list,
        description="Scenarios or modules where this lesson applies",
    )


class UserMemory(MemoryRecord):
    """User preferences, organisation settings, and personal defaults.

    Stores configuration and preference data scoped to a user or
    organisation that influences behaviour across ADIP modules.
    """

    memory_type: MemoryType = MemoryType.USER
    user_id: str = Field(
        default="",
        description="Identifier of the user this record belongs to",
    )
    preferences: dict[str, Any] = Field(
        default_factory=dict,
        description="User-specific preference key-value pairs",
    )
    organisation_settings: dict[str, Any] = Field(
        default_factory=dict,
        description="Organisation-level settings",
    )
    personal_defaults: dict[str, Any] = Field(
        default_factory=dict,
        description="Personal default values for the user",
    )


class CacheMemory(MemoryRecord):
    """Frequently accessed objects with TTL and cache metadata.

    Stores ephemeral, high-read-rate objects to reduce load on
    warm and cold storage tiers.
    """

    memory_type: MemoryType = MemoryType.CACHE
    cache_key: str = Field(
        default="",
        description="The cache lookup key",
    )
    cached_data: dict[str, Any] = Field(
        default_factory=dict,
        description="The cached object data",
    )
    ttl_seconds: int | None = Field(
        default=None,
        ge=1,
        description="Time-to-live in seconds before automatic eviction",
    )
    access_count: int = Field(
        default=0,
        ge=0,
        description="Number of times this cache entry has been accessed",
    )


# ─────────────────────────────────────────────────────────────────────────────
# MemoryContext
# ─────────────────────────────────────────────────────────────────────────────


class MemoryContext(BaseModel):
    """Aggregated context of all active memory for a given scope.

    Provides a single snapshot of all relevant memory — session,
    conversation, workflow, planning, recommendation, learning,
    user, and cache — for use by any ADIP module.
    """

    session: SessionMemory | None = Field(
        default=None,
        description="Current session memory, if any",
    )
    conversation: ConversationMemory | None = Field(
        default=None,
        description="Current conversation memory, if any",
    )
    workflow: WorkflowMemory | None = Field(
        default=None,
        description="Current workflow memory, if any",
    )
    planning: PlanningMemory | None = Field(
        default=None,
        description="Current planning memory, if any",
    )
    recommendation: RecommendationMemory | None = Field(
        default=None,
        description="Current recommendation memory, if any",
    )
    learning: LearningMemory | None = Field(
        default=None,
        description="Current learning memory, if any",
    )
    user: UserMemory | None = Field(
        default=None,
        description="Current user memory, if any",
    )
    cache: CacheMemory | None = Field(
        default=None,
        description="Current cache memory, if any",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional free-form context metadata",
    )


# ─────────────────────────────────────────────────────────────────────────────
# MemoryPolicy
# ─────────────────────────────────────────────────────────────────────────────


class MemoryPolicy(BaseModel):
    """Configurable policy governing memory management behaviour.

    The Memory Manager reads policy values to decide retention,
    encryption, compression, persistence, replication, and audit
    behaviour for stored records.
    """

    retention_policy: RetentionPolicy = Field(
        default=RetentionPolicy.TEMPORARY,
        description="How long records should be retained",
    )
    ttl: int | None = Field(
        default=None,
        ge=1,
        description="Default time-to-live in seconds for new records",
    )
    encryption_required: bool = Field(
        default=False,
        description="Whether records must be encrypted at rest",
    )
    compression_enabled: bool = Field(
        default=False,
        description="Whether records should be compressed before storage",
    )
    persistence_required: bool = Field(
        default=True,
        description="Whether records must be persisted to durable storage",
    )
    replication_required: bool = Field(
        default=False,
        description="Whether records must be replicated across nodes",
    )
    audit_enabled: bool = Field(
        default=True,
        description="Whether all memory operations should be audited",
    )


# ─────────────────────────────────────────────────────────────────────────────
# MemoryMetrics
# ─────────────────────────────────────────────────────────────────────────────


class MemoryMetrics(BaseModel):
    """Performance metrics collected by the Memory Manager.

    Tracks operational statistics across all storage tiers
    to enable monitoring, alerting, and capacity planning.
    """

    reads: int = Field(
        default=0,
        ge=0,
        description="Total read operations",
    )
    writes: int = Field(
        default=0,
        ge=0,
        description="Total write operations",
    )
    cache_hits: int = Field(
        default=0,
        ge=0,
        description="Number of cache hit events",
    )
    cache_misses: int = Field(
        default=0,
        ge=0,
        description="Number of cache miss events",
    )
    retrieval_latency: float = Field(
        default=0.0,
        ge=0.0,
        description="Average retrieval latency in milliseconds",
    )
    storage_latency: float = Field(
        default=0.0,
        ge=0.0,
        description="Average storage latency in milliseconds",
    )
    expired_records: int = Field(
        default=0,
        ge=0,
        description="Number of records that have expired",
    )
    memory_usage: dict[str, Any] = Field(
        default_factory=dict,
        description="Memory usage statistics by storage tier",
    )


# ─────────────────────────────────────────────────────────────────────────────
# ExplainabilityMetadata
# ─────────────────────────────────────────────────────────────────────────────


class ExplainabilityMetadata(BaseModel):
    """Metadata that preserves the rationale for every memory operation.

    Consumed by the Explainability Engine to provide transparency
    into why memory was created, updated, archived, restored,
    deleted, or expired, and which component/workflow/user
    triggered the operation.
    """

    why_created: str = Field(
        default="",
        description="Reason the record was created",
    )
    why_updated: str = Field(
        default="",
        description="Reason the record was last updated",
    )
    why_archived: str = Field(
        default="",
        description="Reason the record was archived",
    )
    why_restored: str = Field(
        default="",
        description="Reason the record was restored from archive",
    )
    why_deleted: str = Field(
        default="",
        description="Reason the record was deleted",
    )
    why_expired: str = Field(
        default="",
        description="Reason the record expired",
    )
    triggering_component: str = Field(
        default="",
        description="The ADIP component that triggered the operation",
    )
    triggering_workflow: str = Field(
        default="",
        description="The workflow that triggered the operation",
    )
    triggering_user: str = Field(
        default="",
        description="The user that triggered the operation",
    )
