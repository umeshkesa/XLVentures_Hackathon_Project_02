"""DocumentCleaner — cleans document content before processing.

Supports whitespace cleanup, encoding normalisation, header/footer
removal, and noise removal. All operations are placeholder-only.
"""

from __future__ import annotations

import structlog

from adip.knowledge.contracts.models import KnowledgeDocument

log = structlog.get_logger(__name__)


class DocumentCleaner:
    """Cleans document text content."""

    def clean(self, content: str) -> str:
        """Clean a string of text content."""
        log.info("cleaner.clean")
        result = content.strip()
        result = result.replace("\r\n", "\n").replace("\r", "\n")
        result = result.replace("\x00", "")
        return result

    def clean_document(self, document: KnowledgeDocument) -> KnowledgeDocument:
        """Return a copy of the document with cleaned content."""
        log.info("cleaner.clean_document", document_id=str(document.document_id))
        cleaned = self.clean(document.content)
        return document.model_copy(update={"content": cleaned}, deep=True)
