"""Knowledge Manager event models.

Events follow the standard ADIP eventing contract with a base
KnowledgeEvent and concrete event types for each knowledge
operation. All events carry enterprise fields (event_id,
timestamp, correlation_id, payload) for tracing and audit.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import UUID4, BaseModel, Field

from adip.knowledge.enums import DocumentType, KnowledgeDomain, KnowledgeStatus

EventVersion: str = "1.0.0"


class KnowledgeEvent(BaseModel):
    """Base event for all knowledge operations.

    Provides standard enterprise event fields shared by every
    concrete knowledge event.
    """

    event_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique event identifier",
    )
    document_id: UUID4 = Field(
        description="The knowledge document this event relates to",
    )
    document_type: DocumentType = Field(
        description="The type of document involved",
    )
    domain: KnowledgeDomain = Field(
        default=KnowledgeDomain.SYSTEM,
        description="The knowledge domain of the document",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the event was emitted",
    )
    correlation_id: str = Field(
        default="",
        description="Correlation ID for distributed tracing",
    )
    payload: dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary event payload data",
    )


class KnowledgeCreated(KnowledgeEvent):
    """Emitted when a new knowledge document is created (ingested)."""


class KnowledgeUpdated(KnowledgeEvent):
    """Emitted when an existing knowledge document is updated."""

    previous_version: int = Field(
        default=0,
        ge=0,
        description="The document version before the update",
    )


class KnowledgeIndexed(KnowledgeEvent):
    """Emitted when a knowledge document has been fully indexed."""

    status: KnowledgeStatus = Field(
        default=KnowledgeStatus.INDEXED,
        description="The indexing status after completion",
    )
    chunk_count: int = Field(
        default=0,
        ge=0,
        description="Number of chunks indexed",
    )


class KnowledgeRetrieved(KnowledgeEvent):
    """Emitted when knowledge is retrieved in response to a query."""

    query_text: str = Field(
        default="",
        description="The original query text",
    )
    result_count: int = Field(
        default=0,
        ge=0,
        description="Number of results returned",
    )
    retrieval_type: str = Field(
        default="",
        description="The retrieval strategy used",
    )


class KnowledgeArchived(KnowledgeEvent):
    """Emitted when a knowledge document is archived."""

    reason: str = Field(
        default="",
        description="Reason for archiving",
    )


class KnowledgeDeleted(KnowledgeEvent):
    """Emitted when a knowledge document is permanently deleted."""

    reason: str = Field(
        default="",
        description="Reason for deletion",
    )
