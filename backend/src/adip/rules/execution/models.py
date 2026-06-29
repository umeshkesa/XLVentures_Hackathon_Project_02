"""Execution-layer models for the Rule Manager.

These models support internal processing: compiled rules, version
tracking, lifecycle history, trace records, and conflict reports.
They are not exposed through the public RuleService API.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import UUID4, BaseModel, Field

from adip.rules.contracts.models import Rule
from adip.rules.enums import RuleLifecycleStatus

# ─────────────────────────────────────────────────────────────────────────────
# CompiledRule
# ─────────────────────────────────────────────────────────────────────────────


class CompiledRule(BaseModel):
    """A compiled rule ready for evaluation.

    Wraps a Rule with its compiled representation including
    optimised condition trees, cached metadata, and compilation
    information.
    """

    compiled_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique compilation identifier",
    )
    rule_id: UUID4 = Field(
        description="The original rule this was compiled from",
    )
    rule: Rule = Field(
        description="The original rule",
    )
    compiled_conditions: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Optimised condition representation",
    )
    compiled_actions: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Optimised action representation",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Compilation metadata (optimisations, warnings)",
    )
    compiled_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the rule was compiled",
    )
    version: int = Field(
        default=1,
        ge=1,
        description="Rule version at compilation time",
    )


# ─────────────────────────────────────────────────────────────────────────────
# VersionRecord
# ─────────────────────────────────────────────────────────────────────────────


class VersionRecord(BaseModel):
    """A version record for a rule.

    Tracks every version of a rule including its version number,
    parent version, change summary, and active state.
    """

    version_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique version identifier",
    )
    rule_id: UUID4 = Field(
        description="The rule this version belongs to",
    )
    version_number: int = Field(
        default=1,
        ge=1,
        description="Monotonic version number",
    )
    parent_version: int | None = Field(
        default=None,
        description="The parent version this was derived from",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When this version was created",
    )
    created_by: str = Field(
        default="",
        description="User or system that created this version",
    )
    change_summary: str = Field(
        default="",
        description="Summary of changes in this version",
    )
    active: bool = Field(
        default=True,
        description="Whether this is the active version",
    )


# ─────────────────────────────────────────────────────────────────────────────
# LifecycleHistoryEntry
# ─────────────────────────────────────────────────────────────────────────────


class LifecycleHistoryEntry(BaseModel):
    """A single lifecycle transition record for a rule."""

    entry_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique history entry identifier",
    )
    rule_id: UUID4 = Field(
        description="The rule that transitioned",
    )
    from_status: RuleLifecycleStatus | None = Field(
        default=None,
        description="Previous lifecycle status",
    )
    to_status: RuleLifecycleStatus = Field(
        description="New lifecycle status",
    )
    reason: str = Field(
        default="",
        description="Reason for the transition",
    )
    changed_by: str = Field(
        default="",
        description="User or system that performed the transition",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the transition occurred",
    )


# ─────────────────────────────────────────────────────────────────────────────
# ConflictReport
# ─────────────────────────────────────────────────────────────────────────────


class ConflictReport(BaseModel):
    """A report detailing a detected rule conflict.

    Captures the conflicting rules, conflict type, description,
    and resolution applied.
    """

    report_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique report identifier",
    )
    rule_id: UUID4 = Field(
        description="The primary rule involved in the conflict",
    )
    conflicting_rule_id: UUID4 = Field(
        description="The conflicting rule",
    )
    conflict_type: str = Field(
        default="",
        description="Type of conflict (direct_overlap, priority_inversion, circular_dependency)",
    )
    description: str = Field(
        default="",
        description="Human-readable conflict description",
    )
    resolution: str = Field(
        default="",
        description="How the conflict was resolved",
    )
    resolved_by: str = Field(
        default="",
        description="Strategy that resolved the conflict",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the conflict was detected",
    )


# ─────────────────────────────────────────────────────────────────────────────
# TraceRecord
# ─────────────────────────────────────────────────────────────────────────────


class TraceRecord(BaseModel):
    """A single trace entry recording a stage in a rule operation.

    Tracks execution stage, operation type, rule context,
    timing, warnings, errors, and correlation ID for observability.
    """

    trace_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique trace identifier",
    )
    stage_name: str = Field(
        description="Name of the pipeline stage",
    )
    operation: str = Field(
        description="The operation being performed",
    )
    rule_id: UUID4 | None = Field(
        default=None,
        description="The rule involved (if applicable)",
    )
    version: int | None = Field(
        default=None,
        ge=1,
        description="Rule version involved",
    )
    lifecycle_state: str = Field(
        default="",
        description="Current lifecycle state",
    )
    domain: str = Field(
        default="",
        description="Rule domain of the operation",
    )
    evaluation_strategy: str = Field(
        default="",
        description="Evaluation strategy used",
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
    correlation_id: str = Field(
        default="",
        description="Correlation ID for distributed tracing",
    )
