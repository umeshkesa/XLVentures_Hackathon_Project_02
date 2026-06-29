"""IntegrationHooks — extension points for the Action Engine.

Provides hook points for external integrations to observe
execution operations. All hooks are exception-isolated
(one hook failure does not affect others).
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import structlog

log = structlog.get_logger(__name__)

HookCallback = Callable[..., Any]


class IntegrationHooks:
    """Extension hooks for the Action Engine.

    Provides pre/post hooks for execution, session, decision,
    readiness, retry, compensation, and error operations.
    All hooks execute with exception isolation.
    """

    def __init__(self) -> None:
        self._pre_execute: list[HookCallback] = []
        self._post_execute: list[HookCallback] = []
        self._on_error: list[HookCallback] = []
        self._session_created: list[HookCallback] = []
        self._session_completed: list[HookCallback] = []
        self._decision_made: list[HookCallback] = []
        self._readiness_assessed: list[HookCallback] = []
        self._task_completed: list[HookCallback] = []
        self._retry_performed: list[HookCallback] = []
        self._compensation_triggered: list[HookCallback] = []

    def register_pre_execute(self, callback: HookCallback) -> None:
        """Register a pre-execute hook."""
        self._pre_execute.append(callback)

    def register_post_execute(self, callback: HookCallback) -> None:
        """Register a post-execute hook."""
        self._post_execute.append(callback)

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

    def register_task_completed(self, callback: HookCallback) -> None:
        """Register a task-completed hook."""
        self._task_completed.append(callback)

    def register_retry_performed(self, callback: HookCallback) -> None:
        """Register a retry-performed hook."""
        self._retry_performed.append(callback)

    def register_compensation_triggered(self, callback: HookCallback) -> None:
        """Register a compensation-triggered hook."""
        self._compensation_triggered.append(callback)

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
                log.warning(
                    "hooks.error",
                    hook=str(hook),
                    error=str(e),
                )

    def fire_pre_execute(self, request_id: str, correlation_id: str = "") -> None:
        """Fire pre-execute hooks."""
        self._run_hooks(self._pre_execute, request_id=request_id, correlation_id=correlation_id)

    def fire_post_execute(self, session_id: str, success: bool, correlation_id: str = "") -> None:
        """Fire post-execute hooks."""
        self._run_hooks(self._post_execute, session_id=session_id, success=success, correlation_id=correlation_id)

    def fire_on_error(self, session_id: str, error: str, correlation_id: str = "") -> None:
        """Fire on-error hooks."""
        self._run_hooks(self._on_error, session_id=session_id, error=error, correlation_id=correlation_id)

    def fire_session_created(self, session_id: str, correlation_id: str = "") -> None:
        """Fire session-created hooks."""
        self._run_hooks(self._session_created, session_id=session_id, correlation_id=correlation_id)

    def fire_session_completed(self, session_id: str, state: str, correlation_id: str = "") -> None:
        """Fire session-completed hooks."""
        self._run_hooks(self._session_completed, session_id=session_id, state=state, correlation_id=correlation_id)

    def fire_decision_made(self, decision_id: str, success: bool, correlation_id: str = "") -> None:
        """Fire decision-made hooks."""
        self._run_hooks(self._decision_made, decision_id=decision_id, success=success, correlation_id=correlation_id)

    def fire_readiness_assessed(self, session_id: str, status: str, score: float, correlation_id: str = "") -> None:
        """Fire readiness-assessed hooks."""
        self._run_hooks(self._readiness_assessed, session_id=session_id, status=status, score=score, correlation_id=correlation_id)

    def fire_task_completed(self, task_id: str, success: bool, correlation_id: str = "") -> None:
        """Fire task-completed hooks."""
        self._run_hooks(self._task_completed, task_id=task_id, success=success, correlation_id=correlation_id)

    def fire_retry_performed(self, task_id: str, attempt: int, correlation_id: str = "") -> None:
        """Fire retry-performed hooks."""
        self._run_hooks(self._retry_performed, task_id=task_id, attempt=attempt, correlation_id=correlation_id)

    def fire_compensation_triggered(self, session_id: str, task_id: str, correlation_id: str = "") -> None:
        """Fire compensation-triggered hooks."""
        self._run_hooks(self._compensation_triggered, session_id=session_id, task_id=task_id, correlation_id=correlation_id)


hooks = IntegrationHooks()
