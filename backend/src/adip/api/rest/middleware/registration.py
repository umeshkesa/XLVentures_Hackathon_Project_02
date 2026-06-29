"""Middleware registration for the REST API Layer."""

from __future__ import annotations

from fastapi import FastAPI

from adip.api.rest.middleware.correlation import CorrelationMiddleware
from adip.api.rest.middleware.exception_handler import register_exception_handlers
from adip.api.rest.middleware.logging import RequestLoggingMiddleware
from adip.api.rest.middleware.metrics import MetricsMiddleware


def register_middleware(application: FastAPI) -> None:
    """Register REST API middleware on a FastAPI application.

    Order (outermost → innermost):
    1. ``MetricsMiddleware``     – request metrics collection
    2. ``RequestLoggingMiddleware`` – request/response logging
    3. ``CorrelationMiddleware``  – correlation ID injection
    """
    application.add_middleware(CorrelationMiddleware)
    application.add_middleware(RequestLoggingMiddleware)
    application.add_middleware(MetricsMiddleware)
    register_exception_handlers(application)
