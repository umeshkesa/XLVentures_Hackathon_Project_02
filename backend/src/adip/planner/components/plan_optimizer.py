"""Deterministic PlanOptimizer implementation."""

from __future__ import annotations

from adip.planner.contracts.models import ExecutionPlan, PlanningContext, PlanningGoal
from adip.planner.interfaces.pipeline import PlanOptimizer


class DeterministicPlanOptimizer(PlanOptimizer):
    """Placeholder plan optimizer.

    Applies basic optimisations:
      - Removes redundant dependency chains (A→B→C where A→C is implied).
      - Marks tasks that can run in parallel (same dependency set) with a
        note in a companion structure (future work).
    """

    async def optimize(
        self,
        plan: ExecutionPlan,
        context: PlanningContext,
        goal: PlanningGoal,
    ) -> ExecutionPlan:
        """Optimize the execution plan by pruning transitive dependencies."""
        task_map = {t.task_id: t for t in plan.tasks}

        for task in plan.tasks:
            direct_deps = list(task.dependencies)
            to_remove: set = set()
            for i, dep_id in enumerate(direct_deps):
                # Check whether *any other* direct dependency transitively
                # depends on *dep_id*.  If so, *dep_id* is redundant.
                for j, other_id in enumerate(direct_deps):
                    if i == j:
                        continue
                    other_task = task_map.get(other_id)
                    if other_task and dep_id in other_task.dependencies:
                        to_remove.add(dep_id)
                        break
            if to_remove:
                task.dependencies = [
                    d for d in task.dependencies if d not in to_remove
                ]

        return plan
