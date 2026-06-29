"""Tests for Rule Manager exceptions."""

from __future__ import annotations

from adip.rules.contracts.exceptions import (
    RuleConflictException,
    RuleEvaluationException,
    RuleException,
    RuleValidationException,
)


class TestRuleException:
    def test_default_message(self) -> None:
        exc = RuleException()
        assert str(exc) == "Rule error"

    def test_custom_message(self) -> None:
        exc = RuleException("Custom rule error")
        assert str(exc) == "Custom rule error"

    def test_inheritance(self) -> None:
        assert issubclass(RuleException, Exception)


class TestRuleValidationException:
    def test_default_message(self) -> None:
        exc = RuleValidationException()
        assert str(exc) == "Rule validation error"

    def test_custom_message(self) -> None:
        exc = RuleValidationException("Rule name is required")
        assert str(exc) == "Rule name is required"

    def test_inheritance(self) -> None:
        assert issubclass(RuleValidationException, RuleException)


class TestRuleConflictException:
    def test_default_message(self) -> None:
        exc = RuleConflictException()
        assert str(exc) == "Rule conflict detected"

    def test_with_rule_ids(self) -> None:
        exc = RuleConflictException(rule_id="rule-1", conflicting_rule_id="rule-2")
        assert "rule-1" in str(exc)
        assert "rule-2" in str(exc)

    def test_with_custom_message(self) -> None:
        exc = RuleConflictException(message="Custom conflict")
        assert str(exc) == "Custom conflict"

    def test_with_only_rule_id(self) -> None:
        exc = RuleConflictException(rule_id="rule-1")
        assert "rule-1" in str(exc)

    def test_inheritance(self) -> None:
        assert issubclass(RuleConflictException, RuleException)

    def test_attributes(self) -> None:
        exc = RuleConflictException(rule_id="r1", conflicting_rule_id="r2")
        assert exc.rule_id == "r1"
        assert exc.conflicting_rule_id == "r2"


class TestRuleEvaluationException:
    def test_default_message(self) -> None:
        exc = RuleEvaluationException()
        assert str(exc) == "Rule evaluation failed"

    def test_with_ids(self) -> None:
        exc = RuleEvaluationException(rule_id="rule-1", context_id="ctx-1")
        assert "rule-1" in str(exc)
        assert "ctx-1" in str(exc)

    def test_with_custom_message(self) -> None:
        exc = RuleEvaluationException(message="Timeout during evaluation")
        assert str(exc) == "Timeout during evaluation"

    def test_with_only_context(self) -> None:
        exc = RuleEvaluationException(context_id="ctx-1")
        assert "ctx-1" in str(exc)

    def test_inheritance(self) -> None:
        assert issubclass(RuleEvaluationException, RuleException)

    def test_attributes(self) -> None:
        exc = RuleEvaluationException(rule_id="r1", context_id="c1")
        assert exc.rule_id == "r1"
        assert exc.context_id == "c1"
