"""Data Transfer Objects for the Reasoning Engine.

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

from adip.reasoning.enums import ReasoningDomain, ReasoningStatus, ReasoningStrategyType


class ReasoningRequestDTO(BaseModel):
    """DTO for reasoning API requests.

    Lightweight input DTO for the reasoning API endpoint.
    Maps to the internal ReasoningRequest domain model.
    """

    evidence_package_id: UUID4 = Field(
        description="The evidence package ID to reason about",
    )
    domain: ReasoningDomain = Field(
        default=ReasoningDomain.SYSTEM,
        description="The domain for this reasoning operation",
    )
    strategy: ReasoningStrategyType = Field(
        default=ReasoningStrategyType.HYBRID,
        description="The reasoning strategy to apply",
    )
    context: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context for the reasoning operation",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional request metadata",
    )


class ReasoningResponseDTO(BaseModel):
    """DTO for reasoning API responses.

    Lightweight output DTO for the reasoning API endpoint.
    Maps from the internal ReasoningResult domain model.
    """

    result_id: UUID4 = Field(
        description="The reasoning result identifier",
    )
    request_id: UUID4 = Field(
        description="The original request identifier",
    )
    decision: dict[str, Any] = Field(
        default_factory=dict,
        description="The reasoning decision summary",
    )
    hypotheses_count: int = Field(
        default=0,
        ge=0,
        description="Number of hypotheses generated",
    )
    inferences_count: int = Field(
        default=0,
        ge=0,
        description="Number of inferences made",
    )
    contradictions_count: int = Field(
        default=0,
        ge=0,
        description="Number of contradictions detected",
    )
    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Overall confidence score",
    )
    status: ReasoningStatus = Field(
        default=ReasoningStatus.COMPLETED,
        description="Status of the reasoning operation",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the result was created",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional response metadata",
    )


class ReasoningDecisionDTO(BaseModel):
    """DTO for reasoning decision API responses.

    Lightweight DTO representing a reasoning decision for
    API consumers.
    """

    decision_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique decision identifier",
    )
    conclusion: str = Field(
        default="",
        description="The final conclusion reached",
    )
    reasoning_summary: str = Field(
        default="",
        description="Summary of the reasoning that led to this decision",
    )
    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Confidence score for this decision (0.0–1.0)",
    )
    selected_hypotheses: list[str] = Field(
        default_factory=list,
        description="Descriptions of selected hypotheses",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the decision was made",
    )
