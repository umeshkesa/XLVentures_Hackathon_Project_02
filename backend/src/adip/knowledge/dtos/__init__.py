"""Knowledge Manager Data Transfer Objects (DTOs).

DTOs provide stable, versioned contracts for external API consumers.
They decouple the public API surface from internal domain models.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import UUID4, BaseModel, Field

from adip.knowledge.enums import DocumentType, KnowledgeDomain, RetrievalType


class KnowledgeRequestDTO(BaseModel):
    """DTO for incoming knowledge ingestion requests.

    Provides a clean API contract for document ingestion that is
    independent of the internal KnowledgeDocument model.
    """

    title: str = Field(
        default="",
        description="Document title",
    )
    source: str = Field(
        default="",
        description="Original source identifier",
    )
    content: str = Field(
        default="",
        description="Raw text content of the document",
    )
    document_type: DocumentType = Field(
        description="The type of document being ingested",
    )
    domain: KnowledgeDomain = Field(
        default=KnowledgeDomain.SYSTEM,
        description="The knowledge domain of the document",
    )
    owner_id: str = Field(
        default="",
        description="The user or system that owns this document",
    )
    namespace: str = Field(
        default="default",
        description="Logical namespace for multi-tenant isolation",
    )
    tags: list[str] = Field(
        default_factory=list,
        description="User-defined tags for classification",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata key-value pairs",
    )


class KnowledgeResponseDTO(BaseModel):
    """DTO for knowledge operation responses.

    Provides a stable API response contract independent of the
    internal domain model structure.
    """

    document_id: UUID4 = Field(
        description="The document identifier",
    )
    title: str = Field(
        default="",
        description="Document title",
    )
    document_type: DocumentType = Field(
        description="The type of document",
    )
    domain: KnowledgeDomain = Field(
        default=KnowledgeDomain.SYSTEM,
        description="The knowledge domain",
    )
    status: str = Field(
        default="PENDING",
        description="Current processing status",
    )
    version: int = Field(
        default=1,
        ge=1,
        description="Document version number",
    )
    created_at: datetime = Field(
        description="When the document was created",
    )
    updated_at: datetime = Field(
        description="When the document was last updated",
    )


class KnowledgeSearchDTO(BaseModel):
    """DTO for knowledge search requests.

    Provides a clean API contract for search that is independent
    of the internal KnowledgeQuery model.
    """

    query_text: str = Field(
        default="",
        description="The search query text",
    )
    retrieval_type: RetrievalType = Field(
        default=RetrievalType.HYBRID,
        description="The retrieval strategy to use",
    )
    domains: list[KnowledgeDomain] = Field(
        default_factory=list,
        description="Restrict to specific knowledge domains",
    )
    document_types: list[DocumentType] = Field(
        default_factory=list,
        description="Restrict to specific document types",
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Filter by tags",
    )
    namespace: str = Field(
        default="",
        description="Filter by namespace",
    )
    owner_id: str = Field(
        default="",
        description="Filter by owner",
    )
    limit: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum number of results",
    )
    offset: int = Field(
        default=0,
        ge=0,
        description="Number of results to skip",
    )
    min_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Minimum relevance score threshold",
    )


class KnowledgeContextDTO(BaseModel):
    """DTO for knowledge context responses.

    Provides a stable API response contract for context assembly
    that is independent of the internal KnowledgeContext model.
    """

    context_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique context identifier",
    )
    query_text: str = Field(
        default="",
        description="The original query text",
    )
    total_results: int = Field(
        default=0,
        ge=0,
        description="Total number of matching results",
    )
    domains: list[str] = Field(
        default_factory=list,
        description="Knowledge domains covered",
    )
    document_types: list[str] = Field(
        default_factory=list,
        description="Document types covered",
    )
    results: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Serialised retrieval results",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Context-level metadata",
    )
    created_at: str = Field(
        default_factory=lambda: datetime.now(UTC).isoformat(),
        description="When the context was assembled",
    )
