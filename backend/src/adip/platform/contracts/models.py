"""Platform Integration domain models.

Defines the core data contracts for the platform integration layer
including the service registry, pipeline context, health aggregation,
trace records, metrics snapshots, and platform manifest.

All models are Pydantic v2 BaseModel subclasses with full type
annotations, validation, and documentation.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import UUID4, BaseModel, Field

from adip.platform.enums import ModuleHealthStatus, ModuleName, PipelineStage, PipelineStatus


class PlatformRequest(BaseModel):
    """An incoming platform request for pipeline processing.

    Carries the correlation ID, input data, and metadata through
    the entire end-to-end pipeline.
    """

    request_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique request identifier",
    )
    correlation_id: str = Field(
        default="",
        description="Correlation ID for distributed tracing",
    )
    pipeline: list[PipelineStage] = Field(
        default_factory=list,
        description="Pipeline stages to execute (empty = all)",
    )
    payload: dict[str, Any] = Field(
        default_factory=dict,
        description="Input payload for the pipeline",
    )
    context: dict[str, Any] = Field(
        default_factory=dict,
        description="Pipeline context propagated between stages",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional request metadata",
    )


class PlatformResponse(BaseModel):
    """The result of a platform pipeline execution."""

    request_id: UUID4 = Field(
        description="The original request identifier",
    )
    correlation_id: str = Field(
        default="",
        description="Correlation ID from the request",
    )
    success: bool = Field(
        default=False,
        description="Whether the pipeline completed successfully",
    )
    status: PipelineStatus = Field(
        default=PipelineStatus.PENDING,
        description="Final pipeline status",
    )
    stages_completed: list[PipelineStage] = Field(
        default_factory=list,
        description="Stages that completed successfully",
    )
    stages_failed: list[PipelineStage] = Field(
        default_factory=list,
        description="Stages that failed",
    )
    output: dict[str, Any] = Field(
        default_factory=dict,
        description="Pipeline output data",
    )
    errors: list[str] = Field(
        default_factory=list,
        description="Error messages from failed stages",
    )
    duration_ms: float = Field(
        default=0.0,
        ge=0.0,
        description="Total pipeline execution time in milliseconds",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the response was generated",
    )


class ModuleHealth(BaseModel):
    """Health status of a single platform module."""

    module: ModuleName = Field(
        description="The module name",
    )
    status: ModuleHealthStatus = Field(
        default=ModuleHealthStatus.UNKNOWN,
        description="Health status of the module",
    )
    is_registered: bool = Field(
        default=False,
        description="Whether the module is registered in the platform",
    )
    version: str = Field(
        default="",
        description="Module version string",
    )
    last_checked: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the health was last checked",
    )
    message: str = Field(
        default="",
        description="Optional health status message",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional module health metadata",
    )


class PlatformHealth(BaseModel):
    """Aggregated health status of the entire platform."""

    overall_status: ModuleHealthStatus = Field(
        default=ModuleHealthStatus.UNKNOWN,
        description="Overall platform health status",
    )
    modules: dict[str, ModuleHealth] = Field(
        default_factory=dict,
        description="Per-module health statuses keyed by module name",
    )
    healthy_count: int = Field(
        default=0,
        ge=0,
        description="Number of healthy modules",
    )
    degraded_count: int = Field(
        default=0,
        ge=0,
        description="Number of degraded modules",
    )
    unhealthy_count: int = Field(
        default=0,
        ge=0,
        description="Number of unhealthy modules",
    )
    total_modules: int = Field(
        default=0,
        ge=0,
        description="Total number of registered modules",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the health report was generated",
    )


class PlatformTraceEntry(BaseModel):
    """A single trace entry in the platform trace log."""

    stage: PipelineStage = Field(
        description="The pipeline stage",
    )
    module: str = Field(
        default="",
        description="The module that produced this entry",
    )
    status: str = Field(
        default="success",
        description="Status of this stage (success, failure, skipped)",
    )
    duration_ms: float = Field(
        default=0.0,
        ge=0.0,
        description="Duration of this stage in milliseconds",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the entry was recorded",
    )
    details: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional trace details",
    )


class PlatformTrace(BaseModel):
    """A complete trace for a single pipeline execution."""

    trace_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique trace identifier",
    )
    correlation_id: str = Field(
        default="",
        description="Correlation ID for distributed tracing",
    )
    entries: list[PlatformTraceEntry] = Field(
        default_factory=list,
        description="Trace entries for each pipeline stage",
    )
    total_duration_ms: float = Field(
        default=0.0,
        ge=0.0,
        description="Total trace duration in milliseconds",
    )
    completed: bool = Field(
        default=False,
        description="Whether the trace is complete",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the trace was created",
    )


class PlatformMetrics(BaseModel):
    """Aggregated platform-wide metrics snapshot."""

    total_requests: int = Field(
        default=0,
        ge=0,
        description="Total number of pipeline requests",
    )
    successful_requests: int = Field(
        default=0,
        ge=0,
        description="Number of successful pipeline executions",
    )
    failed_requests: int = Field(
        default=0,
        ge=0,
        description="Number of failed pipeline executions",
    )
    partial_requests: int = Field(
        default=0,
        ge=0,
        description="Number of partially successful executions",
    )
    average_duration_ms: float = Field(
        default=0.0,
        ge=0.0,
        description="Average pipeline duration in milliseconds",
    )
    total_duration_ms: float = Field(
        default=0.0,
        ge=0.0,
        description="Total accumulated pipeline duration",
    )
    per_stage_counts: dict[str, int] = Field(
        default_factory=dict,
        description="Number of executions per pipeline stage",
    )
    per_stage_errors: dict[str, int] = Field(
        default_factory=dict,
        description="Number of errors per pipeline stage",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the metrics snapshot was taken",
    )


class ServiceDescriptor(BaseModel):
    """Descriptor for a registered service in the platform."""

    name: str = Field(
        description="Service name",
    )
    module: ModuleName = Field(
        description="The module this service belongs to",
    )
    service_type: str = Field(
        default="",
        description="Type of service (service, manager, coordinator)",
    )
    version: str = Field(
        default="1.0.0",
        description="Service version",
    )
    dependencies: list[str] = Field(
        default_factory=list,
        description="Names of services this service depends on",
    )


class PlatformManifest(BaseModel):
    """Platform manifest describing all wired services and modules."""

    platform_version: str = Field(
        default="1.0.0",
        description="Platform integration version",
    )
    generated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the manifest was generated",
    )
    modules: list[dict[str, Any]] = Field(
        default_factory=list,
        description="List of registered modules with their services",
    )
    services: list[ServiceDescriptor] = Field(
        default_factory=list,
        description="All registered service descriptors",
    )
    total_services: int = Field(
        default=0,
        ge=0,
        description="Total number of registered services",
    )
    total_modules: int = Field(
        default=0,
        ge=0,
        description="Total number of registered modules",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional manifest metadata",
    )


class SharedContext(BaseModel):
    """Cross-module shared context propagated through the entire pipeline.

    Carries the correlation ID, trace ID, request metadata, domain-
    specific context, execution context, module session IDs, and
    per-module results so that every stage has visibility into what
    previous stages produced.
    """

    correlation_id: str = Field(
        default="",
        description="Correlation ID for distributed tracing",
    )
    trace_id: str = Field(
        default="",
        description="Trace ID for the current pipeline execution",
    )
    request_metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Request-level metadata (source, auth, etc.)",
    )
    domain_context: dict[str, Any] = Field(
        default_factory=dict,
        description="Domain-specific context (energy domain, etc.)",
    )
    execution_context: dict[str, Any] = Field(
        default_factory=dict,
        description="Execution-specific context (environment, flags, etc.)",
    )
    session_ids: dict[str, str] = Field(
        default_factory=dict,
        description="Mapping of module name to its session ID",
    )
    module_results: dict[str, Any] = Field(
        default_factory=dict,
        description="Results produced by each module during pipeline execution",
    )


# ──────────────────────────────────────────────────────────────────────
# Phase 3 – Platform Validation & Orchestration
# ──────────────────────────────────────────────────────────────────────


class PlatformValidationResult(BaseModel):
    """Result of platform validation across all checks."""

    platform_valid: bool = Field(default=False, description="Overall platform validity")
    bootstrap_valid: bool = Field(default=False, description="Whether bootstrap validation passed")
    contracts_valid: bool = Field(default=False, description="Whether all cross-module contracts validated")
    diagnostics_valid: bool = Field(default=False, description="Whether diagnostics passed")
    health_status: str = Field(default="unknown", description="Aggregated health status string")
    message: str = Field(default="", description="Human-readable validation message")
    details: dict[str, Any] = Field(default_factory=dict, description="Per-check details")


class PlatformCompatibilityReport(BaseModel):
    """Compatibility assessment across platform domains."""

    platform: str = Field(default="UNKNOWN", description="Platform-level compatibility status")
    rest_api: str = Field(default="UNKNOWN", description="REST API compatibility status")
    energy_domain: str = Field(default="UNKNOWN", description="Energy Domain compatibility status")
    pairs_validated: int = Field(default=0, ge=0, description="Number of adjacent pairs validated")
    pairs_ok: int = Field(default=0, ge=0, description="Number of compatible pairs")
    pairs_skipped: int = Field(default=0, ge=0, description="Number of skipped pairs")
    pairs_error: int = Field(default=0, ge=0, description="Number of incompatible pairs")
    messages: list[str] = Field(default_factory=list, description="Compatibility messages")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Report generation time")


class PlatformDiagnosticsResult(BaseModel):
    """Diagnostics result for the full platform."""

    all_valid: bool = Field(default=True, description="Whether all diagnostics passed")
    service_count: int = Field(default=0, ge=0, description="Total registered services")
    module_count: int = Field(default=0, ge=0, description="Total registered modules")
    missing_services: list[str] = Field(default_factory=list, description="Services expected but not registered")
    circular_dependencies: list[list[str]] = Field(default_factory=list, description="Detected circular dependency chains")
    invalid_registrations: list[str] = Field(default_factory=list, description="Services with invalid registrations")
    broken_pipelines: list[str] = Field(default_factory=list, description="Pipeline stages with unresolvable services")
    missing_exports: list[str] = Field(default_factory=list, description="Module exports expected but missing")
    invalid_imports: list[str] = Field(default_factory=list, description="Module imports that reference unregistered services")
    contract_violations: list[str] = Field(default_factory=list, description="Cross-module contract violations")
    warnings: list[str] = Field(default_factory=list, description="Diagnostic warnings")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Diagnostics run time")


class PlatformVersionRecord(BaseModel):
    """Version record for a platform module."""

    module: str = Field(description="Module name")
    version: str = Field(default="1.0.0", description="Current module version")
    last_validated: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Last validation timestamp")
    status: str = Field(default="active", description="Module status (active, deprecated, beta)")


class IntegrationAuditPackage(BaseModel):
    """Immutable audit package capturing a complete platform validation snapshot."""

    audit_id: str = Field(description="Unique audit identifier")
    version: str = Field(default="1.0.0", description="Audit package version")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Package creation time")
    validation: PlatformValidationResult = Field(description="Platform validation result")
    compatibility: PlatformCompatibilityReport = Field(description="Compatibility report")
    diagnostics: PlatformDiagnosticsResult = Field(description="Diagnostics result")
    health: PlatformHealth = Field(description="Platform health snapshot")
    manifest: PlatformManifest = Field(description="Platform manifest")
    quality: PlatformQualityResult | None = Field(default=None, description="Platform quality assessment")
    compliance: PlatformComplianceResult | None = Field(default=None, description="Platform compliance assessment")
    readiness: PlatformReadinessReport | None = Field(default=None, description="Platform readiness report")
    checksum: str = Field(default="", description="Simple content hash for integrity verification")


# ──────────────────────────────────────────────────────────────────────
# Phase 3.5 – Enterprise Refinement & Platform Freeze
# ──────────────────────────────────────────────────────────────────────


class PlatformQualityResult(BaseModel):
    """Quality assessment for the platform."""

    architecture_completeness: float = Field(default=0.0, ge=0.0, le=1.0, description="Architecture completeness score")
    integration_completeness: float = Field(default=0.0, ge=0.0, le=1.0, description="Integration completeness score")
    documentation_completeness: float = Field(default=0.0, ge=0.0, le=1.0, description="Documentation completeness score")
    test_coverage: float = Field(default=0.0, ge=0.0, le=1.0, description="Test coverage estimate")
    overall_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Overall quality score")
    messages: list[str] = Field(default_factory=list, description="Quality evaluation messages")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC), description="When the assessment was run")


class PlatformComplianceResult(BaseModel):
    """Compliance validation result."""

    solid_principles: bool = Field(default=False, description="SOLID principles compliance")
    clean_architecture: bool = Field(default=False, description="Clean Architecture compliance")
    layer_isolation: bool = Field(default=False, description="Layer isolation compliance")
    dependency_rules: bool = Field(default=False, description="Dependency injection rules compliance")
    naming_conventions: bool = Field(default=False, description="Naming conventions compliance")
    overall_compliant: bool = Field(default=False, description="Overall compliance status")
    messages: list[str] = Field(default_factory=list, description="Compliance evaluation messages")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC), description="When compliance was checked")


class PlatformReadinessReport(BaseModel):
    """Readiness assessment for the platform."""

    bootstrap_status: str = Field(default="unknown", description="Bootstrap validation status")
    health_status: str = Field(default="unknown", description="Overall health status")
    compatibility_status: str = Field(default="unknown", description="Compatibility status")
    version: str = Field(default="1.0.0", description="Platform version")
    build_metadata: dict[str, str] = Field(default_factory=dict, description="Build metadata key-value pairs")
    overall_ready: bool = Field(default=False, description="Whether the platform is deemed ready")
    messages: list[str] = Field(default_factory=list, description="Readiness report messages")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Report generation time")


class PlatformSnapshot(BaseModel):
    """Immutable platform snapshot capturing the full runtime state."""

    snapshot_id: str = Field(description="Unique snapshot identifier")
    version: str = Field(default="1.0.0", description="Snapshot version")
    services: list[ServiceDescriptor] = Field(default_factory=list, description="All service descriptors")
    managers: list[str] = Field(default_factory=list, description="Registered manager names")
    coordinators: list[str] = Field(default_factory=list, description="Registered coordinator names")
    registry: dict[str, Any] = Field(default_factory=dict, description="Registry state overview")
    versions: dict[str, str] = Field(default_factory=dict, description="Module versions snapshot")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Snapshot creation time")


class PipelineVersionRecord(BaseModel):
    """Version record for the full platform pipeline."""

    pipeline_version: str = Field(description="Pipeline version identifier")
    platform_version: str = Field(default="1.0.0", description="Platform version at creation")
    is_active: bool = Field(default=False, description="Whether this is the active pipeline version")
    stage_count: int = Field(default=0, ge=0, description="Number of pipeline stages")
    modules: list[str] = Field(default_factory=list, description="Modules included in this version")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Version creation time")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional version metadata")


class DocumentationMetadata(BaseModel):
    """Metadata describing platform documentation coverage."""

    modules: dict[str, str] = Field(default_factory=dict, description="Module → doc status map")
    services: dict[str, str] = Field(default_factory=dict, description="Service → doc status map")
    apis: dict[str, str] = Field(default_factory=dict, description="API → doc status map")
    dependencies: dict[str, str] = Field(default_factory=dict, description="Dependency → doc status map")
    domains: dict[str, str] = Field(default_factory=dict, description="Domain → doc status map")
    total_documented: int = Field(default=0, ge=0, description="Total documented items")
    total_items: int = Field(default=0, ge=0, description="Total items requiring documentation")
    coverage_pct: float = Field(default=0.0, ge=0.0, le=1.0, description="Documentation coverage percentage")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Metadata generation time")


class PlatformExportPackage(BaseModel):
    """Exportable platform snapshot for release packaging."""

    manifest: PlatformManifest = Field(description="Platform manifest")
    architecture_report: dict[str, Any] = Field(default_factory=dict, description="Architecture report data")
    compatibility_report: PlatformCompatibilityReport = Field(description="Compatibility report")
    api_inventory: dict[str, Any] = Field(default_factory=dict, description="API inventory data")
    module_inventory: dict[str, Any] = Field(default_factory=dict, description="Module inventory data")
    quality: PlatformQualityResult | None = Field(default=None, description="Quality assessment")
    compliance: PlatformComplianceResult | None = Field(default=None, description="Compliance assessment")
    readiness: PlatformReadinessReport | None = Field(default=None, description="Readiness report")
    exported_at: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Export timestamp")


class PlatformReleaseChecklist(BaseModel):
    """Release checklist validation result."""

    services_registered: bool = Field(default=False, description="All services registered")
    imports_valid: bool = Field(default=False, description="All imports valid")
    tests_passing: bool = Field(default=False, description="All tests passing")
    routers_registered: bool = Field(default=False, description="All routers registered")
    no_circular_dependencies: bool = Field(default=False, description="No circular dependencies detected")
    platform_ready: bool = Field(default=False, description="Platform deemed ready for release")
    messages: list[str] = Field(default_factory=list, description="Checklist evaluation messages")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Checklist validation time")
