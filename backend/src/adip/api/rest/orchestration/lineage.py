"""APILineage — tracks request flow through the API pipeline."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

import structlog

logger = structlog.get_logger(__name__)


class LineageEntry:
    """A single entry in the request lineage."""

    def __init__(self, stage: str, data: dict[str, Any] | None = None) -> None:
        self.stage = stage
        self.timestamp = datetime.now(UTC)
        self.data = data or {}

    def to_dict(self) -> dict[str, Any]:
        return {
            "stage": self.stage,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data,
        }


class APILineage:
    """Tracks request lineage through: request, middleware, router, adapter, service, response."""

    def __init__(self) -> None:
        self._lineages: dict[str, list[LineageEntry]] = {}

    def start_trace(self, trace_id: str | None = None) -> str:
        tid = trace_id or str(uuid4())[:8]
        self._lineages[tid] = []
        self._lineages[tid].append(LineageEntry("request", {"trace_id": tid}))
        logger.debug("lineage.started", trace_id=tid)
        return tid

    def record_stage(self, trace_id: str, stage: str, data: dict[str, Any] | None = None) -> None:
        if trace_id not in self._lineages:
            self._lineages[trace_id] = []
        self._lineages[trace_id].append(LineageEntry(stage, data))
        logger.debug("lineage.stage", trace_id=trace_id, stage=stage)

    def record_middleware(self, trace_id: str, middleware_name: str, status: str = "passed") -> None:
        self.record_stage(trace_id, "middleware", {"name": middleware_name, "status": status})

    def record_router(self, trace_id: str, route: str, method: str) -> None:
        self.record_stage(trace_id, "router", {"route": route, "method": method})

    def record_adapter(self, trace_id: str, adapter_name: str, operation: str) -> None:
        self.record_stage(trace_id, "adapter", {"name": adapter_name, "operation": operation})

    def record_service(self, trace_id: str, service_name: str, status: str = "called") -> None:
        self.record_stage(trace_id, "service", {"name": service_name, "status": status})

    def record_response(self, trace_id: str, status_code: int) -> None:
        self.record_stage(trace_id, "response", {"status_code": status_code})

    def get_lineage(self, trace_id: str) -> list[dict[str, Any]] | None:
        if trace_id not in self._lineages:
            return None
        return [entry.to_dict() for entry in self._lineages[trace_id]]

    def list_traces(self) -> list[str]:
        return list(self._lineages.keys())

    def clear(self) -> None:
        self._lineages.clear()
