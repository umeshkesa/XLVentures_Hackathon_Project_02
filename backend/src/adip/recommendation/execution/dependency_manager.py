"""DependencyManager — manages recommendation dependencies.

Builds and manages dependency graphs between recommendations
to determine execution order and identify blocking issues.
Deterministic placeholder implementation.
"""

from __future__ import annotations

import structlog

from adip.recommendation.execution.models import DependencyGraph, DependencyNode

log = structlog.get_logger(__name__)


class DependencyManager:
    """Manages dependencies between recommendation candidates.

    Deterministic placeholder that builds dependency graphs,
    determines execution order, and identifies blockers.
    """

    def __init__(self) -> None:
        self._graphs: dict[str, DependencyGraph] = {}

    def build_graph(
        self,
        recommendation_ids: list[str],
        blocking_map: dict[str, list[str]] | None = None,
        optional_map: dict[str, list[str]] | None = None,
    ) -> DependencyGraph:
        """Build a dependency graph for recommendations.

        Args:
            recommendation_ids: List of recommendation IDs to include.
            blocking_map: Map of recommendation_id -> list of blocking recommendations.
            optional_map: Map of recommendation_id -> list of optional dependencies.

        Returns:
            DependencyGraph with nodes and execution order.
        """
        blocking_map = blocking_map or {}
        optional_map = optional_map or {}
        nodes: list[DependencyNode] = []
        all_deps: set[str] = set()

        for rid in recommendation_ids:
            blocking = blocking_map.get(rid, [])
            optional = optional_map.get(rid, [])
            merged_deps = list(set(blocking + optional))
            is_blocked = any(d in recommendation_ids and d != rid for d in merged_deps)
            node = DependencyNode(
                recommendation_id=rid,
                description=f"Recommendation {rid[:8]}...",
                blocking_dependencies=blocking,
                optional_dependencies=optional,
                depends_on=merged_deps,
                is_blocked=is_blocked,
            )
            nodes.append(node)
            all_deps.update(merged_deps)

        execution_order, has_cycles = self._compute_execution_order(nodes)

        graph = DependencyGraph(
            nodes=nodes,
            execution_order=execution_order,
            has_cycles=has_cycles,
        )
        self._graphs[graph.graph_id] = graph
        log.info("dependency.build_graph", node_count=len(nodes), has_cycles=has_cycles)
        return graph

    def _compute_execution_order(self, nodes: list[DependencyNode]) -> tuple[list[str], bool]:
        """Compute topological execution order (simple placeholder).

        Returns:
            Tuple of (execution_order, has_cycles).
        """
        order: list[str] = []
        visited: set[str] = set()
        remaining = {n.recommendation_id: n for n in nodes}
        cycled = False
        while remaining:
            found = False
            for rid, node in list(remaining.items()):
                deps = node.depends_on
                if all(d in visited or d not in remaining for d in deps):
                    order.append(rid)
                    visited.add(rid)
                    del remaining[rid]
                    found = True
                    break
            if not found:
                cycled = True
                break
        order.extend(remaining.keys())
        return order, cycled

    def get_graph(self, graph_id: str) -> DependencyGraph | None:
        """Get a dependency graph by ID.

        Args:
            graph_id: The graph identifier.

        Returns:
            DependencyGraph if found, None otherwise.
        """
        return self._graphs.get(graph_id)

    def clear(self) -> None:
        """Clear all graphs."""
        self._graphs.clear()

    def count(self) -> int:
        """Get the number of graphs.

        Returns:
            Graph count.
        """
        return len(self._graphs)
