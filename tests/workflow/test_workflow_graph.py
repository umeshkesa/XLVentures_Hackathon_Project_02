"""Validation tests for WorkflowGraph."""

from __future__ import annotations

import uuid

import pytest

from adip.workflow.contracts.models import WorkflowGraph, WorkflowTask


@pytest.fixture
def linear_tasks() -> list[WorkflowTask]:
    t1 = WorkflowTask(task_id=uuid.uuid4(), task_name="A")
    t2 = WorkflowTask(task_id=uuid.uuid4(), task_name="B", dependencies=[t1.task_id])
    t3 = WorkflowTask(task_id=uuid.uuid4(), task_name="C", dependencies=[t2.task_id])
    return [t1, t2, t3]


@pytest.fixture
def diamond_tasks() -> list[WorkflowTask]:
    t1 = WorkflowTask(task_id=uuid.uuid4(), task_name="Root")
    t2 = WorkflowTask(task_id=uuid.uuid4(), task_name="Left", dependencies=[t1.task_id])
    t3 = WorkflowTask(task_id=uuid.uuid4(), task_name="Right", dependencies=[t1.task_id])
    t4 = WorkflowTask(
        task_id=uuid.uuid4(), task_name="Merge",
        dependencies=[t2.task_id, t3.task_id],
    )
    return [t1, t2, t3, t4]


@pytest.fixture
def cyclic_tasks() -> list[WorkflowTask]:
    t1 = WorkflowTask(task_id=uuid.uuid4(), task_name="A")
    t2 = WorkflowTask(task_id=uuid.uuid4(), task_name="B", dependencies=[t1.task_id])
    t3 = WorkflowTask(task_id=uuid.uuid4(), task_name="C", dependencies=[t2.task_id])
    t1.dependencies = [t3.task_id]
    return [t1, t2, t3]


@pytest.fixture
def parallel_tasks() -> list[WorkflowTask]:
    t1 = WorkflowTask(task_id=uuid.uuid4(), task_name="Root")
    t2 = WorkflowTask(task_id=uuid.uuid4(), task_name="A", dependencies=[t1.task_id])
    t3 = WorkflowTask(task_id=uuid.uuid4(), task_name="B", dependencies=[t1.task_id])
    t4 = WorkflowTask(task_id=uuid.uuid4(), task_name="C", dependencies=[t1.task_id])
    return [t1, t2, t3, t4]


class TestWorkflowGraphConstruction:
    def test_from_tasks(self, linear_tasks: list[WorkflowTask]) -> None:
        graph = WorkflowGraph.from_workflow_tasks(linear_tasks)
        assert len(graph.nodes) == 3
        assert len(graph.edges) == 3
        for t in linear_tasks:
            assert t.task_id in graph.nodes

    def test_add_node(self) -> None:
        graph = WorkflowGraph()
        t = WorkflowTask(task_id=uuid.uuid4(), task_name="New")
        graph.add_node(t)
        assert t.task_id in graph.nodes
        assert graph.edges[t.task_id] == []

    def test_add_edge(self) -> None:
        t1 = WorkflowTask(task_id=uuid.uuid4(), task_name="A")
        t2 = WorkflowTask(task_id=uuid.uuid4(), task_name="B")
        graph = WorkflowGraph()
        graph.add_node(t1)
        graph.add_node(t2)
        graph.add_edge(t2.task_id, t1.task_id)
        assert t1.task_id in graph.edges[t2.task_id]

    def test_empty_graph(self) -> None:
        graph = WorkflowGraph()
        assert graph.nodes == {}
        assert graph.edges == {}


