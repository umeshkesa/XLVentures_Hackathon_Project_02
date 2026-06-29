"""IndexManager — maintains three logical indexes for knowledge retrieval.

Manages Vector Index, Metadata Index, and Keyword Index with
placeholder operations for create, update, delete, search, and
synchronize.
"""

from __future__ import annotations

import structlog

from adip.knowledge.contracts.models import KnowledgeChunk, KnowledgeDocument, KnowledgeIndex
from adip.knowledge.enums import KnowledgeStatus

log = structlog.get_logger(__name__)


class IndexManager:
    """Manages three logical indexes: vector, metadata, and keyword."""

    def __init__(self) -> None:
        self._vector_index: dict[str, KnowledgeIndex] = {}
        self._metadata_index: dict[str, dict[str, str]] = {}
        self._keyword_index: dict[str, set[str]] = {}

    def index_document(
        self,
        document: KnowledgeDocument,
        chunks: list[KnowledgeChunk],
    ) -> KnowledgeIndex:
        """Index all chunks for a document across all three indexes."""
        log.info("index_manager.index_document", document_id=str(document.document_id))

        index_entry = KnowledgeIndex(
            document_id=document.document_id,
            document_type=document.document_type,
            domain=document.domain,
            provider="placeholder",
            status=KnowledgeStatus.INDEXED,
            chunk_count=len(chunks),
        )
        doc_id_str = str(document.document_id)
        self._vector_index[doc_id_str] = index_entry
        self._metadata_index[doc_id_str] = {
            "title": document.title,
            "domain": document.domain.value,
            "type": document.document_type.value,
            "namespace": document.namespace,
            "owner": document.owner_id,
        }
        keywords: set[str] = set()
        for chunk in chunks:
            for word in chunk.content.split():
                if len(word) > 3:
                    keywords.add(word.lower())
        self._keyword_index[doc_id_str] = keywords

        log.info("index_manager.index_document.complete", document_id=doc_id_str, chunks=len(chunks))
        return index_entry

    def delete_index(self, document_id: str) -> bool:
        """Remove a document's entries from all indexes."""
        log.info("index_manager.delete_index", document_id=document_id)
        found = document_id in self._vector_index
        self._vector_index.pop(document_id, None)
        self._metadata_index.pop(document_id, None)
        self._keyword_index.pop(document_id, None)
        return found

    def get_index_status(self, document_id: str) -> str:
        """Return the indexing status for a document."""
        entry = self._vector_index.get(document_id)
        if entry is None:
            return "NOT_INDEXED"
        return entry.status.value

    def search_vector(self, query: str, limit: int = 10) -> list[str]:
        """Placeholder vector search. Returns all indexed document IDs."""
        return list(self._vector_index.keys())[:limit]

    def search_metadata(self, filters: dict[str, str], limit: int = 10) -> list[str]:
        """Search the metadata index for documents matching filters."""
        results: list[str] = []
        for doc_id, meta in self._metadata_index.items():
            if all(meta.get(k) == v for k, v in filters.items()):
                results.append(doc_id)
        return results[:limit]

    def search_keyword(self, keywords: list[str], limit: int = 10) -> list[str]:
        """Search the keyword index for documents containing keywords."""
        results: list[str] = []
        kw_lower = {k.lower() for k in keywords}
        for doc_id, doc_keywords in self._keyword_index.items():
            if kw_lower & doc_keywords:
                results.append(doc_id)
        return results[:limit]

    def clear(self) -> None:
        """Clear all indexes."""
        self._vector_index.clear()
        self._metadata_index.clear()
        self._keyword_index.clear()

    @property
    def indexed_count(self) -> int:
        """Return the number of indexed documents."""
        return len(self._vector_index)
