"""ParallelTaskExecutor — executes tasks in parallel groups.

Executes placeholder tasks in parallel groups based on the
execution graph structure. Tasks in the same level run
concurrently; tasks in later levels wait for earlier ones.
"""

from __future__ import annotations

import structlog

from adip.execution.enums import ExecutionState

log = structlog.get_logger(__name__)


class ParallelTaskExecutor:
    """Executes placeholder tasks in parallel groups."""

    def __init__(self) -> None:
        self._completed_tasks: dict[str, dict] = {}

    def execute_parallel_group(
        self,
        task_ids: list[str],
        session_id: str = "",
        correlation_id: str = "",
    ) -> dict[str, dict]:
        """Execute a group of tasks in parallel (placeholder).

        Simulates parallel execution by processing each task
        deterministically and collecting results.

        Args:
            task_ids: List of task IDs to execute in parallel.
            session_id: Session ID for this execution.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            Dict mapping task_id to result dict with success, output, duration_ms.
        """
        results: dict[str, dict] = {}
        for tid in task_ids:
            result = self._simulate_task(tid, session_id)
            results[tid] = result
            self._completed_tasks[tid] = result

        log.info(
            "parallel_executor.group_executed",
            session_id=session_id,
            task_count=len(task_ids),
            success_count=sum(1 for r in results.values() if r.get("success")),
            correlation_id=correlation_id,
        )
        return results

    def execute_sequentially(
        self,
        task_ids: list[str],
        session_id: str = "",
        correlation_id: str = "",
    ) -> dict[str, dict]:
        """Execute tasks sequentially (placeholder).

        Args:
            task_ids: Ordered list of task IDs to execute.
            session_id: Session ID for this execution.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            Dict mapping task_id to result dict.
        """
        results: dict[str, dict] = {}
        for tid in task_ids:
            result = self._simulate_task(tid, session_id)
            results[tid] = result
            self._completed_tasks[tid] = result
        log.info(
            "parallel_executor.sequential",
            session_id=session_id,
            task_count=len(task_ids),
            correlation_id=correlation_id,
        )
        return results

    def simulate_task_failure(
        self,
        task_id: str,
        session_id: str = "",
        correlation_id: str = "",
    ) -> dict:
        """Simulate a task failure for testing.

        Args:
            task_id: The task ID to simulate failure for.
            session_id: Session ID.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            Result dict with success=False and error details.
        """
        result = {
            "task_id": task_id,
            "success": False,
            "output": "",
            "error": "Simulated task failure",
            "duration_ms": 10,
            "state": ExecutionState.FAILED,
        }
        self._completed_tasks[task_id] = result
        log.info(
            "parallel_executor.simulated_failure",
            task_id=task_id,
            correlation_id=correlation_id,
        )
        return result

    def get_completed_tasks(self) -> dict[str, dict]:
        """Get all completed task results."""
        return dict(self._completed_tasks)

    def reset(self) -> None:
        """Clear all completed task data."""
        self._completed_tasks.clear()

    def _simulate_task(self, task_id: str, session_id: str) -> dict:
        """Simulate a single task execution (deterministic placeholder)."""
        duration_ms = 10 + (hash(task_id) % 50)
        return {
            "task_id": task_id,
            "success": True,
            "output": f"Task {task_id} executed successfully",
            "error": "",
            "duration_ms": duration_ms,
            "state": ExecutionState.COMPLETED,
        }
