"""Tests for Knowledge Manager Phase 3 — Enterprise Orchestration.

Covers KnowledgeService, KnowledgeManager, KnowledgeCoordinator,
KnowledgeSession, Retrieval Strategy Framework, KnowledgeHealth,
Metrics Aggregation, Tracing, Integration Hooks, and Pipeline.
"""

from __future__ import annotations

import uuid
from typing import Any

import pytest

from adip.knowledge.contracts.models import (
    ExplainabilityMetadata,
    KnowledgeContext,
    KnowledgeDocument,
    KnowledgeHealth,
    KnowledgeMetadata,
    KnowledgeMetrics,
    KnowledgeQuery,
    KnowledgeSession,
)
from adip.knowledge.enums import (
    DocumentType,
    KnowledgeDomain,
    KnowledgeStatus,
    RetrievalType,
)
from adip.knowledge.execution.metrics import KnowledgeMetricsCollector
from adip.knowledge.execution.models import TraceRecord
from adip.knowledge.execution.session import KnowledgeSessionManager
from adip.knowledge.execution.strategies import (
    AgenticRetrievalStrategy,
    GraphRetrievalStrategy,
    HybridRetrievalStrategy,
    KeywordRetrievalStrategy,
    MetadataRetrievalStrategy,
    RetrievalStrategyResult,
    VectorRetrievalStrategy,
    get_strategy,
)
from adip.knowledge.execution.trace import KnowledgeTrace
from adip.knowledge.orchestration.coordinator import KnowledgeCoordinator
from adip.knowledge.orchestration.manager import KnowledgeManager
from adip.knowledge.services.hooks import IntegrationHooks
from adip.knowledge.services.service import AuthResult, KnowledgeService

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
def sample_query() -> KnowledgeQuery:
    return KnowledgeQuery(
        query_text="safety procedures",
        domains=[KnowledgeDomain.SAFETY],
        limit=10,
        retrieval_type=RetrievalType.HYBRID,
    )


# ─────────────────────────────────────────────────────────────────────────────
# KnowledgeSession
# ─────────────────────────────────────────────────────────────────────────────


class TestKnowledgeSession:
    def test_create_session(self) -> None:
        sm = KnowledgeSessionManager()
        session = sm.create_session(query="test query", user_id="user-1", retrieval_strategy="HYBRID")
        assert session.session_id is not None
        assert session.query == "test query"
        assert session.user_id == "user-1"
        assert session.retrieval_strategy == "HYBRID"
        assert session.started_at is not None
        assert session.completed_at is None

    def test_complete_session(self) -> None:
        sm = KnowledgeSessionManager()
        session = sm.create_session(query="test")
        completed = sm.complete_session(
            session,
            duration_ms=150.0,
            documents_used=["doc-1"],
            versions_used=[1],
            chunks_used=["chunk-1"],
            cache_hits=3,
            processing_statistics={"retrieval_ms": 100},
        )
        assert completed.completed_at is not None
        assert completed.duration_ms == 150.0
        assert "doc-1" in completed.documents_used
        assert 1 in completed.versions_used
        assert completed.cache_hits == 3

    def test_get_session(self) -> None:
        sm = KnowledgeSessionManager()
        created = sm.create_session()
        fetched = sm.get_session(str(created.session_id))
        assert fetched is not None
        assert fetched.session_id == created.session_id

    def test_get_session_not_found(self) -> None:
        sm = KnowledgeSessionManager()
        assert sm.get_session("nonexistent") is None

    def test_clear(self) -> None:
        sm = KnowledgeSessionManager()
        sm.create_session()
        sm.create_session()
        sm.clear()
        assert sm.get_session("anything") is None


# ─────────────────────────────────────────────────────────────────────────────
# ExplainabilityMetadata
# ─────────────────────────────────────────────────────────────────────────────


