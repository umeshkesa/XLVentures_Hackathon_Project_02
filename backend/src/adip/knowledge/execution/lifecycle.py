"""KnowledgeLifecycleManager — manages document lifecycle transitions.

Validates lifecycle transitions according to allowed state machine
rules and tracks lifecycle history for audit and observability.
"""

from __future__ import annotations

import structlog

from adip.knowledge.contracts.models import KnowledgeDocument
from adip.knowledge.enums import KnowledgeLifecycleStatus
from adip.knowledge.execution.models import LifecycleHistoryEntry

log = structlog.get_logger(__name__)


_ALLOWED_TRANSITIONS: dict[KnowledgeLifecycleStatus, set[KnowledgeLifecycleStatus]] = {
    KnowledgeLifecycleStatus.DRAFT: {KnowledgeLifecycleStatus.UNDER_REVIEW},
    KnowledgeLifecycleStatus.UNDER_REVIEW: {KnowledgeLifecycleStatus.APPROVED, KnowledgeLifecycleStatus.DRAFT},
    KnowledgeLifecycleStatus.APPROVED: {KnowledgeLifecycleStatus.PUBLISHED, KnowledgeLifecycleStatus.DRAFT},
    KnowledgeLifecycleStatus.PUBLISHED: {KnowledgeLifecycleStatus.DEPRECATED, KnowledgeLifecycleStatus.ARCHIVED},
    KnowledgeLifecycleStatus.DEPRECATED: {KnowledgeLifecycleStatus.ARCHIVED},
    KnowledgeLifecycleStatus.ARCHIVED: set(),
}


class KnowledgeLifecycleManager:
    """Manages knowledge document lifecycle transitions."""

    def __init__(self) -> None:
        self._history: list[LifecycleHistoryEntry] = []

    def get_current_status(self, document: KnowledgeDocument) -> KnowledgeLifecycleStatus:
        """Return the current lifecycle status from document metadata."""
        raw = document.metadata.extra.get("lifecycle_status", "DRAFT")
        try:
            return KnowledgeLifecycleStatus(raw)
        except ValueError:
            return KnowledgeLifecycleStatus.DRAFT

    def transition(
        self,
        document: KnowledgeDocument,
        to_status: KnowledgeLifecycleStatus,
        reason: str = "",
        changed_by: str = "",
    ) -> KnowledgeDocument:
        """Transition a document to a new lifecycle status.

        Validates the transition before applying. Returns an updated
        document copy with the new status in metadata.
        """
        doc_id = str(document.document_id)
        from_status = self.get_current_status(document)

        log.info(
            "lifecycle.transition",
            document_id=doc_id,
            from_status=from_status.value,
            to_status=to_status.value,
        )

        if to_status == from_status:
            return document

        allowed = _ALLOWED_TRANSITIONS.get(from_status, set())
        if to_status not in allowed:
            raise ValueError(
                f"Illegal lifecycle transition: {from_status.value} → {to_status.value} "
                f"for document {doc_id}"
            )

        entry = LifecycleHistoryEntry(
            document_id=document.document_id,
            from_status=from_status,
            to_status=to_status,
            reason=reason or f"Transitioned from {from_status.value} to {to_status.value}",
            changed_by=changed_by,
        )
        self._history.append(entry)
        extra = dict(document.metadata.extra)
        extra["lifecycle_status"] = to_status.value
        updated_meta = document.metadata.model_copy(update={"extra": extra})
        result = document.model_copy(update={"metadata": updated_meta})
        log.info("lifecycle.transition.complete", document_id=doc_id, to_status=to_status.value)
        return result

    def get_history(self, document_id: str) -> list[LifecycleHistoryEntry]:
        """Return lifecycle history for a specific document."""
        return [e for e in self._history if str(e.document_id) == document_id]

    def get_all_history(self) -> list[LifecycleHistoryEntry]:
        """Return all lifecycle history entries."""
        return list(self._history)

    def clear(self) -> None:
        """Clear all lifecycle history."""
        self._history.clear()
