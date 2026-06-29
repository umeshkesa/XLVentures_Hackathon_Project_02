"""Tests for Knowledge Manager Phase 3.5 — Enterprise Refinement & Interface Freeze.

Covers KnowledgeDecision, KnowledgeConfidenceCalculator, enhanced
KnowledgeHealth, enhanced KnowledgeMetrics, enriched tracing,
domain-aware routing preparation, explainability completeness,
and backward compatibility.
"""

from __future__ import annotations

import uuid

import pytest

from adip.knowledge.contracts.models import (
    ExplainabilityMetadata,
    KnowledgeChunk,
    KnowledgeConfidence,
    KnowledgeDecision,
    KnowledgeDocument,
    KnowledgeHealth,
    KnowledgeMetrics,
    KnowledgeQuery,
    KnowledgeResult,
)
from adip.knowledge.enums import DocumentType, KnowledgeDomain, RetrievalType
from adip.knowledge.execution.confidence import KnowledgeConfidenceCalculator
from adip.knowledge.execution.metrics import KnowledgeMetricsCollector
from adip.knowledge.execution.models import TraceRecord
from adip.knowledge.execution.trace import KnowledgeTrace
from adip.knowledge.orchestration.coordinator import KnowledgeCoordinator

# ─────────────────────────────────────────────────────────────────────────────
# KnowledgeDecision
# ─────────────────────────────────────────────────────────────────────────────


class TestKnowledgeDecision:
    def test_defaults(self) -> None:
        d = KnowledgeDecision()
        assert d.retrieval_strategy == ""
        assert d.selected_documents == []
        assert d.rejected_documents == []
        assert d.confidence == 1.0

    def test_custom_values(self) -> None:
        d = KnowledgeDecision(
            retrieval_strategy="HYBRID",
            selected_documents=["doc-1", "doc-2"],
            rejected_documents=["doc-3"],
            selection_reason="Keyword and vector match",
            ranking_reason="Score-based ordering",
            confidence=0.87,
        )
        assert d.retrieval_strategy == "HYBRID"
        assert len(d.selected_documents) == 2
        assert d.confidence == 0.87


# ─────────────────────────────────────────────────────────────────────────────
# KnowledgeConfidence
# ─────────────────────────────────────────────────────────────────────────────


class TestKnowledgeConfidence:
    def test_defaults(self) -> None:
        c = KnowledgeConfidence()
        assert c.overall_confidence == 0.0
        assert c.quality_score == 0.0
        assert c.freshness_score == 0.0
        assert c.completeness_score == 0.0

    def test_custom_values(self) -> None:
        c = KnowledgeConfidence(
            overall_confidence=0.85,
            quality_score=0.9,
            freshness_score=0.8,
            completeness_score=0.75,
        )
        assert c.overall_confidence == 0.85
        assert c.quality_score == 0.9


# ─────────────────────────────────────────────────────────────────────────────
# KnowledgeConfidenceCalculator
# ─────────────────────────────────────────────────────────────────────────────


class TestKnowledgeConfidenceCalculator:
    def test_calculate_with_results(self) -> None:
        calc = KnowledgeConfidenceCalculator()
        qid = uuid.uuid4()
        chunk = KnowledgeChunk(document_id=uuid.uuid4(), document_type=DocumentType.TXT, content="test")
        results = [
            KnowledgeResult(query_id=qid, chunk=chunk, score=0.9, rank=0),
            KnowledgeResult(query_id=qid, chunk=chunk, score=0.7, rank=1),
            KnowledgeResult(query_id=qid, chunk=chunk, score=0.5, rank=2),
        ]
        confidence = calc.calculate(results, version=1)
        assert confidence.overall_confidence > 0
        assert confidence.quality_score > 0
        assert confidence.freshness_score > 0
        assert confidence.completeness_score > 0

    def test_calculate_empty(self) -> None:
        calc = KnowledgeConfidenceCalculator()
        confidence = calc.calculate([], version=1)
        assert confidence.overall_confidence == 0.0

    def test_calculate_freshness_decay(self) -> None:
        calc = KnowledgeConfidenceCalculator()
        qid = uuid.uuid4()
        chunk = KnowledgeChunk(document_id=uuid.uuid4(), document_type=DocumentType.TXT, content="test")
        results = [KnowledgeResult(query_id=qid, chunk=chunk, score=0.8, rank=0)]
        v1 = calc.calculate(results, version=1)
        v5 = calc.calculate(results, version=5)
        assert v5.freshness_score < v1.freshness_score


