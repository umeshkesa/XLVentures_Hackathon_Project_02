"""Tests for Knowledge Manager Phase 2 execution components."""

from __future__ import annotations

import uuid

import pytest

from adip.knowledge.contracts.models import (
    KnowledgeChunk,
    KnowledgeContext,
    KnowledgeDocument,
    KnowledgeMetadata,
    KnowledgeQuery,
    KnowledgeResult,
)
from adip.knowledge.enums import (
    DocumentType,
    KnowledgeDomain,
    KnowledgeLifecycleStatus,
    RetrievalType,
)
from adip.knowledge.execution.cache import KnowledgeCache
from adip.knowledge.execution.chunk_manager import ChunkManager
from adip.knowledge.execution.classifier import DocumentClassifier
from adip.knowledge.execution.cleaner import DocumentCleaner
from adip.knowledge.execution.context_builder import ContextBuilder
from adip.knowledge.execution.embedding_manager import EmbeddingManager
from adip.knowledge.execution.fusion import ResultFusion
from adip.knowledge.execution.index_manager import IndexManager
from adip.knowledge.execution.lifecycle import KnowledgeLifecycleManager
from adip.knowledge.execution.metadata_extractor import MetadataExtractor
from adip.knowledge.execution.metrics import KnowledgeMetricsCollector
from adip.knowledge.execution.ocr import OCRProcessor
from adip.knowledge.execution.policy import KnowledgePolicyEngine
from adip.knowledge.execution.provenance import KnowledgeProvenanceManager
from adip.knowledge.execution.query_analyzer import QueryAnalyzer
from adip.knowledge.execution.query_rewriter import QueryRewriter
from adip.knowledge.execution.reranker import Reranker
from adip.knowledge.execution.retriever import HybridRetriever
from adip.knowledge.execution.trace import KnowledgeTrace
from adip.knowledge.execution.validator import DocumentValidator
from adip.knowledge.execution.version_manager import KnowledgeVersionManager

# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────


@pytest.fixture
def sample_document() -> KnowledgeDocument:
    return KnowledgeDocument(
        document_id=uuid.uuid4(),
        document_type=DocumentType.PDF,
        domain=KnowledgeDomain.SAFETY,
        title="Safety Manual 2024",
        content="This is the safety manual content for 2024.",
        source="/path/to/safety_manual.pdf",
        owner_id="user-42",
        namespace="acme",
        tags=["safety", "manual"],
        metadata=KnowledgeMetadata(author="John Doe", file_size=1024),
        version=1,
    )


@pytest.fixture
def sample_chunks() -> list[KnowledgeChunk]:
    doc_id = uuid.uuid4()
    return [
        KnowledgeChunk(
            document_id=doc_id,
            document_type=DocumentType.PDF,
            content="Chunk one content about safety procedures.",
            chunk_index=0,
            domain=KnowledgeDomain.SAFETY,
        ),
        KnowledgeChunk(
            document_id=doc_id,
            document_type=DocumentType.PDF,
            content="Chunk two content about compliance rules.",
            chunk_index=1,
            domain=KnowledgeDomain.COMPLIANCE,
        ),
    ]


@pytest.fixture
def sample_query() -> KnowledgeQuery:
    return KnowledgeQuery(
        query_text="safety procedures",
        domains=[KnowledgeDomain.SAFETY],
        limit=10,
        retrieval_type=RetrievalType.HYBRID,
    )


# ─────────────────────────────────────────────────────────────────────────────
# DocumentValidator
# ─────────────────────────────────────────────────────────────────────────────


class TestDocumentValidator:
    def test_validate_valid(self, sample_document: KnowledgeDocument) -> None:
        validator = DocumentValidator()
        violations = validator.validate(sample_document)
        assert violations == []

    def test_validate_empty_content(self) -> None:
        validator = DocumentValidator()
        doc = KnowledgeDocument(document_type=DocumentType.PDF, content="", title="t", namespace="ns")
        violations = validator.validate(doc)
        assert any("content" in v.lower() for v in violations)

    def test_validate_empty_title(self) -> None:
        validator = DocumentValidator()
        doc = KnowledgeDocument(document_type=DocumentType.PDF, title="", content="c", namespace="ns")
        violations = validator.validate(doc)
        assert any("title" in v.lower() for v in violations)


# ─────────────────────────────────────────────────────────────────────────────
# DocumentClassifier
# ─────────────────────────────────────────────────────────────────────────────


class TestDocumentClassifier:
    def test_classify_by_type(self) -> None:
        classifier = DocumentClassifier()
        doc = KnowledgeDocument(document_type=DocumentType.MANUAL, content="Safety manual content.")
        result = classifier.classify(doc)
        assert result == "Manual"

    def test_classify_fallback(self) -> None:
        classifier = DocumentClassifier()
        doc = KnowledgeDocument(document_type=DocumentType.CSV, content="Generic content.")
        result = classifier.classify(doc)
        assert result == "Report"


# ─────────────────────────────────────────────────────────────────────────────
# MetadataExtractor
# ─────────────────────────────────────────────────────────────────────────────


