"""OCRProcessor — placeholder OCR processor for image-based documents.

Future support for images, scanned PDFs, and handwritten notes.
Currently returns documents unchanged with a warning log.
"""

from __future__ import annotations

import structlog

from adip.knowledge.contracts.models import KnowledgeDocument
from adip.knowledge.enums import DocumentType

log = structlog.get_logger(__name__)


class OCRProcessor:
    """Placeholder OCR processor. No actual OCR is performed."""

    def process(self, document: KnowledgeDocument) -> KnowledgeDocument:
        """Placeholder: log a warning and return the document unchanged."""
        log.warning("ocr.process.not_implemented", document_id=str(document.document_id))
        return document

    def is_supported(self, document_type: DocumentType) -> bool:
        """Return True if OCR is supported for the given document type."""
        return document_type == DocumentType.PDF
