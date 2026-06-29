"""RuleParser — parses rule definitions from various source formats.

Supports placeholder parsing for JSON, YAML, database, plugin,
and future DSL formats. No actual parsing implementation.
"""

from __future__ import annotations

import structlog

from adip.rules.contracts.models import Rule, RuleSet

log = structlog.get_logger(__name__)


class RuleParser:
    """Parses rule definitions from structured formats.

    Placeholder implementation — returns pre-configured rules
    for testing and structural validation.
    """

    def __init__(self) -> None:
        self._supported_formats: list[str] = ["json", "yaml"]

    def parse_rule(self, source: str, format: str = "json") -> Rule:
        """Parse a rule definition from a source string.

        Placeholder — returns a default Rule for structural validation.
        """
        log.info("rule_parser.parse_rule", format=format, source_length=len(source))
        return Rule()

    def parse_ruleset(self, source: str, format: str = "json") -> RuleSet:
        """Parse a rule set definition from a source string.

        Placeholder — returns a default RuleSet for structural validation.
        """
        log.info("rule_parser.parse_ruleset", format=format, source_length=len(source))
        return RuleSet()

    def get_supported_formats(self) -> list[str]:
        """Return the source formats this parser supports."""
        return list(self._supported_formats)

    def add_format(self, format: str) -> None:
        """Register a new supported format."""
        if format not in self._supported_formats:
            self._supported_formats.append(format)
            log.info("rule_parser.add_format", format=format)
