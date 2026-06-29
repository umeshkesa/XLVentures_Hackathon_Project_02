"""ActionGraph — DAG construction and cycle detection.

Builds a Directed Acyclic Graph from action plan steps and
their dependencies, validates the graph structure, detects
cycles, and provides topological ordering.
"""

from __future__ import annotations

from collections import deque
from typing import Any

import structlog

from adip.actions.execution.models import ActionGraph, ActionGraphEdge, ActionGraphNode

log = structlog.get_logger(__name__)


class ActionGraphBuilder:
    """Constructs and validates action dependency DAGs."""

    def build_graph(
        self,
        plan_id: str = "",
        step_ids: list[str] | None = None,
        dependencies: list[tuple[str, str, str]] | None = None,
        correlation_id: str = "",
    ) -> ActionGraph:
        """Build a dependency graph from step IDs and dependencies.

        Args:
            plan_id: The plan ID.
            step_ids: List of step IDs to include as nodes.
            dependencies: List of (source, target, dep_type) tuples.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            An ActionGraph with nodes, edges, and analysis results.
        """
        step_ids = step_ids or []
        dependencies = dependencies or []

        nodes = [
            ActionGraphNode(
                step_id=sid,
                name=f"Step {sid[:8]}",
                action_type=self._infer_action_type(sid),
            )
            for sid in step_ids
        ]

        edges = [
            ActionGraphEdge(
                source_node_id=src,
                target_node_id=tgt,
                dependency_type=dep_type or "hard",
            )
            for src, tgt, dep_type in dependencies
        ]

        has_cycle, _ = self._detect_cycle(step_ids, dependencies)
        topo_order = self._topological_sort(step_ids, dependencies) if not has_cycle else []
        levels = self._assign_levels(step_ids, dependencies) if not has_cycle else {}

        for node in nodes:
            node.level = levels.get(node.step_id, 0)

        graph = ActionGraph(
            plan_id=plan_id,
            nodes=nodes,
            edges=edges,
            has_cycle=has_cycle,
            is_dag=not has_cycle,
            topological_order=topo_order,
        )
        log.info(
            "action_graph.built",
            plan_id=plan_id,
            node_count=len(nodes),
            edge_count=len(edges),
            has_cycle=has_cycle,
            correlation_id=correlation_id,
        )
        return graph

    def _detect_cycle(
        self,
        step_ids: list[str],
        dependencies: list[tuple[str, str, str]],
    ) -> tuple[bool, list[str]]:
        """Detect cycles in the dependency graph using DFS."""
        adj: dict[str, list[str]] = {sid: [] for sid in step_ids}
        for src, tgt, _ in dependencies:
            if src in adj and tgt in adj:
                adj[src].append(tgt)

        WHITE, GRAY, BLACK = 0, 1, 2
        color: dict[str, int] = {sid: WHITE for sid in step_ids}
        cycle_path: list[str] = []

        def dfs(u: str) -> bool:
            color[u] = GRAY
            cycle_path.append(u)
            for v in adj.get(u, []):
                if color.get(v) == GRAY:
                    cycle_path.append(v)
                    return True
                if color.get(v) == WHITE and dfs(v):
                    return True
            cycle_path.pop()
            color[u] = BLACK
            return False

        for sid in step_ids:
            if color.get(sid) == WHITE:
                if dfs(sid):
                    return True, cycle_path
        return False, []

    def _topological_sort(
        self,
        step_ids: list[str],
        dependencies: list[tuple[str, str, str]],
    ) -> list[str]:
        """Return topologically sorted step IDs using Kahn's algorithm."""
        in_degree: dict[str, int] = {sid: 0 for sid in step_ids}
        adj: dict[str, list[str]] = {sid: [] for sid in step_ids}
        for src, tgt, _ in dependencies:
            if src in adj and tgt in adj:
                adj[src].append(tgt)
                in_degree[tgt] = in_degree.get(tgt, 0) + 1

        queue = deque([sid for sid in step_ids if in_degree.get(sid, 0) == 0])
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
        step_ids: list[str],
        dependencies: list[tuple[str, str, str]],
    ) -> dict[str, int]:
        """Assign topological levels to each node."""
        in_degree: dict[str, int] = {sid: 0 for sid in step_ids}
        adj: dict[str, list[str]] = {sid: [] for sid in step_ids}
        for src, tgt, _ in dependencies:
            if src in adj and tgt in adj:
                adj[src].append(tgt)
                in_degree[tgt] = in_degree.get(tgt, 0) + 1

        levels: dict[str, int] = {}
        queue = deque([sid for sid in step_ids if in_degree.get(sid, 0) == 0])
        for sid in queue:
            levels[sid] = 0

        while queue:
            node = queue.popleft()
            for neighbor in adj.get(node, []):
                levels[neighbor] = max(levels.get(neighbor, 0), levels.get(node, 0) + 1)
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        return levels

    def _infer_action_type(self, step_id: str) -> Any:
        """Infer a placeholder action type from step ID."""
        from adip.actions.enums import ActionType
        return ActionType.AUTOMATED

    def get_dependencies(
        self,
        plan_id: str = "",
        step_ids: list[str] | None = None,
        correlation_id: str = "",
    ) -> list[tuple[str, str, str]]:
        """Extract dependency tuples from step data.

        Returns:
            List of (source_step_id, target_step_id, dependency_type).
        """
        _ = plan_id, step_ids, correlation_id
        return []

    def validate_graph(self, graph: ActionGraph) -> list[str]:
        """Validate a constructed graph.

        Returns:
            List of validation violations (empty if valid).
        """
        violations: list[str] = []
        if not graph.nodes:
            violations.append("Graph must have at least one node")
        node_ids = {n.step_id for n in graph.nodes}
        for edge in graph.edges:
            if edge.source_node_id not in node_ids:
                violations.append(f"Edge source {edge.source_node_id} not found in nodes")
            if edge.target_node_id not in node_ids:
                violations.append(f"Edge target {edge.target_node_id} not found in nodes")
        if graph.has_cycle:
            violations.append("Graph contains a cycle")
        return violations
