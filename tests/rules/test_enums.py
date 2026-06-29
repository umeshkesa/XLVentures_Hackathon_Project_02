"""Tests for Rule Manager enums."""

from __future__ import annotations

from enum import StrEnum

from adip.rules.enums import (
    EvaluationStrategyType,
    RuleDomain,
    RuleLifecycleStatus,
    RuleType,
)


class TestRuleDomain:
    def test_values(self) -> None:
        assert RuleDomain.SYSTEM == "SYSTEM"
        assert RuleDomain.PLANNER == "PLANNER"
        assert RuleDomain.WORKFLOW == "WORKFLOW"
        assert RuleDomain.MEMORY == "MEMORY"
        assert RuleDomain.KNOWLEDGE == "KNOWLEDGE"
        assert RuleDomain.REASONING == "REASONING"
        assert RuleDomain.EVIDENCE == "EVIDENCE"
        assert RuleDomain.ACTION == "ACTION"
        assert RuleDomain.ENERGY == "ENERGY"
        assert RuleDomain.CUSTOMER == "CUSTOMER"
        assert RuleDomain.PLUGIN == "PLUGIN"

    def test_all_members(self) -> None:
        assert len(RuleDomain) == 11

    def test_is_str_enum(self) -> None:
        assert issubclass(RuleDomain, StrEnum)

    def test_member_access(self) -> None:
        assert RuleDomain("SYSTEM") == RuleDomain.SYSTEM
        assert RuleDomain("PLANNER") == RuleDomain.PLANNER


class TestRuleType:
    def test_values(self) -> None:
        assert RuleType.BUSINESS == "BUSINESS"
        assert RuleType.SAFETY == "SAFETY"
        assert RuleType.COMPLIANCE == "COMPLIANCE"
        assert RuleType.MAINTENANCE == "MAINTENANCE"
        assert RuleType.APPROVAL == "APPROVAL"
        assert RuleType.ENERGY == "ENERGY"
        assert RuleType.CUSTOMER == "CUSTOMER"
        assert RuleType.SECURITY == "SECURITY"
        assert RuleType.WORKFLOW == "WORKFLOW"
        assert RuleType.PLANNING == "PLANNING"

    def test_all_members(self) -> None:
        assert len(RuleType) == 10

    def test_is_str_enum(self) -> None:
        assert issubclass(RuleType, StrEnum)


class TestRuleLifecycleStatus:
    def test_values(self) -> None:
        assert RuleLifecycleStatus.DRAFT == "DRAFT"
        assert RuleLifecycleStatus.UNDER_REVIEW == "UNDER_REVIEW"
        assert RuleLifecycleStatus.APPROVED == "APPROVED"
        assert RuleLifecycleStatus.ACTIVE == "ACTIVE"
        assert RuleLifecycleStatus.DEPRECATED == "DEPRECATED"
        assert RuleLifecycleStatus.ARCHIVED == "ARCHIVED"

    def test_all_members(self) -> None:
        assert len(RuleLifecycleStatus) == 6

    def test_lifecycle_order(self) -> None:
        """Verify expected lifecycle progression."""
        statuses = list(RuleLifecycleStatus)
        assert statuses.index(RuleLifecycleStatus.DRAFT) < statuses.index(RuleLifecycleStatus.UNDER_REVIEW)
        assert statuses.index(RuleLifecycleStatus.UNDER_REVIEW) < statuses.index(RuleLifecycleStatus.APPROVED)
        assert statuses.index(RuleLifecycleStatus.APPROVED) < statuses.index(RuleLifecycleStatus.ACTIVE)
        assert statuses.index(RuleLifecycleStatus.ACTIVE) < statuses.index(RuleLifecycleStatus.DEPRECATED)
        assert statuses.index(RuleLifecycleStatus.DEPRECATED) < statuses.index(RuleLifecycleStatus.ARCHIVED)


class TestEvaluationStrategyType:
    def test_values(self) -> None:
        assert EvaluationStrategyType.SEQUENTIAL == "SEQUENTIAL"
        assert EvaluationStrategyType.PRIORITY == "PRIORITY"
        assert EvaluationStrategyType.CONDITIONAL == "CONDITIONAL"
        assert EvaluationStrategyType.COMPOSITE == "COMPOSITE"
        assert EvaluationStrategyType.PARALLEL == "PARALLEL"

    def test_all_members(self) -> None:
        assert len(EvaluationStrategyType) == 5

    def test_is_str_enum(self) -> None:
        assert issubclass(EvaluationStrategyType, StrEnum)
