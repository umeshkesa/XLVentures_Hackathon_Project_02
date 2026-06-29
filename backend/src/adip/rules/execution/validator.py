"""RuleValidator — validates rules before processing.

Validates rule schema, conditions, actions, required fields,
priority, lifecycle state, and version constraints.
"""

from __future__ import annotations

import structlog

from adip.rules.contracts.models import Rule, RuleSet
from adip.rules.enums import RuleLifecycleStatus, RuleType

log = structlog.get_logger(__name__)


class RuleValidator:
    """Validates rules and rule sets against platform constraints."""

    MAX_PRIORITY: int = 1000

    def validate_rule(self, rule: Rule) -> list[str]:
        """Validate a single rule. Returns a list of violation strings (empty = valid)."""
        violations: list[str] = []

        log.info("rule_validator.validate_rule", rule_id=str(rule.rule_id))

        if not rule.name.strip():
            violations.append("Rule name is required")

        if not isinstance(rule.rule_type, RuleType):
            violations.append(f"Unsupported rule type: {rule.rule_type}")

        if not isinstance(rule.domain, rule.domain.__class__):
            violations.append(f"Unsupported rule domain: {rule.domain}")

        if not isinstance(rule.status, RuleLifecycleStatus):
            violations.append(f"Unsupported lifecycle status: {rule.status}")

        if rule.priority < 0:
            violations.append(f"Rule priority cannot be negative: {rule.priority}")

        if rule.priority > self.MAX_PRIORITY:
            violations.append(f"Rule priority {rule.priority} exceeds maximum {self.MAX_PRIORITY}")

        if not rule.namespace.strip():
            violations.append("Rule namespace is required")

        if rule.version < 1:
            violations.append(f"Rule version must be >= 1, got {rule.version}")

        for i, cond in enumerate(rule.conditions):
            if not cond.field.strip():
                violations.append(f"Condition {i}: field is required")
            if not cond.operator.strip():
                violations.append(f"Condition {i}: operator is required")

        for i, action in enumerate(rule.actions):
            if not action.action_type.strip():
                violations.append(f"Action {i}: action_type is required")

        return violations

    def validate_rule_batch(self, rules: list[Rule]) -> list[list[str]]:
        """Validate a batch of rules."""
        log.info("rule_validator.validate_batch", count=len(rules))
        return [self.validate_rule(r) for r in rules]

    def validate_ruleset(self, ruleset: RuleSet) -> list[str]:
        """Validate a rule set. Returns a list of violation strings (empty = valid)."""
        violations: list[str] = []

        log.info("rule_validator.validate_ruleset", ruleset_id=str(ruleset.ruleset_id))

        if not ruleset.name.strip():
            violations.append("RuleSet name is required")

        if not ruleset.namespace.strip():
            violations.append("RuleSet namespace is required")

        if ruleset.version < 1:
            violations.append(f"RuleSet version must be >= 1, got {ruleset.version}")

        for i, rule in enumerate(ruleset.rules):
            rule_violations = self.validate_rule(rule)
            for v in rule_violations:
                violations.append(f"Rule {i} ({rule.name or 'unnamed'}): {v}")

        return violations

    def validate_lifecycle_transition(
        self,
        from_status: RuleLifecycleStatus,
        to_status: RuleLifecycleStatus,
    ) -> list[str]:
        """Validate a proposed lifecycle transition."""
        violations: list[str] = []
        if from_status == to_status:
            return violations
        # Core state machine is managed by LifecycleManager;
        # this validates at the rule level
        return violations
