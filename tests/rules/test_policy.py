"""Tests for RulePolicyEngine."""

from __future__ import annotations

from adip.rules.contracts.models import Rule, RulePolicy
from adip.rules.enums import RuleLifecycleStatus, RuleType
from adip.rules.execution.policy import RulePolicyEngine


class TestRulePolicyEngine:
    def test_default_policy(self) -> None:
        engine = RulePolicyEngine()
        policy = engine.get_policy()
        assert policy.default_decision == "DENY"

    def test_set_policy(self) -> None:
        engine = RulePolicyEngine()
        policy = RulePolicy(name="Custom Policy", max_rules_per_set=50)
        engine.set_policy(policy)
        assert engine.get_policy().name == "Custom Policy"

    def test_check_access_policy(self) -> None:
        engine = RulePolicyEngine()
        rule = Rule(name="Test")
        violations = engine.check_access_policy(rule, user_id="user-1")
        assert violations == []

    def test_check_lifecycle_policy_disabled_rule(self) -> None:
        engine = RulePolicyEngine()
        rule = Rule(name="Test", enabled=False)
        violations = engine.check_lifecycle_policy(rule, RuleLifecycleStatus.ACTIVE)
        assert any("disabled" in v for v in violations)

    def test_check_lifecycle_policy_no_conditions(self) -> None:
        engine = RulePolicyEngine()
        rule = Rule(name="Test", enabled=True)
        violations = engine.check_lifecycle_policy(rule, RuleLifecycleStatus.APPROVED)
        assert any("condition" in v for v in violations)

    def test_check_lifecycle_policy_valid(self) -> None:
        engine = RulePolicyEngine()
        from adip.rules.contracts.models import RuleCondition
        rule = Rule(
            name="Test",
            enabled=True,
            conditions=[RuleCondition(field="temp", operator="gt", value="100")],
        )
        violations = engine.check_lifecycle_policy(rule, RuleLifecycleStatus.APPROVED)
        assert violations == []

    def test_check_version_policy_valid(self) -> None:
        engine = RulePolicyEngine()
        rule = Rule(name="Test", version=1)
        violations = engine.check_version_policy(rule, 2)
        assert violations == []

    def test_check_version_policy_invalid(self) -> None:
        engine = RulePolicyEngine()
        rule = Rule(name="Test", version=5)
        violations = engine.check_version_policy(rule, 3)
        assert len(violations) > 0

    def test_check_domain_policy_allowed_rule_types(self) -> None:
        policy = RulePolicy(allowed_rule_types=[RuleType.SAFETY])
        engine = RulePolicyEngine(policy=policy)
        rule = Rule(name="Test", rule_type=RuleType.BUSINESS)
        violations = engine.check_domain_policy(rule)
        assert len(violations) > 0

    def test_check_domain_policy_allowed_actions(self) -> None:
        policy = RulePolicy(allowed_actions=["alert"])
        engine = RulePolicyEngine(policy=policy)
        from adip.rules.contracts.models import RuleAction
        rule = Rule(
            name="Test",
            actions=[RuleAction(action_type="shutdown")],
        )
        violations = engine.check_domain_policy(rule)
        assert len(violations) > 0

    def test_check_all(self) -> None:
        engine = RulePolicyEngine()
        rule = Rule(name="Test")
        violations = engine.check_all(rule)
        assert isinstance(violations, list)
