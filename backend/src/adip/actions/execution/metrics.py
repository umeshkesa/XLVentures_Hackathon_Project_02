"""ActionMetrics — action planning metrics collection.

Collects operational metrics for the action planning system
including plan counts, task counts, resource allocations,
conflict detection, optimisation scores, and cost tracking.
"""

from __future__ import annotations

import structlog

from adip.actions.execution.models import ActionMetricsSnapshot

log = structlog.get_logger(__name__)


class ActionMetrics:
    """Collects operational metrics for the action planning system."""

    def __init__(self) -> None:
        self._plans_total: int = 0
        self._tasks_total: int = 0
        self._resources_allocated: int = 0
        self._conflicts_detected: int = 0
        self._planning_times_ms: list[float] = []
        self._optimization_scores: list[float] = []
        self._total_cost: float = 0.0
        self._total_duration_minutes: int = 0
        self._plans_per_action_type: dict[str, int] = {}

    def record_plan(self, action_type: str = "", step_count: int = 0) -> None:
        """Record a new action plan."""
        self._plans_total += 1
        self._tasks_total += step_count
        if action_type:
            at = action_type.upper()
            self._plans_per_action_type[at] = self._plans_per_action_type.get(at, 0) + 1
        log.info("action_metrics.plan", action_type=action_type, steps=step_count)

    def record_resource_allocation(self, resource_count: int) -> None:
        """Record resource allocation."""
        self._resources_allocated += resource_count
        log.info("action_metrics.resources", count=resource_count)

    def record_conflict(self) -> None:
        """Record a resource conflict."""
        self._conflicts_detected += 1
        log.info("action_metrics.conflict", total=self._conflicts_detected)

    def record_planning_time(self, time_ms: float) -> None:
        """Record a planning latency sample."""
        self._planning_times_ms.append(time_ms)
        log.info("action_metrics.planning_time", time_ms=time_ms)

    def record_optimization_score(self, score: float) -> None:
        """Record an optimisation score."""
        self._optimization_scores.append(max(0.0, min(1.0, score)))
        log.info("action_metrics.optimization_score", score=score)

    def record_cost(self, cost: float) -> None:
        """Record a plan cost."""
        self._total_cost += max(0.0, cost)
        log.info("action_metrics.cost", cost=cost)

    def record_duration(self, duration_minutes: int) -> None:
        """Record a plan duration."""
        self._total_duration_minutes += max(0, duration_minutes)
        log.info("action_metrics.duration", minutes=duration_minutes)

    def get_plans_total(self) -> int:
        return self._plans_total

    def get_tasks_total(self) -> int:
        return self._tasks_total

    def get_resources_allocated(self) -> int:
        return self._resources_allocated

    def get_conflicts_detected(self) -> int:
        return self._conflicts_detected

    def get_average_planning_time_ms(self) -> float:
        if not self._planning_times_ms:
            return 0.0
        return round(sum(self._planning_times_ms) / len(self._planning_times_ms), 2)

    def get_average_optimization_score(self) -> float:
        if not self._optimization_scores:
            return 0.0
        return round(sum(self._optimization_scores) / len(self._optimization_scores), 4)

    def get_average_cost(self) -> float:
        if self._plans_total == 0:
            return 0.0
        return round(self._total_cost / self._plans_total, 2)

    def get_average_duration_minutes(self) -> float:
        if self._plans_total == 0:
            return 0.0
        return round(self._total_duration_minutes / self._plans_total, 2)

    def snapshot(self) -> ActionMetricsSnapshot:
        """Take a point-in-time snapshot of all action metrics."""
        return ActionMetricsSnapshot(
            plans_total=self._plans_total,
            tasks_total=self._tasks_total,
            resources_allocated=self._resources_allocated,
            conflicts_detected=self._conflicts_detected,
            planning_times_ms=list(self._planning_times_ms),
            optimization_scores=list(self._optimization_scores),
            average_cost=self.get_average_cost(),
            average_duration_minutes=self.get_average_duration_minutes(),
            plans_per_action_type=dict(self._plans_per_action_type),
        )

    def reset(self) -> None:
        """Reset all metrics to zero."""
        self._plans_total = 0
        self._tasks_total = 0
        self._resources_allocated = 0
        self._conflicts_detected = 0
        self._planning_times_ms.clear()
        self._optimization_scores.clear()
        self._total_cost = 0.0
        self._total_duration_minutes = 0
        self._plans_per_action_type.clear()
        log.info("action_metrics.reset")
