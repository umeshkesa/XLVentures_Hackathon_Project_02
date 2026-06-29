"""Deterministic TaskDecomposer implementation."""

from __future__ import annotations

import uuid

from adip.planner.contracts.models import PlanningContext, PlanningGoal, PlanningTask
from adip.planner.enums import TaskStatusEnum
from adip.planner.interfaces.pipeline import TaskDecomposer


class DeterministicTaskDecomposer(TaskDecomposer):
    """Placeholder task decomposer using sentence splitting.

    Splits the goal objective into sentences, wrapping each as a
    :class:`PlanningTask`.  A more sophisticated implementation would
    use an LLM to produce semantically meaningful subtasks.
    """

    async def decompose(
        self, goal: PlanningGoal, context: PlanningContext
    ) -> list[PlanningTask]:
        """Decompose the goal into a list of sentence-level tasks."""
        import re

        sentences = re.split(r"(?<=[.?!])\s+", goal.objective.strip())
        tasks: list[PlanningTask] = []
        previous_id: uuid.UUID | None = None

        for _i, sentence in enumerate(sentences):
            sentence = sentence.strip()
            if not sentence:
                continue
            task = PlanningTask(
                task_id=uuid.uuid4(),
                description=sentence,
                dependencies=[previous_id] if previous_id else [],
                status=TaskStatusEnum.PENDING,
            )
            previous_id = task.task_id
            tasks.append(task)

        return tasks if tasks else [
            PlanningTask(
                task_id=uuid.uuid4(),
                description=goal.objective,
                status=TaskStatusEnum.PENDING,
            )
        ]
