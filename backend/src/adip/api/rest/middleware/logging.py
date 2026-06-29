"""Request/response logging middleware for the REST API Layer."""

from __future__ import annotations

import time
import uuid

import structlog
from starlette.types import ASGIApp, Message, Receive, Scope, Send

logger = structlog.get_logger(__name__)


class RequestLoggingMiddleware:
    """Logs every HTTP request and its response status."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request_id = str(uuid.uuid4())[:8]
        start_time = time.monotonic()
        path = scope.get("path", "/")
        method = scope.get("method", "UNKNOWN")

        status_code: list[int] = [0]

        async def send_with_logging(message: Message) -> None:
            if message["type"] == "http.response.start":
                status_code[0] = message.get("status", 0)
            await send(message)

        try:
            await self.app(scope, receive, send_with_logging)
        except Exception as exc:
            elapsed = (time.monotonic() - start_time) * 1000
            logger.error(
                "request_failed",
                request_id=request_id,
                method=method,
                path=path,
                elapsed_ms=f"{elapsed:.1f}",
                error_type=type(exc).__name__,
            )
            raise

        elapsed = (time.monotonic() - start_time) * 1000
        logger.info(
            "request_completed",
            request_id=request_id,
            method=method,
            path=path,
            status_code=status_code[0],
            elapsed_ms=f"{elapsed:.1f}",
        )
