"""Event definitions for the Action Engine.

Defines all event types emitted during execution operations
for observability, auditing, and integration hooks.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from pydantic import BaseModel, Field
from pydantic.types import UUID4

from adip.execution.enums import ExecutionMode, ExecutionPriority, ExecutionState


class ExecutionEvent(BaseModel):
    """Base event for execution operations.

    All execution events inherit from this base class,
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


class ExecutionRequested(ExecutionEvent):
    """Emitted when an execution request is submitted."""

    request_id: UUID4 = Field(
        description="The request identifier",
    )
    action_decision_id: UUID4 = Field(
        description="The action decision ID being executed",
    )
    execution_mode: ExecutionMode = Field(
        default=ExecutionMode.LIVE,
        description="Mode of execution",
    )
    priority: ExecutionPriority = Field(
        default=ExecutionPriority.MEDIUM,
        description="Priority of the execution",
    )


class ExecutionStarted(ExecutionEvent):
    """Emitted when execution actually begins."""

    session_id: UUID4 = Field(
        description="The session identifier",
    )
    package_id: UUID4 = Field(
        description="The execution package identifier",
    )
    task_count: int = Field(
        default=0,
        ge=0,
        description="Number of tasks in the package",
    )


class TaskStarted(ExecutionEvent):
    """Emitted when a task begins execution."""

    task_id: UUID4 = Field(
        description="The task identifier",
    )
    session_id: UUID4 = Field(
        description="The session this task belongs to",
    )
    task_name: str = Field(
        default="",
        description="Name of the task",
    )


class TaskCompleted(ExecutionEvent):
    """Emitted when a task completes execution."""

    task_id: UUID4 = Field(
        description="The task identifier",
    )
    session_id: UUID4 = Field(
        description="The session this task belongs to",
    )
    success: bool = Field(
        default=True,
        description="Whether the task succeeded",
    )
    duration_ms: int = Field(
        default=0,
        ge=0,
        description="Duration of task execution in milliseconds",
    )


class TaskFailed(ExecutionEvent):
    """Emitted when a task fails during execution."""

    task_id: UUID4 = Field(
        description="The task identifier",
    )
    session_id: UUID4 = Field(
        description="The session this task belongs to",
    )
    error_message: str = Field(
        default="",
        description="Error message describing the failure",
    )
    error_code: str = Field(
        default="",
        description="Error code for the failure",
    )
    retry_attempt: int = Field(
        default=0,
        ge=0,
        description="Which retry attempt this failure occurred on",
    )


class ExecutionCompleted(ExecutionEvent):
    """Emitted when execution completes (success or failure)."""

    session_id: UUID4 = Field(
        description="The session identifier",
    )
    overall_success: bool = Field(
        default=False,
        description="Whether the overall execution succeeded",
    )
    state: ExecutionState = Field(
        description="Final state of the execution",
    )
    total_duration_ms: int = Field(
        default=0,
        ge=0,
        description="Total execution duration in milliseconds",
    )
    tasks_completed: int = Field(
        default=0,
        ge=0,
        description="Number of tasks completed",
    )
    tasks_failed: int = Field(
        default=0,
        ge=0,
        description="Number of tasks failed",
    )
