"""Abstract interfaces for the Knowledge Manager.

All interfaces follow dependency inversion — consumers depend on
abstractions, not concrete implementations.

Architecture:
    KnowledgeService  →  KnowledgeManager  →  KnowledgeCoordinator
                                                      ├── DocumentProcessor
                                                      ├── ChunkManager
                                                      ├── EmbeddingManager
                                                      ├── IndexManager
                                                      ├── Retriever
                                                      ├── Reranker
                                                      ├── ContextBuilder
                                                      └── KnowledgeCache

KnowledgeService is the enterprise facade for external callers.
KnowledgeManager is the internal orchestrator.
KnowledgeCoordinator coordinates all sub-components.
"""

from __future__ import annotations

import abc

from adip.knowledge.contracts.models import (
    KnowledgeChunk,
    KnowledgeContext,
    KnowledgeDocument,
    KnowledgeHealth,
    KnowledgeMetrics,
    KnowledgeQuery,
    KnowledgeResult,
)
from adip.knowledge.enums import (
    DocumentType,
    KnowledgeDomain,
    RetrievalType,
)

# ─────────────────────────────────────────────────────────────────────────────
# KnowledgeService — enterprise facade (ONLY public API)
# ─────────────────────────────────────────────────────────────────────────────


class KnowledgeService(abc.ABC):
    """Enterprise facade for knowledge operations.

    Provides validation, authorisation, audit, and observability
    wrapping around the KnowledgeManager. External modules interact
    with this facade rather than with KnowledgeManager directly.
    """

    @abc.abstractmethod
    async def ingest(self, document: KnowledgeDocument) -> KnowledgeDocument:
        """Validate, authorise, and ingest a knowledge document."""
        ...

    @abc.abstractmethod
    async def retrieve(self, query: KnowledgeQuery) -> KnowledgeContext:
        """Retrieve knowledge matching the given query with authorisation."""
        ...

    @abc.abstractmethod
    async def get_document(self, document_id: str) -> KnowledgeDocument | None:
        """Retrieve a single document by its identifier."""
        ...

    @abc.abstractmethod
    async def update_document(self, document: KnowledgeDocument) -> KnowledgeDocument:
        """Update an existing knowledge document."""
        ...

    @abc.abstractmethod
    async def delete_document(self, document_id: str) -> bool:
        """Delete a knowledge document with authorisation and audit."""
        ...

    @abc.abstractmethod
    async def archive_document(self, document_id: str, reason: str = "") -> bool:
        """Archive a knowledge document."""
        ...

    @abc.abstractmethod
    async def search_documents(
        self,
        query: str = "",
        domain: KnowledgeDomain | None = None,
        document_type: DocumentType | None = None,
        tags: list[str] | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[KnowledgeDocument]:
        """Search for documents matching the given filters."""
        ...

    @abc.abstractmethod
    async def health(self) -> KnowledgeHealth:
        """Return the current health status of the knowledge platform."""
        ...

    @abc.abstractmethod
    async def get_metrics(self) -> KnowledgeMetrics:
        """Return aggregated knowledge platform metrics."""
        ...


# ─────────────────────────────────────────────────────────────────────────────
# KnowledgeManager — internal orchestrator
# ─────────────────────────────────────────────────────────────────────────────


class KnowledgeManager(abc.ABC):
    """Internal orchestrator for all knowledge operations.

    Every ADIP module that needs knowledge operations goes through
    this interface. The KnowledgeManager:
      1. Validates the operation
      2. Delegates to KnowledgeCoordinator for orchestration
      3. Records events for audit and observability
    """

    @abc.abstractmethod
    async def create_document(self, document: KnowledgeDocument) -> KnowledgeDocument:
        """Store a new knowledge document."""
        ...

    @abc.abstractmethod
    async def read_document(self, document_id: str) -> KnowledgeDocument | None:
        """Retrieve a knowledge document by ID."""
        ...

    @abc.abstractmethod
    async def update_document(self, document: KnowledgeDocument) -> KnowledgeDocument:
        """Update an existing knowledge document."""
        ...

    @abc.abstractmethod
    async def delete_document(self, document_id: str) -> bool:
        """Delete a knowledge document."""
        ...

    @abc.abstractmethod
    async def search_documents(
        self,
        query: str = "",
        domain: KnowledgeDomain | None = None,
        document_type: DocumentType | None = None,
        tags: list[str] | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[KnowledgeDocument]:
        """Search for documents matching the given filters."""
        ...

    @abc.abstractmethod
    async def retrieve_knowledge(self, query: KnowledgeQuery) -> KnowledgeContext:
        """Retrieve knowledge matching the given query."""
        ...

    @abc.abstractmethod
    async def get_health(self) -> KnowledgeHealth:
        """Return the current health status."""
        ...

    @abc.abstractmethod
    async def get_metrics(self) -> KnowledgeMetrics:
        """Return aggregated metrics."""
        ...


# ─────────────────────────────────────────────────────────────────────────────
# KnowledgeCoordinator — sub-component orchestrator
# ─────────────────────────────────────────────────────────────────────────────


class KnowledgeCoordinator(abc.ABC):
    """Sub-component orchestrator for knowledge operations.

    Coordinates DocumentProcessor, ChunkManager, EmbeddingManager,
    IndexManager, Retriever, Reranker, ContextBuilder, and
    KnowledgeCache. Contains orchestration only — no business logic.
    """

    @abc.abstractmethod
    async def process_document(self, document: KnowledgeDocument) -> KnowledgeDocument:
        """Orchestrate the full document processing pipeline."""
        ...

    @abc.abstractmethod
    async def retrieve(self, query: KnowledgeQuery) -> KnowledgeContext:
        """Orchestrate retrieval across all sub-components."""
        ...

    @abc.abstractmethod
    async def get_document(self, document_id: str) -> KnowledgeDocument | None:
        """Retrieve a document by ID."""
        ...

    @abc.abstractmethod
    async def delete_document(self, document_id: str) -> bool:
        """Delete a document and its associated data."""
        ...

    @abc.abstractmethod
    async def archive_document(self, document_id: str) -> bool:
        """Archive a document."""
        ...

    @abc.abstractmethod
    async def health(self) -> KnowledgeHealth:
        """Return health status of all sub-components."""
        ...

    @abc.abstractmethod
    async def metrics(self) -> KnowledgeMetrics:
        """Return aggregated metrics from all sub-components."""
        ...


# ─────────────────────────────────────────────────────────────────────────────
# DocumentProcessor
# ─────────────────────────────────────────────────────────────────────────────


class DocumentProcessor(abc.ABC):
    """Processes raw documents for downstream consumption.

    Handles document parsing, content extraction, format conversion,
    and initial validation before chunking and embedding.
    """

    @abc.abstractmethod
    async def process(self, document: KnowledgeDocument) -> KnowledgeDocument:
        """Parse and extract content from a raw document."""
        ...

    @abc.abstractmethod
    async def validate(self, document: KnowledgeDocument) -> list[str]:
        """Validate a document before processing. Returns list of violations."""
        ...

    @abc.abstractmethod
    async def get_supported_types(self) -> list[DocumentType]:
        """Return the document types this processor supports."""
        ...


# ─────────────────────────────────────────────────────────────────────────────
# ChunkManager
# ─────────────────────────────────────────────────────────────────────────────


class ChunkManager(abc.ABC):
    """Splits documents into chunks for embedding and retrieval.

    Implements chunking strategies (fixed-size, semantic, recursive)
    and manages chunk-level metadata.
    """

    @abc.abstractmethod
    async def chunk_document(self, document: KnowledgeDocument) -> list[KnowledgeChunk]:
        """Split a processed document into chunks."""
        ...

    @abc.abstractmethod
    async def get_chunks(self, document_id: str) -> list[KnowledgeChunk]:
        """Retrieve all chunks for a given document."""
        ...

    @abc.abstractmethod
    async def delete_chunks(self, document_id: str) -> bool:
        """Delete all chunks for a given document."""
        ...


# ─────────────────────────────────────────────────────────────────────────────
# EmbeddingManager
# ─────────────────────────────────────────────────────────────────────────────


class EmbeddingManager(abc.ABC):
    """Generates and manages embeddings for knowledge chunks.

    Abstracts over embedding providers (OpenAI, HuggingFace, etc.)
    so the Knowledge Manager remains provider-independent.
    """

    @abc.abstractmethod
    async def embed(self, chunk: KnowledgeChunk) -> KnowledgeChunk:
        """Generate an embedding for a single chunk."""
        ...

    @abc.abstractmethod
    async def embed_batch(self, chunks: list[KnowledgeChunk]) -> list[KnowledgeChunk]:
        """Generate embeddings for a batch of chunks."""
        ...

    @abc.abstractmethod
    async def get_embedding_dimensions(self) -> int:
        """Return the dimensionality of generated embeddings."""
        ...


# ─────────────────────────────────────────────────────────────────────────────
# IndexManager
# ─────────────────────────────────────────────────────────────────────────────


class IndexManager(abc.ABC):
    """Manages the indexing of document chunks into vector storage.

    Handles index creation, update, deletion, and status tracking
    across supported vector store providers.
    """

    @abc.abstractmethod
    async def index_document(self, document: KnowledgeDocument, chunks: list[KnowledgeChunk]) -> bool:
        """Index all chunks for a document."""
        ...

    @abc.abstractmethod
    async def delete_index(self, document_id: str) -> bool:
        """Remove a document's entries from the index."""
        ...

    @abc.abstractmethod
    async def get_index_status(self, document_id: str) -> str:
        """Return the indexing status for a document."""
        ...


# ─────────────────────────────────────────────────────────────────────────────
# Retriever
# ─────────────────────────────────────────────────────────────────────────────


class Retriever(abc.ABC):
    """Retrieves knowledge chunks matching a query.

    Supports multiple retrieval strategies: vector, keyword,
    metadata, and hybrid.
    """

    @abc.abstractmethod
    async def retrieve(
        self,
        query: KnowledgeQuery,
    ) -> list[KnowledgeResult]:
        """Retrieve knowledge chunks matching the query."""
        ...

    @abc.abstractmethod
    def get_supported_retrieval_types(self) -> list[RetrievalType]:
        """Return the retrieval types this retriever supports."""
        ...


# ─────────────────────────────────────────────────────────────────────────────
# Reranker
# ─────────────────────────────────────────────────────────────────────────────


class Reranker(abc.ABC):
    """Reranks retrieved results to improve relevance ordering.

    Applied after initial retrieval to refine result ordering
    using cross-encoders, business rules, or other strategies.
    """

    @abc.abstractmethod
    async def rerank(
        self,
        query: KnowledgeQuery,
        results: list[KnowledgeResult],
    ) -> list[KnowledgeResult]:
        """Rerank a list of retrieval results by relevance."""
        ...


# ─────────────────────────────────────────────────────────────────────────────
# ContextBuilder
# ─────────────────────────────────────────────────────────────────────────────


class ContextBuilder(abc.ABC):
    """Assembles retrieval results into a structured KnowledgeContext.

    Aggregates, deduplicates, and formats results into a context
    object ready for consumption by downstream ADIP components.
    """

    @abc.abstractmethod
    async def build_context(
        self,
        query: KnowledgeQuery,
        results: list[KnowledgeResult],
    ) -> KnowledgeContext:
        """Build a KnowledgeContext from retrieval results."""
        ...


# ─────────────────────────────────────────────────────────────────────────────
# KnowledgeCache
# ─────────────────────────────────────────────────────────────────────────────


class KnowledgeCache(abc.ABC):
    """Cache layer for knowledge retrieval results.

    Caches query results to reduce latency for repeated or
    similar queries.
    """

    @abc.abstractmethod
    async def get(self, cache_key: str) -> KnowledgeContext | None:
        """Retrieve a cached KnowledgeContext by key."""
        ...

    @abc.abstractmethod
    async def set(self, cache_key: str, context: KnowledgeContext, ttl_seconds: int = 300) -> None:
        """Cache a KnowledgeContext with an optional TTL."""
        ...

    @abc.abstractmethod
    async def invalidate(self, cache_key: str) -> bool:
        """Invalidate a single cache entry."""
        ...

    @abc.abstractmethod
    async def clear(self) -> int:
        """Clear all cache entries. Returns the number cleared."""
        ...
