"""MemoryOperationPipeline — standardized pipeline for every memory operation.

Every memory operation follows this deterministic pipeline:

    Memory Request
    → MemoryService
    → MemoryManager
    → MemoryCoordinator
    → MemoryValidator
    → MemoryPolicyEngine
    → MemoryRouter
    → MemoryStore / StorageAdapter
    → LifecycleManager
    → AuditManager
    → MetricsCollector
    → TraceCollector
    → MemoryResponse
"""

from __future__ import annotations

from typing import Any

import structlog

from adip.memory.enums import MemoryOperation

log = structlog.get_logger(__name__)


class MemoryOperationPipeline:
    """Records and validates the pipeline stages for a memory operation.

    Does NOT execute stages — it is a pipeline descriptor that
    documents the standard flow and validates that all stages
    are covered.
    """

    STAGES: list[str] = [
        "MemoryService",
        "MemoryManager",
        "MemoryCoordinator",
        "MemoryValidator",
        "MemoryPolicyEngine",
        "MemoryRouter",
        "MemoryStore",
        "StorageAdapter",
        "LifecycleManager",
        "AuditManager",
        "MetricsCollector",
        "TraceCollector",
    ]

    def __init__(self) -> None:
        self._executed_stages: list[dict[str, Any]] = []

    def record_stage(self, stage: str, operation: MemoryOperation, record_id: str = "") -> None:
        """Record that a pipeline stage was executed."""
        self._executed_stages.append({
            "stage": stage,
            "operation": operation.value,
            "record_id": record_id,
            "order": len(self._executed_stages),
        })

    def get_executed_stages(self) -> list[dict[str, Any]]:
        return list(self._executed_stages)

    def validate_pipeline(self) -> list[str]:
        """Return a list of missing stages (empty = all stages executed)."""
        executed_names = {s["stage"] for s in self._executed_stages}
        return [s for s in self.STAGES if s not in executed_names]

    def clear(self) -> None:
        self._executed_stages.clear()
