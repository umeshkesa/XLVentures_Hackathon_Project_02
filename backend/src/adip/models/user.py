"""SQLAlchemy User model."""

from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from adip.core.constants import Role
from adip.models.base import AuditMixin, Base


class User(Base, AuditMixin):
    """Application user with role-based access control."""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(320), unique=True, nullable=False, index=True
    )
    """Unique email address used as the login identifier."""

    hashed_password: Mapped[str] = mapped_column(
        String(128), nullable=False
    )
    """bcrypt hash of the user's password."""

    full_name: Mapped[str | None] = mapped_column(String(256), default=None)
    """Optional display name."""

    role: Mapped[Role] = mapped_column(
        sa.Enum(Role, name="user_role", create_constraint=True),
        nullable=False,
    )
    """Assigned role which determines effective permissions."""

    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )
    """Soft-disable flag — inactive users cannot authenticate."""
