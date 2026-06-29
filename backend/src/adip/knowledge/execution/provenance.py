"""KnowledgeProvenanceManager — tracks document provenance.

Records origin, source type, import details, processing pipeline,
version used, and confidence for every document to support
explainability and audit.
"""

from __future__ import annotations

import structlog

from adip.knowledge.contracts.models import KnowledgeDocument, KnowledgeProvenance

log = structlog.get_logger(__name__)


class KnowledgeProvenanceManager:
    """Manages provenance records for knowledge documents."""

    def __init__(self) -> None:
        self._records: dict[str, KnowledgeProvenance] = {}

    def record_provenance(
        self,
        document: KnowledgeDocument,
        source_document: str = "",
        source_type: str = "",
        imported_by: str = "",
        processing_pipeline: list[str] | None = None,
    ) -> KnowledgeProvenance:
        """Create a provenance record for a document."""
        doc_id = str(document.document_id)
        log.info("provenance.record", document_id=doc_id)

        provenance = KnowledgeProvenance(
            document_id=document.document_id,
            source_document=source_document or document.source,
            source_type=source_type or "upload",
            imported_by=imported_by or document.owner_id,
            processing_pipeline=processing_pipeline or [],
            version_used=document.version,
            confidence=1.0,
            metadata={"title": document.title, "domain": document.domain.value},
        )
        self._records[doc_id] = provenance
        log.info("provenance.record.complete", document_id=doc_id)
        return provenance

    def get_provenance(self, document_id: str) -> KnowledgeProvenance | None:
        """Retrieve the provenance record for a document."""
        return self._records.get(document_id)

    def update_confidence(self, document_id: str, confidence: float) -> bool:
        """Update the confidence score for a document's provenance."""
        record = self._records.get(document_id)
        if record is None:
            return False
        record.confidence = max(0.0, min(1.0, confidence))
        return True

    def add_pipeline_stage(self, document_id: str, stage: str) -> bool:
        """Append a processing stage to the provenance pipeline."""
        record = self._records.get(document_id)
        if record is None:
            return False
        record.processing_pipeline.append(stage)
        return True

    def clear(self) -> None:
        """Clear all provenance records."""
        self._records.clear()
