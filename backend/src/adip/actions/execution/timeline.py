"""ExecutionTimeline — chronological execution timeline generator.

Generates a chronological timeline of action plan execution,
ordering steps by their dependency-based sequence, parallel
group membership, and estimated durations.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import structlog

from adip.actions.execution.models import ActionGraph, CriticalPath, ParallelGroup, TimelineEntry

log = structlog.get_logger(__name__)


class ExecutionTimeline:
    """Generates chronological execution timelines for action plans."""

    def generate(
        self,
        plan_id: str = "",
        graph: ActionGraph | None = None,
        parallel_groups: list[ParallelGroup] | None = None,
        critical_path: CriticalPath | None = None,
        start_time: datetime | None = None,
        correlation_id: str = "",
    ) -> list[TimelineEntry]:
        """Generate a chronological execution timeline.

        Steps are ordered by parallel group level, with each
        step's time bounds calculated based on cumulative group
        durations.

        Args:
            plan_id: The plan ID.
            graph: The action dependency graph (optional, for node metadata).
            parallel_groups: The parallel groups to timeline.
            critical_path: The critical path analysis result.
            start_time: Optional start time (defaults to now).
            correlation_id: Optional correlation ID for tracing.

        Returns:
            List of TimelineEntry in chronological order.
        """
        graph = graph or ActionGraph(plan_id=plan_id)
        parallel_groups = parallel_groups or []
        critical_path = critical_path or CriticalPath(plan_id=plan_id)
        start = start_time or datetime.now(UTC)

        node_map = {n.step_id: n for n in graph.nodes}
        critical_ids = set(critical_path.step_ids)

        timeline: list[TimelineEntry] = []
        current_time = start
        sequence = 0

        for group in parallel_groups:
            group_start = current_time
            for sid in group.step_ids:
                node = node_map.get(sid)
                duration = node.duration_minutes if node else 30
                step_start = group_start
                step_end = step_start + timedelta(minutes=duration)

                timeline.append(
                    TimelineEntry(
                        plan_id=plan_id,
                        step_id=sid,
                        step_name=node.name if node else f"Step {sid[:8]}",
                        sequence=sequence,
                        parallel_group=group.level,
                        estimated_start=step_start,
                        estimated_end=step_end,
                        duration_minutes=duration,
                        is_critical=sid in critical_ids,
                    )
                )
                sequence += 1

            # Advance to next group
            max_duration = group.estimated_duration_minutes
            current_time += timedelta(minutes=max_duration)

        log.info(
            "execution_timeline.generated",
            plan_id=plan_id,
            entry_count=len(timeline),
            start_time=start.isoformat(),
            correlation_id=correlation_id,
        )
        return timeline

    def get_total_duration_minutes(
        self,
        timeline: list[TimelineEntry],
    ) -> int:
        """Get the total duration of the timeline in minutes."""
        if not timeline:
            return 0
        earliest = min(e.estimated_start for e in timeline)
        latest = max(e.estimated_end for e in timeline)
        return int((latest - earliest).total_seconds() // 60)

    def get_critical_entries(
        self,
        timeline: list[TimelineEntry],
    ) -> list[TimelineEntry]:
        """Filter timeline to critical path entries."""
        return [e for e in timeline if e.is_critical]
