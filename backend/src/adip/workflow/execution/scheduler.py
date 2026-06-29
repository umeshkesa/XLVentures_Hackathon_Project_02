"""Task scheduler — determines which tasks are eligible for execution.

The scheduler uses an ``ExecutionStrategy`` to produce a schedule and
returns the next wave of executable tasks from the workflow graph.
"""

from __future__ import annotations

import time
import uuid

import structlog

from adip.workflow.contracts.models import (
    TaskExecutionStatus,
    WorkflowGraph,
    WorkflowTask,
)
from adip.workflow.execution.strategy import ExecutionStrategy
from adip.workflow.interfaces import TaskScheduler

log = structlog.get_logger(__name__)


class DefaultScheduler(TaskScheduler):
    """Deterministic scheduler that delegates to an ``ExecutionStrategy``.

    The scheduler:
      1. Delegates schedule creation to the injected strategy.
      2. Maps the next incomplete wave to actual ``WorkflowTask``
         instances from the graph.
      3. Filters out already-completed or running tasks.
      4. Returns the set of tasks eligible for immediate execution.
    """

    def __init__(self, strategy: ExecutionStrategy | None = None) -> None:
        from adip.workflow.execution.strategy import SequentialStrategy

        self._strategy = strategy or SequentialStrategy()

    async def schedule(self, graph: WorkflowGraph) -> list[WorkflowTask]:
        start = time.monotonic()
        correlation_id = str(uuid.uuid4())
        bound_log = log.bind(correlation_id=correlation_id)

        bound_log.info(
            "scheduler.schedule",
            node_count=len(graph.nodes),
        )

        schedule = await self._strategy.create_schedule(graph)

        # Find the first incomplete wave
        executable: list[WorkflowTask] = []
        for wave in schedule:
            tasks_in_wave = [
                graph.nodes[tid]
                for tid in wave
                if tid in graph.nodes
            ]
            # Skip waves where all tasks are already done or running
            if all(
                t.runtime_status
                in (TaskExecutionStatus.COMPLETED, TaskExecutionStatus.RUNNING)
                for t in tasks_in_wave
            ):
                continue

            for tid in wave:
                task = graph.nodes.get(tid)
                if task is None:
                    continue
                if task.runtime_status == TaskExecutionStatus.PENDING:
                    deps_met = all(
                        graph.nodes[d].runtime_status
                        == TaskExecutionStatus.COMPLETED
                        for d in task.dependencies
                        if d in graph.nodes
                    )
                    if deps_met:
                        executable.append(task)

            if executable:
                break

        elapsed = (time.monotonic() - start) * 1000
        bound_log.info(
            "scheduler.completed",
            executable_count=len(executable),
            duration_ms=round(elapsed, 2),
        )

        return executable
