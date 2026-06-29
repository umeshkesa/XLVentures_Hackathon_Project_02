"""KnowledgeService — the ONLY public API for enterprise knowledge operations.

Responsible for:
• Request validation
• Authentication & authorisation hooks
• Audit hook
• Logging & metrics
• Correlation ID propagation
• Session management
• Delegation to KnowledgeManager

All external modules (Planner, Reasoning Engine, Workflow Engine, etc.)
MUST go through KnowledgeService. KnowledgeManager is internal-only.
"""

from __future__ import annotations

import uuid
from collections.abc import Callable
from typing import Any

import structlog

from adip.knowledge.contracts.models import (
    KnowledgeContext,
    KnowledgeDocument,
    KnowledgeHealth,
    KnowledgeMetrics,
    KnowledgeQuery,
    KnowledgeSession,
)
from adip.knowledge.enums import DocumentType, KnowledgeDomain
from adip.knowledge.execution.metrics import KnowledgeMetricsCollector
from adip.knowledge.execution.session import KnowledgeSessionManager
from adip.knowledge.orchestration.manager import KnowledgeManager
from adip.knowledge.services.hooks import IntegrationHooks
from adip.knowledge.services.hooks import hooks as default_hooks

log = structlog.get_logger(__name__)


class AuthResult:
    """Result of an authentication/authorisation check."""

    def __init__(self, allowed: bool = True, reason: str = "") -> None:
        self.allowed = allowed
        self.reason = reason


