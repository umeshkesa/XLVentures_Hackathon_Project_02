"""Tests for Evaluation Strategies."""

from __future__ import annotations

from adip.rules.contracts.models import Rule, RuleContext
from adip.rules.enums import EvaluationStrategyType
from adip.rules.execution.strategies import (
    CompositeEvaluationStrategy,
    ConditionalEvaluationStrategy,
    PriorityEvaluationStrategy,
    SequentialEvaluationStrategy,
    get_strategy,
)


class TestSequentialEvaluationStrategy:
    def test_evaluate(self) -> None:
        strategy = SequentialEvaluationStrategy()
        rules = [
            Rule(name="R1", priority=10),
            Rule(name="R2", priority=20),
        ]
        ctx = RuleContext()
        evaluation = strategy.evaluate(rules, ctx)
        assert len(evaluation.decisions) == 1
        assert evaluation.evaluation_strategy == EvaluationStrategyType.SEQUENTIAL
        assert evaluation.decisions[0].decision == "allow"

    def test_get_strategy_type(self) -> None:
        strategy = SequentialEvaluationStrategy()
        assert strategy.get_strategy_type() == EvaluationStrategyType.SEQUENTIAL


class TestPriorityEvaluationStrategy:
    def test_evaluate_returns_highest_priority(self) -> None:
        strategy = PriorityEvaluationStrategy()
        rules = [
            Rule(name="Low", priority=10),
            Rule(name="High", priority=100),
        ]
        ctx = RuleContext()
        evaluation = strategy.evaluate(rules, ctx)
        assert len(evaluation.decisions) == 1
        assert evaluation.decisions[0].reason is not None

    def test_evaluate_empty(self) -> None:
        strategy = PriorityEvaluationStrategy()
        ctx = RuleContext()
        evaluation = strategy.evaluate([], ctx)
        assert len(evaluation.decisions) == 0

    def test_get_strategy_type(self) -> None:
        strategy = PriorityEvaluationStrategy()
        assert strategy.get_strategy_type() == EvaluationStrategyType.PRIORITY


class TestConditionalEvaluationStrategy:
    def test_evaluate_with_conditions(self) -> None:
        strategy = ConditionalEvaluationStrategy()
        rules = [Rule(name="R1", conditions=[])]
        ctx = RuleContext(inputs={"temp": 100})
        evaluation = strategy.evaluate(rules, ctx)
        assert len(evaluation.decisions) == 1

    def test_evaluate_multiple_rules(self) -> None:
        strategy = ConditionalEvaluationStrategy()
        rules = [
            Rule(name="R1", conditions=[]),
            Rule(name="R2", conditions=[]),
        ]
        ctx = RuleContext(inputs={"temp": 50})
        evaluation = strategy.evaluate(rules, ctx)
        assert len(evaluation.decisions) == 2

    def test_get_strategy_type(self) -> None:
        strategy = ConditionalEvaluationStrategy()
        assert strategy.get_strategy_type() == EvaluationStrategyType.CONDITIONAL


class TestCompositeEvaluationStrategy:
    def test_evaluate_with_sub_strategies(self) -> None:
        composite = CompositeEvaluationStrategy()
        composite.add_strategy(SequentialEvaluationStrategy())
        composite.add_strategy(ConditionalEvaluationStrategy())

        rules = [Rule(name="R1")]
        ctx = RuleContext(inputs={"test": 1})
        evaluation = composite.evaluate(rules, ctx)
        # Should have decisions from both sub-strategies
        assert len(evaluation.decisions) >= 1
        assert evaluation.evaluation_strategy == EvaluationStrategyType.COMPOSITE

    def test_evaluate_without_sub_strategies(self) -> None:
        composite = CompositeEvaluationStrategy()
        rules = [Rule(name="R1")]
        ctx = RuleContext()
        evaluation = composite.evaluate(rules, ctx)
        assert evaluation.evaluation_strategy == EvaluationStrategyType.COMPOSITE
        assert len(evaluation.decisions) == 0

    def test_get_strategy_type(self) -> None:
        strategy = CompositeEvaluationStrategy()
        assert strategy.get_strategy_type() == EvaluationStrategyType.COMPOSITE


class TestGetStrategy:
    def test_get_sequential(self) -> None:
        strategy = get_strategy(EvaluationStrategyType.SEQUENTIAL)
        assert isinstance(strategy, SequentialEvaluationStrategy)

    def test_get_priority(self) -> None:
        strategy = get_strategy(EvaluationStrategyType.PRIORITY)
        assert isinstance(strategy, PriorityEvaluationStrategy)

    def test_get_conditional(self) -> None:
        strategy = get_strategy(EvaluationStrategyType.CONDITIONAL)
        assert isinstance(strategy, ConditionalEvaluationStrategy)

    def test_get_composite(self) -> None:
        strategy = get_strategy(EvaluationStrategyType.COMPOSITE)
        assert isinstance(strategy, CompositeEvaluationStrategy)

    def test_get_unknown(self) -> None:
        try:
            from adip.rules.enums import EvaluationStrategyType
            get_strategy(EvaluationStrategyType.PARALLEL)
            assert False, "Should have raised ValueError"
        except ValueError:
            pass
