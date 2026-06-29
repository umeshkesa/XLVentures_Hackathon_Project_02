"""Abstract interfaces for the Platform Integration module.

All interfaces follow dependency inversion — consumers depend on
abstractions, not concrete implementations.

Architecture:
    PlatformService  →  PlatformManager  →  PlatformCoordinator
                                                ├── ServiceRegistry
                                                ├── HealthAggregator
                                                ├── TraceManager
                                                ├── MetricsCollector
                                                ├── ExceptionMapper
                                                └── ManifestBuilder
"""

from __future__ import annotations

import abc
from typing import Any

from adip.platform.contracts.models import (
    DocumentationMetadata,
    IntegrationAuditPackage,
    PipelineVersionRecord,
    PlatformCompatibilityReport,
    PlatformComplianceResult,
    PlatformDiagnosticsResult,
    PlatformExportPackage,
    PlatformHealth,
    PlatformManifest,
    PlatformMetrics,
    PlatformQualityResult,
    PlatformReadinessReport,
    PlatformReleaseChecklist,
    PlatformRequest,
    PlatformResponse,
    PlatformSnapshot,
    PlatformTrace,
    PlatformValidationResult,
    PlatformVersionRecord,
    ServiceDescriptor,
    SharedContext,
)
from adip.platform.enums import ModuleName, PipelineStage


class PlatformService(abc.ABC):
    """Enterprise facade for platform operations.

    External modules interact with this facade rather than with
    PlatformManager directly.
    """

    @abc.abstractmethod
    async def execute_pipeline(self, request: PlatformRequest) -> PlatformResponse:
        """Execute the end-to-end platform pipeline."""
        ...

    @abc.abstractmethod
    async def get_health(self) -> PlatformHealth:
        """Get aggregated platform health."""
        ...

    @abc.abstractmethod
    async def get_metrics(self) -> PlatformMetrics:
        """Get aggregated platform metrics."""
        ...

    @abc.abstractmethod
    async def get_manifest(self) -> PlatformManifest:
        """Get the platform manifest."""
        ...

    @abc.abstractmethod
    async def get_trace(self, trace_id: str) -> PlatformTrace | None:
        """Get a specific trace by ID."""
        ...

    @abc.abstractmethod
    async def list_traces(self) -> list[PlatformTrace]:
        """List all platform traces."""
        ...


class PlatformManager(abc.ABC):
    """Internal orchestrator for platform operations.

    Coordinates the PlatformCoordinator and enforces platform policies
    before delegating to the coordinator.
    """

    @abc.abstractmethod
    async def execute_pipeline(self, request: PlatformRequest) -> PlatformResponse:
        """Execute the end-to-end platform pipeline."""
        ...

    @abc.abstractmethod
    async def get_health(self) -> PlatformHealth:
        """Get aggregated platform health."""
        ...

    @abc.abstractmethod
    async def get_metrics(self) -> PlatformMetrics:
        """Get aggregated platform metrics."""
        ...

    @abc.abstractmethod
    async def get_manifest(self) -> PlatformManifest:
        """Get the platform manifest."""
        ...


class PlatformCoordinator(abc.ABC):
    """Coordinates all platform sub-components.

    Orchestrates the pipeline execution by delegating to the
    service registry, health aggregator, trace manager, metrics
    collector, exception mapper, and manifest builder.
    """

    @abc.abstractmethod
    async def execute_pipeline(self, request: PlatformRequest) -> PlatformResponse:
        """Coordinate the full pipeline execution."""
        ...

    @abc.abstractmethod
    async def get_health(self) -> PlatformHealth:
        """Coordinate health aggregation."""
        ...

    @abc.abstractmethod
    async def get_metrics(self) -> PlatformMetrics:
        """Coordinate metrics collection."""
        ...

    @abc.abstractmethod
    async def get_manifest(self) -> PlatformManifest:
        """Coordinate manifest generation."""
        ...


