"""Event definitions for the Recommendation Engine.

Defines all event types emitted during recommendation operations
for observability, auditing, and integration hooks.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field


class RecommendationEvent(BaseModel):
    """Base event for recommendation operations.

    All recommendation events inherit from this base class,
    providing common fields for event correlation.
    """

    event_type: str = Field(
        default="",
        description="The type of recommendation event",
    )
    recommendation_id: str = Field(
        default="",
        description="The recommendation operation identifier",
    )
    correlation_id: str = Field(
        default="",
        description="Correlation ID for distributed tracing",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the event occurred",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional event metadata",
    )


class RecommendationRequested(RecommendationEvent):
    """Emitted when a recommendation operation starts."""

    event_type: str = "recommendation.requested"
    domain: str = Field(
        default="",
        description="The domain for the recommendation operation",
    )
    strategy: str = Field(
        default="",
        description="The strategy used for recommendation",
    )
    goals: list[str] = Field(
        default_factory=list,
        description="The goals for the recommendation operation",
    )


class RecommendationGenerated(RecommendationEvent):
    """Emitted when recommendation candidates are generated."""

    event_type: str = "recommendation.generated"
    candidate_count: int = Field(
        default=0,
        ge=0,
        description="Total number of candidates generated",
    )
    primary_candidate_id: str = Field(
        default="",
        description="The primary recommendation candidate identifier",
    )


class RecommendationRanked(RecommendationEvent):
    """Emitted when recommendation candidates are ranked."""

    event_type: str = "recommendation.ranked"
    ranked_candidate_ids: list[str] = Field(
        default_factory=list,
        description="Ranked list of candidate identifiers",
    )
    best_candidate_id: str = Field(
        default="",
        description="The best-ranked candidate identifier",
    )


class RecommendationValidated(RecommendationEvent):
    """Emitted when a recommendation is validated."""

    event_type: str = "recommendation.validated"
    validator: str = Field(
        default="",
        description="The validator that performed the validation",
    )
    passed: bool = Field(
        default=False,
        description="Whether validation passed",
    )
    violations: list[str] = Field(
        default_factory=list,
        description="List of validation violations",
    )


class RecommendationCompleted(RecommendationEvent):
    """Emitted when a recommendation operation completes."""

    event_type: str = "recommendation.completed"
    status: str = Field(
        default="",
        description="Final status of the recommendation operation",
    )
    result_id: str = Field(
        default="",
        description="The recommendation result identifier",
    )
    duration_ms: float = Field(
        default=0.0,
        ge=0.0,
        description="Total duration of the recommendation operation in milliseconds",
    )
