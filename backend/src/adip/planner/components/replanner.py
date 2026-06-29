"""Deterministic Replanner implementation."""

from __future__ import annotations

from datetime import UTC, datetime

from adip.planner.contracts.models import ExecutionPlan, PlanningContext, PlanningGoal
from adip.planner.enums import TaskStatusEnum
from adip.planner.interfaces.pipeline import Replanner


class DeterministicReplanner(Replanner):
    """Placeholder replanner.

    When a deviation is detected:
      1. Marks all incomplete (PENDING / IN_PROGRESS) tasks as FAILED.
      2. Returns a new plan containing only the remaining unstarted tasks
         (those still PENDING) with their original dependencies preserved.
    Returns ``None`` when there are no remaining tasks to replan.
    """

    async def replan(
        self,
        original_plan: ExecutionPlan,
        current_context: PlanningContext,
        deviation_reason: str,
        goal: PlanningGoal,
    ) -> ExecutionPlan | None:
        """Replan based on a deviation description."""
        import uuid

        pending_tasks = [
            t
            for t in original_plan.tasks
            if t.status
            in (TaskStatusEnum.PENDING, TaskStatusEnum.IN_PROGRESS)
        ]

        if not pending_tasks:
            return None

        id_map: dict = {}
        new_tasks = []
        for t in pending_tasks:
            new_id = uuid.uuid4()
            id_map[t.task_id] = new_id
            new_tasks.append(
                t.model_copy(
                    update={
                        "task_id": new_id,
                        "status": TaskStatusEnum.PENDING,
                    }
                )
            )

        for t in new_tasks:
            t.dependencies = [id_map[d] for d in t.dependencies if d in id_map]

        return ExecutionPlan(
            plan_id=uuid.uuid4(),
            parent_plan_id=original_plan.plan_id,
            goal=goal or original_plan.goal,
            tasks=new_tasks,
            planning_timestamp=datetime.now(UTC),
            version=_bump_version(original_plan.version),
        )


def _bump_version(v: str) -> str:
    parts = v.split(".")
    try:
        parts[-1] = str(int(parts[-1]) + 1)
    except (ValueError, IndexError):
        return "1.0.0"
    return ".".join(parts)
