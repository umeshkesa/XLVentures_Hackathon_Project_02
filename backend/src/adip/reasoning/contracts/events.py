"""Event definitions for the Reasoning Engine.

Defines all event types emitted during reasoning operations
for observability, auditing, and integration hooks.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field


class ReasoningEvent(BaseModel):
    """Base event for reasoning operations.

    All reasoning events inherit from this base class,
    providing common fields for event correlation.
    """

    event_type: str = Field(
        default="",
        description="The type of reasoning event",
    )
    reasoning_id: str = Field(
        default="",
        description="The reasoning operation identifier",
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


class ReasoningStarted(ReasoningEvent):
    """Emitted when a reasoning operation starts."""

    event_type: str = "reasoning.started"
    domain: str = Field(
        default="",
        description="The domain for the reasoning operation",
    )
    strategy: str = Field(
        default="",
        description="The strategy used for reasoning",
    )


class HypothesisGenerated(ReasoningEvent):
    """Emitted when a hypothesis is generated."""

    event_type: str = "reasoning.hypothesis_generated"
    hypothesis_id: str = Field(
        default="",
        description="The generated hypothesis identifier",
    )
    hypothesis_count: int = Field(
        default=0,
        ge=0,
        description="Total hypotheses generated so far",
    )


class InferenceCompleted(ReasoningEvent):
    """Emitted when an inference is completed."""

    event_type: str = "reasoning.inference_completed"
    inference_id: str = Field(
        default="",
        description="The completed inference identifier",
    )
    inference_type: str = Field(
        default="",
        description="The type of inference completed",
    )


class ContradictionDetected(ReasoningEvent):
    """Emitted when a contradiction is detected."""

    event_type: str = "reasoning.contradiction_detected"
    contradiction_id: str = Field(
        default="",
        description="The detected contradiction identifier",
    )
    severity: str = Field(
        default="",
        description="Severity of the detected contradiction",
    )


class ReasoningCompleted(ReasoningEvent):
    """Emitted when a reasoning operation completes."""

    event_type: str = "reasoning.completed"
    status: str = Field(
        default="",
        description="Final status of the reasoning operation",
    )
    result_id: str = Field(
        default="",
        description="The reasoning result identifier",
    )
    duration_ms: float = Field(
        default=0.0,
        ge=0.0,
        description="Total duration of the reasoning operation in milliseconds",
    )