class TestMetadataExtractor:
    def test_extract_standard(self, sample_document: KnowledgeDocument) -> None:
        extractor = MetadataExtractor()
        result = extractor.extract(sample_document)
        assert result["author"] == "extracted-author"
        assert result["file_size"] == sample_document.metadata.file_size
        assert result["title"] == sample_document.title
        assert result["source"] == sample_document.source

    def test_extract_minimal_document(self) -> None:
        extractor = MetadataExtractor()
        doc = KnowledgeDocument(document_type=DocumentType.PDF)
        result = extractor.extract(doc)
        assert result is not None
        assert "author" in result


# ─────────────────────────────────────────────────────────────────────────────
# DocumentCleaner
# ─────────────────────────────────────────────────────────────────────────────


class TestDocumentCleaner:
    def test_clean_string(self) -> None:
        cleaner = DocumentCleaner()
        result = cleaner.clean("  Hello world!\n\n")
        assert result.startswith("Hello")
        assert result == "Hello world!"

    def test_clean_document(self) -> None:
        cleaner = DocumentCleaner()
        doc = KnowledgeDocument(
            document_type=DocumentType.TXT,
            content="  Dirty content.  \n\n",
        )
        result = cleaner.clean_document(doc)
        assert result.content.startswith("Dirty")
        assert "  " not in result.content

    def test_clean_document_empty(self) -> None:
        cleaner = DocumentCleaner()
        doc = KnowledgeDocument(document_type=DocumentType.TXT, content="")
        result = cleaner.clean_document(doc)
        assert result.content == ""


# ─────────────────────────────────────────────────────────────────────────────
# OCRProcessor
# ─────────────────────────────────────────────────────────────────────────────


class TestOCRProcessor:
    def test_process_placeholder(self) -> None:
        processor = OCRProcessor()
        doc = KnowledgeDocument(
            document_type=DocumentType.PDF,
            content="Some PDF content",
        )
        result = processor.process(doc)
        assert result == doc  # placeholder returns unchanged

    def test_is_supported_pdf(self) -> None:
        processor = OCRProcessor()
        assert processor.is_supported(DocumentType.PDF) is True

    def test_is_supported_txt(self) -> None:
        processor = OCRProcessor()
        assert processor.is_supported(DocumentType.TXT) is False


# ─────────────────────────────────────────────────────────────────────────────
# ChunkManager
# ─────────────────────────────────────────────────────────────────────────────


class TestChunkManager:
    def test_chunk_document_fixed(self, sample_document: KnowledgeDocument) -> None:
        manager = ChunkManager()
        chunks = manager.chunk_document(sample_document, strategy="fixed", chunk_size=50)
        assert len(chunks) > 0
        all_same = all(c.document_id == sample_document.document_id for c in chunks)
        assert all_same

    def test_chunk_document_paragraph(self) -> None:
        manager = ChunkManager()
        doc = KnowledgeDocument(
            document_type=DocumentType.TXT,
            content="First paragraph.\n\nSecond paragraph.\n\nThird paragraph.",
        )
        chunks = manager.chunk_document(doc, strategy="paragraph")
        assert len(chunks) == 3

    def test_chunk_document_empty_content(self) -> None:
        manager = ChunkManager()
        doc = KnowledgeDocument(document_type=DocumentType.PDF, content="")
        chunks = manager.chunk_document(doc)
        assert len(chunks) == 0

    def test_chunk_document_default_strategy(self, sample_document: KnowledgeDocument) -> None:
        manager = ChunkManager()
        chunks = manager.chunk_document(sample_document)
        assert len(chunks) > 0


# ─────────────────────────────────────────────────────────────────────────────
# EmbeddingManager
# ─────────────────────────────────────────────────────────────────────────────


class TestEmbeddingManager:
    def test_embed_single(self, sample_chunks: list[KnowledgeChunk]) -> None:
        manager = EmbeddingManager()
        emb = manager.embed(sample_chunks[0])
        assert emb.provider == "placeholder"
        assert emb.dimensions == 768
        assert emb.chunk_id == sample_chunks[0].chunk_id

    def test_embed_batch(self, sample_chunks: list[KnowledgeChunk]) -> None:
        manager = EmbeddingManager()
        embeddings = manager.embed_batch(sample_chunks)
        assert len(embeddings) == len(sample_chunks)
        for emb in embeddings:
            assert emb.provider == "placeholder"

    def test_embed_batch_empty(self) -> None:
        manager = EmbeddingManager()
        embeddings = manager.embed_batch([])
        assert embeddings == []

    def test_get_embedding_dimensions(self) -> None:
        manager = EmbeddingManager()
        assert manager.get_embedding_dimensions() == 768


# ─────────────────────────────────────────────────────────────────────────────
# IndexManager
# ─────────────────────────────────────────────────────────────────────────────


