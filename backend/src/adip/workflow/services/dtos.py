"""Data Transfer Objects for workflow API layer."""

from __future__ import annotations

from adip.workflow.contracts.models import (
    WorkflowRequest,
    WorkflowResult,
)


class WorkflowRequestDTO(WorkflowRequest):
    """DTO for initiating a workflow execution via the API.

    Inherits all fields from ``WorkflowRequest``:
    ``execution_plan``, ``workflow_context``, ``metadata``.
    """


class WorkflowResponseDTO(WorkflowResult):
    """DTO for returning workflow results via the API.

    Inherits all fields from ``WorkflowResult``:
    ``workflow_id``, ``workflow_status``, ``completed_tasks``,
    ``failed_tasks``, ``skipped_tasks``, ``execution_time``,
    ``execution_summary``, ``task_results``, ``events``.
    """
