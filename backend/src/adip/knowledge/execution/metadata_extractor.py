"""MetadataExtractor — extracts structured metadata from documents.

Provides deterministic placeholder extraction for title, author,
created date, department, knowledge domain, version, tags, and
language.
"""

from __future__ import annotations

from typing import Any

import structlog

from adip.knowledge.contracts.models import KnowledgeDocument

log = structlog.get_logger(__name__)


class MetadataExtractor:
    """Extracts placeholder metadata from knowledge documents."""

    def extract(self, document: KnowledgeDocument) -> dict[str, Any]:
        """Extract placeholder metadata from a document."""
        log.info("metadata_extractor.extract", document_id=str(document.document_id))

        return {
            "title": document.title,
            "author": "extracted-author",
            "created_date": document.metadata.created_date or "unknown",
            "department": "extracted-department",
            "knowledge_domain": document.domain.value,
            "version": str(document.version),
            "tags": list(document.tags),
            "language": document.metadata.language or "en",
            "source": document.source,
            "file_size": document.metadata.file_size,
        }

    def extract_batch(self, documents: list[KnowledgeDocument]) -> list[dict[str, Any]]:
        """Extract metadata from a batch of documents."""
        log.info("metadata_extractor.extract_batch", count=len(documents))
        return [self.extract(doc) for doc in documents]
