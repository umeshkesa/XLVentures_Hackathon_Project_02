"""ExecutionProgressTracker — tracks execution progress for sessions and tasks.

Tracks overall execution progress, per-task progress,
completed tasks, failed tasks, and estimates remaining
time for active executions.
"""

from __future__ import annotations

import structlog

from adip.execution.enums import ExecutionState
from adip.execution.execution.models import ProgressReport

log = structlog.get_logger(__name__)


class ExecutionProgressTracker:
    """Tracks execution progress for sessions and tasks."""

    def __init__(self) -> None:
        self._reports: dict[str, ProgressReport] = {}

    def get_progress(
        self,
        session_id: str = "",
        total_tasks: int = 0,
        completed_tasks: int = 0,
        failed_tasks: int = 0,
        in_progress_tasks: int = 0,
        pending_tasks: int = 0,
        state: ExecutionState = ExecutionState.RUNNING,
        elapsed_seconds: float = 0.0,
        estimated_remaining_seconds: float = 0.0,
        correlation_id: str = "",
    ) -> ProgressReport:
        """Generate a progress report for a session.

        Args:
            session_id: The session ID.
            total_tasks: Total number of tasks.
            completed_tasks: Number of completed tasks.
            failed_tasks: Number of failed tasks.
            in_progress_tasks: Number of in-progress tasks.
            pending_tasks: Number of pending tasks.
            state: Current execution state.
            elapsed_seconds: Elapsed time in seconds.
            estimated_remaining_seconds: Estimated remaining time.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            A ProgressReport with current progress.
        """
        total = total_tasks or 1
        # Only count non-failed tasks for progress
        effective_total = total_tasks
        overall_progress = (
            round((completed_tasks + failed_tasks) / effective_total, 4)
            if effective_total > 0
            else 0.0
        )

        report = ProgressReport(
            session_id=session_id,
            total_tasks=total_tasks,
            completed_tasks=completed_tasks,
            failed_tasks=failed_tasks,
            in_progress_tasks=in_progress_tasks,
            pending_tasks=pending_tasks,
            overall_progress=min(overall_progress, 1.0),
            state=state,
            elapsed_seconds=elapsed_seconds,
            estimated_remaining_seconds=estimated_remaining_seconds,
        )
        self._reports[session_id] = report
        log.info(
            "progress_tracker.report",
            session_id=session_id,
            progress=report.overall_progress,
            completed=completed_tasks,
            failed=failed_tasks,
            correlation_id=correlation_id,
        )
        return report

    def update_task_completed(
        self,
        session_id: str = "",
        correlation_id: str = "",
    ) -> ProgressReport | None:
        """Update progress when a task completes.

        Args:
            session_id: The session ID.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            Updated ProgressReport if session tracked, None otherwise.
        """
        report = self._reports.get(session_id)
        if not report:
            return None
        return self.get_progress(
            session_id=session_id,
            total_tasks=report.total_tasks,
            completed_tasks=report.completed_tasks + 1,
            failed_tasks=report.failed_tasks,
            in_progress_tasks=max(0, report.in_progress_tasks - 1),
            pending_tasks=max(0, report.pending_tasks - 1) if report.pending_tasks > 0 else 0,
            state=report.state,
            elapsed_seconds=report.elapsed_seconds + 1.0,
            correlation_id=correlation_id,
        )

    def update_task_failed(
        self,
        session_id: str = "",
        correlation_id: str = "",
    ) -> ProgressReport | None:
        """Update progress when a task fails.

        Args:
            session_id: The session ID.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            Updated ProgressReport if session tracked, None otherwise.
        """
        report = self._reports.get(session_id)
        if not report:
            return None
        return self.get_progress(
            session_id=session_id,
            total_tasks=report.total_tasks,
            completed_tasks=report.completed_tasks,
            failed_tasks=report.failed_tasks + 1,
            in_progress_tasks=max(0, report.in_progress_tasks - 1),
            pending_tasks=max(0, report.pending_tasks - 1) if report.pending_tasks > 0 else 0,
            state=ExecutionState.FAILED if report.failed_tasks + 1 >= report.total_tasks else report.state,
            elapsed_seconds=report.elapsed_seconds + 1.0,
            correlation_id=correlation_id,
        )

    def get_report(self, session_id: str) -> ProgressReport | None:
        """Get the latest progress report for a session.

        Args:
            session_id: The session ID.

        Returns:
            ProgressReport if found, None otherwise.
        """
        return self._reports.get(session_id)

    def get_all_reports(self) -> dict[str, ProgressReport]:
        """Get all progress reports."""
        return dict(self._reports)

    def clear(self) -> None:
        """Clear all progress reports."""
        self._reports.clear()
