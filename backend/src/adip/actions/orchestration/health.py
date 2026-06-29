"""ExecutionHealth — provides health status for action sub-components.

Deterministic placeholder that aggregates health statuses
from all action sub-components into a comprehensive ActionHealth
model.
"""

from __future__ import annotations

from datetime import UTC, datetime

import structlog

from adip.actions.contracts.models import ActionHealth

log = structlog.get_logger(__name__)


class ExecutionHealth:
    """Provides health status for action sub-components.

    Aggregates health from all sub-components and returns
    a comprehensive ActionHealth model.
    """

    def __init__(self) -> None:
        self._error_count = 0
        self._plan_count = 0
        self._total_latency_ms = 0.0
        self._check_count = 0

    def record_error(self) -> None:
        """Record an error occurrence."""
        self._error_count += 1

    def record_plan(self) -> None:
        """Record a plan processed."""
        self._plan_count += 1

    def record_latency(self, latency_ms: float) -> None:
        """Record a latency sample.

        Args:
            latency_ms: Latency in milliseconds.
        """
        self._total_latency_ms += latency_ms
        self._check_count += 1

    def get_health(self) -> ActionHealth:
        """Get comprehensive health status.

        Returns:
            ActionHealth with all component statuses.
        """
        avg_latency = (
            self._total_latency_ms / self._check_count
            if self._check_count > 0
            else 0.0
        )

        overall = "HEALTHY" if self._error_count == 0 else "DEGRADED"

        return ActionHealth(
            overall_status=overall,
            service_status="HEALTHY",
            manager_status="HEALTHY",
            coordinator_status="HEALTHY",
            planner_status="HEALTHY",
            dependency_resolver_status="HEALTHY",
            resource_allocator_status="HEALTHY",
            schedule_planner_status="HEALTHY",
            rollback_planner_status="HEALTHY",
            readiness_validator_status="HEALTHY",
            confidence_calculator_status="HEALTHY",
            session_manager_status="HEALTHY",
            version_manager_status="HEALTHY",
            lineage_status="HEALTHY",
            snapshot_status="HEALTHY",
            quality_manager_status="HEALTHY",
            review_status="HEALTHY",
            plan_count=self._plan_count,
            error_count=self._error_count,
            average_planning_time_ms=round(avg_latency, 2),
            last_check=datetime.now(UTC),
        )

    def reset(self) -> None:
        """Reset health counters."""
        self._error_count = 0
        self._plan_count = 0
        self._total_latency_ms = 0.0
        self._check_count = 0
