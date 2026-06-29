"""ExecutionPackageBuilder — builds execution packages from action plans.

Deterministic placeholder that bundles an action plan with
all execution metadata (resources, schedule, risk, cost,
compensation) into a self-contained execution package ready
for the Action Engine.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

import structlog
from pydantic import UUID4, BaseModel, Field

log = structlog.get_logger(__name__)


class ExecutionPackage(BaseModel):
    """A self-contained execution package for an action plan."""

    package_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique package identifier",
    )
    plan_id: str = Field(
        default="",
        description="The plan this package wraps",
    )
    step_count: int = Field(
        default=0,
        ge=0,
        description="Number of steps in the package",
    )
    has_rollback: bool = Field(
        default=False,
        description="Whether rollback is configured",
    )
    resource_summary: str = Field(
        default="",
        description="Summary of resource allocations",
    )
    schedule_summary: str = Field(
        default="",
        description="Summary of execution schedule",
    )
    risk_summary: str = Field(
        default="",
        description="Summary of risk assessment",
    )
    cost_summary: str = Field(
        default="",
        description="Summary of cost estimate",
    )
    compensation_summary: str = Field(
        default="",
        description="Summary of compensation strategies",
    )
    readiness_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Readiness score at packaging time",
    )
    version: str = Field(
        default="1.0.0",
        description="Package version",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional package metadata",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the package was created",
    )


class ExecutionPackageBuilder:
    """Builds execution packages from action plans.

    Combines plan data with execution metadata into a
    self-contained package.
    """

    def __init__(self) -> None:
        self._packages: dict[str, ExecutionPackage] = {}

    def build(
        self,
        plan_id: str,
        step_count: int = 0,
        has_rollback: bool = False,
        resource_summary: str = "",
        schedule_summary: str = "",
        risk_summary: str = "",
        cost_summary: str = "",
        compensation_summary: str = "",
        readiness_score: float = 0.0,
        correlation_id: str = "",
    ) -> ExecutionPackage:
        """Build an execution package from plan data.

        Args:
            plan_id: The plan ID to package.
            step_count: Number of steps in the plan.
            has_rollback: Whether rollback is configured.
            resource_summary: Resource allocation summary.
            schedule_summary: Schedule summary.
            risk_summary: Risk assessment summary.
            cost_summary: Cost estimate summary.
            compensation_summary: Compensation strategy summary.
            readiness_score: Readiness score.
            correlation_id: Optional correlation ID.

        Returns:
            ExecutionPackage with bundled metadata.
        """
        pkg = ExecutionPackage(
            plan_id=plan_id,
            step_count=step_count,
            has_rollback=has_rollback,
            resource_summary=resource_summary or f"{'Resources allocated' if step_count > 0 else 'No resources'}",
            schedule_summary=schedule_summary or f"{'Schedule defined' if step_count > 0 else 'No schedule'}",
            risk_summary=risk_summary or "Risk assessment completed",
            cost_summary=cost_summary or "Cost estimate available",
            compensation_summary=compensation_summary or "Compensation strategies defined",
            readiness_score=round(readiness_score, 4),
        )
        self._packages[str(pkg.package_id)] = pkg
        log.info(
            "package.built",
            plan_id=plan_id,
            package_id=str(pkg.package_id),
        )
        return pkg

    def get_package(self, package_id: str) -> ExecutionPackage | None:
        """Retrieve a package by ID.

        Args:
            package_id: The package identifier.

        Returns:
            ExecutionPackage if found, None otherwise.
        """
        return self._packages.get(package_id)

    def get_all_packages(self) -> list[ExecutionPackage]:
        """Get all packages.

        Returns:
            List of all ExecutionPackages.
        """
        return list(self._packages.values())

    def clear(self) -> None:
        """Clear all packages."""
        self._packages.clear()
