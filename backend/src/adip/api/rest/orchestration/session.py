"""ApiSessionManager — manages API request session lifecycle."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import structlog

from adip.api.rest.enums import OperationStatus
from adip.api.rest.orchestration.models import ApiSession

logger = structlog.get_logger(__name__)


class ApiSessionManager:
    """Manages API session lifecycle."""

    def __init__(self) -> None:
        self._sessions: dict[str, ApiSession] = {}

    def create_session(
        self,
        route: str = "",
        method: str = "GET",
        correlation_id: str | None = None,
        api_version: str = "v1",
    ) -> ApiSession:
        session = ApiSession(
            route=route,
            method=method,
            status=OperationStatus.PENDING,
            correlation_id=correlation_id,
            api_version=api_version,
        )
        self._sessions[str(session.session_id)] = session
        logger.info("api_session.created", session_id=str(session.session_id), route=route, method=method)
        return session

    def get_session(self, session_id: str) -> ApiSession | None:
        return self._sessions.get(session_id)

    def complete_session(self, session_id: str) -> bool:
        session = self._sessions.get(session_id)
        if session is None:
            return False
        session.status = OperationStatus.COMPLETED
        session.completed_at = datetime.now(UTC)
        logger.info("api_session.completed", session_id=session_id)
        return True

    def fail_session(self, session_id: str) -> bool:
        session = self._sessions.get(session_id)
        if session is None:
            return False
        session.status = OperationStatus.FAILED
        session.completed_at = datetime.now(UTC)
        logger.info("api_session.failed", session_id=session_id)
        return True

    def list_sessions(self) -> list[dict[str, Any]]:
        return [
            {
                "session_id": str(s.session_id),
                "route": s.route,
                "method": s.method,
                "status": s.status.value,
                "started_at": s.started_at.isoformat(),
                "completed_at": s.completed_at.isoformat() if s.completed_at else None,
            }
            for s in self._sessions.values()
        ]

    def get_active_sessions(self) -> list[ApiSession]:
        return [s for s in self._sessions.values() if s.status == OperationStatus.PENDING]

    def count(self) -> int:
        return len(self._sessions)

    def clear(self) -> None:
        self._sessions.clear()
