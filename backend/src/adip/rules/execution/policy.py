"""RulePolicyEngine — enforces rule management policies.

Validates access policy, lifecycle policy, version policy,
approval policy, and domain policy for rule operations.
"""

from __future__ import annotations

import structlog

from adip.rules.contracts.models import Rule, RulePolicy
from adip.rules.enums import RuleLifecycleStatus

log = structlog.get_logger(__name__)


class RulePolicyEngine:
    """Enforces configurable policies for rule operations."""

    def __init__(self, policy: RulePolicy | None = None) -> None:
        self._policy: RulePolicy = policy or RulePolicy()

    def set_policy(self, policy: RulePolicy) -> None:
        """Set the active policy."""
        self._policy = policy
        log.info("rule_policy_engine.set_policy", policy_id=str(policy.policy_id))

    def get_policy(self) -> RulePolicy:
        """Return the current policy."""
        return self._policy

    def check_access_policy(self, rule: Rule, user_id: str = "") -> list[str]:
        """Validate that a rule can be accessed by a user.

        Placeholder — returns empty violations.
        """
        _ = user_id
        return []

    def check_lifecycle_policy(self, rule: Rule, to_status: RuleLifecycleStatus) -> list[str]:
        """Validate a lifecycle transition against policy."""
        violations: list[str] = []

        if to_status == RuleLifecycleStatus.ACTIVE and not rule.enabled:
            violations.append("Cannot activate a disabled rule")

        if to_status == RuleLifecycleStatus.APPROVED and not rule.conditions:
            violations.append("Rule must have at least one condition before approval")

        return violations

    def check_version_policy(self, rule: Rule, new_version: int) -> list[str]:
        """Validate a version change against policy."""
        violations: list[str] = []

        if new_version <= rule.version:
            violations.append(f"New version {new_version} must be greater than current version {rule.version}")

        return violations

    def check_approval_policy(self, rule: Rule, approved_by: str = "") -> list[str]:
        """Validate that a rule can be approved.

        Placeholder — returns empty violations.
        """
        _ = approved_by
        return []

    def check_domain_policy(self, rule: Rule) -> list[str]:
        """Validate that a rule's domain is allowed by policy."""
        violations: list[str] = []

        if self._policy.allowed_rule_types:
            if rule.rule_type not in self._policy.allowed_rule_types:
                violations.append(f"Rule type {rule.rule_type.value} is not allowed by policy")

        if self._policy.allowed_actions:
            for action in rule.actions:
                if action.action_type not in self._policy.allowed_actions:
                    violations.append(f"Action {action.action_type} is not allowed by policy")

        return violations

    def check_all(self, rule: Rule) -> list[str]:
        """Run all policy checks against a rule."""
        violations: list[str] = []
        violations.extend(self.check_domain_policy(rule))
        violations.extend(self.check_access_policy(rule))
        return violations