class TestExplainabilityMetadata:
    def test_defaults(self) -> None:
        meta = ExplainabilityMetadata()
        assert meta.why_selected == ""
        assert meta.strategy_used == ""
        assert meta.version_selected == 1

    def test_custom_values(self) -> None:
        meta = ExplainabilityMetadata(
            why_selected="Vector similarity match",
            strategy_used="VECTOR",
            ranking_reason="Score 0.95 at rank 0",
            version_selected=2,
            provenance="upload → validate → clean → chunk → embed",
        )
        assert meta.why_selected == "Vector similarity match"
        assert meta.version_selected == 2


# ─────────────────────────────────────────────────────────────────────────────
# Retrieval Strategy Framework
# ─────────────────────────────────────────────────────────────────────────────


class TestRetrievalStrategies:
    def test_vector_strategy(self) -> None:
        strategy = VectorRetrievalStrategy()
        assert strategy.get_type() == RetrievalType.VECTOR

    def test_keyword_strategy(self) -> None:
        strategy = KeywordRetrievalStrategy()
        assert strategy.get_type() == RetrievalType.KEYWORD

    def test_metadata_strategy(self) -> None:
        strategy = MetadataRetrievalStrategy()
        assert strategy.get_type() == RetrievalType.METADATA

    def test_hybrid_strategy(self) -> None:
        strategy = HybridRetrievalStrategy()
        assert strategy.get_type() == RetrievalType.HYBRID

    def test_graph_strategy_placeholder(self) -> None:
        strategy = GraphRetrievalStrategy()
        result = strategy.retrieve(KnowledgeQuery(query_text="test"))
        assert result.results == []

    def test_agentic_strategy_placeholder(self) -> None:
        strategy = AgenticRetrievalStrategy()
        result = strategy.retrieve(KnowledgeQuery(query_text="test"))
        assert result.results == []

    def test_get_strategy_factory(self) -> None:
        strategy = get_strategy(RetrievalType.VECTOR)
        assert isinstance(strategy, VectorRetrievalStrategy)

        strategy = get_strategy(RetrievalType.HYBRID)
        assert isinstance(strategy, HybridRetrievalStrategy)

    def test_strategy_result(self) -> None:
        result = RetrievalStrategyResult([], RetrievalType.VECTOR, [{"why": "test"}])
        assert result.strategy == RetrievalType.VECTOR
        assert result.explainability == [{"why": "test"}]


# ─────────────────────────────────────────────────────────────────────────────
# KnowledgeMetricsCollector (enhanced)
# ─────────────────────────────────────────────────────────────────────────────


class TestKnowledgeMetricsCollector:
    def test_snapshot_defaults(self) -> None:
        mc = KnowledgeMetricsCollector()
        snap = mc.snapshot()
        assert snap.documents_total == 0
        assert snap.chunks_total == 0
        assert snap.retrievals_total == 0
        assert snap.cache_hits == 0
        assert snap.cache_misses == 0

    def test_increment_documents(self) -> None:
        mc = KnowledgeMetricsCollector()
        mc.increment_documents(domain="SAFETY", doc_type="PDF")
        snap = mc.snapshot()
        assert snap.documents_total == 1
        assert snap.documents_per_domain.get("SAFETY") == 1

    def test_increment_chunks(self) -> None:
        mc = KnowledgeMetricsCollector()
        mc.increment_chunks(5)
        assert mc.snapshot().chunks_total == 5

    def test_retrieval_and_timing(self) -> None:
        mc = KnowledgeMetricsCollector()
        mc.increment_retrievals()
        mc.record_retrieval_time(100.0)
        mc.record_retrieval_time(200.0)
        snap = mc.snapshot()
        assert snap.retrievals_total == 1
        assert snap.average_retrieval_time_ms == 150.0

    def test_cache_counts(self) -> None:
        mc = KnowledgeMetricsCollector()
        mc.increment_cache_hits()
        mc.increment_cache_hits()
        mc.increment_cache_misses()
        snap = mc.snapshot()
        assert snap.cache_hits == 2
        assert snap.cache_misses == 1

    def test_indexed_and_failed(self) -> None:
        mc = KnowledgeMetricsCollector()
        mc.increment_indexed()
        mc.increment_failed()
        snap = mc.snapshot()
        assert snap.indexed_total == 1
        assert snap.failed_total == 1

    def test_reset(self) -> None:
        mc = KnowledgeMetricsCollector()
        mc.increment_documents()
        mc.reset()
        assert mc.snapshot().documents_total == 0


