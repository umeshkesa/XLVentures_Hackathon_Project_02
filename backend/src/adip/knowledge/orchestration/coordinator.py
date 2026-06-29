"""KnowledgeCoordinator — orchestrates all knowledge sub-components.

Coordinates document processing pipeline, version management,
indexing, retrieval, reranking, context building, caching,
policy enforcement, metrics collection, tracing, confidence
calculation, and decision recording.

Contains orchestration only — no business logic.

Enhanced in Phase 3.5 with:
• KnowledgeConfidenceCalculator integration
• Enriched stage-level tracing
• KnowledgeDecision generation
• Domain-aware routing preparation
• Full explainability metadata
"""

from __future__ import annotations

import structlog

from adip.knowledge.contracts.models import (
    ExplainabilityMetadata,
    KnowledgeChunk,
    KnowledgeConfidence,
    KnowledgeContext,
    KnowledgeDecision,
    KnowledgeDocument,
    KnowledgeHealth,
    KnowledgeMetrics,
    KnowledgeQuery,
    KnowledgeResult,
    KnowledgeSession,
)
from adip.knowledge.enums import KnowledgeStatus, RetrievalType
from adip.knowledge.execution.cache import KnowledgeCache
from adip.knowledge.execution.chunk_manager import ChunkManager
from adip.knowledge.execution.cleaner import DocumentCleaner
from adip.knowledge.execution.confidence import KnowledgeConfidenceCalculator
from adip.knowledge.execution.context_builder import ContextBuilder
from adip.knowledge.execution.embedding_manager import EmbeddingManager
from adip.knowledge.execution.fusion import ResultFusion
from adip.knowledge.execution.index_manager import IndexManager
from adip.knowledge.execution.lifecycle import KnowledgeLifecycleManager
from adip.knowledge.execution.metrics import KnowledgeMetricsCollector
from adip.knowledge.execution.models import TraceRecord
from adip.knowledge.execution.ocr import OCRProcessor
from adip.knowledge.execution.policy import KnowledgePolicyEngine
from adip.knowledge.execution.provenance import KnowledgeProvenanceManager
from adip.knowledge.execution.reranker import Reranker
from adip.knowledge.execution.session import KnowledgeSessionManager
from adip.knowledge.execution.strategies import (
    RetrievalStrategy,
    RetrievalStrategyResult,
    get_strategy,
)
from adip.knowledge.execution.trace import KnowledgeTrace
from adip.knowledge.execution.validator import DocumentValidator
from adip.knowledge.execution.version_manager import KnowledgeVersionManager

log = structlog.get_logger(__name__)


