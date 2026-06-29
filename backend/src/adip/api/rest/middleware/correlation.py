"""Correlation ID middleware for the REST API Layer."""

from __future__ import annotations

import uuid

from starlette.types import ASGIApp, Message, Receive, Scope, Send
from structlog.contextvars import bind_contextvars


class CorrelationMiddleware:
    """Injects and propagates correlation IDs for distributed tracing.

    Reads the ``X-Correlation-ID`` request header or generates a new UUID.
    The value is bound to the structlog context and echoed back in the
    ``X-Correlation-ID`` response header.
    """

    def __init__(self, app: ASGIApp, header_name: str = "X-Correlation-ID") -> None:
        self.app = app
        self.header_key = header_name.lower().encode()

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = dict(scope.get("headers", []))
        raw = headers.get(self.header_key) or str(uuid.uuid4()).encode()
        cid = raw.decode()
        bind_contextvars(correlation_id=cid)

        async def send_with_header(message: Message) -> None:
            if message["type"] == "http.response.start":
                message.setdefault("headers", []).append(
                    (self.header_key, cid.encode())
                )
            await send(message)

        await self.app(scope, receive, send_with_header)
