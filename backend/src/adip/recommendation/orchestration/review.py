"""RecommendationReview — validates recommendation quality.

Reviews recommendation results for policy compliance, feasibility,
dependencies, portfolio completeness, and confidence.
Deterministic placeholder implementation.
"""

from __future__ import annotations

from typing import Any

import structlog

from adip.recommendation.execution.models import (
    FeasibilityAnalysis,
    PolicyEvalResult,
    RecommendationPortfolio,
)

log = structlog.get_logger(__name__)


class ReviewResult:
    """Result of a recommendation review.

    Attributes:
        passed: Whether the review passed.
        policy_compliant: Whether policy compliance passed.
        feasible: Whether feasibility passed.
        dependencies_resolved: Whether dependencies are resolved.
        portfolio_complete: Whether the portfolio is complete.
        confidence_adequate: Whether confidence is adequate.
        violations: List of review violations.
        warnings: List of review warnings.
        details: Detailed review breakdown.
    """

    def __init__(
        self,
        passed: bool = True,
        policy_compliant: bool = True,
        feasible: bool = True,
        dependencies_resolved: bool = True,
        portfolio_complete: bool = True,
        confidence_adequate: bool = True,
        business_goals_aligned: bool = True,
        violations: list[str] | None = None,
        warnings: list[str] | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.passed = passed
        self.policy_compliant = policy_compliant
        self.feasible = feasible
        self.dependencies_resolved = dependencies_resolved
        self.portfolio_complete = portfolio_complete
        self.confidence_adequate = confidence_adequate
        self.business_goals_aligned = business_goals_aligned
        self.violations = violations or []
        self.warnings = warnings or []
        self.details = details or {}


class RecommendationReview:
    """Reviews recommendation results for quality and completeness.

    Deterministic placeholder that validates policy compliance,
    feasibility, dependencies, portfolio completeness, and confidence.
    """

    def review(
        self,
        policy_result: PolicyEvalResult | None = None,
        feasibility: FeasibilityAnalysis | None = None,
        portfolio: RecommendationPortfolio | None = None,
        confidence: float = 0.0,
        has_dependencies: bool = True,
        business_goals: list[str] | None = None,
    ) -> ReviewResult:
        """Review a recommendation for quality and completeness.

        Args:
            policy_result: The policy evaluation result.
            feasibility: The feasibility analysis.
            portfolio: The recommendation portfolio.
            confidence: The overall confidence score.
            has_dependencies: Whether dependencies exist.
            business_goals: Optional list of business goals.

        Returns:
            ReviewResult with review findings.
        """
        violations: list[str] = []
        warnings: list[str] = []

        business_goals_aligned = len(business_goals) > 0 if business_goals else True
        if business_goals is not None and len(business_goals) == 0:
            violations.append("No business goals provided for alignment check")

        policy_compliant = policy_result.overall_passed if policy_result else True
        if policy_result and not policy_result.overall_passed:
            violations.extend(policy_result.violations)
            warnings.extend(policy_result.warnings)

        feasible = (feasibility.status.value in ("FEASIBLE", "PARTIALLY_FEASIBLE")) if feasibility else True
        if feasibility and feasibility.status.value == "NOT_FEASIBLE":
            violations.append("Recommendation is not feasible")

        dependencies_resolved = has_dependencies or True

        portfolio_complete = portfolio is not None
        if portfolio is None:
            violations.append("No portfolio created")

        confidence_adequate = confidence >= 0.3
        if confidence < 0.3:
            warnings.append("Confidence below 0.3 threshold")

        passed = policy_compliant and feasible and portfolio_complete and confidence_adequate and business_goals_aligned

        log.info(
            "review.complete",
            passed=passed,
            policy=policy_compliant,
            feasible=feasible,
            portfolio=portfolio_complete,
            confidence=confidence_adequate,
        )
        return ReviewResult(
            passed=passed,
            policy_compliant=policy_compliant,
            feasible=feasible,
            dependencies_resolved=dependencies_resolved,
            portfolio_complete=portfolio_complete,
            confidence_adequate=confidence_adequate,
            business_goals_aligned=business_goals_aligned,
            violations=violations,
            warnings=warnings,
        )
