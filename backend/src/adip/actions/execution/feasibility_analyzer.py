"""ActionFeasibilityAnalyzer — resource, budget, skills, schedule and dependency feasibility.

Evaluates whether an action plan is feasible across five
dimensions: resource availability, budget sufficiency,
skill availability, schedule feasibility, and dependency
satisfaction, using deterministic placeholder checks.
"""

from __future__ import annotations

import structlog

from adip.actions.execution.models import FeasibilityResult, ResourceAllocationResult

log = structlog.get_logger(__name__)


class ActionFeasibilityAnalyzer:
    """Evaluates feasibility of action plans across five dimensions."""

    def analyze(
        self,
        plan_id: str = "",
        allocation: ResourceAllocationResult | None = None,
        budget_required: float = 0.0,
        step_count: int = 0,
        correlation_id: str = "",
    ) -> FeasibilityResult:
        """Analyse feasibility of an action plan.

        Uses deterministic placeholder heuristics:
        - Resource: always available (unless >20 personnel requested)
        - Budget: sufficient for up to $100,000
        - Skills: available for up to 10 steps
        - Schedule: feasible for up to 50 steps
        - Dependencies: always satisfiable

        Args:
            plan_id: The plan ID.
            allocation: The resource allocation result.
            budget_required: Required budget.
            step_count: Number of steps.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            FeasibilityResult with per-dimension and overall feasibility.
        """
        allocation = allocation or ResourceAllocationResult(plan_id=plan_id)

        resource_ok = allocation.total_personnel <= 20
        if not resource_ok:
            log.warning("feasibility.resource_unavailable", plan_id=plan_id, personnel=allocation.total_personnel)

        budget_ok = budget_required <= 100000.0
        if not budget_ok:
            log.warning("feasibility.budget_exceeded", plan_id=plan_id, required=budget_required)

        skills_ok = step_count <= 10
        if not skills_ok:
            log.warning("feasibility.skills_unavailable", plan_id=plan_id, steps=step_count)

        schedule_ok = step_count <= 50
        if not schedule_ok:
            log.warning("feasibility.schedule_infeasible", plan_id=plan_id, steps=step_count)

        deps_ok = True

        issues: list[str] = []
        if not resource_ok:
            issues.append("Required personnel exceed available capacity (20)")
        if not budget_ok:
            issues.append(f"Required budget ${budget_required:.2f} exceeds limit ($100,000)")
        if not skills_ok:
            issues.append(f"Required skills for {step_count} steps exceed available expertise")
        if not schedule_ok:
            issues.append(f"Schedule with {step_count} steps exceeds planning horizon")
        if not deps_ok:
            issues.append("Unsatisfiable dependencies detected")

        is_feasible = all([resource_ok, budget_ok, skills_ok, schedule_ok, deps_ok])

        result = FeasibilityResult(
            plan_id=plan_id,
            resource_available=resource_ok,
            budget_available=budget_ok,
            skills_available=skills_ok,
            schedule_feasible=schedule_ok,
            dependencies_satisfied=deps_ok,
            is_feasible=is_feasible,
            issues=issues,
        )
        log.info(
            "feasibility.analyzed",
            plan_id=plan_id,
            is_feasible=is_feasible,
            issues=len(issues),
            correlation_id=correlation_id,
        )
        return result
