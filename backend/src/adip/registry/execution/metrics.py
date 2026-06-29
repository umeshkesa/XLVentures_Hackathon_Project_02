"""RegistryMetricsCollector — collects and aggregates registry metrics.

Tracks entries, searches, cache hits/misses, version count, index
count, lifecycle transitions, search latency, validation failures,
updates, search strategy usage, namespace usage, and registry types.
Enhanced in Phase 3.5 with counters for validation_failures, updates,
cache_usage, search_strategy_usage, namespace_usage, and registry_types.
"""

from __future__ import annotations

import structlog

from adip.registry.contracts.models import RegistryMetrics
from adip.registry.enums import RegistryType

log = structlog.get_logger(__name__)


class RegistryMetricsCollector:
    """Collects and aggregates registry operational metrics.

    Phase 3.5 adds counters for validation_failures, updates,
    cache_usage, search_strategy_usage, namespace_usage, and
    registry_types.
    """

    def __init__(self) -> None:
        self._entries_total: int = 0
        self._registrations_total: int = 0
        self._deregistrations_total: int = 0
        self._lookups_total: int = 0
        self._searches_total: int = 0
        self._versions_total: int = 0
        self._active_entries: int = 0
        self._cache_hits: int = 0
        self._cache_misses: int = 0
        self._errors_total: int = 0
        self._lifecycle_transitions: int = 0
        self._search_latencies: list[float] = []
        self._entries_per_scope: dict[str, int] = {}
        self._entries_per_status: dict[str, int] = {}
        self._registry_type: RegistryType = RegistryType.CAPABILITY
        # Phase 3.5 counters
        self._validation_failures_total: int = 0
        self._updates_total: int = 0
        self._cache_usage: dict[str, int] = {}
        self._search_strategy_usage: dict[str, int] = {}
        self._namespace_usage: dict[str, int] = {}
        self._registry_types: dict[str, int] = {}

    def set_registry_type(self, registry_type: RegistryType) -> None:
        self._registry_type = registry_type

    def increment_entries_total(self) -> None:
        self._entries_total += 1

    def decrement_entries_total(self) -> None:
        self._entries_total = max(0, self._entries_total - 1)

    def increment_registrations(self) -> None:
        self._registrations_total += 1

    def increment_deregistrations(self) -> None:
        self._deregistrations_total += 1

    def increment_lookups(self) -> None:
        self._lookups_total += 1

    def increment_searches(self) -> None:
        self._searches_total += 1

    def increment_versions(self) -> None:
        self._versions_total += 1

    def increment_active_entries(self) -> None:
        self._active_entries += 1

    def decrement_active_entries(self) -> None:
        self._active_entries = max(0, self._active_entries - 1)

    def increment_cache_hits(self) -> None:
        self._cache_hits += 1

    def increment_cache_misses(self) -> None:
        self._cache_misses += 1

    def increment_errors(self) -> None:
        self._errors_total += 1

    def increment_lifecycle_transitions(self) -> None:
        self._lifecycle_transitions += 1

    def record_search_latency(self, latency_ms: float) -> None:
        self._search_latencies.append(latency_ms)
        self._searches_total += 1

    def set_entries_per_scope(self, data: dict[str, int]) -> None:
        self._entries_per_scope = dict(data)

    def set_entries_per_status(self, data: dict[str, int]) -> None:
        self._entries_per_status = dict(data)

    # ── Phase 3.5 counters ────────────────────────────────────────

    def increment_validation_failures(self) -> None:
        self._validation_failures_total += 1

    def increment_updates(self) -> None:
        self._updates_total += 1

    def record_cache_usage(self, cache_key: str) -> None:
        self._cache_usage[cache_key] = self._cache_usage.get(cache_key, 0) + 1

    def increment_search_strategy(self, strategy: str) -> None:
        self._search_strategy_usage[strategy] = self._search_strategy_usage.get(strategy, 0) + 1

    def increment_namespace_usage(self, namespace: str) -> None:
        self._namespace_usage[namespace] = self._namespace_usage.get(namespace, 0) + 1

    def increment_registry_type_usage(self, registry_type: str) -> None:
        self._registry_types[registry_type] = self._registry_types.get(registry_type, 0) + 1

    # ── Snapshot ─────────────────────────────────────────────────

    def snapshot(self) -> RegistryMetrics:
        """Build a point-in-time RegistryMetrics from current counters."""
        avg_latency = 0.0
        if self._search_latencies:
            avg_latency = sum(self._search_latencies) / len(self._search_latencies)
        total_cache = self._cache_hits + self._cache_misses
        cache_hit_ratio = round(self._cache_hits / total_cache, 4) if total_cache > 0 else 0.0
        return RegistryMetrics(
            registry_type=self._registry_type,
            entries_total=self._entries_total,
            registrations_total=self._registrations_total,
            deregistrations_total=self._deregistrations_total,
            lookups_total=self._lookups_total,
            searches_total=self._searches_total,
            versions_total=self._versions_total,
            active_entries=self._active_entries,
            cache_hits=self._cache_hits,
            cache_misses=self._cache_misses,
            average_latency_ms=avg_latency,
            errors_total=self._errors_total,
            entries_per_scope=dict(self._entries_per_scope),
            entries_per_status=dict(self._entries_per_status),
            validation_failures_total=self._validation_failures_total,
            updates_total=self._updates_total,
            cache_hit_ratio=cache_hit_ratio,
            search_strategy_usage=dict(self._search_strategy_usage),
            namespace_usage=dict(self._namespace_usage),
            registry_types=dict(self._registry_types),
        )

    def reset(self) -> None:
        """Reset all counters to zero."""
        self.__init__()
