"""KnowledgeSession — manages retrieval session lifecycle.

Creates, completes, and tracks sessions for knowledge retrieval
operations with full observability metadata.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import structlog

from adip.knowledge.contracts.models import KnowledgeSession

log = structlog.get_logger(__name__)


class KnowledgeSessionManager:
    """Manages the lifecycle of knowledge retrieval sessions."""

    def __init__(self) -> None:
        self._sessions: dict[str, KnowledgeSession] = {}

    def create_session(
        self,
        query: str = "",
        user_id: str = "",
        correlation_id: str = "",
        retrieval_strategy: str = "HYBRID",
    ) -> KnowledgeSession:
        """Create a new retrieval session."""
        session = KnowledgeSession(
            query=query,
            user_id=user_id,
            correlation_id=correlation_id,
            retrieval_strategy=retrieval_strategy,
            started_at=datetime.now(UTC),
        )
        self._sessions[str(session.session_id)] = session
        log.info(
            "session.created",
            session_id=str(session.session_id),
            user_id=user_id,
            strategy=retrieval_strategy,
        )
        return session

    def complete_session(
        self,
        session: KnowledgeSession,
        duration_ms: float = 0.0,
        documents_used: list[str] | None = None,
        versions_used: list[int] | None = None,
        chunks_used: list[str] | None = None,
        cache_hits: int = 0,
        processing_statistics: dict[str, Any] | None = None,
    ) -> KnowledgeSession:
        """Mark a session as completed with its statistics."""
        session.completed_at = datetime.now(UTC)
        session.duration_ms = duration_ms
        session.documents_used = documents_used or []
        session.versions_used = versions_used or []
        session.chunks_used = chunks_used or []
        session.cache_hits = cache_hits
        session.processing_statistics = processing_statistics or {}
        log.info(
            "session.completed",
            session_id=str(session.session_id),
            duration_ms=duration_ms,
            documents=len(session.documents_used),
        )
        return session

    def get_session(self, session_id: str) -> KnowledgeSession | None:
        """Retrieve a session by ID."""
        return self._sessions.get(session_id)

    def clear(self) -> None:
        """Clear all sessions."""
        self._sessions.clear()
