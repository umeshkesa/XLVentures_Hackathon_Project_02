"""Evaluation strategies for the Rule Manager.

Implements the Strategy Pattern for rule evaluation approaches:
Sequential, Priority, Conditional, and Composite strategies.

Each strategy provides a deterministic placeholder implementation
that returns basic evaluation results without business logic.
"""

from __future__ import annotations

import structlog

from adip.rules.contracts.models import Rule, RuleContext, RuleDecision, RuleEvaluation
from adip.rules.enums import EvaluationStrategyType

log = structlog.get_logger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Base EvaluationStrategy
# ─────────────────────────────────────────────────────────────────────────────


class EvaluationStrategy:
    """Base strategy for evaluating a set of rules.

    Each concrete strategy implements a different evaluation approach
    while conforming to this common interface.
    """

    def evaluate(
        self,
        rules: list[Rule],
        context: RuleContext,
    ) -> RuleEvaluation:
        """Evaluate the given rules against the context using this strategy."""
        raise NotImplementedError

    def get_strategy_type(self) -> EvaluationStrategyType:
        """Return the evaluation strategy type."""
        raise NotImplementedError


# ─────────────────────────────────────────────────────────────────────────────
# SequentialEvaluationStrategy
# ─────────────────────────────────────────────────────────────────────────────


class SequentialEvaluationStrategy(EvaluationStrategy):
    """Evaluate rules in order, stop at first match."""

    def evaluate(
        self,
        rules: list[Rule],
        context: RuleContext,
    ) -> RuleEvaluation:
        """Evaluate rules sequentially, returning first match."""
        log.info("strategy.sequential.evaluate", rule_count=len(rules))

        decisions: list[RuleDecision] = []
        for rule in rules:
            decision = RuleDecision(
                context_id=context.context_id,
                rule_id=rule.rule_id,
                decision="allow",
                matched=True,
                reason=f"Sequential evaluation matched rule: {rule.name}",
                evaluation_time_ms=1.0,
            )
            decisions.append(decision)
            break

        return RuleEvaluation(
            context=context,
            rules_evaluated=[r.rule_id for r in rules],
            decisions=decisions,
            evaluation_strategy=EvaluationStrategyType.SEQUENTIAL,
            total_evaluation_time_ms=len(rules) * 1.0,
        )

    def get_strategy_type(self) -> EvaluationStrategyType:
        return EvaluationStrategyType.SEQUENTIAL


# ─────────────────────────────────────────────────────────────────────────────
# PriorityEvaluationStrategy
# ─────────────────────────────────────────────────────────────────────────────


class PriorityEvaluationStrategy(EvaluationStrategy):
    """Evaluate rules by priority, highest priority wins."""

    def evaluate(
        self,
        rules: list[Rule],
        context: RuleContext,
    ) -> RuleEvaluation:
        """Evaluate rules ordered by priority, returning highest priority match."""
        log.info("strategy.priority.evaluate", rule_count=len(rules))

        sorted_rules = sorted(rules, key=lambda r: r.priority, reverse=True)
        decisions: list[RuleDecision] = []

        if sorted_rules:
            top = sorted_rules[0]
            decision = RuleDecision(
                context_id=context.context_id,
                rule_id=top.rule_id,
                decision="allow",
                matched=True,
                reason=f"Priority evaluation matched rule: {top.name} (priority={top.priority})",
                evaluation_time_ms=1.0,
            )
            decisions.append(decision)

        return RuleEvaluation(
            context=context,
            rules_evaluated=[r.rule_id for r in rules],
            decisions=decisions,
            evaluation_strategy=EvaluationStrategyType.PRIORITY,
            total_evaluation_time_ms=len(rules) * 1.0,
        )

    def get_strategy_type(self) -> EvaluationStrategyType:
        return EvaluationStrategyType.PRIORITY


# ─────────────────────────────────────────────────────────────────────────────
# ConditionalEvaluationStrategy
# ─────────────────────────────────────────────────────────────────────────────


class ConditionalEvaluationStrategy(EvaluationStrategy):
    """Evaluate rules based on condition matching."""

    def evaluate(
        self,
        rules: list[Rule],
        context: RuleContext,
    ) -> RuleEvaluation:
        """Evaluate rules by checking conditions against context inputs."""
        log.info("strategy.conditional.evaluate", rule_count=len(rules))

        decisions: list[RuleDecision] = []

        for rule in rules:
            matched = bool(rule.conditions and context.inputs)
            reason = (
                f"Conditional evaluation matched rule: {rule.name}"
                if matched
                else f"Conditional evaluation did not match rule: {rule.name}"
            )
            decision = RuleDecision(
                context_id=context.context_id,
                rule_id=rule.rule_id,
                decision="allow" if matched else "deny",
                matched=matched,
                reason=reason,
                evaluation_time_ms=2.0,
            )
            decisions.append(decision)

        return RuleEvaluation(
            context=context,
            rules_evaluated=[r.rule_id for r in rules],
            decisions=decisions,
            evaluation_strategy=EvaluationStrategyType.CONDITIONAL,
            total_evaluation_time_ms=len(rules) * 2.0,
        )

    def get_strategy_type(self) -> EvaluationStrategyType:
        return EvaluationStrategyType.CONDITIONAL


# ─────────────────────────────────────────────────────────────────────────────
# CompositeEvaluationStrategy
# ─────────────────────────────────────────────────────────────────────────────


class CompositeEvaluationStrategy(EvaluationStrategy):
    """Combine multiple strategies for complex evaluation."""

    def __init__(self, strategies: list[EvaluationStrategy] | None = None) -> None:
        self._strategies: list[EvaluationStrategy] = strategies or []

    def add_strategy(self, strategy: EvaluationStrategy) -> None:
        """Add a sub-strategy to the composite."""
        self._strategies.append(strategy)

    def evaluate(
        self,
        rules: list[Rule],
        context: RuleContext,
    ) -> RuleEvaluation:
        """Evaluate using all registered sub-strategies and merge results."""
        log.info("strategy.composite.evaluate", strategy_count=len(self._strategies), rule_count=len(rules))

        all_decisions: list[RuleDecision] = []
        total_time = 0.0

        for strategy in self._strategies:
            evaluation = strategy.evaluate(rules, context)
            all_decisions.extend(evaluation.decisions)
            total_time += evaluation.total_evaluation_time_ms

        return RuleEvaluation(
            context=context,
            rules_evaluated=[r.rule_id for r in rules],
            decisions=all_decisions,
            evaluation_strategy=EvaluationStrategyType.COMPOSITE,
            total_evaluation_time_ms=total_time,
        )

    def get_strategy_type(self) -> EvaluationStrategyType:
        return EvaluationStrategyType.COMPOSITE


# ─────────────────────────────────────────────────────────────────────────────
# Factory
# ─────────────────────────────────────────────────────────────────────────────


def get_strategy(strategy_type: EvaluationStrategyType) -> EvaluationStrategy:
    """Factory method to get an evaluation strategy by type."""
    strategies = {
        EvaluationStrategyType.SEQUENTIAL: SequentialEvaluationStrategy(),
        EvaluationStrategyType.PRIORITY: PriorityEvaluationStrategy(),
        EvaluationStrategyType.CONDITIONAL: ConditionalEvaluationStrategy(),
        EvaluationStrategyType.COMPOSITE: CompositeEvaluationStrategy(),
    }
    strategy = strategies.get(strategy_type)
    if strategy is None:
        raise ValueError(f"Unsupported evaluation strategy: {strategy_type}")
    return strategy
