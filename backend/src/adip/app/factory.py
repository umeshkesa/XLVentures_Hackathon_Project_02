"""FastAPI application factory."""

from fastapi import FastAPI

from adip import __version__
from adip.api.rest.openapi import configure_openapi as configure_rest_openapi
from adip.api.rest.routers import router as rest_router
from adip.api.router import api_router
from adip.config.settings import get_settings
from adip.core.exceptions.handlers import register_exception_handlers
from adip.logging.configuration import configure_logging
from adip.middleware.registration import register_middleware


def create_application() -> FastAPI:
    """Create and configure the ADIP API application."""
    settings = get_settings()
    configure_logging(settings.logging)

    application = FastAPI(
        title=settings.app.name,
        version=__version__,
        debug=settings.app.debug,
    )
    register_middleware(application, environment=settings.app.environment)
    register_exception_handlers(application)
    configure_rest_openapi(application)
    # REST API routers carry their own /api/v1 prefix; mount directly.
    application.include_router(rest_router)
    # Legacy routers (auth) are mounted under the configured prefix.
    application.include_router(api_router, prefix=settings.api.prefix)
    return application

