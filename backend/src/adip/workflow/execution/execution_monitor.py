"""Execution monitor — tracks task lifecycle and runtime statistics."""

from __future__ import annotations

import time
from collections import Counter

import structlog

from adip.workflow.contracts.models import (
    TaskResult,
    WorkflowGraph,
    WorkflowMetrics,
    WorkflowTask,
)
from adip.workflow.enums import TaskExecutionStatus
from adip.workflow.interfaces import ExecutionMonitor

log = structlog.get_logger(__name__)


class DefaultExecutionMonitor(ExecutionMonitor):
    """Tracks per-task lifecycle and aggregate runtime statistics.

    Maintains counters for every ``TaskExecutionStatus``, records start
    and completion timestamps, and aggregates metrics into a
    ``WorkflowMetrics`` instance that can be queried at any point during
    execution.
    """

    def __init__(self) -> None:
        self._status_counts: Counter[TaskExecutionStatus] = Counter()
        self._task_timestamps: dict[str, float] = {}
        self._start_time: float = time.monotonic()

    # ── Public API ─────────────────────────────────────────────────────

    def record_task_pending(self, task: WorkflowTask) -> None:
        """Record that a task has entered PENDING state."""
        key = str(task.task_id)
        self._task_timestamps[key] = time.monotonic()
        self._status_counts[TaskExecutionStatus.PENDING] += 1
        log.debug("monitor.task_pending", task_id=key)

    def record_task_ready(self, task: WorkflowTask) -> None:
        """Record that a task is ready for execution."""
        key = str(task.task_id)
        self._task_timestamps[f"{key}_ready"] = time.monotonic()
        self._status_counts[TaskExecutionStatus.READY] += 1
        log.debug("monitor.task_ready", task_id=key)

    def record_task_running(self, task: WorkflowTask) -> None:
        """Record that execution has started for a task."""
        key = str(task.task_id)
        self._task_timestamps[f"{key}_running"] = time.monotonic()
        self._status_counts[TaskExecutionStatus.RUNNING] += 1
        log.debug("monitor.task_running", task_id=key)

    def record_task_waiting(self, task: WorkflowTask) -> None:
        """Record that a task is waiting (e.g. for approval)."""
        key = str(task.task_id)
        self._task_timestamps[f"{key}_waiting"] = time.monotonic()
        self._status_counts[TaskExecutionStatus.WAITING] += 1
        log.debug("monitor.task_waiting", task_id=key)

    # ── Interface methods ──────────────────────────────────────────────

    async def on_task_completed(
        self,
        task: WorkflowTask,
        result: TaskResult,
        graph: WorkflowGraph,
    ) -> None:
        key = str(task.task_id)
        self._status_counts[TaskExecutionStatus.COMPLETED] += 1
        elapsed = time.monotonic() - self._task_timestamps.get(key, time.monotonic())
        log.info(
            "monitor.task_completed",
            task_id=key,
            duration_ms=round(elapsed * 1000, 2),
            success=result.success,
        )

    async def on_task_failed(
        self,
        task: WorkflowTask,
        result: TaskResult,
        graph: WorkflowGraph,
    ) -> None:
        key = str(task.task_id)
        self._status_counts[TaskExecutionStatus.FAILED] += 1
        elapsed = time.monotonic() - self._task_timestamps.get(key, time.monotonic())
        log.info(
            "monitor.task_failed",
            task_id=key,
            duration_ms=round(elapsed * 1000, 2),
            errors=result.errors,
        )

    # ── Aggregated metrics ─────────────────────────────────────────────

    def get_metrics(self) -> WorkflowMetrics:
        """Compute and return current aggregate metrics."""
        pending = self._status_counts[TaskExecutionStatus.PENDING]
        running = self._status_counts[TaskExecutionStatus.RUNNING]
        waiting = self._status_counts[TaskExecutionStatus.WAITING]
        completed = self._status_counts[TaskExecutionStatus.COMPLETED]
        failed = self._status_counts[TaskExecutionStatus.FAILED]

        total_scheduled = pending + running + waiting + completed + failed

        return WorkflowMetrics(
            scheduled_tasks=total_scheduled,
            executed_tasks=completed + failed,
            successful_tasks=completed,
            failed_tasks=failed,
            waiting_tasks=waiting,
            total_execution_time=(time.monotonic() - self._start_time) * 1000,
            total_runtime=(time.monotonic() - self._start_time) * 1000,
        )

    def get_status_summary(self) -> dict[str, int]:
        """Return a snapshot of current status counts."""
        return {
            s.value: self._status_counts.get(s, 0)
            for s in TaskExecutionStatus
        }

    def reset(self) -> None:
        """Reset all counters and timestamps."""
        self._status_counts.clear()
        self._task_timestamps.clear()
        self._start_time = time.monotonic()
