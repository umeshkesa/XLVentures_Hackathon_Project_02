"""Correlation-ID injection middleware."""

import uuid

from starlette.types import ASGIApp, Message, Receive, Scope, Send
from structlog.contextvars import bind_contextvars


class CorrelationIDMiddleware:
    """Inject a ``correlation_id`` into the structlog context and response.

    Reads the ``X-Correlation-ID`` header from the incoming request, or generates
    a new ``uuid4`` if none is provided.  The value is echoed back in the
    ``X-Correlation-ID`` response header so that downstream services can follow
    the request across service boundaries.
    """

    def __init__(self, app: ASGIApp, header_name: str = "X-Correlation-ID") -> None:
        self.app = app
        self.header_name = header_name.lower().encode()

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = dict(scope.get("headers", []))
        correlation_id = headers.get(self.header_name) or str(uuid.uuid4()).encode()
        cid = correlation_id.decode()

        bind_contextvars(correlation_id=cid)

        async def send_with_header(message: Message) -> None:
            if message["type"] == "http.response.start":
                message.setdefault("headers", []).append(
                    (self.header_name, cid.encode())
                )
            await send(message)

        await self.app(scope, receive, send_with_header)