class TestIndexManager:
    def test_index_and_search_vector(self) -> None:
        manager = IndexManager()
        doc = KnowledgeDocument(
            document_type=DocumentType.PDF, domain=KnowledgeDomain.SAFETY,
            title="Safety", content="safety procedure content", namespace="ns",
        )
        chunk = KnowledgeChunk(document_id=doc.document_id, document_type=DocumentType.PDF,
                               content="safety procedure content")
        manager.index_document(doc, [chunk])
        results = manager.search_vector("safety", limit=10)
        assert str(doc.document_id) in results

    def test_index_and_search_keyword(self) -> None:
        manager = IndexManager()
        doc = KnowledgeDocument(
            document_type=DocumentType.TXT, domain=KnowledgeDomain.COMPLIANCE,
            title="Rules", content="compliance rules for energy", namespace="ns",
        )
        chunk = KnowledgeChunk(document_id=doc.document_id, document_type=DocumentType.TXT,
                               content="compliance rules for energy")
        manager.index_document(doc, [chunk])
        results = manager.search_keyword(["compliance", "energy"], limit=10)
        assert str(doc.document_id) in results

    def test_index_and_search_metadata(self) -> None:
        manager = IndexManager()
        doc = KnowledgeDocument(
            document_type=DocumentType.PDF, domain=KnowledgeDomain.SAFETY,
            title="Test", content="content", namespace="ns", owner_id="user-42",
        )
        chunk = KnowledgeChunk(document_id=doc.document_id, document_type=DocumentType.PDF, content="content")
        manager.index_document(doc, [chunk])
        results = manager.search_metadata({"domain": "SAFETY"}, limit=10)
        assert str(doc.document_id) in results

    def test_search_no_matches(self) -> None:
        manager = IndexManager()
        results = manager.search_vector("nonexistent", limit=10)
        assert results == []

    def test_clear_indexes(self) -> None:
        manager = IndexManager()
        doc = KnowledgeDocument(document_type=DocumentType.TXT, content="content", namespace="ns")
        chunk = KnowledgeChunk(document_id=doc.document_id, document_type=DocumentType.TXT, content="content")
        manager.index_document(doc, [chunk])
        manager.clear()
        assert manager.search_vector("content", limit=10) == []


# ─────────────────────────────────────────────────────────────────────────────
# KnowledgeVersionManager
# ─────────────────────────────────────────────────────────────────────────────


class TestKnowledgeVersionManager:
    def test_create_version(self, sample_document: KnowledgeDocument) -> None:
        vmanager = KnowledgeVersionManager()
        version = vmanager.create_version(sample_document)
        assert version.version_number == 1
        assert version.active is True

    def test_create_multiple_versions(self, sample_document: KnowledgeDocument) -> None:
        vmanager = KnowledgeVersionManager()
        v1 = vmanager.create_version(sample_document)
        v2 = vmanager.create_version(sample_document)
        assert v2.version_number == 2
        assert v2.parent_version == 1
        assert v1.active is False
        assert v2.active is True

    def test_get_version(self, sample_document: KnowledgeDocument) -> None:
        vmanager = KnowledgeVersionManager()
        vmanager.create_version(sample_document)
        version = vmanager.get_version(str(sample_document.document_id), 1)
        assert version is not None
        assert version.version_number == 1

    def test_get_version_not_found(self) -> None:
        vmanager = KnowledgeVersionManager()
        version = vmanager.get_version("nonexistent", 1)
        assert version is None

    def test_list_versions(self, sample_document: KnowledgeDocument) -> None:
        vmanager = KnowledgeVersionManager()
        vmanager.create_version(sample_document)
        vmanager.create_version(sample_document, change_summary="Updated content")
        versions = vmanager.list_versions(str(sample_document.document_id))
        assert len(versions) == 2

    def test_get_active_version(self, sample_document: KnowledgeDocument) -> None:
        vmanager = KnowledgeVersionManager()
        vmanager.create_version(sample_document)
        v2 = vmanager.create_version(sample_document)
        active = vmanager.get_active_version(str(sample_document.document_id))
        assert active is not None
        assert active.version_number == v2.version_number

    def test_mark_active(self, sample_document: KnowledgeDocument) -> None:
        vmanager = KnowledgeVersionManager()
        v1 = vmanager.create_version(sample_document)
        v2 = vmanager.create_version(sample_document)
        result = vmanager.mark_active(str(sample_document.document_id), 1)
        assert result is True
        assert v1.active is True
        assert v2.active is False

    def test_compare_versions(self, sample_document: KnowledgeDocument) -> None:
        vmanager = KnowledgeVersionManager()
        vmanager.create_version(sample_document)
        vmanager.create_version(sample_document, change_summary="Updated")
        diff = vmanager.compare_versions(str(sample_document.document_id), 1, 2)
        assert diff["version_a"] == 1
        assert diff["version_b"] == 2

    def test_compare_versions_not_found(self, sample_document: KnowledgeDocument) -> None:
        vmanager = KnowledgeVersionManager()
        with pytest.raises(ValueError):
            vmanager.compare_versions(str(sample_document.document_id), 1, 99)

    def test_restore_version(self, sample_document: KnowledgeDocument) -> None:
        vmanager = KnowledgeVersionManager()
        vmanager.create_version(sample_document)
        vmanager.create_version(sample_document)
        restored = vmanager.restore_version(str(sample_document.document_id), 1)
        assert restored is not None
        assert restored.change_summary == "Restored from version 1"

    def test_restore_version_not_found(self) -> None:
        vmanager = KnowledgeVersionManager()
        restored = vmanager.restore_version("nonexistent", 1)
        assert restored is None

    def test_update_lifecycle_status(self, sample_document: KnowledgeDocument) -> None:
        vmanager = KnowledgeVersionManager()
        vmanager.create_version(sample_document)
        result = vmanager.update_lifecycle_status(
            str(sample_document.document_id), 1, KnowledgeLifecycleStatus.UNDER_REVIEW
        )
        assert result is True
        version = vmanager.get_version(str(sample_document.document_id), 1)
        assert version is not None
        assert version.lifecycle_status == KnowledgeLifecycleStatus.UNDER_REVIEW

    def test_update_lifecycle_status_not_found(self) -> None:
        vmanager = KnowledgeVersionManager()
        result = vmanager.update_lifecycle_status("nonexistent", 1, KnowledgeLifecycleStatus.APPROVED)
        assert result is False

    def test_clear(self, sample_document: KnowledgeDocument) -> None:
        vmanager = KnowledgeVersionManager()
        vmanager.create_version(sample_document)
        vmanager.clear()
        assert vmanager.list_versions(str(sample_document.document_id)) == []


