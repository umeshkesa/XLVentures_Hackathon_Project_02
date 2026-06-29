"""ActionReview — reviews and validates action plans.

Deterministic placeholder that performs 5-dimension review
of an action plan: completeness, consistency, feasibility,
safety, and compliance. Produces a review result with score
and issues.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import structlog
from pydantic import UUID4, BaseModel, Field

log = structlog.get_logger(__name__)


class ReviewResult(BaseModel):
    """Result of an action plan review."""

    review_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique review identifier",
    )
    plan_id: str = Field(
        default="",
        description="The plan being reviewed",
    )
    overall_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Overall review score",
    )
    completeness_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Completeness score",
    )
    consistency_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Consistency score",
    )
    feasibility_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Feasibility score",
    )
    safety_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Safety score",
    )
    compliance_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Compliance score",
    )
    issues: list[str] = Field(
        default_factory=list,
        description="Issues identified during review",
    )
    passed: bool = Field(
        default=True,
        description="Whether the plan passed review",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the review was completed",
    )


class ActionReview:
    """Reviews action plans for quality and readiness.

    Evaluates plans across 5 dimensions and produces
    a composite score.
    """

    def __init__(self) -> None:
        self._reviews: dict[str, ReviewResult] = {}

    def review(
        self,
        plan_id: str,
        step_count: int = 0,
        has_dependencies: bool = False,
        has_resources: bool = False,
        has_schedule: bool = False,
        has_rollback: bool = False,
        has_preconditions: bool = False,
        correlation_id: str = "",
    ) -> ReviewResult:
        """Review an action plan.

        Args:
            plan_id: The plan ID to review.
            step_count: Number of steps in the plan.
            has_dependencies: Whether dependencies are defined.
            has_resources: Whether resources are allocated.
            has_schedule: Whether schedule is defined.
            has_rollback: Whether rollback is configured.
            has_preconditions: Whether preconditions are defined.
            correlation_id: Optional correlation ID.

        Returns:
            ReviewResult with dimension scores.
        """
        issues: list[str] = []

        completeness = 1.0
        if step_count == 0:
            completeness -= 0.5
            issues.append("Plan has no steps")
        if not has_dependencies:
            completeness -= 0.1
            issues.append("No dependencies defined")
        if not has_resources:
            completeness -= 0.1
            issues.append("No resources allocated")
        if not has_schedule:
            completeness -= 0.1
            issues.append("No schedule defined")
        if not has_rollback:
            completeness -= 0.1
            issues.append("No rollback configured")
        completeness = max(0.0, completeness)

        consistency = 0.9 if step_count > 0 else 0.0
        if has_dependencies and step_count == 0:
            consistency -= 0.3
            issues.append("Dependencies defined but no steps")

        feasibility = 0.8
        if step_count > 20:
            feasibility -= 0.2
            issues.append("Plan has too many steps")
        if not has_resources:
            feasibility -= 0.2

        safety = 0.9
        if has_rollback:
            safety += 0.05
        if not has_preconditions:
            safety -= 0.1
            issues.append("No preconditions defined")
        safety = min(1.0, safety)

        compliance = 0.85
        if step_count == 0:
            compliance -= 0.3

        overall = round(
            (completeness + consistency + feasibility + safety + compliance) / 5,
            4,
        )
        passed = overall >= 0.5 and len([i for i in issues if "no steps" in i.lower()]) == 0

        result = ReviewResult(
            plan_id=plan_id,
            overall_score=overall,
            completeness_score=round(completeness, 4),
            consistency_score=round(consistency, 4),
            feasibility_score=round(feasibility, 4),
            safety_score=round(safety, 4),
            compliance_score=round(compliance, 4),
            issues=issues,
            passed=passed,
        )
        self._reviews[str(result.review_id)] = result
        log.info(
            "review.completed",
            plan_id=plan_id,
            score=overall,
            passed=passed,
        )
        return result

    def get_review(self, review_id: str) -> ReviewResult | None:
        """Retrieve a review by ID.

        Args:
            review_id: The review identifier.

        Returns:
            ReviewResult if found, None otherwise.
        """
        return self._reviews.get(review_id)

    def get_all_reviews(self) -> list[ReviewResult]:
        """Get all reviews.

        Returns:
            List of all ReviewResults.
        """
        return list(self._reviews.values())

    def clear(self) -> None:
        """Clear all reviews."""
        self._reviews.clear()