class ServiceRegistry(abc.ABC):
    """Registry for all platform module services.

    Provides DI-style service resolution and lifecycle management.
    """

    @abc.abstractmethod
    def register(self, name: str, service: Any, module: ModuleName) -> None:
        """Register a service in the platform registry."""
        ...

    @abc.abstractmethod
    def resolve(self, name: str) -> Any:
        """Resolve a service by name from the registry."""
        ...

    @abc.abstractmethod
    def resolve_all(self) -> dict[str, Any]:
        """Resolve all registered services."""
        ...

    @abc.abstractmethod
    def get_service_descriptors(self) -> list[ServiceDescriptor]:
        """Get descriptors for all registered services."""
        ...

    @abc.abstractmethod
    def get_modules(self) -> list[dict[str, Any]]:
        """Get list of registered modules with their services."""
        ...

    @abc.abstractmethod
    def has_module(self, module: ModuleName) -> bool:
        """Check if a module is registered."""
        ...

    @abc.abstractmethod
    def clear(self) -> None:
        """Clear all registered services."""
        ...


class HealthAggregator(abc.ABC):
    """Aggregates health status across all platform modules."""

    @abc.abstractmethod
    def aggregate(self, registry: ServiceRegistry) -> PlatformHealth:
        """Aggregate health from all registered modules."""
        ...


