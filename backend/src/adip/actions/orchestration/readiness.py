"""ActionExecutionReadiness — assesses readiness for action execution.

Deterministic placeholder evaluating execution readiness based on
resource availability, dependency satisfaction, schedule feasibility,
policy compliance, and risk acceptance. Returns both a status
(READY/BLOCKED/WAITING/SCHEDULED) and a numeric score.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import structlog
from pydantic import UUID4, BaseModel, Field

from adip.actions.enums import ExecutionReadiness

log = structlog.get_logger(__name__)


class ReadinessAssessment(BaseModel):
    """Result of an execution readiness assessment."""

    assessment_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique assessment identifier",
    )
    plan_id: str = Field(
        default="",
        description="The plan this assessment belongs to",
    )
    status: ExecutionReadiness = Field(
        default=ExecutionReadiness.WAITING,
        description="Readiness status",
    )
    score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Readiness score (0.0 to 1.0)",
    )
    reason: str = Field(
        default="",
        description="Reason for the readiness assessment",
    )
    checks: dict[str, bool] = Field(
        default_factory=dict,
        description="Individual readiness check results",
    )
    issues: list[str] = Field(
        default_factory=list,
        description="Issues preventing readiness",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the assessment was made",
    )


class ActionExecutionReadiness:
    """Assesses execution readiness for action plans.

    Evaluates 5 readiness dimensions and returns a status
    and score.
    """

    def __init__(self) -> None:
        self._assessments: dict[str, ReadinessAssessment] = {}

    def assess(
        self,
        plan_id: str,
        resources_available: bool = True,
        dependencies_satisfied: bool = True,
        schedule_feasible: bool = True,
        policy_compliant: bool = True,
        risk_accepted: bool = True,
        correlation_id: str = "",
    ) -> ReadinessAssessment:
        """Assess execution readiness for a plan.

        Args:
            plan_id: The plan ID to assess.
            resources_available: Whether resources are available.
            dependencies_satisfied: Whether dependencies are satisfied.
            schedule_feasible: Whether schedule is feasible.
            policy_compliant: Whether policy checks pass.
            risk_accepted: Whether risks are accepted.
            correlation_id: Optional correlation ID.

        Returns:
            ReadinessAssessment with status and score.
        """
        checks = {
            "resources_available": resources_available,
            "dependencies_satisfied": dependencies_satisfied,
            "schedule_feasible": schedule_feasible,
            "policy_compliant": policy_compliant,
            "risk_accepted": risk_accepted,
        }

        passed = sum(1 for v in checks.values() if v)
        score = passed / len(checks) if checks else 0.0

        issues: list[str] = []
        if not resources_available:
            issues.append("Resources not available")
        if not dependencies_satisfied:
            issues.append("Dependencies not satisfied")
        if not schedule_feasible:
            issues.append("Schedule not feasible")
        if not policy_compliant:
            issues.append("Policy compliance not met")
        if not risk_accepted:
            issues.append("Risks not accepted")

        if score >= 1.0:
            status = ExecutionReadiness.READY
            reason = "All readiness checks passed"
        elif score >= 0.6:
            status = ExecutionReadiness.WAITING
            reason = f"Some checks pending: {'; '.join(issues)}"
        else:
            status = ExecutionReadiness.BLOCKED
            reason = f"Multiple checks failed: {'; '.join(issues)}"

        assessment = ReadinessAssessment(
            plan_id=plan_id,
            status=status,
            score=round(score, 4),
            reason=reason,
            checks=checks,
            issues=issues,
        )
        self._assessments[str(assessment.assessment_id)] = assessment
        log.info(
            "readiness.assessed",
            plan_id=plan_id,
            status=status,
            score=score,
        )
        return assessment

    def get_assessment(self, assessment_id: str) -> ReadinessAssessment | None:
        """Retrieve an assessment by ID.

        Args:
            assessment_id: The assessment identifier.

        Returns:
            ReadinessAssessment if found, None otherwise.
        """
        return self._assessments.get(assessment_id)

    def get_all_assessments(self) -> list[ReadinessAssessment]:
        """Get all assessments.

        Returns:
            List of all ReadinessAssessments.
        """
        return list(self._assessments.values())

    def clear(self) -> None:
        """Clear all assessments."""
        self._assessments.clear()
