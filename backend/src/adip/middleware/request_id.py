"""Request-ID injection middleware."""

import uuid

from starlette.types import ASGIApp, Message, Receive, Scope, Send
from structlog.contextvars import bind_contextvars


class RequestIDMiddleware:
    """Inject a unique ``request_id`` into the structlog context and response.

    Reads the ``X-Request-ID`` header from the incoming request, or generates a
    new ``uuid4`` if none is provided.  The value is exposed in the structlog
    context and echoed back in the ``X-Request-ID`` response header.
    """

    def __init__(self, app: ASGIApp, header_name: str = "X-Request-ID") -> None:
        self.app = app
        self.header_name = header_name.lower().encode()

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = dict(scope.get("headers", []))
        request_id = headers.get(self.header_name) or str(uuid.uuid4()).encode()
        rid = request_id.decode()

        bind_contextvars(request_id=rid)

        async def send_with_header(message: Message) -> None:
            if message["type"] == "http.response.start":
                message.setdefault("headers", []).append(
                    (self.header_name, rid.encode())
                )
            await send(message)

        await self.app(scope, receive, send_with_header)
