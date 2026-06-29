"""Deterministic ExecutionDispatcher implementation."""

from __future__ import annotations

from adip.planner.contracts.models import PlanningContext, PlanningTask
from adip.planner.enums import TaskStatusEnum
from adip.planner.interfaces.pipeline import ExecutionDispatcher


class DeterministicExecutionDispatcher(ExecutionDispatcher):
    """Placeholder execution dispatcher.

    Transitions a task from PENDING to IN_PROGRESS.  In a real system
    this would submit the task to a worker queue or external executor.
    """

    async def dispatch(
        self, task: PlanningTask, context: PlanningContext
    ) -> PlanningTask:
        """Dispatch a single task for execution."""
        new_status = TaskStatusEnum.IN_PROGRESS
        if task.status not in (TaskStatusEnum.PENDING, TaskStatusEnum.READY):
            return task

        return task.model_copy(update={"status": new_status})
