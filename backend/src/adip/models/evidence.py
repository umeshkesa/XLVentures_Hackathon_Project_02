"""SQLAlchemy ORM model for Evidence items."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from adip.models.base import AuditMixin, Base


class EvidenceRecord(Base, AuditMixin):
    """Persistent storage for Evidence items."""

    __tablename__ = "evidence"

    entity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), unique=True, nullable=False, index=True
    )
    evidence_type: Mapped[str] = mapped_column(
        sa.String(50), nullable=False, default="knowledge"
    )
    domain: Mapped[str] = mapped_column(
        sa.String(50), nullable=False, default="system"
    )
    status: Mapped[str] = mapped_column(
        sa.String(50), nullable=False, default="collected"
    )
    source: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, default=dict
    )
    metadata_: Mapped[dict[str, Any]] = mapped_column(
        "metadata", JSONB, nullable=False, default=dict
    )
    provenance: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, default=dict
    )
    quality: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, default=dict
    )
    payload: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, default=dict
    )
    evidence_timestamp: Mapped[datetime | None] = mapped_column(
        sa.DateTime(timezone=True), nullable=True
    )
    serialized: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB, nullable=True, default=None
    )
