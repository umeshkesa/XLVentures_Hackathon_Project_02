"""ExecutionTelemetry — collects metrics, events, logs, and timing data.

Collects and stores telemetry data for execution operations
including metrics, events, log messages, and timing information
for observability and analysis.
"""

from __future__ import annotations

import structlog

from adip.execution.execution.models import TelemetryRecord

log = structlog.get_logger(__name__)


class ExecutionTelemetry:
    """Collects telemetry data for execution observability."""

    def __init__(self) -> None:
        self._records: list[TelemetryRecord] = []

    def record_metric(
        self,
        session_id: str = "",
        metric_name: str = "",
        metric_value: float = 0.0,
        unit: str = "",
        tags: dict[str, str] | None = None,
        correlation_id: str = "",
    ) -> TelemetryRecord:
        """Record a telemetry metric.

        Args:
            session_id: The session ID.
            metric_name: Name of the metric.
            metric_value: Value of the metric.
            unit: Unit of measurement.
            tags: Tags associated with this metric.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The created TelemetryRecord.
        """
        record = TelemetryRecord(
            session_id=session_id,
            metric_name=metric_name,
            metric_value=metric_value,
            unit=unit,
            tags=tags or {},
        )
        self._records.append(record)
        log.debug(
            "telemetry.metric",
            metric_name=metric_name,
            metric_value=metric_value,
            session_id=session_id,
            correlation_id=correlation_id,
        )
        return record

    def record_event(
        self,
        session_id: str = "",
        event_name: str = "",
        task_id: str = "",
        tags: dict[str, str] | None = None,
        correlation_id: str = "",
    ) -> TelemetryRecord:
        """Record a telemetry event.

        Args:
            session_id: The session ID.
            event_name: Name of the event.
            task_id: Task ID associated with the event.
            tags: Tags associated with this event.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The created TelemetryRecord.
        """
        record = TelemetryRecord(
            session_id=session_id,
            metric_name=f"event.{event_name}",
            metric_value=1.0,
            unit="count",
            tags={"task_id": task_id, **(tags or {})},
        )
        self._records.append(record)
        log.info(
            "telemetry.event",
            event_name=event_name,
            session_id=session_id,
            task_id=task_id,
            correlation_id=correlation_id,
        )
        return record

    def record_timing(
        self,
        session_id: str = "",
        operation: str = "",
        duration_ms: float = 0.0,
        task_id: str = "",
        tags: dict[str, str] | None = None,
        correlation_id: str = "",
    ) -> TelemetryRecord:
        """Record a timing measurement.

        Args:
            session_id: The session ID.
            operation: Name of the timed operation.
            duration_ms: Duration in milliseconds.
            task_id: Task ID associated with this timing.
            tags: Tags associated with this timing.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The created TelemetryRecord.
        """
        record = TelemetryRecord(
            session_id=session_id,
            metric_name=f"timing.{operation}",
            metric_value=duration_ms,
            unit="ms",
            tags={"task_id": task_id, **(tags or {})},
        )
        self._records.append(record)
        log.info(
            "telemetry.timing",
            operation=operation,
            duration_ms=duration_ms,
            session_id=session_id,
            correlation_id=correlation_id,
        )
        return record

    def get_records(
        self,
        session_id: str | None = None,
        metric_name: str | None = None,
    ) -> list[TelemetryRecord]:
        """Get telemetry records with optional filtering.

        Args:
            session_id: Optional session ID filter.
            metric_name: Optional metric name filter.

        Returns:
            Filtered list of TelemetryRecord.
        """
        records = self._records
        if session_id:
            records = [r for r in records if r.session_id == session_id]
        if metric_name:
            records = [r for r in records if r.metric_name == metric_name]
        return records

    def get_average_timing(
        self,
        operation: str,
        session_id: str | None = None,
    ) -> float:
        """Get average timing for a specific operation.

        Args:
            operation: The operation name.
            session_id: Optional session ID filter.

        Returns:
            Average duration in milliseconds.
        """
        records = self.get_records(
            session_id=session_id,
            metric_name=f"timing.{operation}",
        )
        if not records:
            return 0.0
        return round(sum(r.metric_value for r in records) / len(records), 2)

    def clear(self) -> None:
        """Clear all telemetry records."""
        self._records.clear()
