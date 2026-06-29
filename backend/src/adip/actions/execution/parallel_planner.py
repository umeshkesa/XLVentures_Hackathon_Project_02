"""ParallelActionPlanner — identifies executable parallel groups.

Analyses the action dependency graph to identify groups of
steps that can execute in parallel based on their topological
levels and dependency constraints.
"""

from __future__ import annotations

import structlog

from adip.actions.execution.models import ActionGraph, ParallelGroup

log = structlog.get_logger(__name__)


class ParallelActionPlanner:
    """Identifies groups of steps that can execute in parallel."""

    def identify_parallel_groups(
        self,
        graph: ActionGraph,
        correlation_id: str = "",
    ) -> list[ParallelGroup]:
        """Identify parallel execution groups from the graph.

        Steps at the same topological level can execute in parallel
        if they have no interdependencies.

        Args:
            graph: The action dependency graph.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            List of ParallelGroups, one per topological level.
        """
        if graph.has_cycle or not graph.nodes:
            return []

        level_groups: dict[int, list[str]] = {}
        for node in graph.nodes:
            level = node.level
            if level not in level_groups:
                level_groups[level] = []
            level_groups[level].append(node.step_id)

        groups: list[ParallelGroup] = []
        for level in sorted(level_groups.keys()):
            step_ids = level_groups[level]
            max_duration = self._estimate_group_duration(graph, step_ids)
            groups.append(
                ParallelGroup(
                    level=level,
                    step_ids=step_ids,
                    estimated_duration_minutes=max_duration,
                )
            )

        log.info(
            "parallel_planner.groups_identified",
            group_count=len(groups),
            correlation_id=correlation_id,
        )
        return groups

    def _estimate_group_duration(
        self,
        graph: ActionGraph,
        step_ids: list[str],
    ) -> int:
        """Estimate the duration of a parallel group (max of steps)."""
        node_map = {n.step_id: n for n in graph.nodes}
        max_duration = 0
        for sid in step_ids:
            node = node_map.get(sid)
            if node:
                max_duration = max(max_duration, node.duration_minutes)
        return max_duration

    def optimize_parallelism(
        self,
        groups: list[ParallelGroup],
        max_parallel: int = 0,
        correlation_id: str = "",
    ) -> list[ParallelGroup]:
        """Optimize parallel groups to respect max parallelism.

        Args:
            groups: The identified parallel groups.
            max_parallel: Maximum parallel steps per group (0 = unlimited).
            correlation_id: Optional correlation ID for tracing.

        Returns:
            Optimized list of ParallelGroups.
        """
        if max_parallel <= 0:
            return groups

        optimized: list[ParallelGroup] = []
        for group in groups:
            if len(group.step_ids) <= max_parallel:
                optimized.append(group)
            else:
                for i in range(0, len(group.step_ids), max_parallel):
                    chunk = group.step_ids[i : i + max_parallel]
                    optimized.append(
                        ParallelGroup(
                            level=group.level,
                            step_ids=chunk,
                            estimated_duration_minutes=group.estimated_duration_minutes,
                        )
                    )
        log.info(
            "parallel_planner.optimized",
            original_count=len(groups),
            optimized_count=len(optimized),
            max_parallel=max_parallel,
            correlation_id=correlation_id,
        )
        return optimized
