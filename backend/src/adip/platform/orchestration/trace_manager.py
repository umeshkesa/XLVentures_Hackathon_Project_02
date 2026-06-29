"""DefaultTraceManager — unified tracing across all platform modules."""

from __future__ import annotations

import uuid
from typing import Any

import structlog

from adip.platform.contracts.models import PlatformTrace, PlatformTraceEntry
from adip.platform.enums import PipelineStage
from adip.platform.interfaces import TraceManager

logger = structlog.get_logger(__name__)


class DefaultTraceManager(TraceManager):
    """Default trace manager for platform pipeline tracing.

    Maintains an in-memory store of traces for each pipeline
    execution.
    """

    def __init__(self) -> None:
        self._traces: dict[str, PlatformTrace] = {}
        logger.debug("trace_manager.initialized")

    def create_trace(self, correlation_id: str) -> PlatformTrace:
        """Create a new trace for a pipeline execution."""
        trace = PlatformTrace(
            trace_id=uuid.uuid4(),
            correlation_id=correlation_id,
            entries=[],
            total_duration_ms=0.0,
            completed=False,
        )
        self._traces[str(trace.trace_id)] = trace
        logger.debug("trace_manager.created", trace_id=str(trace.trace_id), correlation_id=correlation_id)
        return trace

    def record_stage(
        self,
        trace_id: str,
        stage: PipelineStage,
        module: str,
        status: str,
        duration_ms: float,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Record a stage execution in a trace."""
        if trace_id not in self._traces:
            logger.warning("trace_manager.trace_not_found", trace_id=trace_id)
            return

        trace = self._traces[trace_id]
        entry = PlatformTraceEntry(
            stage=stage,
            module=module,
            status=status,
            duration_ms=duration_ms,
            details=details or {},
        )
        trace.entries.append(entry)
        trace.total_duration_ms = sum(e.duration_ms for e in trace.entries)
        logger.debug(
            "trace_manager.stage_recorded",
            trace_id=trace_id,
            stage=stage.value,
            status=status,
            duration_ms=duration_ms,
        )

    def complete_trace(self, trace_id: str, total_duration_ms: float) -> None:
        """Mark a trace as completed."""
        if trace_id not in self._traces:
            logger.warning("trace_manager.trace_not_found", trace_id=trace_id)
            return

        trace = self._traces[trace_id]
        trace.completed = True
        trace.total_duration_ms = total_duration_ms
        logger.debug(
            "trace_manager.completed",
            trace_id=trace_id,
            total_duration_ms=total_duration_ms,
        )

    def get_trace(self, trace_id: str) -> PlatformTrace | None:
        """Get a trace by ID."""
        return self._traces.get(trace_id)

    def list_traces(self) -> list[PlatformTrace]:
        """List all traces."""
        return list(self._traces.values())

    def clear(self) -> None:
        """Clear all traces."""
        self._traces.clear()
        logger.debug("trace_manager.cleared")
