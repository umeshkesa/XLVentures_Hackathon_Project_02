"""Event definitions for the Decision Review Layer.

Defines all event types emitted during review operations
for observability, auditing, and integration hooks.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from pydantic import BaseModel, Field
from pydantic.types import UUID4

from adip.review.enums import ApprovalWorkflowType, ReviewDomain, ReviewerRole, ReviewOutcome


class ReviewEvent(BaseModel):
    """Base event for review operations.

    All review events inherit from this base class,
    providing common fields for event correlation.
    """

    event_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique event identifier",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the event occurred",
    )
    correlation_id: str = Field(
        default="",
        description="Correlation ID for distributed tracing",
    )


class ReviewRequested(ReviewEvent):
    """Emitted when a review is requested."""

    request_id: UUID4 = Field(
        description="The request identifier",
    )
    domain: ReviewDomain = Field(
        default=ReviewDomain.SYSTEM,
        description="The domain for this review operation",
    )


class ReviewStarted(ReviewEvent):
    """Emitted when a review session starts."""

    session_id: UUID4 = Field(
        description="The session identifier",
    )
    reviewer_id: str = Field(
        default="",
        description="Identifier of the reviewer",
    )
    role: ReviewerRole = Field(
        description="Role of the reviewer in this session",
    )


class ReviewCompleted(ReviewEvent):
    """Emitted when a review session completes."""

    session_id: UUID4 = Field(
        description="The session identifier",
    )
    outcome: ReviewOutcome = Field(
        description="The final outcome of the review",
    )
    duration_ms: float = Field(
        default=0.0,
        ge=0.0,
        description="Duration of the review in milliseconds",
    )


class ReviewEscalated(ReviewEvent):
    """Emitted when a review is escalated."""

    session_id: UUID4 = Field(
        description="The session identifier",
    )
    reason: str = Field(
        default="",
        description="Reason for the escalation",
    )
    escalated_to_role: ReviewerRole = Field(
        description="The role the review was escalated to",
    )


class ReviewApproved(ReviewEvent):
    """Emitted when a review is approved."""

    session_id: UUID4 = Field(
        description="The session identifier",
    )
    approval_workflow_type: ApprovalWorkflowType = Field(
        description="The approval workflow type used",
    )
    approved_by: str = Field(
        default="",
        description="Identifier of the approver",
    )


class ReviewRejected(ReviewEvent):
    """Emitted when a review is rejected."""

    session_id: UUID4 = Field(
        description="The session identifier",
    )
    reason: str = Field(
        default="",
        description="Reason for the rejection",
    )
    rejected_by: str = Field(
        default="",
        description="Identifier of the reviewer who rejected",
    )
