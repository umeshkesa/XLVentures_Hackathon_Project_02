"""ExecutionHealthManager — provides health status for execution sub-components.

Deterministic placeholder that aggregates health statuses
from all execution sub-components into a comprehensive
ExecutionHealth model.
"""

from __future__ import annotations

from datetime import UTC, datetime

import structlog

from adip.execution.contracts.models import ExecutionHealth

log = structlog.get_logger(__name__)


class ExecutionHealthManager:
    """Provides health status for execution sub-components.

    Aggregates health from all sub-components and returns
    a comprehensive ExecutionHealth model.
    """

    def __init__(self) -> None:
        self._error_count = 0
        self._session_count = 0
        self._active_tasks = 0
        self._total_latency_ms = 0.0
        self._check_count = 0

    def record_error(self) -> None:
        """Record an error occurrence."""
        self._error_count += 1

    def record_session(self) -> None:
        """Record a session processed."""
        self._session_count += 1

    def record_active_task(self, count: int = 1) -> None:
        """Record an active task (Phase 3.5).

        Args:
            count: Number of active tasks.
        """
        self._active_tasks += count

    def record_latency(self, latency_ms: float) -> None:
        """Record a latency sample.

        Args:
            latency_ms: Latency in milliseconds.
        """
        self._total_latency_ms += latency_ms
        self._check_count += 1

    def get_health(self) -> ExecutionHealth:
        """Get comprehensive health status.

        Returns:
            ExecutionHealth with all component statuses.
        """
        avg_latency = (
            self._total_latency_ms / self._check_count
            if self._check_count > 0
            else 0.0
        )

        overall = "HEALTHY" if self._error_count == 0 else "DEGRADED"
        error_rate = round(self._error_count / max(self._session_count, 1), 4)

        return ExecutionHealth(
            overall_status=overall,
            coordinator_status="HEALTHY",
            executor_status="HEALTHY",
            scheduler_status="HEALTHY",
            retry_manager_status="HEALTHY",
            compensation_manager_status="HEALTHY",
            monitor_status="HEALTHY",
            sandbox_status="HEALTHY",
            telemetry_status="HEALTHY",
            diagnostics_status="HEALTHY",
            session_count=self._session_count,
            active_tasks=self._active_tasks,
            error_count=self._error_count,
            average_latency_ms=round(avg_latency, 2),
            error_rate=error_rate,
            last_check=datetime.now(UTC),
        )

    def reset(self) -> None:
        """Reset health counters."""
        self._error_count = 0
        self._session_count = 0
        self._active_tasks = 0
        self._total_latency_ms = 0.0
        self._check_count = 0
