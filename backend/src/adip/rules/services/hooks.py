"""IntegrationHooks — extension points for ADIP platform modules.

All hooks are no-op by default. Downstream modules (Memory Manager,
Planner, Reasoning Engine, etc.) can attach callbacks at runtime
without modifying the Rule Manager.

Only hook definitions — no business logic.
"""

from __future__ import annotations

from collections.abc import Callable

import structlog

from adip.rules.contracts.models import Rule, RuleContext, RuleEvaluation, RuleSession

log = structlog.get_logger(__name__)


class IntegrationHooks:
    """Extension hooks for ADIP platform module integration.

    Each hook is a list of callables. Consumers register callbacks
    via the on_* methods. The RuleService invokes them at the
    appropriate points in the pipeline.
    """

    def __init__(self) -> None:
        self._pre_evaluate_hooks: list[Callable[[RuleContext], None]] = []
        self._post_evaluate_hooks: list[Callable[[RuleEvaluation], None]] = []
        self._pre_create_rule_hooks: list[Callable[[Rule], None]] = []
        self._post_create_rule_hooks: list[Callable[[Rule], None]] = []
        self._pre_update_rule_hooks: list[Callable[[Rule], None]] = []
        self._post_update_rule_hooks: list[Callable[[Rule], None]] = []
        self._pre_delete_rule_hooks: list[Callable[[str], None]] = []
        self._post_delete_rule_hooks: list[Callable[[str, bool], None]] = []
        self._session_started_hooks: list[Callable[[RuleSession], None]] = []
        self._session_completed_hooks: list[Callable[[RuleSession], None]] = []
        self._error_hooks: list[Callable[[str, Exception], None]] = []

    def on_pre_evaluate(self, callback: Callable[[RuleContext], None]) -> None:
        """Register a hook called before rule evaluation."""
        self._pre_evaluate_hooks.append(callback)

    def on_post_evaluate(self, callback: Callable[[RuleEvaluation], None]) -> None:
        """Register a hook called after rule evaluation."""
        self._post_evaluate_hooks.append(callback)

    def on_pre_create_rule(self, callback: Callable[[Rule], None]) -> None:
        """Register a hook called before rule creation."""
        self._pre_create_rule_hooks.append(callback)

    def on_post_create_rule(self, callback: Callable[[Rule], None]) -> None:
        """Register a hook called after rule creation."""
        self._post_create_rule_hooks.append(callback)

    def on_pre_update_rule(self, callback: Callable[[Rule], None]) -> None:
        """Register a hook called before rule update."""
        self._pre_update_rule_hooks.append(callback)

    def on_post_update_rule(self, callback: Callable[[Rule], None]) -> None:
        """Register a hook called after rule update."""
        self._post_update_rule_hooks.append(callback)

    def on_pre_delete_rule(self, callback: Callable[[str], None]) -> None:
        """Register a hook called before rule deletion."""
        self._pre_delete_rule_hooks.append(callback)

    def on_post_delete_rule(self, callback: Callable[[str, bool], None]) -> None:
        """Register a hook called after rule deletion."""
        self._post_delete_rule_hooks.append(callback)

    def on_session_started(self, callback: Callable[[RuleSession], None]) -> None:
        """Register a hook called when an evaluation session starts."""
        self._session_started_hooks.append(callback)

    def on_session_completed(self, callback: Callable[[RuleSession], None]) -> None:
        """Register a hook called when an evaluation session completes."""
        self._session_completed_hooks.append(callback)

    def on_error(self, callback: Callable[[str, Exception], None]) -> None:
        """Register a hook called when an error occurs."""
        self._error_hooks.append(callback)

    def invoke_pre_evaluate(self, context: RuleContext) -> None:
        for hook in self._pre_evaluate_hooks:
            try:
                hook(context)
            except Exception:
                log.exception("hooks.pre_evaluate.error")

    def invoke_post_evaluate(self, evaluation: RuleEvaluation) -> None:
        for hook in self._post_evaluate_hooks:
            try:
                hook(evaluation)
            except Exception:
                log.exception("hooks.post_evaluate.error")

    def invoke_pre_create_rule(self, rule: Rule) -> None:
        for hook in self._pre_create_rule_hooks:
            try:
                hook(rule)
            except Exception:
                log.exception("hooks.pre_create_rule.error")

    def invoke_post_create_rule(self, rule: Rule) -> None:
        for hook in self._post_create_rule_hooks:
            try:
                hook(rule)
            except Exception:
                log.exception("hooks.post_create_rule.error")

    def invoke_pre_update_rule(self, rule: Rule) -> None:
        for hook in self._pre_update_rule_hooks:
            try:
                hook(rule)
            except Exception:
                log.exception("hooks.pre_update_rule.error")

    def invoke_post_update_rule(self, rule: Rule) -> None:
        for hook in self._post_update_rule_hooks:
            try:
                hook(rule)
            except Exception:
                log.exception("hooks.post_update_rule.error")

    def invoke_pre_delete_rule(self, rule_id: str) -> None:
        for hook in self._pre_delete_rule_hooks:
            try:
                hook(rule_id)
            except Exception:
                log.exception("hooks.pre_delete_rule.error")

    def invoke_post_delete_rule(self, rule_id: str, success: bool) -> None:
        for hook in self._post_delete_rule_hooks:
            try:
                hook(rule_id, success)
            except Exception:
                log.exception("hooks.post_delete_rule.error")

    def invoke_session_started(self, session: RuleSession) -> None:
        for hook in self._session_started_hooks:
            try:
                hook(session)
            except Exception:
                log.exception("hooks.session_started.error")

    def invoke_session_completed(self, session: RuleSession) -> None:
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