class KnowledgeService:
    """Enterprise facade for all knowledge operations.

    This is the ONLY public API. External modules MUST use this class
    to interact with the Knowledge Manager.
    """

    def __init__(
        self,
        manager: KnowledgeManager | None = None,
        hooks: IntegrationHooks | None = None,
        session_manager: KnowledgeSessionManager | None = None,
        metrics_collector: KnowledgeMetricsCollector | None = None,
        auth_callback: Callable[[str, str], AuthResult] | None = None,
        audit_callback: Callable[[str, str, str, dict[str, Any]], None] | None = None,
    ) -> None:
        self._manager = manager or KnowledgeManager()
        self._hooks = hooks or default_hooks
        self._session_manager = session_manager or KnowledgeSessionManager()
        self._metrics = metrics_collector or KnowledgeMetricsCollector()
        self._auth_callback = auth_callback
        self._audit_callback = audit_callback

    def ingest(
        self,
        document: KnowledgeDocument,
        user_id: str = "",
        correlation_id: str = "",
    ) -> KnowledgeDocument:
        """Validate, authorise, and ingest a knowledge document."""
        correlation_id = correlation_id or str(uuid.uuid4())
        log.info(
            "service.ingest",
            document_id=str(document.document_id),
            user_id=user_id,
            correlation_id=correlation_id,
        )

        if self._auth_callback:
            auth = self._auth_callback(user_id, "ingest")
            if not auth.allowed:
                raise PermissionError(f"Ingest not allowed: {auth.reason}")

        self._hooks.invoke_pre_ingest(document)
        result = self._manager.create_document(document)
        self._hooks.invoke_post_ingest(result)
        self._audit("ingest", str(result.document_id), user_id, {"correlation_id": correlation_id})
        return result

    def retrieve(
        self,
        query: KnowledgeQuery,
        user_id: str = "",
        correlation_id: str = "",
    ) -> KnowledgeContext:
        """Retrieve knowledge matching the given query."""
        correlation_id = correlation_id or str(uuid.uuid4())
        log.info(
            "service.retrieve",
            query_id=str(query.query_id),
            user_id=user_id,
            correlation_id=correlation_id,
        )

        if self._auth_callback:
            auth = self._auth_callback(user_id, "retrieve")
            if not auth.allowed:
                raise PermissionError(f"Retrieve not allowed: {auth.reason}")

        session = self._session_manager.create_session(
            query=query.query_text,
            user_id=user_id,
            correlation_id=correlation_id,
            retrieval_strategy=query.retrieval_type.value,
        )
        self._hooks.invoke_session_started(session)

        self._hooks.invoke_pre_retrieve(query)
        context = self._manager.retrieve_knowledge(query, query.retrieval_type)
        self._hooks.invoke_post_retrieve(context)

        doc_ids = [str(r.chunk.document_id) for r in context.results if r.chunk.document_id]
        chunk_ids = [str(r.chunk.chunk_id) for r in context.results]
        self._session_manager.complete_session(
            session,
            documents_used=doc_ids,
            chunks_used=chunk_ids,
            cache_hits=1 if context.total_results > 0 else 0,
        )
        self._hooks.invoke_session_completed(session)

        self._metrics.increment_retrievals()
        self._audit("retrieve", str(query.query_id), user_id, {
            "correlation_id": correlation_id,
            "results": context.total_results,
            "strategy": query.retrieval_type.value,
        })
        return context

    def get_document(
        self,
        document_id: str,
        user_id: str = "",
        correlation_id: str = "",
    ) -> KnowledgeDocument | None:
        """Retrieve a single document by its identifier."""
        correlation_id = correlation_id or str(uuid.uuid4())
        log.info("service.get_document", document_id=document_id, user_id=user_id)

        if self._auth_callback:
            auth = self._auth_callback(user_id, "read")
            if not auth.allowed:
                raise PermissionError(f"Read not allowed: {auth.reason}")

        doc = self._manager.read_document(document_id)
        self._audit("read", document_id, user_id, {"correlation_id": correlation_id})
        return doc

    def update_document(
        self,
        document: KnowledgeDocument,
        user_id: str = "",
        correlation_id: str = "",
    ) -> KnowledgeDocument:
        """Update an existing knowledge document."""
        correlation_id = correlation_id or str(uuid.uuid4())
        log.info("service.update_document", document_id=str(document.document_id), user_id=user_id)

        if self._auth_callback:
            auth = self._auth_callback(user_id, "update")
            if not auth.allowed:
                raise PermissionError(f"Update not allowed: {auth.reason}")

        result = self._manager.update_document(document)
        self._audit("update", str(result.document_id), user_id, {"correlation_id": correlation_id})
        return result

    def delete_document(
        self,
        document_id: str,
        user_id: str = "",
        correlation_id: str = "",
    ) -> bool:
        """Delete a knowledge document with authorisation and audit."""
        correlation_id = correlation_id or str(uuid.uuid4())
        log.info("service.delete_document", document_id=document_id, user_id=user_id)

        if self._auth_callback:
            auth = self._auth_callback(user_id, "delete")
            if not auth.allowed:
                raise PermissionError(f"Delete not allowed: {auth.reason}")

        self._hooks.invoke_pre_delete(document_id)
        success = self._manager.delete_document(document_id)
        self._hooks.invoke_post_delete(document_id, success)
        self._audit("delete", document_id, user_id, {
            "correlation_id": correlation_id,
            "success": success,
        })
        return success

    def search_documents(
        self,
        query: str = "",
        domain: KnowledgeDomain | None = None,
        document_type: DocumentType | None = None,
        tags: list[str] | None = None,
        limit: int = 20,
        offset: int = 0,
        user_id: str = "",
        correlation_id: str = "",
    ) -> list[KnowledgeDocument]:
        """Search for documents matching the given filters."""
        correlation_id = correlation_id or str(uuid.uuid4())
        log.info("service.search_documents", query=query, user_id=user_id)

        if self._auth_callback:
            auth = self._auth_callback(user_id, "search")
            if not auth.allowed:
                raise PermissionError(f"Search not allowed: {auth.reason}")

        results = self._manager.search_documents(
            query=query, domain=domain, document_type=document_type,
            tags=tags, limit=limit, offset=offset,
        )
        self._audit("search", "", user_id, {
            "correlation_id": correlation_id,
            "results": len(results),
        })
        return results

    def health(self) -> KnowledgeHealth:
        """Return the current health status of the knowledge platform."""
        log.info("service.health")
        return self._manager.get_health()

    def get_metrics(self) -> KnowledgeMetrics:
        """Return aggregated knowledge platform metrics."""
        log.info("service.get_metrics")
        return self._manager.get_metrics()

    def get_session(self, session_id: str) -> KnowledgeSession | None:
        """Get a session by ID."""
        return self._session_manager.get_session(session_id)

    def _audit(self, operation: str, resource_id: str, user_id: str, details: dict[str, Any]) -> None:
        """Record an audit entry if an audit callback is configured."""
        if self._audit_callback:
            try:
                self._audit_callback(operation, resource_id, user_id, details)
            except Exception:
                log.exception("service.audit.error", operation=operation)



