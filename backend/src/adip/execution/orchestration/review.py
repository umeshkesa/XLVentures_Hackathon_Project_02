"""ExecutionReview — reviews and validates execution operations.

Deterministic placeholder that performs 5-dimension review
of an execution session: completeness, consistency, feasibility,
safety, and compliance.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import structlog
from pydantic import UUID4, BaseModel, Field

log = structlog.get_logger(__name__)


class ReviewResult(BaseModel):
    """Result of an execution review."""

    review_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique review identifier",
    )
    session_id: str = Field(
        default="",
        description="The session being reviewed",
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
        description="Whether the session passed review",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the review was completed",
    )


class ExecutionReview:
    """Reviews execution operations for quality and readiness.

    Evaluates sessions across 5 dimensions and produces
    a composite score.
    """

    def __init__(self) -> None:
        self._reviews: dict[str, ReviewResult] = {}

    def review(
        self,
        session_id: str,
        task_count: int = 0,
        has_dependencies: bool = False,
        has_resources: bool = False,
        has_schedule: bool = False,
        has_compensation: bool = False,
        correlation_id: str = "",
    ) -> ReviewResult:
        """Perform a review of an execution session.

        All scores are computed as deterministic heuristics
        based on the provided parameters.

        Args:
            session_id: The session ID to review.
            task_count: Number of tasks in the session.
            has_dependencies: Whether dependencies are defined.
            has_resources: Whether resources are allocated.
            has_schedule: Whether schedule is defined.
            has_compensation: Whether compensation is configured.
            correlation_id: Optional correlation ID.

        Returns:
            ReviewResult with dimension scores.
        """
        completeness = 0.9 if task_count > 0 else 0.1
        consistency = 1.0 if has_dependencies else 0.5
        feasibility = 0.8 if has_resources else 0.3
        safety = 0.9 if has_compensation else 0.4
        compliance = 0.85 if has_schedule else 0.5

        issues: list[str] = []
        if task_count == 0:
            issues.append("No tasks defined")
        if not has_resources:
            issues.append("No resources allocated")
        if not has_compensation:
            issues.append("No compensation configured")
        if not has_schedule:
            issues.append("No schedule defined")

        overall = (
            completeness * 0.25
            + consistency * 0.20
            + feasibility * 0.20
            + safety * 0.20
            + compliance * 0.15
        )
        passed = overall >= 0.5 and task_count > 0

        result = ReviewResult(
            session_id=session_id,
            overall_score=round(overall, 4),
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
            session_id=session_id,
            score=round(overall, 4),
            passed=passed,
            cid=correlation_id,
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

    def get_reviews_for_session(self, session_id: str) -> list[ReviewResult]:
        """Get all reviews for a session.

        Args:
            session_id: The session identifier.

        Returns:
            List of ReviewResult objects.
        """
        return [
            r for r in self._reviews.values()
            if r.session_id == session_id
        ]

    def get_all_reviews(self) -> list[ReviewResult]:
        """Get all reviews.

        Returns:
            List of all ReviewResult objects.
        """
        return list(self._reviews.values())
