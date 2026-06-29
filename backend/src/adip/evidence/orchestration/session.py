"""EvidenceSessionManager — session lifecycle management for evidence operations.

Manages the creation, completion, and querying of evidence processing
sessions. Each session tracks a single evidence operation from start
to finish, collecting timing, affected evidence, and statistics.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import structlog

from adip.evidence.contracts.models import EvidenceSession

log = structlog.get_logger(__name__)


class EvidenceSessionManager:
    """Manages evidence operation session lifecycle.

    Sessions provide correlation across pipeline stages within a
    single operation. Each session has a unique ID, tracks affected
    evidence, and records timing from start to completion.
    """

    def __init__(self) -> None:
        self._sessions: dict[str, EvidenceSession] = {}

    def create_session(
        self,
        operation: str = "",
        user_id: str = "",
        correlation_id: str = "",
    ) -> EvidenceSession:
        """Create a new evidence session.

        Returns the created session with ACTIVE status.
        """
        log.info(
            "evidence_session.create",
            operation=operation,
            user_id=user_id,
            correlation_id=correlation_id,
        )
        session_id = str(uuid.uuid4())
        session = EvidenceSession(
            session_id=uuid.UUID(session_id),
            operation=operation,
            user_id=user_id,
            correlation_id=correlation_id or session_id,
            status="ACTIVE",
        )
        self._sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> EvidenceSession | None:
        """Retrieve a session by its ID."""
        return self._sessions.get(session_id)

    def complete_session(
        self,
        session_id: str,
        status: str = "COMPLETED",
        statistics: dict[str, int | float] | None = None,
    ) -> EvidenceSession | None:
        """Mark a session as completed.

        Sets the completed_at timestamp and updates the session
        status and statistics. Returns the updated session, or None
        if the session_id is not found.
        """
        session = self._sessions.get(session_id)
        if session is None:
            log.warning("evidence_session.complete.not_found", session_id=session_id)
            return None
        log.info(
            "evidence_session.complete",
            session_id=session_id,
            status=status,
        )
        updated = session.model_copy(update={
            "completed_at": datetime.now(UTC),
            "status": status,
            "statistics": statistics or session.statistics,
        })
        self._sessions[session_id] = updated
        return updated

    def add_evidence_id(self, session_id: str, evidence_id: str) -> EvidenceSession | None:
        """Add an evidence ID to the session's evidence list.

        Updates the evidence_count. Returns the updated session or
        None if the session_id is not found.
        """
        session = self._sessions.get(session_id)
        if session is None:
            return None
        updated = session.model_copy(update={
            "evidence_count": session.evidence_count + 1,
        })
        self._sessions[session_id] = updated
        return updated

    def update_statistics(
        self,
        session_id: str,
        statistics: dict[str, int | float],
    ) -> EvidenceSession | None:
        """Update session statistics (merged with existing)."""
        session = self._sessions.get(session_id)
        if session is None:
            return None
        merged = {**session.statistics, **statistics}
        updated = session.model_copy(update={"statistics": merged})
        self._sessions[session_id] = updated
        return updated

    def get_active_sessions(self) -> list[EvidenceSession]:
        """Return all sessions with ACTIVE status."""
        return [s for s in self._sessions.values() if s.status == "ACTIVE"]

    def clear(self) -> int:
        """Clear all sessions. Returns the count of cleared sessions."""
        count = len(self._sessions)
        self._sessions.clear()
        return count
