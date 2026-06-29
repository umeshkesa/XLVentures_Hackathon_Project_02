"""ActionTrace — distributed tracing for action planning operations.

Records trace spans for planning, optimisation, dependency
resolution, resource allocation, cost estimation, timeline
generation, and other pipeline stages with timing and
structured metadata.
"""

from __future__ import annotations

from datetime import UTC, datetime

import structlog

from adip.actions.execution.models import TraceRecord

log = structlog.get_logger(__name__)


class ActionTrace:
    """Manages trace records for action planning observability."""

    def __init__(self) -> None:
        self._traces: list[TraceRecord] = []

    def record(self, trace: TraceRecord) -> None:
        """Record a trace entry."""
        log.info("action_trace.record", trace_id=str(trace.trace_id), operation=trace.operation)
        self._traces.append(trace)

    def record_stage(
        self,
        stage_name: str,
        plan_id: str = "",
        session_id: str = "",
        details: str = "",
        correlation_id: str = "",
        success: bool = True,
        duration_ms: float | None = None,
    ) -> TraceRecord:
        """Create and record a trace for a pipeline stage."""
        record = TraceRecord(
            stage_name=stage_name,
            operation=stage_name,
            plan_id=plan_id,
            session_id=session_id,
            details=details,
            duration_ms=duration_ms,
            success=success,
            correlation_id=correlation_id,
            timestamp=datetime.now(UTC),
        )
        self.record(record)
        return record

    def record_planning(
        self,
        plan_id: str = "",
        session_id: str = "",
        correlation_id: str = "",
        success: bool = True,
        duration_ms: float | None = None,
    ) -> TraceRecord:
        return self.record_stage(
            stage_name="planning", plan_id=plan_id, session_id=session_id,
            details="Action plan generation", correlation_id=correlation_id,
            success=success, duration_ms=duration_ms,
        )

    def record_optimization(
        self,
        plan_id: str = "",
        session_id: str = "",
        correlation_id: str = "",
        success: bool = True,
        duration_ms: float | None = None,
    ) -> TraceRecord:
        return self.record_stage(
            stage_name="optimisation", plan_id=plan_id, session_id=session_id,
            details="Action plan optimization", correlation_id=correlation_id,
            success=success, duration_ms=duration_ms,
        )

    def record_dependency(
        self,
        plan_id: str = "",
        session_id: str = "",
        correlation_id: str = "",
        success: bool = True,
        duration_ms: float | None = None,
    ) -> TraceRecord:
        return self.record_stage(
            stage_name="dependencies", plan_id=plan_id, session_id=session_id,
            details="Dependency resolution", correlation_id=correlation_id,
            success=success, duration_ms=duration_ms,
        )

    def record_resource(
        self,
        plan_id: str = "",
        session_id: str = "",
        correlation_id: str = "",
        success: bool = True,
        duration_ms: float | None = None,
    ) -> TraceRecord:
        return self.record_stage(
            stage_name="resources", plan_id=plan_id, session_id=session_id,
            details="Resource allocation", correlation_id=correlation_id,
            success=success, duration_ms=duration_ms,
        )

    def record_cost(
        self,
        plan_id: str = "",
        session_id: str = "",
        correlation_id: str = "",
        success: bool = True,
        duration_ms: float | None = None,
    ) -> TraceRecord:
        return self.record_stage(
            stage_name="cost", plan_id=plan_id, session_id=session_id,
            details="Cost estimation", correlation_id=correlation_id,
            success=success, duration_ms=duration_ms,
        )

    def record_timeline(
        self,
        plan_id: str = "",
        session_id: str = "",
        correlation_id: str = "",
        success: bool = True,
        duration_ms: float | None = None,
    ) -> TraceRecord:
        return self.record_stage(
            stage_name="timeline", plan_id=plan_id, session_id=session_id,
            details="Timeline generation", correlation_id=correlation_id,
            success=success, duration_ms=duration_ms,
        )

    def record_risk(
        self,
        plan_id: str = "",
        session_id: str = "",
        correlation_id: str = "",
        success: bool = True,
        duration_ms: float | None = None,
    ) -> TraceRecord:
        return self.record_stage(
            stage_name="risk", plan_id=plan_id, session_id=session_id,
            details="Risk evaluation", correlation_id=correlation_id,
            success=success, duration_ms=duration_ms,
        )

    def record_policy(
        self,
        plan_id: str = "",
        session_id: str = "",
        correlation_id: str = "",
        success: bool = True,
        duration_ms: float | None = None,
    ) -> TraceRecord:
        return self.record_stage(
            stage_name="policy", plan_id=plan_id, session_id=session_id,
            details="Policy validation", correlation_id=correlation_id,
            success=success, duration_ms=duration_ms,
        )

    def record_conflict(
        self,
        plan_id: str = "",
        session_id: str = "",
        correlation_id: str = "",
        success: bool = True,
        duration_ms: float | None = None,
    ) -> TraceRecord:
        return self.record_stage(
            stage_name="conflicts", plan_id=plan_id, session_id=session_id,
            details="Conflict detection", correlation_id=correlation_id,
            success=success, duration_ms=duration_ms,
        )

    def record_feasibility(
        self,
        plan_id: str = "",
        session_id: str = "",
        correlation_id: str = "",
        success: bool = True,
        duration_ms: float | None = None,
    ) -> TraceRecord:
        return self.record_stage(
            stage_name="feasibility", plan_id=plan_id, session_id=session_id,
            details="Feasibility analysis", correlation_id=correlation_id,
            success=success, duration_ms=duration_ms,
        )

    def record_graph(
        self,
        plan_id: str = "",
        session_id: str = "",
        correlation_id: str = "",
        success: bool = True,
        duration_ms: float | None = None,
    ) -> TraceRecord:
        return self.record_stage(
            stage_name="graph", plan_id=plan_id, session_id=session_id,
            details="Graph construction", correlation_id=correlation_id,
            success=success, duration_ms=duration_ms,
        )

    def record_execution_window(
        self,
        plan_id: str = "",
        session_id: str = "",
        correlation_id: str = "",
        success: bool = True,
        duration_ms: float | None = None,
    ) -> TraceRecord:
        return self.record_stage(
            stage_name="execution_window", plan_id=plan_id, session_id=session_id,
            details="Execution window selection", correlation_id=correlation_id,
            success=success, duration_ms=duration_ms,
        )

    def record_compensation(
        self,
        plan_id: str = "",
        session_id: str = "",
        correlation_id: str = "",
        success: bool = True,
        duration_ms: float | None = None,
    ) -> TraceRecord:
        return self.record_stage(
            stage_name="compensation", plan_id=plan_id, session_id=session_id,
            details="Compensation strategy selection", correlation_id=correlation_id,
            success=success, duration_ms=duration_ms,
        )

    # ── Query methods ──

    def get_by_plan_id(self, plan_id: str) -> list[TraceRecord]:
        return [t for t in self._traces if t.plan_id == plan_id]

    def get_by_operation(self, operation: str) -> list[TraceRecord]:
        return [t for t in self._traces if t.operation == operation]

    def get_by_stage(self, stage_name: str) -> list[TraceRecord]:
        return [t for t in self._traces if t.stage_name == stage_name]

    def get_recent(self, limit: int = 50) -> list[TraceRecord]:
        return sorted(self._traces, key=lambda t: t.timestamp, reverse=True)[:limit]

    def clear(self) -> None:
        self._traces.clear()

    def count(self) -> int:
        return len(self._traces)
