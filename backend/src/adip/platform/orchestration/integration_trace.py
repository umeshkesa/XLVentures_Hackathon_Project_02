"""DefaultIntegrationTrace — workflow-spanning trace for the complete pipeline.

Builds on top of the Phase 1 TraceManager to provide higher-level
workflow traces that span the entire end-to-end pipeline execution.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import structlog

from adip.platform.contracts.models import PlatformTraceEntry
from adip.platform.enums import PipelineStage
from adip.platform.orchestration.trace_manager import DefaultTraceManager

logger = structlog.get_logger(__name__)


class DefaultIntegrationTrace(DefaultTraceManager):
    """Enhanced trace manager for cross-module workflow tracing.

    In addition to standard per-stage tracing, this provides:
    - Workflow-level trace summarisation
    - Cross-module dependency tracing
    - Per-module latency breakdown
    - Validation pipeline traces (Phase 3.5)
    - Phase-level trace summaries (Phase 3.5)
    """

    def __init__(self) -> None:
        super().__init__()
        self._workflow_traces: dict[str, dict[str, Any]] = {}
        self._validation_traces: dict[str, dict[str, Any]] = {}
        logger.debug("integration_trace.initialized")

    def record_workflow_stage(
        self,
        trace_id: str,
        stage: PipelineStage,
        module: str,
        input_keys: list[str],
        output_keys: list[str],
        duration_ms: float,
        status: str = "success",
    ) -> None:
        """Record a workflow-level stage with input/output contract keys."""
        entry = PlatformTraceEntry(
            stage=stage,
            module=module,
            status=status,
            duration_ms=round(duration_ms, 2),
            details={
                "input_keys": input_keys,
                "output_keys": output_keys,
                "workflow_level": True,
            },
        )
        trace = self._traces.get(trace_id)
        if trace:
            trace.entries.append(entry)
            trace.total_duration_ms = sum(e.duration_ms for e in trace.entries)

    def record_validation_stage(
        self,
        trace_id: str,
        stage: str,
        component: str,
        status: str,
        duration_ms: float,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Record a validation pipeline trace entry (Phase 3.5)."""
        entry = PlatformTraceEntry(
            stage=PipelineStage.VALIDATION,
            module=component,
            status=status,
            duration_ms=round(duration_ms, 2),
            details={
                "validation_stage": stage,
                **(details or {}),
            },
        )
        trace = self._traces.get(trace_id)
        if trace:
            trace.entries.append(entry)
            trace.total_duration_ms = sum(e.duration_ms for e in trace.entries)

    def get_workflow_summary(self, trace_id: str) -> dict[str, Any] | None:
        """Get a workflow-level summary for the given trace."""
        if trace_id not in self._workflow_traces:
            return None
        return dict(self._workflow_traces[trace_id])

    def get_phase_trace_summary(self, trace_id: str) -> dict[str, Any]:
        """Get a phase-level trace summary (Phase 3.5)."""
        trace = self._traces.get(trace_id)
        if trace is None:
            return {"trace_id": trace_id, "error": "trace not found"}

        phase_breakdown: dict[str, dict[str, float]] = {}
        for entry in trace.entries:
            phase_key = entry.details.get("validation_stage", entry.stage.value)
            if phase_key not in phase_breakdown:
                phase_breakdown[phase_key] = {"count": 0, "total_ms": 0.0}
            phase_breakdown[phase_key]["count"] += 1
            phase_breakdown[phase_key]["total_ms"] += entry.duration_ms

        return {
            "trace_id": trace_id,
            "correlation_id": trace.correlation_id,
            "phase_breakdown": phase_breakdown,
            "total_entries": len(trace.entries),
            "total_duration_ms": round(trace.total_duration_ms, 2),
            "completed": trace.completed,
        }

    def summarize_workflow(self, trace_id: str) -> dict[str, Any]:
        """Create a workflow summary from the recorded entries."""
        trace = self._traces.get(trace_id)
        if trace is None:
            return {"trace_id": trace_id, "error": "trace not found"}

        stages_count = len(trace.entries)
        total_duration = trace.total_duration_ms
        module_breakdown: dict[str, float] = {}
        for entry in trace.entries:
            mod = entry.module or entry.stage.value
            module_breakdown[mod] = module_breakdown.get(mod, 0.0) + entry.duration_ms

        summary = {
            "trace_id": trace_id,
            "correlation_id": trace.correlation_id,
            "stages_count": stages_count,
            "total_duration_ms": round(total_duration, 2),
            "completed": trace.completed,
            "module_breakdown": module_breakdown,
            "phase_breakdown": self.get_phase_trace_summary(trace_id).get("phase_breakdown", {}),
            "timestamp": datetime.now(UTC).isoformat(),
        }
        self._workflow_traces[trace_id] = summary
        return summary
