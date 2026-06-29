"""Execution strategies for task scheduling.

Each strategy determines how tasks are grouped into execution waves.
The ``TaskScheduler`` delegates to a strategy to produce a schedule.

Strategy Pattern:
    ``ExecutionStrategy`` (interface)
    ├── ``SequentialStrategy`` — one task per wave
    ├── ``ParallelStrategy`` — all available tasks per wave (placeholder)
    ├── ``ConditionalStrategy`` — respects conditional gates (placeholder)
    └── ``EmergencyStrategy`` — high-priority override (placeholder)
"""

from __future__ import annotations

import abc
from uuid import UUID

from adip.workflow.contracts.models import WorkflowGraph


class ExecutionStrategy(abc.ABC):
    """Determines the shape of an execution schedule.

    A schedule is a list of execution *waves*, where each wave is a list
    of task IDs that may be executed together (sequentially or in
    parallel, depending on the strategy).
    """

    @abc.abstractmethod
    async def create_schedule(
        self, graph: WorkflowGraph,
    ) -> list[list[UUID]]:
        """Produce a schedule from the given workflow graph.

        Returns a list of execution waves (list of task-ID lists).
        """
        ...


class SequentialStrategy(ExecutionStrategy):
    """Execute one task at a time in dependency order.

    Each execution wave contains exactly one task.  Tasks are emitted
    in topological order with respect to the graph.
    """

    async def create_schedule(
        self, graph: WorkflowGraph,
    ) -> list[list[UUID]]:
        topo = graph.topological_sort()
        return [[t.task_id] for t in topo]


class ParallelStrategy(ExecutionStrategy):
    """Execute all available (ready) tasks within the same wave.

    Future implementation: groups all tasks whose dependencies are
    satisfied into a single wave, maximising concurrency.

    Currently returns the topological execution levels as waves.
    """

    async def create_schedule(
        self, graph: WorkflowGraph,
    ) -> list[list[UUID]]:
        return graph.get_execution_levels()


class ConditionalStrategy(ExecutionStrategy):
    """Execute tasks based on conditional gates (placeholder).

    Future implementation: only includes tasks in a wave if their
    preconditions evaluate to True.
    """

    async def create_schedule(
        self, graph: WorkflowGraph,
    ) -> list[list[UUID]]:
        # Placeholder: same as Sequential
        topo = graph.topological_sort()
        return [[t.task_id] for t in topo]


class EmergencyStrategy(ExecutionStrategy):
    """High-priority override — execute critical-path tasks first.

    Future implementation: identifies the critical path and executes
    only those tasks, skipping non-critical ones.
    """

    async def create_schedule(
        self, graph: WorkflowGraph,
    ) -> list[list[UUID]]:
        critical = graph.get_critical_path()
        return [[t.task_id] for t in critical]
