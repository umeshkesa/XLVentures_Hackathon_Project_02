"""RuleService — the ONLY public API for enterprise rule operations.

Responsible for:
• Request validation
• Authentication & authorisation hooks
• Audit hook
• Logging & metrics
• Correlation ID propagation
• Session management
• Delegation to RuleManager

All external modules (Planner, Reasoning Engine, Workflow Engine, etc.)
MUST go through RuleService. RuleManager is internal-only.
"""

from __future__ import annotations

import uuid
from collections.abc import Callable
from typing import Any

import structlog

from adip.rules.contracts.models import (
    Rule,
    RuleContext,
    RuleEvaluation,
    RuleHealth,
    RuleMetrics,
    RuleSet,
)
from adip.rules.enums import (
    EvaluationStrategyType,
    RuleDomain,
)
from adip.rules.execution.metrics import RuleMetricsCollector
from adip.rules.orchestration.manager import RuleManager
from adip.rules.orchestration.session import RuleSessionManager
from adip.rules.services.hooks import IntegrationHooks
from adip.rules.services.hooks import hooks as default_hooks

log = structlog.get_logger(__name__)


class AuthResult:
    """Result of an authentication/authorisation check."""

    def __init__(self, allowed: bool = True, reason: str = "") -> None:
        self.allowed = allowed
        self.reason = reason


