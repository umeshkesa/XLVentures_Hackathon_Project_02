"""Data Transfer Objects for the Action Engine.

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

from adip.execution.enums import ExecutionMode, ExecutionPriority, ExecutionState


class ExecutionRequestDTO(BaseModel):
    """DTO for execution API requests.

    Lightweight input DTO for the execution API endpoint.
    Maps to the internal ExecutionRequest domain model.
    """

    request_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique request identifier",
    )
    action_decision_id: UUID4 = Field(
        description="The action decision ID to execute",
    )
    execution_mode: ExecutionMode = Field(
        default=ExecutionMode.LIVE,
        description="Mode of execution",
    )
    priority: ExecutionPriority = Field(
        default=ExecutionPriority.MEDIUM,
        description="Priority of the execution",
    )
    domain: str = Field(
        default="",
        description="Domain for this execution operation",
    )
    target: str = Field(
        default="",
        description="Target entity for the execution",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional request metadata",
    )


class ExecutionResponseDTO(BaseModel):
    """DTO for execution API responses.

    Lightweight output DTO for the execution API endpoint.
    Maps from the internal ExecutionSession and ExecutionResult
    domain models.
    """

    response_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique response identifier",
    )
    request_id: UUID4 = Field(
        description="The original request identifier",
    )
    session_id: UUID4 = Field(
        description="The execution session identifier",
    )
    state: ExecutionState = Field(
        default=ExecutionState.PENDING,
        description="Current state of the execution",
    )
    execution_mode: ExecutionMode = Field(
        default=ExecutionMode.LIVE,
        description="Mode of execution",
    )
    message: str = Field(
        default="",
        description="Response message",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the response was created",
    )


class ExecutionResultDTO(BaseModel):
    """DTO for execution result responses.

    Lightweight DTO representing an execution result summary
    for API consumers.
    """

    result_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique result identifier",
    )
    session_id: UUID4 = Field(
        description="The session this result belongs to",
    )
    request_id: UUID4 = Field(
        description="The original request identifier",
    )
    overall_success: bool = Field(
        default=False,
        description="Whether the overall execution succeeded",
    )
    tasks_total: int = Field(
        default=0,
        ge=0,
        description="Total number of tasks",
    )
    tasks_completed: int = Field(
        default=0,
        ge=0,
        description="Number of completed tasks",
    )
    tasks_failed: int = Field(
        default=0,
        ge=0,
        description="Number of failed tasks",
    )
    error_message: str = Field(
        default="",
        description="Overall error message if execution failed",
    )
    total_duration_ms: int = Field(
        default=0,
        ge=0,
        description="Total execution duration in milliseconds",
    )
