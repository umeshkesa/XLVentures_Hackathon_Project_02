"""SQLAlchemy async engine and session factory.

Usage (FastAPI dependency)::

    from adip.database.connections import get_session

    @router.get("/items")
    async def list_items(session: AsyncSession = Depends(get_session)):
        ...
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from adip.config.settings import DatabaseConfig

_factory: async_sessionmaker[AsyncSession] | None = None


def create_engine(config: DatabaseConfig) -> AsyncEngine:
    """Build and return an async SQLAlchemy engine from *config*."""
    return create_async_engine(
        url=str(config.dsn),
        pool_size=config.pool_size,
        max_overflow=config.max_overflow,
        pool_recycle=config.pool_recycle,
        echo=config.echo,
        pool_pre_ping=True,
    )


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Return a configured ``async_sessionmaker`` bound to *engine*."""
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


def init_session_factory(config: DatabaseConfig | None = None) -> None:
    """Initialise the global session factory (call at app startup)."""
    global _factory
    cfg = config or DatabaseConfig()
    engine = create_engine(cfg)
    _factory = create_session_factory(engine)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield an :class:`AsyncSession` for use as a FastAPI dependency.

    The session is automatically closed when the request finishes.
    Requires :func:`init_session_factory` to have been called at startup.
    """
    global _factory
    if _factory is None:
        init_session_factory()
    async with _factory() as session:
        try:
            yield session
        finally:
            await session.close()
