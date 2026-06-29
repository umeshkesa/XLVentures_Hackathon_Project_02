"""KnowledgeMetrics — collects and exposes knowledge manager metrics.

Provides counters and timing for documents, chunks, embeddings,
retrievals, indexing, cache, strategy usage, domain usage, version
usage, and latency tracking.
"""

from __future__ import annotations

import structlog

from adip.knowledge.contracts.models import KnowledgeMetrics

log = structlog.get_logger(__name__)


class KnowledgeMetricsCollector:
    """Collects operational metrics for the knowledge manager."""

    def __init__(self) -> None:
        self._documents_total: int = 0
        self._chunks_total: int = 0
        self._embeddings_total: int = 0
        self._retrievals_total: int = 0
        self._indexed_total: int = 0
        self._failed_total: int = 0
        self._cache_hits: int = 0
        self._cache_misses: int = 0
        self._documents_per_domain: dict[str, int] = {}
        self._documents_per_type: dict[str, int] = {}
        self._indexing_times: list[float] = []
        self._retrieval_times: list[float] = []
        self._strategy_usage: dict[str, int] = {}
        self._domain_usage: dict[str, int] = {}
        self._version_usage: dict[str, int] = {}

    def increment_documents(self, domain: str = "", doc_type: str = "") -> None:
        self._documents_total += 1
        if domain:
            self._documents_per_domain[domain] = self._documents_per_domain.get(domain, 0) + 1
        if doc_type:
            self._documents_per_type[doc_type] = self._documents_per_type.get(doc_type, 0) + 1

    def increment_chunks(self, count: int = 1) -> None:
        self._chunks_total += count

    def increment_embeddings(self, count: int = 1) -> None:
        self._embeddings_total += count

    def increment_retrievals(self) -> None:
        self._retrievals_total += 1

    def increment_indexed(self) -> None:
        self._indexed_total += 1

    def increment_failed(self) -> None:
        self._failed_total += 1

    def increment_cache_hits(self) -> None:
        self._cache_hits += 1

    def increment_cache_misses(self) -> None:
        self._cache_misses += 1

    def record_indexing_time(self, time_ms: float) -> None:
        self._indexing_times.append(time_ms)

    def record_retrieval_time(self, time_ms: float) -> None:
        self._retrieval_times.append(time_ms)

    def increment_strategy_usage(self, strategy: str) -> None:
        """Increment usage counter for a retrieval strategy."""
        self._strategy_usage[strategy] = self._strategy_usage.get(strategy, 0) + 1

    def increment_domain_usage(self, domain: str) -> None:
        """Increment usage counter for a knowledge domain."""
        self._domain_usage[domain] = self._domain_usage.get(domain, 0) + 1

    def increment_version_usage(self, version: str) -> None:
        """Increment usage counter for a document version."""
        self._version_usage[version] = self._version_usage.get(version, 0) + 1

    def snapshot(self) -> KnowledgeMetrics:
        """Take a point-in-time snapshot of all metrics."""
        avg_idx = (
            sum(self._indexing_times) / len(self._indexing_times)
            if self._indexing_times
            else 0.0
        )
        avg_ret = (
            sum(self._retrieval_times) / len(self._retrieval_times)
            if self._retrieval_times
            else 0.0
        )

        return KnowledgeMetrics(
            documents_total=self._documents_total,
            chunks_total=self._chunks_total,
            embeddings_total=self._embeddings_total,
            retrievals_total=self._retrievals_total,
            indexed_total=self._indexed_total,
            failed_total=self._failed_total,
            cache_hits=self._cache_hits,
            cache_misses=self._cache_misses,
            documents_per_domain=dict(self._documents_per_domain),
            documents_per_type=dict(self._documents_per_type),
            average_indexing_time_ms=round(avg_idx, 2),
            average_retrieval_time_ms=round(avg_ret, 2),
            strategy_usage=dict(self._strategy_usage),
            domain_usage=dict(self._domain_usage),
            version_usage=dict(self._version_usage),
        )

    def reset(self) -> None:
        """Reset all metrics to zero."""
        self._documents_total = 0
        self._chunks_total = 0
        self._embeddings_total = 0
        self._retrievals_total = 0
        self._indexed_total = 0
        self._failed_total = 0
        self._cache_hits = 0
        self._cache_misses = 0
        self._documents_per_domain.clear()
        self._documents_per_type.clear()
        self._indexing_times.clear()
        self._retrieval_times.clear()
        self._strategy_usage.clear()
        self._domain_usage.clear()
        self._version_usage.clear()
