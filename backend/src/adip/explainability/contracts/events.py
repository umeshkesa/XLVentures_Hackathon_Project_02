"""Event definitions for the Explainability Engine.

Defines all event types emitted during explanation operations
for observability, auditing, and integration hooks.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field


class ExplanationEvent(BaseModel):
    """Base event for explanation operations.

    All explanation events inherit from this base class,
    providing common fields for event correlation.
    """

    event_type: str = Field(
        default="",
        description="The type of explanation event",
    )
    explanation_id: str = Field(
        default="",
        description="The explanation operation identifier",
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


class ExplanationRequested(ExplanationEvent):
    """Emitted when an explanation operation starts."""

    event_type: str = "explanation.requested"
    domain: str = Field(
        default="",
        description="The domain for the explanation operation",
    )
    target_audiences: list[str] = Field(
        default_factory=list,
        description="Target audience layers for the explanation",
    )


class ExplanationGenerated(ExplanationEvent):
    """Emitted when explanation narratives are generated."""

    event_type: str = "explanation.generated"
    result_id: str = Field(
        default="",
        description="The explanation result identifier",
    )
    narratives_count: int = Field(
        default=0,
        ge=0,
        description="Total number of narratives generated",
    )


class ExplanationValidated(ExplanationEvent):
    """Emitted when an explanation is validated."""

    event_type: str = "explanation.validated"
    result_id: str = Field(
        default="",
        description="The explanation result identifier",
    )
    passed: bool = Field(
        default=False,
        description="Whether validation passed",
    )
    violations: list[str] = Field(
        default_factory=list,
        description="List of validation violations",
    )


class ExplanationCompleted(ExplanationEvent):
    """Emitted when an explanation operation completes."""

    event_type: str = "explanation.completed"
    result_id: str = Field(
        default="",
        description="The explanation result identifier",
    )
    status: str = Field(
        default="",
        description="Final status of the explanation operation",
    )
    duration_ms: float = Field(
        default=0.0,
        ge=0.0,
        description="Total duration of the explanation operation in milliseconds",
    )
