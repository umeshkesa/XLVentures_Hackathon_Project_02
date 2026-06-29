"""ExplanationSessionManager — manages explanation sessions.

Tracks session lifecycle, stores session data, and provides
session statistics. Deterministic placeholder implementation.
"""

from __future__ import annotations

from datetime import UTC, datetime

import structlog

from adip.explainability.contracts.models import ExplanationContext, ExplanationSession
from adip.explainability.enums import ExplanationDomain, ExplanationLayer, ExplanationStatus

log = structlog.get_logger(__name__)

_VALID_TRANSITIONS: dict[ExplanationStatus, set[ExplanationStatus]] = {
    ExplanationStatus.INITIALIZED: {ExplanationStatus.COLLECTING, ExplanationStatus.FAILED},
    ExplanationStatus.COLLECTING: {ExplanationStatus.BUILDING, ExplanationStatus.FAILED},
    ExplanationStatus.BUILDING: {ExplanationStatus.VALIDATED, ExplanationStatus.FAILED},
    ExplanationStatus.VALIDATED: {ExplanationStatus.COMPLETED, ExplanationStatus.FAILED},
    ExplanationStatus.COMPLETED: set(),
    ExplanationStatus.FAILED: set(),
}


class ExplanationSessionManager:
    """Manages explanation session lifecycle.

    Deterministic placeholder that creates, tracks, and manages
    sessions for explanation operations.
    """

    def __init__(self) -> None:
        self._sessions: dict[str, ExplanationSession] = {}
        self._narrative_ids: dict[str, list[str]] = {}
        self._citation_ids: dict[str, list[str]] = {}

    def create_session(
        self,
        context: ExplanationContext,
        correlation_id: str = "",
    ) -> ExplanationSession:
        """Create a new explanation session.

        Args:
            context: The explanation context for this session.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The created ExplanationSession with INITIALIZED status.
        """
        session = ExplanationSession(
            request_id=context.context_id,
            domain=ExplanationDomain.SYSTEM,
            target_layers=[ExplanationLayer.ENGINEER],
            status=ExplanationStatus.INITIALIZED,
            started_at=datetime.now(UTC),
            completed_at=None,
            metadata={"correlation_id": correlation_id, "context_id": str(context.context_id)},
        )
        sid = str(session.session_id)
        self._sessions[sid] = session
        self._narrative_ids[sid] = []
        self._citation_ids[sid] = []
        log.info("session.created", session_id=sid, correlation_id=correlation_id)
        return session

    def get_session(self, session_id: str) -> ExplanationSession | None:
        """Get a session by ID.

        Args:
            session_id: The session identifier.

        Returns:
            ExplanationSession if found, None otherwise.
        """
        return self._sessions.get(session_id)

    def update_status(self, session_id: str, status: ExplanationStatus) -> ExplanationSession | None:
        """Update the status of a session with transition validation.

        Validates that the transition is allowed:
        INITIALIZED → COLLECTING → BUILDING → VALIDATED → COMPLETED or FAILED.

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
                "session.invalid_transition",
                session_id=session_id,
                current=session.status.value,
                requested=status.value,
                allowed=[s.value for s in allowed],
            )
            return None

        session.status = status
        if status in (ExplanationStatus.COMPLETED, ExplanationStatus.FAILED):
            session.completed_at = datetime.now(UTC)
        self._sessions[session_id] = session
        log.info("session.status_updated", session_id=session_id, status=status.value)
        return session

    def add_narrative(self, session_id: str, narrative_id: str) -> ExplanationSession | None:
        """Add a narrative ID to a session.

        Args:
            session_id: The session identifier.
            narrative_id: The narrative identifier to add.

        Returns:
            Updated session if found, None otherwise.
        """
        session = self._sessions.get(session_id)
        if session is None:
            return None
        if session_id not in self._narrative_ids:
            self._narrative_ids[session_id] = []
        self._narrative_ids[session_id].append(narrative_id)
        session.statistics["narrative_count"] = len(self._narrative_ids[session_id])
        return session

    def add_citation(self, session_id: str, citation_id: str) -> ExplanationSession | None:
        """Add a citation ID to a session.

        Args:
            session_id: The session identifier.
            citation_id: The citation identifier to add.

        Returns:
            Updated session if found, None otherwise.
        """
        session = self._sessions.get(session_id)
        if session is None:
            return None
        if session_id not in self._citation_ids:
            self._citation_ids[session_id] = []
        self._citation_ids[session_id].append(citation_id)
        session.statistics["citation_count"] = len(self._citation_ids[session_id])
        return session

    def get_active_sessions(self) -> list[ExplanationSession]:
        """Get all active (non-terminal) sessions.

        Returns:
            List of active ExplanationSession instances.
        """
        terminal = {ExplanationStatus.COMPLETED, ExplanationStatus.FAILED}
        return [s for s in self._sessions.values() if s.status not in terminal]

    def get_all_sessions(self) -> list[ExplanationSession]:
        """Get all sessions.

        Returns:
            List of all ExplanationSession instances.
        """
        return list(self._sessions.values())

    def clear(self) -> None:
        """Clear all sessions."""
        self._sessions.clear()
        self._narrative_ids.clear()
        self._citation_ids.clear()
        log.info("sessions.cleared")

    def count(self) -> int:
        """Get the number of sessions.

        Returns:
            The number of sessions.
        """
        return len(self._sessions)
