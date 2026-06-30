"""SQLAlchemy ORM model for Rules."""

from __future__ import annotations

import uuid
from typing import Any

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from adip.models.base import AuditMixin, Base


class RuleRecord(Base, AuditMixin):
    """Persistent storage for Rules."""

    __tablename__ = "rules"

    entity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), unique=True, nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(
        sa.String(512), nullable=False, default=""
    )
    description: Mapped[str] = mapped_column(
        sa.Text, nullable=False, default=""
    )
    domain: Mapped[str] = mapped_column(
        sa.String(50), nullable=False, default="system"
    )
    rule_type: Mapped[str] = mapped_column(
        sa.String(50), nullable=False, default="business"
    )
    status: Mapped[str] = mapped_column(
        sa.String(50), nullable=False, default="draft"
    )
    conditions: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB, nullable=False, default=list
    )
    actions: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB, nullable=False, default=list
    )
    priority: Mapped[int] = mapped_column(
        sa.Integer, nullable=False, default=0
    )
    version: Mapped[int] = mapped_column(
        sa.Integer, nullable=False, default=1
    )
    tags: Mapped[list[str]] = mapped_column(
        JSONB, nullable=False, default=list
    )
    owner_id: Mapped[str] = mapped_column(
        sa.String(256), nullable=False, default=""
    )
    namespace: Mapped[str] = mapped_column(
        sa.String(128), nullable=False, default="default"
    )
    category: Mapped[str] = mapped_column(
        sa.String(128), nullable=False, default=""
    )
    scope: Mapped[str] = mapped_column(
        sa.String(128), nullable=False, default=""
    )
    serialized: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB, nullable=True, default=None
    )