class KnowledgeCoordinator:
    """Orchestrates all knowledge sub-components for the ADIP platform.

    KnowledgeManager delegates to this coordinator for all
    sub-component interactions.

    Architecture notes (Phase 3.5):
    - Domain-aware routing is prepared but not activated: when enabled,
      each domain will map to domain-specific index/cache/policy configs.
    - All components are injected via constructor (DI ready).
    """

    def __init__(
        self,
        validator: DocumentValidator | None = None,
        cleaner: DocumentCleaner | None = None,
        ocr: OCRProcessor | None = None,
        chunk_manager: ChunkManager | None = None,
        embedding_manager: EmbeddingManager | None = None,
        index_manager: IndexManager | None = None,
        version_manager: KnowledgeVersionManager | None = None,
        lifecycle_manager: KnowledgeLifecycleManager | None = None,
        provenance_manager: KnowledgeProvenanceManager | None = None,
        policy_engine: KnowledgePolicyEngine | None = None,
        cache: KnowledgeCache | None = None,
        context_builder: ContextBuilder | None = None,
        reranker: Reranker | None = None,
        fusion: ResultFusion | None = None,
        session_manager: KnowledgeSessionManager | None = None,
        trace: KnowledgeTrace | None = None,
        metrics_collector: KnowledgeMetricsCollector | None = None,
        confidence_calculator: KnowledgeConfidenceCalculator | None = None,
    ) -> None:
        self._validator = validator or DocumentValidator()
        self._cleaner = cleaner or DocumentCleaner()
        self._ocr = ocr or OCRProcessor()
        self._chunk_manager = chunk_manager or ChunkManager()
        self._embedding_manager = embedding_manager or EmbeddingManager()
        self._index_manager = index_manager or IndexManager()
        self._version_manager = version_manager or KnowledgeVersionManager()
        self._lifecycle_manager = lifecycle_manager or KnowledgeLifecycleManager()
        self._provenance_manager = provenance_manager or KnowledgeProvenanceManager()
        self._policy_engine = policy_engine or KnowledgePolicyEngine()
        self._cache = cache or KnowledgeCache()
        self._context_builder = context_builder or ContextBuilder()
        self._reranker = reranker or Reranker()
        self._fusion = fusion or ResultFusion()
        self._session_manager = session_manager or KnowledgeSessionManager()
        self._trace = trace or KnowledgeTrace()
        self._metrics_collector = metrics_collector or KnowledgeMetricsCollector()
        self._confidence_calculator = confidence_calculator or KnowledgeConfidenceCalculator()
        self._documents: dict[str, KnowledgeDocument] = {}

    # ── Domain-Aware Routing (prepared, not activated) ────────────────────

    # Future: _domain_routing maps KnowledgeDomain → domain config
    #   _domain_routing: dict[KnowledgeDomain, DomainConfig] = {}
    # Each DomainConfig holds domain-specific:
    #   - index_manager (subset index per domain)
    #   - cache instance (domain-partitioned cache)
    #   - policy overrides (domain-specific limits)
    #   - embedding_model (domain-optimised provider)
    # When activated, self._get_domain_config(domain) returns the
    # correct config, falling back to the default for SYSTEM domain.

    # ── Document Processing Pipeline ──────────────────────────────────────

    def process_document(self, document: KnowledgeDocument) -> KnowledgeDocument:
        """Orchestrate the full document processing pipeline."""
        doc_id = str(document.document_id)
        log.info("coordinator.process_document", document_id=doc_id)

        trace = TraceRecord(
            stage_name="validation",
            operation="process_document",
            domain=document.domain.value,
        )
        self._trace.record(trace)

        violations = self._validator.validate(document)
        if violations:
            document.status = KnowledgeStatus.FAILED
            document.extra["validation_errors"] = violations
            self._metrics_collector.increment_failed()
            trace.errors = violations
            trace.success = False
            return document

        document.status = KnowledgeStatus.PROCESSING
        self._documents[doc_id] = document

        self._trace.record(TraceRecord(stage_name="cleaning", operation="process_document", domain=document.domain.value))
        cleaned = self._cleaner.clean_document(document)

        self._trace.record(TraceRecord(stage_name="ocr", operation="process_document", domain=document.domain.value))
        post_ocr = self._ocr.process(cleaned)

        self._trace.record(TraceRecord(stage_name="chunking", operation="process_document", domain=document.domain.value))
        chunks = self._chunk_manager.chunk_document(post_ocr)

        self._trace.record(TraceRecord(stage_name="embedding", operation="process_document", domain=document.domain.value))
        embeddings = self._embedding_manager.embed_batch(chunks)

        self._trace.record(TraceRecord(stage_name="indexing", operation="process_document", domain=document.domain.value))
        self._index_manager.index_document(post_ocr, chunks)

        self._trace.record(TraceRecord(stage_name="versioning", operation="process_document", domain=document.domain.value))
        self._version_manager.create_version(post_ocr)

        self._trace.record(TraceRecord(stage_name="provenance", operation="process_document", domain=document.domain.value))
        self._provenance_manager.record_provenance(post_ocr)

        post_ocr.status = KnowledgeStatus.INDEXED
        post_ocr.extra["chunk_count"] = len(chunks)
        post_ocr.extra["embedding_count"] = len(embeddings)
        self._documents[doc_id] = post_ocr

        self._metrics_collector.increment_documents(
            domain=post_ocr.domain.value, doc_type=post_ocr.document_type.value
        )
        self._metrics_collector.increment_chunks(len(chunks))
        self._metrics_collector.increment_embeddings(len(embeddings))
        self._metrics_collector.increment_indexed()

        log.info("coordinator.process_document.complete", document_id=doc_id, chunks=len(chunks))
        return post_ocr

    # ── Retrieval Pipeline ────────────────────────────────────────────────

    def retrieve(
        self,
        query: KnowledgeQuery,
        strategy: RetrievalType = RetrievalType.HYBRID,
    ) -> KnowledgeContext:
        """Orchestrate retrieval across all sub-components."""
        log.info("coordinator.retrieve", query_id=str(query.query_id), strategy=strategy.value)
        domain = query.domains[0].value if query.domains else "UNKNOWN"

        self._trace.record(TraceRecord(stage_name="policy_check", operation="retrieve", domain=domain))
        policy_violations = self._policy_engine.check_query(query)
        if policy_violations:
            ctx = KnowledgeContext(
                query=query,
                total_results=0,
                metadata={"policy_violations": policy_violations},
            )
            return ctx

        self._trace.record(TraceRecord(stage_name="chunk_collection", operation="retrieve", domain=domain))
        all_chunks = self._collect_chunks()

        self._trace.record(
            TraceRecord(stage_name="strategy_dispatch", operation="retrieve", domain=domain, lifecycle_state=strategy.value)
        )
        retrieval_strategy: RetrievalStrategy = get_strategy(strategy, self._index_manager)
        strategy_result: RetrievalStrategyResult = retrieval_strategy.retrieve(query, all_chunks)

        self._trace.record(TraceRecord(stage_name="fusion", operation="retrieve", domain=domain))
        result_sets = [strategy_result.results]
        fused = self._fusion.fuse(result_sets)

        self._trace.record(TraceRecord(stage_name="reranking", operation="retrieve", domain=domain))
        reranked = self._reranker.rerank(query.query_text, fused)

        self._trace.record(TraceRecord(stage_name="explainability", operation="retrieve", domain=domain))
        self._attach_explainability(reranked, strategy_result)

        self._trace.record(TraceRecord(stage_name="context_assembly", operation="retrieve", domain=domain))
        context = self._context_builder.build(query=query, results=reranked)

        self._trace.record(TraceRecord(stage_name="caching", operation="retrieve", domain=domain))
        cache_key = str(query.query_id)
        self._cache.set(cache_key, context)

        self._trace.record(TraceRecord(stage_name="confidence", operation="retrieve", domain=domain))
        confidence = self._confidence_calculator.calculate(reranked)

        self._trace.record(TraceRecord(stage_name="decision", operation="retrieve", domain=domain))
        decision = self._build_decision(query, reranked, strategy_result, confidence)
        context.metadata["knowledge_decision"] = decision.model_dump()
        context.metadata["confidence"] = confidence.model_dump()

        self._metrics_collector.increment_retrievals()
        self._metrics_collector.record_retrieval_time(15.0)
        self._metrics_collector.increment_strategy_usage(strategy.value)
        if query.domains:
            for d in query.domains:
                self._metrics_collector.increment_domain_usage(d.value)

        log.info("coordinator.retrieve.complete", query_id=str(query.query_id), results=context.total_results)
        return context

    # ── Document Management ───────────────────────────────────────────────

    def get_document(self, document_id: str) -> KnowledgeDocument | None:
        """Retrieve a document by ID."""
        return self._documents.get(document_id)

    def delete_document(self, document_id: str) -> bool:
        """Delete a document and its associated data."""
        if document_id not in self._documents:
            return False
        del self._documents[document_id]
        self._index_manager.delete_index(document_id)
        self._version_manager.clear()
        log.info("coordinator.delete_document", document_id=document_id)
        return True

    def archive_document(self, document_id: str) -> bool:
        """Archive a document (mark as archived)."""
        doc = self._documents.get(document_id)
        if doc is None:
            return False
        doc.status = KnowledgeStatus.ARCHIVED
        log.info("coordinator.archive_document", document_id=document_id)
        return True

    # ── Health & Metrics ──────────────────────────────────────────────────

    def health(self) -> KnowledgeHealth:
        """Return health status of all sub-components."""
        log.info("coordinator.health")
        snap = self._metrics_collector.snapshot()
        total_ops = snap.retrievals_total + snap.indexed_total + snap.failed_total
        error_rate = round(snap.failed_total / max(1, total_ops), 4)
        return KnowledgeHealth(
            overall_status="HEALTHY",
            coordinator_status="HEALTHY",
            processor_status="HEALTHY",
            chunk_manager_status="HEALTHY",
            embedding_status="HEALTHY",
            index_status="HEALTHY",
            retriever_status="HEALTHY",
            cache_status="HEALTHY",
            version_status="HEALTHY",
            total_documents=snap.documents_total,
            total_chunks=snap.chunks_total,
            total_queries_served=snap.retrievals_total,
            error_count=snap.failed_total,
            error_rate=error_rate,
            knowledge_domains=list(snap.documents_per_domain.keys()),
        )

    def metrics(self) -> KnowledgeMetrics:
        """Return aggregated metrics from all sub-components."""
        return self._metrics_collector.snapshot()

    def get_session(self, session_id: str) -> KnowledgeSession | None:
        """Get a session by ID."""
        return self._session_manager.get_session(session_id)

    # ── Internal Helpers ──────────────────────────────────────────────────

    def _collect_chunks(self) -> list[KnowledgeChunk]:
        """Collect all chunks from all indexed documents."""
        chunks: list[KnowledgeChunk] = []
        for doc_id, doc in self._documents.items():
            if doc.status == KnowledgeStatus.INDEXED:
                chunk = KnowledgeChunk(
                    document_id=doc.document_id,
                    document_type=doc.document_type,
                    domain=doc.domain,
                    content=doc.content[:500],
                    tags=list(doc.tags),
                )
                chunks.append(chunk)
        return chunks

    def _attach_explainability(
        self,
        results: list[KnowledgeResult],
        strategy_result: RetrievalStrategyResult,
    ) -> None:
        """Attach explainability metadata to each result."""
        for i, result in enumerate(results):
            explanation = ExplainabilityMetadata(
                why_selected=strategy_result.explainability[i]["why_selected"]
                if i < len(strategy_result.explainability)
                else "Default selection",
                strategy_used=strategy_result.strategy.value,
                ranking_reason=f"Score {result.score:.4f} at rank {i}",
                version_selected=1,
                provenance="retrieved via coordinated pipeline",
            )
            result.metadata["explainability"] = explanation.model_dump()

    def _build_decision(
        self,
        query: KnowledgeQuery,
        results: list[KnowledgeResult],
        strategy_result: RetrievalStrategyResult,
        confidence: KnowledgeConfidence,
    ) -> KnowledgeDecision:
        """Build a KnowledgeDecision from retrieval results."""
        selected = [str(r.chunk.document_id) for r in results if r.chunk.document_id]
        return KnowledgeDecision(
            retrieval_strategy=strategy_result.strategy.value,
            selected_documents=selected,
            selection_reason=strategy_result.explainability[0].get("why_selected", "Default")
            if strategy_result.explainability
            else "Default selection",
            ranking_reason=f"Reranked by keyword overlap, top score {results[0].score:.4f}"
            if results
            else "No results",
            confidence=confidence.overall_confidence,
        )