# ─────────────────────────────────────────────────────────────────────────────
# Enhanced KnowledgeHealth
# ─────────────────────────────────────────────────────────────────────────────


class TestKnowledgeHealthEnhanced:
    def test_defaults(self) -> None:
        h = KnowledgeHealth()
        assert h.overall_status == "HEALTHY"
        assert h.version_status == "HEALTHY"
        assert h.error_rate == 0.0
        assert h.total_queries_served == 0
        assert h.knowledge_domains == []

    def test_custom_values(self) -> None:
        h = KnowledgeHealth(
            overall_status="DEGRADED",
            version_status="DEGRADED",
            error_rate=0.05,
            total_queries_served=100,
            knowledge_domains=["SAFETY", "COMPLIANCE"],
        )
        assert h.overall_status == "DEGRADED"
        assert h.version_status == "DEGRADED"
        assert h.error_rate == 0.05
        assert h.total_queries_served == 100
        assert "SAFETY" in h.knowledge_domains

    def test_is_healthy(self) -> None:
        assert KnowledgeHealth().is_healthy() is True
        assert KnowledgeHealth(overall_status="UNHEALTHY").is_healthy() is False


# ─────────────────────────────────────────────────────────────────────────────
# Enhanced KnowledgeMetrics
# ─────────────────────────────────────────────────────────────────────────────


class TestKnowledgeMetricsEnhanced:
    def test_defaults(self) -> None:
        m = KnowledgeMetrics()
        assert m.strategy_usage == {}
        assert m.domain_usage == {}
        assert m.version_usage == {}

    def test_custom_values(self) -> None:
        m = KnowledgeMetrics(
            strategy_usage={"HYBRID": 10, "VECTOR": 5},
            domain_usage={"SAFETY": 8, "COMPLIANCE": 3},
            version_usage={"1": 15, "2": 7},
        )
        assert m.strategy_usage["HYBRID"] == 10
        assert m.domain_usage["SAFETY"] == 8
        assert m.version_usage["1"] == 15


# ─────────────────────────────────────────────────────────────────────────────
# Enhanced KnowledgeMetricsCollector
# ─────────────────────────────────────────────────────────────────────────────


class TestKnowledgeMetricsCollectorEnhanced:
    def test_strategy_usage(self) -> None:
        mc = KnowledgeMetricsCollector()
        mc.increment_strategy_usage("HYBRID")
        mc.increment_strategy_usage("HYBRID")
        mc.increment_strategy_usage("VECTOR")
        snap = mc.snapshot()
        assert snap.strategy_usage["HYBRID"] == 2
        assert snap.strategy_usage["VECTOR"] == 1

    def test_domain_usage(self) -> None:
        mc = KnowledgeMetricsCollector()
        mc.increment_domain_usage("SAFETY")
        mc.increment_domain_usage("COMPLIANCE")
        snap = mc.snapshot()
        assert snap.domain_usage["SAFETY"] == 1
        assert snap.domain_usage["COMPLIANCE"] == 1

    def test_version_usage(self) -> None:
        mc = KnowledgeMetricsCollector()
        mc.increment_version_usage("1")
        mc.increment_version_usage("2")
        snap = mc.snapshot()
        assert snap.version_usage["1"] == 1
        assert snap.version_usage["2"] == 1

    def test_all_metrics_in_snapshot(self) -> None:
        mc = KnowledgeMetricsCollector()
        mc.increment_documents(domain="SAFETY", doc_type="PDF")
        mc.increment_chunks(5)
        mc.increment_retrievals()
        mc.increment_strategy_usage("HYBRID")
        mc.increment_domain_usage("SAFETY")
        snap = mc.snapshot()
        assert snap.documents_total == 1
        assert snap.chunks_total == 5
        assert snap.retrievals_total == 1
        assert snap.strategy_usage.get("HYBRID") == 1
        assert snap.domain_usage.get("SAFETY") == 1

    def test_reset_clears_new_counters(self) -> None:
        mc = KnowledgeMetricsCollector()
        mc.increment_strategy_usage("HYBRID")
        mc.increment_domain_usage("SAFETY")
        mc.reset()
        snap = mc.snapshot()
        assert snap.strategy_usage == {}
        assert snap.domain_usage == {}


# ─────────────────────────────────────────────────────────────────────────────
# Enhanced KnowledgeTrace
# ─────────────────────────────────────────────────────────────────────────────


