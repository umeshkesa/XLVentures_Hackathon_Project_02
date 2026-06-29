"""Knowledge Manager domain models.

Defines the core data contracts for the knowledge platform including
documents, chunks, embeddings, indices, queries, results, context,
health, and metrics.

All models are Pydantic v2 BaseModel subclasses with full type
annotations, validation, and documentation.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import UUID4, BaseModel, Field

from adip.knowledge.enums import (
    DocumentType,
    KnowledgeDomain,
    KnowledgeStatus,
    RetrievalType,
)

# ─────────────────────────────────────────────────────────────────────────────
# KnowledgeDocument
# ─────────────────────────────────────────────────────────────────────────────


class KnowledgeDocument(BaseModel):
    """A knowledge document ingested into the Knowledge Manager.

    Represents any supported document type (PDF, DOCX, TXT, etc.)
    with its metadata, content, and lifecycle tracking fields.
    """

    document_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique document identifier",
    )
    document_type: DocumentType = Field(
        description="The type of document (PDF, DOCX, etc.)",
    )
    domain: KnowledgeDomain = Field(
        default=KnowledgeDomain.SYSTEM,
        description="The knowledge domain this document belongs to",
    )
    title: str = Field(
        default="",
        description="Document title",
    )
    source: str = Field(
        default="",
        description="Original source identifier (file path, URL, etc.)",
    )
    content: str = Field(
        default="",
        description="Raw text content of the document",
    )
    status: KnowledgeStatus = Field(
        default=KnowledgeStatus.PENDING,
        description="Current processing status",
    )
    metadata: KnowledgeMetadata = Field(
        default_factory=lambda: KnowledgeMetadata(),
        description="Structured document metadata",
    )
    tags: list[str] = Field(
        default_factory=list,
        description="User-defined tags for classification",
    )
    owner_id: str = Field(
        default="",
        description="The user or system that owns this document",
    )
    namespace: str = Field(
        default="default",
        description="Logical namespace for multi-tenant isolation",
    )
    version: int = Field(
        default=1,
        ge=1,
        description="Document version number",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the document was created",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the document was last updated",
    )
    expires_at: datetime | None = Field(
        default=None,
        description="Optional expiration timestamp",
    )
    extra: dict[str, Any] = Field(
        default_factory=dict,
        description="Extensibility dictionary for arbitrary additional data",
    )


# ─────────────────────────────────────────────────────────────────────────────
# KnowledgeChunk
# ─────────────────────────────────────────────────────────────────────────────


class KnowledgeChunk(BaseModel):
    """A chunk (segment) of a knowledge document.

    Documents are split into chunks during processing for efficient
    embedding and retrieval. Each chunk retains a reference to its
    parent document and its position in the original sequence.
    """

    chunk_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique chunk identifier",
    )
    document_id: UUID4 = Field(
        description="The parent document this chunk belongs to",
    )
    document_type: DocumentType = Field(
        description="The type of the parent document",
    )
    domain: KnowledgeDomain = Field(
        default=KnowledgeDomain.SYSTEM,
        description="The knowledge domain inherited from the parent document",
    )
    content: str = Field(
        default="",
        description="The text content of this chunk",
    )
    chunk_index: int = Field(
        default=0,
        ge=0,
        description="Zero-based position within the parent document",
    )
    token_count: int = Field(
        default=0,
        ge=0,
        description="Approximate token count for this chunk",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Chunk-level metadata (e.g. page number, section heading)",
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Tags inherited or derived for this chunk",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the chunk was created",
    )


# ─────────────────────────────────────────────────────────────────────────────
# KnowledgeEmbedding
# ─────────────────────────────────────────────────────────────────────────────


class KnowledgeEmbedding(BaseModel):
    """Reference to an embedding vector for a knowledge chunk.

    This model does not store the actual vector data — it references
    an embedding that exists in an external vector store. The
    embedding_id and provider identify where and how the vector is
    stored.
    """

    embedding_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique embedding identifier",
    )
    chunk_id: UUID4 = Field(
        description="The chunk this embedding represents",
    )
    document_id: UUID4 = Field(
        description="The parent document of the chunk",
    )
    provider: str = Field(
        default="",
        description="The embedding provider (e.g. openai, huggingface)",
    )
    model: str = Field(
        default="",
        description="The embedding model name",
    )
    dimensions: int = Field(
        default=0,
        ge=0,
        description="The dimensionality of the embedding vector",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the embedding was created",
    )


# ─────────────────────────────────────────────────────────────────────────────
# KnowledgeMetadata
# ─────────────────────────────────────────────────────────────────────────────


class KnowledgeMetadata(BaseModel):
    """Structured metadata associated with a knowledge document.

    Captures bibliographic and provenance information that is
    independent of the document's text content.
    """

    author: str = Field(
        default="",
        description="Document author",
    )
    created_date: str = Field(
        default="",
        description="Document creation date (original source)",
    )
    last_modified: str = Field(
        default="",
        description="Document last modified date (original source)",
    )
    source_url: str = Field(
        default="",
        description="Original source URL if applicable",
    )
    file_size: int = Field(
        default=0,
        ge=0,
        description="File size in bytes",
    )
    page_count: int = Field(
        default=0,
        ge=0,
        description="Number of pages (for PDF and similar formats)",
    )
    language: str = Field(
        default="",
        description="Document language code (e.g. en, fr, de)",
    )
    extra: dict[str, Any] = Field(
        default_factory=dict,
        description="Extensibility dictionary for arbitrary additional metadata",
    )


# ─────────────────────────────────────────────────────────────────────────────
# KnowledgeProvenance
# ─────────────────────────────────────────────────────────────────────────────


class KnowledgeProvenance(BaseModel):
    """Provenance tracking for a knowledge document.

    Records the origin, processing history, and confidence of a
    knowledge document to support explainability and audit.
    """

    provenance_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique provenance identifier",
    )
    document_id: UUID4 = Field(
        description="The document this provenance record belongs to",
    )
    source_document: str = Field(
        default="",
        description="Original source document identifier",
    )
    source_type: str = Field(
        default="",
        description="Original source type (e.g. upload, api, webhook)",
    )
    imported_by: str = Field(
        default="",
        description="User or system that imported the document",
    )
    import_date: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the document was imported",
    )
    processing_pipeline: list[str] = Field(
        default_factory=list,
        description="List of processing stages applied",
    )
    version_used: int = Field(
        default=1,
        ge=1,
        description="Document version used during processing",
    )
    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Confidence score for the document content (0.0–1.0)",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional provenance metadata",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the provenance record was created",
    )


# ─────────────────────────────────────────────────────────────────────────────
# KnowledgeIndex
# ─────────────────────────────────────────────────────────────────────────────


class KnowledgeIndex(BaseModel):
    """An index entry tracking a document's indexing lifecycle.

    Records which documents and chunks have been indexed, by which
    provider, and the current status of the indexing operation.
    """

    index_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique index entry identifier",
    )
    document_id: UUID4 = Field(
        description="The document being indexed",
    )
    document_type: DocumentType = Field(
        description="The type of document being indexed",
    )
    domain: KnowledgeDomain = Field(
        default=KnowledgeDomain.SYSTEM,
        description="The knowledge domain of the document",
    )
    provider: str = Field(
        default="",
        description="The indexing provider (e.g. chroma, pinecone, qdrant)",
    )
    status: KnowledgeStatus = Field(
        default=KnowledgeStatus.PENDING,
        description="Current indexing status",
    )
    chunk_count: int = Field(
        default=0,
        ge=0,
        description="Number of chunks indexed",
    )
    error_message: str = Field(
        default="",
        description="Error details if indexing failed",
    )
    started_at: datetime | None = Field(
        default=None,
        description="When indexing started",
    )
    completed_at: datetime | None = Field(
        default=None,
        description="When indexing completed",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the index entry was created",
    )


# ─────────────────────────────────────────────────────────────────────────────
# KnowledgeQuery
# ─────────────────────────────────────────────────────────────────────────────


class KnowledgeQuery(BaseModel):
    """A query against the knowledge base.

    Encapsulates the query text, retrieval strategy, filters,
    pagination, and domain scoping for knowledge retrieval.
    """

    query_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique query identifier",
    )
    query_text: str = Field(
        default="",
        description="The natural language query text",
    )
    retrieval_type: RetrievalType = Field(
        default=RetrievalType.HYBRID,
        description="The retrieval strategy to use",
    )
    domains: list[KnowledgeDomain] = Field(
        default_factory=list,
        description="Restrict retrieval to specific knowledge domains",
    )
    document_types: list[DocumentType] = Field(
        default_factory=list,
        description="Restrict retrieval to specific document types",
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
        description="Maximum number of results to return",
    )
    offset: int = Field(
        default=0,
        ge=0,
        description="Number of results to skip (for pagination)",
    )
    min_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Minimum relevance score threshold (0.0–1.0)",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the query was created",
    )


# ─────────────────────────────────────────────────────────────────────────────
# KnowledgeResult
# ─────────────────────────────────────────────────────────────────────────────


class KnowledgeResult(BaseModel):
    """A single knowledge retrieval result.

    Contains the matched chunk, its parent document reference,
    relevance score, and any rank-related metadata.
    """

    result_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique result identifier",
    )
    query_id: UUID4 = Field(
        description="The query that produced this result",
    )
    chunk: KnowledgeChunk = Field(
        description="The matched chunk",
    )
    document: KnowledgeDocument | None = Field(
        default=None,
        description="The parent document (may be omitted for performance)",
    )
    score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Relevance score (0.0–1.0, higher is better)",
    )
    rank: int = Field(
        default=0,
        ge=0,
        description="Rank position in the result set (0 = most relevant)",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Result-level metadata (e.g. reranking details)",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the result was created",
    )


# ─────────────────────────────────────────────────────────────────────────────
# KnowledgeContext
# ─────────────────────────────────────────────────────────────────────────────


class KnowledgeContext(BaseModel):
    """Aggregated context assembled from knowledge retrieval.

    Combines all retrieved results into a coherent context that
    downstream consumers (Planner, Reasoning Engine, etc.) can
    consume directly.
    """

    context_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique context identifier",
    )
    query: KnowledgeQuery | None = Field(
        default=None,
        description="The original query that produced this context",
    )
    results: list[KnowledgeResult] = Field(
        default_factory=list,
        description="Ordered list of retrieval results",
    )
    total_results: int = Field(
        default=0,
        ge=0,
        description="Total number of matching results",
    )
    domains: list[KnowledgeDomain] = Field(
        default_factory=list,
        description="Knowledge domains covered by the results",
    )
    document_types: list[DocumentType] = Field(
        default_factory=list,
        description="Document types covered by the results",
    )
    token_count: int = Field(
        default=0,
        ge=0,
        description="Approximate total token count of all result chunks",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Context-level metadata (e.g. retrieval timing, provider info)",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the context was assembled",
    )


# ─────────────────────────────────────────────────────────────────────────────
# KnowledgeHealth
# ─────────────────────────────────────────────────────────────────────────────


class KnowledgeHealth(BaseModel):
    """Health status of the Knowledge Manager platform.

    Tracks overall and per-component health status for monitoring
    and observability. Includes version status, error rate, and
    knowledge domain coverage.
    """

    overall_status: str = Field(
        default="HEALTHY",
        description="Overall health: HEALTHY, DEGRADED, or UNHEALTHY",
    )
    coordinator_status: str = Field(
        default="HEALTHY",
        description="KnowledgeCoordinator health",
    )
    processor_status: str = Field(
        default="HEALTHY",
        description="DocumentProcessor health",
    )
    chunk_manager_status: str = Field(
        default="HEALTHY",
        description="ChunkManager health",
    )
    embedding_status: str = Field(
        default="HEALTHY",
        description="EmbeddingManager health",
    )
    index_status: str = Field(
        default="HEALTHY",
        description="IndexManager health",
    )
    retriever_status: str = Field(
        default="HEALTHY",
        description="Retriever health",
    )
    cache_status: str = Field(
        default="HEALTHY",
        description="KnowledgeCache health",
    )
    version_status: str = Field(
        default="HEALTHY",
        description="VersionManager health",
    )
    average_latency_ms: float = Field(
        default=0.0,
        ge=0.0,
        description="Average operation latency in milliseconds",
    )
    error_count: int = Field(
        default=0,
        ge=0,
        description="Total number of errors encountered",
    )
    error_rate: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Error rate as a fraction of total operations (0.0–1.0)",
    )
    total_documents: int = Field(
        default=0,
        ge=0,
        description="Total number of documents managed",
    )
    total_chunks: int = Field(
        default=0,
        ge=0,
        description="Total number of chunks indexed",
    )
    total_queries_served: int = Field(
        default=0,
        ge=0,
        description="Total number of queries served",
    )
    knowledge_domains: list[str] = Field(
        default_factory=list,
        description="List of knowledge domains with indexed documents",
    )
    last_checked_at: str = Field(
        default_factory=lambda: datetime.now(UTC).isoformat(),
        description="When the health check was last performed",
    )

    def is_healthy(self) -> bool:
        """Return True if overall status is HEALTHY."""
        return self.overall_status == "HEALTHY"


# ─────────────────────────────────────────────────────────────────────────────
# KnowledgeMetrics
# ─────────────────────────────────────────────────────────────────────────────


class KnowledgeMetrics(BaseModel):
    """Aggregated metrics snapshot for the Knowledge Manager.

    Provides a point-in-time view of key operational metrics for
    monitoring and observability. Includes strategy, version, and
    domain usage tracking.
    """

    documents_total: int = Field(
        default=0,
        ge=0,
        description="Total documents ingested",
    )
    chunks_total: int = Field(
        default=0,
        ge=0,
        description="Total chunks created",
    )
    embeddings_total: int = Field(
        default=0,
        ge=0,
        description="Total embeddings generated",
    )
    retrievals_total: int = Field(
        default=0,
        ge=0,
        description="Total retrieval operations",
    )
    indexed_total: int = Field(
        default=0,
        ge=0,
        description="Total documents successfully indexed",
    )
    failed_total: int = Field(
        default=0,
        ge=0,
        description="Total failed operations",
    )
    cache_hits: int = Field(
        default=0,
        ge=0,
        description="Total cache hits",
    )
    cache_misses: int = Field(
        default=0,
        ge=0,
        description="Total cache misses",
    )
    documents_per_domain: dict[str, int] = Field(
        default_factory=dict,
        description="Document count per knowledge domain",
    )
    documents_per_type: dict[str, int] = Field(
        default_factory=dict,
        description="Document count per document type",
    )
    average_indexing_time_ms: float = Field(
        default=0.0,
        ge=0.0,
        description="Average time to index a document in milliseconds",
    )
    average_retrieval_time_ms: float = Field(
        default=0.0,
        ge=0.0,
        description="Average time to retrieve results in milliseconds",
    )
    strategy_usage: dict[str, int] = Field(
        default_factory=dict,
        description="Usage count per retrieval strategy (e.g. HYBRID: 10, VECTOR: 5)",
    )
    domain_usage: dict[str, int] = Field(
        default_factory=dict,
        description="Usage count per knowledge domain for queries",
    )
    version_usage: dict[str, int] = Field(
        default_factory=dict,
        description="Usage count per document version",
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.now(UTC).isoformat(),
        description="When the metrics snapshot was taken",
    )


# ─────────────────────────────────────────────────────────────────────────────
# ExplainabilityMetadata
# ─────────────────────────────────────────────────────────────────────────────


class ExplainabilityMetadata(BaseModel):
    """Explainability metadata attached to each retrieval result.

    Preserves why each document was selected or rejected, which
    retrieval strategy was used, ranking rationale, version
    information, and provenance.
    """

    why_selected: str = Field(
        default="",
        description="Reason this result was selected (e.g. keyword match, vector similarity)",
    )
    why_rejected: str = Field(
        default="",
        description="Reason this result was rejected (if applicable)",
    )
    strategy_used: str = Field(
        default="",
        description="The retrieval strategy that produced this result",
    )
    ranking_reason: str = Field(
        default="",
        description="Rationale for the rank position",
    )
    version_selected: int = Field(
        default=1,
        ge=1,
        description="Document version used for this result",
    )
    provenance: str = Field(
        default="",
        description="Provenance summary (source, pipeline stages)",
    )


# ─────────────────────────────────────────────────────────────────────────────
# KnowledgeSession
# ─────────────────────────────────────────────────────────────────────────────


class KnowledgeSession(BaseModel):
    """A knowledge retrieval session.

    Tracks every request's lifecycle — who queried, what strategy
    was used, which documents/versions/chunks were accessed, cache
    interaction, and processing statistics.
    """

    session_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique session identifier",
    )
    query: str = Field(
        default="",
        description="The original query text",
    )
    user_id: str = Field(
        default="",
        description="The user or system that initiated the session",
    )
    correlation_id: str = Field(
        default="",
        description="Correlation ID for distributed tracing",
    )
    retrieval_strategy: str = Field(
        default="HYBRID",
        description="The retrieval strategy used",
    )
    documents_used: list[str] = Field(
        default_factory=list,
        description="Document IDs accessed during the session",
    )
    versions_used: list[int] = Field(
        default_factory=list,
        description="Document versions accessed",
    )
    chunks_used: list[str] = Field(
        default_factory=list,
        description="Chunk IDs accessed during the session",
    )
    cache_hits: int = Field(
        default=0,
        ge=0,
        description="Number of cache hits",
    )
    started_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the session started",
    )
    completed_at: datetime | None = Field(
        default=None,
        description="When the session completed",
    )
    duration_ms: float = Field(
        default=0.0,
        ge=0.0,
        description="Total session duration in milliseconds",
    )
    processing_statistics: dict[str, Any] = Field(
        default_factory=dict,
        description="Processing statistics (timing per stage, etc.)",
    )


# ─────────────────────────────────────────────────────────────────────────────
# KnowledgeDecision
# ─────────────────────────────────────────────────────────────────────────────


class KnowledgeDecision(BaseModel):
    """Records a retrieval decision for explainability and audit.

    Captures why documents were selected or rejected, which strategy
    was chosen, ranking rationale, and confidence. This model feeds
    Evidence Fusion, Reasoning, and Explainability engines.
    """

    retrieval_strategy: str = Field(
        default="",
        description="The retrieval strategy used (VECTOR, KEYWORD, METADATA, HYBRID)",
    )
    selected_documents: list[str] = Field(
        default_factory=list,
        description="Document IDs that were selected as relevant",
    )
    rejected_documents: list[str] = Field(
        default_factory=list,
        description="Document IDs that were considered and rejected",
    )
    selection_reason: str = Field(
        default="",
        description="Why the selected documents were chosen",
    )
    ranking_reason: str = Field(
        default="",
        description="How the selected documents were ranked",
    )
    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Confidence in the retrieval decision (0.0–1.0)",
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.now(UTC).isoformat(),
        description="When the decision was made",
    )


# ─────────────────────────────────────────────────────────────────────────────
# KnowledgeConfidence
# ─────────────────────────────────────────────────────────────────────────────


class KnowledgeConfidence(BaseModel):
    """Aggregated confidence and quality assessment for a retrieval.

    Produced by KnowledgeConfidenceCalculator from raw retrieval
    scores, metadata, version information, and provenance data.
    """

    overall_confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Overall confidence in the retrieval (0.0–1.0)",
    )
    quality_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Quality score based on source reliability (0.0–1.0)",
    )
    freshness_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Freshness score based on document age (0.0–1.0)",
    )
    completeness_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Completeness score based on coverage (0.0–1.0)",
    )

