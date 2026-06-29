"""Enumerations for the Decision Review Layer.

Defines all enum types used across review domain models,
contracts, and interfaces.
"""

from __future__ import annotations

from enum import StrEnum


class ReviewOutcome(StrEnum):
    """Outcome of a review decision.

    Values:
    - APPROVED: Review approved
    - REJECTED: Review rejected
    - MODIFIED: Review approved with modifications
    - MORE_INFORMATION_REQUIRED: Additional information is required
    - ESCALATED: Review escalated to higher authority
    - DEFERRED: Review deferred to a later time
    """

    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    MODIFIED = "MODIFIED"
    MORE_INFORMATION_REQUIRED = "MORE_INFORMATION_REQUIRED"
    ESCALATED = "ESCALATED"
    DEFERRED = "DEFERRED"


class ReviewerRole(StrEnum):
    """Role of a reviewer in the review process.

    Values:
    - OPERATOR: Front-line operator role
    - ENGINEER: Engineering role
    - SUPERVISOR: Supervisory role
    - MANAGER: Management role
    - ADMINISTRATOR: Administrative role
    - AUDITOR: Audit role
    """

    OPERATOR = "OPERATOR"
    ENGINEER = "ENGINEER"
    SUPERVISOR = "SUPERVISOR"
    MANAGER = "MANAGER"
    ADMINISTRATOR = "ADMINISTRATOR"
    AUDITOR = "AUDITOR"


class ApprovalWorkflowType(StrEnum):
    """Type of approval workflow for reviews.

    Values:
    - SINGLE_APPROVAL: Single reviewer approval
    - SEQUENTIAL_APPROVAL: Sequential multi-reviewer approval
    - PARALLEL_APPROVAL: Parallel multi-reviewer approval
    - MULTI_LEVEL_APPROVAL: Multi-level hierarchical approval
    - EMERGENCY_APPROVAL: Emergency fast-track approval
    """

    SINGLE_APPROVAL = "SINGLE_APPROVAL"
    SEQUENTIAL_APPROVAL = "SEQUENTIAL_APPROVAL"
    PARALLEL_APPROVAL = "PARALLEL_APPROVAL"
    MULTI_LEVEL_APPROVAL = "MULTI_LEVEL_APPROVAL"
    EMERGENCY_APPROVAL = "EMERGENCY_APPROVAL"


class ReviewStatus(StrEnum):
    """Lifecycle status for a review operation.

    Values:
    - INITIALIZED: Review has been initialized
    - UNDER_REVIEW: Review is in progress
    - PENDING_APPROVAL: Review is pending approval
    - APPROVED: Review has been approved
    - REJECTED: Review has been rejected
    - ESCALATED: Review has been escalated
    - COMPLETED: Review has been completed
    """

    INITIALIZED = "INITIALIZED"
    UNDER_REVIEW = "UNDER_REVIEW"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    ESCALATED = "ESCALATED"
    COMPLETED = "COMPLETED"


class ReviewDomain(StrEnum):
    """Domain classification for review operations.

    Values:
    - SYSTEM: System-level reviews (logs, metrics, telemetry)
    - ENERGY: Energy-related reviews (consumption, production, storage)
    - MAINTENANCE: Maintenance-related reviews (repairs, inspections, schedules)
    - OPERATIONS: Operational reviews (processes, workflows, tasks)
    - CUSTOMER: Customer-related reviews (feedback, behavior, preferences)
    - SAFETY: Safety-related reviews (incidents, hazards, compliance)
    - COMPLIANCE: Compliance reviews (regulations, audits, policies)
    - WORKFLOW: Workflow-related reviews (executions, states, transitions)
    - PLANNING: Planning-related reviews (schedules, forecasts, resources)
    - GENERAL: General domain reviews
    """

    SYSTEM = "SYSTEM"
    ENERGY = "ENERGY"
    MAINTENANCE = "MAINTENANCE"
    OPERATIONS = "OPERATIONS"
    CUSTOMER = "CUSTOMER"
    SAFETY = "SAFETY"
    COMPLIANCE = "COMPLIANCE"
    WORKFLOW = "WORKFLOW"
    PLANNING = "PLANNING"
    GENERAL = "GENERAL"
