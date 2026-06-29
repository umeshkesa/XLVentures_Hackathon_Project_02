"""PlanQualityManager — evaluates quality of action plans.

Deterministic placeholder assessing 6-dimension plan quality:
completeness, consistency, optimisability, maintainability,
testability, and observability. Produces an overall quality score.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import structlog
from pydantic import UUID4, BaseModel, Field

log = structlog.get_logger(__name__)


class QualityAssessment(BaseModel):
    """Result of a plan quality assessment."""

    assessment_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique assessment identifier",
    )
    plan_id: str = Field(
        default="",
        description="The plan being assessed",
    )
    overall_quality: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Overall quality score",
    )
    completeness: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Plan completeness score",
    )
    consistency: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Plan consistency score",
    )
    optimisability: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Plan optimisability score",
    )
    maintainability: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Plan maintainability score",
    )
    testability: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Plan testability score",
    )
    observability: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Plan observability score",
    )
    recommendations: list[str] = Field(
        default_factory=list,
        description="Recommendations for improvement",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the assessment was made",
    )


class PlanQualityManager:
    """Assesses quality of action plans.

    Evaluates plans across 6 quality dimensions and
    produces recommendations for improvement.
    """

    def __init__(self) -> None:
        self._assessments: dict[str, QualityAssessment] = {}

    def assess(
        self,
        plan_id: str,
        step_count: int = 0,
        has_dependencies: bool = False,
        has_resources: bool = False,
        has_schedule: bool = False,
        has_rollback: bool = False,
        has_preconditions: bool = False,
        has_postconditions: bool = False,
        correlation_id: str = "",
    ) -> QualityAssessment:
        """Assess the quality of an action plan.

        Args:
            plan_id: The plan ID to assess.
            step_count: Number of steps in the plan.
            has_dependencies: Whether dependencies are defined.
            has_resources: Whether resources are allocated.
            has_schedule: Whether schedule is defined.
            has_rollback: Whether rollback is configured.
            has_preconditions: Whether preconditions are defined.
            has_postconditions: Whether postconditions are defined.
            correlation_id: Optional correlation ID.

        Returns:
            QualityAssessment with dimension scores.
        """
        recommendations: list[str] = []

        completeness = 1.0
        missing = 0
        if step_count == 0:
            completeness -= 0.4
            recommendations.append("Add steps to the plan")
            missing += 1
        if not has_dependencies:
            completeness -= 0.15
            recommendations.append("Define dependencies")
            missing += 1
        if not has_resources:
            completeness -= 0.15
            recommendations.append("Allocate resources")
            missing += 1
        if not has_schedule:
            completeness -= 0.1
            recommendations.append("Define schedule")
            missing += 1
        if not has_rollback:
            completeness -= 0.1
            recommendations.append("Configure rollback")
            missing += 1
        if not has_preconditions:
            completeness -= 0.05
            recommendations.append("Add preconditions")
            missing += 1
        if not has_postconditions:
            completeness -= 0.05
            recommendations.append("Add postconditions")
            missing += 1
        completeness = max(0.0, completeness)

        consistency = 0.9 if step_count > 0 else 0.0
        if step_count > 20:
            consistency -= 0.2
            recommendations.append("Reduce number of steps for better consistency")

        optimisability = 0.7
        if has_dependencies:
            optimisability += 0.1
        if step_count > 5:
            optimisability += 0.1
        optimisability = min(1.0, optimisability)

        maintainability = 0.75
        if has_rollback:
            maintainability += 0.1
        if step_count > 0 and step_count <= 10:
            maintainability += 0.1
        maintainability = min(1.0, maintainability)

        testability = 0.65
        if has_preconditions:
            testability += 0.15
        if has_postconditions:
            testability += 0.15
        testability = min(1.0, testability)

        observability = 0.7
        if step_count > 0:
            observability += 0.1
        if has_schedule:
            observability += 0.1
        observability = min(1.0, observability)

        overall = round(
            (completeness + consistency + optimisability + maintainability + testability + observability) / 6,
            4,
        )

        assessment = QualityAssessment(
            plan_id=plan_id,
            overall_quality=overall,
            completeness=round(completeness, 4),
            consistency=round(consistency, 4),
            optimisability=round(optimisability, 4),
            maintainability=round(maintainability, 4),
            testability=round(testability, 4),
            observability=round(observability, 4),
            recommendations=recommendations,
        )
        self._assessments[str(assessment.assessment_id)] = assessment
        log.info(
            "quality.assessed",
            plan_id=plan_id,
            quality=overall,
        )
        return assessment

    def get_assessment(self, assessment_id: str) -> QualityAssessment | None:
        """Retrieve an assessment by ID.

        Args:
            assessment_id: The assessment identifier.

        Returns:
            QualityAssessment if found, None otherwise.
        """
        return self._assessments.get(assessment_id)

    def get_all_assessments(self) -> list[QualityAssessment]:
        """Get all assessments.

        Returns:
            List of all QualityAssessments.
        """
        return list(self._assessments.values())

    def clear(self) -> None:
        """Clear all assessments."""
        self._assessments.clear()
