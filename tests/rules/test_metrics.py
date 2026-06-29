"""Tests for RuleMetricsCollector."""

from __future__ import annotations

from adip.rules.execution.metrics import RuleMetricsCollector


class TestRuleMetricsCollector:
    def test_defaults(self) -> None:
        collector = RuleMetricsCollector()
        metrics = collector.snapshot()
        assert metrics.rules_total == 0
        assert metrics.evaluations_total == 0
        assert metrics.cache_hits == 0
        assert metrics.conflicts_total == 0

    def test_increment_rules(self) -> None:
        collector = RuleMetricsCollector()
        collector.increment_rules()
        assert collector.snapshot().rules_total == 1

    def test_increment_rules_with_domain(self) -> None:
        collector = RuleMetricsCollector()
        collector.increment_rules(domain="ENERGY", rule_type="SAFETY")
        metrics = collector.snapshot()
        assert metrics.rules_per_domain.get("ENERGY") == 1
        assert metrics.rules_per_type.get("SAFETY") == 1

    def test_increment_evaluations(self) -> None:
        collector = RuleMetricsCollector()
        collector.increment_evaluations()
        assert collector.snapshot().evaluations_total == 1

    def test_increment_decisions(self) -> None:
        collector = RuleMetricsCollector()
        collector.increment_decisions(3)
        assert collector.snapshot().decisions_total == 3

    def test_increment_conflicts(self) -> None:
        collector = RuleMetricsCollector()
        collector.increment_conflicts()
        assert collector.snapshot().conflicts_total == 1

    def test_increment_cache_hits_and_misses(self) -> None:
        collector = RuleMetricsCollector()
        collector.increment_cache_hits()
        collector.increment_cache_hits()
        collector.increment_cache_misses()
        metrics = collector.snapshot()
        assert metrics.cache_hits == 2
        assert metrics.cache_misses == 1

    def test_increment_strategy_usage(self) -> None:
        collector = RuleMetricsCollector()
        collector.increment_strategy_usage("SEQUENTIAL")
        collector.increment_strategy_usage("PRIORITY")
        collector.increment_strategy_usage("SEQUENTIAL")
        metrics = collector.snapshot()
        assert metrics.strategy_usage["SEQUENTIAL"] == 2
        assert metrics.strategy_usage["PRIORITY"] == 1

    def test_increment_domain_usage(self) -> None:
        collector = RuleMetricsCollector()
        collector.increment_domain_usage("ENERGY")
        collector.increment_domain_usage("SAFETY")
        metrics = collector.snapshot()
        assert metrics.domain_usage["ENERGY"] == 1
        assert metrics.domain_usage["SAFETY"] == 1

    def test_record_evaluation_time(self) -> None:
        collector = RuleMetricsCollector()
        collector.record_evaluation_time(10.5)
        collector.record_evaluation_time(20.5)
        metrics = collector.snapshot()
        assert metrics.average_evaluation_time_ms == 15.5

    def test_record_decision_time(self) -> None:
        collector = RuleMetricsCollector()
        collector.record_decision_time(5.0)
        collector.record_decision_time(15.0)
        metrics = collector.snapshot()
        assert metrics.average_decision_time_ms == 10.0

    def test_increment_rulesets(self) -> None:
        collector = RuleMetricsCollector()
        collector.increment_rulesets()
        assert collector.snapshot().rulesets_total == 1

    def test_reset(self) -> None:
        collector = RuleMetricsCollector()
        collector.increment_rules()
        collector.increment_evaluations()
        collector.increment_cache_hits()
        collector.record_evaluation_time(10.0)
        collector.reset()
        metrics = collector.snapshot()
        assert metrics.rules_total == 0
        assert metrics.evaluations_total == 0
        assert metrics.cache_hits == 0
        assert metrics.average_evaluation_time_ms == 0.0
        assert metrics.strategy_usage == {}
