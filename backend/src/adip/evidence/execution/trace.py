"""Evidence pipeline tracing.

Tracks pipeline stage execution for evidence processing.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from enum import StrEnum

from adip.evidence.execution.models import TraceRecord


class TraceStage(StrEnum):
    """Stages in the evidence processing pipeline."""

    COLLECTION = "COLLECTION"
    VALIDATION = "VALIDATION"
    NORMALIZATION = "NORMALIZATION"
    CLASSIFICATION = "CLASSIFICATION"
    PRIORITY_ASSIGNMENT = "PRIORITY_ASSIGNMENT"
    CORRELATION = "CORRELATION"
    CONFLICT_DETECTION = "CONFLICT_DETECTION"
    DEDUPLICATION = "DEDUPLICATION"
    GRAPH_BUILDING = "GRAPH_BUILDING"
    BUNDLE_CREATION = "BUNDLE_CREATION"
    TIMELINE = "TIMELINE"
    WEIGHT = "WEIGHT"
    CONSENSUS = "CONSENSUS"
    FUSION = "FUSION"
    PACKAGING = "PACKAGING"
    METRICS = "METRICS"


class EvidenceTrace:
    """Tracks pipeline stage execution for evidence processing.

    Deterministic placeholder that records trace events per stage.
    """

    def __init__(self) -> None:
        self._records: list[TraceRecord] = []

    def record_event(
        self,
        stage: TraceStage,
        operation: str,
        evidence_id: str,
        correlation_id: str | None = None,
        success: bool = True,
        warnings: list[str] | None = None,
        errors: list[str] | None = None,
        duration_ms: float | None = None,
    ) -> TraceRecord:
        """Record a trace event for a pipeline stage.

        Args:
            stage: The pipeline stage name.
            operation: The operation being performed.
            evidence_id: The evidence ID being processed.
            correlation_id: Optional correlation ID.
            success: Whether the stage completed successfully.
            warnings: Optional list of warnings.
            errors: Optional list of errors.
            duration_ms: Optional stage duration in milliseconds.

        Returns:
            The created TraceRecord.
        """
        record = TraceRecord(
            trace_id=str(uuid.uuid4()),
            stage_name=stage.value if isinstance(stage, TraceStage) else str(stage),
            operation=operation,
            evidence_id=str(evidence_id),
            correlation_id=correlation_id or "",
            started_at=datetime.now(UTC),
            completed_at=datetime.now(UTC),
            duration_ms=duration_ms,
            success=success,
            warnings=warnings or [],
            errors=errors or [],
        )
        self._records.append(record)
        return record

    def get_by_evidence_id(self, evidence_id: str) -> list[TraceRecord]:
        """Get all trace records for a given evidence ID.

        Args:
            evidence_id: The evidence ID to filter by.

        Returns:
            List of matching TraceRecord objects.
        """
        return [r for r in self._records if r.evidence_id == evidence_id]

    def get_by_stage(self, stage: TraceStage) -> list[TraceRecord]:
        """Get all trace records for a given stage.

        Args:
            stage: The stage name to filter by.

        Returns:
            List of matching TraceRecord objects.
        """
        stage_name = stage.value if isinstance(stage, TraceStage) else str(stage)
        return [r for r in self._records if r.stage_name == stage_name]

    def get_recent(self, limit: int = 10) -> list[TraceRecord]:
        """Get the most recent trace records.

        Args:
            limit: Maximum number of records to return.

        Returns:
            List of recent TraceRecord objects.
        """
        return self._records[-limit:]

    def clear(self) -> None:
        """Clear all trace records."""
        self._records.clear()

    def count(self) -> int:
        """Get the total number of trace records.

        Returns:
            Number of trace records.
        """
        return len(self._records)
