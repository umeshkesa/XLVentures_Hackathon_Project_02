"""Event definitions for the Action Manager.

Defines all event types emitted during action planning
operations for observability, auditing, and integration hooks.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from pydantic import BaseModel, Field
from pydantic.types import UUID4

from adip.actions.enums import ActionType, ExecutionReadiness


class ActionEvent(BaseModel):
    """Base event for action operations.

    All action events inherit from this base class,
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


class ActionRequested(ActionEvent):
    """Emitted when an action planning request is submitted."""

    request_id: UUID4 = Field(
        description="The request identifier",
    )
    review_decision_id: UUID4 = Field(
        description="The review decision ID being acted upon",
    )
    action_type: ActionType = Field(
        default=ActionType.AUTOMATED,
        description="Type of action being planned",
    )


class ActionPlanned(ActionEvent):
    """Emitted when an action plan has been generated."""

    plan_id: UUID4 = Field(
        description="The plan identifier",
    )
    request_id: UUID4 = Field(
        description="The request identifier",
    )
    step_count: int = Field(
        default=0,
        ge=0,
        description="Number of steps in the plan",
    )
    has_rollback: bool = Field(
        default=False,
        description="Whether the plan includes rollback",
    )


class ActionValidated(ActionEvent):
    """Emitted when an action plan has been validated."""

    plan_id: UUID4 = Field(
        description="The plan identifier",
    )
    is_valid: bool = Field(
        default=False,
        description="Whether the plan is valid",
    )
    issues: list[str] = Field(
        default_factory=list,
        description="Validation issues found",
    )


class ActionReady(ActionEvent):
    """Emitted when an action plan is ready for execution."""

    plan_id: UUID4 = Field(
        description="The plan identifier",
    )
    readiness: ExecutionReadiness = Field(
        description="The execution readiness status",
    )
    reason: str = Field(
        default="",
        description="Reason for the readiness assessment",
    )
