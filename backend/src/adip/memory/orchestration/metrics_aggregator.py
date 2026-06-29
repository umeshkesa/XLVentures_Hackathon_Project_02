"""MetricsAggregator — aggregated enterprise metrics for the Memory Platform.

Extends the basic MetricsCollector from Phase 2 with domain-aware,
tier-aware, and operation-type-aware metrics aggregation.
"""

from __future__ import annotations

from typing import Any

import structlog

from adip.memory.enums import MemoryDomain

log = structlog.get_logger(__name__)


class MetricsAggregator:
    """Aggregates enterprise-level metrics across all memory operations.

    Tracks operations, sessions, reads, writes, searches, cache
    operations, routing decisions, lifecycle transitions, policy
    violations, memory usage, domain-aware metrics, tier utilization,
    and latency per domain.
    """

    def __init__(self) -> None:
        self._operations_total: int = 0
        self._sessions_total: int = 0
        self._reads_total: int = 0
        self._writes_total: int = 0
        self._updates_total: int = 0
        self._deletes_total: int = 0
        self._archives_total: int = 0
        self._restores_total: int = 0
        self._searches_total: int = 0
        self._cache_hits: int = 0
        self._cache_misses: int = 0
        self._routing_decisions: int = 0
        self._lifecycle_transitions: int = 0
        self._policy_violations: int = 0
        self._memory_usage: dict[str, int] = {}
        self._operations_per_domain: dict[str, int] = {}
        self._latency_per_domain: dict[str, list[float]] = {}
        self._tier_utilization: dict[str, int] = {}

    def increment_operations(self, count: int = 1) -> None:
        self._operations_total += count

    def increment_sessions(self, count: int = 1) -> None:
        self._sessions_total += count

    def increment_reads(self, count: int = 1) -> None:
        self._reads_total += count

    def increment_writes(self, count: int = 1) -> None:
        self._writes_total += count

    def increment_updates(self, count: int = 1) -> None:
        self._updates_total += count

    def increment_deletes(self, count: int = 1) -> None:
        self._deletes_total += count

    def increment_archives(self, count: int = 1) -> None:
        self._archives_total += count

    def increment_restores(self, count: int = 1) -> None:
        self._restores_total += count

    def increment_searches(self, count: int = 1) -> None:
        self._searches_total += count

    def increment_cache_hits(self, count: int = 1) -> None:
        self._cache_hits += count

    def increment_cache_misses(self, count: int = 1) -> None:
        self._cache_misses += count

    def increment_routing_decisions(self, count: int = 1) -> None:
        self._routing_decisions += count

    def increment_lifecycle_transitions(self, count: int = 1) -> None:
        self._lifecycle_transitions += count

    def increment_policy_violations(self, count: int = 1) -> None:
        self._policy_violations += count

    def record_operation_for_domain(self, domain: MemoryDomain, latency_ms: float = 0.0) -> None:
        key = domain.value
        self._operations_per_domain[key] = self._operations_per_domain.get(key, 0) + 1
        if latency_ms > 0:
            self._latency_per_domain.setdefault(key, []).append(latency_ms)

    def record_tier_utilization(self, tier: str, count: int = 1) -> None:
        self._tier_utilization[tier] = self._tier_utilization.get(tier, 0) + count

    def set_memory_usage(self, usage: dict[str, int]) -> None:
        self._memory_usage = dict(usage)

    @property
    def cache_hit_ratio(self) -> float:
        total = self._cache_hits + self._cache_misses
        if total == 0:
            return 0.0
        return round(self._cache_hits / total, 4)

    def snapshot(self) -> dict[str, Any]:
        avg_latency_per_domain: dict[str, float] = {}
        for domain, latencies in self._latency_per_domain.items():
            if latencies:
                avg_latency_per_domain[domain] = round(sum(latencies) / len(latencies), 2)

        return {
            "operations_total": self._operations_total,
            "sessions_total": self._sessions_total,
            "reads_total": self._reads_total,
            "writes_total": self._writes_total,
            "updates_total": self._updates_total,
            "deletes_total": self._deletes_total,
            "archives_total": self._archives_total,
            "restores_total": self._restores_total,
            "searches_total": self._searches_total,
            "cache_hits": self._cache_hits,
            "cache_misses": self._cache_misses,
            "cache_hit_ratio": self.cache_hit_ratio,
            "routing_decisions": self._routing_decisions,
            "lifecycle_transitions": self._lifecycle_transitions,
            "policy_violations": self._policy_violations,
            "memory_usage": dict(self._memory_usage),
            "operations_per_domain": dict(self._operations_per_domain),
            "latency_per_domain": avg_latency_per_domain,
            "tier_utilization": dict(self._tier_utilization),
        }

    def reset(self) -> None:
        self._operations_total = 0
        self._sessions_total = 0
        self._reads_total = 0
        self._writes_total = 0
        self._updates_total = 0
        self._deletes_total = 0
        self._archives_total = 0
        self._restores_total = 0
        self._searches_total = 0
        self._cache_hits = 0
        self._cache_misses = 0
        self._routing_decisions = 0
        self._lifecycle_transitions = 0
        self._policy_violations = 0
        self._memory_usage.clear()
        self._operations_per_domain.clear()
        self._latency_per_domain.clear()
        self._tier_utilization.clear()
