"""TraceAggregator — merges traces from upstream pipelines.

Deterministic placeholder that aggregates trace records from
evidence, reasoning, and recommendation pipelines into a
unified trace list.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import structlog

from adip.explainability.execution.models import TraceRecord

log = structlog.get_logger(__name__)


class TraceAggregator:
    """Aggregates trace records from upstream pipelines.

    Deterministic placeholder that merges traces from evidence,
    reasoning, and recommendation pipelines into a unified list
    of TraceRecord objects.
    """

    def __init__(self) -> None:
        self._records: list[TraceRecord] = []

    def aggregate(
        self,
        evidence_trace: list[dict[str, Any]] | None = None,
        reasoning_trace: list[dict[str, Any]] | None = None,
        recommendation_trace: list[dict[str, Any]] | None = None,
        correlation_id: str = "",
    ) -> list[TraceRecord]:
        """Aggregate traces from upstream pipelines.

        Merges traces from evidence, reasoning, and recommendation
        pipelines into unified TraceRecord objects.

        Args:
            evidence_trace: Optional list of evidence trace dicts.
            reasoning_trace: Optional list of reasoning trace dicts.
            recommendation_trace: Optional list of recommendation trace dicts.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            List of aggregated TraceRecord instances.
        """
        all_traces: list[dict[str, Any]] = []
        if evidence_trace:
            all_traces.extend([{**t, "source": "evidence"} for t in evidence_trace])
        if reasoning_trace:
            all_traces.extend([{**t, "source": "reasoning"} for t in reasoning_trace])
        if recommendation_trace:
            all_traces.extend([{**t, "source": "recommendation"} for t in recommendation_trace])

        records = self.merge_traces(all_traces)
        log.info("Traces aggregated", count=len(records), correlation_id=correlation_id)
        return records

    def merge_traces(self, traces: list[dict[str, Any]]) -> list[TraceRecord]:
        """Merge raw trace dicts into TraceRecord objects.

        Args:
            traces: List of raw trace dictionaries.

        Returns:
            List of TraceRecord instances.
        """
        records: list[TraceRecord] = []
        for trace in traces:
            now = datetime.now(UTC)
            record = TraceRecord(
                stage_name=trace.get("stage_name", ""),
                operation=trace.get("operation", ""),
                explanation_id=trace.get("explanation_id", ""),
                correlation_id=trace.get("correlation_id", ""),
                started_at=trace.get("started_at", now),
                completed_at=trace.get("completed_at", now),
                duration_ms=trace.get("duration_ms"),
                success=trace.get("success", True),
                warnings=trace.get("warnings", []),
                errors=trace.get("errors", []),
                metadata={"source": trace.get("source", "unknown"), **trace.get("metadata", {})},
            )
            records.append(record)
            self._records.append(record)
        return records

    def get_by_stage(self, stage_name: str) -> list[TraceRecord]:
        """Get all trace records for a specific stage.

        Args:
            stage_name: The stage name to filter by.

        Returns:
            List of matching TraceRecord instances.
        """
        return [r for r in self._records if r.stage_name == stage_name]

    def get_by_source(self, source: str) -> list[TraceRecord]:
        """Get all trace records from a specific source.

        Args:
            source: The source name to filter by.

        Returns:
            List of matching TraceRecord instances.
        """
        return [r for r in self._records if r.metadata.get("source") == source]

    def get_all(self) -> list[TraceRecord]:
        """Get all aggregated trace records.

        Returns:
            List of all TraceRecord instances.
        """
        return list(self._records)

    def clear(self) -> None:
        """Clear all aggregated trace records."""
        self._records.clear()
        log.info("Trace aggregator records cleared")

    def count(self) -> int:
        """Get the total number of aggregated trace records.

        Returns:
            The number of trace records.
        """
        return len(self._records)
