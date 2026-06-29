"""API Trace — tracks requests through the API pipeline."""

from __future__ import annotations

import time
from typing import Any
from uuid import uuid4

import structlog
from structlog.contextvars import bind_contextvars

logger = structlog.get_logger(__name__)


class TraceStage:
    """Represents a single stage in the request trace."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.start_time = time.monotonic()
        self.end_time: float | None = None
        self.duration_ms: float | None = None
        self.status: str = "pending"
        self.details: dict[str, Any] | None = {}

    def complete(self, status: str = "completed", details: dict[str, Any] | None = None) -> None:
        self.end_time = time.monotonic()
        self.duration_ms = (self.end_time - self.start_time) * 1000
        self.status = status
        if details:
            self.details = details

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "duration_ms": round(self.duration_ms, 2) if self.duration_ms else None,
            "status": self.status,
            "details": self.details,
        }


class RequestTrace:
    """Tracks a single request through the API pipeline."""

    def __init__(self) -> None:
        self.trace_id = str(uuid4())[:8]
        self.stages: list[TraceStage] = []
        self.start_time = time.monotonic()
        self._current_stage: TraceStage | None = None
        bind_contextvars(api_trace_id=self.trace_id)

    def begin_stage(self, name: str) -> TraceStage:
        if self._current_stage:
            self._current_stage.complete()
        stage = TraceStage(name)
        self.stages.append(stage)
        self._current_stage = stage
        logger.debug("trace.stage.start", trace_id=self.trace_id, stage=name)
        return stage

    def end_stage(self, status: str = "completed", details: dict[str, Any] | None = None) -> None:
        if self._current_stage:
            self._current_stage.complete(status=status, details=details)
            logger.debug(
                "trace.stage.end",
                trace_id=self.trace_id,
                stage=self._current_stage.name,
                duration_ms=self._current_stage.duration_ms,
                status=status,
            )
            self._current_stage = None

    def complete(self) -> None:
        if self._current_stage:
            self._current_stage.complete()
        self.end_time = time.monotonic()
        total_duration = (self.end_time - self.start_time) * 1000
        logger.info(
            "trace.completed",
            trace_id=self.trace_id,
            stages=len(self.stages),
            total_duration_ms=f"{total_duration:.1f}",
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "total_duration_ms": round((time.monotonic() - self.start_time) * 1000, 2) if self.start_time else None,
            "stages": [s.to_dict() for s in self.stages],
        }


class APITraceManager:
    """Manages request tracing across the API pipeline.

    Phase 3.5: added record_diagnostics_stage for diagnostics tracing.
    """

    def __init__(self) -> None:
        self._traces: dict[str, RequestTrace] = {}

    def start_trace(self) -> RequestTrace:
        trace = RequestTrace()
        self._traces[trace.trace_id] = trace
        return trace

    def get_trace(self, trace_id: str) -> RequestTrace | None:
        return self._traces.get(trace_id)

    def complete_trace(self, trace_id: str) -> None:
        trace = self._traces.get(trace_id)
        if trace:
            trace.complete()

    def record_diagnostics_stage(self, trace_id: str, category: str, status: str = "completed", details: dict[str, Any] | None = None) -> None:
        trace = self._traces.get(trace_id)
        if trace:
            stage = trace.begin_stage(f"diagnostics:{category}")
            stage.complete(status=status, details=details)

    def record_compliance_stage(self, trace_id: str, status: str = "completed", details: dict[str, Any] | None = None) -> None:
        trace = self._traces.get(trace_id)
        if trace:
            stage = trace.begin_stage("compliance")
            stage.complete(status=status, details=details)

    def record_governance_stage(self, trace_id: str, status: str = "completed", details: dict[str, Any] | None = None) -> None:
        trace = self._traces.get(trace_id)
        if trace:
            stage = trace.begin_stage("governance")
            stage.complete(status=status, details=details)

    def list_traces(self) -> list[dict[str, Any]]:
        return [t.to_dict() for t in self._traces.values()]

    def clear(self) -> None:
        self._traces.clear()