class RuleService:
    """Enterprise facade for all rule operations.

    This is the ONLY public API. External modules MUST use this class
    to interact with the Rule Manager.

    RuleService must never call evaluation components directly.
    """

    def __init__(
        self,
        manager: RuleManager | None = None,
        hooks: IntegrationHooks | None = None,
        session_manager: RuleSessionManager | None = None,
        metrics_collector: RuleMetricsCollector | None = None,
        auth_callback: Callable[[str, str], AuthResult] | None = None,
        audit_callback: Callable[[str, str, str, dict[str, Any]], None] | None = None,
    ) -> None:
        self._manager = manager or RuleManager()
        self._hooks = hooks or default_hooks
        self._session_manager = session_manager or RuleSessionManager()
        self._metrics = metrics_collector or RuleMetricsCollector()
        self._auth_callback = auth_callback
        self._audit_callback = audit_callback

    def _audit(self, operation: str, entity_id: str, user_id: str, details: dict[str, Any]) -> None:
        if self._audit_callback:
            self._audit_callback(operation, entity_id, user_id, details)

    # ── Rule CRUD ──────────────────────────────────────────────────────────

    def create_rule(
        self,
        rule: Rule,
        user_id: str = "",
        correlation_id: str = "",
    ) -> Rule:
        """Validate, authorise, and create a new rule."""
        correlation_id = correlation_id or str(uuid.uuid4())
        log.info(
            "service.create_rule",
            rule_id=str(rule.rule_id),
            user_id=user_id,
            correlation_id=correlation_id,
        )

        if self._auth_callback:
            auth = self._auth_callback(user_id, "create_rule")
            if not auth.allowed:
                raise PermissionError(f"Create rule not allowed: {auth.reason}")

        self._hooks.invoke_pre_create_rule(rule)
        result = self._manager.create_rule(rule, created_by=user_id)
        self._hooks.invoke_post_create_rule(result)
        self._audit("create_rule", str(result.rule_id), user_id, {"correlation_id": correlation_id})
        return result

    def get_rule(self, rule_id: str, user_id: str = "") -> Rule | None:
        """Retrieve a rule by its identifier."""
        log.info("service.get_rule", rule_id=rule_id, user_id=user_id)
        return self._manager.read_rule(rule_id)

    def update_rule(
        self,
        rule: Rule,
        user_id: str = "",
        correlation_id: str = "",
    ) -> Rule:
        """Update an existing rule with authorisation."""
        correlation_id = correlation_id or str(uuid.uuid4())
        log.info("service.update_rule", rule_id=str(rule.rule_id), user_id=user_id)

        if self._auth_callback:
            auth = self._auth_callback(user_id, "update_rule")
            if not auth.allowed:
                raise PermissionError(f"Update rule not allowed: {auth.reason}")

        self._hooks.invoke_pre_update_rule(rule)
        result = self._manager.update_rule(rule)
        self._hooks.invoke_post_update_rule(result)
        self._audit("update_rule", str(result.rule_id), user_id, {"correlation_id": correlation_id})
        return result

    def delete_rule(self, rule_id: str, user_id: str = "") -> bool:
        """Delete a rule with authorisation and audit."""
        log.info("service.delete_rule", rule_id=rule_id, user_id=user_id)

        if self._auth_callback:
            auth = self._auth_callback(user_id, "delete_rule")
            if not auth.allowed:
                raise PermissionError(f"Delete rule not allowed: {auth.reason}")

        self._hooks.invoke_pre_delete_rule(rule_id)
        result = self._manager.delete_rule(rule_id)
        self._hooks.invoke_post_delete_rule(rule_id, result)
        self._audit("delete_rule", rule_id, user_id, {"success": result})
        return result

    # ── Rule Evaluation ───────────────────────────────────────────────────

    def evaluate(
        self,
        context: RuleContext,
        domain: RuleDomain = RuleDomain.SYSTEM,
        user_id: str = "",
        correlation_id: str = "",
        strategy_type: EvaluationStrategyType | None = None,
    ) -> RuleEvaluation:
        """Evaluate rules matching the given context and domain."""
        correlation_id = correlation_id or str(uuid.uuid4())
        log.info(
            "service.evaluate",
            domain=domain.value,
            user_id=user_id,
            correlation_id=correlation_id,
        )

        if self._auth_callback:
            auth = self._auth_callback(user_id, "evaluate")
            if not auth.allowed:
                raise PermissionError(f"Evaluate not allowed: {auth.reason}")

        # Create evaluation session
        session = self._session_manager.create_session(
            domain=domain,
            user_id=user_id,
            correlation_id=correlation_id,
            evaluation_strategy=strategy_type or EvaluationStrategyType.SEQUENTIAL,
        )
        self._hooks.invoke_session_started(session)

        # Augment context with correlation ID
        context.correlation_id = correlation_id

        try:
            self._hooks.invoke_pre_evaluate(context)
            evaluation = self._manager.evaluate_rules(
                context,
                domain=domain,
                strategy_type=strategy_type,
            )
            self._hooks.invoke_post_evaluate(evaluation)

            # Update session
            for decision in evaluation.decisions:
                self._session_manager.add_decision(str(session.session_id), decision)
            for rule_id in evaluation.rules_evaluated:
                self._session_manager.add_evaluated_rule(str(session.session_id), str(rule_id))

            self._session_manager.complete_session(str(session.session_id))
            self._hooks.invoke_session_completed(session)

            self._audit("evaluate", domain.value, user_id, {
                "correlation_id": correlation_id,
                "rules_evaluated": len(evaluation.rules_evaluated),
                "decisions": len(evaluation.decisions),
            })

            return evaluation

        except Exception as e:
            self._session_manager.complete_session(str(session.session_id))
            self._hooks.invoke_error("evaluate", e)
            self._audit("evaluate_error", domain.value, user_id, {
                "correlation_id": correlation_id,
                "error": str(e),
            })
            raise

    # ── Rule Set Management ───────────────────────────────────────────────

    def create_ruleset(self, ruleset: RuleSet, user_id: str = "") -> RuleSet:
        """Create a new rule set."""
        log.info("service.create_ruleset", ruleset_id=str(ruleset.ruleset_id), user_id=user_id)

        if self._auth_callback:
            auth = self._auth_callback(user_id, "create_ruleset")
            if not auth.allowed:
                raise PermissionError(f"Create ruleset not allowed: {auth.reason}")

        return self._manager.create_ruleset(ruleset)

    def get_ruleset(self, ruleset_id: str) -> RuleSet | None:
        """Retrieve a rule set by its identifier."""
        return self._manager.read_ruleset(ruleset_id)

    # ── Rule Lifecycle ────────────────────────────────────────────────────

    def activate_rule(self, rule_id: str, user_id: str = "") -> Rule:
        """Activate a rule (transition to ACTIVE status)."""
        log.info("service.activate_rule", rule_id=rule_id, user_id=user_id)

        if self._auth_callback:
            auth = self._auth_callback(user_id, "activate_rule")
            if not auth.allowed:
                raise PermissionError(f"Activate rule not allowed: {auth.reason}")

        result = self._manager.activate_rule(rule_id)
        self._audit("activate_rule", rule_id, user_id, {})
        return result

    def archive_rule(self, rule_id: str, reason: str = "", user_id: str = "") -> bool:
        """Archive a rule."""
        log.info("service.archive_rule", rule_id=rule_id, user_id=user_id)

        if self._auth_callback:
            auth = self._auth_callback(user_id, "archive_rule")
            if not auth.allowed:
                raise PermissionError(f"Archive rule not allowed: {auth.reason}")

        result = self._manager.archive_rule(rule_id)
        self._audit("archive_rule", rule_id, user_id, {"reason": reason})
        return result

    # ── Health & Metrics ──────────────────────────────────────────────────

    def health(self) -> RuleHealth:
        """Return the current health status of the rule platform."""
        log.info("service.health")
        return self._manager.get_health()

    def get_metrics(self) -> RuleMetrics:
        """Return aggregated rule platform metrics."""
        log.info("service.get_metrics")
        return self._manager.get_metrics()
