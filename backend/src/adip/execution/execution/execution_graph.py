"""ExecutionGraph — DAG construction, cycle detection, and parallel grouping.

Builds a Directed Acyclic Graph from execution tasks and their
dependencies, validates the graph structure, detects cycles,
and provides topological ordering and parallel group assignment.
"""

from __future__ import annotations

from collections import deque

import structlog

from adip.execution.execution.models import (
    ExecutionGraph as ExecutionGraphModel,
)
from adip.execution.execution.models import (
    ExecutionGraphEdge,
    ExecutionGraphNode,
)

log = structlog.get_logger(__name__)


class ExecutionGraph:
    """Constructs and validates execution dependency DAGs."""

    def build_graph(
        self,
        package_id: str = "",
        task_ids: list[str] | None = None,
        dependencies: list[tuple[str, str, str]] | None = None,
        correlation_id: str = "",
    ) -> ExecutionGraphModel:
        """Build a dependency graph from task IDs and dependencies.

        Args:
            package_id: The execution package ID.
            task_ids: List of task IDs to include as nodes.
            dependencies: List of (source, target, dep_type) tuples.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            An ExecutionGraph with nodes, edges, and analysis results.
        """
        task_ids = task_ids or []
        dependencies = dependencies or []

        nodes = [
            ExecutionGraphNode(
                task_id=tid,
                name=f"Task {tid[:8]}",
                duration_seconds=self._infer_duration(tid),
            )
            for tid in task_ids
        ]

        edges = [
            ExecutionGraphEdge(
                source_node_id=src,
                target_node_id=tgt,
                dependency_type=dep_type or "hard",
            )
            for src, tgt, dep_type in dependencies
        ]

        has_cycle, cycle_path = self._detect_cycle(task_ids, dependencies)
        topo_order = self._topological_sort(task_ids, dependencies) if not has_cycle else []
        levels = self._assign_levels(task_ids, dependencies) if not has_cycle else {}
        p_groups = self._assign_parallel_groups(task_ids, levels) if not has_cycle else []

        for node in nodes:
            node.level = levels.get(node.task_id, 0)
            for gid, g_tasks in enumerate(p_groups):
                if node.task_id in g_tasks:
                    node.parallel_group = gid
                    break

        graph = ExecutionGraphModel(
            package_id=package_id,
            nodes=nodes,
            edges=edges,
            has_cycle=has_cycle,
            is_dag=not has_cycle,
            topological_order=topo_order,
            parallel_groups=p_groups,
        )
        log.info(
            "execution_graph.built",
            package_id=package_id,
            node_count=len(nodes),
            edge_count=len(edges),
            has_cycle=has_cycle,
            correlation_id=correlation_id,
        )
        return graph

    def validate_graph(
        self,
        graph: ExecutionGraphModel,
        correlation_id: str = "",
    ) -> list[str]:
        """Validate a built execution graph.

        Args:
            graph: The graph to validate.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            List of validation violations (empty if valid).
        """
        issues: list[str] = []
        if graph.has_cycle:
            issues.append("Graph contains a cycle")
        if not graph.is_dag:
            issues.append("Graph is not a valid DAG")
        if not graph.topological_order and not graph.has_cycle:
            issues.append("Topological order is empty")
        if not graph.nodes:
            issues.append("Graph has no nodes")
        node_ids = {n.task_id for n in graph.nodes}
        for edge in graph.edges:
            if edge.source_node_id not in node_ids:
                issues.append(f"Edge references unknown source node: {edge.source_node_id}")
            if edge.target_node_id not in node_ids:
                issues.append(f"Edge references unknown target node: {edge.target_node_id}")
        log.info(
            "execution_graph.validated",
            graph_id=str(graph.graph_id),
            valid=len(issues) == 0,
            issues=len(issues),
            correlation_id=correlation_id,
        )
        return issues

    def get_ready_tasks(
        self,
        graph: ExecutionGraphModel,
        completed_ids: set[str],
        correlation_id: str = "",
    ) -> list[str]:
        """Get tasks that are ready to execute (dependencies satisfied).

        Args:
            graph: The execution graph.
            completed_ids: Set of completed task IDs.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            List of task IDs that are ready to execute.
        """
        ready: list[str] = []
        for node in graph.nodes:
            if node.task_id in completed_ids:
                continue
            deps = [
                e.source_node_id
                for e in graph.edges
                if e.target_node_id == node.task_id
            ]
            if all(d in completed_ids for d in deps):
                ready.append(node.task_id)
        log.info(
            "execution_graph.ready_tasks",
            count=len(ready),
            correlation_id=correlation_id,
        )
        return ready

    def _infer_duration(self, task_id: str) -> int:
        """Infer a deterministic placeholder duration based on task_id hash."""
        return 30 + (hash(task_id) % 120)

    def _detect_cycle(
        self,
        task_ids: list[str],
        dependencies: list[tuple[str, str, str]],
    ) -> tuple[bool, list[str]]:
        """Detect cycles using DFS."""
        adj: dict[str, list[str]] = {tid: [] for tid in task_ids}
        for src, tgt, _ in dependencies:
            if src in adj:
                adj[src].append(tgt)

        visited: set[str] = set()
        rec_stack: set[str] = set()
        parent: dict[str, str | None] = {}

        def dfs(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)
            for neighbor in adj.get(node, []):
                if neighbor not in visited:
                    parent[neighbor] = node
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    cycle: list[str] = [neighbor, node]
                    curr = node
                    while curr is not None and curr != neighbor:
                        cycle.append(curr)
                        curr = parent.get(curr)
                    cycle.reverse()
                    return True
            rec_stack.discard(node)
            return False

        for tid in task_ids:
            if tid not in visited:
                if dfs(tid):
                    return True, list(rec_stack)
        return False, []

    def _topological_sort(
        self,
        task_ids: list[str],
        dependencies: list[tuple[str, str, str]],
    ) -> list[str]:
        """Kahn's algorithm for topological ordering."""
        in_degree: dict[str, int] = {tid: 0 for tid in task_ids}
        adj: dict[str, list[str]] = {tid: [] for tid in task_ids}
        for src, tgt, _ in dependencies:
            if src in adj and tgt in in_degree:
                adj[src].append(tgt)
                in_degree[tgt] += 1

        queue = deque([tid for tid, deg in in_degree.items() if deg == 0])
        result: list[str] = []
        while queue:
            node = queue.popleft()
            result.append(node)
            for neighbor in adj.get(node, []):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        return result

    def _assign_levels(
        self,
        task_ids: list[str],
        dependencies: list[tuple[str, str, str]],
    ) -> dict[str, int]:
        """Assign topological levels to each node."""
        adj: dict[str, list[str]] = {tid: [] for tid in task_ids}
        for src, tgt, _ in dependencies:
            if src in adj:
                adj[src].append(tgt)

        levels: dict[str, int] = {}
        order = self._topological_sort(task_ids, dependencies)
        for tid in order:
            max_level = 0
            for src, tgt, _ in dependencies:
                if tgt == tid and src in levels:
                    max_level = max(max_level, levels[src] + 1)
            levels[tid] = max_level
        return levels

    def _assign_parallel_groups(
        self,
        task_ids: list[str],
        levels: dict[str, int],
    ) -> list[list[str]]:
        """Group tasks by level for parallel execution."""
        max_level = max(levels.values()) if levels else 0
        groups: list[list[str]] = [[] for _ in range(max_level + 1)]
        for tid, level in levels.items():
            groups[level].append(tid)
        return [g for g in groups if g]