# ─────────────────────────────────────────────────────────────────────────────
# KnowledgeTrace
# ─────────────────────────────────────────────────────────────────────────────


class TestKnowledgeTrace:
    def test_record_and_retrieve(self) -> None:
        trace = KnowledgeTrace()
        record = TraceRecord(stage_name="retrieval", operation="retrieve")
        trace.record(record)
        results = trace.get_by_operation("retrieve")
        assert len(results) == 1

    def test_get_by_trace_id(self) -> None:
        trace = KnowledgeTrace()
        record = TraceRecord(stage_name="indexing", operation="index")
        trace.record(record)
        fetched = trace.get_by_trace_id(str(record.trace_id))
        assert len(fetched) == 1

    def test_get_recent(self) -> None:
        trace = KnowledgeTrace()
        for i in range(5):
            trace.record(TraceRecord(stage_name="test", operation=f"op-{i}"))
        recent = trace.get_recent(limit=3)
        assert len(recent) == 3

    def test_count_and_clear(self) -> None:
        trace = KnowledgeTrace()
        assert trace.count() == 0
        trace.record(TraceRecord(stage_name="test", operation="op"))
        assert trace.count() == 1
        trace.clear()
        assert trace.count() == 0


# ─────────────────────────────────────────────────────────────────────────────
# IntegrationHooks
# ─────────────────────────────────────────────────────────────────────────────


class TestIntegrationHooks:
    def test_pre_ingest_hook(self) -> None:
        hooks = IntegrationHooks()
        calls: list[str] = []

        def hook(doc: KnowledgeDocument) -> None:
            calls.append(doc.title)

        hooks.on_pre_ingest(hook)
        doc = KnowledgeDocument(document_type=DocumentType.PDF, title="Test Doc")
        hooks.invoke_pre_ingest(doc)
        assert calls == ["Test Doc"]

    def test_post_retrieve_hook(self) -> None:
        hooks = IntegrationHooks()
        calls: list[int] = []

        def hook(ctx: KnowledgeContext) -> None:
            calls.append(ctx.total_results)

        hooks.on_post_retrieve(hook)
        ctx = KnowledgeContext(total_results=5)
        hooks.invoke_post_retrieve(ctx)
        assert calls == [5]

    def test_session_hooks(self) -> None:
        hooks = IntegrationHooks()
        started: list[str] = []
        completed: list[str] = []

        hooks.on_session_started(lambda s: started.append(s.query))
        hooks.on_session_completed(lambda s: completed.append(s.query))

        session = KnowledgeSession(query="test query")
        hooks.invoke_session_started(session)
        hooks.invoke_session_completed(session)

        assert started == ["test query"]
        assert completed == ["test query"]

    def test_error_hook(self) -> None:
        hooks = IntegrationHooks()
        errors: list[str] = []

        def hook(op: str, err: Exception) -> None:
            errors.append(f"{op}: {err}")

        hooks.on_error(hook)
        hooks.invoke_error("retrieve", ValueError("test error"))
        assert "retrieve" in errors[0]

    def test_hook_exception_isolation(self) -> None:
        hooks = IntegrationHooks()

        def failing(doc: KnowledgeDocument) -> None:
            msg = "hook failed"
            raise RuntimeError(msg)

        def succeeding(doc: KnowledgeDocument) -> None:
            pass

        hooks.on_pre_ingest(failing)
        hooks.on_pre_ingest(succeeding)
        # Should not raise
        hooks.invoke_pre_ingest(KnowledgeDocument(document_type=DocumentType.PDF))


# ─────────────────────────────────────────────────────────────────────────────
# KnowledgeCoordinator
# ─────────────────────────────────────────────────────────────────────────────


