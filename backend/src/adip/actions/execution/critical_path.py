"""CriticalPathAnalyzer — critical path, duration and bottleneck analysis.

Analyses the action dependency graph to find the critical path
(longest path through the DAG), calculate total project duration,
and identify bottleneck steps that impact the overall timeline.
"""

from __future__ import annotations

import structlog

from adip.actions.execution.models import ActionGraph, CriticalPath

log = structlog.get_logger(__name__)


class CriticalPathAnalyzer:
    """Calculates critical path, total duration, and bottlenecks."""

    def analyze(
        self,
        graph: ActionGraph,
        correlation_id: str = "",
    ) -> CriticalPath:
        """Analyse the critical path of an action dependency graph.

        Uses forward and backward pass to find the longest path.

        Args:
            graph: The action dependency graph.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            CriticalPath with step IDs, total duration, and bottlenecks.
        """
        if graph.has_cycle or not graph.nodes:
            return CriticalPath(
                plan_id=graph.plan_id,
            )

        node_map = {n.step_id: n for n in graph.nodes}
        adj: dict[str, list[str]] = {n.step_id: [] for n in graph.nodes}
        in_edges: dict[str, list[str]] = {n.step_id: [] for n in graph.nodes}
        for edge in graph.edges:
            if edge.source_node_id in adj:
                adj[edge.source_node_id].append(edge.target_node_id)
            if edge.target_node_id in in_edges:
                in_edges[edge.target_node_id].append(edge.source_node_id)

        topo_order = graph.topological_order or list(node_map.keys())

        # Forward pass — earliest start times
        earliest_start: dict[str, int] = {sid: 0 for sid in node_map}
        for sid in topo_order:
            node = node_map.get(sid)
            duration = node.duration_minutes if node else 0
            for neighbor in adj.get(sid, []):
                earliest_start[neighbor] = max(
                    earliest_start[neighbor],
                    earliest_start[sid] + duration,
                )

        total_duration = 0
        for sid in node_map:
            node = node_map.get(sid)
            duration = node.duration_minutes if node else 0
            completion = earliest_start[sid] + duration
            total_duration = max(total_duration, completion)

        # Backward pass — latest start times
        latest_start: dict[str, int] = {
            sid: total_duration - (node_map[sid].duration_minutes if node_map.get(sid) else 0)
            for sid in node_map
        }
        for sid in reversed(topo_order):
            node = node_map.get(sid)
            duration = node.duration_minutes if node else 0
            for neighbor in adj.get(sid, []):
                latest_start[sid] = min(
                    latest_start[sid],
                    latest_start.get(neighbor, total_duration) - duration,
                )

        # Identify critical path steps (zero float)
        critical_step_ids: list[str] = []
        bottleneck_step_ids: list[str] = []
        for sid in node_map:
            if earliest_start[sid] == latest_start[sid]:
                critical_step_ids.append(sid)
            node = node_map.get(sid)
            if node and node.duration_minutes >= 60:
                bottleneck_step_ids.append(sid)

        path = CriticalPath(
            plan_id=graph.plan_id,
            step_ids=critical_step_ids,
            total_duration_minutes=total_duration,
            bottleneck_step_ids=bottleneck_step_ids,
        )
        log.info(
            "critical_path.analyzed",
            plan_id=graph.plan_id,
            total_duration=total_duration,
            critical_steps=len(critical_step_ids),
            bottlenecks=len(bottleneck_step_ids),
            correlation_id=correlation_id,
        )
        return path
