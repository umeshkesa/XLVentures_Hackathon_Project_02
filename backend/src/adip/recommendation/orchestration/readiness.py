"""RecommendationReadiness — determines recommendation readiness.

Assesses whether a recommendation is ready for deployment,
requires further review, or is blocked by unresolved issues.
Deterministic placeholder implementation.
"""

from __future__ import annotations

import structlog

from adip.recommendation.enums import RecommendationReadinessStatus
from adip.recommendation.orchestration.review import ReviewResult

log = structlog.get_logger(__name__)


class RecommendationReadiness:
    """Determines readiness of recommendation decisions.

    Deterministic placeholder that assesses readiness based on
    review results, confidence, feasibility, and policy compliance.
    """

    def assess(
        self,
        review_result: ReviewResult | None = None,
        confidence: float = 0.0,
        feasibility_score: float = 0.0,
        policy_passed: bool = True,
    ) -> RecommendationReadinessStatus:
        """Assess the readiness of a recommendation.

        Args:
            review_result: The review result to consider.
            confidence: Overall confidence score (0.0-1.0).
            feasibility_score: Feasibility score (0.0-1.0).
            policy_passed: Whether policy checks passed.

        Returns:
            RecommendationReadinessStatus indicating readiness level.
        """
        if review_result:
            if review_result.violations:
                log.info("readiness.assess", status="BLOCKED", reason="review violations")
                return RecommendationReadinessStatus.BLOCKED
            if not review_result.passed:
                log.info("readiness.assess", status="REQUIRES_REVIEW", reason="review not passed")
                return RecommendationReadinessStatus.REQUIRES_REVIEW

        if not policy_passed:
            log.info("readiness.assess", status="BLOCKED", reason="policy failed")
            return RecommendationReadinessStatus.BLOCKED

        if confidence < 0.3:
            log.info("readiness.assess", status="REQUIRES_REVIEW", reason="low confidence")
            return RecommendationReadinessStatus.REQUIRES_REVIEW

        if feasibility_score < 0.3:
            log.info("readiness.assess", status="BLOCKED", reason="low feasibility")
            return RecommendationReadinessStatus.BLOCKED

        if confidence >= 0.7 and feasibility_score >= 0.7 and policy_passed:
            log.info("readiness.assess", status="READY")
            return RecommendationReadinessStatus.READY

        log.info("readiness.assess", status="REQUIRES_REVIEW", reason="conditional")
        return RecommendationReadinessStatus.REQUIRES_REVIEW

    def assess_portfolio(
        self,
        portfolio,
        review_result: ReviewResult | None = None,
    ) -> RecommendationReadinessStatus:
        """Assess readiness for a portfolio.

        Args:
            portfolio: The recommendation portfolio.
            review_result: Optional review result.

        Returns:
            RecommendationReadinessStatus.
        """
        confidence = getattr(portfolio, 'overall_confidence', 0.0) if portfolio else 0.0
        return self.assess(
            review_result=review_result,
            confidence=confidence,
            feasibility_score=confidence,
            policy_passed=True,
        )
