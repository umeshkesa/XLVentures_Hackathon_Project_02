"""Reranker — re-ranks retrieval results for improved relevance.

Placeholder implementation using deterministic scoring; no ML/NLP.
"""

from __future__ import annotations

import structlog

from adip.knowledge.contracts.models import KnowledgeResult

log = structlog.get_logger(__name__)


class Reranker:
    """Re-orders retrieval results to improve relevance."""

    def rerank(self, query_text: str, results: list[KnowledgeResult]) -> list[KnowledgeResult]:
        """Re-rank results based on keyword overlap with the query."""
        log.info("reranker.rerank", results=len(results))

        query_keywords = {w for w in query_text.lower().split() if len(w) > 2}
        if not query_keywords or not results:
            return results

        for result in results:
            chunk_text = result.chunk.content.lower()
            overlap = sum(1 for kw in query_keywords if kw in chunk_text)
            boost = overlap / len(query_keywords) * 0.2
            result.score = min(1.0, result.score + boost)

        reranked = sorted(results, key=lambda r: r.score, reverse=True)
        for rank, result in enumerate(reranked):
            result.rank = rank
            result.metadata["reranked"] = True

        log.info("reranker.rerank.complete", results=len(reranked))
        return reranked
