"""Sync SQLAlchemy engine and session for domain coordinators.

All domain coordinators (Evidence, Knowledge, Rules, etc.) are synchronous,
so they cannot use the async session factory from
``adip.database.connections.session``. This module provides a sync
counterpart that shares the same configuration.
"""

from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import URL, create_engine, make_url
from sqlalchemy.orm import Session, sessionmaker

from adip.config.settings import DatabaseConfig

_factory: sessionmaker[Session] | None = None


def _to_sync_dsn(raw: str | URL) -> URL:
    """Convert an async DSN (``postgresql+asyncpg://``) to sync (``postgresql+psycopg2://``)."""
    url = make_url(str(raw)) if not isinstance(raw, URL) else raw
    drivername = url.drivername.replace("+asyncpg", "+psycopg2")
    return url.set(drivername=drivername)


def init_sync_factory(config: DatabaseConfig | None = None) -> None:
    """Initialise the global sync session factory (call at app startup)."""
    global _factory
    cfg = config or DatabaseConfig()
    sync_dsn = _to_sync_dsn(cfg.dsn)
    engine = create_engine(
        url=sync_dsn,
        pool_size=cfg.pool_size,
        max_overflow=cfg.max_overflow,
        pool_recycle=cfg.pool_recycle,
        echo=cfg.echo,
        pool_pre_ping=True,
    )
    _factory = sessionmaker(bind=engine, expire_on_commit=False)


def is_db_available() -> bool:
    """Check if the sync database factory has been initialised."""
    global _factory
    return _factory is not None


@contextmanager
def get_sync_session() -> Generator[Session, None, None]:
    """Yield a sync :class:`Session` for domain coordinator use.

    Requires :func:`init_sync_factory` to have been called at startup.
    """
    global _factory
    if _factory is None:
        raise RuntimeError(
            "Sync database factory not initialised. "
            "Call init_sync_factory() at application startup."
        )
    session = _factory()
    try:
        yield session
        session.commit()
    except BaseException:
        session.rollback()
        raise
    finally:
        session.close()
