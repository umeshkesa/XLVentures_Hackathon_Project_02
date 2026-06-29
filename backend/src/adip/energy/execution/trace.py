"""DomainTrace — distributed tracing for energy domain operations.

Records trace entries for assets, sensors, alarms, incidents,
and maintenance operations with structured metadata.
"""

from __future__ import annotations

from datetime import datetime

import structlog

from adip.energy.execution.models import DomainTraceRecord

log = structlog.get_logger(__name__)


class DomainTrace:
    """Manages trace records for energy domain observability."""

    def __init__(self) -> None:
        self._traces: list[DomainTraceRecord] = []

    def record(self, trace: DomainTraceRecord) -> None:
        """Record a trace entry.

        Args:
            trace: The DomainTraceRecord to record.
        """
        log.info(
            "energy.trace.record",
            trace_id=str(trace.trace_id),
            entity_type=trace.entity_type,
            operation=trace.operation,
        )
        self._traces.append(trace)

    def record_asset_operation(
        self,
        entity_id: str = "",
        operation: str = "",
        details: str = "",
        success: bool = True,
    ) -> DomainTraceRecord:
        """Record an asset-related trace.

        Args:
            entity_id: The asset identifier.
            operation: The operation being traced.
            details: Details about the trace.
            success: Whether the operation succeeded.

        Returns:
            The created DomainTraceRecord.
        """
        record = DomainTraceRecord(
            entity_id=entity_id,
            entity_type="asset",
            operation=operation,
            details=details,
            success=success,
            timestamp=datetime.now(),
        )
        self.record(record)
        return record

    def record_sensor_operation(
        self,
        entity_id: str = "",
        operation: str = "",
        details: str = "",
        success: bool = True,
    ) -> DomainTraceRecord:
        """Record a sensor-related trace.

        Args:
            entity_id: The sensor identifier.
            operation: The operation being traced.
            details: Details about the trace.
            success: Whether the operation succeeded.

        Returns:
            The created DomainTraceRecord.
        """
        record = DomainTraceRecord(
            entity_id=entity_id,
            entity_type="sensor",
            operation=operation,
            details=details,
            success=success,
            timestamp=datetime.now(),
        )
        self.record(record)
        return record

    def record_alarm_operation(
        self,
        entity_id: str = "",
        operation: str = "",
        details: str = "",
        success: bool = True,
    ) -> DomainTraceRecord:
        """Record an alarm-related trace.

        Args:
            entity_id: The alarm identifier.
            operation: The operation being traced.
            details: Details about the trace.
            success: Whether the operation succeeded.

        Returns:
            The created DomainTraceRecord.
        """
        record = DomainTraceRecord(
            entity_id=entity_id,
            entity_type="alarm",
            operation=operation,
            details=details,
            success=success,
            timestamp=datetime.now(),
        )
        self.record(record)
        return record

    def record_incident_operation(
        self,
        entity_id: str = "",
        operation: str = "",
        details: str = "",
        success: bool = True,
    ) -> DomainTraceRecord:
        """Record an incident-related trace.

        Args:
            entity_id: The incident identifier.
            operation: The operation being traced.
            details: Details about the trace.
            success: Whether the operation succeeded.

        Returns:
            The created DomainTraceRecord.
        """
        record = DomainTraceRecord(
            entity_id=entity_id,
            entity_type="incident",
            operation=operation,
            details=details,
            success=success,
            timestamp=datetime.now(),
        )
        self.record(record)
        return record

    def record_maintenance_operation(
        self,
        entity_id: str = "",
        operation: str = "",
        details: str = "",
        success: bool = True,
    ) -> DomainTraceRecord:
        """Record a maintenance-related trace.

        Args:
            entity_id: The maintenance record identifier.
            operation: The operation being traced.
            details: Details about the trace.
            success: Whether the operation succeeded.

        Returns:
            The created DomainTraceRecord.
        """
        record = DomainTraceRecord(
            entity_id=entity_id,
            entity_type="maintenance",
            operation=operation,
            details=details,
            success=success,
            timestamp=datetime.now(),
        )
        self.record(record)
        return record

    def record_quality_stage(
        self,
        entity_id: str = "",
        operation: str = "",
        details: str = "",
        success: bool = True,
    ) -> DomainTraceRecord:
        """Record a quality-related trace.

        Args:
            entity_id: The entity identifier.
            operation: The operation being traced.
            details: Details about the trace.
            success: Whether the operation succeeded.

        Returns:
            The created DomainTraceRecord.
        """
        record = DomainTraceRecord(
            entity_id=entity_id,
            entity_type="quality",
            operation=operation,
            details=details,
            success=success,
            timestamp=datetime.now(),
        )
        self.record(record)
        return record

    def record_compliance_stage(
        self,
        entity_id: str = "",
        operation: str = "",
        details: str = "",
        success: bool = True,
    ) -> DomainTraceRecord:
        """Record a compliance-related trace.

        Args:
            entity_id: The entity identifier.
            operation: The operation being traced.
            details: Details about the trace.
            success: Whether the operation succeeded.

        Returns:
            The created DomainTraceRecord.
        """
        record = DomainTraceRecord(
            entity_id=entity_id,
            entity_type="compliance",
            operation=operation,
            details=details,
            success=success,
            timestamp=datetime.now(),
        )
        self.record(record)
        return record

    def record_diagnostics_stage(
        self,
        entity_id: str = "",
        operation: str = "",
        details: str = "",
        success: bool = True,
    ) -> DomainTraceRecord:
        """Record a diagnostics-related trace.

        Args:
            entity_id: The entity identifier.
            operation: The operation being traced.
            details: Details about the trace.
            success: Whether the operation succeeded.

        Returns:
            The created DomainTraceRecord.
        """
        record = DomainTraceRecord(
            entity_id=entity_id,
            entity_type="diagnostics",
            operation=operation,
            details=details,
            success=success,
            timestamp=datetime.now(),
        )
        self.record(record)
        return record

    def record_audit_stage(
        self,
        entity_id: str = "",
        operation: str = "",
        details: str = "",
        success: bool = True,
    ) -> DomainTraceRecord:
        """Record an audit-related trace.

        Args:
            entity_id: The entity identifier.
            operation: The operation being traced.
            details: Details about the trace.
            success: Whether the operation succeeded.

        Returns:
            The created DomainTraceRecord.
        """
        record = DomainTraceRecord(
            entity_id=entity_id,
            entity_type="audit",
            operation=operation,
            details=details,
            success=success,
            timestamp=datetime.now(),
        )
        self.record(record)
        return record

    def record_export_stage(
        self,
        entity_id: str = "",
        operation: str = "",
        details: str = "",
        success: bool = True,
    ) -> DomainTraceRecord:
        """Record an export-related trace.

        Args:
            entity_id: The entity identifier.
            operation: The operation being traced.
            details: Details about the trace.
            success: Whether the operation succeeded.

        Returns:
            The created DomainTraceRecord.
        """
        record = DomainTraceRecord(
            entity_id=entity_id,
            entity_type="export",
            operation=operation,
            details=details,
            success=success,
            timestamp=datetime.now(),
        )
        self.record(record)
        return record

    def record_pipeline_version_stage(
        self,
        entity_id: str = "",
        operation: str = "",
        details: str = "",
        success: bool = True,
    ) -> DomainTraceRecord:
        """Record a pipeline version-related trace.

        Args:
            entity_id: The entity identifier.
            operation: The operation being traced.
            details: Details about the trace.
            success: Whether the operation succeeded.

        Returns:
            The created DomainTraceRecord.
        """
        record = DomainTraceRecord(
            entity_id=entity_id,
            entity_type="pipeline_version",
            operation=operation,
            details=details,
            success=success,
            timestamp=datetime.now(),
        )
        self.record(record)
        return record

    def get_traces(
        self,
        entity_type: str | None = None,
        operation: str | None = None,
    ) -> list[DomainTraceRecord]:
        """Get trace records with optional filtering.

        Args:
            entity_type: Optional entity type filter.
            operation: Optional operation filter.

        Returns:
            Filtered list of DomainTraceRecord.
        """
        traces = self._traces
        if entity_type:
            traces = [t for t in traces if t.entity_type == entity_type]
        if operation:
            traces = [t for t in traces if t.operation == operation]
        return traces

    def get_all_traces(self) -> list[DomainTraceRecord]:
        """Get all trace records.

        Returns:
            List of all DomainTraceRecord objects.
        """
        return list(self._traces)

    def clear(self) -> None:
        """Clear all trace records."""
        self._traces.clear()
