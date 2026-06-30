"""SQLAlchemy ORM model for Recommendations."""

from __future__ import annotations

import uuid
from typing import Any

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from adip.models.base import AuditMixin, Base


class RecommendationRecord(Base, AuditMixin):
    """Persistent storage for Recommendations."""

    __tablename__ = "recommendations"

    entity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), unique=True, nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(
        sa.String(50), nullable=False, default="pending"
    )
    priority: Mapped[str] = mapped_column(
        sa.String(50), nullable=False, default="medium"
    )
    recommendation_type: Mapped[str] = mapped_column(
        sa.String(50), nullable=False, default="corrective"
    )
    source: Mapped[str] = mapped_column(
        sa.String(128), nullable=False, default=""
    )
    title: Mapped[str] = mapped_column(
        sa.String(512), nullable=False, default=""
    )
    description: Mapped[str] = mapped_column(
        sa.Text, nullable=False, default=""
    )
    domain: Mapped[str] = mapped_column(
        sa.String(50), nullable=False, default="system"
    )
    confidence: Mapped[float] = mapped_column(
        sa.Float, nullable=False, default=0.0
    )
    estimated_cost: Mapped[float | None] = mapped_column(
        sa.Float, nullable=True, default=None
    )
    estimated_savings: Mapped[float | None] = mapped_column(
        sa.Float, nullable=True, default=None
    )
    action: Mapped[str] = mapped_column(
        sa.Text, nullable=False, default=""
    )
    reasoning_session_id: Mapped[str | None] = mapped_column(
        sa.String(256), nullable=True, default=None
    )
    metadata_: Mapped[dict[str, Any]] = mapped_column(
        "metadata", JSONB, nullable=False, default=dict
    )
    serialized: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB, nullable=True, default=None
    )
