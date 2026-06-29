"""IntegrationHooks — extension points for the Recommendation Engine.

Provides hook points for Explainability Engine, Decision Review Layer,
Action Manager, and Action Engine integration.
All hooks are exception-isolated (one hook failure does not affect others).
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import structlog

log = structlog.get_logger(__name__)


HookCallback = Callable[..., Any]


class IntegrationHooks:
    """Extension hooks for the Recommendation Engine.

    Provides pre/post hooks for session, recommendation, portfolio,
    review, confidence, version, readiness, lineage, snapshot, and
    comparison operations. All hooks execute with exception isolation.
    """

    def __init__(self) -> None:
        self._pre_recommend: list[HookCallback] = []
        self._post_recommend: list[HookCallback] = []
        self._pre_session_create: list[HookCallback] = []
        self._post_session_create: list[HookCallback] = []
        self._pre_portfolio: list[HookCallback] = []
        self._post_portfolio: list[HookCallback] = []
        self._pre_review: list[HookCallback] = []
        self._post_review: list[HookCallback] = []
        self._pre_confidence: list[HookCallback] = []
        self._post_confidence: list[HookCallback] = []
        self._on_error: list[HookCallback] = []
        self._on_complete: list[HookCallback] = []

    def register_pre_recommend(self, callback: HookCallback) -> None:
        """Register a hook to run before recommendation."""
        self._pre_recommend.append(callback)

    def register_post_recommend(self, callback: HookCallback) -> None:
        """Register a hook to run after recommendation."""
        self._post_recommend.append(callback)

    def register_pre_session_create(self, callback: HookCallback) -> None:
        """Register a hook to run before session creation."""
        self._pre_session_create.append(callback)

    def register_post_session_create(self, callback: HookCallback) -> None:
        """Register a hook to run after session creation."""
        self._post_session_create.append(callback)

    def register_pre_portfolio(self, callback: HookCallback) -> None:
        """Register a hook to run before portfolio creation."""
        self._pre_portfolio.append(callback)

    def register_post_portfolio(self, callback: HookCallback) -> None:
        """Register a hook to run after portfolio creation."""
        self._post_portfolio.append(callback)

    def register_pre_review(self, callback: HookCallback) -> None:
        """Register a hook to run before review."""
        self._pre_review.append(callback)

    def register_post_review(self, callback: HookCallback) -> None:
        """Register a hook to run after review."""
        self._post_review.append(callback)

    def register_pre_confidence(self, callback: HookCallback) -> None:
        """Register a hook to run before confidence calculation."""
        self._pre_confidence.append(callback)

    def register_post_confidence(self, callback: HookCallback) -> None:
        """Register a hook to run after confidence calculation."""
        self._post_confidence.append(callback)

    def register_on_error(self, callback: HookCallback) -> None:
        """Register a hook to run on error."""
        self._on_error.append(callback)

    def register_on_complete(self, callback: HookCallback) -> None:
        """Register a hook to run on completion."""
        self._on_complete.append(callback)

    def _run_hooks(self, hooks: list[HookCallback], *args: Any, **kwargs: Any) -> None:
        for hook in hooks:
            try:
                hook(*args, **kwargs)
            except Exception as e:
                log.warning("hook.failed", hook=str(hook), error=str(e))

    def run_pre_recommend(self, **kwargs: Any) -> None:
        """Run all pre-recommendation hooks."""
        self._run_hooks(self._pre_recommend, **kwargs)

    def run_post_recommend(self, **kwargs: Any) -> None:
        """Run all post-recommendation hooks."""
        self._run_hooks(self._post_recommend, **kwargs)

    def run_pre_session_create(self, **kwargs: Any) -> None:
        """Run all pre-session-creation hooks."""
        self._run_hooks(self._pre_session_create, **kwargs)

    def run_post_session_create(self, **kwargs: Any) -> None:
        """Run all post-session-creation hooks."""
        self._run_hooks(self._post_session_create, **kwargs)

    def run_pre_portfolio(self, **kwargs: Any) -> None:
        """Run all pre-portfolio hooks."""
        self._run_hooks(self._pre_portfolio, **kwargs)

    def run_post_portfolio(self, **kwargs: Any) -> None:
        """Run all post-portfolio hooks."""
        self._run_hooks(self._post_portfolio, **kwargs)

    def run_pre_review(self, **kwargs: Any) -> None:
        """Run all pre-review hooks."""
        self._run_hooks(self._pre_review, **kwargs)

    def run_post_review(self, **kwargs: Any) -> None:
        """Run all post-review hooks."""
        self._run_hooks(self._post_review, **kwargs)

    def run_pre_confidence(self, **kwargs: Any) -> None:
        """Run all pre-confidence hooks."""
        self._run_hooks(self._pre_confidence, **kwargs)

    def run_post_confidence(self, **kwargs: Any) -> None:
        """Run all post-confidence hooks."""
        self._run_hooks(self._post_confidence, **kwargs)

    def run_on_error(self, **kwargs: Any) -> None:
        """Run all error hooks."""
        self._run_hooks(self._on_error, **kwargs)

    def run_on_complete(self, **kwargs: Any) -> None:
        """Run all completion hooks."""
        self._run_hooks(self._on_complete, **kwargs)


# Global singleton hooks instance
hooks = IntegrationHooks()
