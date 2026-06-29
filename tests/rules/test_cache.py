"""Tests for RuleCache."""

from __future__ import annotations

from adip.rules.contracts.models import Rule, RuleSet
from adip.rules.execution.cache import RuleCache
from adip.rules.execution.models import CompiledRule, VersionRecord


class TestRuleCache:
    def test_set_and_get_compiled_rule(self) -> None:
        cache = RuleCache()
        rule = Rule(name="Test")
        compiled = CompiledRule(rule_id=rule.rule_id, rule=rule)
        cache.set_compiled_rule("rule:1", compiled)
        result = cache.get_compiled_rule("rule:1")
        assert result is not None
        assert result.rule_id == rule.rule_id

    def test_get_compiled_rule_missing(self) -> None:
        cache = RuleCache()
        result = cache.get_compiled_rule("nonexistent")
        assert result is None

    def test_set_and_get_rule(self) -> None:
        cache = RuleCache()
        rule = Rule(name="Test")
        cache.set_rule("rule:1", rule)
        result = cache.get_rule("rule:1")
        assert result is not None
        assert result.name == "Test"

    def test_set_and_get_ruleset(self) -> None:
        cache = RuleCache()
        ruleset = RuleSet(name="Test Set")
        cache.set_ruleset("set:1", ruleset)
        result = cache.get_ruleset("set:1")
        assert result is not None
        assert result.name == "Test Set"

    def test_set_and_get_version_metadata(self) -> None:
        cache = RuleCache()
        rule = Rule(name="Test")
        versions = [VersionRecord(rule_id=rule.rule_id)]
        cache.set_version_metadata("versions:1", versions)
        result = cache.get_version_metadata("versions:1")
        assert result is not None
        assert len(result) == 1

    def test_invalidate(self) -> None:
        cache = RuleCache()
        rule = Rule(name="Test")
        cache.set_rule("rule:1", rule)
        assert cache.invalidate("rule:1") is True
        assert cache.get_rule("rule:1") is None

    def test_invalidate_nonexistent(self) -> None:
        cache = RuleCache()
        assert cache.invalidate("nonexistent") is False

    def test_clear(self) -> None:
        cache = RuleCache()
        rule = Rule(name="Test")
        compiled = CompiledRule(rule_id=rule.rule_id, rule=rule)
        cache.set_compiled_rule("c:1", compiled)
        cache.set_rule("r:1", rule)
        count = cache.clear()
        assert count >= 2
        assert cache.size() == 0

    def test_size(self) -> None:
        cache = RuleCache()
        assert cache.size() == 0
        rule = Rule(name="Test")
        compiled = CompiledRule(rule_id=rule.rule_id, rule=rule)
        cache.set_compiled_rule("c:1", compiled)
        assert cache.size() == 1
        cache.set_rule("r:1", rule)
        assert cache.size() == 2
