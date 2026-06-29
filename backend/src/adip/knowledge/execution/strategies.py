"""Retrieval Strategy Framework — Strategy pattern for knowledge retrieval.

Defines the abstract RetrievalStrategy base and concrete strategies
for Vector, Keyword, Metadata, Hybrid, and future Graph/Agentic modes.

KnowledgeManager depends only on RetrievalStrategy.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

import structlog

from adip.knowledge.contracts.models import (
    KnowledgeChunk,
    KnowledgeQuery,
    KnowledgeResult,
)
from adip.knowledge.enums import RetrievalType
from adip.knowledge.execution.index_manager import IndexManager
from adip.knowledge.execution.retriever import HybridRetriever

log = structlog.get_logger(__name__)


class RetrievalStrategyResult:
    """Result from a retrieval strategy with explainability."""

    def __init__(
        self,
        results: list[KnowledgeResult],
        strategy: RetrievalType,
        explainability: list[dict[str, str]] | None = None,
    ) -> None:
        self.results = results
        self.strategy = strategy
        self.explainability = explainability or []


class RetrievalStrategy(ABC):
    """Abstract base for all retrieval strategies."""

    @abstractmethod
    def retrieve(
        self,
        query: KnowledgeQuery,
        chunks: list[KnowledgeChunk] | None = None,
    ) -> RetrievalStrategyResult:
        ...

    @abstractmethod
    def get_type(self) -> RetrievalType:
        ...


class VectorRetrievalStrategy(RetrievalStrategy):
    """Retrieve using vector similarity search."""

    def __init__(self, index_manager: IndexManager | None = None) -> None:
        self._retriever = HybridRetriever(index_manager=index_manager or IndexManager())

    def retrieve(
        self,
        query: KnowledgeQuery,
        chunks: list[KnowledgeChunk] | None = None,
    ) -> RetrievalStrategyResult:
        log.info("strategy.vector", query_id=str(query.query_id))
        vector_query = query.model_copy(update={"retrieval_type": RetrievalType.VECTOR})
        results = self._retriever.retrieve(vector_query, chunks)
        explanations = [
            {"why_selected": "Vector similarity match", "strategy_used": "VECTOR"}
            for _ in results
        ]
        return RetrievalStrategyResult(results, RetrievalType.VECTOR, explanations)

    def get_type(self) -> RetrievalType:
        return RetrievalType.VECTOR


class KeywordRetrievalStrategy(RetrievalStrategy):
    """Retrieve using keyword / full-text search."""

    def __init__(self, index_manager: IndexManager | None = None) -> None:
        self._retriever = HybridRetriever(index_manager=index_manager or IndexManager())

    def retrieve(
        self,
        query: KnowledgeQuery,
        chunks: list[KnowledgeChunk] | None = None,
    ) -> RetrievalStrategyResult:
        log.info("strategy.keyword", query_id=str(query.query_id))
        kw_query = query.model_copy(update={"retrieval_type": RetrievalType.KEYWORD})
        results = self._retriever.retrieve(kw_query, chunks)
        explanations = [
            {"why_selected": "Keyword match found", "strategy_used": "KEYWORD"}
            for _ in results
        ]
        return RetrievalStrategyResult(results, RetrievalType.KEYWORD, explanations)

    def get_type(self) -> RetrievalType:
        return RetrievalType.KEYWORD


class MetadataRetrievalStrategy(RetrievalStrategy):
    """Retrieve using metadata filters only."""

    def __init__(self, index_manager: IndexManager | None = None) -> None:
        self._retriever = HybridRetriever(index_manager=index_manager or IndexManager())

    def retrieve(
        self,
        query: KnowledgeQuery,
        chunks: list[KnowledgeChunk] | None = None,
    ) -> RetrievalStrategyResult:
        log.info("strategy.metadata", query_id=str(query.query_id))
        md_query = query.model_copy(update={"retrieval_type": RetrievalType.METADATA})
        results = self._retriever.retrieve(md_query, chunks)
        explanations = [
            {"why_selected": "Metadata filter match", "strategy_used": "METADATA"}
            for _ in results
        ]
        return RetrievalStrategyResult(results, RetrievalType.METADATA, explanations)

    def get_type(self) -> RetrievalType:
        return RetrievalType.METADATA


class HybridRetrievalStrategy(RetrievalStrategy):
    """Retrieve using combined vector + keyword + metadata."""

    def __init__(self, index_manager: IndexManager | None = None) -> None:
        self._retriever = HybridRetriever(index_manager=index_manager or IndexManager())

    def retrieve(
        self,
        query: KnowledgeQuery,
        chunks: list[KnowledgeChunk] | None = None,
    ) -> RetrievalStrategyResult:
        log.info("strategy.hybrid", query_id=str(query.query_id))
        hybrid_query = query.model_copy(update={"retrieval_type": RetrievalType.HYBRID})
        results = self._retriever.retrieve(hybrid_query, chunks)
        explanations = [
            {"why_selected": "Combined vector+keyword+metadata match", "strategy_used": "HYBRID"}
            for _ in results
        ]
        return RetrievalStrategyResult(results, RetrievalType.HYBRID, explanations)

    def get_type(self) -> RetrievalType:
        return RetrievalType.HYBRID


class GraphRetrievalStrategy(RetrievalStrategy):
    """Placeholder for future Graph-based retrieval."""

    def retrieve(
        self,
        query: KnowledgeQuery,
        chunks: list[KnowledgeChunk] | None = None,
    ) -> RetrievalStrategyResult:
        log.warning("strategy.graph.not_implemented")
        return RetrievalStrategyResult([], RetrievalType.HYBRID)

    def get_type(self) -> RetrievalType:
        return RetrievalType.HYBRID


class AgenticRetrievalStrategy(RetrievalStrategy):
    """Placeholder for future Agentic retrieval."""

    def retrieve(
        self,
        query: KnowledgeQuery,
        chunks: list[KnowledgeChunk] | None = None,
    ) -> RetrievalStrategyResult:
        log.warning("strategy.agentic.not_implemented")
        return RetrievalStrategyResult([], RetrievalType.HYBRID)

    def get_type(self) -> RetrievalType:
        return RetrievalType.HYBRID


_STRATEGY_MAP: dict[RetrievalType, type[RetrievalStrategy]] = {
    RetrievalType.VECTOR: VectorRetrievalStrategy,
    RetrievalType.KEYWORD: KeywordRetrievalStrategy,
    RetrievalType.METADATA: MetadataRetrievalStrategy,
    RetrievalType.HYBRID: HybridRetrievalStrategy,
}


def get_strategy(
    retrieval_type: RetrievalType,
    index_manager: IndexManager | None = None,
) -> RetrievalStrategy:
    """Factory: return the appropriate strategy for the given type."""
    cls = _STRATEGY_MAP.get(retrieval_type, HybridRetrievalStrategy)
    return cls(index_manager=index_manager)
