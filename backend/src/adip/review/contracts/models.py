"""Domain models for the Decision Review Layer.

Defines all domain models used across review contracts,
interfaces, and execution components.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field
from pydantic.types import UUID4

from adip.review.enums import (
    ApprovalWorkflowType as ApprovalWorkflowTypeEnum,
)
from adip.review.enums import (
    ReviewDomain as ReviewDomainEnum,
)
from adip.review.enums import (
    ReviewerRole as ReviewerRoleEnum,
)
from adip.review.enums import (
    ReviewOutcome as ReviewOutcomeEnum,
)
from adip.review.enums import (
    ReviewStatus as ReviewStatusEnum,
)


class ReviewRequest(BaseModel):
    """Request to initiate a review operation.

    Captures the input parameters for a review operation,
    including the recommendation decision ID and explanation
    decision ID to review, along with contextual information.
    """

    request_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique request identifier",
    )
    recommendation_decision_id: UUID4 = Field(
        description="The recommendation decision ID to review",
    )
    explanation_decision_id: UUID4 = Field(
        description="The explanation decision ID to review",
    )
    package: ReviewPackage | None = Field(
        default=None,
        description="Optional review package with pre-aggregated data",
    )
    domain: ReviewDomainEnum = Field(
        default=ReviewDomainEnum.SYSTEM,
        description="The domain for this review operation",
    )
    priority: str = Field(
        default="MEDIUM",
        description="Priority level of the review",
    )
    deadline: datetime | None = Field(
        default=None,
        description="Deadline for completing the review",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional request metadata",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the request was created",
    )


class ReviewDecision(BaseModel):
    """Decision produced by a review operation.

    Captures the complete outcome of a review, including
    the reviewer, workflow details, and any modifications
    or comments made during the review process.
    Phase 3.5 adds quality_score, governance_confidence,
    readiness, and approved_action for Action Manager consumption.
    """

    decision_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique decision identifier",
    )
    request_id: UUID4 = Field(
        description="The request this decision belongs to",
    )
    outcome: ReviewOutcomeEnum = Field(
        description="The final outcome of the review",
    )
    review_summary: str = Field(
        default="",
        description="Summary of the review findings",
    )
    reviewer: Reviewer | None = Field(
        default=None,
        description="The reviewer who made this decision",
    )
    workflow: ApprovalWorkflow | None = Field(
        default=None,
        description="The approval workflow used",
    )
    selected_narrative_id: str = Field(
        default="",
        description="ID of the selected narrative from explanation",
    )
    modified_narrative: str = Field(
        default="",
        description="Modified narrative text if outcome is MODIFIED",
    )
    additional_comments: list[ReviewComment] = Field(
        default_factory=list,
        description="Additional comments attached to the decision",
    )
    confidence: ReviewConfidence | None = Field(
        default=None,
        description="Confidence assessment for this decision",
    )
    compliance_status: str = Field(
        default="",
        description="Compliance status check result",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional decision metadata",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the decision was made",
    )
    # Phase 3.5 fields
    approved_action: str = Field(
        default="",
        description="The approved action for Action Manager consumption",
    )
    quality_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Overall review quality score (0-1)",
    )
    governance_confidence_value: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Governance confidence score (0-1)",
    )
    readiness: ReviewReadiness | None = Field(
        default=None,
        description="Readiness assessment for this decision",
    )


class ReviewSession(BaseModel):
    """Session tracking for a review operation.

    Captures the lifecycle of a reviewer's session,
    including status transitions, timing, and escalation
    information.
    """

    session_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique session identifier",
    )
    request_id: UUID4 = Field(
        description="The request this session belongs to",
    )
    reviewer_id: str = Field(
        default="",
        description="Identifier of the reviewer",
    )
    role: ReviewerRoleEnum = Field(
        description="Role of the reviewer in this session",
    )
    status: ReviewStatusEnum = Field(
        default=ReviewStatusEnum.INITIALIZED,
        description="Current status of the session",
    )
    started_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the session was started",
    )
    completed_at: datetime | None = Field(
        default=None,
        description="When the session was completed",
    )
    assigned_at: datetime | None = Field(
        default=None,
        description="When the reviewer was assigned",
    )
    target_outcome: ReviewOutcomeEnum | None = Field(
        default=None,
        description="Target outcome expected from this session",
    )
    escalation_reason: str = Field(
        default="",
        description="Reason for escalation if applicable",
    )
    statistics: dict[str, Any] = Field(
        default_factory=dict,
        description="Session statistics",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional session metadata",
    )


class ReviewPackage(BaseModel):
    """Package containing pre-aggregated review data.

    Bundles recommendation and explanation decisions with
    summaries and policy information for efficient review.
    """

    package_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique package identifier",
    )
    request_id: UUID4 = Field(
        description="The request this package belongs to",
    )
    recommendation_decision: dict[str, Any] = Field(
        default_factory=dict,
        description="The recommendation decision data",
    )
    explanation_decision: dict[str, Any] = Field(
        default_factory=dict,
        description="The explanation decision data",
    )
    evidence_summary: str = Field(
        default="",
        description="Summary of evidence considered",
    )
    reasoning_summary: str = Field(
        default="",
        description="Summary of reasoning applied",
    )
    recommendation_summary: str = Field(
        default="",
        description="Summary of the recommendation",
    )
    policy_information: dict[str, Any] = Field(
        default_factory=dict,
        description="Policy information relevant to the review",
    )
    review_notes: list[str] = Field(
        default_factory=list,
        description="Notes added during review assembly",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional package metadata",
    )


class ReviewContext(BaseModel):
    """Contextual information for a review operation.

    Provides asset, machine, facility, and workflow context
    to inform the review process.
    """

    context_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique context identifier",
    )
    review_id: UUID4 = Field(
        description="The review this context belongs to",
    )
    recommendation_context: dict[str, Any] = Field(
        default_factory=dict,
        description="Context from the recommendation engine",
    )
    explanation_context: dict[str, Any] = Field(
        default_factory=dict,
        description="Context from the explanation engine",
    )
    asset_id: str = Field(
        default="",
        description="Identifier of the related asset",
    )
    machine_id: str = Field(
        default="",
        description="Identifier of the related machine",
    )
    facility_id: str = Field(
        default="",
        description="Identifier of the related facility",
    )
    workflow_id: str = Field(
        default="",
        description="Identifier of the related workflow",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context metadata",
    )


class ReviewPolicy(BaseModel):
    """Policy configuration for a review operation.

    Defines the rules and constraints governing how a review
    should be conducted, including allowed outcomes, required
    reviewer roles, and escalation rules.
    """

    policy_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique policy identifier",
    )
    name: str = Field(
        default="",
        description="Name of the review policy",
    )
    description: str = Field(
        default="",
        description="Description of the review policy",
    )
    allowed_outcomes: list[ReviewOutcomeEnum] = Field(
        default_factory=list,
        description="List of allowed review outcomes",
    )
    required_reviewer_roles: list[ReviewerRoleEnum] = Field(
        default_factory=list,
        description="Roles required to conduct the review",
    )
    max_reviewers: int = Field(
        default=3,
        ge=1,
        description="Maximum number of reviewers allowed",
    )
    require_justification: bool = Field(
        default=True,
        description="Whether justification is required",
    )
    require_evidence: bool = Field(
        default=True,
        description="Whether evidence is required",
    )
    enforce_deadline: bool = Field(
        default=False,
        description="Whether deadlines are enforced",
    )
    escalation_rule_id: str = Field(
        default="",
        description="Identifier of the escalation rule to apply",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional policy metadata",
    )


class ReviewOutcome(BaseModel):
    """Full outcome tracking model for a review.

    Captures the complete outcome details including the
    reason, justification, and supporting evidence for
    why a particular outcome was reached.
    """

    outcome_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique outcome identifier",
    )
    decision_id: UUID4 = Field(
        description="The decision this outcome belongs to",
    )
    outcome: ReviewOutcomeEnum = Field(
        description="The review outcome",
    )
    reason: str = Field(
        default="",
        description="Reason for the outcome",
    )
    justification: str = Field(
        default="",
        description="Detailed justification for the outcome",
    )
    supporting_evidence: list[str] = Field(
        default_factory=list,
        description="Evidence supporting this outcome",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the outcome was recorded",
    )


class Reviewer(BaseModel):
    """Reviewer profile information.

    Represents a human or automated reviewer with their
    credentials, role, and capacity constraints.
    """

    reviewer_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique reviewer identifier",
    )
    name: str = Field(
        default="",
        description="Name of the reviewer",
    )
    email: str = Field(
        default="",
        description="Email address of the reviewer",
    )
    role: ReviewerRoleEnum = Field(
        description="Role of the reviewer",
    )
    department: str = Field(
        default="",
        description="Department of the reviewer",
    )
    is_active: bool = Field(
        default=True,
        description="Whether the reviewer is currently active",
    )
    certifications: list[str] = Field(
        default_factory=list,
        description="Certifications held by the reviewer",
    )
    max_concurrent_reviews: int = Field(
        default=5,
        ge=1,
        description="Maximum number of concurrent reviews allowed",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional reviewer metadata",
    )


class ReviewerRole(BaseModel):
    """Role definition model for the review process.

    Defines a specific reviewer role with its permissions,
    display name, and certification requirements.
    """

    role_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique role identifier",
    )
    role: ReviewerRoleEnum = Field(
        description="The reviewer role enum value",
    )
    display_name: str = Field(
        default="",
        description="Human-readable display name for the role",
    )
    permissions: list[str] = Field(
        default_factory=list,
        description="Permissions granted to this role",
    )
    requires_certification: bool = Field(
        default=False,
        description="Whether this role requires certification",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional role metadata",
    )


class ReviewComment(BaseModel):
    """Comment attached to a review decision.

    Captures reviewer feedback on specific sections of the
    review, with resolution tracking.
    """

    comment_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique comment identifier",
    )
    decision_id: UUID4 = Field(
        description="The decision this comment belongs to",
    )
    reviewer_id: UUID4 = Field(
        description="The reviewer who made the comment",
    )
    comment: str = Field(
        default="",
        description="The comment text",
    )
    section: str = Field(
        default="",
        description="The section of the review this comment refers to",
    )
    is_resolved: bool = Field(
        default=False,
        description="Whether this comment has been resolved",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the comment was created",
    )
    resolved_at: datetime | None = Field(
        default=None,
        description="When the comment was resolved",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional comment metadata",
    )


class ReviewAudit(BaseModel):
    """Audit log entry for a review operation.

    Records actions performed during the review process
    for compliance and traceability.
    """

    audit_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique audit identifier",
    )
    decision_id: UUID4 = Field(
        description="The decision this audit entry belongs to",
    )
    reviewer_id: UUID4 = Field(
        description="The reviewer who performed the action",
    )
    action: str = Field(
        default="",
        description="The action performed",
    )
    previous_status: ReviewStatusEnum | None = Field(
        default=None,
        description="Previous status before the action",
    )
    new_status: ReviewStatusEnum | None = Field(
        default=None,
        description="New status after the action",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the action occurred",
    )
    ip_address: str = Field(
        default="",
        description="IP address of the reviewer",
    )
    user_agent: str = Field(
        default="",
        description="User agent of the reviewer's client",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional audit metadata",
    )


class ReviewConfidence(BaseModel):
    """Confidence assessment for a review decision.

    Multi-dimensional confidence score capturing the quality
    of the recommendation, explanation, reviewer expertise,
    and compliance.
    """

    overall_confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Overall confidence score (0-1)",
    )
    recommendation_quality: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Quality of the recommendation (0-1)",
    )
    explanation_quality: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Quality of the explanation (0-1)",
    )
    reviewer_expertise: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Expertise level of the reviewer (0-1)",
    )
    compliance_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Compliance score for the decision (0-1)",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional confidence metadata",
    )


class ReviewMetadata(BaseModel):
    """Metadata describing a review operation.

    Provides classification, tagging, and versioning
    information for review entities.
    """

    title: str = Field(
        default="",
        description="Title of the review",
    )
    description: str = Field(
        default="",
        description="Description of the review",
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Tags for categorizing the review",
    )
    category: str = Field(
        default="",
        description="Category of the review",
    )
    priority: str = Field(
        default="",
        description="Priority of the review",
    )
    source: str = Field(
        default="",
        description="Source system of the review",
    )
    version: str = Field(
        default="1.0.0",
        description="Version of the review schema",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata",
    )


class ReviewHealth(BaseModel):
    """Health status for the review system.

    Provides a comprehensive view of the health of all
    review sub-components and overall system status.
    """

    overall_status: str = Field(
        default="",
        description="Overall health status",
    )
    service_status: str = Field(
        default="",
        description="Status of the review service",
    )
    manager_status: str = Field(
        default="",
        description="Status of the review manager",
    )
    coordinator_status: str = Field(
        default="",
        description="Status of the review coordinator",
    )
    validator_status: str = Field(
        default="",
        description="Status of the review validator",
    )
    policy_status: str = Field(
        default="",
        description="Status of the review policy engine",
    )
    escalation_status: str = Field(
        default="",
        description="Status of the escalation system",
    )
    approval_status: str = Field(
        default="",
        description="Status of the approval workflow",
    )
    audit_status: str = Field(
        default="",
        description="Status of the audit system",
    )
    assignment_status: str = Field(
        default="",
        description="Status of the reviewer assignment system",
    )
    workflow_status: str = Field(
        default="",
        description="Status of the workflow system",
    )
    consensus_status: str = Field(
        default="",
        description="Status of the consensus system",
    )
    delegation_status: str = Field(
        default="",
        description="Status of the delegation system",
    )
    readiness_status: str = Field(
        default="",
        description="Status of the readiness assessment system",
    )
    version_status: str = Field(
        default="",
        description="Status of the version management system",
    )
    lineage_status: str = Field(
        default="",
        description="Status of the lineage tracking system",
    )
    consensus_manager_status: str = Field(
        default="",
        description="Status of the reviewer consensus manager",
    )
    delegation_manager_status: str = Field(
        default="",
        description="Status of the delegation manager",
    )
    compliance_status: str = Field(
        default="",
        description="Status of the compliance manager",
    )
    quality_status: str = Field(
        default="",
        description="Status of the quality manager",
    )
    review_count: int = Field(
        default=0,
        ge=0,
        description="Total number of reviews processed",
    )
    error_count: int = Field(
        default=0,
        ge=0,
        description="Total number of errors encountered",
    )
    average_latency_ms: float = Field(
        default=0.0,
        ge=0.0,
        description="Average review latency in milliseconds",
    )
    last_check: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the health was last checked",
    )


class ReviewMetrics(BaseModel):
    """Metrics for the review system.

    Captures operational metrics including review counts,
    outcomes distribution, timing, domain/role breakdowns,
    and governance-specific metrics.
    """

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
    pending_total: int = Field(
        default=0,
        ge=0,
        description="Total number of pending reviews",
    )
    modified_total: int = Field(
        default=0,
        ge=0,
        description="Total number of modified reviews",
    )
    deferred_total: int = Field(
        default=0,
        ge=0,
        description="Total number of deferred reviews",
    )
    approval_rate: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Approval rate as percentage (0-100)",
    )
    rejection_rate: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Rejection rate as percentage (0-100)",
    )
    escalation_rate: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Escalation rate as percentage (0-100)",
    )
    average_review_time_ms: float = Field(
        default=0.0,
        ge=0.0,
        description="Average review time in milliseconds",
    )
    average_confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Average confidence score (0-1)",
    )
    sla_compliance_rate: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="SLA compliance rate as percentage (0-100)",
    )
    average_governance_confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Average governance confidence score (0-1)",
    )
    reviews_per_domain: dict[str, int] = Field(
        default_factory=dict,
        description="Number of reviews per domain",
    )
    reviews_per_role: dict[str, int] = Field(
        default_factory=dict,
        description="Number of reviews per reviewer role",
    )
    audits_total: int = Field(
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
    governance_quality: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Average governance quality score (0-1)",
    )
    compliance_total: int = Field(
        default=0,
        ge=0,
        description="Total number of compliance checks performed",
    )
    compliance_failures: int = Field(
        default=0,
        ge=0,
        description="Total number of compliance check failures",
    )
    exports_total: int = Field(
        default=0,
        ge=0,
        description="Total number of export packages created",
    )
    snapshots_total: int = Field(
        default=0,
        ge=0,
        description="Total number of review snapshots created",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the metrics were captured",
    )


class EscalationRule(BaseModel):
    """Rule defining when and how a review should be escalated.

    Specifies triggers for escalation including outcome,
    role, duration, and the target escalation role.
    """

    rule_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique rule identifier",
    )
    name: str = Field(
        default="",
        description="Name of the escalation rule",
    )
    description: str = Field(
        default="",
        description="Description of the escalation rule",
    )
    trigger_outcome: ReviewOutcomeEnum | None = Field(
        default=None,
        description="Outcome that triggers escalation",
    )
    trigger_role: ReviewerRoleEnum | None = Field(
        default=None,
        description="Reviewer role that triggers escalation",
    )
    max_duration_minutes: int = Field(
        default=0,
        ge=0,
        description="Maximum duration before escalation in minutes",
    )
    escalation_role: ReviewerRoleEnum = Field(
        description="The role to escalate to",
    )
    notify_roles: list[ReviewerRoleEnum] = Field(
        default_factory=list,
        description="Roles to notify on escalation",
    )
    is_active: bool = Field(
        default=True,
        description="Whether this rule is currently active",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional rule metadata",
    )


class ApprovalWorkflow(BaseModel):
    """Workflow definition for approval processes.

    Defines the sequence and configuration of approval
    steps including workflow type, required approvals,
    and deadline constraints.
    """

    workflow_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique workflow identifier",
    )
    name: str = Field(
        default="",
        description="Name of the approval workflow",
    )
    workflow_type: ApprovalWorkflowTypeEnum = Field(
        description="Type of the approval workflow",
    )
    description: str = Field(
        default="",
        description="Description of the approval workflow",
    )
    steps: list[dict[str, Any]] = Field(
        default_factory=list,
        description=(
            "Approval steps each containing role, order, and required fields"
        ),
    )
    required_approvals: int = Field(
        default=1,
        ge=1,
        description="Number of approvals required to complete",
    )
    auto_approve: bool = Field(
        default=False,
        description="Whether auto-approval is enabled",
    )
    deadline_minutes: int = Field(
        default=0,
        ge=0,
        description="Deadline for completion in minutes",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional workflow metadata",
    )


class GovernanceConfidence(BaseModel):
    """Governance confidence for a review operation.

    Six-dimension governance confidence capturing AI confidence,
    reviewer confidence, policy compliance, consensus, workflow
    completion, and SLA compliance scores.
    Phase 3.5 adds sla_compliance dimension.
    """

    overall_governance_confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Overall governance confidence score (0-1)",
    )
    ai_confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Confidence in the AI recommendation (0-1)",
    )
    reviewer_confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Confidence based on reviewer expertise (0-1)",
    )
    policy_compliance: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Policy compliance score (0-1)",
    )
    consensus_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Consensus score between reviewers (0-1)",
    )
    workflow_completion: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Workflow completion score (0-1)",
    )
    sla_compliance: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="SLA compliance score (0-1)",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional governance confidence metadata",
    )


class ReviewReadiness(BaseModel):
    """Readiness assessment for a review operation.

    Determines whether a review is ready to proceed, is blocked,
    needs escalation, or requires more information.
    """

    readiness_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique readiness identifier",
    )
    decision_id: UUID4 = Field(
        description="The decision this readiness belongs to",
    )
    status: str = Field(
        default="PENDING",
        description="Readiness status: READY, PENDING, BLOCKED, ESCALATED, MORE_INFORMATION_REQUIRED",
    )
    reason: str = Field(
        default="",
        description="Reason for the readiness assessment",
    )
    checklist_complete: bool = Field(
        default=False,
        description="Whether all checklist items are complete",
    )
    sla_compliant: bool = Field(
        default=True,
        description="Whether the review is SLA-compliant",
    )
    reviewers_assigned: bool = Field(
        default=False,
        description="Whether all required reviewers are assigned",
    )
    policy_compliant: bool = Field(
        default=True,
        description="Whether the review is policy-compliant",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional readiness metadata",
    )


class GovernanceAuditPackage(BaseModel):
    """Immutable audit package for a governance review.

    Packages the complete review record including the review
    package, reviewer decisions, comments, workflow, timeline,
    and policy evaluations for audit purposes.
    """

    package_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique audit package identifier",
    )
    decision_id: UUID4 = Field(
        description="The decision this audit package belongs to",
    )
    review_package: dict[str, Any] = Field(
        default_factory=dict,
        description="The original review package data",
    )
    reviewer_decisions: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Decisions made by each reviewer",
    )
    comments: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Reviewer comments captured during review",
    )
    workflow: dict[str, Any] = Field(
        default_factory=dict,
        description="The approval workflow details",
    )
    timeline: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Timeline of review events",
    )
    policy_evaluations: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Policy evaluation results",
    )
    hash: str = Field(
        default="",
        description="Immutable hash for audit integrity",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the audit package was created",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional audit package metadata",
    )


class GovernanceLineage(BaseModel):
    """Lineage tracking for governance decisions.

    Tracks the complete chain from recommendation through
    explanation, review, and final action for full governance
    traceability.
    """

    lineage_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique lineage identifier",
    )
    decision_id: UUID4 = Field(
        description="The decision this lineage belongs to",
    )
    recommendation_id: str = Field(
        default="",
        description="ID of the originating recommendation",
    )
    explanation_id: str = Field(
        default="",
        description="ID of the explanation",
    )
    review_id: str = Field(
        default="",
        description="ID of the review operation",
    )
    action_id: str = Field(
        default="",
        description="ID of the final action taken",
    )
    chain: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Complete lineage chain entries",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional lineage metadata",
    )


class ReviewExplainabilityMetadata(BaseModel):
    """Explainability metadata for a review decision.

    Captures why-fields explaining the reasoning behind
    the review outcome, workflow selection, reviewer assignment,
    confidence assessment, and policy decisions.
    """

    why_outcome_selected: str = Field(
        default="",
        description="Why this review outcome was selected",
    )
    why_workflow_selected: str = Field(
        default="",
        description="Why this approval workflow was chosen",
    )
    why_reviewer_assigned: str = Field(
        default="",
        description="Why this reviewer was assigned",
    )
    why_confidence_assessed: str = Field(
        default="",
        description="Why the confidence score is as calculated",
    )
    why_policy_applied: str = Field(
        default="",
        description="Why this policy was applied to the review",
    )
    why_escalation_triggered: str = Field(
        default="",
        description="Why an escalation was triggered (if any)",
    )
    why_assigned: str = Field(
        default="",
        description="Why the reviewer was assigned",
    )
    why_escalated: str = Field(
        default="",
        description="Why the review was escalated",
    )
    why_modified: str = Field(
        default="",
        description="Why the review was modified",
    )
    why_rejected: str = Field(
        default="",
        description="Why the review was rejected",
    )
    why_approved: str = Field(
        default="",
        description="Why the review was approved",
    )
    why_delegated: str = Field(
        default="",
        description="Why the review was delegated",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional explainability metadata",
    )
