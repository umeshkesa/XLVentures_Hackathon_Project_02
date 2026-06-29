"""ExecutionMetricsCollector — collects execution metrics.

Tracks operational metrics for the execution engine including
task counts, runtime statistics, retries, failures, and
rollback operations with snapshot capabilities.
"""

from __future__ import annotations

import structlog

from adip.execution.execution.models import MetricsSnapshot

log = structlog.get_logger(__name__)


class ExecutionMetricsCollector:
    """Collects operational metrics for the execution engine."""

    def __init__(self) -> None:
        self._sessions_total: int = 0
        self._sessions_completed: int = 0
        self._tasks_total: int = 0
        self._tasks_completed: int = 0
        self._tasks_failed: int = 0
        self._retries_total: int = 0
        self._rollbacks_total: int = 0
        self._compensations_total: int = 0
        self._diagnostics_total: int = 0
        self._sla_violations: int = 0
        self._audit_count: int = 0
        self._version_count: int = 0
        self._recovery_time_total_ms: float = 0.0
        self._recovery_count: int = 0
        self._task_durations_ms: list[float] = []
        self._total_runtime_ms: float = 0.0

    def record_session(self) -> None:
        """Record a new execution session."""
        self._sessions_total += 1
        log.info("execution_metrics.session", total=self._sessions_total)

    def record_task(self, task_count: int = 1) -> None:
        """Record new tasks.

        Args:
            task_count: Number of tasks to record.
        """
        self._tasks_total += max(0, task_count)
        log.debug("execution_metrics.task", count=task_count, total=self._tasks_total)

    def record_task_completed(self, duration_ms: float = 0.0) -> None:
        """Record a completed task.

        Args:
            duration_ms: Task duration in milliseconds.
        """
        self._tasks_completed += 1
        self._task_durations_ms.append(max(0.0, duration_ms))
        log.debug("execution_metrics.task_completed", duration_ms=duration_ms)

    def record_task_failed(self) -> None:
        """Record a failed task."""
        self._tasks_failed += 1
        log.info("execution_metrics.task_failed", total=self._tasks_failed)

    def record_retry(self) -> None:
        """Record a retry attempt."""
        self._retries_total += 1
        log.info("execution_metrics.retry", total=self._retries_total)

    def record_rollback(self) -> None:
        """Record a rollback operation."""
        self._rollbacks_total += 1
        log.info("execution_metrics.rollback", total=self._rollbacks_total)

    def record_compensation(self) -> None:
        """Record a compensation operation."""
        self._compensations_total += 1
        log.info("execution_metrics.compensation", total=self._compensations_total)

    def record_session_completed(self) -> None:
        """Record a completed execution session (Phase 3.5)."""
        self._sessions_completed += 1
        log.debug("execution_metrics.session_completed", total=self._sessions_completed)

    def record_diagnostics_event(self, count: int = 1) -> None:
        """Record diagnostics events collected (Phase 3.5).

        Args:
            count: Number of diagnostics events.
        """
        self._diagnostics_total += max(0, count)
        log.debug("execution_metrics.diagnostics_event", total=self._diagnostics_total)

    def record_sla_violation(self) -> None:
        """Record an SLA violation (Phase 3.5)."""
        self._sla_violations += 1
        log.info("execution_metrics.sla_violation", total=self._sla_violations)

    def record_audit(self) -> None:
        """Record an audit operation (Phase 3.5)."""
        self._audit_count += 1
        log.debug("execution_metrics.audit", total=self._audit_count)

    def record_pipeline_version(self) -> None:
        """Record a pipeline version creation (Phase 3.5)."""
        self._version_count += 1
        log.debug("execution_metrics.pipeline_version", total=self._version_count)

    def record_recovery_time(self, duration_ms: float = 0.0) -> None:
        """Record recovery time (Phase 3.5).

        Args:
            duration_ms: Recovery duration in milliseconds.
        """
        self._recovery_time_total_ms += max(0.0, duration_ms)
        self._recovery_count += 1
        log.debug("execution_metrics.recovery_time", duration_ms=duration_ms)

    def get_average_recovery_time_ms(self) -> float:
        """Get average recovery time in milliseconds (Phase 3.5).

        Returns:
            Average recovery time, or 0.0 if no recoveries recorded.
        """
        if self._recovery_count == 0:
            return 0.0
        return round(self._recovery_time_total_ms / self._recovery_count, 2)

    def get_sessions_completed(self) -> int:
        return self._sessions_completed

    def get_diagnostics_total(self) -> int:
        return self._diagnostics_total

    def get_sla_violations(self) -> int:
        return self._sla_violations

    def get_audit_count(self) -> int:
        return self._audit_count

    def get_version_count(self) -> int:
        return self._version_count

    def record_runtime(self, duration_ms: float = 0.0) -> None:
        """Record execution runtime.

        Args:
            duration_ms: Runtime duration in milliseconds.
        """
        self._total_runtime_ms += max(0.0, duration_ms)
        log.debug("execution_metrics.runtime", duration_ms=duration_ms)

    def get_average_task_duration_ms(self) -> float:
        """Get average task duration in milliseconds.

        Returns:
            Average duration, or 0.0 if no tasks completed.
        """
        if not self._task_durations_ms:
            return 0.0
        return round(sum(self._task_durations_ms) / len(self._task_durations_ms), 2)

    def get_sessions_total(self) -> int:
        return self._sessions_total

    def get_tasks_total(self) -> int:
        return self._tasks_total

    def get_tasks_completed(self) -> int:
        return self._tasks_completed

    def get_tasks_failed(self) -> int:
        return self._tasks_failed

    def get_retries_total(self) -> int:
        return self._retries_total

    def get_rollbacks_total(self) -> int:
        return self._rollbacks_total

    def get_compensations_total(self) -> int:
        return self._compensations_total

    def snapshot(self) -> MetricsSnapshot:
        """Take a metrics snapshot.

        Returns:
            A MetricsSnapshot with current values.
        """
        snapshot = MetricsSnapshot(
            sessions_total=self._sessions_total,
            sessions_completed=self._sessions_completed,
            tasks_total=self._tasks_total,
            tasks_completed=self._tasks_completed,
            tasks_failed=self._tasks_failed,
            retries_total=self._retries_total,
            rollbacks_total=self._rollbacks_total,
            compensations_total=self._compensations_total,
            average_task_duration_ms=self.get_average_task_duration_ms(),
            total_runtime_ms=self._total_runtime_ms,
            diagnostics_total=self._diagnostics_total,
            sla_violations=self._sla_violations,
            audit_count=self._audit_count,
            version_count=self._version_count,
            recovery_time_total_ms=self._recovery_time_total_ms,
        )
        log.info(
            "execution_metrics.snapshot",
            sessions=snapshot.sessions_total,
            tasks=snapshot.tasks_total,
            completed=snapshot.tasks_completed,
            failed=snapshot.tasks_failed,
            diagnostics=snapshot.diagnostics_total,
        )
        return snapshot

    def reset(self) -> None:
        """Reset all metrics counters."""
        self._sessions_total = 0
        self._sessions_completed = 0
        self._tasks_total = 0
        self._tasks_completed = 0
        self._tasks_failed = 0
        self._retries_total = 0
        self._rollbacks_total = 0
        self._compensations_total = 0
        self._diagnostics_total = 0
        self._sla_violations = 0
        self._audit_count = 0
        self._version_count = 0
        self._recovery_time_total_ms = 0.0
        self._recovery_count = 0
        self._task_durations_ms.clear()
        self._total_runtime_ms = 0.0
        log.info("execution_metrics.reset")
