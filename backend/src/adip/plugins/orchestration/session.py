"""PluginSessionManager — manages plugin operation session lifecycle.

Creates, tracks, and completes operation sessions with timing,
dependency tracking, sandbox association, and correlation support.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import structlog

from adip.plugins.contracts.models import PluginSession

log = structlog.get_logger(__name__)


class PluginSessionManager:
    """Manages plugin operation session lifecycle."""

    def __init__(self) -> None:
        self._sessions: dict[str, PluginSession] = {}

    def create_session(
        self,
        plugin_id: str,
        operation: str = "",
        user_id: str = "",
        correlation_id: str = "",
    ) -> PluginSession:
        """Create a new plugin operation session."""
        session = PluginSession(
            plugin_id=uuid.UUID(plugin_id) if isinstance(plugin_id, str) else plugin_id,
            operation=operation,
            user_id=user_id,
            correlation_id=correlation_id or str(uuid.uuid4()),
        )
        self._sessions[str(session.session_id)] = session
        log.info(
            "plugin_session.created",
            session_id=str(session.session_id),
            operation=operation,
            plugin_id=plugin_id,
        )
        return session

    def get_session(self, session_id: str) -> PluginSession | None:
        """Retrieve a session by ID."""
        return self._sessions.get(session_id)

    def complete_session(self, session_id: str) -> PluginSession | None:
        """Mark a session as completed with timing."""
        session = self._sessions.get(session_id)
        if session is None:
            return None

        now = datetime.now(UTC)
        duration = (now - session.started_at).total_seconds() * 1000
        session.completed_at = now
        session.duration_ms = round(duration, 2)
        session.status = "COMPLETED"
        log.info("plugin_session.completed", session_id=session_id, duration_ms=duration)
        return session

    def fail_session(self, session_id: str, error_message: str = "") -> PluginSession | None:
        """Mark a session as failed with an error."""
        session = self._sessions.get(session_id)
        if session is None:
            return None

        now = datetime.now(UTC)
        duration = (now - session.started_at).total_seconds() * 1000
        session.completed_at = now
        session.duration_ms = round(duration, 2)
        session.status = "FAILED"
        session.error_message = error_message
        log.info("plugin_session.failed", session_id=session_id, error=error_message)
        return session

    def update_session_field(self, session_id: str, **kwargs: dict[str, Any]) -> bool:
        """Update session fields dynamically."""
        session = self._sessions.get(session_id)
        if session is None:
            return False
        for key, value in kwargs.items():
            if hasattr(session, key):
                setattr(session, key, value)
        return True

    def get_active_sessions(self) -> list[PluginSession]:
        """Return all sessions that have not completed."""
        return [s for s in self._sessions.values() if s.completed_at is None]

    def get_sessions_by_plugin(self, plugin_id: str) -> list[PluginSession]:
        """Return all sessions for a given plugin."""
        return [s for s in self._sessions.values() if str(s.plugin_id) == plugin_id]

    def clear(self) -> None:
        """Clear all sessions."""
        self._sessions.clear()


from typing import Any  # noqa: E402
