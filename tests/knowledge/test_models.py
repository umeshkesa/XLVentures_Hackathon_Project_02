"""Tests for Knowledge Manager domain models."""

from __future__ import annotations

import uuid
from uuid import UUID

from adip.knowledge.contracts.models import (
    KnowledgeChunk,
    KnowledgeContext,
    KnowledgeDocument,
    KnowledgeEmbedding,
    KnowledgeHealth,
    KnowledgeIndex,
    KnowledgeMetadata,
    KnowledgeMetrics,
    KnowledgeQuery,
    KnowledgeResult,
)
from adip.knowledge.enums import (
    DocumentType,
    KnowledgeDomain,
    KnowledgeStatus,
    RetrievalType,
)

# ─────────────────────────────────────────────────────────────────────────────
# KnowledgeDocument
# ─────────────────────────────────────────────────────────────────────────────


class TestKnowledgeDocument:
    def test_minimal(self) -> None:
        doc = KnowledgeDocument(document_type=DocumentType.PDF)
        assert isinstance(doc.document_id, UUID)
        assert doc.document_type == DocumentType.PDF
        assert doc.domain == KnowledgeDomain.SYSTEM
        assert doc.status == KnowledgeStatus.PENDING
        assert doc.version == 1
        assert doc.tags == []
        assert doc.extra == {}

    def test_custom_values(self) -> None:
        doc = KnowledgeDocument(
            document_type=DocumentType.DOCX,
            domain=KnowledgeDomain.ENERGY,
            title="Safety Report",
            source="/path/to/report.docx",
            content="Full text content...",
            tags=["safety", "energy"],
            owner_id="user-42",
            namespace="acme",
        )
        assert doc.domain == KnowledgeDomain.ENERGY
        assert doc.title == "Safety Report"
        assert doc.source == "/path/to/report.docx"
        assert doc.content == "Full text content..."
        assert "safety" in doc.tags
        assert doc.owner_id == "user-42"
        assert doc.namespace == "acme"

    def test_document_id_is_uuid(self) -> None:
        doc = KnowledgeDocument(document_type=DocumentType.PDF)
        assert isinstance(doc.document_id, UUID)

    def test_default_metadata(self) -> None:
        doc = KnowledgeDocument(document_type=DocumentType.PDF)
        assert doc.metadata.author == ""
        assert doc.metadata.file_size == 0

    def test_status_default_pending(self) -> None:
        doc = KnowledgeDocument(document_type=DocumentType.PDF)
        assert doc.status == KnowledgeStatus.PENDING

    def test_version_default_one(self) -> None:
        doc = KnowledgeDocument(document_type=DocumentType.PDF)
        assert doc.version == 1

    def test_serialization(self) -> None:
        doc = KnowledgeDocument(document_type=DocumentType.PDF, domain=KnowledgeDomain.SAFETY)
        data = doc.model_dump()
        assert data["document_type"] == "PDF"
        assert data["domain"] == "SAFETY"
        assert data["status"] == "PENDING"


# ─────────────────────────────────────────────────────────────────────────────
# KnowledgeChunk
# ─────────────────────────────────────────────────────────────────────────────


class TestKnowledgeChunk:
    def test_minimal(self) -> None:
        chunk = KnowledgeChunk(
            document_id=uuid.uuid4(),
            document_type=DocumentType.PDF,
        )
        assert isinstance(chunk.chunk_id, UUID)
        assert chunk.chunk_index == 0
        assert chunk.token_count == 0
        assert chunk.content == ""
        assert chunk.metadata == {}

    def test_custom_values(self) -> None:
        chunk = KnowledgeChunk(
            document_id=uuid.uuid4(),
            document_type=DocumentType.ARTICLE,
            content="Chunk content here",
            chunk_index=3,
            token_count=150,
            domain=KnowledgeDomain.COMPLIANCE,
            metadata={"page": 5, "section": "intro"},
        )
        assert chunk.content == "Chunk content here"
        assert chunk.chunk_index == 3
        assert chunk.token_count == 150
        assert chunk.domain == KnowledgeDomain.COMPLIANCE
        assert chunk.metadata["page"] == 5


# ─────────────────────────────────────────────────────────────────────────────
# KnowledgeEmbedding
# ─────────────────────────────────────────────────────────────────────────────


class TestKnowledgeEmbedding:
    def test_minimal(self) -> None:
        emb = KnowledgeEmbedding(
            chunk_id=uuid.uuid4(),
            document_id=uuid.uuid4(),
        )
        assert isinstance(emb.embedding_id, UUID)
        assert emb.provider == ""
        assert emb.model == ""
        assert emb.dimensions == 0

    def test_custom_values(self) -> None:
        emb = KnowledgeEmbedding(
            chunk_id=uuid.uuid4(),
            document_id=uuid.uuid4(),
            provider="openai",
            model="text-embedding-3-small",
            dimensions=1536,
        )
        assert emb.provider == "openai"
        assert emb.model == "text-embedding-3-small"
        assert emb.dimensions == 1536


