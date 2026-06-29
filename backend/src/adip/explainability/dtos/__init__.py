"""Data Transfer Objects for the Explainability Engine.

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


class ExplanationRequestDTO(BaseModel):
    """DTO for explanation API requests.

    Lightweight input DTO for the explanation API endpoint.
    Maps to the internal ExplanationRequest domain model.
    """

    reasoning_result_id: str = Field(
        description="The reasoning result ID to explain",
    )
    evidence_result_id: str = Field(
        default="",
        description="The evidence result ID to explain",
    )
    recommendation_result_id: str = Field(
        default="",
        description="The recommendation result ID to explain",
    )
    target_audiences: list[str] = Field(
        default_factory=list,
        description="Target audience layers for this explanation",
    )
    domain: str = Field(
        default="GENERAL",
        description="The domain for this explanation operation",
    )
    context: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context for the explanation operation",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional request metadata",
    )


class ExplanationResponseDTO(BaseModel):
    """DTO for explanation API responses.

    Lightweight output DTO for the explanation API endpoint.
    Maps from the internal ExplanationResult domain model.
    """

    result_id: UUID4 = Field(
        description="The explanation result identifier",
    )
    request_id: UUID4 = Field(
        description="The original request identifier",
    )
    package_id: str = Field(
        default="",
        description="The explanation package identifier",
    )
    narratives_count: int = Field(
        default=0,
        ge=0,
        description="Number of narratives generated",
    )
    citations_count: int = Field(
        default=0,
        ge=0,
        description="Number of citations generated",
    )
    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Overall confidence score",
    )
    status: str = Field(
        default="",
        description="Status of the explanation operation",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the result was created",
    )


class ExplanationPackageDTO(BaseModel):
    """DTO for explanation package API responses.

    Lightweight DTO representing an explanation package for
    API consumers.
    """

    package_id: str = Field(
        default="",
        description="Unique package identifier",
    )
    result_id: str = Field(
        default="",
        description="The result this package belongs to",
    )
    primary_narrative: dict[str, Any] = Field(
        default_factory=dict,
        description="The primary explanation narrative",
    )
    supporting_narratives: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Supporting narratives for this package",
    )
    evidence_citations: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Evidence citations supporting the explanation",
    )
    reasoning_summary: str = Field(
        default="",
        description="Summary of the reasoning behind this explanation",
    )
    recommendation_summary: str = Field(
        default="",
        description="Summary of the recommendations from this explanation",
    )
    overall_confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Overall confidence score for this package (0.0-1.0)",
    )
    created_at: str = Field(
        default="",
        description="When the package was created",
    )
