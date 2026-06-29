"""Tests for PriorityEngine."""

from __future__ import annotations

from adip.rules.contracts.models import Rule, RuleContext
from adip.rules.enums import EvaluationStrategyType, RuleDomain
from adip.rules.execution.priority_engine import PriorityEngine


class TestPriorityEngine:
    def test_order_rules_priority_descending(self) -> None:
        engine = PriorityEngine()
        rules = [
            Rule(name="Low", priority=10),
            Rule(name="Medium", priority=50),
            Rule(name="High", priority=100),
        ]
        ordered = engine.order_rules(rules, EvaluationStrategyType.PRIORITY)
        assert ordered[0].name == "High"
        assert ordered[1].name == "Medium"
        assert ordered[2].name == "Low"

    def test_order_rules_sequential(self) -> None:
        engine = PriorityEngine()
        rules = [
            Rule(name="A", priority=100),
            Rule(name="B", priority=10),
        ]
        ordered = engine.order_rules(rules, EvaluationStrategyType.SEQUENTIAL)
        assert ordered[0].name == "A"
        assert ordered[1].name == "B"

    def test_get_effective_priority(self) -> None:
        engine = PriorityEngine()
        rule = Rule(name="Test", priority=50, domain=RuleDomain.ENERGY)
        priority = engine.get_effective_priority(rule)
        assert priority == 50

    def test_get_effective_priority_with_domain_boost(self) -> None:
        engine = PriorityEngine()
        rule = Rule(name="Test", priority=50, domain=RuleDomain.ENERGY)
        ctx = RuleContext(domain=RuleDomain.ENERGY, attributes={"type": "turbine"})
        priority = engine.get_effective_priority(rule, ctx)
        assert priority == 100  # 50 + 50 domain boost

    def test_get_effective_priority_different_domain(self) -> None:
        engine = PriorityEngine()
        rule = Rule(name="Test", priority=50, domain=RuleDomain.ENERGY)
        ctx = RuleContext(domain=RuleDomain.SYSTEM, attributes={"type": "server"})
        priority = engine.get_effective_priority(rule, ctx)
        assert priority == 50

    def test_get_effective_priority_no_context(self) -> None:
        engine = PriorityEngine()
        rule = Rule(name="Test", priority=0)
        priority = engine.get_effective_priority(rule, None)
        assert priority == 0

    def test_resolve_tie(self) -> None:
        engine = PriorityEngine()
        rules = [
            Rule(name="A", priority=50),
            Rule(name="B", priority=50),
        ]
        winner = engine.resolve_tie(rules)
        assert winner is not None
        assert winner.name == "A"

    def test_resolve_tie_empty(self) -> None:
        engine = PriorityEngine()
        winner = engine.resolve_tie([])
        assert winner is None