# ─────────────────────────────────────────────────────────────────────────────
# KnowledgeLifecycleManager
# ─────────────────────────────────────────────────────────────────────────────


class TestKnowledgeLifecycleManager:
    def test_default_status(self, sample_document: KnowledgeDocument) -> None:
        lcm = KnowledgeLifecycleManager()
        status = lcm.get_current_status(sample_document)
        assert status == KnowledgeLifecycleStatus.DRAFT

    def test_transition_draft_to_review(self, sample_document: KnowledgeDocument) -> None:
        lcm = KnowledgeLifecycleManager()
        updated = lcm.transition(sample_document, KnowledgeLifecycleStatus.UNDER_REVIEW)
        assert lcm.get_current_status(updated) == KnowledgeLifecycleStatus.UNDER_REVIEW

    def test_transition_review_to_draft(self, sample_document: KnowledgeDocument) -> None:
        lcm = KnowledgeLifecycleManager()
        updated = lcm.transition(sample_document, KnowledgeLifecycleStatus.UNDER_REVIEW)
        updated = lcm.transition(updated, KnowledgeLifecycleStatus.DRAFT)
        assert lcm.get_current_status(updated) == KnowledgeLifecycleStatus.DRAFT

    def test_transition_full_pipeline(self, sample_document: KnowledgeDocument) -> None:
        lcm = KnowledgeLifecycleManager()
        doc = sample_document
        doc = lcm.transition(doc, KnowledgeLifecycleStatus.UNDER_REVIEW)
        doc = lcm.transition(doc, KnowledgeLifecycleStatus.APPROVED)
        doc = lcm.transition(doc, KnowledgeLifecycleStatus.PUBLISHED)
        doc = lcm.transition(doc, KnowledgeLifecycleStatus.DEPRECATED)
        doc = lcm.transition(doc, KnowledgeLifecycleStatus.ARCHIVED)
        assert lcm.get_current_status(doc) == KnowledgeLifecycleStatus.ARCHIVED

    def test_transition_illegal(self, sample_document: KnowledgeDocument) -> None:
        lcm = KnowledgeLifecycleManager()
        with pytest.raises(ValueError, match="Illegal lifecycle transition"):
            lcm.transition(sample_document, KnowledgeLifecycleStatus.APPROVED)

    def test_transition_same_status(self, sample_document: KnowledgeDocument) -> None:
        lcm = KnowledgeLifecycleManager()
        doc = lcm.transition(sample_document, KnowledgeLifecycleStatus.DRAFT)
        assert doc == sample_document  # no-op

    def test_get_history(self, sample_document: KnowledgeDocument) -> None:
        lcm = KnowledgeLifecycleManager()
        lcm.transition(sample_document, KnowledgeLifecycleStatus.UNDER_REVIEW, reason="Ready")
        history = lcm.get_history(str(sample_document.document_id))
        assert len(history) == 1
        assert history[0].reason == "Ready"

    def test_get_all_history(self, sample_document: KnowledgeDocument) -> None:
        lcm = KnowledgeLifecycleManager()
        lcm.transition(sample_document, KnowledgeLifecycleStatus.UNDER_REVIEW)
        assert len(lcm.get_all_history()) == 1

    def test_clear(self, sample_document: KnowledgeDocument) -> None:
        lcm = KnowledgeLifecycleManager()
        lcm.transition(sample_document, KnowledgeLifecycleStatus.UNDER_REVIEW)
        lcm.clear()
        assert len(lcm.get_all_history()) == 0


