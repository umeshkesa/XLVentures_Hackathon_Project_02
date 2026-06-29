"""Workflow Engine events — recorded during workflow execution."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import UUID4, BaseModel, Field

EVENT_VERSION: str = "1.0.0"


class WorkflowEvent(BaseModel):
    """Base event with standard enterprise fields."""
    event_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique event identifier",
    )
    workflow_id: UUID4 = Field(
        description="Workflow instance this event belongs to",
    )
    execution_plan_id: str = Field(
        default="",
        description="The plan ID that produced this workflow",
    )
    planner_plan_id: str = Field(
        default="",
        description="The Planner's plan ID (may differ from execution plan ID)",
    )
    event_version: str = Field(
        default=EVENT_VERSION,
        description="Schema version of this event",
    )
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="When the event occurred",
    )
    correlation_id: str = Field(
        default="",
        description="Correlation ID for tracing across services",
    )
    payload: dict[str, Any] = Field(
        default_factory=dict,
        description="Event-specific data",
    )


class WorkflowStarted(WorkflowEvent):
    """Emitted when a workflow is created and ready for initialisation."""


class WorkflowInitialized(WorkflowEvent):
    """Emitted after the workflow graph is built and validated."""


class GraphBuilt(WorkflowEvent):
    """Emitted after the execution graph is constructed."""
    node_count: int = 0
    edge_count: int = 0
    cycle_free: bool = True


class TasksScheduled(WorkflowEvent):
    """Emitted when tasks are scheduled into execution waves."""
    wave_count: int = 0
    total_tasks: int = 0


class ExecutionStarted(WorkflowEvent):
    """Emitted when the workflow begins task execution."""
    total_tasks: int = 0


class TaskScheduled(WorkflowEvent):
    """Emitted when a task is queued for execution."""
    task_id: UUID4


class TaskDispatched(WorkflowEvent):
    """Emitted when a task is dispatched to an executor."""
    task_id: UUID4
    executor: str = ""


class TaskStarted(WorkflowEvent):
    """Emitted when a task begins execution."""
    task_id: UUID4


class TaskCompleted(WorkflowEvent):
    """Emitted when a task finishes successfully."""
    task_id: UUID4
    execution_time: float | None = None


class TaskFailed(WorkflowEvent):
    """Emitted when a task fails."""
    task_id: UUID4
    error: str = ""


class RetryStarted(WorkflowEvent):
    """Emitted when a retry attempt begins."""
    task_id: UUID4
    attempt: int = 1


class RetryCompleted(WorkflowEvent):
    """Emitted after a retry attempt finishes."""
    task_id: UUID4
    attempt: int = 1
    success: bool = False


class WorkflowPaused(WorkflowEvent):
    """Emitted when a workflow is paused (e.g. awaiting approval)."""
    reason: str = ""


class WorkflowResumed(WorkflowEvent):
    """Emitted when a paused workflow resumes execution."""


class ApprovalRequested(WorkflowEvent):
    """Emitted when human approval is needed."""
    task_id: UUID4 | None = None
    approval_type: str = ""


class ApprovalGranted(WorkflowEvent):
    """Emitted when an approval request is granted."""
    task_id: UUID4 | None = None
    approval_type: str = ""
    approved_by: str = ""


class ApprovalRejected(WorkflowEvent):
    """Emitted when an approval request is rejected."""
    task_id: UUID4 | None = None
    approval_type: str = ""
    rejected_by: str = ""
    reason: str = ""


class WorkflowCompleted(WorkflowEvent):
    """Emitted when the entire workflow finishes successfully."""
    summary: str = ""


class WorkflowFailed(WorkflowEvent):
    """Emitted when the entire workflow fails."""
    error: str = ""
