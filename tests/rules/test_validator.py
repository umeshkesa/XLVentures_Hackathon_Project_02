"""Tests for RuleValidator."""

from __future__ import annotations

from adip.rules.contracts.models import Rule, RuleAction, RuleCondition, RuleSet
from adip.rules.enums import RuleLifecycleStatus, RuleType
from adip.rules.execution.validator import RuleValidator


class TestRuleValidator:
    def test_valid_rule(self) -> None:
        rule = Rule(
            name="Test Rule",
            rule_type=RuleType.BUSINESS,
            priority=50,
            version=1,
        )
        validator = RuleValidator()
        violations = validator.validate_rule(rule)
        assert violations == []

    def test_missing_name(self) -> None:
        rule = Rule(name="", rule_type=RuleType.SAFETY)
        validator = RuleValidator()
        violations = validator.validate_rule(rule)
        assert "Rule name is required" in violations

    def test_excessive_priority(self) -> None:
        rule = Rule(name="Test", rule_type=RuleType.BUSINESS, priority=1001)
        validator = RuleValidator()
        violations = validator.validate_rule(rule)
        assert any("exceeds maximum" in v for v in violations)

    def test_missing_namespace(self) -> None:
        rule = Rule(name="Test", rule_type=RuleType.BUSINESS, namespace="")
        validator = RuleValidator()
        violations = validator.validate_rule(rule)
        assert "Rule namespace is required" in violations

    def test_condition_missing_field(self) -> None:
        rule = Rule(
            name="Test",
            rule_type=RuleType.BUSINESS,
            conditions=[RuleCondition(field="", operator="gt", value="100")],
        )
        validator = RuleValidator()
        violations = validator.validate_rule(rule)
        assert any("field is required" in v for v in violations)

    def test_condition_missing_operator(self) -> None:
        rule = Rule(
            name="Test",
            rule_type=RuleType.BUSINESS,
            conditions=[RuleCondition(field="temp", operator="", value="100")],
        )
        validator = RuleValidator()
        violations = validator.validate_rule(rule)
        assert any("operator is required" in v for v in violations)

    def test_action_missing_type(self) -> None:
        rule = Rule(
            name="Test",
            rule_type=RuleType.BUSINESS,
            actions=[RuleAction(action_type="")],
        )
        validator = RuleValidator()
        violations = validator.validate_rule(rule)
        assert any("action_type is required" in v for v in violations)

    def test_validate_batch(self) -> None:
        rule_valid = Rule(name="Valid", rule_type=RuleType.BUSINESS)
        rule_invalid = Rule(name="", rule_type=RuleType.SAFETY)
        validator = RuleValidator()
        results = validator.validate_rule_batch([rule_valid, rule_invalid])
        assert len(results) == 2
        assert results[0] == []
        assert len(results[1]) > 0

    def test_validate_ruleset_valid(self) -> None:
        ruleset = RuleSet(
            name="Test Set",
            rules=[
                Rule(name="Rule 1", rule_type=RuleType.BUSINESS),
                Rule(name="Rule 2", rule_type=RuleType.SAFETY),
            ],
        )
        validator = RuleValidator()
        violations = validator.validate_ruleset(ruleset)
        assert violations == []

    def test_validate_ruleset_missing_name(self) -> None:
        ruleset = RuleSet(name="")
        validator = RuleValidator()
        violations = validator.validate_ruleset(ruleset)
        assert "RuleSet name is required" in violations

    def test_validate_ruleset_missing_namespace(self) -> None:
        ruleset = RuleSet(name="Test", namespace="")
        validator = RuleValidator()
        violations = validator.validate_ruleset(ruleset)
        assert "RuleSet namespace is required" in violations

    def test_validate_ruleset_bad_rule(self) -> None:
        ruleset = RuleSet(
            name="Test Set",
            rules=[Rule(name="", rule_type=RuleType.BUSINESS)],
        )
        validator = RuleValidator()
        violations = validator.validate_ruleset(ruleset)
        assert any("Rule 0" in v for v in violations)

    def test_validate_lifecycle_transition(self) -> None:
        validator = RuleValidator()
        violations = validator.validate_lifecycle_transition(
            RuleLifecycleStatus.DRAFT,
            RuleLifecycleStatus.UNDER_REVIEW,
        )
        assert violations == []
