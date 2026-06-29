"""Global exception handling."""

from typing import Any

import structlog
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from structlog.contextvars import get_contextvars

from adip.core.exceptions.base import BaseApplicationException

logger = structlog.get_logger(__name__)

SECURITY_HEADERS: dict[str, str] = {
    "content-security-policy": "default-src 'self'",
    "x-content-type-options": "nosniff",
    "x-frame-options": "DENY",
    "x-xss-protection": "1; mode=block",
    "strict-transport-security": "max-age=31536000; includeSubDomains",
    "referrer-policy": "strict-origin-when-cross-origin",
    "permissions-policy": "geolocation=(), microphone=(), camera=()",
}


def _error_envelope(
    code: str,
    message: str,
    *,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the standard ADIP error response body."""
    envelope: dict[str, Any] = {"error": {"code": code, "message": message}}
    if details:
        envelope["error"]["details"] = details
    return envelope


def _with_trace_headers(headers: dict[str, str]) -> dict[str, str]:
    """Copy trace identifiers from the structlog context into *headers*."""
    ctx = get_contextvars()
    for key in ("request_id", "correlation_id"):
        value = ctx.get(key)
        if value:
            header_key = "x-request-id" if key == "request_id" else "x-correlation-id"
            headers[header_key] = str(value)
    return headers


async def base_application_exception_handler(
    request: Request,
    exc: BaseApplicationException,
) -> JSONResponse:
    """Handle known application exceptions."""
    logger.warning(
        "application_exception",
        code=exc.code,
        status_code=exc.status_code,
        path=request.url.path,
        error_type=type(exc).__name__,
    )
    headers = _with_trace_headers({})
    return JSONResponse(
        status_code=exc.status_code,
        content=_error_envelope(exc.code, exc.message, details=exc.details),
        headers=headers,
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Log unexpected failures and return a stable error envelope."""
    try:
        logger.exception(
            "unhandled_exception",
            path=request.url.path,
            error_type=type(exc).__name__,
        )
    except Exception:
        logger.error(
            "unhandled_exception_logging_failed",
            path=request.url.path,
            error_type=type(exc).__name__,
        )
    headers = _with_trace_headers(dict(SECURITY_HEADERS))
    return JSONResponse(
        status_code=500,
        content=_error_envelope(
            "internal_server_error",
            "An unexpected error occurred.",
        ),
        headers=headers,
    )


def register_exception_handlers(application: FastAPI) -> None:
    """Register application-wide exception handlers.

    Handlers are registered from most- to least-specific so that Starlette's
    MRO-based lookup dispatches to the correct handler for each exception type.
    """
    application.add_exception_handler(BaseApplicationException, base_application_exception_handler)
    application.add_exception_handler(Exception, unhandled_exception_handler)

