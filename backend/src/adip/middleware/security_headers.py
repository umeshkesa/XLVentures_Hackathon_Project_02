"""Security response-headers middleware."""

from collections.abc import Sequence

from starlette.types import ASGIApp, Message, Receive, Scope, Send

# ── Content-Security-Policy profiles ──────────────────────────────────────

CSP_PRODUCTION = "default-src 'self'"

CSP_DEVELOPMENT = (
    "default-src 'self'; "
    "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
    "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
    "img-src 'self' data: https://fastapi.tiangolo.com; "
    "font-src 'self' data: https://cdn.jsdelivr.net; "
    "connect-src 'self'"
)

BASE_SECURITY_HEADERS: Sequence[tuple[bytes, bytes]] = (
    (b"x-content-type-options", b"nosniff"),
    (b"x-frame-options", b"DENY"),
    (b"x-xss-protection", b"1; mode=block"),
    (b"strict-transport-security", b"max-age=31536000; includeSubDomains"),
    (b"referrer-policy", b"strict-origin-when-cross-origin"),
    (b"permissions-policy", b"geolocation=(), microphone=(), camera=()"),
)


class SecurityHeadersMiddleware:
    """Attach hardened security headers to every HTTP response.

    ``content-security-policy`` is configurable so that local/development
    environments can permit the CDN-hosted assets required by FastAPI's
    Swagger UI and ReDoc without weakening the production policy.
    """

    def __init__(self, app: ASGIApp, *, csp: str = CSP_PRODUCTION) -> None:
        self.app = app
        self._csp = csp.encode()

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def send_with_headers(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers: list[tuple[bytes, bytes]] = [
                    (b"content-security-policy", self._csp),
                ]
                headers.extend(BASE_SECURITY_HEADERS)
                message.setdefault("headers", []).extend(headers)
            await send(message)

        await self.app(scope, receive, send_with_headers)
