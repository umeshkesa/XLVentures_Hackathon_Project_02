"""RuleManager — lightweight internal orchestrator.

Facade over RuleCoordinator. Validates operations, delegates
orchestration to the coordinator, and records events for audit
and observability.

RuleManager remains lightweight — no business logic lives here.
"""

from __future__ import annotations

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
    RuleLifecycleStatus,
    RuleType,
)
from adip.rules.orchestration.coordinator import RuleCoordinator

log = structlog.get_logger(__name__)


class RuleManager:
    """Lightweight internal orchestrator for all rule operations."""

    def __init__(self, coordinator: RuleCoordinator | None = None) -> None:
        self._coordinator = coordinator or RuleCoordinator()

    def create_rule(
        self,
        rule: Rule,
        created_by: str = "",
        change_summary: str = "",
    ) -> Rule:
        """Create a new rule."""
        rule_id = str(rule.rule_id)
        log.info("rule_manager.create_rule", rule_id=rule_id)
        return self._coordinator.create_rule(rule, created_by=created_by, change_summary=change_summary)

    def read_rule(self, rule_id: str) -> Rule | None:
        """Retrieve a rule by ID."""
        return self._coordinator.get_rule(rule_id)

    def update_rule(self, rule: Rule) -> Rule:
        """Update an existing rule."""
        log.info("rule_manager.update_rule", rule_id=str(rule.rule_id))
        return self._coordinator.update_rule(rule)

    def delete_rule(self, rule_id: str) -> bool:
        """Delete a rule."""
        log.info("rule_manager.delete_rule", rule_id=rule_id)
        return self._coordinator.delete_rule(rule_id)

    def search_rules(
        self,
        query: str = "",
        domain: RuleDomain | None = None,
        rule_type: RuleType | None = None,
        status: RuleLifecycleStatus | None = None,
        tags: list[str] | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Rule]:
        """Search for rules matching the given filters."""
        log.info("rule_manager.search_rules", query=query, domain=domain)
        # Simple in-memory filter (placeholder)
        results: list[Rule] = []
        query_lower = query.lower()

        # Access rules from coordinator
        for rule_id in list(self._coordinator._rules.keys()):
            rule = self._coordinator._rules[rule_id]
            if query and query_lower not in rule.name.lower() and query_lower not in rule.description.lower():
                continue
            if domain and rule.domain != domain:
                continue
            if rule_type and rule.rule_type != rule_type:
                continue
            if status and rule.status != status:
                continue
            if tags and not all(t in rule.tags for t in tags):
                continue
            results.append(rule)

        return results[offset:offset + limit]

    def evaluate_rules(
        self,
        context: RuleContext,
        domain: RuleDomain = RuleDomain.SYSTEM,
        strategy_type: EvaluationStrategyType | None = None,
    ) -> RuleEvaluation:
        """Evaluate rules matching the given context and domain."""
        log.info("rule_manager.evaluate_rules", domain=domain.value)
        return self._coordinator.evaluate(context, domain=domain, strategy_type=strategy_type)

    def create_ruleset(self, ruleset: RuleSet) -> RuleSet:
        """Create a new rule set."""
        log.info("rule_manager.create_ruleset", ruleset_id=str(ruleset.ruleset_id))
        return self._coordinator.create_ruleset(ruleset)

    def read_ruleset(self, ruleset_id: str) -> RuleSet | None:
        """Retrieve a rule set by ID."""
        return self._coordinator.get_ruleset(ruleset_id)

    def update_ruleset(self, ruleset: RuleSet) -> RuleSet:
        """Update an existing rule set."""
        log.info("rule_manager.update_ruleset", ruleset_id=str(ruleset.ruleset_id))
        return self._coordinator.update_ruleset(ruleset)

    def delete_ruleset(self, ruleset_id: str) -> bool:
        """Delete a rule set."""
        log.info("rule_manager.delete_ruleset", ruleset_id=ruleset_id)
        return self._coordinator.delete_ruleset(ruleset_id)

    def activate_rule(self, rule_id: str) -> Rule:
        """Activate a rule."""
        log.info("rule_manager.activate_rule", rule_id=rule_id)
        return self._coordinator.activate_rule(rule_id)

    def archive_rule(self, rule_id: str, reason: str = "") -> bool:
        """Archive a rule."""
        log.info("rule_manager.archive_rule", rule_id=rule_id)
        return self._coordinator.archive_rule(rule_id)

    def get_health(self) -> RuleHealth:
        """Return the current health status."""
        return self._coordinator.health()

    def get_metrics(self) -> RuleMetrics:
        """Return aggregated metrics."""
        return self._coordinator.metrics()
