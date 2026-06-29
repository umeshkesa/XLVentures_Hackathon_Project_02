"""Tests for RuleLifecycleManager."""

from __future__ import annotations

import pytest

from adip.rules.contracts.models import Rule
from adip.rules.enums import RuleLifecycleStatus
from adip.rules.execution.lifecycle import RuleLifecycleManager


class TestRuleLifecycleManager:
    def test_get_current_status(self) -> None:
        rule = Rule(name="Test")
        lm = RuleLifecycleManager()
        assert lm.get_current_status(rule) == RuleLifecycleStatus.DRAFT

    def test_transition_draft_to_under_review(self) -> None:
        rule = Rule(name="Test")
        lm = RuleLifecycleManager()
        result = lm.transition(rule, RuleLifecycleStatus.UNDER_REVIEW, reason="Ready")
        assert result.status == RuleLifecycleStatus.UNDER_REVIEW

    def test_transition_under_review_to_approved(self) -> None:
        rule = Rule(name="Test", status=RuleLifecycleStatus.UNDER_REVIEW)
        lm = RuleLifecycleManager()
        result = lm.transition(rule, RuleLifecycleStatus.APPROVED)
        assert result.status == RuleLifecycleStatus.APPROVED

    def test_transition_approved_to_active(self) -> None:
        rule = Rule(name="Test", status=RuleLifecycleStatus.APPROVED)
        lm = RuleLifecycleManager()
        result = lm.transition(rule, RuleLifecycleStatus.ACTIVE)
        assert result.status == RuleLifecycleStatus.ACTIVE

    def test_transition_active_to_deprecated(self) -> None:
        rule = Rule(name="Test", status=RuleLifecycleStatus.ACTIVE)
        lm = RuleLifecycleManager()
        result = lm.transition(rule, RuleLifecycleStatus.DEPRECATED)
        assert result.status == RuleLifecycleStatus.DEPRECATED

    def test_transition_deprecated_to_archived(self) -> None:
        rule = Rule(name="Test", status=RuleLifecycleStatus.DEPRECATED)
        lm = RuleLifecycleManager()
        result = lm.transition(rule, RuleLifecycleStatus.ARCHIVED)
        assert result.status == RuleLifecycleStatus.ARCHIVED

    def test_transition_same_status(self) -> None:
        rule = Rule(name="Test", status=RuleLifecycleStatus.DRAFT)
        lm = RuleLifecycleManager()
        result = lm.transition(rule, RuleLifecycleStatus.DRAFT)
        assert result is rule  # Same object, no transition

    def test_illegal_transition(self) -> None:
        rule = Rule(name="Test", status=RuleLifecycleStatus.DRAFT)
        lm = RuleLifecycleManager()
        with pytest.raises(ValueError, match="Illegal lifecycle transition"):
            lm.transition(rule, RuleLifecycleStatus.ARCHIVED)

    def test_illegal_transition_from_archived(self) -> None:
        rule = Rule(name="Test", status=RuleLifecycleStatus.ARCHIVED)
        lm = RuleLifecycleManager()
        with pytest.raises(ValueError, match="Illegal lifecycle transition"):
            lm.transition(rule, RuleLifecycleStatus.DRAFT)

    def test_under_review_back_to_draft(self) -> None:
        rule = Rule(name="Test", status=RuleLifecycleStatus.UNDER_REVIEW)
        lm = RuleLifecycleManager()
        result = lm.transition(rule, RuleLifecycleStatus.DRAFT, reason="Rework needed")
        assert result.status == RuleLifecycleStatus.DRAFT

    def test_get_history(self) -> None:
        rule = Rule(name="Test")
        lm = RuleLifecycleManager()
        lm.transition(rule, RuleLifecycleStatus.UNDER_REVIEW, changed_by="user-1")
        rule = rule.model_copy(update={"status": RuleLifecycleStatus.UNDER_REVIEW})
        lm.transition(rule, RuleLifecycleStatus.APPROVED, changed_by="user-2")
        history = lm.get_history(str(rule.rule_id))
        assert len(history) == 2
        assert history[0].changed_by == "user-1"
        assert history[1].changed_by == "user-2"

    def test_get_all_history(self) -> None:
        r1 = Rule(name="R1")
        r2 = Rule(name="R2")
        lm = RuleLifecycleManager()
        lm.transition(r1, RuleLifecycleStatus.UNDER_REVIEW)
        lm.transition(r2, RuleLifecycleStatus.UNDER_REVIEW)
        assert len(lm.get_all_history()) == 2

    def test_clear(self) -> None:
        rule = Rule(name="Test")
        lm = RuleLifecycleManager()
        lm.transition(rule, RuleLifecycleStatus.UNDER_REVIEW)
        lm.clear()
        assert lm.get_all_history() == []
