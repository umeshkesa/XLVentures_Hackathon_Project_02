"""RegistryTrace — distributed tracing for registry pipeline stages.

Records trace spans for validation, search, index, version, lifecycle,
cache, audit, policy, dependency, metrics, and other pipeline stages
with timing and structured metadata.

Phase 3.5 adds dedicated stage methods for cache, audit, policy,
dependency resolution, and metrics.
"""

from __future__ import annotations

from datetime import UTC, datetime

import structlog

from adip.registry.execution.models import TraceRecord

log = structlog.get_logger(__name__)


class RegistryTrace:
    """Manages trace records for registry pipeline observability.

    Supports per-stage tracing for all registry pipeline stages with
    dedicated methods for each stage type. Stages are independently
    timed and carry structured metadata including warnings, errors,
    and correlation IDs.
    """

    def __init__(self) -> None:
        self._traces: list[TraceRecord] = []

    def record(self, trace: TraceRecord) -> None:
        """Record a trace."""
        log.info("registry_trace.record", trace_id=str(trace.trace_id), stage=trace.stage_name)
        self._traces.append(trace)

    def record_stage(
        self,
        stage_name: str,
        operation: str,
        entry_id: str | None = None,
        entry_name: str = "",
        registry_type: str = "",
        namespace: str = "",
        correlation_id: str = "",
        warnings: list[str] | None = None,
        errors: list[str] | None = None,
        success: bool = True,
        duration_ms: float | None = None,
    ) -> TraceRecord:
        """Record a trace span for a registry stage."""
        record = TraceRecord(
            stage_name=stage_name,
            operation=operation,
            entry_id=entry_id,
            entry_name=entry_name,
            registry_type=registry_type,
            namespace=namespace,
            correlation_id=correlation_id,
            completed_at=datetime.now(UTC),
            duration_ms=duration_ms,
            success=success,
            warnings=warnings or [],
            errors=errors or [],
        )
        self.record(record)
        return record

    # ── Dedicated stage methods ───────────────────────────────────

    def record_validation_stage(
        self,
        entry_id: str | None = None,
        entry_name: str = "",
        registry_type: str = "",
        correlation_id: str = "",
        warnings: list[str] | None = None,
        errors: list[str] | None = None,
        success: bool = True,
        duration_ms: float | None = None,
    ) -> TraceRecord:
        return self.record_stage(
            stage_name="validation",
            operation="validate",
            entry_id=entry_id,
            entry_name=entry_name,
            registry_type=registry_type,
            correlation_id=correlation_id,
            warnings=warnings,
            errors=errors,
            success=success,
            duration_ms=duration_ms,
        )

    def record_search_stage(
        self,
        query: str = "",
        registry_type: str = "",
        correlation_id: str = "",
        warnings: list[str] | None = None,
        errors: list[str] | None = None,
        success: bool = True,
        duration_ms: float | None = None,
    ) -> TraceRecord:
        return self.record_stage(
            stage_name="search",
            operation="search",
            entry_name=query,
            registry_type=registry_type,
            correlation_id=correlation_id,
            warnings=warnings,
            errors=errors,
            success=success,
            duration_ms=duration_ms,
        )

    def record_index_stage(
        self,
        entry_id: str | None = None,
        entry_name: str = "",
        registry_type: str = "",
        correlation_id: str = "",
        warnings: list[str] | None = None,
        errors: list[str] | None = None,
        success: bool = True,
        duration_ms: float | None = None,
    ) -> TraceRecord:
        return self.record_stage(
            stage_name="index",
            operation="index",
            entry_id=entry_id,
            entry_name=entry_name,
            registry_type=registry_type,
            correlation_id=correlation_id,
            warnings=warnings,
            errors=errors,
            success=success,
            duration_ms=duration_ms,
        )

    def record_version_stage(
        self,
        entry_id: str | None = None,
        entry_name: str = "",
        version: str = "",
        registry_type: str = "",
        correlation_id: str = "",
        warnings: list[str] | None = None,
        errors: list[str] | None = None,
        success: bool = True,
        duration_ms: float | None = None,
    ) -> TraceRecord:
        return self.record_stage(
            stage_name="version",
            operation="version",
            entry_id=entry_id,
            entry_name=entry_name,
            registry_type=registry_type,
            namespace=version,
            correlation_id=correlation_id,
            warnings=warnings,
            errors=errors,
            success=success,
            duration_ms=duration_ms,
        )

    def record_lifecycle_stage(
        self,
        entry_id: str | None = None,
        entry_name: str = "",
        lifecycle_transition: str = "",
        registry_type: str = "",
        correlation_id: str = "",
        warnings: list[str] | None = None,
        errors: list[str] | None = None,
        success: bool = True,
        duration_ms: float | None = None,
    ) -> TraceRecord:
        return self.record_stage(
            stage_name="lifecycle",
            operation="transition",
            entry_id=entry_id,
            entry_name=entry_name,
            registry_type=registry_type,
            namespace=lifecycle_transition,
            correlation_id=correlation_id,
            warnings=warnings,
            errors=errors,
            success=success,
            duration_ms=duration_ms,
        )

    # ── Phase 3.5: New dedicated stage methods ────────────────────

    def record_cache_stage(
        self,
        operation: str = "cache",
        entry_id: str | None = None,
        registry_type: str = "",
        correlation_id: str = "",
        cache_hit: bool = False,
        warnings: list[str] | None = None,
        errors: list[str] | None = None,
        duration_ms: float | None = None,
    ) -> TraceRecord:
        """Record a cache stage trace span."""
        return self.record_stage(
            stage_name="cache",
            operation=operation,
            entry_id=entry_id,
            registry_type=registry_type,
            correlation_id=correlation_id,
            warnings=warnings,
            errors=errors,
            success=True,
            duration_ms=duration_ms,
            namespace="hit" if cache_hit else "miss",
        )

    def record_audit_stage(
        self,
        operation: str = "audit",
        entry_id: str | None = None,
        entry_name: str = "",
        registry_type: str = "",
        correlation_id: str = "",
        warnings: list[str] | None = None,
        errors: list[str] | None = None,
        success: bool = True,
        duration_ms: float | None = None,
    ) -> TraceRecord:
        """Record an audit stage trace span."""
        return self.record_stage(
            stage_name="audit",
            operation=operation,
            entry_id=entry_id,
            entry_name=entry_name,
            registry_type=registry_type,
            correlation_id=correlation_id,
            warnings=warnings,
            errors=errors,
            success=success,
            duration_ms=duration_ms,
        )

    def record_policy_stage(
        self,
        operation: str = "policy",
        entry_id: str | None = None,
        entry_name: str = "",
        registry_type: str = "",
        correlation_id: str = "",
        violations: list[str] | None = None,
        warnings: list[str] | None = None,
        errors: list[str] | None = None,
        duration_ms: float | None = None,
    ) -> TraceRecord:
        """Record a policy engine stage trace span."""
        return self.record_stage(
            stage_name="policy",
            operation=operation,
            entry_id=entry_id,
            entry_name=entry_name,
            registry_type=registry_type,
            correlation_id=correlation_id,
            warnings=warnings,
            errors=violations or errors or [],
            success=len(violations or []) == 0,
            duration_ms=duration_ms,
        )

    def record_dependency_stage(
        self,
        operation: str = "dependency",
        entry_id: str | None = None,
        entry_name: str = "",
        registry_type: str = "",
        correlation_id: str = "",
        has_cycles: bool = False,
        warnings: list[str] | None = None,
        errors: list[str] | None = None,
        duration_ms: float | None = None,
    ) -> TraceRecord:
        """Record a dependency resolution stage trace span."""
        return self.record_stage(
            stage_name="dependency",
            operation=operation,
            entry_id=entry_id,
            entry_name=entry_name,
            registry_type=registry_type,
            correlation_id=correlation_id,
            warnings=warnings,
            errors=errors,
            success=not has_cycles,
            duration_ms=duration_ms,
            namespace="cycle_detected" if has_cycles else "ok",
        )

    def record_metrics_stage(
        self,
        operation: str = "metrics",
        registry_type: str = "",
        correlation_id: str = "",
        warnings: list[str] | None = None,
        errors: list[str] | None = None,
        duration_ms: float | None = None,
    ) -> TraceRecord:
        """Record a metrics aggregation stage trace span."""
        return self.record_stage(
            stage_name="metrics",
            operation=operation,
            registry_type=registry_type,
            correlation_id=correlation_id,
            warnings=warnings,
            errors=errors,
            success=True,
            duration_ms=duration_ms,
        )

    # ── Query methods ─────────────────────────────────────────────

    def get_by_trace_id(self, trace_id: str) -> list[TraceRecord]:
        return [t for t in self._traces if str(t.trace_id) == trace_id]

    def get_by_operation(self, operation: str) -> list[TraceRecord]:
        return [t for t in self._traces if t.operation == operation]

    def get_by_stage(self, stage_name: str) -> list[TraceRecord]:
        return [t for t in self._traces if t.stage_name == stage_name]

    def get_by_entry_id(self, entry_id: str) -> list[TraceRecord]:
        return [t for t in self._traces if t.entry_id == entry_id]

    def get_recent(self, limit: int = 50) -> list[TraceRecord]:
        return sorted(self._traces, key=lambda t: t.started_at, reverse=True)[:limit]

    def clear(self) -> None:
        self._traces.clear()

    def count(self) -> int:
        return len(self._traces)
