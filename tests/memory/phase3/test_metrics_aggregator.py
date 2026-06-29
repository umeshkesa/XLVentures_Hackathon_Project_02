"""Tests for MetricsAggregator."""

from __future__ import annotations

from adip.memory.enums import MemoryDomain
from adip.memory.orchestration.metrics_aggregator import MetricsAggregator


class TestMetricsAggregator:
    def test_initial_state(self) -> None:
        agg = MetricsAggregator()
        snap = agg.snapshot()
        assert snap["operations_total"] == 0
        assert snap["sessions_total"] == 0
        assert snap["reads_total"] == 0
        assert snap["writes_total"] == 0
        assert snap["searches_total"] == 0
        assert snap["cache_hits"] == 0
        assert snap["cache_misses"] == 0
        assert snap["routing_decisions"] == 0
        assert snap["lifecycle_transitions"] == 0
        assert snap["policy_violations"] == 0
        assert snap["memory_usage"] == {}
        assert snap["operations_per_domain"] == {}
        assert snap["latency_per_domain"] == {}
        assert snap["tier_utilization"] == {}

    def test_increment_operations(self) -> None:
        agg = MetricsAggregator()
        agg.increment_operations(5)
        assert agg.snapshot()["operations_total"] == 5

    def test_increment_sessions(self) -> None:
        agg = MetricsAggregator()
        agg.increment_sessions()
        assert agg.snapshot()["sessions_total"] == 1

    def test_increment_reads(self) -> None:
        agg = MetricsAggregator()
        agg.increment_reads(3)
        assert agg.snapshot()["reads_total"] == 3

    def test_increment_writes(self) -> None:
        agg = MetricsAggregator()
        agg.increment_writes(2)
        assert agg.snapshot()["writes_total"] == 2

    def test_increment_searches(self) -> None:
        agg = MetricsAggregator()
        agg.increment_searches()
        assert agg.snapshot()["searches_total"] == 1

    def test_cache_hits_misses(self) -> None:
        agg = MetricsAggregator()
        agg.increment_cache_hits(3)
        agg.increment_cache_misses(1)
        snap = agg.snapshot()
        assert snap["cache_hits"] == 3
        assert snap["cache_misses"] == 1

    def test_routing_decisions(self) -> None:
        agg = MetricsAggregator()
        agg.increment_routing_decisions(4)
        assert agg.snapshot()["routing_decisions"] == 4

    def test_lifecycle_transitions(self) -> None:
        agg = MetricsAggregator()
        agg.increment_lifecycle_transitions(2)
        assert agg.snapshot()["lifecycle_transitions"] == 2

    def test_policy_violations(self) -> None:
        agg = MetricsAggregator()
        agg.increment_policy_violations()
        assert agg.snapshot()["policy_violations"] == 1

    def test_operation_for_domain(self) -> None:
        agg = MetricsAggregator()
        agg.record_operation_for_domain(MemoryDomain.PLANNER, 10.5)
        agg.record_operation_for_domain(MemoryDomain.PLANNER, 20.3)
        agg.record_operation_for_domain(MemoryDomain.WORKFLOW, 5.0)
        snap = agg.snapshot()
        assert snap["operations_per_domain"]["PLANNER"] == 2
        assert snap["operations_per_domain"]["WORKFLOW"] == 1
        assert snap["latency_per_domain"]["PLANNER"] == 15.4  # (10.5 + 20.3) / 2
        assert snap["latency_per_domain"]["WORKFLOW"] == 5.0

    def test_tier_utilization(self) -> None:
        agg = MetricsAggregator()
        agg.record_tier_utilization("HOT", 10)
        agg.record_tier_utilization("WARM", 5)
        agg.record_tier_utilization("HOT", 3)
        snap = agg.snapshot()
        assert snap["tier_utilization"]["HOT"] == 13
        assert snap["tier_utilization"]["WARM"] == 5

    def test_memory_usage(self) -> None:
        agg = MetricsAggregator()
        agg.set_memory_usage({"HOT": 100, "WARM": 200, "COLD": 50})
        assert agg.snapshot()["memory_usage"] == {"HOT": 100, "WARM": 200, "COLD": 50}

    def test_increment_updates(self) -> None:
        agg = MetricsAggregator()
        agg.increment_updates(3)
        snap = agg.snapshot()
        assert snap["updates_total"] == 3

    def test_increment_deletes(self) -> None:
        agg = MetricsAggregator()
        agg.increment_deletes(2)
        snap = agg.snapshot()
        assert snap["deletes_total"] == 2

    def test_increment_archives(self) -> None:
        agg = MetricsAggregator()
        agg.increment_archives(1)
        snap = agg.snapshot()
        assert snap["archives_total"] == 1

    def test_increment_restores(self) -> None:
        agg = MetricsAggregator()
        agg.increment_restores(4)
        snap = agg.snapshot()
        assert snap["restores_total"] == 4

    def test_cache_hit_ratio_default_zero(self) -> None:
        agg = MetricsAggregator()
        assert agg.cache_hit_ratio == 0.0

    def test_cache_hit_ratio_all_hits(self) -> None:
        agg = MetricsAggregator()
        agg.increment_cache_hits(10)
        assert agg.cache_hit_ratio == 1.0

    def test_cache_hit_ratio_all_misses(self) -> None:
        agg = MetricsAggregator()
        agg.increment_cache_misses(5)
        assert agg.cache_hit_ratio == 0.0

    def test_cache_hit_ratio_mixed(self) -> None:
        agg = MetricsAggregator()
        agg.increment_cache_hits(7)
        agg.increment_cache_misses(3)
        assert agg.cache_hit_ratio == 0.7

    def test_cache_hit_ratio_in_snapshot(self) -> None:
        agg = MetricsAggregator()
        agg.increment_cache_hits(9)
        agg.increment_cache_misses(1)
        snap = agg.snapshot()
        assert snap["cache_hit_ratio"] == 0.9

    def test_reset(self) -> None:
        agg = MetricsAggregator()
        agg.increment_operations(10)
        agg.increment_reads(5)
        agg.increment_updates(3)
        agg.increment_deletes(2)
        agg.increment_archives(1)
        agg.increment_restores(4)
        agg.record_operation_for_domain(MemoryDomain.SYSTEM)
        agg.reset()
        snap = agg.snapshot()
        assert snap["operations_total"] == 0
        assert snap["reads_total"] == 0
        assert snap["updates_total"] == 0
        assert snap["deletes_total"] == 0
        assert snap["archives_total"] == 0
        assert snap["restores_total"] == 0
        assert snap["operations_per_domain"] == {}
