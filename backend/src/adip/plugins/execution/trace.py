"""PluginTrace — distributed tracing for plugin operations.

Records trace spans for discovery, validation, dependency resolution,
compatibility checks, sandbox creation, initialisation, activation,
and other pipeline stages with timing and structured metadata.
"""

from __future__ import annotations

from datetime import UTC, datetime

import structlog

from adip.plugins.execution.models import TraceRecord

log = structlog.get_logger(__name__)


class PluginTrace:
    """Manages trace records for plugin pipeline observability.

    Supports per-stage tracing for discovery, validation, dependency
    resolution, compatibility checks, sandbox creation, initialisation,
    activation, and other operations.
    """

    def __init__(self) -> None:
        self._traces: list[TraceRecord] = []

    def record(self, trace: TraceRecord) -> None:
        """Record a trace."""
        log.info("plugin_trace.record", trace_id=str(trace.trace_id), operation=trace.operation)
        self._traces.append(trace)

    def record_stage(
        self,
        stage_name: str,
        operation: str,
        plugin_id: str | None = None,
        plugin_version: str = "",
        manifest_version: str = "",
        domain: str = "",
        sandbox_id: str = "",
        lifecycle_state: str = "",
        correlation_id: str = "",
        warnings: list[str] | None = None,
        errors: list[str] | None = None,
        success: bool = True,
        duration_ms: float | None = None,
    ) -> TraceRecord:
        """Create and record a trace for a pipeline stage.

        Tracks the full range of stages: discovery, validation,
        dependency_resolution, compatibility_check, sandbox_creation,
        initialisation, activation, and others.
        """
        record = TraceRecord(
            stage_name=stage_name,
            operation=operation,
            plugin_id=plugin_id,
            plugin_version=plugin_version,
            manifest_version=manifest_version,
            domain=domain,
            sandbox_id=sandbox_id,
            lifecycle_state=lifecycle_state,
            completed_at=datetime.now(UTC),
            duration_ms=duration_ms,
            warnings=warnings or [],
            errors=errors or [],
            success=success,
            correlation_id=correlation_id,
        )
        self.record(record)
        return record

    def record_discovery_stage(
        self,
        domain: str = "",
        correlation_id: str = "",
        warnings: list[str] | None = None,
        errors: list[str] | None = None,
        success: bool = True,
        duration_ms: float | None = None,
    ) -> TraceRecord:
        """Record a discovery stage trace."""
        return self.record_stage(
            stage_name="discovery",
            operation="discover",
            domain=domain,
            correlation_id=correlation_id,
            warnings=warnings,
            errors=errors,
            success=success,
            duration_ms=duration_ms,
        )

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

    def record_dependency_resolution_stage(
        self,
        plugin_id: str | None = None,
        domain: str = "",
        correlation_id: str = "",
        warnings: list[str] | None = None,
        errors: list[str] | None = None,
        success: bool = True,
        duration_ms: float | None = None,
    ) -> TraceRecord:
        """Record a dependency resolution stage trace."""
        return self.record_stage(
            stage_name="dependency_resolution",
            operation="resolve_dependencies",
            plugin_id=plugin_id,
            domain=domain,
            correlation_id=correlation_id,
            warnings=warnings,
            errors=errors,
            success=success,
            duration_ms=duration_ms,
        )

    def record_compatibility_stage(
        self,
        plugin_id: str | None = None,
        domain: str = "",
        correlation_id: str = "",
        warnings: list[str] | None = None,
        errors: list[str] | None = None,
        success: bool = True,
        duration_ms: float | None = None,
    ) -> TraceRecord:
        """Record a compatibility check stage trace."""
        return self.record_stage(
            stage_name="compatibility_check",
            operation="check_compatibility",
            plugin_id=plugin_id,
            domain=domain,
            correlation_id=correlation_id,
            warnings=warnings,
            errors=errors,
            success=success,
            duration_ms=duration_ms,
        )

    def record_sandbox_stage(
        self,
        sandbox_id: str = "",
        plugin_id: str | None = None,
        domain: str = "",
        correlation_id: str = "",
        warnings: list[str] | None = None,
        errors: list[str] | None = None,
        success: bool = True,
        duration_ms: float | None = None,
    ) -> TraceRecord:
        """Record a sandbox creation stage trace."""
        return self.record_stage(
            stage_name="sandbox_creation",
            operation="create_sandbox",
            sandbox_id=sandbox_id,
            plugin_id=plugin_id,
            domain=domain,
            correlation_id=correlation_id,
            warnings=warnings,
            errors=errors,
            success=success,
            duration_ms=duration_ms,
        )

    def record_initialization_stage(
        self,
        plugin_id: str | None = None,
        domain: str = "",
        correlation_id: str = "",
        warnings: list[str] | None = None,
        errors: list[str] | None = None,
        success: bool = True,
        duration_ms: float | None = None,
    ) -> TraceRecord:
        """Record an initialisation stage trace."""
        return self.record_stage(
            stage_name="initialization",
            operation="initialize",
            plugin_id=plugin_id,
            domain=domain,
            correlation_id=correlation_id,
            warnings=warnings,
            errors=errors,
            success=success,
            duration_ms=duration_ms,
        )

    def record_registration_stage(
        self,
        plugin_id: str | None = None,
        domain: str = "",
        correlation_id: str = "",
        warnings: list[str] | None = None,
        errors: list[str] | None = None,
        success: bool = True,
        duration_ms: float | None = None,
    ) -> TraceRecord:
        """Record a capability registration stage trace."""
        return self.record_stage(
            stage_name="registration",
            operation="register_capabilities",
            plugin_id=plugin_id,
            domain=domain,
            correlation_id=correlation_id,
            warnings=warnings,
            errors=errors,
            success=success,
            duration_ms=duration_ms,
        )

    def record_activation_stage(
        self,
        plugin_id: str | None = None,
        domain: str = "",
        correlation_id: str = "",
        warnings: list[str] | None = None,
        errors: list[str] | None = None,
        success: bool = True,
        duration_ms: float | None = None,
    ) -> TraceRecord:
        """Record an activation stage trace."""
        return self.record_stage(
            stage_name="activation",
            operation="activate",
            plugin_id=plugin_id,
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

    def get_by_plugin_id(self, plugin_id: str) -> list[TraceRecord]:
        """Get all trace records for a given plugin ID."""
        return [t for t in self._traces if t.plugin_id == plugin_id]

    def get_recent(self, limit: int = 50) -> list[TraceRecord]:
        """Get the most recent trace records."""
        return sorted(self._traces, key=lambda t: t.started_at, reverse=True)[:limit]

    def clear(self) -> None:
        """Clear all trace records."""
        self._traces.clear()

    def count(self) -> int:
        """Return the total number of trace records."""
        return len(self._traces)
