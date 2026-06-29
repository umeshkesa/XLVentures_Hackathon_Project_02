"""RegistrySessionManager — session lifecycle management for registry operations.

Manages the creation, completion, and querying of registry operation
sessions. Each session tracks a single registry operation from start
to finish, collecting timing, affected entries, and statistics.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import structlog

from adip.registry.contracts.models import RegistrySession
from adip.registry.enums import RegistryType

log = structlog.get_logger(__name__)


class RegistrySessionManager:
    """Manages registry operation session lifecycle.

    Sessions provide correlation across pipeline stages within a
    single operation. Each session has a unique ID, tracks affected
    entries, and records timing from start to completion.
    """

    def __init__(self) -> None:
        self._sessions: dict[str, RegistrySession] = {}

    def create_session(
        self,
        registry_type: RegistryType = RegistryType.CAPABILITY,
        operation: str = "",
        user_id: str = "",
        namespace: str = "default",
        correlation_id: str = "",
        search_strategy: str = "",
        version_used: str = "",
    ) -> RegistrySession:
        """Create a new registry session.

        Returns the created session with ACTIVE status.
        """
        log.info(
            "registry_session.create",
            operation=operation,
            user_id=user_id,
            correlation_id=correlation_id,
        )
        session_id = str(uuid.uuid4())
        session = RegistrySession(
            session_id=uuid.UUID(session_id),
            registry_type=registry_type,
            operation=operation,
            user_id=user_id,
            namespace=namespace,
            correlation_id=correlation_id or session_id,
            search_strategy=search_strategy,
            version_used=version_used,
            status="ACTIVE",
        )
        self._sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> RegistrySession | None:
        """Retrieve a session by its ID."""
        return self._sessions.get(session_id)

    def complete_session(
        self,
        session_id: str,
        status: str = "COMPLETED",
        statistics: dict[str, int | float] | None = None,
    ) -> RegistrySession | None:
        """Mark a session as completed.

        Sets the completed_at timestamp and updates the session
        status and statistics. Returns the updated session, or None
        if the session_id is not found.
        """
        session = self._sessions.get(session_id)
        if session is None:
            log.warning("registry_session.complete.not_found", session_id=session_id)
            return None
        log.info(
            "registry_session.complete",
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

    def add_affected_entry(self, session_id: str, entry_id: str) -> RegistrySession | None:
        """Add an entry ID to the session's affected entries list.

        Entries are deduplicated. Returns the updated session or
        None if the session_id is not found.
        """
        session = self._sessions.get(session_id)
        if session is None:
            return None
        if entry_id not in session.entries_affected:
            updated = session.model_copy(update={
                "entries_affected": [*session.entries_affected, entry_id],
            })
            self._sessions[session_id] = updated
            return updated
        return session

    def update_statistics(
        self,
        session_id: str,
        statistics: dict[str, int | float],
    ) -> RegistrySession | None:
        """Update session statistics (merged with existing)."""
        session = self._sessions.get(session_id)
        if session is None:
            return None
        merged = {**session.statistics, **statistics}
        updated = session.model_copy(update={"statistics": merged})
        self._sessions[session_id] = updated
        return updated

    def get_active_sessions(self) -> list[RegistrySession]:
        """Return all sessions with ACTIVE status."""
        return [s for s in self._sessions.values() if s.status == "ACTIVE"]

    def clear(self) -> int:
        """Clear all sessions. Returns the count of cleared sessions."""
        count = len(self._sessions)
        self._sessions.clear()
        return count
