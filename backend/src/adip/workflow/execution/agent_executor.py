"""Placeholder agent executor — deterministic mock task execution.

For Phase 2 this component returns a fixed ``TaskResult`` with no
side-effects.  It must be replaced with real agent implementations
in a later phase.
"""

from __future__ import annotations

import time
import uuid

import structlog

from adip.workflow.contracts.models import TaskResult, WorkflowTask

log = structlog.get_logger(__name__)


class PlaceholderExecutor:
    """Deterministic placeholder task executor.

    Returns a mock ``TaskResult`` with ``success=True`` and a fixed
    execution time.  The output dictionary contains a single entry
    ``result`` summarising the task name.
    """

    FIXED_EXECUTION_TIME_MS: float = 10.0

    async def execute(self, task: WorkflowTask) -> TaskResult:
        correlation_id = str(uuid.uuid4())
        bound_log = log.bind(
            task_id=str(task.task_id),
            task_name=task.task_name,
            correlation_id=correlation_id,
        )

        bound_log.info("agent_executor.executing")

        # Simulate deterministic execution duration
        _ = time.monotonic()  # noqa
        duration = self.FIXED_EXECUTION_TIME_MS / 1000.0

        result = TaskResult(
            success=True,
            outputs={
                "result": f"{task.task_name} completed",
                "task_id": str(task.task_id),
                "executor": task.assigned_executor or "unknown",
            },
            execution_time=duration,
            warnings=[],
            errors=[],
            metadata={
                "executor": task.assigned_executor or "unknown",
                "strategy": "placeholder",
            },
        )

        bound_log.info(
            "agent_executor.completed",
            success=True,
            duration_ms=duration * 1000,
        )

        return result
