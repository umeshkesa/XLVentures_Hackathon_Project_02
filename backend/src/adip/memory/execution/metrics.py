"""MetricsCollector — tracks operational metrics for the Memory Manager.

Records read/write/search counts, cache hits/misses, routing decisions,
policy violations, lifecycle transitions, latency, and record counts
by tier and state.
"""

from __future__ import annotations

from typing import Any

import structlog

from adip.memory.contracts.models import MemoryMetrics

log = structlog.get_logger(__name__)


class MetricsCollector:
    """Collects and aggregates Memory Manager performance metrics."""

    def __init__(self) -> None:
        self._metrics = MemoryMetrics()
        self._routing_decisions: int = 0
        self._policy_violations: int = 0
        self._lifecycle_transitions: int = 0
        self._search_count: int = 0

    # ── Incrementers ──────────────────────────────────────────────────────

    def increment_reads(self, count: int = 1) -> None:
        self._metrics.reads += count

    def increment_writes(self, count: int = 1) -> None:
        self._metrics.writes += count

    def increment_cache_hits(self, count: int = 1) -> None:
        self._metrics.cache_hits += count

    def increment_cache_misses(self, count: int = 1) -> None:
        self._metrics.cache_misses += count

    def increment_searches(self, count: int = 1) -> None:
        self._search_count += count

    def increment_routing_decisions(self, count: int = 1) -> None:
        self._routing_decisions += count

    def increment_policy_violations(self, count: int = 1) -> None:
        self._policy_violations += count

    def increment_lifecycle_transitions(self, count: int = 1) -> None:
        self._lifecycle_transitions += count

    def increment_expired(self, count: int = 1) -> None:
        self._metrics.expired_records += count

    def record_latency(self, retrieval_ms: float = 0.0, storage_ms: float = 0.0) -> None:
        if retrieval_ms > 0:
            self._metrics.retrieval_latency = (
                self._metrics.retrieval_latency + retrieval_ms
            ) / 2 if self._metrics.reads > 0 else retrieval_ms
        if storage_ms > 0:
            self._metrics.storage_latency = (
                self._metrics.storage_latency + storage_ms
            ) / 2 if self._metrics.writes > 0 else storage_ms

    # ── Snapshot ──────────────────────────────────────────────────────────

    def snapshot(self) -> MemoryMetrics:
        """Return the current aggregated metrics."""
        return self._metrics.model_copy(deep=True)

    def get_extended(self) -> dict[str, Any]:
        """Return metrics plus extended counters."""
        base = self._metrics.model_dump()
        base["routing_decisions"] = self._routing_decisions
        base["policy_violations"] = self._policy_violations
        base["lifecycle_transitions"] = self._lifecycle_transitions
        base["search_count"] = self._search_count
        return base

    def reset(self) -> None:
        """Reset all counters (for testing)."""
        self._metrics = MemoryMetrics()
        self._routing_decisions = 0
        self._policy_violations = 0
        self._lifecycle_transitions = 0
        self._search_count = 0
