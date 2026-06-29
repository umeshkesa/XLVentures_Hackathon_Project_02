"""PolicyEngine — enforces reasoning policies.

Supports STRICT, BALANCED, CONSERVATIVE, AGGRESSIVE, and
EMERGENCY policy types for reasoning decisions.
Deterministic placeholder implementation.
"""

from __future__ import annotations

import structlog

from adip.reasoning.enums import PolicyType
from adip.reasoning.execution.models import PolicyDecision

log = structlog.get_logger(__name__)


class PolicyEngine:
    """Enforces policies for reasoning operations.

    Deterministic placeholder that checks reasoning decisions
    against configured policies with different strictness levels.
    """

    def check(
        self,
        policy_type: PolicyType = PolicyType.BALANCED,
        confidence: float = 0.0,
        contradiction_count: int = 0,
        constraint_violations: int = 0,
    ) -> PolicyDecision:
        """Check a reasoning decision against a policy.

        Args:
            policy_type: The policy to enforce.
            confidence: The confidence in the decision (0.0–1.0).
            contradiction_count: Number of contradictions found.
            constraint_violations: Number of constraint violations.

        Returns:
            A PolicyDecision indicating whether the operation is allowed.
        """
        log.info(
            "policy_engine.check",
            policy=policy_type.value,
            confidence=confidence,
            contradictions=contradiction_count,
            violations=constraint_violations,
        )

        if policy_type == PolicyType.EMERGENCY:
            return self._check_emergency(confidence, contradiction_count, constraint_violations)
        if policy_type == PolicyType.STRICT:
            return self._check_strict(confidence, contradiction_count, constraint_violations)
        if policy_type == PolicyType.CONSERVATIVE:
            return self._check_conservative(confidence, contradiction_count, constraint_violations)
        if policy_type == PolicyType.AGGRESSIVE:
            return self._check_aggressive(confidence, contradiction_count, constraint_violations)
        return self._check_balanced(confidence, contradiction_count, constraint_violations)

    def _check_strict(
        self,
        confidence: float,
        contradiction_count: int,
        constraint_violations: int,
    ) -> PolicyDecision:
        """Strict policy — requires high confidence, no contradictions, no violations.

        Args:
            confidence: Confidence score.
            contradiction_count: Number of contradictions.
            constraint_violations: Number of violations.

        Returns:
            PolicyDecision.
        """
        allowed = confidence >= 0.8 and contradiction_count == 0 and constraint_violations == 0
        reasoning = [
            f"Strict policy: confidence={confidence:.2f} (requires >= 0.80)",
            f"Contradictions: {contradiction_count} (requires 0)",
            f"Constraint violations: {constraint_violations} (requires 0)",
        ]
        return PolicyDecision(
            policy_type=PolicyType.STRICT,
            allowed=allowed,
            reasoning=reasoning,
            confidence=confidence if allowed else max(0.0, confidence - 0.3),
        )

    def _check_balanced(
        self,
        confidence: float,
        contradiction_count: int,
        constraint_violations: int,
    ) -> PolicyDecision:
        """Balanced policy — moderate thresholds.

        Args:
            confidence: Confidence score.
            contradiction_count: Number of contradictions.
            constraint_violations: Number of violations.

        Returns:
            PolicyDecision.
        """
        allowed = confidence >= 0.5 and contradiction_count <= 2 and constraint_violations <= 1
        reasoning = [
            f"Balanced policy: confidence={confidence:.2f} (requires >= 0.50)",
            f"Contradictions: {contradiction_count} (allows <= 2)",
            f"Constraint violations: {constraint_violations} (allows <= 1)",
        ]
        return PolicyDecision(
            policy_type=PolicyType.BALANCED,
            allowed=allowed,
            reasoning=reasoning,
            confidence=confidence,
        )

    def _check_conservative(
        self,
        confidence: float,
        contradiction_count: int,
        constraint_violations: int,
    ) -> PolicyDecision:
        """Conservative policy — requires high confidence, minimal contradictions.

        Args:
            confidence: Confidence score.
            contradiction_count: Number of contradictions.
            constraint_violations: Number of violations.

        Returns:
            PolicyDecision.
        """
        allowed = confidence >= 0.7 and contradiction_count <= 1 and constraint_violations == 0
        reasoning = [
            f"Conservative policy: confidence={confidence:.2f} (requires >= 0.70)",
            f"Contradictions: {contradiction_count} (allows <= 1)",
            f"Constraint violations: {constraint_violations} (requires 0)",
        ]
        return PolicyDecision(
            policy_type=PolicyType.CONSERVATIVE,
            allowed=allowed,
            reasoning=reasoning,
            confidence=confidence if allowed else max(0.0, confidence - 0.2),
        )

    def _check_aggressive(
        self,
        confidence: float,
        contradiction_count: int,
        constraint_violations: int,
    ) -> PolicyDecision:
        """Aggressive policy — accepts lower confidence and some issues.

        Args:
            confidence: Confidence score.
            contradiction_count: Number of contradictions.
            constraint_violations: Number of violations.

        Returns:
            PolicyDecision.
        """
        allowed = confidence >= 0.3 and contradiction_count <= 5 and constraint_violations <= 3
        reasoning = [
            f"Aggressive policy: confidence={confidence:.2f} (requires >= 0.30)",
            f"Contradictions: {contradiction_count} (allows <= 5)",
            f"Constraint violations: {constraint_violations} (allows <= 3)",
        ]
        return PolicyDecision(
            policy_type=PolicyType.AGGRESSIVE,
            allowed=allowed,
            reasoning=reasoning,
            confidence=confidence,
        )

    def _check_emergency(
        self,
        confidence: float,
        contradiction_count: int,
        constraint_violations: int,
    ) -> PolicyDecision:
        """Emergency policy — bypasses normal checks.

        Args:
            confidence: Confidence score.
            contradiction_count: Number of contradictions.
            constraint_violations: Number of violations.

        Returns:
            PolicyDecision.
        """
        reasoning = [
            "Emergency policy: bypassing standard checks",
            f"Confidence: {confidence:.2f} (not enforced)",
            f"Contradictions: {contradiction_count} (ignored)",
            f"Constraint violations: {constraint_violations} (ignored)",
        ]
        return PolicyDecision(
            policy_type=PolicyType.EMERGENCY,
            allowed=True,
            reasoning=reasoning,
            confidence=max(0.3, confidence),
        )
