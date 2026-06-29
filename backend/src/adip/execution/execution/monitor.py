"""ExecutionMonitor — monitors running executions, status, progress, and failures.

Provides real-time monitoring of active execution sessions,
task statuses, progress tracking, and failure detection.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import structlog

from adip.execution.enums import ExecutionState

log = structlog.get_logger(__name__)


class ExecutionMonitor:
    """Monitors active execution sessions and tasks."""

    def __init__(self) -> None:
        self._sessions: dict[str, dict[str, Any]] = {}

    def register_session(
        self,
        session_id: str = "",
        package_id: str = "",
        task_ids: list[str] | None = None,
        correlation_id: str = "",
    ) -> None:
        """Register a new execution session for monitoring.

        Args:
            session_id: The session ID.
            package_id: The package ID.
            task_ids: Task IDs in this session.
            correlation_id: Optional correlation ID for tracing.
        """
        self._sessions[session_id] = {
            "session_id": session_id,
            "package_id": package_id,
            "status": ExecutionState.PENDING,
            "tasks": {tid: ExecutionState.PENDING for tid in (task_ids or [])},
            "progress": 0.0,
            "failures": [],
            "started_at": datetime.now(UTC),
            "completed_at": None,
        }
        log.info(
            "monitor.session_registered",
            session_id=session_id,
            task_count=len(task_ids or []),
            correlation_id=correlation_id,
        )

    def update_task_state(
        self,
        session_id: str = "",
        task_id: str = "",
        state: ExecutionState = ExecutionState.PENDING,
        correlation_id: str = "",
    ) -> bool:
        """Update the state of a monitored task.

        Args:
            session_id: The session ID.
            task_id: The task ID.
            state: New task state.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            True if updated, False if session not found.
        """
        session = self._sessions.get(session_id)
        if not session:
            return False
        if task_id in session["tasks"]:
            session["tasks"][task_id] = state
        self._recalculate_progress(session)
        log.info(
            "monitor.task_state_updated",
            session_id=session_id,
            task_id=task_id,
            state=state.value,
            correlation_id=correlation_id,
        )
        return True

    def record_failure(
        self,
        session_id: str = "",
        task_id: str = "",
        error: str = "",
        correlation_id: str = "",
    ) -> bool:
        """Record a task failure in the monitoring data.

        Args:
            session_id: The session ID.
            task_id: The task ID.
            error: Error message.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            True if recorded, False if session not found.
        """
        session = self._sessions.get(session_id)
        if not session:
            return False
        session["failures"].append({
            "task_id": task_id,
            "error": error,
            "timestamp": datetime.now(UTC),
        })
        self.update_task_state(session_id, task_id, ExecutionState.FAILED, correlation_id)
        log.info(
            "monitor.failure_recorded",
            session_id=session_id,
            task_id=task_id,
            correlation_id=correlation_id,
        )
        return True

    def get_session_status(
        self,
        session_id: str,
        correlation_id: str = "",
    ) -> dict[str, Any] | None:
        """Get the current status of a monitored session.

        Args:
            session_id: The session ID.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            Session status dict or None if not found.
        """
        return self._sessions.get(session_id)

    def get_active_sessions(
        self,
        correlation_id: str = "",
    ) -> list[dict[str, Any]]:
        """Get all currently active (non-terminal) sessions.

        Args:
            correlation_id: Optional correlation ID for tracing.

        Returns:
            List of active session status dicts.
        """
        terminal = {ExecutionState.COMPLETED, ExecutionState.FAILED, ExecutionState.CANCELLED}
        return [
            s for s in self._sessions.values()
            if s["status"] not in terminal
        ]

    def get_all_sessions(
        self,
        correlation_id: str = "",
    ) -> list[dict[str, Any]]:
        """Get all monitored sessions.

        Args:
            correlation_id: Optional correlation ID for tracing.

        Returns:
            List of all session status dicts.
        """
        return list(self._sessions.values())

    def get_total_failures(self) -> int:
        """Get total number of recorded failures across all sessions."""
        return sum(len(s["failures"]) for s in self._sessions.values())

    def _recalculate_progress(self, session: dict[str, Any]) -> None:
        """Recalculate progress based on task states."""
        tasks = session["tasks"]
        if not tasks:
            session["progress"] = 0.0
            return
        completed = sum(
            1 for s in tasks.values()
            if s in (ExecutionState.COMPLETED, ExecutionState.FAILED, ExecutionState.CANCELLED)
        )
        session["progress"] = round(completed / len(tasks), 4)

        if all(s == ExecutionState.COMPLETED for s in tasks.values()):
            session["status"] = ExecutionState.COMPLETED
        elif any(s == ExecutionState.FAILED for s in tasks.values()):
            session["status"] = ExecutionState.FAILED
        elif any(s == ExecutionState.RUNNING for s in tasks.values()):
            session["status"] = ExecutionState.RUNNING
