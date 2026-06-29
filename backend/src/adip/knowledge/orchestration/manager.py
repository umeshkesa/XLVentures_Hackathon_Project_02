"""KnowledgeManager — lightweight internal orchestrator.

Facade over KnowledgeCoordinator. Validates operations, delegates
orchestration to the coordinator, and records events for audit
and observability.

KnowledgeManager remains lightweight — no business logic lives here.
"""

from __future__ import annotations

import structlog

from adip.knowledge.contracts.models import (
    KnowledgeContext,
    KnowledgeDocument,
    KnowledgeHealth,
    KnowledgeMetrics,
    KnowledgeQuery,
    KnowledgeSession,
)
from adip.knowledge.enums import DocumentType, KnowledgeDomain, RetrievalType
from adip.knowledge.orchestration.coordinator import KnowledgeCoordinator

log = structlog.get_logger(__name__)


class KnowledgeManager:
    """Lightweight internal orchestrator for all knowledge operations.

    Every ADIP module that needs knowledge operations goes through
    this class.
    """

    def __init__(self, coordinator: KnowledgeCoordinator | None = None) -> None:
        self._coordinator = coordinator or KnowledgeCoordinator()
        self._documents: dict[str, KnowledgeDocument] = {}

    def create_document(self, document: KnowledgeDocument) -> KnowledgeDocument:
        """Store and process a new knowledge document."""
        doc_id = str(document.document_id)
        log.info("manager.create_document", document_id=doc_id)
        result = self._coordinator.process_document(document)
        self._documents[doc_id] = result
        return result

    def read_document(self, document_id: str) -> KnowledgeDocument | None:
        """Retrieve a knowledge document by ID."""
        return self._documents.get(document_id) or self._coordinator.get_document(document_id)

    def update_document(self, document: KnowledgeDocument) -> KnowledgeDocument:
        """Update an existing knowledge document."""
        doc_id = str(document.document_id)
        log.info("manager.update_document", document_id=doc_id)
        self._documents[doc_id] = document
        return document

    def delete_document(self, document_id: str) -> bool:
        """Delete a knowledge document."""
        log.info("manager.delete_document", document_id=document_id)
        self._documents.pop(document_id, None)
        return self._coordinator.delete_document(document_id)

    def search_documents(
        self,
        query: str = "",
        domain: KnowledgeDomain | None = None,
        document_type: DocumentType | None = None,
        tags: list[str] | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[KnowledgeDocument]:
        """Search for documents matching the given filters."""
        log.info("manager.search_documents", query=query, domain=domain)
        results: list[KnowledgeDocument] = []
        query_lower = query.lower()

        for doc in self._documents.values():
            if query and query_lower not in doc.title.lower() and query_lower not in doc.content.lower():
                continue
            if domain and doc.domain != domain:
                continue
            if document_type and doc.document_type != document_type:
                continue
            if tags and not all(t in doc.tags for t in tags):
                continue
            results.append(doc)

        return results[offset : offset + limit]

    def retrieve_knowledge(
        self,
        query: KnowledgeQuery,
        strategy: RetrievalType = RetrievalType.HYBRID,
    ) -> KnowledgeContext:
        """Retrieve knowledge matching the given query."""
        log.info("manager.retrieve_knowledge", query_id=str(query.query_id), strategy=strategy.value)
        return self._coordinator.retrieve(query, strategy)

    def get_health(self) -> KnowledgeHealth:
        """Return the current health status."""
        return self._coordinator.health()

    def get_metrics(self) -> KnowledgeMetrics:
        """Return aggregated metrics."""
        return self._coordinator.metrics()

    def get_session(self, session_id: str) -> KnowledgeSession | None:
        """Get a session by ID."""
        return self._coordinator.get_session(session_id)

    def ingest_document(
        self,
        content: str,
        document_type: DocumentType,
        title: str = "",
        domain: KnowledgeDomain = KnowledgeDomain.SYSTEM,
        source: str = "",
        owner_id: str = "",
        namespace: str = "default",
        tags: list[str] | None = None,
    ) -> KnowledgeDocument:
        """Convenience method: create and process a document from raw fields."""
        doc = KnowledgeDocument(
            document_type=document_type,
            domain=domain,
            title=title,
            source=source,
            content=content,
            owner_id=owner_id,
            namespace=namespace,
            tags=tags or [],
        )
        return self.create_document(doc)
