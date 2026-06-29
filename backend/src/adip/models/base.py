"""Declarative Base, timestamp mixin, and common audit columns.

All ADIP SQLAlchemy ORM models should inherit from :class:`Base` and
include :class:`AuditMixin` for consistent primary-key and timestamp
columns.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column


class Base(DeclarativeBase):
    """SQLAlchemy declarative base for all ADIP ORM models."""

    @declared_attr.directive
    def __tablename__(cls) -> str:
        """Auto-derive the table name from the class name (snake_case).

        ``UserProfile`` → ``user_profile``
        """
        name = cls.__name__
        return "".join(f"_{c.lower()}" if c.isupper() else c for c in name).lstrip("_")


class AuditMixin:
    """Common audit columns for every database entity.

    Usage::

        class User(Base, AuditMixin):
            pass
    """

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    """UUID primary key (generated client-side)."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    """Timestamp when the row was inserted (set by the database)."""

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    """Timestamp when the row was last updated (set by the database)."""
