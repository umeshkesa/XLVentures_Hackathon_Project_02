"""RecommendationApprovalReadiness — determines approval readiness.

Assesses whether a recommendation is ready for approval, requires
further review, or is blocked by unresolved issues.
Deterministic placeholder implementation.
"""

from __future__ import annotations

import structlog

from adip.recommendation.orchestration.review import ReviewResult

log = structlog.get_logger(__name__)


class ApprovalReadinessResult:
    """Result of an approval readiness assessment.

    Attributes:
        status: Readiness status (READY, REVIEW_REQUIRED, BLOCKED).
        confidence_adequate: Whether confidence meets minimum threshold.
        feasibility_adequate: Whether feasibility meets minimum threshold.
        policy_passed: Whether policy checks passed.
        review_passed: Whether the review passed.
        quality_adequate: Whether quality meets minimum threshold.
        reasons: List of reasons for the status.
    """

    def __init__(
        self,
        status: str = "REVIEW_REQUIRED",
        confidence_adequate: bool = False,
        feasibility_adequate: bool = False,
        policy_passed: bool = True,
        review_passed: bool = True,
        quality_adequate: bool = False,
        reasons: list[str] | None = None,
    ) -> None:
        self.status = status
        self.confidence_adequate = confidence_adequate
        self.feasibility_adequate = feasibility_adequate
        self.policy_passed = policy_passed
        self.review_passed = review_passed
        self.quality_adequate = quality_adequate
        self.reasons = reasons or []


class RecommendationApprovalReadiness:
    """Determines approval readiness for recommendations.

    Deterministic placeholder that assesses readiness based on
    review results, confidence, feasibility, policy compliance,
    and quality scores.
    """

    def assess(
        self,
        review_result: ReviewResult | None = None,
        confidence: float = 0.0,
        feasibility_score: float = 0.0,
        policy_passed: bool = True,
        quality_score: float = 0.0,
    ) -> ApprovalReadinessResult:
        """Assess approval readiness.

        Args:
            review_result: The review result.
            confidence: Overall confidence score (0.0-1.0).
            feasibility_score: Feasibility score (0.0-1.0).
            policy_passed: Whether policy checks passed.
            quality_score: Quality score (0.0-1.0).

        Returns:
            ApprovalReadinessResult with status and reasons.
        """
        reasons: list[str] = []
        review_passed = review_result.passed if review_result else True

        if review_result and review_result.violations:
            reasons.append("Review violations found")

        if not policy_passed:
            reasons.append("Policy check failed")

        if feasibility_score < 0.3:
            reasons.append("Feasibility below 0.3 threshold")

        if quality_score < 0.3:
            reasons.append("Quality below 0.3 threshold")

        confidence_adequate = confidence >= 0.3
        feasibility_adequate = feasibility_score >= 0.3
        quality_adequate = quality_score >= 0.3

        if (
            (review_result and review_result.violations)
            or not policy_passed
            or feasibility_score < 0.3
            or quality_score < 0.3
        ):
            status = "BLOCKED"
        elif confidence < 0.5 or quality_score < 0.5:
            status = "REVIEW_REQUIRED"
            if confidence < 0.5:
                reasons.append("Confidence below 0.5")
            if quality_score < 0.5:
                reasons.append("Quality below 0.5")
        elif confidence >= 0.7 and feasibility_score >= 0.7 and quality_score >= 0.7:
            status = "READY"
        else:
            status = "REVIEW_REQUIRED"
            reasons.append("Conditional - thresholds not fully met")

        log.info(
            "approval_readiness.assess",
            status=status,
            confidence=confidence,
            feasibility=feasibility_score,
            quality=quality_score,
        )
        return ApprovalReadinessResult(
            status=status,
            confidence_adequate=confidence_adequate,
            feasibility_adequate=feasibility_adequate,
            policy_passed=policy_passed,
            review_passed=review_passed,
            quality_adequate=quality_adequate,
            reasons=reasons,
        )
