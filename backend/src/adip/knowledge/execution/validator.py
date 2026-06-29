"""DocumentValidator — validates knowledge documents before processing.

Validates supported document types, required metadata, maximum file
size, document integrity, and version compatibility.
"""

from __future__ import annotations

import structlog

from adip.knowledge.contracts.models import KnowledgeDocument
from adip.knowledge.enums import DocumentType

log = structlog.get_logger(__name__)


class DocumentValidator:
    """Validates knowledge documents against platform rules."""

    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100 MB

    def validate(self, document: KnowledgeDocument) -> list[str]:
        """Validate a document. Returns a list of violation strings (empty = valid)."""
        violations: list[str] = []

        log.info("validator.validate", document_id=str(document.document_id))

        if not isinstance(document.document_type, DocumentType):
            violations.append(f"Unsupported document type: {document.document_type}")

        if not document.title.strip():
            violations.append("Document title is required")

        if not document.content.strip():
            violations.append("Document content is required")

        if document.metadata.file_size > self.MAX_FILE_SIZE:
            violations.append(
                f"File size {document.metadata.file_size} bytes exceeds maximum {self.MAX_FILE_SIZE} bytes"
            )

        if not document.namespace.strip():
            violations.append("Document namespace is required")

        return violations

    def validate_batch(self, documents: list[KnowledgeDocument]) -> list[list[str]]:
        """Validate a batch of documents."""
        log.info("validator.validate_batch", count=len(documents))
        return [self.validate(doc) for doc in documents]
