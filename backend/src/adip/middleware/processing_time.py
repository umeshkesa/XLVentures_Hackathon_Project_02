"""Processing-time response header middleware."""

import time

from starlette.types import ASGIApp, Message, Receive, Scope, Send


class ProcessingTimeMiddleware:
    """Add an ``X-Processing-Time`` response header with the elapsed wall-clock
    time of each request in milliseconds.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app
        self.header_name = b"x-processing-time"

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        start = time.monotonic()

        async def send_with_header(message: Message) -> None:
            if message["type"] == "http.response.start":
                elapsed_ms = (time.monotonic() - start) * 1000
                message.setdefault("headers", []).append(
                    (self.header_name, f"{elapsed_ms:.0f}".encode())
                )
            await send(message)

        await self.app(scope, receive, send_with_header)
