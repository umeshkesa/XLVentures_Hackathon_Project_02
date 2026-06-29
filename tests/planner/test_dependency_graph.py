"""Tests for the DependencyGraph model."""

from __future__ import annotations

import uuid

import pytest

from adip.planner.contracts.models import DependencyGraph, PlanningTask


@pytest.fixture
def linear_tasks() -> list[PlanningTask]:
    t1 = PlanningTask(task_id=uuid.uuid4(), description="A")
    t2 = PlanningTask(task_id=uuid.uuid4(), description="B", dependencies=[t1.task_id])
    t3 = PlanningTask(task_id=uuid.uuid4(), description="C", dependencies=[t2.task_id])
    return [t1, t2, t3]


@pytest.fixture
def diamond_tasks() -> list[PlanningTask]:
    t1 = PlanningTask(task_id=uuid.uuid4(), description="Root")
    t2 = PlanningTask(task_id=uuid.uuid4(), description="Left", dependencies=[t1.task_id])
    t3 = PlanningTask(task_id=uuid.uuid4(), description="Right", dependencies=[t1.task_id])
    t4 = PlanningTask(
        task_id=uuid.uuid4(), description="Merge",
        dependencies=[t2.task_id, t3.task_id],
    )
    return [t1, t2, t3, t4]


@pytest.fixture
def cyclic_tasks() -> list[PlanningTask]:
    t1 = PlanningTask(task_id=uuid.uuid4(), description="A")
    t2 = PlanningTask(task_id=uuid.uuid4(), description="B", dependencies=[t1.task_id])
    t3 = PlanningTask(task_id=uuid.uuid4(), description="C", dependencies=[t2.task_id])
    t1.dependencies = [t3.task_id]  # A -> B -> C -> A
    return [t1, t2, t3]


@pytest.fixture
def parallel_tasks() -> list[PlanningTask]:
    t1 = PlanningTask(task_id=uuid.uuid4(), description="Root")
    t2 = PlanningTask(task_id=uuid.uuid4(), description="A", dependencies=[t1.task_id])
    t3 = PlanningTask(task_id=uuid.uuid4(), description="B", dependencies=[t1.task_id])
    t4 = PlanningTask(task_id=uuid.uuid4(), description="C", dependencies=[t1.task_id])
    return [t1, t2, t3, t4]


class TestDependencyGraphConstruction:
    def test_from_tasks(self, linear_tasks: list[PlanningTask]) -> None:
        graph = DependencyGraph.from_tasks(linear_tasks)
        assert len(graph.nodes) == 3
        assert len(graph.edges) == 3

    def test_add_task(self) -> None:
        graph = DependencyGraph()
        t = PlanningTask(task_id=uuid.uuid4(), description="New")
        graph.add_task(t)
        assert t.task_id in graph.nodes
        assert t.task_id in graph.edges

    def test_empty_graph(self) -> None:
        graph = DependencyGraph()
        assert graph.nodes == {}
        assert graph.edges == {}


class TestDependencyGraphExecutionOrder:
    async def test_linear_order(self, linear_tasks: list[PlanningTask]) -> None:
        graph = DependencyGraph.from_tasks(linear_tasks)
        order = graph.get_execution_order()
        ids = [t.task_id for t in order]
        # Root first, then B, then C
        assert ids[0] == linear_tasks[0].task_id
        assert ids[2] == linear_tasks[2].task_id

    async def test_diamond_order(self, diamond_tasks: list[PlanningTask]) -> None:
        graph = DependencyGraph.from_tasks(diamond_tasks)
        order = graph.get_execution_order()
        ids = [t.task_id for t in order]
        root_id = diamond_tasks[0].task_id
        merge_id = diamond_tasks[3].task_id
        assert ids[0] == root_id
        assert ids[-1] == merge_id  # Merge comes last

    async def test_no_dependencies(self) -> None:
        t1 = PlanningTask(task_id=uuid.uuid4(), description="A")
        t2 = PlanningTask(task_id=uuid.uuid4(), description="B")
        graph = DependencyGraph.from_tasks([t1, t2])
        order = graph.get_execution_order()
        assert len(order) == 2


class TestDependencyGraphCycleDetection:
    async def test_no_cycle(self, linear_tasks: list[PlanningTask]) -> None:
        graph = DependencyGraph.from_tasks(linear_tasks)
        cycles = graph.detect_cycles()
        assert cycles == []

    async def test_detects_cycle(self, cyclic_tasks: list[PlanningTask]) -> None:
        graph = DependencyGraph.from_tasks(cyclic_tasks)
        cycles = graph.detect_cycles()
        assert len(cycles) >= 1
        assert all(len(c) >= 2 for c in cycles)


class TestDependencyGraphRootsAndLeaves:
    async def test_root_tasks(self, linear_tasks: list[PlanningTask]) -> None:
        graph = DependencyGraph.from_tasks(linear_tasks)
        roots = graph.get_root_tasks()
        assert len(roots) == 1
        assert roots[0].task_id == linear_tasks[0].task_id

    async def test_leaf_tasks(self, linear_tasks: list[PlanningTask]) -> None:
        graph = DependencyGraph.from_tasks(linear_tasks)
        leaves = graph.get_leaf_tasks()
        assert len(leaves) == 1
        assert leaves[0].task_id == linear_tasks[2].task_id

    async def test_multiple_roots(self, diamond_tasks: list[PlanningTask]) -> None:
        graph = DependencyGraph.from_tasks(diamond_tasks)
        roots = graph.get_root_tasks()
        assert len(roots) == 1  # Only t1 has no deps

    async def test_multiple_leaves(self) -> None:
        t1 = PlanningTask(task_id=uuid.uuid4(), description="Root")
        t2 = PlanningTask(task_id=uuid.uuid4(), description="A", dependencies=[t1.task_id])
        t3 = PlanningTask(task_id=uuid.uuid4(), description="B", dependencies=[t1.task_id])
        graph = DependencyGraph.from_tasks([t1, t2, t3])
        leaves = graph.get_leaf_tasks()
        assert len(leaves) == 2  # t2 and t3 have no dependents


class TestDependencyGraphParallelGroups:
    async def test_parallel_groups(self, parallel_tasks: list[PlanningTask]) -> None:
        graph = DependencyGraph.from_tasks(parallel_tasks)
        groups = graph.get_parallel_groups()
        # Root has deps=[], A/B/C each have deps=[root] so they share the same set
        assert len(groups) == 1  # one group of 3 tasks
        assert len(groups[0]) == 3

    async def test_no_parallel_groups(self, linear_tasks: list[PlanningTask]) -> None:
        graph = DependencyGraph.from_tasks(linear_tasks)
        groups = graph.get_parallel_groups()
        assert groups == []
