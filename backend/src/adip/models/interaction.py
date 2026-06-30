"""SQLAlchemy ORM model for Customer Interactions."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from adip.models.base import AuditMixin, Base


class InteractionRecord(Base, AuditMixin):
    """Persistent storage for Customer Interactions."""

    __tablename__ = "interactions"

    entity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), unique=True, nullable=False, index=True
    )
    interaction_type: Mapped[str] = mapped_column(
        sa.String(50), nullable=False
    )
    title: Mapped[str] = mapped_column(
        sa.String(512), nullable=False, default=""
    )
    description: Mapped[str] = mapped_column(
        sa.Text, nullable=False, default=""
    )
    status: Mapped[str] = mapped_column(
        sa.String(50), nullable=False, default="completed"
    )
    priority: Mapped[str] = mapped_column(
        sa.String(50), nullable=False, default="medium"
    )
    customer_id: Mapped[str] = mapped_column(
        sa.String(128), nullable=False, default=""
    )
    customer_name: Mapped[str] = mapped_column(
        sa.String(256), nullable=False, default=""
    )
    asset_id: Mapped[str | None] = mapped_column(
        sa.String(128), nullable=True, default=None
    )
    related_evidence_ids: Mapped[list[str]] = mapped_column(
        JSONB, nullable=False, default=list
    )
    related_recommendation_ids: Mapped[list[str]] = mapped_column(
        JSONB, nullable=False, default=list
    )
    metadata_: Mapped[dict[str, Any]] = mapped_column(
        "metadata", JSONB, nullable=False, default=dict
    )
    interaction_timestamp: Mapped[datetime | None] = mapped_column(
        sa.DateTime(timezone=True), nullable=True, default=None
    )
    serialized: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB, nullable=True, default=None
    )
