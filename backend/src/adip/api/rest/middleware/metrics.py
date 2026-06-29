"""Metrics collection middleware for the REST API Layer."""

from __future__ import annotations

import time

import structlog
from starlette.types import ASGIApp, Message, Receive, Scope, Send

logger = structlog.get_logger(__name__)


class MetricsMiddleware:
    """Collects basic HTTP metrics for each request.

    Tracks request count, active requests, and latency distribution
    per method and path. Metrics are logged as structured events.
    """

    _request_counts: dict[str, int] = {}
    _active_requests: int = 0

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        method = scope.get("method", "UNKNOWN")
        path = scope.get("path", "/")
        route_key = f"{method}:{path}"

        self.__class__._active_requests += 1
        self.__class__._request_counts[route_key] = self.__class__._request_counts.get(route_key, 0) + 1
        start_time = time.monotonic()
        status_code: list[int] = [0]

        async def send_with_metrics(message: Message) -> None:
            if message["type"] == "http.response.start":
                status_code[0] = message.get("status", 0)
            await send(message)

        try:
            await self.app(scope, receive, send_with_metrics)
        finally:
            self.__class__._active_requests -= 1
            elapsed = (time.monotonic() - start_time) * 1000
            logger.debug(
                "http_metrics",
                method=method,
                path=path,
                status_code=status_code[0],
                latency_ms=f"{elapsed:.1f}",
                active_requests=self.__class__._active_requests,
            )

    @classmethod
    def get_request_count(cls, route_key: str | None = None) -> int:
        if route_key:
            return cls._request_counts.get(route_key, 0)
        return sum(cls._request_counts.values())

    @classmethod
    def get_active_requests(cls) -> int:
        return cls._active_requests

    @classmethod
    def reset(cls) -> None:
        cls._request_counts.clear()
        cls._active_requests = 0
