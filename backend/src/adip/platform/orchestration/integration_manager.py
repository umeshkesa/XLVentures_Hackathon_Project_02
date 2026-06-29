"""PlatformIntegrationManager — lightweight facade over the integration coordinator."""

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
from adip.platform.interfaces import PlatformIntegrationCoordinator, PlatformIntegrationManager

logger = structlog.get_logger(__name__)


class DefaultPlatformIntegrationManager(PlatformIntegrationManager):
    """Lightweight internal facade over PlatformIntegrationCoordinator."""

    def __init__(self, coordinator: PlatformIntegrationCoordinator) -> None:
        self._coordinator = coordinator
        logger.debug("integration_manager.initialized")

    async def validate_platform(self) -> PlatformValidationResult:
        return await self._coordinator.validate_platform()

    async def get_compatibility_report(self) -> PlatformCompatibilityReport:
        return await self._coordinator.get_compatibility_report()

    async def run_diagnostics(self) -> PlatformDiagnosticsResult:
        return await self._coordinator.run_diagnostics()

    async def get_unified_health(self) -> PlatformHealth:
        return await self._coordinator.get_unified_health()

    async def get_platform_manifest(self) -> PlatformManifest:
        return await self._coordinator.get_platform_manifest()

    async def create_audit_package(self) -> IntegrationAuditPackage:
        return await self._coordinator.create_audit_package()

    async def get_platform_quality(self) -> PlatformQualityResult:
        return await self._coordinator.get_platform_quality()

    async def check_platform_compliance(self) -> PlatformComplianceResult:
        return await self._coordinator.check_platform_compliance()

    async def get_platform_readiness(self) -> PlatformReadinessReport:
        return await self._coordinator.get_platform_readiness()

    async def get_platform_snapshot(self) -> PlatformSnapshot:
        return await self._coordinator.get_platform_snapshot()

    async def get_pipeline_version_history(self) -> list[PipelineVersionRecord]:
        return await self._coordinator.get_pipeline_version_history()

    async def create_pipeline_version(self, platform_version: str) -> PipelineVersionRecord:
        return await self._coordinator.create_pipeline_version(platform_version)

    async def get_documentation_metadata(self) -> DocumentationMetadata:
        return await self._coordinator.get_documentation_metadata()

    async def export_platform_package(self) -> PlatformExportPackage:
        return await self._coordinator.export_platform_package()

    async def run_release_checklist(self) -> PlatformReleaseChecklist:
        return await self._coordinator.run_release_checklist()