# ─────────────────────────────────────────────────────────────────────────────
# KnowledgeMetadata
# ─────────────────────────────────────────────────────────────────────────────


class TestKnowledgeMetadata:
    def test_defaults(self) -> None:
        meta = KnowledgeMetadata()
        assert meta.author == ""
        assert meta.created_date == ""
        assert meta.last_modified == ""
        assert meta.source_url == ""
        assert meta.file_size == 0
        assert meta.page_count == 0
        assert meta.language == ""
        assert meta.extra == {}

    def test_custom_values(self) -> None:
        meta = KnowledgeMetadata(
            author="John Doe",
            file_size=1024000,
            page_count=42,
            language="en",
            extra={"publisher": "Acme Corp"},
        )
        assert meta.author == "John Doe"
        assert meta.file_size == 1024000
        assert meta.page_count == 42
        assert meta.language == "en"
        assert meta.extra["publisher"] == "Acme Corp"

    def test_serialization(self) -> None:
        meta = KnowledgeMetadata(author="Jane", language="fr")
        data = meta.model_dump()
        assert data["author"] == "Jane"
        assert data["language"] == "fr"


# ─────────────────────────────────────────────────────────────────────────────
# KnowledgeIndex
# ─────────────────────────────────────────────────────────────────────────────


class TestKnowledgeIndex:
    def test_minimal(self) -> None:
        idx = KnowledgeIndex(
            document_id=uuid.uuid4(),
            document_type=DocumentType.PDF,
        )
        assert isinstance(idx.index_id, UUID)
        assert idx.status == KnowledgeStatus.PENDING
        assert idx.chunk_count == 0
        assert idx.error_message == ""

    def test_custom_values(self) -> None:
        idx = KnowledgeIndex(
            document_id=uuid.uuid4(),
            document_type=DocumentType.PDF,
            provider="chroma",
            status=KnowledgeStatus.INDEXED,
            chunk_count=25,
            domain=KnowledgeDomain.MAINTENANCE,
        )
        assert idx.provider == "chroma"
        assert idx.status == KnowledgeStatus.INDEXED
        assert idx.chunk_count == 25
        assert idx.domain == KnowledgeDomain.MAINTENANCE


# ─────────────────────────────────────────────────────────────────────────────
# KnowledgeQuery
# ─────────────────────────────────────────────────────────────────────────────


class TestKnowledgeQuery:
    def test_minimal(self) -> None:
        q = KnowledgeQuery()
        assert isinstance(q.query_id, UUID)
        assert q.query_text == ""
        assert q.retrieval_type == RetrievalType.HYBRID
        assert q.limit == 10
        assert q.offset == 0
        assert q.min_score == 0.0
        assert q.domains == []
        assert q.document_types == []

    def test_custom_values(self) -> None:
        q = KnowledgeQuery(
            query_text="What are the safety protocols?",
            retrieval_type=RetrievalType.VECTOR,
            domains=[KnowledgeDomain.SAFETY, KnowledgeDomain.COMPLIANCE],
            limit=5,
            min_score=0.7,
        )
        assert q.query_text == "What are the safety protocols?"
        assert q.retrieval_type == RetrievalType.VECTOR
        assert KnowledgeDomain.SAFETY in q.domains
        assert q.limit == 5
        assert q.min_score == 0.7

    def test_limit_bounds(self) -> None:
        q = KnowledgeQuery(limit=1)
        assert q.limit == 1
        q = KnowledgeQuery(limit=100)
        assert q.limit == 100

    def test_pagination_defaults(self) -> None:
        q = KnowledgeQuery()
        assert q.offset == 0
        assert q.limit == 10


# ─────────────────────────────────────────────────────────────────────────────
# KnowledgeResult
# ─────────────────────────────────────────────────────────────────────────────


class TestKnowledgeResult:
    def test_minimal(self) -> None:
        chunk = KnowledgeChunk(
            document_id=uuid.uuid4(),
            document_type=DocumentType.PDF,
        )
        result = KnowledgeResult(
            query_id=uuid.uuid4(),
            chunk=chunk,
        )
        assert isinstance(result.result_id, UUID)
        assert result.score == 0.0
        assert result.rank == 0
        assert result.document is None
        assert result.metadata == {}

    def test_custom_values(self) -> None:
        chunk = KnowledgeChunk(
            document_id=uuid.uuid4(),
            document_type=DocumentType.PDF,
            content="Test chunk",
        )
        result = KnowledgeResult(
            query_id=uuid.uuid4(),
            chunk=chunk,
            score=0.95,
            rank=1,
            metadata={"reranker": "cross-encoder"},
        )
        assert result.score == 0.95
        assert result.rank == 1
        assert result.metadata["reranker"] == "cross-encoder"


