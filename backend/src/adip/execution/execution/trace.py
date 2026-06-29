"""ExecutionTrace — distributed tracing for execution operations.

Records trace spans for execution, monitoring, recovery,
and event operations with timing and structured metadata.
"""

from __future__ import annotations

from datetime import UTC, datetime

import structlog

from adip.execution.execution.models import TraceRecord

log = structlog.get_logger(__name__)


class ExecutionTrace:
    """Manages trace records for execution observability."""

    def __init__(self) -> None:
        self._traces: list[TraceRecord] = []

    def record(self, trace: TraceRecord) -> None:
        """Record a trace entry.

        Args:
            trace: The TraceRecord to record.
        """
        log.info(
            "execution_trace.record",
            trace_id=str(trace.trace_id),
            operation=trace.operation,
            stage=trace.stage_name,
        )
        self._traces.append(trace)

    def record_stage(
        self,
        stage_name: str,
        session_id: str = "",
        task_id: str = "",
        details: str = "",
        correlation_id: str = "",
        success: bool = True,
        duration_ms: float | None = None,
    ) -> TraceRecord:
        """Create and record a trace for a pipeline stage.

        Args:
            stage_name: Name of the stage.
            session_id: Session ID.
            task_id: Task ID.
            details: Details about the trace span.
            correlation_id: Correlation ID for distributed tracing.
            success: Whether the operation succeeded.
            duration_ms: Duration in milliseconds.

        Returns:
            The created TraceRecord.
        """
        record = TraceRecord(
            stage_name=stage_name,
            operation=stage_name,
            session_id=session_id,
            task_id=task_id,
            details=details,
            duration_ms=duration_ms,
            success=success,
            correlation_id=correlation_id,
            timestamp=datetime.now(UTC),
        )
        self.record(record)
        return record

    def record_execution_stage(
        self,
        session_id: str = "",
        task_id: str = "",
        correlation_id: str = "",
        success: bool = True,
        duration_ms: float | None = None,
    ) -> TraceRecord:
        """Record an execution stage trace.

        Args:
            session_id: Session ID.
            task_id: Task ID.
            correlation_id: Correlation ID.
            success: Whether the operation succeeded.
            duration_ms: Duration in milliseconds.

        Returns:
            The created TraceRecord.
        """
        return self.record_stage(
            stage_name="execution",
            session_id=session_id,
            task_id=task_id,
            details="Task execution",
            correlation_id=correlation_id,
            success=success,
            duration_ms=duration_ms,
        )

    def record_monitoring_stage(
        self,
        session_id: str = "",
        correlation_id: str = "",
        success: bool = True,
        duration_ms: float | None = None,
    ) -> TraceRecord:
        """Record a monitoring stage trace.

        Args:
            session_id: Session ID.
            correlation_id: Correlation ID.
            success: Whether the operation succeeded.
            duration_ms: Duration in milliseconds.

        Returns:
            The created TraceRecord.
        """
        return self.record_stage(
            stage_name="monitoring",
            session_id=session_id,
            details="Execution monitoring check",
            correlation_id=correlation_id,
            success=success,
            duration_ms=duration_ms,
        )

    def record_recovery_stage(
        self,
        session_id: str = "",
        task_id: str = "",
        recovery_type: str = "retry",
        correlation_id: str = "",
        success: bool = True,
        duration_ms: float | None = None,
    ) -> TraceRecord:
        """Record a recovery stage trace.

        Args:
            session_id: Session ID.
            task_id: Task ID.
            recovery_type: Type of recovery (retry, compensation, rollback).
            correlation_id: Correlation ID.
            success: Whether the operation succeeded.
            duration_ms: Duration in milliseconds.

        Returns:
            The created TraceRecord.
        """
        return self.record_stage(
            stage_name=f"recovery.{recovery_type}",
            session_id=session_id,
            task_id=task_id,
            details=f"Recovery operation: {recovery_type}",
            correlation_id=correlation_id,
            success=success,
            duration_ms=duration_ms,
        )

    def record_event_stage(
        self,
        session_id: str = "",
        event_type: str = "",
        correlation_id: str = "",
        success: bool = True,
        duration_ms: float | None = None,
    ) -> TraceRecord:
        """Record an event stage trace.

        Args:
            session_id: Session ID.
            event_type: Type of event.
            correlation_id: Correlation ID.
            success: Whether the operation succeeded.
            duration_ms: Duration in milliseconds.

        Returns:
            The created TraceRecord.
        """
        return self.record_stage(
            stage_name=f"event.{event_type}",
            session_id=session_id,
            details=f"Event: {event_type}",
            correlation_id=correlation_id,
            success=success,
            duration_ms=duration_ms,
        )

    def get_traces(
        self,
        session_id: str | None = None,
        stage_name: str | None = None,
    ) -> list[TraceRecord]:
        """Get trace records with optional filtering.

        Args:
            session_id: Optional session ID filter.
            stage_name: Optional stage name filter.

        Returns:
            Filtered list of TraceRecord.
        """
        traces = self._traces
        if session_id:
            traces = [t for t in traces if t.session_id == session_id]
        if stage_name:
            traces = [t for t in traces if t.stage_name == stage_name]
        return traces

    def get_all_traces(self) -> list[TraceRecord]:
        """Get all trace records."""
        return list(self._traces)

    def record_diagnostics_stage(
        self,
        session_id: str = "",
        correlation_id: str = "",
        success: bool = True,
        diagnostics_count: int = 0,
        duration_ms: float | None = None,
    ) -> TraceRecord:
        """Record a diagnostics collection stage trace (Phase 3.5).

        Args:
            session_id: Session ID.
            correlation_id: Correlation ID.
            success: Whether the operation succeeded.
            diagnostics_count: Number of diagnostics events collected.
            duration_ms: Duration in milliseconds.

        Returns:
            The created TraceRecord.
        """
        return self.record_stage(
            stage_name="diagnostics",
            session_id=session_id,
            details=f"Diagnostics collection: {diagnostics_count} events",
            correlation_id=correlation_id,
            success=success,
            duration_ms=duration_ms,
        )

    def record_compliance_stage(
        self,
        session_id: str = "",
        correlation_id: str = "",
        success: bool = True,
        compliance_status: str = "compliant",
        duration_ms: float | None = None,
    ) -> TraceRecord:
        """Record a compliance validation stage trace (Phase 3.5).

        Args:
            session_id: Session ID.
            correlation_id: Correlation ID.
            success: Whether the operation succeeded.
            compliance_status: Compliance status result.
            duration_ms: Duration in milliseconds.

        Returns:
            The created TraceRecord.
        """
        return self.record_stage(
            stage_name="compliance",
            session_id=session_id,
            details=f"Compliance validation: {compliance_status}",
            correlation_id=correlation_id,
            success=success,
            duration_ms=duration_ms,
        )

    def record_export_stage(
        self,
        session_id: str = "",
        correlation_id: str = "",
        success: bool = True,
        export_type: str = "",
        duration_ms: float | None = None,
    ) -> TraceRecord:
        """Record an export generation stage trace (Phase 3.5).

        Args:
            session_id: Session ID.
            correlation_id: Correlation ID.
            success: Whether the operation succeeded.
            export_type: Type of export generated.
            duration_ms: Duration in milliseconds.

        Returns:
            The created TraceRecord.
        """
        return self.record_stage(
            stage_name=f"export.{export_type}",
            session_id=session_id,
            details=f"Export: {export_type}",
            correlation_id=correlation_id,
            success=success,
            duration_ms=duration_ms,
        )

    def record_recovery_report_stage(
        self,
        session_id: str = "",
        correlation_id: str = "",
        success: bool = True,
        recovery_type: str = "retry",
        duration_ms: float | None = None,
    ) -> TraceRecord:
        """Record a recovery report stage trace (Phase 3.5).

        Args:
            session_id: Session ID.
            correlation_id: Correlation ID.
            success: Whether the operation succeeded.
            recovery_type: Type of recovery (retry, compensation, rollback).
            duration_ms: Duration in milliseconds.

        Returns:
            The created TraceRecord.
        """
        return self.record_stage(
            stage_name=f"recovery_report.{recovery_type}",
            session_id=session_id,
            details=f"Recovery report: {recovery_type}",
            correlation_id=correlation_id,
            success=success,
            duration_ms=duration_ms,
        )

    def clear(self) -> None:
        """Clear all trace records."""
        self._traces.clear()
