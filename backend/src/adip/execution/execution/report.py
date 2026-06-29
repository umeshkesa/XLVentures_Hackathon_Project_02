"""ExecutionReportGenerator — generates comprehensive execution reports.

Creates detailed execution reports including summaries,
metrics, failures, retries, and rollback information.
"""

from __future__ import annotations

from typing import Any

import structlog

from adip.execution.enums import ExecutionState
from adip.execution.execution.models import (
    AuditRecord,
    ExecutionReport,
    FailureClassification,
    MetricsSnapshot,
)

log = structlog.get_logger(__name__)


class ExecutionReportGenerator:
    """Generates comprehensive execution reports."""

    def generate(
        self,
        session_id: str = "",
        package_id: str = "",
        total_tasks: int = 0,
        completed_tasks: int = 0,
        failed_tasks: int = 0,
        skipped_tasks: int = 0,
        retries_performed: int = 0,
        rollbacks_performed: int = 0,
        compensations_performed: int = 0,
        total_duration_ms: float = 0.0,
        final_state: ExecutionState = ExecutionState.COMPLETED,
        failures: list[FailureClassification] | None = None,
        audit_entries: list[AuditRecord] | None = None,
        metrics: MetricsSnapshot | None = None,
        correlation_id: str = "",
    ) -> ExecutionReport:
        """Generate a comprehensive execution report.

        Args:
            session_id: The session ID.
            package_id: The package ID.
            total_tasks: Total number of tasks.
            completed_tasks: Number of completed tasks.
            failed_tasks: Number of failed tasks.
            skipped_tasks: Number of skipped tasks.
            retries_performed: Number of retries.
            rollbacks_performed: Number of rollbacks.
            compensations_performed: Number of compensations.
            total_duration_ms: Total execution duration.
            final_state: Final execution state.
            failures: List of failure classifications.
            audit_entries: List of audit records.
            metrics: Metrics snapshot.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            An ExecutionReport with all available data.
        """
        overall_success = final_state == ExecutionState.COMPLETED
        failure_summary = self._build_failure_summary(failures or [])

        report = ExecutionReport(
            session_id=session_id,
            package_id=package_id,
            overall_success=overall_success,
            final_state=final_state,
            total_tasks=total_tasks,
            tasks_completed=completed_tasks,
            tasks_failed=failed_tasks,
            tasks_skipped=skipped_tasks,
            retries_performed=retries_performed,
            rollbacks_performed=rollbacks_performed,
            compensations_performed=compensations_performed,
            total_duration_ms=total_duration_ms,
            failure_summary=failure_summary,
            failure_details=failures or [],
            audit_entries=audit_entries or [],
            metrics=metrics,
        )
        log.info(
            "report.generated",
            session_id=session_id,
            success=overall_success,
            total_tasks=total_tasks,
            failed=failed_tasks,
            correlation_id=correlation_id,
        )
        return report

    def generate_summary(
        self,
        session_id: str = "",
        package_id: str = "",
        total_tasks: int = 0,
        completed_tasks: int = 0,
        failed_tasks: int = 0,
        final_state: ExecutionState = ExecutionState.COMPLETED,
        total_duration_ms: float = 0.0,
        correlation_id: str = "",
    ) -> dict[str, Any]:
        """Generate a brief execution summary.

        Args:
            session_id: The session ID.
            package_id: The package ID.
            total_tasks: Total number of tasks.
            completed_tasks: Number of completed tasks.
            failed_tasks: Number of failed tasks.
            final_state: Final execution state.
            total_duration_ms: Total execution duration.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            Dict with summary fields.
        """
        overall_success = final_state == ExecutionState.COMPLETED
        summary = {
            "session_id": session_id,
            "package_id": package_id,
            "overall_success": overall_success,
            "final_state": final_state.value,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks,
            "skipped_tasks": 0,
            "total_duration_ms": total_duration_ms,
            "success_rate": round(completed_tasks / max(1, total_tasks), 4),
        }
        log.info(
            "report.summary",
            session_id=session_id,
            success=overall_success,
            correlation_id=correlation_id,
        )
        return summary

    def _build_failure_summary(
        self,
        failures: list[FailureClassification],
    ) -> str:
        """Build a human-readable failure summary from failure classifications."""
        if not failures:
            return ""
        by_type: dict[str, int] = {}
        for f in failures:
            by_type[f.failure_type] = by_type.get(f.failure_type, 0) + 1
        parts = [f"{count} {ftype}" for ftype, count in sorted(by_type.items())]
        return f"Failures: {', '.join(parts)}" if parts else ""
