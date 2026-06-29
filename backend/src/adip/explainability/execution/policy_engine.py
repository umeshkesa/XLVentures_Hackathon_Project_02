"""PolicyEngine — enforces explanation generation policies.

Deterministic placeholder that checks policy rules for
explanation generation constraints.
"""

from __future__ import annotations

import structlog

from adip.explainability.execution.models import PolicyRule

log = structlog.get_logger(__name__)

_POLICY_RULES: dict[str, PolicyRule] = {
    "SUMMARY": PolicyRule(
        policy_type="SUMMARY",
        name="Summary Policy",
        allowed_audiences=["EXECUTIVE", "MANAGER"],
        max_narratives=1,
        require_citations=False,
        require_trace=False,
        metadata={"description": "Brief summary explanations for executive audiences."},
    ),
    "STANDARD": PolicyRule(
        policy_type="STANDARD",
        name="Standard Policy",
        allowed_audiences=["EXECUTIVE", "MANAGER", "ENGINEER", "OPERATOR"],
        max_narratives=5,
        require_citations=False,
        require_trace=False,
        metadata={"description": "Standard explanations with moderate detail."},
    ),
    "FULL": PolicyRule(
        policy_type="FULL",
        name="Full Policy",
        allowed_audiences=["ENGINEER", "TECHNICIAN", "DEVELOPER"],
        max_narratives=10,
        require_citations=True,
        require_trace=True,
        metadata={"description": "Full technical explanations with citations and trace."},
    ),
    "AUDIT": PolicyRule(
        policy_type="AUDIT",
        name="Audit Policy",
        allowed_audiences=["AUDITOR", "MANAGER"],
        max_narratives=10,
        require_citations=True,
        require_trace=True,
        metadata={"description": "Audit-focused explanations requiring citations and trace."},
    ),
    "CONFIDENTIAL": PolicyRule(
        policy_type="CONFIDENTIAL",
        name="Confidential Policy",
        allowed_audiences=["EXECUTIVE", "AUDITOR"],
        max_narratives=3,
        require_citations=True,
        require_trace=False,
        metadata={"description": "Confidential explanations restricted to senior roles."},
    ),
}


class PolicyEngine:
    """Enforces explanation generation policies.

    Deterministic placeholder that validates explanation requests
    against predefined policy rules.
    """

    def __init__(self) -> None:
        self._policies: dict[str, PolicyRule] = dict(_POLICY_RULES)

    def check_policy(
        self,
        policy_type: str,
        audience: str,
        narrative_count: int,
        has_citations: bool,
        has_trace: bool,
    ) -> list[str]:
        """Check an explanation against policy constraints.

        Args:
            policy_type: The policy type to check against.
            audience: The target audience for the explanation.
            narrative_count: The number of narratives in the explanation.
            has_citations: Whether the explanation has citations.
            has_trace: Whether the explanation has trace records.

        Returns:
            List of policy violation descriptions (empty if compliant).
        """
        violations: list[str] = []
        policy = self._policies.get(policy_type)

        if not policy:
            violations.append(f"No policy found for type: {policy_type}")
            return violations

        if audience not in policy.allowed_audiences:
            violations.append(
                f"Audience '{audience}' not allowed by {policy_type} policy. "
                f"Allowed: {policy.allowed_audiences}"
            )

        if narrative_count > policy.max_narratives:
            violations.append(
                f"Narrative count {narrative_count} exceeds {policy_type} policy "
                f"maximum of {policy.max_narratives}."
            )

        if policy.require_citations and not has_citations:
            violations.append(f"{policy_type} policy requires citations but none provided.")

        if policy.require_trace and not has_trace:
            violations.append(f"{policy_type} policy requires trace but none provided.")

        if violations:
            log.info("Policy violations found", policy_type=policy_type, violations=violations)
        else:
            log.info("Policy check passed", policy_type=policy_type)

        return violations

    def get_policy(self, policy_type: str) -> PolicyRule | None:
        """Get a policy rule by type.

        Args:
            policy_type: The policy type identifier.

        Returns:
            The PolicyRule if found, None otherwise.
        """
        return self._policies.get(policy_type)

    def list_policies(self) -> list[PolicyRule]:
        """List all available policies.

        Returns:
            List of all registered PolicyRule instances.
        """
        return list(self._policies.values())
