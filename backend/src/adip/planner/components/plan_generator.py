"""Deterministic PlanGenerator implementation."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from adip.planner.contracts.models import (
    ExecutionPlan,
    PlanningContext,
    PlanningGoal,
    PlanningTask,
)
from adip.planner.interfaces.pipeline import PlanGenerator


class DeterministicPlanGenerator(PlanGenerator):
    """Placeholder plan generator.

    Creates an :class:`ExecutionPlan` from the provided tasks, ordering
    them by dependency chain.  Tasks with no unresolved dependencies
    appear first.
    """

    async def generate(
        self,
        tasks: list[PlanningTask],
        context: PlanningContext,
        goal: PlanningGoal,
    ) -> ExecutionPlan:
        """Generate an execution plan with topological ordering."""
        dep_map: dict[uuid.UUID, set[uuid.UUID]] = {}
        for t in tasks:
            dep_map[t.task_id] = set(t.dependencies)

        ordered: list[PlanningTask] = []
        ready = [t for t in tasks if not dep_map[t.task_id]]

        while ready:
            task = ready.pop(0)
            ordered.append(task)
            for other in tasks:
                if task.task_id in dep_map[other.task_id]:
                    dep_map[other.task_id].discard(task.task_id)
                    if not dep_map[other.task_id]:
                        ready.append(other)

        return ExecutionPlan(
            plan_id=uuid.uuid4(),
            goal=goal,
            tasks=ordered if ordered else tasks,
            planning_timestamp=datetime.now(UTC),
        )
