"""IntegrationHooks — extension points for the Explainability Engine.

Provides hook points for external integrations to observe
explanation operations.
All hooks are exception-isolated (one hook failure does not affect others).
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import structlog

log = structlog.get_logger(__name__)


HookCallback = Callable[..., Any]


class IntegrationHooks:
    """Extension hooks for the Explainability Engine.

    Provides pre/post hooks for explanation, session, error,
    decision review, and action operations.
    All hooks execute with exception isolation.
    """

    def __init__(self) -> None:
        self._pre_explain: list[HookCallback] = []
        self._post_explain: list[HookCallback] = []
        self._on_error: list[HookCallback] = []
        self._session_created: list[HookCallback] = []
        self._session_completed: list[HookCallback] = []
        self._decision_review: list[HookCallback] = []
        self._action_manager: list[HookCallback] = []
        self._action_engine: list[HookCallback] = []

    def register_pre_explain(self, callback: HookCallback) -> None:
        """Register a hook to run before explanation."""
        self._pre_explain.append(callback)

    def register_post_explain(self, callback: HookCallback) -> None:
        """Register a hook to run after explanation."""
        self._post_explain.append(callback)

    def register_on_error(self, callback: HookCallback) -> None:
        """Register a hook to run on error."""
        self._on_error.append(callback)

    def register_session_created(self, callback: HookCallback) -> None:
        """Register a hook to run when a session is created."""
        self._session_created.append(callback)

    def register_session_completed(self, callback: HookCallback) -> None:
        """Register a hook to run when a session is completed."""
        self._session_completed.append(callback)

    def register_decision_review(self, callback: HookCallback) -> None:
        """Register a hook to run during decision review."""
        self._decision_review.append(callback)

    def register_action_manager(self, callback: HookCallback) -> None:
        """Register a hook to run for action manager."""
        self._action_manager.append(callback)

    def register_action_engine(self, callback: HookCallback) -> None:
        """Register a hook to run for action engine."""
        self._action_engine.append(callback)

    def _run_hooks(self, hooks: list[HookCallback], *args: Any, **kwargs: Any) -> None:
        for hook in hooks:
            try:
                hook(*args, **kwargs)
            except Exception as e:
                log.warning("hook.failed", hook=str(hook), error=str(e))

    def run_pre_explain(self, **kwargs: Any) -> None:
        """Run all pre-explanation hooks."""
        self._run_hooks(self._pre_explain, **kwargs)

    def run_post_explain(self, **kwargs: Any) -> None:
        """Run all post-explanation hooks."""
        self._run_hooks(self._post_explain, **kwargs)

    def run_on_error(self, **kwargs: Any) -> None:
        """Run all error hooks."""
        self._run_hooks(self._on_error, **kwargs)

    def run_session_created(self, **kwargs: Any) -> None:
        """Run all session-created hooks."""
        self._run_hooks(self._session_created, **kwargs)

    def run_session_completed(self, **kwargs: Any) -> None:
        """Run all session-completed hooks."""
        self._run_hooks(self._session_completed, **kwargs)

    def run_decision_review(self, decision: Any, **kwargs: Any) -> None:
        """Run all decision review hooks.

        Args:
            decision: The decision being reviewed.
            **kwargs: Additional keyword arguments to pass to hooks.
        """
        self._run_hooks(self._decision_review, decision, **kwargs)

    def run_action_manager(self, action: Any, **kwargs: Any) -> None:
        """Run all action manager hooks.

        Args:
            action: The action being managed.
            **kwargs: Additional keyword arguments to pass to hooks.
        """
        self._run_hooks(self._action_manager, action, **kwargs)

    def run_action_engine(self, action: Any, **kwargs: Any) -> None:
        """Run all action engine hooks.

        Args:
            action: The action being processed.
            **kwargs: Additional keyword arguments to pass to hooks.
        """
        self._run_hooks(self._action_engine, action, **kwargs)


# Global singleton hooks instance
hooks = IntegrationHooks()
