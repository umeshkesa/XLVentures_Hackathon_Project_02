"""PriorityEngine — determines rule priority ordering for evaluation.

Computes the effective priority of rules, considering explicit
priority values, rule type precedence, domain precedence, and
dependency ordering.
"""

from __future__ import annotations

import structlog

from adip.rules.contracts.models import Rule, RuleContext
from adip.rules.enums import EvaluationStrategyType

log = structlog.get_logger(__name__)


class PriorityEngine:
    """Computes rule priority ordering for evaluation."""

    def order_rules(
        self,
        rules: list[Rule],
        strategy: EvaluationStrategyType = EvaluationStrategyType.PRIORITY,
    ) -> list[Rule]:
        """Order rules by their effective priority for evaluation."""
        log.info("priority_engine.order_rules", count=len(rules), strategy=strategy.value)

        if strategy == EvaluationStrategyType.PRIORITY:
            return sorted(rules, key=lambda r: r.priority, reverse=True)
        elif strategy == EvaluationStrategyType.SEQUENTIAL:
            return list(rules)
        else:
            return sorted(rules, key=lambda r: r.priority, reverse=True)

    def get_effective_priority(
        self,
        rule: Rule,
        context: RuleContext | None = None,
    ) -> int:
        """Compute the effective priority of a rule.

        Placeholder — returns the rule's explicit priority.
        """
        log.info("priority_engine.get_effective_priority", rule_id=str(rule.rule_id))

        effective = rule.priority

        if context and context.attributes:
            domain_boost = 0
            context_domain = context.domain.value
            rule_domain = rule.domain.value
            if context_domain == rule_domain:
                domain_boost = 50
            effective += domain_boost

        return max(0, effective)

    def resolve_tie(
        self,
        rules: list[Rule],
    ) -> Rule | None:
        """Resolve a tie between rules with equal priority.

        Placeholder — returns the first rule.
        """
        if not rules:
            return None
        log.info("priority_engine.resolve_tie", count=len(rules))
        return rules[0]
