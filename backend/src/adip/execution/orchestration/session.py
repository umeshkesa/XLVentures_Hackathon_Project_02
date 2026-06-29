"""ExecutionSessionManager — manages execution session lifecycle.

Deterministic placeholder implementation with validated status
transitions:
  PENDING -> RUNNING, COMPLETED, FAILED, CANCELLED
  RUNNING -> COMPLETED, FAILED, CANCELLED, PAUSED, ROLLING_BACK
  PAUSED -> RUNNING, CANCELLED, FAILED
  ROLLING_BACK -> ROLLED_BACK, FAILED
  COMPLETED -> (terminal)
  FAILED -> (terminal)
  CANCELLED -> (terminal)
  ROLLED_BACK -> (terminal)
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import structlog

from adip.execution.contracts.models import (
    ExecutionMode,
    ExecutionPriority,
    ExecutionSession,
)
from adip.execution.enums import ExecutionState

log = structlog.get_logger(__name__)

VALID_TRANSITIONS: dict[str, set[str]] = {
    "PENDING": {"RUNNING", "COMPLETED", "FAILED", "CANCELLED"},
    "RUNNING": {"COMPLETED", "FAILED", "CANCELLED", "PAUSED", "ROLLING_BACK"},
    "PAUSED": {"RUNNING", "CANCELLED", "FAILED"},
    "ROLLING_BACK": {"ROLLED_BACK", "FAILED"},
    "COMPLETED": set(),
    "FAILED": set(),
    "CANCELLED": set(),
    "ROLLED_BACK": set(),
}


class ExecutionSessionManager:
    """Manages execution session lifecycle.

    Provides validated status transitions, session CRUD,
    and aggregated statistics.
    """

    def __init__(self) -> None:
        self._sessions: dict[str, ExecutionSession] = {}

    def create_session(
        self,
        request_id: str,
        package_id: str = "",
        execution_mode: str = "LIVE",
        priority: str = "MEDIUM",
    ) -> ExecutionSession:
        """Create a new execution session.

        Args:
            request_id: The related request ID.
            package_id: The execution package ID.
            execution_mode: The execution mode for this session.
            priority: The priority for this session.

        Returns:
            The created ExecutionSession with PENDING state.
        """
        session = ExecutionSession(
            session_id=uuid.uuid4(),
            request_id=uuid.UUID(request_id),
            package_id=uuid.UUID(package_id) if package_id else uuid.uuid4(),
            state=ExecutionState.PENDING,
            execution_mode=ExecutionMode(execution_mode),
            priority=ExecutionPriority(priority),
            started_at=datetime.now(UTC),
            task_count=0,
            tasks_completed=0,
            tasks_failed=0,
            tasks_skipped=0,
        )
        self._sessions[str(session.session_id)] = session
        log.info(
            "session.created",
            session_id=str(session.session_id),
            request_id=request_id,
            state=str(session.state),
        )
        return session

    def update_status(
        self,
        session_id: str,
        new_status: str,
    ) -> bool:
        """Update the status of a session with transition validation.

        Args:
            session_id: The session identifier.
            new_status: The new status to transition to.

        Returns:
            True if transition was valid and applied, False otherwise.
        """
        session = self._sessions.get(session_id)
        if session is None:
            log.warning("session.not_found", session_id=session_id)
            return False

        current = str(session.state.value)
        allowed = VALID_TRANSITIONS.get(current, set())
        if new_status not in allowed:
            log.warning(
                "session.invalid_transition",
                session_id=session_id,
                current=current,
                requested=new_status,
                allowed=sorted(allowed),
            )
            return False

        session.state = ExecutionState(new_status)
        if new_status in ("COMPLETED", "FAILED", "CANCELLED", "ROLLED_BACK"):
            session.completed_at = datetime.now(UTC)
        log.info(
            "session.status_updated",
            session_id=session_id,
            previous=current,
            new=new_status,
        )
        return True

    def update_session(
        self,
        session_id: str,
        package_id: str | None = None,
        task_count: int | None = None,
        tasks_completed: int | None = None,
        tasks_failed: int | None = None,
        tasks_skipped: int | None = None,
        error_message: str = "",
    ) -> bool:
        """Update session fields.

        Args:
            session_id: The session identifier.
            package_id: Optional new package ID.
            task_count: Optional new task count.
            tasks_completed: Optional completed tasks count.
            tasks_failed: Optional failed tasks count.
            tasks_skipped: Optional skipped tasks count.
            error_message: Optional error message.

        Returns:
            True if updated, False if session not found.
        """
        session = self._sessions.get(session_id)
        if session is None:
            return False

        if package_id is not None:
            session.package_id = uuid.UUID(package_id)
        if task_count is not None:
            session.task_count = task_count
        if tasks_completed is not None:
            session.tasks_completed = tasks_completed
        if tasks_failed is not None:
            session.tasks_failed = tasks_failed
        if tasks_skipped is not None:
            session.tasks_skipped = tasks_skipped
        if error_message:
            session.error_message = error_message
        return True

    def get_session(self, session_id: str) -> ExecutionSession | None:
        """Retrieve a session by ID.

        Args:
            session_id: The session identifier.

        Returns:
            ExecutionSession if found, None otherwise.
        """
        return self._sessions.get(session_id)

    def get_active_sessions(self) -> list[ExecutionSession]:
        """Get all active (non-terminal) sessions.

        Returns:
            List of active ExecutionSession objects.
        """
        terminal = {"COMPLETED", "FAILED", "CANCELLED", "ROLLED_BACK"}
        return [
            s for s in self._sessions.values()
            if str(s.state.value) not in terminal
        ]

    def count(self) -> int:
        """Get total number of sessions.

        Returns:
            Total session count.
        """
        return len(self._sessions)

    def count_by_state(self) -> dict[str, int]:
        """Get session counts grouped by state.

        Returns:
            Dict mapping state labels to counts.
        """
        counts: dict[str, int] = {}
        for s in self._sessions.values():
            label = str(s.state.value)
            counts[label] = counts.get(label, 0) + 1
        return counts