# ─────────────────────────────────────────────────────────────────────────────
# KnowledgeProvenanceManager
# ─────────────────────────────────────────────────────────────────────────────


class TestKnowledgeProvenanceManager:
    def test_record_provenance(self, sample_document: KnowledgeDocument) -> None:
        pm = KnowledgeProvenanceManager()
        prov = pm.record_provenance(sample_document)
        assert prov.document_id == sample_document.document_id
        assert prov.source_type == "upload"
        assert prov.confidence == 1.0

    def test_record_provenance_custom(self, sample_document: KnowledgeDocument) -> None:
        pm = KnowledgeProvenanceManager()
        prov = pm.record_provenance(
            sample_document,
            source_document="imported_doc_1",
            source_type="import",
            imported_by="admin",
            processing_pipeline=["validate", "clean", "chunk"],
        )
        assert prov.source_document == "imported_doc_1"
        assert prov.source_type == "import"
        assert prov.imported_by == "admin"
        assert len(prov.processing_pipeline) == 3

    def test_get_provenance(self, sample_document: KnowledgeDocument) -> None:
        pm = KnowledgeProvenanceManager()
        pm.record_provenance(sample_document)
        prov = pm.get_provenance(str(sample_document.document_id))
        assert prov is not None

    def test_get_provenance_not_found(self) -> None:
        pm = KnowledgeProvenanceManager()
        prov = pm.get_provenance("nonexistent")
        assert prov is None

    def test_update_confidence(self, sample_document: KnowledgeDocument) -> None:
        pm = KnowledgeProvenanceManager()
        pm.record_provenance(sample_document)
        result = pm.update_confidence(str(sample_document.document_id), 0.85)
        assert result is True
        prov = pm.get_provenance(str(sample_document.document_id))
        assert prov is not None
        assert prov.confidence == 0.85

    def test_update_confidence_clamps(self, sample_document: KnowledgeDocument) -> None:
        pm = KnowledgeProvenanceManager()
        pm.record_provenance(sample_document)
        pm.update_confidence(str(sample_document.document_id), 1.5)
        prov = pm.get_provenance(str(sample_document.document_id))
        assert prov is not None
        assert prov.confidence == 1.0

    def test_update_confidence_not_found(self) -> None:
        pm = KnowledgeProvenanceManager()
        result = pm.update_confidence("nonexistent", 0.5)
        assert result is False

    def test_add_pipeline_stage(self, sample_document: KnowledgeDocument) -> None:
        pm = KnowledgeProvenanceManager()
        pm.record_provenance(sample_document)
        result = pm.add_pipeline_stage(str(sample_document.document_id), "embed")
        assert result is True
        prov = pm.get_provenance(str(sample_document.document_id))
        assert prov is not None
        assert "embed" in prov.processing_pipeline

    def test_add_pipeline_stage_not_found(self) -> None:
        pm = KnowledgeProvenanceManager()
        result = pm.add_pipeline_stage("nonexistent", "embed")
        assert result is False

    def test_clear(self, sample_document: KnowledgeDocument) -> None:
        pm = KnowledgeProvenanceManager()
        pm.record_provenance(sample_document)
        pm.clear()
        assert pm.get_provenance(str(sample_document.document_id)) is None


# ─────────────────────────────────────────────────────────────────────────────
# QueryAnalyzer
# ─────────────────────────────────────────────────────────────────────────────


class TestQueryAnalyzer:
    def test_analyse_lookup(self) -> None:
        analyzer = QueryAnalyzer()
        query = KnowledgeQuery(query_text="what is safety protocol")
        analysis = analyzer.analyse(query)
        assert analysis.intent == "lookup"
        assert "safety" in analysis.keywords
        assert analysis.suggested_retrieval_type == RetrievalType.VECTOR

    def test_analyse_compare(self) -> None:
        analyzer = QueryAnalyzer()
        query = KnowledgeQuery(query_text="compare safety vs compliance")
        analysis = analyzer.analyse(query)
        assert analysis.intent == "compare"
        assert analysis.suggested_retrieval_type == RetrievalType.HYBRID

    def test_analyse_summarise(self) -> None:
        analyzer = QueryAnalyzer()
        query = KnowledgeQuery(query_text="summarise the safety report")
        analysis = analyzer.analyse(query)
        assert analysis.intent == "summarise"

    def test_analyse_list(self) -> None:
        analyzer = QueryAnalyzer()
        query = KnowledgeQuery(query_text="list all safety documents")
        analysis = analyzer.analyse(query)
        assert analysis.intent == "list"
        assert analysis.suggested_retrieval_type == RetrievalType.METADATA

    def test_analyse_with_filters(self) -> None:
        analyzer = QueryAnalyzer()
        query = KnowledgeQuery(
            query_text="find safety docs",
            namespace="acme",
            owner_id="user-42",
        )
        analysis = analyzer.analyse(query)
        assert analysis.filters.get("namespace") == "acme"
        assert analysis.filters.get("owner") == "user-42"

    def test_analyse_with_domains(self) -> None:
        analyzer = QueryAnalyzer()
        query = KnowledgeQuery(
            query_text="energy compliance",
            domains=[KnowledgeDomain.ENERGY],
        )
        analysis = analyzer.analyse(query)
        assert analysis.domain == KnowledgeDomain.ENERGY


