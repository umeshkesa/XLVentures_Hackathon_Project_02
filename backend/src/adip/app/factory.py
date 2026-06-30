"""FastAPI application factory."""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from adip import __version__
from adip.api.rest.openapi import configure_openapi as configure_rest_openapi
from adip.api.rest.routers import router as rest_router
from adip.api.router import api_router
from adip.config.settings import get_settings
from adip.core.exceptions.handlers import register_exception_handlers
from adip.database.connections.session import init_session_factory as init_async_session_factory
from adip.infrastructure.cache import init_redis_cache
from adip.infrastructure.database import get_sync_session, init_sync_factory
from adip.logging.configuration import configure_logging
from adip.middleware.registration import register_middleware
from adip.models.base import Base

log = logging.getLogger(__name__)


def _init_database() -> None:
    """Initialize database engines, Redis cache, and run migrations (best-effort)."""
    settings = get_settings()
    try:
        init_async_session_factory(settings.database)
        init_sync_factory(settings.database)
        log.info("Database engines initialised")
    except Exception as exc:
        log.warning("Database not available — persistence disabled: %s", exc)
    _init_redis()
    if settings.database.migrate:
        try:
            _run_migrations()
        except Exception as exc:
            log.warning("Migration skipped — DB unavailable: %s", exc)


def _init_redis() -> None:
    """Initialize the Redis cache client (best-effort)."""
    try:
        init_redis_cache()
        log.info("Redis cache initialised")
    except Exception as exc:
        log.warning("Redis not available — caching disabled: %s", exc)


def _run_migrations() -> None:
    """Create all tables via SQLAlchemy metadata (lightweight migration)."""
    try:
        from alembic.config import Config
        from alembic.command import upgrade

        cfg = Config("alembic.ini")
        upgrade(cfg, "head")
        log.info("Alembic migrations applied successfully")
        return
    except Exception:
        log.warning("Alembic migration failed, falling back to table creation")

    try:
        with get_sync_session() as session:
            engine = session.get_bind()
            Base.metadata.create_all(bind=engine)
        log.info("Tables created via Base.metadata.create_all")
    except Exception as exc:
        log.warning("Could not create tables — DB may not be available yet: %s", exc)


def create_application() -> FastAPI:
    """Create and configure the ADIP API application."""
    settings = get_settings()
    configure_logging(settings.logging)

    _init_database()

    application = FastAPI(
        title=settings.app.name,
        version=__version__,
        debug=settings.app.debug,
    )
    # CORSMiddleware must be the outermost middleware to ensure CORS headers
    # are set even when downstream handlers throw exceptions.
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.api.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_middleware(application, environment=settings.app.environment)
    register_exception_handlers(application)
    configure_rest_openapi(application)
    # REST API routers carry their own /api/v1 prefix; mount directly.
    application.include_router(rest_router)
    # Legacy routers (auth) are mounted under the configured prefix.
    application.include_router(api_router, prefix=settings.api.prefix)
    return application

