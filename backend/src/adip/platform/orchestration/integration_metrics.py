"""DefaultIntegrationMetrics — workflow-spanning aggregated metrics.

Builds on the Phase 1 PlatformMetricsCollector to provide higher-level
metrics across the complete end-to-end pipeline.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import structlog

from adip.platform.enums import PipelineStage
from adip.platform.orchestration.metrics_collector import DefaultPlatformMetricsCollector

logger = structlog.get_logger(__name__)

# ── Workflow stage grouping ─────────────────────────────────────────
_WORKFLOW_PHASES: dict[str, list[PipelineStage]] = {
    "intake": [PipelineStage.VALIDATION],
    "planning": [PipelineStage.PLANNER, PipelineStage.WORKFLOW],
    "knowledge": [PipelineStage.MEMORY, PipelineStage.KNOWLEDGE],
    "rules": [PipelineStage.RULES],
    "evidence": [PipelineStage.EVIDENCE],
    "reasoning": [PipelineStage.REASONING],
    "recommendation": [PipelineStage.RECOMMENDATION],
    "explainability": [PipelineStage.EXPLAINABILITY],
    "review": [PipelineStage.DECISION_REVIEW],
    "action": [PipelineStage.ACTION_MANAGER, PipelineStage.ACTION_ENGINE],
    "energy": [PipelineStage.ENERGY],
    "response": [PipelineStage.RESPONSE],
}


class DefaultIntegrationMetrics(DefaultPlatformMetricsCollector):
    """Enhanced metrics collector for cross-module workflow metrics.

    In addition to per-stage metrics, this provides:
    - Per-phase aggregated metrics (intake, planning, knowledge, etc.)
    - Workflow-level latency breakdown
    - Cross-module throughput
    - Validation pipeline metrics (Phase 3.5)
    - Platform health metrics (Phase 3.5)
    """

    def __init__(self) -> None:
        super().__init__()
        self._phase_latency: dict[str, list[float]] = {phase: [] for phase in _WORKFLOW_PHASES}
        self._validation_count: int = 0
        self._readiness_checks: int = 0
        self._audit_packages_created: int = 0
        self._snapshots_taken: int = 0
        logger.debug("integration_metrics.initialized")

    def record_phase_latency(self, phase: str, duration_ms: float) -> None:
        """Record latency for a workflow phase."""
        if phase in self._phase_latency:
            self._phase_latency[phase].append(duration_ms)

    def record_validation_operation(self) -> None:
        """Record a validation pipeline operation (Phase 3.5)."""
        self._validation_count += 1

    def record_readiness_check(self) -> None:
        """Record a readiness check operation (Phase 3.5)."""
        self._readiness_checks += 1

    def record_audit_package_created(self) -> None:
        """Record an audit package creation (Phase 3.5)."""
        self._audit_packages_created += 1

    def record_snapshot_taken(self) -> None:
        """Record a platform snapshot (Phase 3.5)."""
        self._snapshots_taken += 1

    def get_phase_summary(self) -> dict[str, dict[str, float]]:
        """Get average latency per workflow phase."""
        summary: dict[str, dict[str, float]] = {}
        for phase, latencies in self._phase_latency.items():
            if latencies:
                avg = sum(latencies) / len(latencies)
                total = sum(latencies)
                summary[phase] = {
                    "average_ms": round(avg, 2),
                    "total_ms": round(total, 2),
                    "count": len(latencies),
                }
            else:
                summary[phase] = {"average_ms": 0.0, "total_ms": 0.0, "count": 0}
        return summary

    def get_workflow_snapshot(self) -> dict[str, Any]:
        """Get a comprehensive workflow metrics snapshot."""
        base = self.get_snapshot()
        phases = self.get_phase_summary()
        return {
            "base": base.model_dump(),
            "phases": phases,
            "phase_count": len(phases),
            "validation_operations": self._validation_count,
            "readiness_checks": self._readiness_checks,
            "audit_packages_created": self._audit_packages_created,
            "snapshots_taken": self._snapshots_taken,
            "timestamp": datetime.now(UTC).isoformat(),
        }
