"""DocumentClassifier — classifies knowledge documents into categories.

Maps DocumentType values to human-readable classification labels.
Supports future-ready custom document types.
"""

from __future__ import annotations

import structlog

from adip.knowledge.contracts.models import KnowledgeDocument
from adip.knowledge.enums import DocumentType

log = structlog.get_logger(__name__)


_CLASSIFICATION_MAP: dict[DocumentType, str] = {
    DocumentType.MANUAL: "Manual",
    DocumentType.SOP: "Standard Operating Procedure",
    DocumentType.PLAYBOOK: "Playbook",
    DocumentType.ARTICLE: "Article",
    DocumentType.MEETING_NOTE: "Meeting Note",
    DocumentType.CRM_NOTE: "CRM Note",
    DocumentType.EMAIL: "Email",
    DocumentType.PDF: "PDF Document",
}


class DocumentClassifier:
    """Classifies documents into predefined categories."""

    def classify(self, document: KnowledgeDocument) -> str:
        """Classify a document based on its DocumentType."""
        log.info("classifier.classify", document_id=str(document.document_id), doc_type=document.document_type.value)
        return _CLASSIFICATION_MAP.get(document.document_type, "Report")

    def get_supported_classifications(self) -> list[str]:
        """Return all supported classification labels."""
        return list(_CLASSIFICATION_MAP.values()) + ["Report"]
