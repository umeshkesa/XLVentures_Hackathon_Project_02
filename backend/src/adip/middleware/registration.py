"""Application middleware registration boundary."""

from fastapi import FastAPI

from adip.core.constants import Environment
from adip.middleware.correlation_id import CorrelationIDMiddleware
from adip.middleware.processing_time import ProcessingTimeMiddleware
from adip.middleware.request_id import RequestIDMiddleware
from adip.middleware.request_logging import RequestLoggingMiddleware
from adip.middleware.security_headers import CSP_DEVELOPMENT, CSP_PRODUCTION, SecurityHeadersMiddleware

_DEV_ENVIRONMENTS = frozenset({
    Environment.LOCAL,
    Environment.DEVELOPMENT,
    Environment.TEST,
})


def register_middleware(application: FastAPI, environment: Environment = Environment.PRODUCTION) -> None:
    """Register HTTP middleware.

    Order (outermost → innermost):

    1. ``SecurityHeadersMiddleware``   – add security headers to every response
    2. ``ProcessingTimeMiddleware``    – add ``X-Processing-Time`` header
    3. ``RequestLoggingMiddleware``    – log every request/response pair
    4. ``CorrelationIDMiddleware``     – inject cross-service correlation ID
    5. ``RequestIDMiddleware``         – inject per-request ID for debugging

    Parameters
    ----------
    application
        The FastAPI application instance.
    environment
        Controls the Content-Security-Policy profile.  Local, development and
        test environments use a relaxed policy that permits the CDN-hosted
        assets required by FastAPI's Swagger UI and ReDoc.
    """
    csp = CSP_DEVELOPMENT if environment in _DEV_ENVIRONMENTS else CSP_PRODUCTION

    # Innermost – registered first, closest to the router.
    application.add_middleware(RequestIDMiddleware)
    application.add_middleware(CorrelationIDMiddleware)
    application.add_middleware(RequestLoggingMiddleware)
    application.add_middleware(ProcessingTimeMiddleware)
    # Outermost – registered last, wraps everything else.
    application.add_middleware(SecurityHeadersMiddleware, csp=csp)

