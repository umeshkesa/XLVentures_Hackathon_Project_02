"""ExecutionReadinessReport — generates readiness summary reports.

Deterministic placeholder that produces a comprehensive readiness
summary combining readiness assessment, policy compliance, resource
availability, and schedule feasibility. Phase 3.5.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import structlog
from pydantic import UUID4, BaseModel, Field

log = structlog.get_logger(__name__)


class ReadinessReport(BaseModel):
    """Comprehensive readiness report for an execution session."""

    report_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique report identifier",
    )
    session_id: str = Field(
        default="",
        description="The session this report describes",
    )
    overall_status: str = Field(
        default="",
        description="Overall readiness status",
    )
    overall_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Overall readiness score",
    )
    resources_available: bool = Field(
        default=False,
        description="Whether resources are available",
    )
    dependencies_satisfied: bool = Field(
        default=False,
        description="Whether dependencies are satisfied",
    )
    schedule_feasible: bool = Field(
        default=False,
        description="Whether schedule is feasible",
    )
    policy_compliant: bool = Field(
        default=False,
        description="Whether policy is compliant",
    )
    risk_accepted: bool = Field(
        default=False,
        description="Whether risk is accepted",
    )
    passed_checks: int = Field(
        default=0,
        ge=0,
        le=5,
        description="Number of checks that passed",
    )
    total_checks: int = Field(
        default=5,
        ge=0,
        description="Total number of checks",
    )
    issues: list[str] = Field(
        default_factory=list,
        description="Issues blocking readiness",
    )
    summary: str = Field(
        default="",
        description="Human-readable readiness summary",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the report was generated",
    )


class ExecutionReadinessReport:
    """Generates readiness summary reports.

    Combines readiness assessment data into a comprehensive
    summary with status, score, and actionable issues.
    """

    def __init__(self) -> None:
        self._reports: dict[str, ReadinessReport] = {}

    def generate(
        self,
        session_id: str,
        resources_available: bool = False,
        dependencies_satisfied: bool = False,
        schedule_feasible: bool = False,
        policy_compliant: bool = False,
        risk_accepted: bool = False,
        correlation_id: str = "",
    ) -> ReadinessReport:
        """Generate a readiness report.

        Args:
            session_id: The session ID.
            resources_available: Whether resources are available.
            dependencies_satisfied: Whether dependencies are satisfied.
            schedule_feasible: Whether schedule is feasible.
            policy_compliant: Whether policy is compliant.
            risk_accepted: Whether risk is accepted.
            correlation_id: Optional correlation ID.

        Returns:
            The generated ReadinessReport.
        """
        checks = {
            "resources_available": resources_available,
            "dependencies_satisfied": dependencies_satisfied,
            "schedule_feasible": schedule_feasible,
            "policy_compliant": policy_compliant,
            "risk_accepted": risk_accepted,
        }
        passed = sum(1 for v in checks.values() if v)
        total = len(checks)
        score = passed / total if total > 0 else 0.0

        issues: list[str] = []
        if not resources_available:
            issues.append("Resources not available")
        if not dependencies_satisfied:
            issues.append("Dependencies not satisfied")
        if not schedule_feasible:
            issues.append("Schedule not feasible")
        if not policy_compliant:
            issues.append("Policy not compliant")
        if not risk_accepted:
            issues.append("Risk not accepted")

        all_ok = passed == total
        status = "READY" if all_ok else "NOT_READY"
        summary = (
            "All readiness checks passed" if all_ok
            else f"{len(issues)} readiness issue(s): {'; '.join(issues[:3])}"
        )

        report = ReadinessReport(
            session_id=session_id,
            overall_status=status,
            overall_score=round(score, 4),
            resources_available=resources_available,
            dependencies_satisfied=dependencies_satisfied,
            schedule_feasible=schedule_feasible,
            policy_compliant=policy_compliant,
            risk_accepted=risk_accepted,
            passed_checks=passed,
            total_checks=total,
            issues=issues,
            summary=summary,
        )
        self._reports[str(report.report_id)] = report
        log.info(
            "readiness_report.generated",
            session_id=session_id,
            status=status,
            score=round(score, 4),
            cid=correlation_id,
        )
        return report

    def get_report(self, report_id: str) -> ReadinessReport | None:
        """Retrieve a report by ID.

        Args:
            report_id: The report identifier.

        Returns:
            ReadinessReport if found, None otherwise.
        """
        return self._reports.get(report_id)

    def get_reports_for_session(self, session_id: str) -> list[ReadinessReport]:
        """Get all reports for a session.

        Args:
            session_id: The session identifier.

        Returns:
            List of ReadinessReport objects.
        """
        return [r for r in self._reports.values() if r.session_id == session_id]
