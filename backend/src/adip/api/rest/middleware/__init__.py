"""REST API middleware package."""

from __future__ import annotations

from adip.api.rest.middleware.correlation import CorrelationMiddleware
from adip.api.rest.middleware.exception_handler import register_exception_handlers
from adip.api.rest.middleware.logging import RequestLoggingMiddleware
from adip.api.rest.middleware.metrics import MetricsMiddleware
from adip.api.rest.middleware.registration import register_middleware

__all__ = [
    "CorrelationMiddleware",
    "RequestLoggingMiddleware",
    "MetricsMiddleware",
    "register_exception_handlers",
    "register_middleware",
]
