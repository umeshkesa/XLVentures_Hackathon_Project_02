"""TraceManager — records execution traces for Memory Manager pipeline stages.

Each stage (validator, policy, router, adapter, etc.) can record a trace
with operation, lifecycle state, tier, namespace, duration, and errors.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import structlog

from adip.memory.enums import MemoryOperation
from adip.memory.execution.models import MemoryTrace

log = structlog.get_logger(__name__)


class TraceManager:
    """Manages execution trace recording for the Memory Manager pipeline."""

    def __init__(self) -> None:
        self._traces: list[MemoryTrace] = []

    def start(
        self,
        stage_name: str,
        operation: MemoryOperation,
        resource_id: str = "",
    ) -> MemoryTrace:
        """Begin a new trace for a pipeline stage."""
        trace = MemoryTrace(
            stage_name=stage_name,
            operation=operation,
            started_at=datetime.now(UTC),
            input_summary={"resource_id": resource_id},
        )
        self._traces.append(trace)
        return trace

    def complete(
        self,
        trace: MemoryTrace,
        output_summary: dict[str, Any],
        warnings: list[str] | None = None,
        errors: list[str] | None = None,
    ) -> MemoryTrace:
        """Complete a trace, recording duration and outcome."""
        trace.completed_at = datetime.now(UTC)
        trace.output_summary = output_summary
        if warnings:
            trace.warnings = warnings
        if errors:
            trace.success = False
            trace.errors = errors

        if trace.started_at:
            delta = trace.completed_at - trace.started_at
            trace.duration_ms = round(delta.total_seconds() * 1000, 2)

        return trace

    def get_traces(self, stage_name: str | None = None) -> list[MemoryTrace]:
        """Return recorded traces, optionally filtered by stage."""
        if stage_name:
            return [t for t in self._traces if t.stage_name == stage_name]
        return list(self._traces)

    def clear(self) -> None:
        """Clear all traces (for testing)."""
        self._traces.clear()
