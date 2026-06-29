"""RequestReplayPackage — stores deterministic replay metadata excluding auth credentials and secrets.

Phase 3.5 replay support for debugging and diagnostics.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

import structlog

logger = structlog.get_logger(__name__)

SENSITIVE_HEADERS = frozenset({"authorization", "cookie", "set-cookie", "x-api-key", "x-auth-token", "x-session-id"})


class RequestReplayPackage:
    """Stores deterministic replay metadata for a single request.

    Authentication credentials and secrets are excluded.
    """

    def __init__(self) -> None:
        self.replay_id: UUID = uuid4()
        self.created_at: datetime = datetime.now(UTC)
        self.method: str = ""
        self.path: str = ""
        self.query_params: dict[str, str] = {}
        self.headers: dict[str, str] = {}
        self.body: dict[str, Any] | None = None
        self.route_params: dict[str, str] = {}
        self.timing_ms: float = 0.0
        self.status_code: int = 200

    def to_dict(self) -> dict[str, Any]:
        return {
            "replay_id": str(self.replay_id),
            "created_at": self.created_at.isoformat(),
            "method": self.method,
            "path": self.path,
            "query_params": self.query_params,
            "headers": self.headers,
            "body": self.body,
            "route_params": self.route_params,
            "timing_ms": self.timing_ms,
            "status_code": self.status_code,
        }


class RequestReplayStore:
    """Manages request replay packages for debugging and diagnostics."""

    def __init__(self) -> None:
        self._packages: dict[str, RequestReplayPackage] = {}

    @staticmethod
    def _sanitize_headers(headers: dict[str, str]) -> dict[str, str]:
        return {k: v for k, v in headers.items() if k.lower() not in SENSITIVE_HEADERS}

    def create_package(
        self,
        method: str,
        path: str,
        headers: dict[str, str] | None = None,
        body: dict[str, Any] | None = None,
        query_params: dict[str, str] | None = None,
        route_params: dict[str, str] | None = None,
        timing_ms: float = 0.0,
        status_code: int = 200,
    ) -> RequestReplayPackage:
        package = RequestReplayPackage()
        package.method = method.upper()
        package.path = path
        package.headers = self._sanitize_headers(headers or {})
        package.body = body
        package.query_params = query_params or {}
        package.route_params = route_params or {}
        package.timing_ms = timing_ms
        package.status_code = status_code
        self._packages[str(package.replay_id)] = package
        logger.info("replay_package.created", replay_id=str(package.replay_id))
        return package

    def get_package(self, replay_id: str) -> RequestReplayPackage | None:
        return self._packages.get(replay_id)

    def list_packages(self) -> list[dict[str, Any]]:
        return [p.to_dict() for p in self._packages.values()]

    def count(self) -> int:
        return len(self._packages)

    def clear(self) -> None:
        self._packages.clear()
