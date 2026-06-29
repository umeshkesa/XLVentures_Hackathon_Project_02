"""Data Transfer Objects for the Action Manager.

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

from adip.actions.enums import ActionPriority, ActionType, ExecutionReadiness


class ActionRequestDTO(BaseModel):
    """DTO for action planning API requests.

    Lightweight input DTO for the action planning API
    endpoint. Maps to the internal ActionRequest domain model.
    """

    request_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique request identifier",
    )
    review_decision_id: UUID4 = Field(
        description="The approved review decision ID",
    )
    action_type: ActionType = Field(
        default=ActionType.AUTOMATED,
        description="Type of action to plan",
    )
    priority: ActionPriority = Field(
        default=ActionPriority.MEDIUM,
        description="Priority of the action",
    )
    domain: str = Field(
        default="",
        description="Domain for this action operation",
    )
    target: str = Field(
        default="",
        description="Target entity for the action",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional request metadata",
    )


class ActionPlanDTO(BaseModel):
    """DTO for action plan API responses.

    Lightweight DTO representing an action plan summary
    for API consumers.
    """

    plan_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique plan identifier",
    )
    request_id: UUID4 = Field(
        description="The request this plan belongs to",
    )
    name: str = Field(
        default="",
        description="Name of the action plan",
    )
    step_count: int = Field(
        default=0,
        ge=0,
        description="Number of steps in the plan",
    )
    has_rollback: bool = Field(
        default=False,
        description="Whether the plan has rollback configured",
    )
    status: str = Field(
        default="DRAFT",
        description="Status of the action plan",
    )
    readiness: ExecutionReadiness = Field(
        default=ExecutionReadiness.WAITING,
        description="Execution readiness status",
    )


class ActionResponseDTO(BaseModel):
    """DTO for action planning API responses.

    Lightweight output DTO for the action planning API endpoint.
    Maps from the internal ActionDecision and ActionSession
    domain models.
    """

    response_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique response identifier",
    )
    request_id: UUID4 = Field(
        description="The original request identifier",
    )
    decision: ActionPlanDTO | None = Field(
        default=None,
        description="The action plan decision summary",
    )
    session_id: UUID4 = Field(
        description="The session identifier",
    )
    status: str = Field(
        default="INITIALIZED",
        description="Status of the action planning operation",
    )
    message: str = Field(
        default="",
        description="Response message",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the response was created",
    )