# ─────────────────────────────────────────────────────────────────────────────
# QueryRewriter
# ─────────────────────────────────────────────────────────────────────────────


class TestQueryRewriter:
    def test_rewrite_basic(self) -> None:
        rewriter = QueryRewriter()
        result = rewriter.rewrite("What is Safety Protocol?")
        assert result.original_query == "What is Safety Protocol?"
        assert result.normalised_query == "what is safety protocol?"
        assert len(result.alternative_queries) >= 1

    def test_rewrite_with_synonyms(self) -> None:
        rewriter = QueryRewriter()
        synonyms = {"safety": ["security", "protection"]}
        result = rewriter.rewrite_with_synonyms("safety protocol", synonyms=synonyms)
        assert "security" in result.expanded_query
        assert "protection" in result.expanded_query
        assert result.strategy == "synonym"


# ─────────────────────────────────────────────────────────────────────────────
# HybridRetriever
# ─────────────────────────────────────────────────────────────────────────────


class TestHybridRetriever:
    def test_retrieve_vector(self) -> None:
        doc_id = uuid.uuid4()
        doc = KnowledgeDocument(
            document_id=doc_id, document_type=DocumentType.PDF, domain=KnowledgeDomain.SAFETY,
            title="Safety", content="safety procedure steps", namespace="ns",
        )
        chunks = [
            KnowledgeChunk(document_id=doc_id, document_type=DocumentType.PDF,
                           content="safety procedure steps", chunk_index=0, domain=KnowledgeDomain.SAFETY),
        ]
        index = IndexManager()
        retriever = HybridRetriever(index_manager=index)
        index.index_document(doc, chunks)
        query = KnowledgeQuery(query_text="safety", limit=10, retrieval_type=RetrievalType.VECTOR)
        results = retriever.retrieve(query, chunks=chunks)
        assert len(results) > 0

    def test_retrieve_hybrid(self) -> None:
        doc_id = uuid.uuid4()
        doc = KnowledgeDocument(
            document_id=doc_id, document_type=DocumentType.PDF, domain=KnowledgeDomain.SAFETY,
            title="Safety", content="safety compliance procedures", namespace="ns",
        )
        chunks = [
            KnowledgeChunk(document_id=doc_id, document_type=DocumentType.PDF,
                           content="safety compliance procedures", chunk_index=0, domain=KnowledgeDomain.SAFETY),
        ]
        index = IndexManager()
        retriever = HybridRetriever(index_manager=index)
        index.index_document(doc, chunks)

        query = KnowledgeQuery(
            query_text="safety compliance",
            limit=10,
            retrieval_type=RetrievalType.HYBRID,
        )
        results = retriever.retrieve(query, chunks=chunks)
        assert len(results) > 0

    def test_retrieve_empty(self) -> None:
        retriever = HybridRetriever()
        query = KnowledgeQuery(
            query_text="nothing",
            limit=10,
            retrieval_type=RetrievalType.VECTOR,
        )
        results = retriever.retrieve(query)
        assert results == []

    def test_get_supported_types(self) -> None:
        retriever = HybridRetriever()
        types = retriever.get_supported_retrieval_types()
        assert len(types) == 4
        assert RetrievalType.VECTOR in types


# ─────────────────────────────────────────────────────────────────────────────
# ResultFusion
# ─────────────────────────────────────────────────────────────────────────────


class TestResultFusion:
    def test_fuse_single_set(self, sample_chunks: list[KnowledgeChunk]) -> None:
        fusion = ResultFusion()
        results = [
            KnowledgeResult(
                query_id=uuid.uuid4(),
                chunk=sample_chunks[0],
                score=0.9,
                rank=0,
            )
        ]
        fused = fusion.fuse([results])
        assert len(fused) == 1

    def test_fuse_multiple_sets(self, sample_chunks: list[KnowledgeChunk]) -> None:
        fusion = ResultFusion()
        qid = uuid.uuid4()

        set1 = [
            KnowledgeResult(query_id=qid, chunk=sample_chunks[0], score=0.9, rank=0),
            KnowledgeResult(query_id=qid, chunk=sample_chunks[1], score=0.7, rank=1),
        ]
        set2 = [
            KnowledgeResult(query_id=qid, chunk=sample_chunks[0], score=0.85, rank=0),
        ]
        fused = fusion.fuse([set1, set2])
        assert len(fused) == 2  # deduplicated
        # should keep higher score
        assert fused[0].score == 0.9

    def test_fuse_empty(self) -> None:
        fusion = ResultFusion()
        fused = fusion.fuse([[], []])
        assert fused == []


# ─────────────────────────────────────────────────────────────────────────────
# Reranker
# ─────────────────────────────────────────────────────────────────────────────


