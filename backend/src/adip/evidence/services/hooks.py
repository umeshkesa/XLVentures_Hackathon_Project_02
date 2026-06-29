"""IntegrationHooks — extension points for the Evidence Fusion Engine.

Provides hook points for external ADIP modules (Planner, Workflow
Engine, Memory Manager, Knowledge Manager, Rule Manager, Plugin
Manager, Registry, Reasoning Engine, Recommendation Engine,
Explainability Engine, Action Engine) to observe and react to
evidence operations.

Hooks are exception-isolated — failures in one hook do not affect
other hooks or the main operation flow.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import structlog

log = structlog.get_logger(__name__)


class IntegrationHooks:
    """A collection of extension-point hooks for evidence operations.

    Each hook type supports multiple registered callbacks. When a
    hook is invoked, all registered callbacks are executed in
    registration order. Exceptions from any callback are logged
    but do not propagate, ensuring hook failures never break the
    main operation.

    Hook types:
        - pre_collect / post_collect
        - pre_process / post_process
        - pre_lookup / post_lookup
        - session_started / session_completed
        - error
    """

    def __init__(self) -> None:
        self._pre_collect: list[Callable[..., Any]] = []
        self._post_collect: list[Callable[..., Any]] = []
        self._pre_process: list[Callable[..., Any]] = []
        self._post_process: list[Callable[..., Any]] = []
        self._pre_lookup: list[Callable[..., Any]] = []
        self._post_lookup: list[Callable[..., Any]] = []
        self._session_started: list[Callable[..., Any]] = []
        self._session_completed: list[Callable[..., Any]] = []
        self._error: list[Callable[..., Any]] = []

    # ── Collection hooks ───────────────────────────────────────────

    def on_pre_collect(self, callback: Callable[..., Any]) -> None:
        """Register a callback invoked before evidence collection."""
        self._pre_collect.append(callback)

    def on_post_collect(self, callback: Callable[..., Any]) -> None:
        """Register a callback invoked after evidence collection."""
        self._post_collect.append(callback)

    def invoke_pre_collect(self, evidence_type: Any, domain: Any, **kwargs: Any) -> None:
        self._invoke_all(self._pre_collect, "pre_collect", evidence_type=evidence_type, domain=domain, **kwargs)

    def invoke_post_collect(self, evidence: Any, **kwargs: Any) -> None:
        self._invoke_all(self._post_collect, "post_collect", evidence=evidence, **kwargs)

    # ── Processing hooks ───────────────────────────────────────────

    def on_pre_process(self, callback: Callable[..., Any]) -> None:
        """Register a callback invoked before evidence processing."""
        self._pre_process.append(callback)

    def on_post_process(self, callback: Callable[..., Any]) -> None:
        """Register a callback invoked after evidence processing."""
        self._post_process.append(callback)

    def invoke_pre_process(self, evidence_list: list[Any], **kwargs: Any) -> None:
        self._invoke_all(self._pre_process, "pre_process", evidence_list=evidence_list, **kwargs)

    def invoke_post_process(self, decision: Any, **kwargs: Any) -> None:
        self._invoke_all(self._post_process, "post_process", decision=decision, **kwargs)

    # ── Lookup hooks ───────────────────────────────────────────────

    def on_pre_lookup(self, callback: Callable[..., Any]) -> None:
        """Register a callback invoked before evidence lookup."""
        self._pre_lookup.append(callback)

    def on_post_lookup(self, callback: Callable[..., Any]) -> None:
        """Register a callback invoked after evidence lookup."""
        self._post_lookup.append(callback)

    def invoke_pre_lookup(self, evidence_id: str, **kwargs: Any) -> None:
        self._invoke_all(self._pre_lookup, "pre_lookup", evidence_id=evidence_id, **kwargs)

    def invoke_post_lookup(self, evidence: Any, **kwargs: Any) -> None:
        self._invoke_all(self._post_lookup, "post_lookup", evidence=evidence, **kwargs)

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
                log.exception("evidence_hooks.error", hook=hook_name, callback=cb.__name__)


# Global singleton — easy import for downstream ADIP modules
hooks: IntegrationHooks = IntegrationHooks()
