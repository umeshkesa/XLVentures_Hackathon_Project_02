"""HybridRetriever — retrieves knowledge using multiple strategies.

Supports vector, metadata, keyword, and hybrid retrieval strategies.
Merges results from all available indexes with proper version handling.
"""

from __future__ import annotations

import structlog

from adip.knowledge.contracts.models import KnowledgeChunk, KnowledgeQuery, KnowledgeResult
from adip.knowledge.enums import RetrievalType
from adip.knowledge.execution.index_manager import IndexManager

log = structlog.get_logger(__name__)


class HybridRetriever:
    """Retrieves knowledge chunks using configurable strategies."""

    def __init__(self, index_manager: IndexManager | None = None) -> None:
        self._index_manager = index_manager or IndexManager()
        self._chunks: dict[str, list[KnowledgeChunk]] = {}

    def register_chunks(self, chunks: list[KnowledgeChunk]) -> None:
        """Register chunks for retrieval lookups."""
        for chunk in chunks:
            doc_id = str(chunk.document_id)
            self._chunks.setdefault(doc_id, []).append(chunk)

    def retrieve(
        self,
        query: KnowledgeQuery,
        chunks: list[KnowledgeChunk] | None = None,
    ) -> list[KnowledgeResult]:
        """Retrieve knowledge matching the query across all indexes."""
        log.info("retriever.retrieve", query_id=str(query.query_id))

        if chunks is not None:
            self._chunks.clear()
            self.register_chunks(chunks)

        retrieval_type = query.retrieval_type
        document_ids: list[str] = []

        if retrieval_type in (RetrievalType.VECTOR, RetrievalType.HYBRID):
            vector_ids = self._index_manager.search_vector(query.query_text, query.limit)
            document_ids.extend(vector_ids)

        if retrieval_type in (RetrievalType.KEYWORD, RetrievalType.HYBRID):
            keywords = [w for w in query.query_text.split() if len(w) > 2]
            if keywords:
                keyword_ids = self._index_manager.search_keyword(keywords, query.limit)
                document_ids.extend(keyword_ids)

        if retrieval_type in (RetrievalType.METADATA, RetrievalType.HYBRID):
            filters = {}
            if query.namespace:
                filters["namespace"] = query.namespace
            if query.owner_id:
                filters["owner"] = query.owner_id
            if filters:
                metadata_ids = self._index_manager.search_metadata(filters, query.limit)
                document_ids.extend(metadata_ids)

        seen: set[str] = set()
        unique_ids: list[str] = []
        for doc_id in document_ids:
            if doc_id not in seen:
                seen.add(doc_id)
                unique_ids.append(doc_id)

        results: list[KnowledgeResult] = []
        for rank, doc_id in enumerate(unique_ids[: query.limit]):
            doc_chunks = self._chunks.get(doc_id, [])
            for chunk in doc_chunks[:1]:
                score = max(0.0, 1.0 - (rank * 0.1))
                if score >= query.min_score:
                    result = KnowledgeResult(
                        query_id=query.query_id,
                        chunk=chunk,
                        score=round(score, 4),
                        rank=rank,
                        metadata={"retrieval_type": retrieval_type.value},
                    )
                    results.append(result)

        log.info("retriever.retrieve.complete", query_id=str(query.query_id), results=len(results))
        return results

    def get_supported_retrieval_types(self) -> list[RetrievalType]:
        """Return the retrieval types this retriever supports."""
        return list(RetrievalType)
