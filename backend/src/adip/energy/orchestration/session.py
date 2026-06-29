"""EnergySessionManager — manages energy domain session lifecycle.

Deterministic placeholder implementation.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import structlog

from adip.energy.orchestration.models import EnergySession

log = structlog.get_logger(__name__)


_VALID_TRANSITIONS: dict[str, set[str]] = {
    "INITIALIZED": {"ACTIVE", "COMPLETED", "FAILED"},
    "ACTIVE": {"COMPLETED", "FAILED"},
    "COMPLETED": set(),
    "FAILED": set(),
}


class EnergySessionManager:
    """Manages energy domain session lifecycle.

    Deterministric placeholder that creates, tracks, and manages
    sessions for energy domain operations.
    """

    def __init__(self) -> None:
        self._sessions: dict[str, EnergySession] = {}

    def create_session(
        self,
        asset_id: str,
        domain: str = "ELECTRICITY",
        operation: str = "",
        correlation_id: str = "",
    ) -> EnergySession:
        """Create a new energy domain session.

        Args:
            asset_id: The asset identifier.
            domain: The energy domain.
            operation: The operation being performed.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The created EnergySession with INITIALIZED status.
        """
        session = EnergySession(
            asset_id=uuid.UUID(asset_id) if isinstance(asset_id, str) else asset_id,
            domain=domain,
            status="INITIALIZED",
            operation=operation,
            started_at=datetime.now(UTC),
            metadata={"correlation_id": correlation_id},
        )
        sid = str(session.session_id)
        self._sessions[sid] = session
        log.info("energy.session.created", session_id=sid, asset_id=asset_id, correlation_id=correlation_id)
        return session

    def get_session(self, session_id: str) -> EnergySession | None:
        """Get a session by ID.

        Args:
            session_id: The session identifier.

        Returns:
            EnergySession if found, None otherwise.
        """
        return self._sessions.get(session_id)

    def update_status(self, session_id: str, status: str) -> EnergySession | None:
        """Update the status of a session with transition validation.

        Validates transitions:
        INITIALIZED -> ACTIVE -> COMPLETED/FAILED

        Args:
            session_id: The session identifier.
            status: The new status.

        Returns:
            Updated session if found and transition valid, None otherwise.
        """
        session = self._sessions.get(session_id)
        if session is None:
            return None

        allowed = _VALID_TRANSITIONS.get(session.status, set())
        if status not in allowed:
            log.warning(
                "energy.session.invalid_transition",
                session_id=session_id,
                current=session.status,
                requested=status,
                allowed=list(allowed),
            )
            return None

        session.status = status
        if status in ("COMPLETED", "FAILED"):
            session.completed_at = datetime.now(UTC)
        self._sessions[session_id] = session
        log.info("energy.session.status_updated", session_id=session_id, status=status)
        return session

    def get_active_sessions(self) -> list[EnergySession]:
        """Get all active (non-terminal) sessions.

        Returns:
            List of active EnergySession instances.
        """
        terminal = {"COMPLETED", "FAILED"}
        return [s for s in self._sessions.values() if s.status not in terminal]

    def get_all_sessions(self) -> list[EnergySession]:
        """Get all sessions.

        Returns:
            List of all EnergySession instances.
        """
        return list(self._sessions.values())

    def count(self) -> int:
        """Get the number of sessions.

        Returns:
            The number of sessions.
        """
        return len(self._sessions)

    def clear(self) -> None:
        """Clear all sessions."""
        self._sessions.clear()
        log.info("energy.sessions.cleared")
