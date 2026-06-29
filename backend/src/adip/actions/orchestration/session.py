"""ActionSessionManager — manages action planning session lifecycle.

Deterministic placeholder implementation following the
ReviewSessionManager pattern with validated status transitions:
  INITIALIZED -> PLANNING, COMPLETED, FAILED
  PLANNING -> VALIDATING, COMPLETED, FAILED
  VALIDATING -> OPTIMIZING, COMPLETED, FAILED
  OPTIMIZING -> READY, COMPLETED, FAILED
  READY -> COMPLETED
  COMPLETED -> (terminal)
  FAILED -> (terminal)
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

import structlog

from adip.actions.contracts.models import ActionSession
from adip.actions.enums import ActionPriority, ActionType

log = structlog.get_logger(__name__)

VALID_TRANSITIONS: dict[str, set[str]] = {
    "INITIALIZED": {"PLANNING", "COMPLETED", "FAILED"},
    "PLANNING": {"VALIDATING", "COMPLETED", "FAILED"},
    "VALIDATING": {"OPTIMIZING", "COMPLETED", "FAILED"},
    "OPTIMIZING": {"READY", "COMPLETED", "FAILED"},
    "READY": {"COMPLETED"},
    "COMPLETED": set(),
    "FAILED": set(),
}


class ActionSessionManager:
    """Manages action planning session lifecycle.

    Provides validated status transitions, session CRUD,
    and aggregated statistics.
    """

    def __init__(self) -> None:
        self._sessions: dict[str, ActionSession] = {}

    def create_session(
        self,
        request_id: str,
        plan_id: str | None = None,
        action_type: str = "AUTOMATED",
        priority: str = "MEDIUM",
    ) -> ActionSession:
        """Create a new action planning session.

        Args:
            request_id: The related request ID.
            plan_id: Optional plan ID.
            action_type: The action type for this session.
            priority: The priority for this session.

        Returns:
            The created ActionSession with INITIALIZED status.
        """
        session = ActionSession(
            session_id=uuid.uuid4(),
            request_id=uuid.UUID(request_id),
            plan_id=uuid.UUID(plan_id) if plan_id else None,
            status="INITIALIZED",
            started_at=datetime.now(UTC),
            completed_at=None,
            action_type=ActionType(action_type),
            priority=ActionPriority(priority),
            step_count=0,
            has_rollback=False,
            decision_id=None,
        )
        self._sessions[str(session.session_id)] = session
        log.info(
            "session.created",
            session_id=str(session.session_id),
            status="INITIALIZED",
        )
        return session

    def get_session(self, session_id: str) -> ActionSession | None:
        """Retrieve a session by ID.

        Args:
            session_id: The session identifier.

        Returns:
            ActionSession if found, None otherwise.
        """
        return self._sessions.get(session_id)

    def update_status(
        self,
        session_id: str,
        new_status: str,
    ) -> ActionSession | None:
        """Update session status with transition validation.

        Args:
            session_id: The session identifier.
            new_status: The target status.

        Returns:
            Updated ActionSession if valid, None otherwise.
        """
        session = self._sessions.get(session_id)
        if not session:
            log.warning("session.not_found", session_id=session_id)
            return None

        current = session.status
        allowed = VALID_TRANSITIONS.get(current, set())
        if new_status not in allowed:
            log.warning(
                "session.invalid_transition",
                session_id=session_id,
                current=current,
                target=new_status,
            )
            return None

        session.status = new_status
        if new_status in ("COMPLETED", "FAILED"):
            session.completed_at = datetime.now(UTC)

        self._sessions[session_id] = session
        log.info(
            "session.status_updated",
            session_id=session_id,
            status=new_status,
        )
        return session

    def update_session(
        self,
        session_id: str,
        plan_id: str | None = None,
        decision_id: str | None = None,
        step_count: int | None = None,
        has_rollback: bool | None = None,
        statistics: dict[str, Any] | None = None,
    ) -> ActionSession | None:
        """Update session fields.

        Args:
            session_id: The session identifier.
            plan_id: Optional new plan ID.
            decision_id: Optional new decision ID.
            step_count: Optional step count.
            has_rollback: Optional rollback flag.
            statistics: Optional statistics update.

        Returns:
            Updated ActionSession if found, None otherwise.
        """
        session = self._sessions.get(session_id)
        if not session:
            return None

        if plan_id is not None:
            session.plan_id = uuid.UUID(plan_id)
        if decision_id is not None:
            session.decision_id = uuid.UUID(decision_id)
        if step_count is not None:
            session.step_count = step_count
        if has_rollback is not None:
            session.has_rollback = has_rollback
        if statistics is not None:
            session.statistics.update(statistics)

        return session

    def get_active_sessions(self) -> list[ActionSession]:
        """Get all sessions that are not in terminal states.

        Returns:
            List of active ActionSessions.
        """
        return [
            s for s in self._sessions.values()
            if s.status not in ("COMPLETED", "FAILED")
        ]

    def get_all_sessions(self) -> list[ActionSession]:
        """Get all sessions.

        Returns:
            List of all ActionSessions.
        """
        return list(self._sessions.values())

    def clear(self) -> None:
        """Clear all sessions."""
        self._sessions.clear()

    def count(self) -> int:
        """Get total session count.

        Returns:
            Total number of sessions.
        """
        return len(self._sessions)
