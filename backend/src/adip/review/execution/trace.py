"""ReviewTrace — distributed tracing for review operations.

Records trace spans for review assignment, policy checks,
workflow execution, decision making, escalation operations,
and pipeline stages with timing and structured metadata.
"""

from __future__ import annotations

from datetime import UTC, datetime

import structlog

from adip.review.execution.models import TraceRecord

log = structlog.get_logger(__name__)


class ReviewTrace:
    """Manages trace records for review operation observability."""

    def __init__(self) -> None:
        self._traces: list[TraceRecord] = []

    def record(self, trace: TraceRecord) -> None:
        """Record a trace entry."""
        log.info("review_trace.record", trace_id=str(trace.trace_id), operation=trace.operation)
        self._traces.append(trace)

    def record_assignment(
        self,
        review_id: str = "",
        performed_by: str = "",
        correlation_id: str = "",
        success: bool = True,
        duration_ms: float | None = None,
    ) -> TraceRecord:
        """Record an assignment trace."""
        return self.record_stage(
            stage_name="assignment",
            review_id=review_id,
            performed_by=performed_by,
            details="Reviewer assignment",
            correlation_id=correlation_id,
            success=success,
            duration_ms=duration_ms,
        )

    def record_policy(
        self,
        review_id: str = "",
        details: str = "",
        correlation_id: str = "",
        success: bool = True,
        duration_ms: float | None = None,
    ) -> TraceRecord:
        """Record a policy check trace."""
        return self.record_stage(
            stage_name="policy",
            review_id=review_id,
            details=details or "Policy evaluation",
            correlation_id=correlation_id,
            success=success,
            duration_ms=duration_ms,
        )

    def record_workflow(
        self,
        review_id: str = "",
        performed_by: str = "",
        correlation_id: str = "",
        success: bool = True,
        duration_ms: float | None = None,
    ) -> TraceRecord:
        """Record a workflow execution trace."""
        return self.record_stage(
            stage_name="workflow",
            review_id=review_id,
            performed_by=performed_by,
            details="Workflow execution",
            correlation_id=correlation_id,
            success=success,
            duration_ms=duration_ms,
        )

    def record_decision(
        self,
        review_id: str = "",
        performed_by: str = "",
        outcome: str = "",
        correlation_id: str = "",
        success: bool = True,
        duration_ms: float | None = None,
    ) -> TraceRecord:
        """Record a decision trace."""
        return self.record_stage(
            stage_name="decision",
            review_id=review_id,
            performed_by=performed_by,
            details=f"Decision outcome: {outcome}" if outcome else "Review decision",
            correlation_id=correlation_id,
            success=success,
            duration_ms=duration_ms,
        )

    def record_escalation(
        self,
        review_id: str = "",
        performed_by: str = "",
        correlation_id: str = "",
        success: bool = True,
        duration_ms: float | None = None,
    ) -> TraceRecord:
        """Record an escalation trace."""
        return self.record_stage(
            stage_name="escalation",
            review_id=review_id,
            performed_by=performed_by,
            details="Escalation triggered",
            correlation_id=correlation_id,
            success=success,
            duration_ms=duration_ms,
        )

    def record_stage(
        self,
        stage_name: str,
        review_id: str = "",
        performed_by: str = "",
        details: str = "",
        correlation_id: str = "",
        success: bool = True,
        duration_ms: float | None = None,
    ) -> TraceRecord:
        """Create and record a trace for a pipeline stage."""
        record = TraceRecord(
            stage_name=stage_name,
            operation=stage_name,
            review_id=review_id,
            performed_by=performed_by,
            details=details,
            duration_ms=duration_ms,
            success=success,
            correlation_id=correlation_id,
            timestamp=datetime.now(UTC),
        )
        self.record(record)
        return record

    # ── Phase 3 dedicated stage methods ──────────────────────────────────

    def record_governance_confidence(
        self,
        review_id: str = "",
        performed_by: str = "",
        correlation_id: str = "",
        success: bool = True,
        duration_ms: float | None = None,
    ) -> TraceRecord:
        """Record a governance confidence trace."""
        return self.record_stage(
            stage_name="governance_confidence",
            review_id=review_id,
            performed_by=performed_by,
            details="Governance confidence calculation",
            correlation_id=correlation_id,
            success=success,
            duration_ms=duration_ms,
        )

    def record_consensus(
        self,
        review_id: str = "",
        performed_by: str = "",
        correlation_id: str = "",
        success: bool = True,
        duration_ms: float | None = None,
    ) -> TraceRecord:
        """Record a consensus evaluation trace."""
        return self.record_stage(
            stage_name="consensus",
            review_id=review_id,
            performed_by=performed_by,
            details="Consensus evaluation",
            correlation_id=correlation_id,
            success=success,
            duration_ms=duration_ms,
        )

    def record_delegation(
        self,
        review_id: str = "",
        performed_by: str = "",
        correlation_id: str = "",
        success: bool = True,
        duration_ms: float | None = None,
    ) -> TraceRecord:
        """Record a delegation trace."""
        return self.record_stage(
            stage_name="delegation",
            review_id=review_id,
            performed_by=performed_by,
            details="Delegation operation",
            correlation_id=correlation_id,
            success=success,
            duration_ms=duration_ms,
        )

    def record_version(
        self,
        review_id: str = "",
        performed_by: str = "",
        correlation_id: str = "",
        success: bool = True,
        duration_ms: float | None = None,
    ) -> TraceRecord:
        """Record a version creation trace."""
        return self.record_stage(
            stage_name="version",
            review_id=review_id,
            performed_by=performed_by,
            details="Version creation",
            correlation_id=correlation_id,
            success=success,
            duration_ms=duration_ms,
        )

    def record_readiness(
        self,
        review_id: str = "",
        performed_by: str = "",
        correlation_id: str = "",
        success: bool = True,
        duration_ms: float | None = None,
    ) -> TraceRecord:
        """Record a readiness assessment trace."""
        return self.record_stage(
            stage_name="readiness",
            review_id=review_id,
            performed_by=performed_by,
            details="Readiness assessment",
            correlation_id=correlation_id,
            success=success,
            duration_ms=duration_ms,
        )

    def record_audit_package(
        self,
        review_id: str = "",
        performed_by: str = "",
        correlation_id: str = "",
        success: bool = True,
        duration_ms: float | None = None,
    ) -> TraceRecord:
        """Record an audit package trace."""
        return self.record_stage(
            stage_name="audit_package",
            review_id=review_id,
            performed_by=performed_by,
            details="Audit package creation",
            correlation_id=correlation_id,
            success=success,
            duration_ms=duration_ms,
        )

    def record_lineage(
        self,
        review_id: str = "",
        performed_by: str = "",
        correlation_id: str = "",
        success: bool = True,
        duration_ms: float | None = None,
    ) -> TraceRecord:
        """Record a lineage trace."""
        return self.record_stage(
            stage_name="lineage",
            review_id=review_id,
            performed_by=performed_by,
            details="Lineage tracking",
            correlation_id=correlation_id,
            success=success,
            duration_ms=duration_ms,
        )

    # ── Query methods ────────────────────────────────────────────────────

    def get_by_review_id(self, review_id: str) -> list[TraceRecord]:
        """Get all trace records for a given review ID."""
        return [t for t in self._traces if t.review_id == review_id]

    def get_by_operation(self, operation: str) -> list[TraceRecord]:
        """Get all trace records for a given operation."""
        return [t for t in self._traces if t.operation == operation]

    def get_by_stage(self, stage_name: str) -> list[TraceRecord]:
        """Get all trace records for a given stage name."""
        return [t for t in self._traces if t.stage_name == stage_name]

    def get_recent(self, limit: int = 50) -> list[TraceRecord]:
        """Get the most recent trace records."""
        return sorted(self._traces, key=lambda t: t.timestamp, reverse=True)[:limit]

    def clear(self) -> None:
        """Clear all trace records."""
        self._traces.clear()

    def count(self) -> int:
        """Return the total number of trace records."""
        return len(self._traces)