class TestReranker:
    def test_rerank_boost(self, sample_chunks: list[KnowledgeChunk]) -> None:
        reranker = Reranker()
        qid = uuid.uuid4()
        results = [
            KnowledgeResult(query_id=qid, chunk=sample_chunks[0], score=0.5, rank=0),
            KnowledgeResult(query_id=qid, chunk=sample_chunks[1], score=0.3, rank=1),
        ]
        reranked = reranker.rerank("safety procedures chunk one content", results)
        assert len(reranked) == 2
        # chunk 0 mentions "safety" which matches query
        assert reranked[0].score > 0.5

    def test_rerank_no_keywords(self, sample_chunks: list[KnowledgeChunk]) -> None:
        reranker = Reranker()
        qid = uuid.uuid4()
        results = [
            KnowledgeResult(query_id=qid, chunk=sample_chunks[0], score=0.5, rank=0),
        ]
        reranked = reranker.rerank("ab", results)  # no keywords > 2 chars
        assert reranked == results

    def test_rerank_empty(self) -> None:
        reranker = Reranker()
        result = reranker.rerank("test", [])
        assert result == []


# ─────────────────────────────────────────────────────────────────────────────
# ContextBuilder
# ─────────────────────────────────────────────────────────────────────────────


class TestContextBuilder:
    def test_build(self, sample_chunks: list[KnowledgeChunk], sample_query: KnowledgeQuery) -> None:
        builder = ContextBuilder()
        qid = uuid.uuid4()
        results = [
            KnowledgeResult(query_id=qid, chunk=sample_chunks[0], score=0.9, rank=0),
            KnowledgeResult(query_id=qid, chunk=sample_chunks[1], score=0.7, rank=1),
        ]
        context = builder.build(query=sample_query, results=results)
        assert context.total_results == 2
        assert context.query is not None
        assert len(context.domains) > 0

    def test_build_no_results(self) -> None:
        builder = ContextBuilder()
        context = builder.build()
        assert context.total_results == 0

    def test_build_max_results(self) -> None:
        builder = ContextBuilder()
        qid = uuid.uuid4()
        many_results = [
            KnowledgeResult(
                query_id=qid,
                chunk=KnowledgeChunk(document_id=uuid.uuid4(), document_type=DocumentType.TXT, content=f"Chunk {i}"),
                score=0.5,
                rank=i,
            )
            for i in range(100)
        ]
        context = builder.build(results=many_results)
        assert context.total_results <= builder.MAX_RESULTS

    def test_estimate_tokens(self) -> None:
        builder = ContextBuilder()
        tokens = builder._estimate_tokens(100)
        assert tokens == 25


# ─────────────────────────────────────────────────────────────────────────────
# KnowledgeCache
# ─────────────────────────────────────────────────────────────────────────────


class TestKnowledgeCache:
    def test_set_and_get(self) -> None:
        cache = KnowledgeCache()
        ctx = KnowledgeContext()
        cache.set("key-1", ctx)
        assert cache.get("key-1") is ctx

    def test_get_miss(self) -> None:
        cache = KnowledgeCache()
        assert cache.get("nonexistent") is None

    def test_invalidate(self) -> None:
        cache = KnowledgeCache()
        ctx = KnowledgeContext()
        cache.set("key-1", ctx)
        assert cache.invalidate("key-1") is True
        assert cache.get("key-1") is None

    def test_invalidate_miss(self) -> None:
        cache = KnowledgeCache()
        assert cache.invalidate("nonexistent") is False

    def test_clear(self) -> None:
        cache = KnowledgeCache()
        cache.set("k1", KnowledgeContext())
        cache.set("k2", KnowledgeContext())
        count = cache.clear()
        assert count == 2
        assert cache.size() == 0

    def test_size(self) -> None:
        cache = KnowledgeCache()
        assert cache.size() == 0
        cache.set("k1", KnowledgeContext())
        assert cache.size() == 1


# ─────────────────────────────────────────────────────────────────────────────
# KnowledgePolicyEngine
# ─────────────────────────────────────────────────────────────────────────────


