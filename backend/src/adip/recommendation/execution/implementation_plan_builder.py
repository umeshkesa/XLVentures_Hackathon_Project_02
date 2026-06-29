"""ImplementationPlanBuilder — builds implementation plans.

Generates placeholder implementation plans with ordered steps,
required resources, expected duration, and success criteria.
Deterministic placeholder implementation.
"""

from __future__ import annotations

import structlog

from adip.recommendation.execution.models import ImplementationPlan, ImplementationStep

log = structlog.get_logger(__name__)


class ImplementationPlanBuilder:
    """Builds implementation plans for recommendations.

    Deterministic placeholder that creates structured implementation
    plans with ordered steps, resources, duration, and success criteria.
    """

    def build(
        self,
        recommendation_id: str,
        action: str = "",
        step_count: int = 3,
        resources: list[str] | None = None,
    ) -> ImplementationPlan:
        """Build an implementation plan for a recommendation.

        Args:
            recommendation_id: The recommendation to build a plan for.
            action: The recommended action description.
            step_count: Number of implementation steps.
            resources: Optional list of required resources.

        Returns:
            ImplementationPlan with ordered steps.
        """
        resources = resources or ["Personnel", "Equipment", "Materials"]
        steps: list[ImplementationStep] = []
        total_hours = 0

        for i in range(step_count):
            step_hours = (i + 1) * 2
            total_hours += step_hours
            step = ImplementationStep(
                order=i + 1,
                description=f"Step {i + 1}: {action} — phase {i + 1}" if action else f"Step {i + 1}: Implementation phase",
                required_resources=[resources[i % len(resources)]],
                estimated_duration=f"{step_hours}h",
                success_criteria=[f"Criterion {j + 1} for step {i + 1}" for j in range(2)],
            )
            steps.append(step)

        log.info("plan_builder.build", recommendation_id=recommendation_id, steps=len(steps))
        return ImplementationPlan(
            recommendation_id=recommendation_id,
            steps=steps,
            total_duration=f"{total_hours}h",
            required_resources=list(set(resources)),
            success_criteria=[
                "All steps completed successfully",
                "Expected outcomes achieved",
                "No adverse side effects",
            ],
        )

    def build_from_candidate(
        self,
        candidate,
        step_count: int = 3,
    ) -> ImplementationPlan:
        """Build an implementation plan from a candidate.

        Args:
            candidate: The recommendation candidate.
            step_count: Number of implementation steps.

        Returns:
            ImplementationPlan.
        """
        action = getattr(candidate, 'action', '')
        resources = getattr(candidate, 'required_resources', None)
        return self.build(
            recommendation_id=str(getattr(candidate, 'candidate_id', '')),
            action=action,
            step_count=step_count,
            resources=resources,
        )