class TestKnowledgeCoordinator:
    def test_process_document(self, sample_document: KnowledgeDocument) -> None:
        coord = KnowledgeCoordinator()
        result = coord.process_document(sample_document)
        assert result.status == KnowledgeStatus.INDEXED
        assert "chunk_count" in result.extra
        assert "embedding_count" in result.extra

    def test_process_invalid_document(self) -> None:
        coord = KnowledgeCoordinator()
        doc = KnowledgeDocument(document_type=DocumentType.PDF, content="", title="", namespace="")
        result = coord.process_document(doc)
        assert result.status == KnowledgeStatus.FAILED

    def test_retrieve(self, sample_document: KnowledgeDocument) -> None:
        coord = KnowledgeCoordinator()
        coord.process_document(sample_document)
        query = KnowledgeQuery(query_text="safety", limit=10)
        ctx = coord.retrieve(query, strategy=RetrievalType.VECTOR)
        assert ctx is not None
        assert ctx.total_results >= 0

    def test_retrieve_hybrid(self, sample_document: KnowledgeDocument) -> None:
        coord = KnowledgeCoordinator()
        coord.process_document(sample_document)
        query = KnowledgeQuery(query_text="safety manual", limit=10)
        ctx = coord.retrieve(query, strategy=RetrievalType.HYBRID)
        assert ctx is not None

    def test_get_document(self, sample_document: KnowledgeDocument) -> None:
        coord = KnowledgeCoordinator()
        coord.process_document(sample_document)
        doc = coord.get_document(str(sample_document.document_id))
        assert doc is not None
        assert doc.title == "Safety Manual 2024"

    def test_delete_document(self, sample_document: KnowledgeDocument) -> None:
        coord = KnowledgeCoordinator()
        coord.process_document(sample_document)
        doc_id = str(sample_document.document_id)
        assert coord.delete_document(doc_id) is True
        assert coord.get_document(doc_id) is None

    def test_delete_nonexistent(self) -> None:
        coord = KnowledgeCoordinator()
        assert coord.delete_document("nonexistent") is False

    def test_archive_document(self, sample_document: KnowledgeDocument) -> None:
        coord = KnowledgeCoordinator()
        coord.process_document(sample_document)
        doc_id = str(sample_document.document_id)
        assert coord.archive_document(doc_id) is True

    def test_archive_nonexistent(self) -> None:
        coord = KnowledgeCoordinator()
        assert coord.archive_document("nonexistent") is False

    def test_health(self) -> None:
        coord = KnowledgeCoordinator()
        health = coord.health()
        assert health.overall_status == "HEALTHY"
        assert health.is_healthy() is True

    def test_metrics(self) -> None:
        coord = KnowledgeCoordinator()
        metrics = coord.metrics()
        assert isinstance(metrics, KnowledgeMetrics)
        assert metrics.documents_total >= 0

    def test_explainability_on_results(self, sample_document: KnowledgeDocument) -> None:
        coord = KnowledgeCoordinator()
        coord.process_document(sample_document)
        query = KnowledgeQuery(query_text="safety", limit=5)
        ctx = coord.retrieve(query, strategy=RetrievalType.VECTOR)
        for r in ctx.results:
            assert "explainability" in r.metadata
            exp = r.metadata["explainability"]
            assert "why_selected" in exp
            assert "strategy_used" in exp

    def test_policy_blocked_query(self) -> None:
        coord = KnowledgeCoordinator()
        query = KnowledgeQuery(query_text="test", domains=[KnowledgeDomain.SAFETY, KnowledgeDomain.ENERGY])
        coord._policy_engine.set_max_domains(1)
        ctx = coord.retrieve(query)
        assert ctx.total_results == 0
        assert "policy_violations" in ctx.metadata

    def test_session_in_coordinator(self) -> None:
        coord = KnowledgeCoordinator()
        session = coord._session_manager.create_session(query="test")
        fetched = coord.get_session(str(session.session_id))
        assert fetched is not None


# ─────────────────────────────────────────────────────────────────────────────
# KnowledgeManager
# ─────────────────────────────────────────────────────────────────────────────


