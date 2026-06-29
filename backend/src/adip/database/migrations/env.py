"""Alembic migration environment for ADIP.

Uses the async SQLAlchemy engine and auto-discovers all ORM models
that import :class:`adip.models.base.Base` so that ``--autogenerate``
picks up schema changes automatically.

Run migrations::

    alembic upgrade head

Auto-generate a new revision::

    alembic revision --autogenerate -m "describe change"
"""

from __future__ import annotations

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from adip.config.settings import get_settings
from adip.models.base import Base

# Alembic's ``logging.ini`` configuration (if present).
if context.config.config_file_name is not None:
    fileConfig(context.config.config_file_name)

# Import all ORM models here so they are registered on ``Base.metadata``.
# pylint: disable-next=unused-import
import adip.models  # noqa: F401

config = context.config
target_metadata = Base.metadata

settings = get_settings()
config.set_main_option("sqlalchemy.url", str(settings.database.dsn))


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (emit SQL without a connection)."""
    context.configure(
        url=str(settings.database.dsn),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode against a live database."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
