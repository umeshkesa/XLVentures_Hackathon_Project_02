"""IntegrationHooks — extension points for the Action Manager.

Provides hook points for external integrations to observe
action planning operations. All hooks are exception-isolated
(one hook failure does not affect others).
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import structlog

log = structlog.get_logger(__name__)

HookCallback = Callable[..., Any]


class IntegrationHooks:
    """Extension hooks for the Action Manager.

    Provides pre/post hooks for plan, session, decision,
    readiness, and error operations. All hooks execute with
    exception isolation.
    """

    def __init__(self) -> None:
        self._pre_plan: list[HookCallback] = []
        self._post_plan: list[HookCallback] = []
        self._on_error: list[HookCallback] = []
        self._session_created: list[HookCallback] = []
        self._session_completed: list[HookCallback] = []
        self._decision_made: list[HookCallback] = []
        self._readiness_assessed: list[HookCallback] = []
        self._pre_optimize: list[HookCallback] = []
        self._post_optimize: list[HookCallback] = []
        self._pre_review: list[HookCallback] = []
        self._post_review: list[HookCallback] = []

    def register_pre_plan(self, callback: HookCallback) -> None:
        """Register a pre-plan hook."""
        self._pre_plan.append(callback)

    def register_post_plan(self, callback: HookCallback) -> None:
        """Register a post-plan hook."""
        self._post_plan.append(callback)

    def register_on_error(self, callback: HookCallback) -> None:
        """Register an on-error hook."""
        self._on_error.append(callback)

    def register_session_created(self, callback: HookCallback) -> None:
        """Register a session-created hook."""
        self._session_created.append(callback)

    def register_session_completed(self, callback: HookCallback) -> None:
        """Register a session-completed hook."""
        self._session_completed.append(callback)

    def register_decision_made(self, callback: HookCallback) -> None:
        """Register a decision-made hook."""
        self._decision_made.append(callback)

    def register_readiness_assessed(self, callback: HookCallback) -> None:
        """Register a readiness-assessed hook."""
        self._readiness_assessed.append(callback)

    def register_pre_optimize(self, callback: HookCallback) -> None:
        """Register a pre-optimize hook."""
        self._pre_optimize.append(callback)

    def register_post_optimize(self, callback: HookCallback) -> None:
        """Register a post-optimize hook."""
        self._post_optimize.append(callback)

    def register_pre_review(self, callback: HookCallback) -> None:
        """Register a pre-review hook."""
        self._pre_review.append(callback)

    def register_post_review(self, callback: HookCallback) -> None:
        """Register a post-review hook."""
        self._post_review.append(callback)

    def _run_hooks(
        self,
        hooks: list[HookCallback],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Run hooks with exception isolation.

        Args:
            hooks: The hooks to run.
            args: Positional arguments.
            kwargs: Keyword arguments.
        """
        for hook in hooks:
            try:
                hook(*args, **kwargs)
            except Exception as e:
                log.warning("hook.failed", hook=str(hook), error=str(e))

    def run_pre_plan(self, *args: Any, **kwargs: Any) -> None:
        """Run pre-plan hooks."""
        self._run_hooks(self._pre_plan, *args, **kwargs)

    def run_post_plan(self, *args: Any, **kwargs: Any) -> None:
        """Run post-plan hooks."""
        self._run_hooks(self._post_plan, *args, **kwargs)

    def run_on_error(self, *args: Any, **kwargs: Any) -> None:
        """Run on-error hooks."""
        self._run_hooks(self._on_error, *args, **kwargs)

    def run_session_created(self, *args: Any, **kwargs: Any) -> None:
        """Run session-created hooks."""
        self._run_hooks(self._session_created, *args, **kwargs)

    def run_session_completed(self, *args: Any, **kwargs: Any) -> None:
        """Run session-completed hooks."""
        self._run_hooks(self._session_completed, *args, **kwargs)

    def run_decision_made(self, *args: Any, **kwargs: Any) -> None:
        """Run decision-made hooks."""
        self._run_hooks(self._decision_made, *args, **kwargs)

    def run_readiness_assessed(self, *args: Any, **kwargs: Any) -> None:
        """Run readiness-assessed hooks."""
        self._run_hooks(self._readiness_assessed, *args, **kwargs)

    def run_pre_optimize(self, *args: Any, **kwargs: Any) -> None:
        """Run pre-optimize hooks."""
        self._run_hooks(self._pre_optimize, *args, **kwargs)

    def run_post_optimize(self, *args: Any, **kwargs: Any) -> None:
        """Run post-optimize hooks."""
        self._run_hooks(self._post_optimize, *args, **kwargs)

    def run_pre_review(self, *args: Any, **kwargs: Any) -> None:
        """Run pre-review hooks."""
        self._run_hooks(self._pre_review, *args, **kwargs)

    def run_post_review(self, *args: Any, **kwargs: Any) -> None:
        """Run post-review hooks."""
        self._run_hooks(self._post_review, *args, **kwargs)


hooks = IntegrationHooks()