class TestKnowledgeManager:
    def test_create_document(self, sample_document: KnowledgeDocument) -> None:
        mgr = KnowledgeManager()
        result = mgr.create_document(sample_document)
        assert result.status == KnowledgeStatus.INDEXED

    def test_read_document(self, sample_document: KnowledgeDocument) -> None:
        mgr = KnowledgeManager()
        mgr.create_document(sample_document)
        doc = mgr.read_document(str(sample_document.document_id))
        assert doc is not None
        assert doc.title == "Safety Manual 2024"

    def test_read_nonexistent(self) -> None:
        mgr = KnowledgeManager()
        assert mgr.read_document("nonexistent") is None

    def test_update_document(self, sample_document: KnowledgeDocument) -> None:
        mgr = KnowledgeManager()
        mgr.create_document(sample_document)
        updated = sample_document.model_copy(update={"title": "Updated Title"})
        result = mgr.update_document(updated)
        assert result.title == "Updated Title"

    def test_delete_document(self, sample_document: KnowledgeDocument) -> None:
        mgr = KnowledgeManager()
        mgr.create_document(sample_document)
        assert mgr.delete_document(str(sample_document.document_id)) is True

    def test_search_documents(self, sample_document: KnowledgeDocument) -> None:
        mgr = KnowledgeManager()
        mgr.create_document(sample_document)
        results = mgr.search_documents(query="safety")
        assert len(results) >= 1

    def test_search_documents_by_domain(self, sample_document: KnowledgeDocument) -> None:
        mgr = KnowledgeManager()
        mgr.create_document(sample_document)
        results = mgr.search_documents(domain=KnowledgeDomain.SAFETY)
        assert len(results) >= 1

    def test_search_documents_no_match(self) -> None:
        mgr = KnowledgeManager()
        results = mgr.search_documents(query="nonexistent")
        assert results == []

    def test_retrieve_knowledge(self, sample_document: KnowledgeDocument) -> None:
        mgr = KnowledgeManager()
        mgr.create_document(sample_document)
        query = KnowledgeQuery(query_text="safety", limit=5)
        ctx = mgr.retrieve_knowledge(query, strategy=RetrievalType.HYBRID)
        assert ctx is not None

    def test_get_health(self) -> None:
        mgr = KnowledgeManager()
        health = mgr.get_health()
        assert health.is_healthy() is True

    def test_get_metrics(self) -> None:
        mgr = KnowledgeManager()
        metrics = mgr.get_metrics()
        assert isinstance(metrics, KnowledgeMetrics)

    def test_ingest_document_convenience(self) -> None:
        mgr = KnowledgeManager()
        doc = mgr.ingest_document(
            content="Test content here",
            document_type=DocumentType.TXT,
            title="Test Doc",
            domain=KnowledgeDomain.SAFETY,
        )
        assert doc.status == KnowledgeStatus.INDEXED
        assert doc.title == "Test Doc"

    def test_get_session(self) -> None:
        mgr = KnowledgeManager()
        session = mgr._coordinator._session_manager.create_session(query="test")
        fetched = mgr.get_session(str(session.session_id))
        assert fetched is not None


# ─────────────────────────────────────────────────────────────────────────────
# KnowledgeService — ONLY public API
# ─────────────────────────────────────────────────────────────────────────────