class TestKnowledgePolicyEngine:
    def test_check_query_ok(self) -> None:
        engine = KnowledgePolicyEngine()
        query = KnowledgeQuery(query_text="test", limit=10)
        violations = engine.check_query(query)
        assert violations == []

    def test_check_query_exceeds_limit(self) -> None:
        engine = KnowledgePolicyEngine()
        engine.set_max_results(10)
        query = KnowledgeQuery(query_text="test", limit=20)
        violations = engine.check_query(query)
        assert len(violations) > 0

    def test_check_query_exceeds_domains(self) -> None:
        engine = KnowledgePolicyEngine()
        query = KnowledgeQuery(
            query_text="test",
            limit=10,
            domains=[KnowledgeDomain.SAFETY, KnowledgeDomain.ENERGY, KnowledgeDomain.COMPLIANCE],
        )
        engine.set_max_domains(2)
        violations = engine.check_query(query)
        assert len(violations) > 0

    def test_check_context_empty(self) -> None:
        engine = KnowledgePolicyEngine()
        ctx = KnowledgeContext(total_results=0)
        violations = engine.check_context(ctx)
        assert len(violations) > 0

    def test_check_context_ok(self) -> None:
        engine = KnowledgePolicyEngine()
        ctx = KnowledgeContext(total_results=5)
        violations = engine.check_context(ctx)
        assert violations == []

    def test_check_result(self, sample_chunks: list[KnowledgeChunk]) -> None:
        engine = KnowledgePolicyEngine()
        result = KnowledgeResult(query_id=uuid.uuid4(), chunk=sample_chunks[0])
        violations = engine.check_result(result)
        assert violations == []

    def test_version_access(self, sample_document: KnowledgeDocument) -> None:
        engine = KnowledgePolicyEngine()
        assert engine.check_version_access(sample_document) is True

    def test_set_allowed_domains(self) -> None:
        engine = KnowledgePolicyEngine()
        engine.set_allowed_domains(["SAFETY"])
        query = KnowledgeQuery(query_text="test", domains=[KnowledgeDomain.SAFETY])
        violations = engine.check_query(query)
        assert violations == []

    def test_set_allowed_domains_blocked(self) -> None:
        engine = KnowledgePolicyEngine()
        engine.set_allowed_domains(["SAFETY"])
        query = KnowledgeQuery(query_text="test", domains=[KnowledgeDomain.ENERGY])
        violations = engine.check_query(query)
        assert len(violations) > 0


# ─────────────────────────────────────────────────────────────────────────────
# KnowledgeTrace
# ─────────────────────────────────────────────────────────────────────────────


class TestKnowledgeTrace:
    def test_record_and_get(self) -> None:
        trace = KnowledgeTrace()
        record = TraceRecord(stage_name="retrieval", operation="retrieve")
        trace.record(record)
        results = trace.get_by_operation("retrieve")
        assert len(results) == 1

    def test_get_by_trace_id(self) -> None:
        trace = KnowledgeTrace()
        record = TraceRecord(stage_name="indexing", operation="index")
        trace.record(record)
        results = trace.get_by_trace_id(str(record.trace_id))
        assert len(results) == 1

    def test_get_by_operation_not_found(self) -> None:
        trace = KnowledgeTrace()
        record = TraceRecord(stage_name="retrieval", operation="retrieve")
        trace.record(record)
        results = trace.get_by_operation("index")
        assert results == []

    def test_get_recent(self) -> None:
        trace = KnowledgeTrace()
        for i in range(5):
            trace.record(TraceRecord(stage_name="retrieval", operation=f"op-{i}"))
        recent = trace.get_recent(limit=3)
        assert len(recent) == 3

    def test_count(self) -> None:
        trace = KnowledgeTrace()
        assert trace.count() == 0
        trace.record(TraceRecord(stage_name="retrieval", operation="retrieve"))
        assert trace.count() == 1

    def test_clear(self) -> None:
        trace = KnowledgeTrace()
        trace.record(TraceRecord(stage_name="retrieval", operation="retrieve"))
        trace.clear()
        assert trace.count() == 0


# ─────────────────────────────────────────────────────────────────────────────
# KnowledgeMetricsCollector
# ─────────────────────────────────────────────────────────────────────────────


class TestKnowledgeMetricsCollector:
    def test_snapshot_defaults(self) -> None:
        mc = KnowledgeMetricsCollector()
        snap = mc.snapshot()
        assert snap.documents_total == 0
        assert snap.chunks_total == 0
        assert snap.retrievals_total == 0

    def test_increment_documents(self) -> None:
        mc = KnowledgeMetricsCollector()
        mc.increment_documents(domain="SAFETY", doc_type="PDF")
        snap = mc.snapshot()
        assert snap.documents_total == 1
        assert snap.documents_per_domain.get("SAFETY") == 1
        assert snap.documents_per_type.get("PDF") == 1

    def test_increment_chunks(self) -> None:
        mc = KnowledgeMetricsCollector()
        mc.increment_chunks(5)
        snap = mc.snapshot()
        assert snap.chunks_total == 5

    def test_retrieval_timing(self) -> None:
        mc = KnowledgeMetricsCollector()
        mc.increment_retrievals()
        mc.record_retrieval_time(150.0)
        mc.record_retrieval_time(50.0)
        snap = mc.snapshot()
        assert snap.retrievals_total == 1
        assert snap.average_retrieval_time_ms == 100.0

    def test_cache_metrics(self) -> None:
        mc = KnowledgeMetricsCollector()
        mc.increment_cache_hits()
        mc.increment_cache_hits()
        mc.increment_cache_misses()
        snap = mc.snapshot()
        assert snap.cache_hits == 2
        assert snap.cache_misses == 1

    def test_reset(self) -> None:
        mc = KnowledgeMetricsCollector()
        mc.increment_documents()
        mc.reset()
        snap = mc.snapshot()
        assert snap.documents_total == 0


# ─────────────────────────────────────────────────────────────────────────────
# Import check: TraceRecord
# ─────────────────────────────────────────────────────────────────────────────


from adip.knowledge.execution.models import TraceRecord  # noqa: E402
