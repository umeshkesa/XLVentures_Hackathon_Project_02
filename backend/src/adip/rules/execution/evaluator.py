"""RuleEvaluator — placeholder evaluation of rules.

Evaluates one rule or a RuleSet and returns RuleDecision and
RuleEvaluation results. No business logic — deterministic
placeholder only.
"""

from __future__ import annotations

import structlog

from adip.rules.contracts.models import Rule, RuleContext, RuleDecision, RuleEvaluation, RuleSet
from adip.rules.enums import EvaluationStrategyType
from adip.rules.execution.strategies import get_strategy

log = structlog.get_logger(__name__)


class RuleEvaluator:
    """Evaluates rules against a given context.

    Delegates to the configured EvaluationStrategy for the actual
    evaluation approach.
    """

    def __init__(self) -> None:
        self._default_strategy_type: EvaluationStrategyType = EvaluationStrategyType.SEQUENTIAL

    def evaluate_rule(
        self,
        rule: Rule,
        context: RuleContext,
    ) -> RuleDecision:
        """Evaluate a single rule against the given context.

        Placeholder — returns a basic RuleDecision without
        business logic.
        """
        rule_id = str(rule.rule_id)
        log.info("rule_evaluator.evaluate_rule", rule_id=rule_id)

        return RuleDecision(
            context_id=context.context_id,
            rule_id=rule.rule_id,
            decision="allow",
            matched=True,
            reason=f"Placeholder evaluation of rule: {rule.name}",
            confidence=1.0,
            evaluation_time_ms=1.0,
        )

    def evaluate_ruleset(
        self,
        ruleset: RuleSet,
        context: RuleContext,
        strategy_type: EvaluationStrategyType | None = None,
    ) -> RuleEvaluation:
        """Evaluate all rules in a rule set against the given context.

        Uses the specified strategy or the ruleset's default strategy.
        """
        ruleset_id = str(ruleset.ruleset_id)
        log.info("rule_evaluator.evaluate_ruleset", ruleset_id=ruleset_id)

        effective_strategy = strategy_type or ruleset.evaluation_strategy or self._default_strategy_type
        strategy = get_strategy(effective_strategy)

        return strategy.evaluate(ruleset.rules, context)

    def get_supported_strategies(self) -> list[EvaluationStrategyType]:
        """Return the evaluation strategies this evaluator supports."""
        return list(EvaluationStrategyType)
