"""SQLAlchemy ORM model for Knowledge Documents."""

from __future__ import annotations

import uuid
from typing import Any

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from adip.models.base import AuditMixin, Base


class KnowledgeDocumentRecord(Base, AuditMixin):
    """Persistent storage for Knowledge Documents."""

    __tablename__ = "knowledge_documents"

    entity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), unique=True, nullable=False, index=True
    )
    document_type: Mapped[str] = mapped_column(
        sa.String(50), nullable=False, default="text"
    )
    domain: Mapped[str] = mapped_column(
        sa.String(50), nullable=False, default="system"
    )
    title: Mapped[str] = mapped_column(
        sa.String(512), nullable=False, default=""
    )
    source: Mapped[str] = mapped_column(
        sa.Text, nullable=False, default=""
    )
    content: Mapped[str] = mapped_column(
        sa.Text, nullable=False, default=""
    )
    status: Mapped[str] = mapped_column(
        sa.String(50), nullable=False, default="pending"
    )
    metadata_: Mapped[dict[str, Any]] = mapped_column(
        "metadata", JSONB, nullable=False, default=dict
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
    version: Mapped[int] = mapped_column(
        sa.Integer, nullable=False, default=1
    )
    serialized: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB, nullable=True, default=None
    )