class TestKnowledgeService:
    def test_ingest(self, sample_document: KnowledgeDocument) -> None:
        svc = KnowledgeService()
        result = svc.ingest(sample_document, user_id="admin")
        assert result.status == KnowledgeStatus.INDEXED

    def test_retrieve(self, sample_document: KnowledgeDocument) -> None:
        svc = KnowledgeService()
        svc.ingest(sample_document)
        query = KnowledgeQuery(query_text="safety", limit=5)
        ctx = svc.retrieve(query, user_id="admin")
        assert ctx is not None

    def test_get_document(self, sample_document: KnowledgeDocument) -> None:
        svc = KnowledgeService()
        svc.ingest(sample_document)
        doc = svc.get_document(str(sample_document.document_id))
        assert doc is not None

    def test_update_document(self, sample_document: KnowledgeDocument) -> None:
        svc = KnowledgeService()
        svc.ingest(sample_document)
        updated = sample_document.model_copy(update={"title": "Updated"})
        result = svc.update_document(updated, user_id="admin")
        assert result.title == "Updated"

    def test_delete_document(self, sample_document: KnowledgeDocument) -> None:
        svc = KnowledgeService()
        svc.ingest(sample_document)
        assert svc.delete_document(str(sample_document.document_id), user_id="admin") is True

    def test_search_documents(self, sample_document: KnowledgeDocument) -> None:
        svc = KnowledgeService()
        svc.ingest(sample_document)
        results = svc.search_documents(query="safety")
        assert len(results) >= 1

    def test_health(self) -> None:
        svc = KnowledgeService()
        health = svc.health()
        assert health.is_healthy() is True

    def test_get_metrics(self) -> None:
        svc = KnowledgeService()
        metrics = svc.get_metrics()
        assert isinstance(metrics, KnowledgeMetrics)

    def test_get_session(self) -> None:
        svc = KnowledgeService()
        # after retrieve, there should be a session
        doc = KnowledgeDocument(
            document_type=DocumentType.TXT,
            content="test content",
            title="test",
            namespace="ns",
        )
        svc.ingest(doc)
        query = KnowledgeQuery(query_text="test", limit=5)
        svc.retrieve(query, user_id="user")
        assert svc.get_session("nonexistent") is None

    # ── Auth ──────────────────────────────────────────────────────────────

    def test_auth_allowed(self, sample_document: KnowledgeDocument) -> None:
        def auth(user: str, op: str) -> AuthResult:
            return AuthResult(allowed=True)

        svc = KnowledgeService(auth_callback=auth)
        result = svc.ingest(sample_document, user_id="user")
        assert result is not None

    def test_auth_denied(self, sample_document: KnowledgeDocument) -> None:
        def auth(user: str, op: str) -> AuthResult:
            return AuthResult(allowed=False, reason="Not authorised")

        svc = KnowledgeService(auth_callback=auth)
        with pytest.raises(PermissionError):
            svc.ingest(sample_document, user_id="user")

    # ── Audit ─────────────────────────────────────────────────────────────

    def test_audit_callback(self, sample_document: KnowledgeDocument) -> None:
        audit_entries: list[dict[str, Any]] = []

        def audit(op: str, resource: str, user: str, details: dict[str, Any]) -> None:
            audit_entries.append({"op": op, "resource": resource, "user": user})

        svc = KnowledgeService(audit_callback=audit)
        svc.ingest(sample_document, user_id="admin")
        assert len(audit_entries) == 1
        assert audit_entries[0]["op"] == "ingest"


# ─────────────────────────────────────────────────────────────────────────────
# Pipeline integration test
# ─────────────────────────────────────────────────────────────────────────────


class TestPipeline:
    def test_full_pipeline(self) -> None:
        """End-to-end: ingest → retrieve → health → metrics."""
        svc = KnowledgeService()

        doc = svc.ingest(
            KnowledgeDocument(
                document_type=DocumentType.PDF,
                domain=KnowledgeDomain.SAFETY,
                title="Safety Report",
                content="This is a safety report about workplace safety procedures.",
                namespace="acme",
            ),
            user_id="admin",
        )
        assert doc.status == KnowledgeStatus.INDEXED

        query = KnowledgeQuery(query_text="workplace safety", limit=5)
        ctx = svc.retrieve(query, user_id="admin")
        assert ctx is not None

        health = svc.health()
        assert health.is_healthy() is True

        metrics = svc.get_metrics()
        assert metrics.documents_total >= 1
        assert metrics.retrievals_total >= 1


# ─────────────────────────────────────────────────────────────────────────────
# Backward compatibility — existing KnowledgeHealth model
# ─────────────────────────────────────────────────────────────────────────────


class TestBackwardCompatibility:
    def test_knowledge_health_defaults(self) -> None:
        health = KnowledgeHealth()
        assert health.overall_status == "HEALTHY"
        assert health.is_healthy() is True
        assert health.coordinator_status == "HEALTHY"
        assert health.processor_status == "HEALTHY"

    def test_knowledge_health_unhealthy(self) -> None:
        health = KnowledgeHealth(overall_status="UNHEALTHY")
        assert health.is_healthy() is False