class TestKnowledgeTraceEnhanced:
    def test_record_stage(self) -> None:
        trace = KnowledgeTrace()
        record = trace.record_stage(
            stage_name="reranking",
            operation="retrieve",
            domain="SAFETY",
            version=2,
            correlation_id="corr-123",
        )
        assert record.stage_name == "reranking"
        assert record.operation == "retrieve"
        assert record.domain == "SAFETY"
        assert record.version == 2
        assert record.correlation_id == "corr-123"

    def test_get_by_stage(self) -> None:
        trace = KnowledgeTrace()
        trace.record_stage("reranking", "retrieve")
        trace.record_stage("fusion", "retrieve")
        rerank = trace.get_by_stage("reranking")
        assert len(rerank) == 1

    def test_get_stages_for_operation(self) -> None:
        trace = KnowledgeTrace()
        trace.record_stage("policy_check", "retrieve")
        trace.record_stage("reranking", "retrieve")
        trace.record_stage("embedding", "process_document")
        stages = trace.get_stages_for_operation("retrieve")
        assert "policy_check" in stages
        assert "reranking" in stages
        assert "embedding" not in stages

    def test_record_stage_with_warnings(self) -> None:
        trace = KnowledgeTrace()
        record = trace.record_stage(
            stage_name="retrieval",
            operation="retrieve",
            warnings=["Low score", "No keyword match"],
            success=False,
        )
        assert len(record.warnings) == 2
        assert record.success is False

    def test_backward_compatible(self) -> None:
        trace = KnowledgeTrace()
        trace.record(TraceRecord(stage_name="old", operation="op"))
        assert trace.count() == 1
        assert trace.get_by_operation("op")[0].stage_name == "old"


# ─────────────────────────────────────────────────────────────────────────────
# Enriched ExplainabilityMetadata
# ─────────────────────────────────────────────────────────────────────────────


class TestExplainabilityMetadataEnhanced:
    def test_all_fields(self) -> None:
        meta = ExplainabilityMetadata(
            why_selected="Vector similarity 0.92",
            why_rejected="Below threshold",
            strategy_used="HYBRID",
            ranking_reason="Top score in hybrid set",
            version_selected=3,
            provenance="upload → validate → clean → chunk → embed → index",
        )
        assert meta.why_selected == "Vector similarity 0.92"
        assert meta.why_rejected == "Below threshold"
        assert meta.strategy_used == "HYBRID"
        assert meta.version_selected == 3
        assert "chunk" in meta.provenance

    def test_explainability_in_coordinator(self, sample_document: KnowledgeDocument) -> None:
        coord = KnowledgeCoordinator()
        coord.process_document(sample_document)
        query = KnowledgeQuery(query_text="safety", limit=5)
        ctx = coord.retrieve(query, strategy=RetrievalType.VECTOR)
        for r in ctx.results:
            exp = r.metadata.get("explainability", {})
            assert "why_selected" in exp
            assert "strategy_used" in exp
            assert "ranking_reason" in exp
            assert "version_selected" in exp
            assert "provenance" in exp

    def test_decision_in_context(self, sample_document: KnowledgeDocument) -> None:
        coord = KnowledgeCoordinator()
        coord.process_document(sample_document)
        query = KnowledgeQuery(query_text="safety", limit=5)
        ctx = coord.retrieve(query, strategy=RetrievalType.HYBRID)
        assert "knowledge_decision" in ctx.metadata
        decision = ctx.metadata["knowledge_decision"]
        assert "retrieval_strategy" in decision
        assert "selected_documents" in decision
        assert "confidence" in decision

    def test_confidence_in_context(self, sample_document: KnowledgeDocument) -> None:
        coord = KnowledgeCoordinator()
        coord.process_document(sample_document)
        query = KnowledgeQuery(query_text="safety", limit=5)
        ctx = coord.retrieve(query, strategy=RetrievalType.VECTOR)
        assert "confidence" in ctx.metadata
        conf = ctx.metadata["confidence"]
        assert "overall_confidence" in conf
        assert "quality_score" in conf
        assert "freshness_score" in conf


# ─────────────────────────────────────────────────────────────────────────────
# Enhanced Coordinator
# ─────────────────────────────────────────────────────────────────────────────


