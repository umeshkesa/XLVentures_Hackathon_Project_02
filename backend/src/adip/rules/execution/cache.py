"""RuleCache — synchronous in-memory cache for rules and evaluations.

Caches compiled rules, active rules, rule sets, version metadata,
and evaluation results with TTL support.
"""

from __future__ import annotations

import structlog

from adip.rules.contracts.models import Rule, RuleSet
from adip.rules.execution.models import CompiledRule, VersionRecord

log = structlog.get_logger(__name__)


class RuleCache:
    """In-memory cache for rule-related objects."""

    def __init__(self) -> None:
        self._compiled_rules: dict[str, CompiledRule] = {}
        self._rules: dict[str, Rule] = {}
        self._rulesets: dict[str, RuleSet] = {}
        self._version_metadata: dict[str, list[VersionRecord]] = {}
        self._ttls: dict[str, int] = {}

    def get_compiled_rule(self, cache_key: str) -> CompiledRule | None:
        """Retrieve a cached CompiledRule by key."""
        if cache_key not in self._compiled_rules:
            return None
        log.info("rule_cache.get_compiled_rule", key=cache_key)
        return self._compiled_rules[cache_key]

    def set_compiled_rule(self, cache_key: str, compiled: CompiledRule, ttl_seconds: int = 300) -> None:
        """Cache a CompiledRule with an optional TTL."""
        log.info("rule_cache.set_compiled_rule", key=cache_key, ttl=ttl_seconds)
        self._compiled_rules[cache_key] = compiled
        self._ttls[cache_key] = ttl_seconds

    def get_rule(self, cache_key: str) -> Rule | None:
        """Retrieve a cached Rule by key."""
        if cache_key not in self._rules:
            return None
        return self._rules[cache_key]

    def set_rule(self, cache_key: str, rule: Rule, ttl_seconds: int = 300) -> None:
        """Cache a Rule with an optional TTL."""
        log.info("rule_cache.set_rule", key=cache_key, ttl=ttl_seconds)
        self._rules[cache_key] = rule
        self._ttls[cache_key] = ttl_seconds

    def get_ruleset(self, cache_key: str) -> RuleSet | None:
        """Retrieve a cached RuleSet by key."""
        if cache_key not in self._rulesets:
            return None
        return self._rulesets[cache_key]

    def set_ruleset(self, cache_key: str, ruleset: RuleSet, ttl_seconds: int = 300) -> None:
        """Cache a RuleSet with an optional TTL."""
        log.info("rule_cache.set_ruleset", key=cache_key, ttl=ttl_seconds)
        self._rulesets[cache_key] = ruleset
        self._ttls[cache_key] = ttl_seconds

    def set_version_metadata(self, cache_key: str, versions: list[VersionRecord], ttl_seconds: int = 600) -> None:
        """Cache version metadata with an optional TTL."""
        log.info("rule_cache.set_version_metadata", key=cache_key, ttl=ttl_seconds)
        self._version_metadata[cache_key] = versions
        self._ttls[cache_key] = ttl_seconds

    def get_version_metadata(self, cache_key: str) -> list[VersionRecord] | None:
        """Retrieve cached version metadata by key."""
        return self._version_metadata.get(cache_key)

    def invalidate(self, cache_key: str) -> bool:
        """Invalidate a single cache entry across all stores."""
        existed = (
            cache_key in self._compiled_rules
            or cache_key in self._rules
            or cache_key in self._rulesets
            or cache_key in self._version_metadata
        )
        self._compiled_rules.pop(cache_key, None)
        self._rules.pop(cache_key, None)
        self._rulesets.pop(cache_key, None)
        self._version_metadata.pop(cache_key, None)
        self._ttls.pop(cache_key, None)
        if existed:
            log.info("rule_cache.invalidate", key=cache_key)
        return existed

    def clear(self) -> int:
        """Clear all cache entries. Returns the number cleared."""
        total = (
            len(self._compiled_rules)
            + len(self._rules)
            + len(self._rulesets)
            + len(self._version_metadata)
        )
        self._compiled_rules.clear()
        self._rules.clear()
        self._rulesets.clear()
        self._version_metadata.clear()
        self._ttls.clear()
        log.info("rule_cache.clear", cleared=total)
        return total

    def size(self) -> int:
        """Return the total number of cached entries across all stores."""
        return (
            len(self._compiled_rules)
            + len(self._rules)
            + len(self._rulesets)
            + len(self._version_metadata)
        )