# ─────────────────────────────────────────────────────────────────────────────
# KnowledgeContext
# ─────────────────────────────────────────────────────────────────────────────


class TestKnowledgeContext:
    def test_minimal(self) -> None:
        ctx = KnowledgeContext()
        assert isinstance(ctx.context_id, UUID)
        assert ctx.results == []
        assert ctx.total_results == 0
        assert ctx.domains == []
        assert ctx.document_types == []
        assert ctx.token_count == 0
        assert ctx.query is None

    def test_with_results(self) -> None:
        chunk = KnowledgeChunk(
            document_id=uuid.uuid4(),
            document_type=DocumentType.ARTICLE,
        )
        result = KnowledgeResult(
            query_id=uuid.uuid4(),
            chunk=chunk,
            score=0.85,
        )
        ctx = KnowledgeContext(
            results=[result],
            total_results=1,
            domains=[KnowledgeDomain.SAFETY],
            document_types=[DocumentType.ARTICLE],
            token_count=500,
        )
        assert len(ctx.results) == 1
        assert ctx.results[0].score == 0.85
        assert ctx.total_results == 1
        assert KnowledgeDomain.SAFETY in ctx.domains
        assert ctx.token_count == 500


# ─────────────────────────────────────────────────────────────────────────────
# KnowledgeHealth
# ─────────────────────────────────────────────────────────────────────────────


class TestKnowledgeHealth:
    def test_default_healthy(self) -> None:
        health = KnowledgeHealth()
        assert health.overall_status == "HEALTHY"
        assert health.coordinator_status == "HEALTHY"
        assert health.processor_status == "HEALTHY"
        assert health.chunk_manager_status == "HEALTHY"
        assert health.embedding_status == "HEALTHY"
        assert health.index_status == "HEALTHY"
        assert health.retriever_status == "HEALTHY"
        assert health.cache_status == "HEALTHY"
        assert health.is_healthy() is True

    def test_is_healthy_true(self) -> None:
        health = KnowledgeHealth()
        assert health.is_healthy() is True

    def test_is_healthy_false(self) -> None:
        health = KnowledgeHealth(overall_status="UNHEALTHY")
        assert health.is_healthy() is False

    def test_custom_values(self) -> None:
        health = KnowledgeHealth(
            overall_status="DEGRADED",
            error_count=3,
            average_latency_ms=250.0,
            total_documents=1000,
            total_chunks=5000,
        )
        assert health.overall_status == "DEGRADED"
        assert health.error_count == 3
        assert health.average_latency_ms == 250.0
        assert health.total_documents == 1000
        assert health.total_chunks == 5000

    def test_serialization(self) -> None:
        health = KnowledgeHealth(overall_status="HEALTHY")
        data = health.model_dump()
        assert data["overall_status"] == "HEALTHY"
        assert data["total_documents"] == 0


# ─────────────────────────────────────────────────────────────────────────────
# KnowledgeMetrics
# ─────────────────────────────────────────────────────────────────────────────


class TestKnowledgeMetrics:
    def test_defaults(self) -> None:
        metrics = KnowledgeMetrics()
        assert metrics.documents_total == 0
        assert metrics.chunks_total == 0
        assert metrics.embeddings_total == 0
        assert metrics.retrievals_total == 0
        assert metrics.indexed_total == 0
        assert metrics.failed_total == 0
        assert metrics.cache_hits == 0
        assert metrics.cache_misses == 0
        assert metrics.documents_per_domain == {}
        assert metrics.documents_per_type == {}
        assert metrics.average_indexing_time_ms == 0.0
        assert metrics.average_retrieval_time_ms == 0.0

    def test_custom_values(self) -> None:
        metrics = KnowledgeMetrics(
            documents_total=500,
            chunks_total=10000,
            embeddings_total=10000,
            retrievals_total=2500,
            indexed_total=450,
            failed_total=5,
            cache_hits=800,
            cache_misses=200,
            documents_per_domain={"SAFETY": 100, "ENERGY": 200},
            documents_per_type={"PDF": 300, "DOCX": 150},
            average_indexing_time_ms=1200.5,
            average_retrieval_time_ms=45.2,
        )
        assert metrics.documents_total == 500
        assert metrics.chunks_total == 10000
        assert metrics.cache_hits == 800
        assert metrics.documents_per_domain["SAFETY"] == 100
        assert metrics.average_indexing_time_ms == 1200.5

    def test_serialization(self) -> None:
        metrics = KnowledgeMetrics(documents_total=42)
        data = metrics.model_dump()
        assert data["documents_total"] == 42
