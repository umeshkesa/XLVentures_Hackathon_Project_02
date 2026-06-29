"""AggregatedTracing — enterprise tracing aggregation for the Memory Platform.

Extends the basic TraceManager from Phase 2 with aggregated trace
collection across all pipeline stages.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import structlog

from adip.memory.enums import MemoryOperation

log = structlog.get_logger(__name__)


class AggregatedTracing:
    """Aggregated execution traces across the entire memory pipeline.

    Provides higher-level tracing that wraps individual pipeline
    stage traces with session, correlation, and domain context.
    """

    def __init__(self) -> None:
        self._traces: list[dict[str, Any]] = []

    def record_stage(
        self,
        stage_name: str,
        operation: MemoryOperation,
        memory_id: str = "",
        session_id: str = "",
        correlation_id: str = "",
        domain: str = "",
        namespace: str = "",
        tier: str = "",
        lifecycle_state: str = "",
        duration_ms: float = 0.0,
        success: bool = True,
        warnings: list[str] | None = None,
        errors: list[str] | None = None,
    ) -> dict[str, Any]:
        """Record an aggregated trace entry for a pipeline stage."""
        entry: dict[str, Any] = {
            "stage_name": stage_name,
            "operation": operation.value,
            "memory_id": memory_id,
            "session_id": session_id,
            "correlation_id": correlation_id,
            "domain": domain,
            "namespace": namespace,
            "tier": tier,
            "lifecycle_state": lifecycle_state,
            "duration_ms": duration_ms,
            "success": success,
            "timestamp": datetime.now(UTC).isoformat(),
            "warnings": warnings or [],
            "errors": errors or [],
        }
        self._traces.append(entry)
        return entry

    def get_traces(
        self,
        stage_name: str | None = None,
        session_id: str | None = None,
        operation: MemoryOperation | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Return recorded traces, optionally filtered."""
        results = list(self._traces)
        if stage_name:
            results = [t for t in results if t["stage_name"] == stage_name]
        if session_id:
            results = [t for t in results if t["session_id"] == session_id]
        if operation:
            results = [t for t in results if t["operation"] == operation.value]
        return results[-limit:]

    def clear(self) -> None:
        """Clear all traces (for testing)."""
        self._traces.clear()
