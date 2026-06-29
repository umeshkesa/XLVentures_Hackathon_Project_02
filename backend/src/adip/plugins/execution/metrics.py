"""PluginMetricsCollector — collects and exposes plugin manager metrics.

Provides counters for plugins, active plugins, validation errors,
compatibility failures, dependency graph size, sandbox count,
and initialisation latency tracking.
"""

from __future__ import annotations

import structlog

from adip.plugins.contracts.models import PluginMetrics

log = structlog.get_logger(__name__)


class PluginMetricsCollector:
    """Collects operational metrics for the plugin manager.

    Enhanced in Phase 3.5 with lifecycle_transitions,
    dependency_failures, and load_latency tracking.
    """

    def __init__(self) -> None:
        self._plugins_total: int = 0
        self._active_plugins: int = 0
        self._validation_errors: int = 0
        self._compatibility_failures: int = 0
        self._dependency_failures: int = 0
        self._lifecycle_transitions: int = 0
        self._dependency_graph_size: int = 0
        self._sandbox_count: int = 0
        self._load_attempts: int = 0
        self._load_successes: int = 0
        self._load_failures: int = 0
        self._load_times: list[float] = []
        self._discoveries_total: int = 0
        self._capability_registrations: int = 0
        self._initialization_attempts: int = 0
        self._initialization_times: list[float] = []
        self._cache_hits: int = 0
        self._cache_misses: int = 0
        self._plugins_per_domain: dict[str, int] = {}
        self._plugins_per_type: dict[str, int] = {}

    def increment_plugins(self, domain: str = "", plugin_type: str = "") -> None:
        """Increment total plugins counter and per-domain/type counters."""
        self._plugins_total += 1
        if domain:
            self._plugins_per_domain[domain] = self._plugins_per_domain.get(domain, 0) + 1
        if plugin_type:
            self._plugins_per_type[plugin_type] = self._plugins_per_type.get(plugin_type, 0) + 1

    def increment_active_plugins(self) -> None:
        """Increment active plugins counter."""
        self._active_plugins += 1

    def decrement_active_plugins(self) -> None:
        """Decrement active plugins counter."""
        self._active_plugins = max(0, self._active_plugins - 1)

    def increment_validation_errors(self) -> None:
        """Increment validation errors counter."""
        self._validation_errors += 1

    def increment_compatibility_failures(self) -> None:
        """Increment compatibility failures counter."""
        self._compatibility_failures += 1

    def increment_dependency_failures(self) -> None:
        """Increment dependency failures counter."""
        self._dependency_failures += 1

    def increment_lifecycle_transitions(self) -> None:
        """Increment lifecycle transitions counter."""
        self._lifecycle_transitions += 1

    def set_dependency_graph_size(self, size: int) -> None:
        """Set the dependency graph size."""
        self._dependency_graph_size = max(0, size)

    def set_sandbox_count(self, count: int) -> None:
        """Set the active sandbox count."""
        self._sandbox_count = max(0, count)

    def increment_load_attempts(self) -> None:
        """Increment load attempts counter."""
        self._load_attempts += 1

    def increment_load_successes(self) -> None:
        """Increment successful loads counter."""
        self._load_successes += 1

    def increment_load_failures(self) -> None:
        """Increment failed loads counter."""
        self._load_failures += 1

    def record_load_time(self, time_ms: float) -> None:
        """Record a load latency sample."""
        self._load_times.append(time_ms)

    def increment_discoveries(self) -> None:
        """Increment discoveries counter."""
        self._discoveries_total += 1

    def increment_capability_registrations(self) -> None:
        """Increment capability registrations counter."""
        self._capability_registrations += 1

    def increment_initialization_attempts(self) -> None:
        """Increment initialisation attempts counter."""
        self._initialization_attempts += 1

    def record_initialization_time(self, time_ms: float) -> None:
        """Record an initialisation latency sample."""
        self._initialization_times.append(time_ms)

    def increment_cache_hits(self) -> None:
        """Increment cache hits counter."""
        self._cache_hits += 1

    def increment_cache_misses(self) -> None:
        """Increment cache misses counter."""
        self._cache_misses += 1

    def snapshot(self) -> PluginMetrics:
        """Take a point-in-time snapshot of all metrics."""
        import uuid

        avg_it = (
            sum(self._initialization_times) / len(self._initialization_times)
            if self._initialization_times
            else 0.0
        )
        avg_lt = (
            sum(self._load_times) / len(self._load_times)
            if self._load_times
            else 0.0
        )

        return PluginMetrics(
            plugin_id=uuid.uuid4(),
            plugins_total=self._plugins_total,
            active_plugins=self._active_plugins,
            executions_total=self._load_attempts,
            executions_success=self._load_successes,
            executions_failed=self._load_failures,
            average_execution_time_ms=round(avg_it, 2),
            errors_total=self._validation_errors + self._compatibility_failures + self._dependency_failures,
            cache_hits=self._cache_hits,
            cache_misses=self._cache_misses,
            compatibility_failures=self._compatibility_failures,
            dependency_failures=self._dependency_failures,
            lifecycle_transitions=self._lifecycle_transitions,
            sandbox_count=self._sandbox_count,
            discoveries_total=self._discoveries_total,
            load_latency_ms=round(avg_lt, 2),
            domain_usage=dict(self._plugins_per_domain),
            plugin_types=dict(self._plugins_per_type),
        )

    def reset(self) -> None:
        """Reset all metrics to zero."""
        self._plugins_total = 0
        self._active_plugins = 0
        self._validation_errors = 0
        self._compatibility_failures = 0
        self._dependency_failures = 0
        self._lifecycle_transitions = 0
        self._dependency_graph_size = 0
        self._sandbox_count = 0
        self._load_attempts = 0
        self._load_successes = 0
        self._load_failures = 0
        self._load_times.clear()
        self._discoveries_total = 0
        self._capability_registrations = 0
        self._initialization_attempts = 0
        self._initialization_times.clear()
        self._cache_hits = 0
        self._cache_misses = 0
        self._plugins_per_domain.clear()
        self._plugins_per_type.clear()
