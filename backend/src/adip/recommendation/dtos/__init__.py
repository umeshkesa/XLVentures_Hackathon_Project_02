"""Data Transfer Objects for the Recommendation Engine.

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

from adip.recommendation.enums import (
    RecommendationDomain,
    RecommendationStatus,
    RecommendationStrategy,
)


class RecommendationRequestDTO(BaseModel):
    """DTO for recommendation API requests.

    Lightweight input DTO for the recommendation API endpoint.
    Maps to the internal RecommendationRequest domain model.
    """

    reasoning_result_id: str = Field(
        description="The reasoning result ID to transform into recommendations",
    )
    domain: RecommendationDomain = Field(
        default=RecommendationDomain.GENERAL,
        description="The domain for this recommendation operation",
    )
    strategy: RecommendationStrategy = Field(
        default=RecommendationStrategy.NEXT_BEST_ACTION,
        description="The recommendation strategy to apply",
    )
    context: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context for the recommendation operation",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional request metadata",
    )


class RecommendationResponseDTO(BaseModel):
    """DTO for recommendation API responses.

    Lightweight output DTO for the recommendation API endpoint.
    Maps from the internal RecommendationResult domain model.
    """

    result_id: UUID4 = Field(
        description="The recommendation result identifier",
    )
    request_id: UUID4 = Field(
        description="The original request identifier",
    )
    decision: dict[str, Any] = Field(
        default_factory=dict,
        description="The recommendation decision summary",
    )
    candidates_count: int = Field(
        default=0,
        ge=0,
        description="Number of candidates generated",
    )
    packages_count: int = Field(
        default=0,
        ge=0,
        description="Number of packages created",
    )
    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Overall confidence score",
    )
    status: RecommendationStatus = Field(
        default=RecommendationStatus.COMPLETED,
        description="Status of the recommendation operation",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the result was created",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional response metadata",
    )


class RecommendationPackageDTO(BaseModel):
    """DTO for recommendation package API responses.

    Lightweight DTO representing a recommendation package for
    API consumers.
    """

    package_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique package identifier",
    )
    primary_candidate_id: str = Field(
        default="",
        description="Identifier of the primary recommendation candidate",
    )
    alternate_candidate_ids: list[str] = Field(
        default_factory=list,
        description="Identifiers of alternate candidates",
    )
    overall_confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Overall confidence score for the package (0.0-1.0)",
    )
    summary: str = Field(
        default="",
        description="Summary of the recommendation package",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the package was created",
    )
