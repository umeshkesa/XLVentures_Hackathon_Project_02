"""Seed the database with a default Super Admin user for development.

Usage::

    from adip.database.seed.admin import seed_admin_user

    async def on_startup():
        async with async_session_maker() as session:
            await seed_admin_user(session)
"""

from __future__ import annotations

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from adip.core.constants import Role
from adip.models.user import User
from adip.security.password import hash_password

logger = structlog.get_logger(__name__)

DEFAULT_ADMIN_EMAIL = "admin@adip.local"
DEFAULT_ADMIN_PASSWORD = "Admin123!"  # noqa: S105


async def seed_admin_user(session: AsyncSession) -> User | None:
    """Ensure a default Super Admin user exists in the database.

    Returns the existing or newly-created user, or ``None`` if the
    user already existed (no action taken).
    """
    result = await session.execute(
        select(User).where(User.email == DEFAULT_ADMIN_EMAIL)
    )
    existing = result.scalar_one_or_none()
    if existing is not None:
        logger.info("admin_user_already_exists", email=DEFAULT_ADMIN_EMAIL)
        return None

    user = User(
        email=DEFAULT_ADMIN_EMAIL,
        hashed_password=hash_password(DEFAULT_ADMIN_PASSWORD),
        full_name="Default Super Admin",
        role=Role.SUPER_ADMIN,
        is_active=True,
    )
    session.add(user)
    await session.flush()
    logger.info("admin_user_created", email=DEFAULT_ADMIN_EMAIL)
    return user
