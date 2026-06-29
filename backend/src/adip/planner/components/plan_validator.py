"""Deterministic PlanValidator implementation."""

from __future__ import annotations

from adip.planner.contracts.models import ExecutionPlan, PlanningContext, ValidationResult
from adip.planner.enums import TaskStatusEnum
from adip.planner.interfaces.pipeline import PlanValidator


class DeterministicPlanValidator(PlanValidator):
    """Placeholder plan validator.

    Checks:
      - Plan has at least one task.
      - No task references a missing dependency.
      - Every task has a non-empty description.
    """

    async def validate(
        self, plan: ExecutionPlan, context: PlanningContext
    ) -> ValidationResult:
        """Validate the execution plan."""
        errors: list[str] = []
        warnings: list[str] = []

        if not plan.tasks:
            errors.append("Plan must contain at least one task.")

        task_ids = {t.task_id for t in plan.tasks}

        for task in plan.tasks:
            if not task.description.strip():
                errors.append(f"Task {task.task_id} has an empty description.")

            for dep_id in task.dependencies:
                if dep_id not in task_ids:
                    errors.append(
                        f"Task {task.task_id} references missing dependency {dep_id}."
                    )

            if task.status == TaskStatusEnum.PENDING and task.description.strip():
                warnings.append(
                    f"Task {task.task_id} is PENDING with no blockers."
                )

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
        )
