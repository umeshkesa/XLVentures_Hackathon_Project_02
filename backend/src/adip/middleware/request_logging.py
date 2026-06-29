"""Request / response logging middleware."""

import time

import structlog
from starlette.types import ASGIApp, Message, Receive, Scope, Send

logger = structlog.get_logger(__name__)


class RequestLoggingMiddleware:
    """Log every HTTP request and its response.

    Emits an ``info``-level log entry when a request arrives and another when
    the response completes, including the HTTP method, path, status code, and
    elapsed time in milliseconds.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        start = time.monotonic()
        status_code = 0

        async def log_send(message: Message) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            await send(message)

        try:
            await self.app(scope, receive, log_send)
        finally:
            elapsed_ms = (time.monotonic() - start) * 1000
            method = scope.get("method", "")
            path = scope.get("path", "")
            if status_code >= 500:
                log = logger.error
            elif status_code >= 400:
                log = logger.warning
            else:
                log = logger.info
            log(
                "request_complete",
                method=method,
                path=path,
                status_code=status_code,
                elapsed_ms=round(elapsed_ms, 1),
            )