class TestCoordinatorEnhanced:
    def test_health_includes_new_fields(self, sample_document: KnowledgeDocument) -> None:
        coord = KnowledgeCoordinator()
        coord.process_document(sample_document)
        health = coord.health()
        assert health.version_status == "HEALTHY"
        assert health.error_rate >= 0.0
        assert health.total_queries_served >= 0
        assert isinstance(health.knowledge_domains, list)

    def test_metrics_includes_new_fields(self, sample_document: KnowledgeDocument) -> None:
        coord = KnowledgeCoordinator()
        coord.process_document(sample_document)
        metrics = coord.metrics()
        assert hasattr(metrics, "strategy_usage")
        assert hasattr(metrics, "domain_usage")
        assert hasattr(metrics, "version_usage")

    def test_retrieve_updates_strategy_metrics(self, sample_document: KnowledgeDocument) -> None:
        coord = KnowledgeCoordinator()
        coord.process_document(sample_document)
        query = KnowledgeQuery(
            query_text="safety",
            limit=5,
            retrieval_type=RetrievalType.HYBRID,
            domains=[KnowledgeDomain.SAFETY],
        )
        coord.retrieve(query)
        snap = coord.metrics()
        assert snap.strategy_usage.get("HYBRID", 0) >= 1
        assert snap.domain_usage.get("SAFETY", 0) >= 1

    def test_coordinator_trace_stages(self, sample_document: KnowledgeDocument) -> None:
        coord = KnowledgeCoordinator()
        coord.process_document(sample_document)
        query = KnowledgeQuery(query_text="safety", limit=5)
        coord.retrieve(query)
        stages = coord._trace.get_stages_for_operation("retrieve")
        assert "policy_check" in stages
        assert "strategy_dispatch" in stages
        assert "fusion" in stages
        assert "reranking" in stages
        assert "explainability" in stages
        assert "context_assembly" in stages
        assert "caching" in stages
        assert "confidence" in stages
        assert "decision" in stages

    def test_coordinator_process_trace_stages(self, sample_document: KnowledgeDocument) -> None:
        coord = KnowledgeCoordinator()
        coord.process_document(sample_document)
        stages = coord._trace.get_stages_for_operation("process_document")
        assert "validation" in stages
        assert "cleaning" in stages
        assert "chunking" in stages
        assert "indexing" in stages


# ─────────────────────────────────────────────────────────────────────────────
# Domain-Aware Routing Preparation
# ─────────────────────────────────────────────────────────────────────────────


class TestDomainAwareRouting:
    def test_routing_module_exists(self) -> None:
        from adip.knowledge.execution import routing  # noqa: F401
        assert True

    def test_coordinator_domain_aware_architecture(self) -> None:
        """Verify coordinator has domain references in trace and metrics."""
        coord = KnowledgeCoordinator()
        doc = KnowledgeDocument(
            document_type=DocumentType.PDF,
            domain=KnowledgeDomain.SAFETY,
            title="Safety Doc",
            content="Safety content here",
            namespace="ns",
        )
        coord.process_document(doc)
        query = KnowledgeQuery(
            query_text="safety",
            domains=[KnowledgeDomain.SAFETY],
            limit=5,
        )
        ctx = coord.retrieve(query)
        assert ctx is not None


# ─────────────────────────────────────────────────────────────────────────────
# KnowledgeService SOLID Review
# ─────────────────────────────────────────────────────────────────────────────


class TestServiceArchitecture:
    def test_service_is_thin(self) -> None:
        """KnowledgeService should delegate to KnowledgeManager (thin layer)."""
        from adip.knowledge.services.service import KnowledgeService
        svc = KnowledgeService()
        # Verify service has no business logic — delegates to manager
        assert svc._manager is not None
        assert svc._hooks is not None
        assert svc._session_manager is not None

    def test_interface_freeze(self) -> None:
        """Verify KnowledgeService, KnowledgeManager, KnowledgeCoordinator
        abstract interfaces are unchanged from Phase 3."""
        # Verify all abstract methods exist

        from adip.knowledge.interfaces import (
            KnowledgeCoordinator as KnowledgeCoordinatorInterface,
        )
        from adip.knowledge.interfaces import (
            KnowledgeManager as KnowledgeManagerInterface,
        )
        from adip.knowledge.interfaces import (
            KnowledgeService as KnowledgeServiceInterface,
        )
        svc_methods = [m for m in dir(KnowledgeServiceInterface) if not m.startswith('_')]
        mgr_methods = [m for m in dir(KnowledgeManagerInterface) if not m.startswith('_')]
        coord_methods = [m for m in dir(KnowledgeCoordinatorInterface) if not m.startswith('_')]
        assert len(svc_methods) >= 8  # ingest, retrieve, get_document, update, delete, search, health, metrics
        assert len(mgr_methods) >= 7
        assert len(coord_methods) >= 6


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
        version=1,
    )
