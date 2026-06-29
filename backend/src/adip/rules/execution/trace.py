"""RuleTrace — distributed tracing for rule operations.

Records trace spans for rule creation, evaluation, lifecycle
transitions, and pipeline stages with timing and structured
metadata. Enhanced for Phase 3.5 with comprehensive stage
tracking (validation, parsing, compilation, evaluation,
conflict resolution, priority resolution, policy validation)
and per-stage duration measurement.
"""

from __future__ import annotations

from datetime import UTC, datetime

import structlog

from adip.rules.execution.models import TraceRecord

log = structlog.get_logger(__name__)


class RuleTrace:
    """Manages trace records for observability.

    Supports per-stage tracing for rule validation, parsing,
    compilation, evaluation, conflict resolution, priority
    resolution, policy validation, lifecycle transitions,
    and other operations.
    """

    def __init__(self) -> None:
        self._traces: list[TraceRecord] = []

    def record(self, trace: TraceRecord) -> None:
        """Record a trace."""
        log.info("rule_trace.record", trace_id=str(trace.trace_id), operation=trace.operation)
        self._traces.append(trace)

    def record_stage(
        self,
        stage_name: str,
        operation: str,
        rule_id: str | None = None,
        version: int | None = None,
        lifecycle_state: str = "",
        domain: str = "",
        evaluation_strategy: str = "",
        correlation_id: str = "",
        warnings: list[str] | None = None,
        errors: list[str] | None = None,
        success: bool = True,
        duration_ms: float | None = None,
    ) -> TraceRecord:
        """Create and record a trace for a pipeline stage.

        Tracks the full range of stages: validation, parsing,
        compilation, evaluation, conflict_resolution,
        priority_resolution, policy_validation, and others.
        """
        from uuid import UUID

        record = TraceRecord(
            stage_name=stage_name,
            operation=operation,
            rule_id=UUID(rule_id) if rule_id else None,
            version=version,
            lifecycle_state=lifecycle_state,
            domain=domain,
            evaluation_strategy=evaluation_strategy,
            completed_at=datetime.now(UTC),
            duration_ms=duration_ms,
            warnings=warnings or [],
            errors=errors or [],
            success=success,
            correlation_id=correlation_id,
        )
        self.record(record)
        return record

    def record_validation_stage(
        self,
        domain: str = "",
        correlation_id: str = "",
        warnings: list[str] | None = None,
        errors: list[str] | None = None,
        success: bool = True,
        duration_ms: float | None = None,
    ) -> TraceRecord:
        """Record a validation stage trace."""
        return self.record_stage(
            stage_name="validation",
            operation="validate",
            domain=domain,
            correlation_id=correlation_id,
            warnings=warnings,
            errors=errors,
            success=success,
            duration_ms=duration_ms,
        )

    def record_parsing_stage(
        self,
        domain: str = "",
        correlation_id: str = "",
        warnings: list[str] | None = None,
        errors: list[str] | None = None,
        success: bool = True,
        duration_ms: float | None = None,
    ) -> TraceRecord:
        """Record a parsing stage trace."""
        return self.record_stage(
            stage_name="parsing",
            operation="parse",
            domain=domain,
            correlation_id=correlation_id,
            warnings=warnings,
            errors=errors,
            success=success,
            duration_ms=duration_ms,
        )

    def record_compilation_stage(
        self,
        rule_id: str | None = None,
        domain: str = "",
        correlation_id: str = "",
        warnings: list[str] | None = None,
        errors: list[str] | None = None,
        success: bool = True,
        duration_ms: float | None = None,
    ) -> TraceRecord:
        """Record a compilation stage trace."""
        return self.record_stage(
            stage_name="compilation",
            operation="compile",
            rule_id=rule_id,
            domain=domain,
            correlation_id=correlation_id,
            warnings=warnings,
            errors=errors,
            success=success,
            duration_ms=duration_ms,
        )

    def record_evaluation_stage(
        self,
        strategy: str = "",
        domain: str = "",
        correlation_id: str = "",
        warnings: list[str] | None = None,
        errors: list[str] | None = None,
        success: bool = True,
        duration_ms: float | None = None,
    ) -> TraceRecord:
        """Record an evaluation stage trace."""
        return self.record_stage(
            stage_name="evaluation",
            operation="evaluate",
            domain=domain,
            evaluation_strategy=strategy,
            correlation_id=correlation_id,
            warnings=warnings,
            errors=errors,
            success=success,
            duration_ms=duration_ms,
        )

    def record_conflict_resolution_stage(
        self,
        domain: str = "",
        correlation_id: str = "",
        warnings: list[str] | None = None,
        errors: list[str] | None = None,
        success: bool = True,
        duration_ms: float | None = None,
    ) -> TraceRecord:
        """Record a conflict resolution stage trace."""
        return self.record_stage(
            stage_name="conflict_resolution",
            operation="resolve_conflicts",
            domain=domain,
            correlation_id=correlation_id,
            warnings=warnings,
            errors=errors,
            success=success,
            duration_ms=duration_ms,
        )

    def record_priority_resolution_stage(
        self,
        domain: str = "",
        correlation_id: str = "",
        warnings: list[str] | None = None,
        errors: list[str] | None = None,
        success: bool = True,
        duration_ms: float | None = None,
    ) -> TraceRecord:
        """Record a priority resolution stage trace."""
        return self.record_stage(
            stage_name="priority_resolution",
            operation="resolve_priorities",
            domain=domain,
            correlation_id=correlation_id,
            warnings=warnings,
            errors=errors,
            success=success,
            duration_ms=duration_ms,
        )

    def record_policy_validation_stage(
        self,
        domain: str = "",
        correlation_id: str = "",
        warnings: list[str] | None = None,
        errors: list[str] | None = None,
        success: bool = True,
        duration_ms: float | None = None,
    ) -> TraceRecord:
        """Record a policy validation stage trace."""
        return self.record_stage(
            stage_name="policy_validation",
            operation="validate_policy",
            domain=domain,
            correlation_id=correlation_id,
            warnings=warnings,
            errors=errors,
            success=success,
            duration_ms=duration_ms,
        )

    def get_by_trace_id(self, trace_id: str) -> list[TraceRecord]:
        """Get all trace records matching a given trace ID."""
        return [t for t in self._traces if str(t.trace_id) == trace_id]

    def get_by_operation(self, operation: str) -> list[TraceRecord]:
        """Get all trace records for a given operation type."""
        return [t for t in self._traces if t.operation == operation]

    def get_by_stage(self, stage_name: str) -> list[TraceRecord]:
        """Get all trace records for a given stage name."""
        return [t for t in self._traces if t.stage_name == stage_name]

    def get_by_rule_id(self, rule_id: str) -> list[TraceRecord]:
        """Get all trace records for a given rule ID."""
        return [t for t in self._traces if t.rule_id and str(t.rule_id) == rule_id]

    def get_recent(self, limit: int = 50) -> list[TraceRecord]:
        """Get the most recent trace records."""
        return sorted(self._traces, key=lambda t: t.started_at, reverse=True)[:limit]

    def clear(self) -> None:
        """Clear all trace records."""
        self._traces.clear()

    def count(self) -> int:
        """Return the total number of trace records."""
        return len(self._traces)
