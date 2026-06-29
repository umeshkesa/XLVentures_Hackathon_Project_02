"""DefaultPlatformIntegrationService — ONLY public API for platform validation."""

from __future__ import annotations

import uuid
from collections.abc import Callable
from typing import Any

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
from adip.platform.enums import PipelineStage
from adip.platform.interfaces import PlatformIntegrationManager, PlatformIntegrationService
from adip.platform.services.hooks import hooks

logger = structlog.get_logger(__name__)


class DefaultPlatformIntegrationService(PlatformIntegrationService):
    """ONLY public API for platform validation operations.

    External modules interact ONLY with this facade. Wraps:
    - Auth callback
    - Audit callback
    - Integration hook firing
    - Error handling
    - Correlation ID propagation
    """

    def __init__(
        self,
        manager: PlatformIntegrationManager,
        auth_callback: Callable[[str], Any] | None = None,
        audit_callback: Callable[[str, dict[str, Any]], None] | None = None,
    ) -> None:
        self._manager = manager
        self._auth_callback = auth_callback
        self._audit_callback = audit_callback
        logger.debug("integration_service.initialized")

    async def validate_platform(self) -> PlatformValidationResult:
        correlation_id = str(uuid.uuid4())
        try:
            hooks.fire_pre_pipeline({"correlation_id": correlation_id, "operation": "validate_platform"})
            if self._auth_callback:
                self._auth_callback(correlation_id)
            result = await self._manager.validate_platform()
            if self._audit_callback:
                self._audit_callback("validate_platform", {"correlation_id": correlation_id, **result.model_dump()})
            hooks.fire_post_pipeline({"correlation_id": correlation_id, "operation": "validate_platform", "success": True})
            return result
        except Exception as exc:
            logger.error("integration_service.validate_platform.failed", error=str(exc))
            hooks.fire_on_error(PipelineStage.VALIDATION, str(exc), {"correlation_id": correlation_id})
            raise

    async def get_compatibility_report(self) -> PlatformCompatibilityReport:
        correlation_id = str(uuid.uuid4())
        try:
            if self._auth_callback:
                self._auth_callback(correlation_id)
            result = await self._manager.get_compatibility_report()
            if self._audit_callback:
                self._audit_callback("get_compatibility_report", {"correlation_id": correlation_id})
            return result
        except Exception as exc:
            logger.error("integration_service.compatibility_report.failed", error=str(exc))
            hooks.fire_on_error(PipelineStage.VALIDATION, str(exc), {"correlation_id": correlation_id})
            raise

    async def run_diagnostics(self) -> PlatformDiagnosticsResult:
        correlation_id = str(uuid.uuid4())
        try:
            if self._auth_callback:
                self._auth_callback(correlation_id)
            result = await self._manager.run_diagnostics()
            if self._audit_callback:
                self._audit_callback("run_diagnostics", {"correlation_id": correlation_id})
            return result
        except Exception as exc:
            logger.error("integration_service.diagnostics.failed", error=str(exc))
            hooks.fire_on_error(PipelineStage.VALIDATION, str(exc), {"correlation_id": correlation_id})
            raise

    async def get_unified_health(self) -> PlatformHealth:
        correlation_id = str(uuid.uuid4())
        try:
            if self._auth_callback:
                self._auth_callback(correlation_id)
            result = await self._manager.get_unified_health()
            if self._audit_callback:
                self._audit_callback("get_unified_health", {"correlation_id": correlation_id})
            hooks.fire_on_health_check({"correlation_id": correlation_id, "status": result.overall_status.value})
            return result
        except Exception as exc:
            logger.error("integration_service.unified_health.failed", error=str(exc))
            hooks.fire_on_error(PipelineStage.VALIDATION, str(exc), {"correlation_id": correlation_id})
            raise

    async def get_platform_manifest(self) -> PlatformManifest:
        correlation_id = str(uuid.uuid4())
        try:
            if self._auth_callback:
                self._auth_callback(correlation_id)
            result = await self._manager.get_platform_manifest()
            if self._audit_callback:
                self._audit_callback("get_platform_manifest", {"correlation_id": correlation_id})
            hooks.fire_on_manifest({"correlation_id": correlation_id, "services": result.total_services})
            return result
        except Exception as exc:
            logger.error("integration_service.manifest.failed", error=str(exc))
            hooks.fire_on_error(PipelineStage.VALIDATION, str(exc), {"correlation_id": correlation_id})
            raise

    async def create_audit_package(self) -> IntegrationAuditPackage:
        correlation_id = str(uuid.uuid4())
        try:
            hooks.fire_pre_pipeline({"correlation_id": correlation_id, "operation": "create_audit_package"})
            if self._auth_callback:
                self._auth_callback(correlation_id)
            result = await self._manager.create_audit_package()
            if self._audit_callback:
                self._audit_callback("create_audit_package", {"correlation_id": correlation_id, "audit_id": result.audit_id})
            hooks.fire_post_pipeline({"correlation_id": correlation_id, "operation": "create_audit_package", "audit_id": result.audit_id})
            return result
        except Exception as exc:
            logger.error("integration_service.audit_package.failed", error=str(exc))
            hooks.fire_on_error(PipelineStage.VALIDATION, str(exc), {"correlation_id": correlation_id})
            raise

    async def get_platform_quality(self) -> PlatformQualityResult:
        correlation_id = str(uuid.uuid4())
        try:
            if self._auth_callback:
                self._auth_callback(correlation_id)
            result = await self._manager.get_platform_quality()
            if self._audit_callback:
                self._audit_callback("get_platform_quality", {"correlation_id": correlation_id})
            return result
        except Exception as exc:
            logger.error("integration_service.quality.failed", error=str(exc))
            hooks.fire_on_error(PipelineStage.VALIDATION, str(exc), {"correlation_id": correlation_id})
            raise

    async def check_platform_compliance(self) -> PlatformComplianceResult:
        correlation_id = str(uuid.uuid4())
        try:
            if self._auth_callback:
                self._auth_callback(correlation_id)
            result = await self._manager.check_platform_compliance()
            if self._audit_callback:
                self._audit_callback("check_platform_compliance", {"correlation_id": correlation_id})
            return result
        except Exception as exc:
            logger.error("integration_service.compliance.failed", error=str(exc))
            hooks.fire_on_error(PipelineStage.VALIDATION, str(exc), {"correlation_id": correlation_id})
            raise

    async def get_platform_readiness(self) -> PlatformReadinessReport:
        correlation_id = str(uuid.uuid4())
        try:
            if self._auth_callback:
                self._auth_callback(correlation_id)
            result = await self._manager.get_platform_readiness()
            if self._audit_callback:
                self._audit_callback("get_platform_readiness", {"correlation_id": correlation_id})
            return result
        except Exception as exc:
            logger.error("integration_service.readiness.failed", error=str(exc))
            hooks.fire_on_error(PipelineStage.VALIDATION, str(exc), {"correlation_id": correlation_id})
            raise

    async def get_platform_snapshot(self) -> PlatformSnapshot:
        correlation_id = str(uuid.uuid4())
        try:
            if self._auth_callback:
                self._auth_callback(correlation_id)
            result = await self._manager.get_platform_snapshot()
            if self._audit_callback:
                self._audit_callback("get_platform_snapshot", {"correlation_id": correlation_id})
            return result
        except Exception as exc:
            logger.error("integration_service.snapshot.failed", error=str(exc))
            hooks.fire_on_error(PipelineStage.VALIDATION, str(exc), {"correlation_id": correlation_id})
            raise

    async def get_pipeline_version_history(self) -> list[PipelineVersionRecord]:
        correlation_id = str(uuid.uuid4())
        try:
            if self._auth_callback:
                self._auth_callback(correlation_id)
            result = await self._manager.get_pipeline_version_history()
            if self._audit_callback:
                self._audit_callback("get_pipeline_version_history", {"correlation_id": correlation_id})
            return result
        except Exception as exc:
            logger.error("integration_service.version_history.failed", error=str(exc))
            hooks.fire_on_error(PipelineStage.VALIDATION, str(exc), {"correlation_id": correlation_id})
            raise

    async def create_pipeline_version(self, platform_version: str) -> PipelineVersionRecord:
        correlation_id = str(uuid.uuid4())
        try:
            if self._auth_callback:
                self._auth_callback(correlation_id)
            result = await self._manager.create_pipeline_version(platform_version)
            if self._audit_callback:
                self._audit_callback("create_pipeline_version", {"correlation_id": correlation_id, "version": result.pipeline_version})
            return result
        except Exception as exc:
            logger.error("integration_service.create_version.failed", error=str(exc))
            hooks.fire_on_error(PipelineStage.VALIDATION, str(exc), {"correlation_id": correlation_id})
            raise

    async def get_documentation_metadata(self) -> DocumentationMetadata:
        correlation_id = str(uuid.uuid4())
        try:
            if self._auth_callback:
                self._auth_callback(correlation_id)
            result = await self._manager.get_documentation_metadata()
            if self._audit_callback:
                self._audit_callback("get_documentation_metadata", {"correlation_id": correlation_id})
            return result
        except Exception as exc:
            logger.error("integration_service.doc_metadata.failed", error=str(exc))
            hooks.fire_on_error(PipelineStage.VALIDATION, str(exc), {"correlation_id": correlation_id})
            raise

    async def export_platform_package(self) -> PlatformExportPackage:
        correlation_id = str(uuid.uuid4())
        try:
            hooks.fire_pre_pipeline({"correlation_id": correlation_id, "operation": "export_platform"})
            if self._auth_callback:
                self._auth_callback(correlation_id)
            result = await self._manager.export_platform_package()
            if self._audit_callback:
                self._audit_callback("export_platform_package", {"correlation_id": correlation_id})
            hooks.fire_post_pipeline({"correlation_id": correlation_id, "operation": "export_platform", "success": True})
            return result
        except Exception as exc:
            logger.error("integration_service.export.failed", error=str(exc))
            hooks.fire_on_error(PipelineStage.VALIDATION, str(exc), {"correlation_id": correlation_id})
            raise

    async def run_release_checklist(self) -> PlatformReleaseChecklist:
        correlation_id = str(uuid.uuid4())
        try:
            hooks.fire_pre_pipeline({"correlation_id": correlation_id, "operation": "release_checklist"})
            if self._auth_callback:
                self._auth_callback(correlation_id)
            result = await self._manager.run_release_checklist()
            if self._audit_callback:
                self._audit_callback("run_release_checklist", {"correlation_id": correlation_id})
            hooks.fire_post_pipeline({"correlation_id": correlation_id, "operation": "release_checklist", "ready": result.platform_ready})
            return result
        except Exception as exc:
            logger.error("integration_service.release_checklist.failed", error=str(exc))
            hooks.fire_on_error(PipelineStage.VALIDATION, str(exc), {"correlation_id": correlation_id})
            raise
