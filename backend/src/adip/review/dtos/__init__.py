"""Data Transfer Objects for the Decision Review Layer.

DTOs provide clean separation between API contracts and
internal domain models, enabling API evolution without
affecting internal logic.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field
from pydantic.types import UUID4

from adip.review.enums import ReviewDomain, ReviewerRole, ReviewOutcome, ReviewStatus


class ReviewRequestDTO(BaseModel):
    """DTO for review API requests.

    Lightweight input DTO for the review API endpoint.
    Maps to the internal ReviewRequest domain model.
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
    domain: ReviewDomain = Field(
        default=ReviewDomain.SYSTEM,
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


class ReviewDecisionDTO(BaseModel):
    """DTO for review decision API responses.

    Lightweight DTO representing a review decision for
    API consumers.
    """

    decision_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique decision identifier",
    )
    request_id: UUID4 = Field(
        description="The request this decision belongs to",
    )
    outcome: ReviewOutcome = Field(
        description="The final outcome of the review",
    )
    review_summary: str = Field(
        default="",
        description="Summary of the review findings",
    )
    reviewer_name: str = Field(
        default="",
        description="Name of the reviewer",
    )
    reviewer_role: ReviewerRole = Field(
        default=ReviewerRole.ENGINEER,
        description="Role of the reviewer",
    )
    selected_narrative_id: str = Field(
        default="",
        description="ID of the selected narrative from explanation",
    )
    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Confidence score for the decision (0.0-1.0)",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the decision was made",
    )


class ReviewResponseDTO(BaseModel):
    """DTO for review API responses.

    Lightweight output DTO for the review API endpoint.
    Maps from the internal ReviewDecision and ReviewSession domain models.
    """

    response_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique response identifier",
    )
    request_id: UUID4 = Field(
        description="The original request identifier",
    )
    decision: ReviewDecisionDTO | None = Field(
        default=None,
        description="The review decision summary",
    )
    session_id: UUID4 = Field(
        description="The session identifier",
    )
    status: ReviewStatus = Field(
        default=ReviewStatus.INITIALIZED,
        description="Status of the review operation",
    )
    message: str = Field(
        default="",
        description="Response message",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the response was created",
    )
