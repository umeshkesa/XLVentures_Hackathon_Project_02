"""PlatformIntegrationCoordinator — coordinates Phase 3/3.5 validation and orchestration."""

from __future__ import annotations

import structlog

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
    PlatformQualityResult,
    PlatformReadinessReport,
    PlatformReleaseChecklist,
    PlatformSnapshot,
    PlatformValidationResult,
)
from adip.platform.enums import ModuleName, PipelineStage
from adip.platform.interfaces import (
    BootstrapValidator,
    CrossModuleContractValidator,
    DocumentationMetadataGenerator,
    IntegrationAuditPackageGenerator,
    PlatformCompatibilityReportGenerator,
    PlatformComplianceManager,
    PlatformDiagnostics,
    PlatformExportPackageBuilder,
    PlatformIntegrationCoordinator,
    PlatformManifestGenerator,
    PlatformPipelineVersionManager,
    PlatformQualityManager,
    PlatformReadinessChecker,
    PlatformReleaseChecklistRunner,
    PlatformSnapshotManager,
    PlatformVersionManager,
    ServiceRegistry,
    UnifiedHealth,
)

logger = structlog.get_logger(__name__)


class DefaultPlatformIntegrationCoordinator(PlatformIntegrationCoordinator):
    """Coordinates all Phase 3/3.5 platform validation and orchestration components."""

    def __init__(
        self,
        registry: ServiceRegistry,
        bootstrap_validator: BootstrapValidator,
        contract_validator: CrossModuleContractValidator,
        diagnostics: PlatformDiagnostics,
        compatibility_report: PlatformCompatibilityReportGenerator,
        unified_health: UnifiedHealth,
        manifest_generator: PlatformManifestGenerator,
        audit_package_generator: IntegrationAuditPackageGenerator,
        version_manager: PlatformVersionManager,
        readiness_checker: PlatformReadinessChecker,
        quality_manager: PlatformQualityManager,
        compliance_manager: PlatformComplianceManager,
        snapshot_manager: PlatformSnapshotManager,
        pipeline_version_manager: PlatformPipelineVersionManager,
        doc_metadata_generator: DocumentationMetadataGenerator,
        export_package_builder: PlatformExportPackageBuilder,
        release_checklist_runner: PlatformReleaseChecklistRunner,
    ) -> None:
        self._registry = registry
        self._bootstrap = bootstrap_validator
        self._contracts = contract_validator
        self._diagnostics = diagnostics
        self._compatibility = compatibility_report
        self._health = unified_health
        self._manifest = manifest_generator
        self._audit = audit_package_generator
        self._versions = version_manager
        self._readiness = readiness_checker
        self._quality = quality_manager
        self._compliance = compliance_manager
        self._snapshot = snapshot_manager
        self._pipeline_versions = pipeline_version_manager
        self._doc_metadata = doc_metadata_generator
        self._export = export_package_builder
        self._release = release_checklist_runner
        logger.debug("integration_coordinator.initialized")

    async def validate_platform(self) -> PlatformValidationResult:
        bootstrap_result = self._bootstrap.validate(self._registry)
        contracts = self._contracts.validate_all_contracts(self._registry)
        diag = self._diagnostics.run_diagnostics(self._registry)
        health = self._health.get_unified_health(self._registry)

        platform_valid = (
            bootstrap_result.bootstrap_valid
            and contracts.pairs_error == 0
            and diag.all_valid
        )

        return PlatformValidationResult(
            platform_valid=platform_valid,
            bootstrap_valid=bootstrap_result.bootstrap_valid,
            contracts_valid=contracts.pairs_error == 0,
            diagnostics_valid=diag.all_valid,
            health_status=health.overall_status.value,
            message=(
                "Platform validation passed"
                if platform_valid
                else "Platform validation failed — see details"
            ),
            details={
                "bootstrap": bootstrap_result.model_dump(),
                "contracts": contracts.model_dump(),
                "diagnostics": diag.model_dump(),
                "health": health.model_dump(),
            },
        )

    async def get_compatibility_report(self) -> PlatformCompatibilityReport:
        return self._compatibility.generate_report(self._registry)

    async def run_diagnostics(self) -> PlatformDiagnosticsResult:
        return self._diagnostics.run_diagnostics(self._registry)

    async def get_unified_health(self) -> PlatformHealth:
        return self._health.get_unified_health(self._registry)

    async def get_platform_manifest(self) -> PlatformManifest:
        return self._manifest.generate_manifest(self._registry)

    async def create_audit_package(self) -> IntegrationAuditPackage:
        validation = await self.validate_platform()
        compatibility = await self.get_compatibility_report()
        diagnostics = await self.run_diagnostics()
        health = await self.get_unified_health()
        manifest = await self.get_platform_manifest()
        quality = await self.get_platform_quality()
        compliance = await self.check_platform_compliance()
        readiness = await self.get_platform_readiness()
        return self._audit.create_audit_package(
            validation=validation,
            compatibility=compatibility,
            diagnostics=diagnostics,
            health=health,
            manifest=manifest,
            quality=quality,
            compliance=compliance,
            readiness=readiness,
        )

    async def get_platform_quality(self) -> PlatformQualityResult:
        return self._quality.evaluate_quality(self._registry)

    async def check_platform_compliance(self) -> PlatformComplianceResult:
        return self._compliance.check_compliance(self._registry)

    async def get_platform_readiness(self) -> PlatformReadinessReport:
        validation = await self.validate_platform()
        health = await self.get_unified_health()
        return self._readiness.check_readiness(self._registry, validation, health)

    async def get_platform_snapshot(self) -> PlatformSnapshot:
        raw_versions = {}
        for record in self._versions.list_versions():
            raw_versions[record.module] = record.version
        return self._snapshot.create_snapshot(self._registry, raw_versions)

    async def get_pipeline_version_history(self) -> list[PipelineVersionRecord]:
        return self._pipeline_versions.get_version_history()

    async def create_pipeline_version(self, platform_version: str) -> PipelineVersionRecord:
        module_names = [m.value for m in ModuleName]
        stage_count = len(PipelineStage)
        record = self._pipeline_versions.create_version(platform_version, module_names, stage_count)
        self._pipeline_versions.activate_version(record.pipeline_version)
        return record

    async def get_documentation_metadata(self) -> DocumentationMetadata:
        return self._doc_metadata.generate_metadata(self._registry)

    async def export_platform_package(self) -> PlatformExportPackage:
        manifest = await self.get_platform_manifest()
        compatibility = await self.get_compatibility_report()
        quality = await self.get_platform_quality()
        compliance = await self.check_platform_compliance()
        readiness = await self.get_platform_readiness()
        return self._export.build_export_package(
            registry=self._registry,
            manifest=manifest,
            compatibility=compatibility,
            quality=quality,
            compliance=compliance,
            readiness=readiness,
        )

    async def run_release_checklist(self) -> PlatformReleaseChecklist:
        diagnostics = await self.run_diagnostics()
        health = await self.get_unified_health()
        return self._release.run_checklist(self._registry, diagnostics, health)
