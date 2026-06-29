"""Tests for ConflictResolver."""

from __future__ import annotations

import uuid

from adip.rules.contracts.models import Rule, RuleContext, RuleDecision
from adip.rules.execution.conflict_resolver import ConflictResolver


class TestConflictResolver:
    def test_detect_conflicts_no_conflicts(self) -> None:
        resolver = ConflictResolver()
        rules = [
            Rule(name="Rule A"),
            Rule(name="Rule B"),
        ]
        reports = resolver.detect_conflicts(rules)
        assert reports == []

    def test_detect_conflicts_name_overlap(self) -> None:
        resolver = ConflictResolver()
        rules = [
            Rule(name="Duplicate"),
            Rule(name="Duplicate"),
        ]
        reports = resolver.detect_conflicts(rules)
        assert len(reports) == 1
        assert reports[0].conflict_type == "direct_overlap"

    def test_resolve_conflicts_priority(self) -> None:
        resolver = ConflictResolver()
        ctx = RuleContext()
        decisions = [
            RuleDecision(context_id=ctx.context_id, rule_id=uuid.uuid4(), decision="deny", confidence=0.8),
            RuleDecision(context_id=ctx.context_id, rule_id=uuid.uuid4(), decision="allow", confidence=0.9),
        ]
        resolved = resolver.resolve_conflicts(decisions, strategy="PRIORITY")
        assert len(resolved) == 2
        # Highest confidence first
        assert resolved[0].confidence == 0.9

    def test_resolve_conflicts_deny_override(self) -> None:
        resolver = ConflictResolver()
        ctx = RuleContext()
        decisions = [
            RuleDecision(context_id=ctx.context_id, rule_id=uuid.uuid4(), decision="allow", confidence=0.9),
            RuleDecision(context_id=ctx.context_id, rule_id=uuid.uuid4(), decision="deny", confidence=0.8),
        ]
        resolved = resolver.resolve_conflicts(decisions, strategy="DENY_OVERRIDE")
        assert len(resolved) == 2
        # Deny decisions come first
        assert resolved[0].decision == "deny"

    def test_resolve_conflicts_default(self) -> None:
        resolver = ConflictResolver()
        ctx = RuleContext()
        decisions = [
            RuleDecision(context_id=ctx.context_id, rule_id=uuid.uuid4(), decision="allow"),
            RuleDecision(context_id=ctx.context_id, rule_id=uuid.uuid4(), decision="deny"),
        ]
        resolved = resolver.resolve_conflicts(decisions, strategy="UNKNOWN")
        assert len(resolved) == 2
