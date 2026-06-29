"""RuleMetricsCollector — collects and exposes rule manager metrics.

Provides counters for rules, active rules, versions, evaluations,
conflicts, cache hits/misses, validation errors, and latency
tracking.
"""

from __future__ import annotations

import structlog

from adip.rules.contracts.models import RuleMetrics

log = structlog.get_logger(__name__)


class RuleMetricsCollector:
    """Collects operational metrics for the rule manager.

    Enhanced for Phase 3.5 with category, scope, and version tracking.
    """

    def __init__(self) -> None:
        self._rules_total: int = 0
        self._active_rules: int = 0
        self._versions_total: int = 0
        self._evaluations_total: int = 0
        self._decisions_total: int = 0
        self._conflicts_total: int = 0
        self._cache_hits: int = 0
        self._cache_misses: int = 0
        self._validation_errors: int = 0
        self._rulesets_total: int = 0
        self._evaluation_times: list[float] = []
        self._decision_times: list[float] = []
        self._strategy_usage: dict[str, int] = {}
        self._domain_usage: dict[str, int] = {}
        self._rules_per_domain: dict[str, int] = {}
        self._rules_per_type: dict[str, int] = {}
        self._rules_per_category: dict[str, int] = {}
        self._rules_per_scope: dict[str, int] = {}
        self._version_usage: dict[str, int] = {}

    def increment_rules(self, domain: str = "", rule_type: str = "") -> None:
        """Increment total rules counter and per-domain/type counters."""
        self._rules_total += 1
        if domain:
            self._rules_per_domain[domain] = self._rules_per_domain.get(domain, 0) + 1
        if rule_type:
            self._rules_per_type[rule_type] = self._rules_per_type.get(rule_type, 0) + 1

    def increment_active_rules(self) -> None:
        """Increment active rules counter."""
        self._active_rules += 1

    def decrement_active_rules(self) -> None:
        """Decrement active rules counter."""
        self._active_rules = max(0, self._active_rules - 1)

    def increment_versions(self) -> None:
        """Increment version counter."""
        self._versions_total += 1

    def increment_evaluations(self) -> None:
        """Increment evaluation counter."""
        self._evaluations_total += 1

    def increment_decisions(self, count: int = 1) -> None:
        """Increment decisions counter."""
        self._decisions_total += count

    def increment_conflicts(self) -> None:
        """Increment conflicts counter."""
        self._conflicts_total += 1

    def increment_cache_hits(self) -> None:
        """Increment cache hits counter."""
        self._cache_hits += 1

    def increment_cache_misses(self) -> None:
        """Increment cache misses counter."""
        self._cache_misses += 1

    def increment_validation_errors(self) -> None:
        """Increment validation errors counter."""
        self._validation_errors += 1

    def increment_rulesets(self) -> None:
        """Increment rulesets counter."""
        self._rulesets_total += 1

    def record_evaluation_time(self, time_ms: float) -> None:
        """Record an evaluation latency sample."""
        self._evaluation_times.append(time_ms)

    def record_decision_time(self, time_ms: float) -> None:
        """Record a decision latency sample."""
        self._decision_times.append(time_ms)

    def increment_strategy_usage(self, strategy: str) -> None:
        """Increment usage counter for an evaluation strategy."""
        self._strategy_usage[strategy] = self._strategy_usage.get(strategy, 0) + 1

    def increment_domain_usage(self, domain: str) -> None:
        """Increment usage counter for a rule domain."""
        self._domain_usage[domain] = self._domain_usage.get(domain, 0) + 1

    def increment_rules_per_category(self, category: str) -> None:
        """Increment rule count per category."""
        self._rules_per_category[category] = self._rules_per_category.get(category, 0) + 1

    def increment_rules_per_scope(self, scope: str) -> None:
        """Increment rule count per scope."""
        self._rules_per_scope[scope] = self._rules_per_scope.get(scope, 0) + 1

    def increment_version_usage(self, version: str) -> None:
        """Increment usage counter for a rule version."""
        self._version_usage[version] = self._version_usage.get(version, 0) + 1

    def snapshot(self) -> RuleMetrics:
        """Take a point-in-time snapshot of all metrics."""
        avg_et = (
            sum(self._evaluation_times) / len(self._evaluation_times)
            if self._evaluation_times
            else 0.0
        )
        avg_dt = (
            sum(self._decision_times) / len(self._decision_times)
            if self._decision_times
            else 0.0
        )

        return RuleMetrics(
            rules_total=self._rules_total,
            rulesets_total=self._rulesets_total,
            evaluations_total=self._evaluations_total,
            decisions_total=self._decisions_total,
            conflicts_total=self._conflicts_total,
            cache_hits=self._cache_hits,
            cache_misses=self._cache_misses,
            rules_per_domain=dict(self._rules_per_domain),
            rules_per_type=dict(self._rules_per_type),
            rules_per_category=dict(self._rules_per_category),
            rules_per_scope=dict(self._rules_per_scope),
            average_evaluation_time_ms=round(avg_et, 2),
            average_decision_time_ms=round(avg_dt, 2),
            strategy_usage=dict(self._strategy_usage),
            domain_usage=dict(self._domain_usage),
            version_usage=dict(self._version_usage),
        )

    def reset(self) -> None:
        """Reset all metrics to zero."""
        self._rules_total = 0
        self._active_rules = 0
        self._versions_total = 0
        self._evaluations_total = 0
        self._decisions_total = 0
        self._conflicts_total = 0
        self._cache_hits = 0
        self._cache_misses = 0
        self._validation_errors = 0
        self._rulesets_total = 0
        self._evaluation_times.clear()
        self._decision_times.clear()
        self._strategy_usage.clear()
        self._domain_usage.clear()
        self._rules_per_domain.clear()
        self._rules_per_type.clear()
        self._rules_per_category.clear()
        self._rules_per_scope.clear()
        self._version_usage.clear()
