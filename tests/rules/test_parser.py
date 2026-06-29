"""Tests for RuleParser."""

from __future__ import annotations

from adip.rules.contracts.models import Rule, RuleSet
from adip.rules.execution.parser import RuleParser


class TestRuleParser:
    def test_parse_rule_returns_rule(self) -> None:
        parser = RuleParser()
        result = parser.parse_rule('{"name": "test"}', format="json")
        assert isinstance(result, Rule)

    def test_parse_ruleset_returns_ruleset(self) -> None:
        parser = RuleParser()
        result = parser.parse_ruleset('{"name": "test"}', format="json")
        assert isinstance(result, RuleSet)

    def test_supported_formats(self) -> None:
        parser = RuleParser()
        formats = parser.get_supported_formats()
        assert "json" in formats
        assert "yaml" in formats

    def test_add_format(self) -> None:
        parser = RuleParser()
        parser.add_format("toml")
        assert "toml" in parser.get_supported_formats()
        assert len(parser.get_supported_formats()) == 3

    def test_add_duplicate_format(self) -> None:
        parser = RuleParser()
        parser.add_format("json")
        assert len(parser.get_supported_formats()) == 2
