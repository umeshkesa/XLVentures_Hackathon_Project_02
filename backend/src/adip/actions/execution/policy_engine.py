"""ActionPolicyEngine — safety, business, resource and compliance policy validation.

Validates action plans against multiple policy domains:
safety policies, business rules, resource policies, and
compliance requirements, using deterministic placeholder checks.
"""

from __future__ import annotations

import structlog

from adip.actions.execution.models import PolicyResult

log = structlog.get_logger(__name__)


class ActionPolicyEngine:
    """Validates action plans against safety, business, resource, and compliance policies."""

    def validate(
        self,
        plan_id: str = "",
        action_type: str = "AUTOMATED",
        priority: str = "MEDIUM",
        domain: str = "",
        step_count: int = 0,
        correlation_id: str = "",
    ) -> PolicyResult:
        """Validate an action plan against all policy domains.

        Uses deterministic placeholder heuristics:
        - EMERGENCY actions bypass some safety policies
        - MANUAL actions require additional safety checks
        - HIGH/CRITICAL priority triggers business policy review
        - EXTERNAL_INTEGRATION requires compliance checks
        - ENERGY/SAFETY domains have stricter safety policies
        - >10 steps triggers resource policy review
        - COMPLIANCE domain triggers compliance policy review

        Args:
            plan_id: The plan ID.
            action_type: The action type string.
            priority: The priority string.
            domain: The domain string.
            step_count: Number of steps.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            PolicyResult with per-domain violations.
        """
        at = action_type.upper() if action_type else "AUTOMATED"
        pri = priority.upper() if priority else "MEDIUM"
        dom = domain.upper() if domain else ""

        safety_violations = self._check_safety(at, dom)
        business_violations = self._check_business(pri, step_count)
        resource_violations = self._check_resource(at, step_count)
        compliance_violations = self._check_compliance(at, dom)

        total = len(safety_violations) + len(business_violations) + len(resource_violations) + len(compliance_violations)

        result = PolicyResult(
            plan_id=plan_id,
            safety_policy_violations=safety_violations,
            business_policy_violations=business_violations,
            resource_policy_violations=resource_violations,
            compliance_policy_violations=compliance_violations,
            is_policy_compliant=total == 0,
            total_violations=total,
        )
        log.info(
            "policy_engine.validated",
            plan_id=plan_id,
            is_compliant=result.is_policy_compliant,
            violations=total,
            correlation_id=correlation_id,
        )
        return result

    def _check_safety(self, action_type: str, domain: str) -> list[str]:
        violations: list[str] = []
        if action_type == "MANUAL" and domain == "ENERGY":
            violations.append("Manual energy actions require lockout/tagout verification")
        if domain == "SAFETY" and action_type != "EMERGENCY":
            violations.append("Safety domain actions require safety officer approval")
        if action_type == "EXTERNAL_INTEGRATION" and domain == "SAFETY":
            violations.append("External integrations in safety domain require additional validation")
        return violations

    def _check_business(self, priority: str, step_count: int) -> list[str]:
        violations: list[str] = []
        if priority in ("CRITICAL", "HIGH") and step_count > 5:
            violations.append("High-priority actions with >5 steps require business case approval")
        if step_count > 15:
            violations.append("Actions with >15 steps require workflow simplification review")
        return violations

    def _check_resource(self, action_type: str, step_count: int) -> list[str]:
        violations: list[str] = []
        if step_count > 10:
            violations.append("Actions with >10 steps require resource pool pre-authorisation")
        if action_type == "MANUAL" and step_count > 5:
            violations.append("Manual actions with >5 steps require additional personnel allocation")
        return violations

    def _check_compliance(self, action_type: str, domain: str) -> list[str]:
        violations: list[str] = []
        if action_type == "EXTERNAL_INTEGRATION":
            violations.append("External integrations require data protection compliance check")
        if domain == "COMPLIANCE":
            violations.append("Compliance domain actions require regulatory review")
        if action_type == "EMERGENCY":
            violations.append("Emergency actions require post-action compliance reporting")
        return violations

    def check_policy_compliance(
        self,
        plan_id: str = "",
        result: PolicyResult | None = None,
    ) -> bool:
        """Check if a plan is fully policy compliant."""
        if result is None:
            return True
        return result.is_policy_compliant
