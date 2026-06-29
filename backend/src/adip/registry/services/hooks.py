"""IntegrationHooks — extension points for the Registry Framework.

Provides hook points for external ADIP modules (Planner, Workflow
Engine, Memory Manager, Knowledge Manager, Rule Manager, Plugin
Manager, Evidence Fusion Engine, Reasoning Engine, Recommendation
Engine, Explainability Engine, Action Engine) to observe and react
to registry operations.

Hooks are exception-isolated — failures in one hook do not affect
other hooks or the main operation flow.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import structlog

log = structlog.get_logger(__name__)


class IntegrationHooks:
    """A collection of extension-point hooks for registry operations.

    Each hook type supports multiple registered callbacks. When a
    hook is invoked, all registered callbacks are executed in
    registration order. Exceptions from any callback are logged
    but do not propagate, ensuring hook failures never break the
    main operation.

    Hook types:
        - pre_register / post_register
        - pre_update / post_update
        - pre_delete / post_delete
        - pre_search / post_search
        - pre_lookup / post_lookup
        - session_started / session_completed
        - error
    """

    def __init__(self) -> None:
        self._pre_register: list[Callable[..., Any]] = []
        self._post_register: list[Callable[..., Any]] = []
        self._pre_update: list[Callable[..., Any]] = []
        self._post_update: list[Callable[..., Any]] = []
        self._pre_delete: list[Callable[..., Any]] = []
        self._post_delete: list[Callable[..., Any]] = []
        self._pre_search: list[Callable[..., Any]] = []
        self._post_search: list[Callable[..., Any]] = []
        self._pre_lookup: list[Callable[..., Any]] = []
        self._post_lookup: list[Callable[..., Any]] = []
        self._session_started: list[Callable[..., Any]] = []
        self._session_completed: list[Callable[..., Any]] = []
        self._error: list[Callable[..., Any]] = []

    # ── Registration hooks ─────────────────────────────────────────

    def on_pre_register(self, callback: Callable[..., Any]) -> None:
        """Register a callback invoked before entry registration."""
        self._pre_register.append(callback)

    def on_post_register(self, callback: Callable[..., Any]) -> None:
        """Register a callback invoked after entry registration."""
        self._post_register.append(callback)

    def invoke_pre_register(self, entry: Any, **kwargs: Any) -> None:
        self._invoke_all(self._pre_register, "pre_register", entry=entry, **kwargs)

    def invoke_post_register(self, entry: Any, **kwargs: Any) -> None:
        self._invoke_all(self._post_register, "post_register", entry=entry, **kwargs)

    # ── Update hooks ───────────────────────────────────────────────

    def on_pre_update(self, callback: Callable[..., Any]) -> None:
        """Register a callback invoked before entry update."""
        self._pre_update.append(callback)

    def on_post_update(self, callback: Callable[..., Any]) -> None:
        """Register a callback invoked after entry update."""
        self._post_update.append(callback)

    def invoke_pre_update(self, entry: Any, **kwargs: Any) -> None:
        self._invoke_all(self._pre_update, "pre_update", entry=entry, **kwargs)

    def invoke_post_update(self, entry: Any, **kwargs: Any) -> None:
        self._invoke_all(self._post_update, "post_update", entry=entry, **kwargs)

    # ── Delete hooks ───────────────────────────────────────────────

    def on_pre_delete(self, callback: Callable[..., Any]) -> None:
        """Register a callback invoked before entry deletion."""
        self._pre_delete.append(callback)

    def on_post_delete(self, callback: Callable[..., Any]) -> None:
        """Register a callback invoked after entry deletion."""
        self._post_delete.append(callback)

    def invoke_pre_delete(self, entry_id: str, **kwargs: Any) -> None:
        self._invoke_all(self._pre_delete, "pre_delete", entry_id=entry_id, **kwargs)

    def invoke_post_delete(self, entry_id: str, **kwargs: Any) -> None:
        self._invoke_all(self._post_delete, "post_delete", entry_id=entry_id, **kwargs)

    # ── Search hooks ───────────────────────────────────────────────

    def on_pre_search(self, callback: Callable[..., Any]) -> None:
        """Register a callback invoked before search."""
        self._pre_search.append(callback)

    def on_post_search(self, callback: Callable[..., Any]) -> None:
        """Register a callback invoked after search."""
        self._post_search.append(callback)

    def invoke_pre_search(self, query: str, **kwargs: Any) -> None:
        self._invoke_all(self._pre_search, "pre_search", query=query, **kwargs)

    def invoke_post_search(self, results: list[Any], **kwargs: Any) -> None:
        self._invoke_all(self._post_search, "post_search", results=results, **kwargs)

    # ── Lookup hooks ───────────────────────────────────────────────

    def on_pre_lookup(self, callback: Callable[..., Any]) -> None:
        """Register a callback invoked before entry lookup."""
        self._pre_lookup.append(callback)

    def on_post_lookup(self, callback: Callable[..., Any]) -> None:
        """Register a callback invoked after entry lookup."""
        self._post_lookup.append(callback)

    def invoke_pre_lookup(self, entry_id: str, **kwargs: Any) -> None:
        self._invoke_all(self._pre_lookup, "pre_lookup", entry_id=entry_id, **kwargs)

    def invoke_post_lookup(self, entry: Any, **kwargs: Any) -> None:
        self._invoke_all(self._post_lookup, "post_lookup", entry=entry, **kwargs)

    # ── Session hooks ──────────────────────────────────────────────

    def on_session_started(self, callback: Callable[..., Any]) -> None:
        """Register a callback invoked when a session starts."""
        self._session_started.append(callback)

    def on_session_completed(self, callback: Callable[..., Any]) -> None:
        """Register a callback invoked when a session completes."""
        self._session_completed.append(callback)

    def invoke_session_started(self, session: Any, **kwargs: Any) -> None:
        self._invoke_all(self._session_started, "session_started", session=session, **kwargs)

    def invoke_session_completed(self, session: Any, **kwargs: Any) -> None:
        self._invoke_all(self._session_completed, "session_completed", session=session, **kwargs)

    # ── Error hooks ────────────────────────────────────────────────

    def on_error(self, callback: Callable[..., Any]) -> None:
        """Register a callback invoked when an error occurs."""
        self._error.append(callback)

    def invoke_error(self, operation: str, error: Exception, **kwargs: Any) -> None:
        self._invoke_all(self._error, "error", operation=operation, error=error, **kwargs)

    # ── Internal ────────────────────────────────────────────────────

    def _invoke_all(self, callbacks: list[Callable[..., Any]], hook_name: str, **kwargs: Any) -> None:
        """Invoke all registered callbacks for a hook, isolated from errors."""
        for cb in callbacks:
            try:
                cb(**kwargs)
            except Exception:
                log.exception("registry_hooks.error", hook=hook_name, callback=cb.__name__)


# Global singleton — easy import for downstream ADIP modules
hooks: IntegrationHooks = IntegrationHooks()
