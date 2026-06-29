"""IntegrationHooks — extension points for ADIP platform modules.

All hooks are no-op by default. Downstream modules (Memory Manager,
Planner, Reasoning Engine, etc.) can attach callbacks at runtime
without modifying the Knowledge Manager.

Only hook definitions — no business logic.
"""

from __future__ import annotations

from collections.abc import Callable

import structlog

from adip.knowledge.contracts.models import (
    KnowledgeContext,
    KnowledgeDocument,
    KnowledgeQuery,
    KnowledgeSession,
)

log = structlog.get_logger(__name__)


class IntegrationHooks:
    """Extension hooks for ADIP platform module integration.

    Each hook is a list of callables. Consumers register callbacks
    via the on_* methods. The KnowledgeService invokes them at the
    appropriate points in the pipeline.
    """

    def __init__(self) -> None:
        self._pre_ingest_hooks: list[Callable[[KnowledgeDocument], None]] = []
        self._post_ingest_hooks: list[Callable[[KnowledgeDocument], None]] = []
        self._pre_retrieve_hooks: list[Callable[[KnowledgeQuery], None]] = []
        self._post_retrieve_hooks: list[Callable[[KnowledgeContext], None]] = []
        self._pre_delete_hooks: list[Callable[[str], None]] = []
        self._post_delete_hooks: list[Callable[[str, bool], None]] = []
        self._session_started_hooks: list[Callable[[KnowledgeSession], None]] = []
        self._session_completed_hooks: list[Callable[[KnowledgeSession], None]] = []
        self._error_hooks: list[Callable[[str, Exception], None]] = []

    def on_pre_ingest(self, callback: Callable[[KnowledgeDocument], None]) -> None:
        """Register a hook called before document ingestion."""
        self._pre_ingest_hooks.append(callback)

    def on_post_ingest(self, callback: Callable[[KnowledgeDocument], None]) -> None:
        """Register a hook called after document ingestion."""
        self._post_ingest_hooks.append(callback)

    def on_pre_retrieve(self, callback: Callable[[KnowledgeQuery], None]) -> None:
        """Register a hook called before retrieval."""
        self._pre_retrieve_hooks.append(callback)

    def on_post_retrieve(self, callback: Callable[[KnowledgeContext], None]) -> None:
        """Register a hook called after retrieval."""
        self._post_retrieve_hooks.append(callback)

    def on_pre_delete(self, callback: Callable[[str], None]) -> None:
        """Register a hook called before document deletion."""
        self._pre_delete_hooks.append(callback)

    def on_post_delete(self, callback: Callable[[str, bool], None]) -> None:
        """Register a hook called after document deletion."""
        self._post_delete_hooks.append(callback)

    def on_session_started(self, callback: Callable[[KnowledgeSession], None]) -> None:
        """Register a hook called when a retrieval session starts."""
        self._session_started_hooks.append(callback)

    def on_session_completed(self, callback: Callable[[KnowledgeSession], None]) -> None:
        """Register a hook called when a retrieval session completes."""
        self._session_completed_hooks.append(callback)

    def on_error(self, callback: Callable[[str, Exception], None]) -> None:
        """Register a hook called when an error occurs."""
        self._error_hooks.append(callback)

    def invoke_pre_ingest(self, document: KnowledgeDocument) -> None:
        for hook in self._pre_ingest_hooks:
            try:
                hook(document)
            except Exception:
                log.exception("hooks.pre_ingest.error")

    def invoke_post_ingest(self, document: KnowledgeDocument) -> None:
        for hook in self._post_ingest_hooks:
            try:
                hook(document)
            except Exception:
                log.exception("hooks.post_ingest.error")

    def invoke_pre_retrieve(self, query: KnowledgeQuery) -> None:
        for hook in self._pre_retrieve_hooks:
            try:
                hook(query)
            except Exception:
                log.exception("hooks.pre_retrieve.error")

    def invoke_post_retrieve(self, context: KnowledgeContext) -> None:
        for hook in self._post_retrieve_hooks:
            try:
                hook(context)
            except Exception:
                log.exception("hooks.post_retrieve.error")

    def invoke_pre_delete(self, document_id: str) -> None:
        for hook in self._pre_delete_hooks:
            try:
                hook(document_id)
            except Exception:
                log.exception("hooks.pre_delete.error")

    def invoke_post_delete(self, document_id: str, success: bool) -> None:
        for hook in self._post_delete_hooks:
            try:
                hook(document_id, success)
            except Exception:
                log.exception("hooks.post_delete.error")

    def invoke_session_started(self, session: KnowledgeSession) -> None:
        for hook in self._session_started_hooks:
            try:
                hook(session)
            except Exception:
                log.exception("hooks.session_started.error")

    def invoke_session_completed(self, session: KnowledgeSession) -> None:
        for hook in self._session_completed_hooks:
            try:
                hook(session)
            except Exception:
                log.exception("hooks.session_completed.error")

    def invoke_error(self, operation: str, error: Exception) -> None:
        for hook in self._error_hooks:
            try:
                hook(operation, error)
            except Exception:
                log.exception("hooks.error.error")


# Default global hooks instance
hooks: IntegrationHooks = IntegrationHooks()
