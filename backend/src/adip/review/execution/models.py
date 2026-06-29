"""Execution-layer models for the Decision Review Layer.

These models support internal processing: policy matrix results,
reviewer assignments, modification tracking, escalation records,
SLA monitoring, conflict resolution, timeline events, checklist
items, governance metrics, and trace records.
They are not exposed through the public ReviewService API.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import UUID4, BaseModel, Field

# ─────────────────────────────────────────────────────────────────────────────
# PolicyMatrixResult
# ─────────────────────────────────────────────────────────────────────────────


class PolicyMatrixResult(BaseModel):
    """Result of evaluating a review request against the policy matrix.

    Determines the recommended workflow, confidence level, risk,
    impact, criticality, compliance requirements, and escalation
    needs based on the input parameters.
    """

    matrix_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique matrix result identifier",
    )
    recommended_workflow: str = Field(
        default="SINGLE_REVIEW",
        description="Recommended approval workflow type",
    )
    confidence_level: str = Field(
        default="MEDIUM",
        description="Confidence level of the recommendation",
    )
    risk_level: str = Field(
        default="MEDIUM",
        description="Risk level assessment",
    )
    impact_level: str = Field(
        default="MEDIUM",
        description="Impact level assessment",
    )
    criticality_level: str = Field(
        default="MEDIUM",
        description="Criticality level assessment",
    )
    compliance_required: bool = Field(
        default=True,
        description="Whether compliance review is required",
    )
    requires_escalation: bool = Field(
        default=False,
        description="Whether escalation is required",
    )
    justification: str = Field(
        default="",
        description="Justification for the matrix decision",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the matrix result was generated",
    )


# ─────────────────────────────────────────────────────────────────────────────
# ReviewerAssignment
# ─────────────────────────────────────────────────────────────────────────────


class ReviewerAssignment(BaseModel):
    """Assignment record for a reviewer.

    Tracks the reviewer's identity, role, expertise, workload,
    availability, and authority level for a specific review.
    """

    assignment_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique assignment identifier",
    )
    reviewer_id: str = Field(
        default="",
        description="Identifier of the assigned reviewer",
    )
    reviewer_name: str = Field(
        default="",
        description="Name of the assigned reviewer",
    )
    reviewer_role: str = Field(
        default="",
        description="Role of the assigned reviewer",
    )
    expertise_score: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Expertise score of the reviewer (0-1)",
    )
    current_workload: int = Field(
        default=0,
        ge=0,
        description="Current number of active reviews for this reviewer",
    )
    is_available: bool = Field(
        default=True,
        description="Whether the reviewer is currently available",
    )
    authority_level: str = Field(
        default="STANDARD",
        description="Authority level of the reviewer",
    )
    assigned_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the reviewer was assigned",
    )


# ─────────────────────────────────────────────────────────────────────────────
# ModificationRecord
# ─────────────────────────────────────────────────────────────────────────────


class ModificationRecord(BaseModel):
    """Record of a modification made to a review decision.

    Captures what was changed, the previous and new values,
    the reason for the change, and who performed it.
    """

    modification_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique modification identifier",
    )
    decision_id: UUID4 = Field(
        description="The decision that was modified",
    )
    modification_type: str = Field(
        default="",
        description="Type of modification (e.g., narrative, outcome, metadata)",
    )
    previous_value: str = Field(
        default="",
        description="Previous value before modification",
    )
    new_value: str = Field(
        default="",
        description="New value after modification",
    )
    reason: str = Field(
        default="",
        description="Reason for the modification",
    )
    modified_by: str = Field(
        default="",
        description="User or system that performed the modification",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the modification was made",
    )


# ─────────────────────────────────────────────────────────────────────────────
# EscalationRecord
# ─────────────────────────────────────────────────────────────────────────────


class EscalationRecord(BaseModel):
    """Record of a review escalation.

    Tracks the reason, type, severity, roles involved,
    and resolution status of an escalation event.
    """

    escalation_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique escalation identifier",
    )
    review_id: str = Field(
        default="",
        description="Identifier of the escalated review",
    )
    reason: str = Field(
        default="",
        description="Reason for the escalation",
    )
    escalation_type: str = Field(
        default="",
        description="Type of escalation (e.g., role, severity, deadline)",
    )
    triggered_by: str = Field(
        default="",
        description="User or system that triggered the escalation",
    )
    from_role: str = Field(
        default="",
        description="Role the escalation originated from",
    )
    to_role: str = Field(
        default="",
        description="Role the escalation was directed to",
    )
    severity: str = Field(
        default="MEDIUM",
        description="Severity level of the escalation",
    )
    resolved: bool = Field(
        default=False,
        description="Whether the escalation has been resolved",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the escalation was created",
    )
    resolved_at: datetime | None = Field(
        default=None,
        description="When the escalation was resolved",
    )


# ─────────────────────────────────────────────────────────────────────────────
# SLARecord
# ─────────────────────────────────────────────────────────────────────────────


class SLARecord(BaseModel):
    """Service Level Agreement tracking record for a review.

    Monitors review deadlines, remaining time, breach status,
    and auto-escalation triggers for SLA compliance.
    """

    sla_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique SLA record identifier",
    )
    review_id: str = Field(
        default="",
        description="Identifier of the review being tracked",
    )
    started_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the SLA tracking started",
    )
    deadline_at: datetime | None = Field(
        default=None,
        description="Absolute deadline for the review",
    )
    sla_minutes: int = Field(
        default=60,
        ge=1,
        description="SLA duration in minutes",
    )
    remaining_minutes: float = Field(
        default=60.0,
        ge=0.0,
        description="Remaining minutes before SLA breach",
    )
    is_breached: bool = Field(
        default=False,
        description="Whether the SLA has been breached",
    )
    auto_escalate: bool = Field(
        default=False,
        description="Whether to auto-escalate on breach",
    )
    breached_at: datetime | None = Field(
        default=None,
        description="When the SLA was breached",
    )


# ─────────────────────────────────────────────────────────────────────────────
# ConflictResolutionResult
# ─────────────────────────────────────────────────────────────────────────────


class ConflictResolutionResult(BaseModel):
    """Result of resolving a conflict between reviews or reviewers.

    Captures voting outcomes, tie-breaking, and the final
    resolution of a conflict.
    """

    conflict_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique conflict resolution identifier",
    )
    review_ids: list[str] = Field(
        default_factory=list,
        description="Identifiers of the conflicting reviews",
    )
    conflict_type: str = Field(
        default="",
        description="Type of conflict (vote_standoff, contradictory_outcomes, etc.)",
    )
    votes_for: int = Field(
        default=0,
        ge=0,
        description="Number of votes in favour",
    )
    votes_against: int = Field(
        default=0,
        ge=0,
        description="Number of votes against",
    )
    tie_broken: bool = Field(
        default=False,
        description="Whether a tie was broken",
    )
    tie_breaker_role: str = Field(
        default="",
        description="Role that broke the tie if applicable",
    )
    outcome: str = Field(
        default="",
        description="Final outcome of the conflict resolution",
    )
    resolution: str = Field(
        default="",
        description="Detailed resolution description",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the conflict was resolved",
    )


# ─────────────────────────────────────────────────────────────────────────────
# TimelineEvent
# ─────────────────────────────────────────────────────────────────────────────


class TimelineEvent(BaseModel):
    """An event recorded on a review timeline.

    Provides a chronological record of actions and events
    during the review lifecycle.
    """

    event_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique event identifier",
    )
    review_id: str = Field(
        default="",
        description="Identifier of the review this event belongs to",
    )
    event_type: str = Field(
        default="",
        description="Type of event (created, assigned, commented, escalated, etc.)",
    )
    description: str = Field(
        default="",
        description="Human-readable description of the event",
    )
    performed_by: str = Field(
        default="",
        description="User or system that performed the event",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the event occurred",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional event metadata",
    )


# ─────────────────────────────────────────────────────────────────────────────
# ChecklistItem
# ─────────────────────────────────────────────────────────────────────────────


class ChecklistItem(BaseModel):
    """A checklist item for a review operation.

    Tracks completion status, who completed it, and whether
    the item is mandatory.
    """

    item_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique checklist item identifier",
    )
    review_id: str = Field(
        default="",
        description="Identifier of the review this item belongs to",
    )
    item_name: str = Field(
        default="",
        description="Name of the checklist item",
    )
    description: str = Field(
        default="",
        description="Description of what needs to be checked",
    )
    is_complete: bool = Field(
        default=False,
        description="Whether this item has been completed",
    )
    completed_by: str = Field(
        default="",
        description="User who completed this item",
    )
    completed_at: datetime | None = Field(
        default=None,
        description="When this item was completed",
    )
    required: bool = Field(
        default=True,
        description="Whether this item is mandatory",
    )


# ─────────────────────────────────────────────────────────────────────────────
# GovernanceMetricsSnapshot
# ─────────────────────────────────────────────────────────────────────────────


class GovernanceMetricsSnapshot(BaseModel):
    """Snapshot of governance metrics for the review system.

    Captures review counts, approval/rejection/escalation rates,
    average review time, SLA compliance, breach statistics,
    and Phase 3 governance metrics at a point in time.
    """

    snapshot_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique snapshot identifier",
    )
    reviews_total: int = Field(
        default=0,
        ge=0,
        description="Total number of reviews",
    )
    approved_total: int = Field(
        default=0,
        ge=0,
        description="Total number of approved reviews",
    )
    rejected_total: int = Field(
        default=0,
        ge=0,
        description="Total number of rejected reviews",
    )
    escalated_total: int = Field(
        default=0,
        ge=0,
        description="Total number of escalated reviews",
    )
    modified_total: int = Field(
        default=0,
        ge=0,
        description="Total number of modified reviews",
    )
    approval_rate: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Approval rate as a percentage (0-100)",
    )
    rejection_rate: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Rejection rate as a percentage (0-100)",
    )
    escalation_rate: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Escalation rate as a percentage (0-100)",
    )
    average_review_time_ms: float = Field(
        default=0.0,
        ge=0.0,
        description="Average review time in milliseconds",
    )
    sla_compliance_rate: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="SLA compliance rate as a percentage (0-100)",
    )
    sla_breaches: int = Field(
        default=0,
        ge=0,
        description="Total number of SLA breaches",
    )
    # Phase 3 fields
    average_governance_confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Average governance confidence score (0-1)",
    )
    audit_packages_total: int = Field(
        default=0,
        ge=0,
        description="Total number of audit packages created",
    )
    versions_total: int = Field(
        default=0,
        ge=0,
        description="Total number of versions created",
    )
    delegations_total: int = Field(
        default=0,
        ge=0,
        description="Total number of delegations performed",
    )
    consensus_evaluations: int = Field(
        default=0,
        ge=0,
        description="Total number of consensus evaluations",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the snapshot was taken",
    )


# ─────────────────────────────────────────────────────────────────────────────
# TraceRecord
# ─────────────────────────────────────────────────────────────────────────────


class TraceRecord(BaseModel):
    """A single trace entry for a review operation stage.

    Records stage execution including timing, success status,
    performer, details, and correlation ID for observability.
    """

    trace_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique trace identifier",
    )
    review_id: str = Field(
        default="",
        description="Identifier of the review being traced",
    )
    stage_name: str = Field(
        default="",
        description="Name of the pipeline stage",
    )
    operation: str = Field(
        default="",
        description="The operation being performed",
    )
    performed_by: str = Field(
        default="",
        description="User or system that performed the operation",
    )
    details: str = Field(
        default="",
        description="Detailed description of the operation",
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
    correlation_id: str = Field(
        default="",
        description="Correlation ID for distributed tracing",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the trace entry was created",
    )