class TraceManager(abc.ABC):
    """Unified tracing across all platform modules."""

    @abc.abstractmethod
    def create_trace(self, correlation_id: str) -> PlatformTrace:
        """Create a new trace for a pipeline execution."""
        ...

    @abc.abstractmethod
    def record_stage(
        self,
        trace_id: str,
        stage: PipelineStage,
        module: str,
        status: str,
        duration_ms: float,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Record a stage execution in a trace."""
        ...

    @abc.abstractmethod
    def complete_trace(self, trace_id: str, total_duration_ms: float) -> None:
        """Mark a trace as completed."""
        ...

    @abc.abstractmethod
    def get_trace(self, trace_id: str) -> PlatformTrace | None:
        """Get a trace by ID."""
        ...

    @abc.abstractmethod
    def list_traces(self) -> list[PlatformTrace]:
        """List all traces."""
        ...

    @abc.abstractmethod
    def clear(self) -> None:
        """Clear all traces."""
        ...


class PlatformMetricsCollector(abc.ABC):
    """Unified metrics collection across the platform."""

    @abc.abstractmethod
    def record_request(self, success: bool, duration_ms: float, stages: list[PipelineStage]) -> None:
        """Record a pipeline request execution."""
        ...

    @abc.abstractmethod
    def record_stage_error(self, stage: PipelineStage) -> None:
        """Record a stage error."""
        ...

    @abc.abstractmethod
    def get_snapshot(self) -> PlatformMetrics:
        """Get a snapshot of current metrics."""
        ...

    @abc.abstractmethod
    def reset(self) -> None:
        """Reset all metrics."""
        ...


class ExceptionMapper(abc.ABC):
    """Standard exception propagation across the platform."""

    @abc.abstractmethod
    def map_exception(self, exc: Exception, stage: PipelineStage) -> str:
        """Map an exception to a standard error message for the pipeline response."""
        ...

    @abc.abstractmethod
    def is_known_exception(self, exc: Exception) -> bool:
        """Check if an exception is a known platform exception."""
        ...


class ManifestBuilder(abc.ABC):
    """Builds the platform manifest."""

    @abc.abstractmethod
    def build(self, registry: ServiceRegistry) -> PlatformManifest:
        """Build the platform manifest from the service registry."""
        ...


# ──────────────────────────────────────────────────────────────────────
# Phase 2 – Shared Context & Cross-Module Integration
# ──────────────────────────────────────────────────────────────────────


class ContextManager(abc.ABC):
    """Manages the shared context that propagates across all modules."""

    @abc.abstractmethod
    def create_context(
        self,
        correlation_id: str,
        trace_id: str,
        metadata: dict[str, Any] | None = None,
    ) -> SharedContext:
        """Create a new shared context for a pipeline execution."""
        ...

    @abc.abstractmethod
    def update_context(self, context: SharedContext, **updates: Any) -> SharedContext:
        """Return a new context with the given updates applied."""
        ...

    @abc.abstractmethod
    def get_module_result(self, context: SharedContext, module: str) -> Any:
        """Get the result produced by a specific module."""
        ...

    @abc.abstractmethod
    def set_module_result(self, context: SharedContext, module: str, result: Any) -> SharedContext:
        """Set the result for a specific module and return updated context."""
        ...


class PlatformBootstrap(abc.ABC):
    """Initialises and wires all platform modules into a working instance."""

    @abc.abstractmethod
    async def initialize(self) -> PlatformService:
        """Create, wire, and return the fully-configured PlatformService."""
        ...

    @abc.abstractmethod
    async def get_service(self) -> PlatformService:
        """Return the already-initialised PlatformService."""
        ...


class CompatibilityValidator(abc.ABC):
    """Verifies contracts between adjacent platform modules."""

    @abc.abstractmethod
    def validate_adjacent(
        self, upstream: ModuleName, downstream: ModuleName, registry: ServiceRegistry
    ) -> str:
        """Validate that *upstream* output is consumable by *downstream*."""
        ...

    @abc.abstractmethod
    def validate_all(self, registry: ServiceRegistry) -> list[str]:
        """Validate all adjacent module pairs and return list of messages."""
        ...


class PipelineValidator(abc.ABC):
    """Validates the complete end-to-end pipeline."""

    @abc.abstractmethod
    async def validate_pipeline(
        self, coordinator: PlatformCoordinator, request: PlatformRequest
    ) -> PlatformResponse:
        """Execute the full pipeline and validate every stage completes."""
        ...

    @abc.abstractmethod
    def validate_stage_order(self, stages: list[PipelineStage]) -> bool:
        """Validate that stages appear in the correct processing order."""
        ...


# ──────────────────────────────────────────────────────────────────────
# Phase 3 – Platform Validation & Enterprise Orchestration
# ──────────────────────────────────────────────────────────────────────


class BootstrapValidator(abc.ABC):
    """Validates that the platform bootstrap completed successfully."""

    @abc.abstractmethod
    def validate(self, registry: ServiceRegistry) -> PlatformValidationResult:
        """Verify all services are registered and the platform is wired correctly."""
        ...


class CrossModuleContractValidator(abc.ABC):
    """Validates cross-module contracts across the full platform."""

    @abc.abstractmethod
    def validate_contract(
        self, upstream: ModuleName, downstream: ModuleName, registry: ServiceRegistry
    ) -> str:
        """Validate the contract between two adjacent modules."""
        ...

    @abc.abstractmethod
    def validate_all_contracts(self, registry: ServiceRegistry) -> PlatformCompatibilityReport:
        """Validate all cross-module contracts and return a compatibility report."""
        ...


class PlatformDiagnostics(abc.ABC):
    """Runs diagnostics on the platform to detect issues."""

    @abc.abstractmethod
    def run_diagnostics(self, registry: ServiceRegistry) -> PlatformDiagnosticsResult:
        """Run full diagnostics and return results."""
        ...


class PlatformCompatibilityReportGenerator(abc.ABC):
    """Generates compatibility reports for platform domains."""

    @abc.abstractmethod
    def generate_report(self, registry: ServiceRegistry) -> PlatformCompatibilityReport:
        """Generate a compatibility report covering all domains."""
        ...


class UnifiedHealth(abc.ABC):
    """Aggregates unified health across all platform modules."""

    @abc.abstractmethod
    def get_unified_health(self, registry: ServiceRegistry) -> PlatformHealth:
        """Return a unified health snapshot with per-module status."""
        ...


class PlatformManifestGenerator(abc.ABC):
    """Generates the platform manifest with full service metadata."""

    @abc.abstractmethod
    def generate_manifest(self, registry: ServiceRegistry) -> PlatformManifest:
        """Generate an immutable platform manifest."""
        ...


class IntegrationAuditPackageGenerator(abc.ABC):
    """Creates immutable audit packages capturing platform validation state."""

    @abc.abstractmethod
    def create_audit_package(
        self,
        validation: PlatformValidationResult,
        compatibility: PlatformCompatibilityReport,
        diagnostics: PlatformDiagnosticsResult,
        health: PlatformHealth,
        manifest: PlatformManifest,
        quality: PlatformQualityResult | None = None,
        compliance: PlatformComplianceResult | None = None,
        readiness: PlatformReadinessReport | None = None,
    ) -> IntegrationAuditPackage:
        """Create an immutable audit snapshot of the current platform state."""
        ...


class PlatformVersionManager(abc.ABC):
    """Manages version tracking for all platform modules."""

    @abc.abstractmethod
    def get_version(self, module: str) -> PlatformVersionRecord:
        """Get the version record for a specific module."""
        ...

    @abc.abstractmethod
    def list_versions(self) -> list[PlatformVersionRecord]:
        """List version records for all tracked modules."""
        ...

    @abc.abstractmethod
    def update_version(self, module: str, version: str) -> PlatformVersionRecord:
        """Update the version for a specific module and return the record."""
        ...


class PlatformIntegrationCoordinator(abc.ABC):
    """Coordinates all Phase 3 platform validation and orchestration components."""

    @abc.abstractmethod
    async def validate_platform(self) -> PlatformValidationResult:
        """Run full platform validation (bootstrap + contracts + diagnostics + health)."""
        ...

    @abc.abstractmethod
    async def get_compatibility_report(self) -> PlatformCompatibilityReport:
        """Generate a platform-wide compatibility report."""
        ...

    @abc.abstractmethod
    async def run_diagnostics(self) -> PlatformDiagnosticsResult:
        """Run platform diagnostics."""
        ...

    @abc.abstractmethod
    async def get_unified_health(self) -> PlatformHealth:
        """Get unified platform health."""
        ...

    @abc.abstractmethod
    async def get_platform_manifest(self) -> PlatformManifest:
        """Get the platform manifest."""
        ...

    @abc.abstractmethod
    async def create_audit_package(self) -> IntegrationAuditPackage:
        """Create an immutable audit package."""
        ...

    @abc.abstractmethod
    async def get_platform_quality(self) -> PlatformQualityResult:
        """Evaluate platform quality."""
        ...

    @abc.abstractmethod
    async def check_platform_compliance(self) -> PlatformComplianceResult:
        """Check platform compliance."""
        ...

    @abc.abstractmethod
    async def get_platform_readiness(self) -> PlatformReadinessReport:
        """Get platform readiness report."""
        ...

    @abc.abstractmethod
    async def get_platform_snapshot(self) -> PlatformSnapshot:
        """Get an immutable platform snapshot."""
        ...

    @abc.abstractmethod
    async def get_pipeline_version_history(self) -> list[PipelineVersionRecord]:
        """Get pipeline version history."""
        ...

    @abc.abstractmethod
    async def create_pipeline_version(self, platform_version: str) -> PipelineVersionRecord:
        """Create a new pipeline version."""
        ...

    @abc.abstractmethod
    async def get_documentation_metadata(self) -> DocumentationMetadata:
        """Get documentation coverage metadata."""
        ...

    @abc.abstractmethod
    async def export_platform_package(self) -> PlatformExportPackage:
        """Build an exportable platform package."""
        ...

    @abc.abstractmethod
    async def run_release_checklist(self) -> PlatformReleaseChecklist:
        """Run the release checklist."""
        ...


class PlatformIntegrationManager(abc.ABC):
    """Lightweight internal facade over PlatformIntegrationCoordinator."""

    @abc.abstractmethod
    async def validate_platform(self) -> PlatformValidationResult:
        """Validate the full platform."""
        ...

    @abc.abstractmethod
    async def get_compatibility_report(self) -> PlatformCompatibilityReport:
        """Get platform compatibility report."""
        ...

    @abc.abstractmethod
    async def run_diagnostics(self) -> PlatformDiagnosticsResult:
        """Run platform diagnostics."""
        ...

    @abc.abstractmethod
    async def get_unified_health(self) -> PlatformHealth:
        """Get unified platform health."""
        ...

    @abc.abstractmethod
    async def get_platform_manifest(self) -> PlatformManifest:
        """Get platform manifest."""
        ...

    @abc.abstractmethod
    async def create_audit_package(self) -> IntegrationAuditPackage:
        """Create audit package."""
        ...

    @abc.abstractmethod
    async def get_platform_quality(self) -> PlatformQualityResult:
        """Evaluate platform quality."""
        ...

    @abc.abstractmethod
    async def check_platform_compliance(self) -> PlatformComplianceResult:
        """Check platform compliance."""
        ...

    @abc.abstractmethod
    async def get_platform_readiness(self) -> PlatformReadinessReport:
        """Get platform readiness report."""
        ...

    @abc.abstractmethod
    async def get_platform_snapshot(self) -> PlatformSnapshot:
        """Get an immutable platform snapshot."""
        ...

    @abc.abstractmethod
    async def get_pipeline_version_history(self) -> list[PipelineVersionRecord]:
        """Get pipeline version history."""
        ...

    @abc.abstractmethod
    async def create_pipeline_version(self, platform_version: str) -> PipelineVersionRecord:
        """Create a new pipeline version."""
        ...

    @abc.abstractmethod
    async def get_documentation_metadata(self) -> DocumentationMetadata:
        """Get documentation coverage metadata."""
        ...

    @abc.abstractmethod
    async def export_platform_package(self) -> PlatformExportPackage:
        """Build an exportable platform package."""
        ...

    @abc.abstractmethod
    async def run_release_checklist(self) -> PlatformReleaseChecklist:
        """Run the release checklist."""
        ...


class PlatformIntegrationService(abc.ABC):
    """ONLY public API for platform validation operations."""

    @abc.abstractmethod
    async def validate_platform(self) -> PlatformValidationResult:
        """Validate the full platform (bootstrap + contracts + diagnostics + health)."""
        ...

    @abc.abstractmethod
    async def get_compatibility_report(self) -> PlatformCompatibilityReport:
        """Get the platform-wide compatibility report."""
        ...

    @abc.abstractmethod
    async def run_diagnostics(self) -> PlatformDiagnosticsResult:
        """Run comprehensive platform diagnostics."""
        ...

    @abc.abstractmethod
    async def get_unified_health(self) -> PlatformHealth:
        """Get unified health across all platform modules."""
        ...

    @abc.abstractmethod
    async def get_platform_manifest(self) -> PlatformManifest:
        """Get the complete platform manifest."""
        ...

    @abc.abstractmethod
    async def create_audit_package(self) -> IntegrationAuditPackage:
        """Create an immutable audit snapshot of the platform."""
        ...

    @abc.abstractmethod
    async def get_platform_quality(self) -> PlatformQualityResult:
        """Evaluate platform quality across architecture, integration, docs, and tests."""
        ...

    @abc.abstractmethod
    async def check_platform_compliance(self) -> PlatformComplianceResult:
        """Validate platform compliance with architecture standards."""
        ...

    @abc.abstractmethod
    async def get_platform_readiness(self) -> PlatformReadinessReport:
        """Get a comprehensive readiness assessment."""
        ...

    @abc.abstractmethod
    async def get_platform_snapshot(self) -> PlatformSnapshot:
        """Get an immutable platform snapshot (services, managers, versions)."""
        ...

    @abc.abstractmethod
    async def get_pipeline_version_history(self) -> list[PipelineVersionRecord]:
        """Get the full pipeline version history."""
        ...

    @abc.abstractmethod
    async def create_pipeline_version(self, platform_version: str) -> PipelineVersionRecord:
        """Create a new pipeline version and return the record."""
        ...

    @abc.abstractmethod
    async def get_documentation_metadata(self) -> DocumentationMetadata:
        """Get documentation coverage metadata for all platform components."""
        ...

    @abc.abstractmethod
    async def export_platform_package(self) -> PlatformExportPackage:
        """Build and return an exportable platform package."""
        ...

    @abc.abstractmethod
    async def run_release_checklist(self) -> PlatformReleaseChecklist:
        """Run the release checklist and return validation results."""
        ...


# ──────────────────────────────────────────────────────────────────────
# Phase 3.5 – Enterprise Refinement & Platform Freeze
# ──────────────────────────────────────────────────────────────────────


class PlatformReadinessChecker(abc.ABC):
    """Generates a readiness report for the platform."""

    @abc.abstractmethod
    def check_readiness(
        self,
        registry: ServiceRegistry,
        validation: PlatformValidationResult,
        health: PlatformHealth,
    ) -> PlatformReadinessReport:
        """Evaluate platform readiness given validation and health state."""
        ...


class PlatformQualityManager(abc.ABC):
    """Evaluates platform quality across multiple dimensions."""

    @abc.abstractmethod
    def evaluate_quality(self, registry: ServiceRegistry) -> PlatformQualityResult:
        """Evaluate architecture, integration, documentation, and test quality."""
        ...


class PlatformComplianceManager(abc.ABC):
    """Validates platform compliance with architecture standards."""

    @abc.abstractmethod
    def check_compliance(self, registry: ServiceRegistry) -> PlatformComplianceResult:
        """Validate SOLID, Clean Architecture, layer isolation, dependency rules, naming."""
        ...


class PlatformSnapshotManager(abc.ABC):
    """Creates immutable platform snapshots."""

    @abc.abstractmethod
    def create_snapshot(self, registry: ServiceRegistry, versions: dict[str, str]) -> PlatformSnapshot:
        """Capture an immutable snapshot of the current platform state."""
        ...


class PlatformPipelineVersionManager(abc.ABC):
    """Manages pipeline versioning."""

    @abc.abstractmethod
    def create_version(self, platform_version: str, modules: list[str], stage_count: int) -> PipelineVersionRecord:
        """Create a new pipeline version record."""
        ...

    @abc.abstractmethod
    def activate_version(self, pipeline_version: str) -> PipelineVersionRecord | None:
        """Set a pipeline version as active."""
        ...

    @abc.abstractmethod
    def get_active_version(self) -> PipelineVersionRecord | None:
        """Get the currently active pipeline version."""
        ...

    @abc.abstractmethod
    def get_version_history(self) -> list[PipelineVersionRecord]:
        """Get the full pipeline version history."""
        ...


class DocumentationMetadataGenerator(abc.ABC):
    """Generates documentation coverage metadata."""

    @abc.abstractmethod
    def generate_metadata(self, registry: ServiceRegistry) -> DocumentationMetadata:
        """Generate documentation metadata for all platform components."""
        ...


class PlatformExportPackageBuilder(abc.ABC):
    """Builds platform export packages for release packaging."""

    @abc.abstractmethod
    def build_export_package(
        self,
        registry: ServiceRegistry,
        manifest: PlatformManifest,
        compatibility: PlatformCompatibilityReport,
        quality: PlatformQualityResult | None = None,
        compliance: PlatformComplianceResult | None = None,
        readiness: PlatformReadinessReport | None = None,
    ) -> PlatformExportPackage:
        """Build an exportable platform package."""
        ...


class PlatformReleaseChecklistRunner(abc.ABC):
    """Runs the release checklist and returns validation results."""

    @abc.abstractmethod
    def run_checklist(
        self,
        registry: ServiceRegistry,
        diagnostics: PlatformDiagnosticsResult,
        health: PlatformHealth,
    ) -> PlatformReleaseChecklist:
        """Run the full release checklist and return results."""
        ...
