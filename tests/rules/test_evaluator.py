"""Tests for RuleEvaluator."""

from __future__ import annotations

from adip.rules.contracts.models import Rule, RuleContext, RuleSet
from adip.rules.enums import EvaluationStrategyType
from adip.rules.execution.evaluator import RuleEvaluator


class TestRuleEvaluator:
    def test_evaluate_rule(self) -> None:
        evaluator = RuleEvaluator()
        rule = Rule(name="Test Rule")
        ctx = RuleContext(inputs={"value": 100})
        decision = evaluator.evaluate_rule(rule, ctx)
        assert decision.rule_id == rule.rule_id
        assert decision.decision == "allow"
        assert decision.matched is True

    def test_evaluate_ruleset_default_strategy(self) -> None:
        evaluator = RuleEvaluator()
        ruleset = RuleSet(
            name="Test Set",
            rules=[Rule(name="R1"), Rule(name="R2")],
        )
        ctx = RuleContext()
        evaluation = evaluator.evaluate_ruleset(ruleset, ctx)
        assert len(evaluation.rules_evaluated) == 2
        assert evaluation.evaluation_strategy == EvaluationStrategyType.SEQUENTIAL

    def test_evaluate_ruleset_priority_strategy(self) -> None:
        evaluator = RuleEvaluator()
        ruleset = RuleSet(
            name="Test Set",
            rules=[Rule(name="R1", priority=10), Rule(name="R2", priority=100)],
        )
        ctx = RuleContext()
        evaluation = evaluator.evaluate_ruleset(
            ruleset, ctx, strategy_type=EvaluationStrategyType.PRIORITY
        )
        assert evaluation.evaluation_strategy == EvaluationStrategyType.PRIORITY
        assert len(evaluation.rules_evaluated) == 2

    def test_get_supported_strategies(self) -> None:
        evaluator = RuleEvaluator()
        strategies = evaluator.get_supported_strategies()
        assert EvaluationStrategyType.SEQUENTIAL in strategies
        assert EvaluationStrategyType.PRIORITY in strategies
        assert EvaluationStrategyType.CONDITIONAL in strategies
        assert EvaluationStrategyType.COMPOSITE in strategies