class TestWorkflowGraphRootsLeaves:
    def test_root_nodes(self, linear_tasks: list[WorkflowTask]) -> None:
        graph = WorkflowGraph.from_workflow_tasks(linear_tasks)
        roots = graph.get_root_nodes()
        assert len(roots) == 1
        assert roots[0].task_id == linear_tasks[0].task_id

    def test_leaf_nodes(self, linear_tasks: list[WorkflowTask]) -> None:
        graph = WorkflowGraph.from_workflow_tasks(linear_tasks)
        leaves = graph.get_leaf_nodes()
        assert len(leaves) == 1
        assert leaves[0].task_id == linear_tasks[2].task_id

    def test_multiple_leaves(self) -> None:
        t1 = WorkflowTask(task_id=uuid.uuid4(), task_name="Root")
        t2 = WorkflowTask(task_id=uuid.uuid4(), task_name="A", dependencies=[t1.task_id])
        t3 = WorkflowTask(task_id=uuid.uuid4(), task_name="B", dependencies=[t1.task_id])
        graph = WorkflowGraph.from_workflow_tasks([t1, t2, t3])
        leaves = graph.get_leaf_nodes()
        assert len(leaves) == 2


class TestWorkflowGraphTopologicalSort:
    def test_linear_order(self, linear_tasks: list[WorkflowTask]) -> None:
        graph = WorkflowGraph.from_workflow_tasks(linear_tasks)
        order = graph.topological_sort()
        ids = [t.task_id for t in order]
        assert ids[0] == linear_tasks[0].task_id
        assert ids[-1] == linear_tasks[-1].task_id

    def test_diamond_order(self, diamond_tasks: list[WorkflowTask]) -> None:
        graph = WorkflowGraph.from_workflow_tasks(diamond_tasks)
        order = graph.topological_sort()
        ids = [t.task_id for t in order]
        assert ids[0] == diamond_tasks[0].task_id  # Root first
        assert ids[-1] == diamond_tasks[-1].task_id  # Merge last

    def test_no_dependencies(self) -> None:
        t1 = WorkflowTask(task_id=uuid.uuid4(), task_name="A")
        t2 = WorkflowTask(task_id=uuid.uuid4(), task_name="B")
        graph = WorkflowGraph.from_workflow_tasks([t1, t2])
        assert len(graph.topological_sort()) == 2


class TestWorkflowGraphExecutionLevels:
    def test_linear_levels(self, linear_tasks: list[WorkflowTask]) -> None:
        graph = WorkflowGraph.from_workflow_tasks(linear_tasks)
        levels = graph.get_execution_levels()
        assert len(levels) == 3  # A, B, C each in their own level
        assert len(levels[0]) == 1  # A alone

    def test_diamond_levels(self, diamond_tasks: list[WorkflowTask]) -> None:
        graph = WorkflowGraph.from_workflow_tasks(diamond_tasks)
        levels = graph.get_execution_levels()
        assert len(levels) >= 2
        # Level 0: Root, Level 1: Left+Right (parallel), Level 2: Merge
        for level in levels:
            assert len(level) >= 1

    def test_parallel_levels(self, parallel_tasks: list[WorkflowTask]) -> None:
        graph = WorkflowGraph.from_workflow_tasks(parallel_tasks)
        levels = graph.get_execution_levels()
        assert len(levels) == 2
        assert len(levels[1]) == 3  # A, B, C share level 1


class TestWorkflowGraphParallelGroups:
    def test_groups_detected(self, parallel_tasks: list[WorkflowTask]) -> None:
        graph = WorkflowGraph.from_workflow_tasks(parallel_tasks)
        groups = graph.get_parallel_groups()
        assert len(groups) == 1
        assert len(groups[0]) == 3

    def test_no_parallel_groups(self, linear_tasks: list[WorkflowTask]) -> None:
        graph = WorkflowGraph.from_workflow_tasks(linear_tasks)
        assert graph.get_parallel_groups() == []


class TestWorkflowGraphCycleDetection:
    def test_no_cycle(self, linear_tasks: list[WorkflowTask]) -> None:
        graph = WorkflowGraph.from_workflow_tasks(linear_tasks)
        assert graph.detect_cycles() == []

    def test_detects_cycle(self, cyclic_tasks: list[WorkflowTask]) -> None:
        graph = WorkflowGraph.from_workflow_tasks(cyclic_tasks)
        cycles = graph.detect_cycles()
        assert len(cycles) >= 1
