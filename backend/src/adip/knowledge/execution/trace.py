"""KnowledgeTrace — distributed tracing for knowledge operations.

Records trace spans for queries, retrievals, document processing,
and pipeline stages with timing, parent-child relationships, and
structured metadata.

Enhanced in Phase 3.5 with per-stage tracking for processing,
retrieval, reranking, and context assembly stages.
"""

from __future__ import annotations

from datetime import UTC, datetime

import structlog

from adip.knowledge.execution.models import TraceRecord

log = structlog.get_logger(__name__)


class KnowledgeTrace:
    """Manages trace records for observability.

    Supports per-stage tracing for processing, retrieval, reranking,
    context building, and other pipeline operations.
    """

    def __init__(self) -> None:
        self._traces: list[TraceRecord] = []

    def record(self, trace: TraceRecord) -> None:
        """Record a trace."""
        log.info("trace.record", trace_id=str(trace.trace_id), operation=trace.operation)
        self._traces.append(trace)

    def record_stage(
        self,
        stage_name: str,
        operation: str,
        domain: str = "",
        version: int | None = None,
        correlation_id: str = "",
        warnings: list[str] | None = None,
        errors: list[str] | None = None,
        success: bool = True,
    ) -> TraceRecord:
        """Create and record a trace for a pipeline stage."""
        record = TraceRecord(
            stage_name=stage_name,
            operation=operation,
            domain=domain,
            version=version,
            completed_at=datetime.now(UTC),
            warnings=warnings or [],
            errors=errors or [],
            success=success,
            correlation_id=correlation_id,
        )
        self.record(record)
        return record

    def get_by_trace_id(self, trace_id: str) -> list[TraceRecord]:
        """Get all trace records matching a given trace ID."""
        return [t for t in self._traces if str(t.trace_id) == trace_id]

    def get_by_operation(self, operation: str) -> list[TraceRecord]:
        """Get all trace records for a given operation type."""
        return [t for t in self._traces if t.operation == operation]

    def get_by_stage(self, stage_name: str) -> list[TraceRecord]:
        """Get all trace records for a given stage name."""
        return [t for t in self._traces if t.stage_name == stage_name]

    def get_recent(self, limit: int = 50) -> list[TraceRecord]:
        """Get the most recent trace records."""
        return sorted(self._traces, key=lambda t: t.started_at, reverse=True)[:limit]

    def get_stages_for_operation(self, operation: str) -> list[str]:
        """Get distinct stage names for a given operation."""
        stages: set[str] = set()
        for t in self._traces:
            if t.operation == operation:
                stages.add(t.stage_name)
        return sorted(stages)

    def clear(self) -> None:
        """Clear all trace records."""
        self._traces.clear()

    def count(self) -> int:
        """Return the total number of trace records."""
        return len(self._traces)
