"""DefaultIntegrationAuditPackageGenerator — creates immutable audit packages."""

from __future__ import annotations

import hashlib
import json
import uuid

import structlog

from adip.platform.contracts.models import (
    IntegrationAuditPackage,
    PlatformCompatibilityReport,
    PlatformComplianceResult,
    PlatformDiagnosticsResult,
    PlatformHealth,
    PlatformManifest,
    PlatformQualityResult,
    PlatformReadinessReport,
    PlatformValidationResult,
)
from adip.platform.interfaces import IntegrationAuditPackageGenerator

logger = structlog.get_logger(__name__)


class DefaultIntegrationAuditPackageGenerator(IntegrationAuditPackageGenerator):
    """Creates immutable audit packages capturing platform validation state."""

    def __init__(self, version: str = "1.0.0") -> None:
        self._version = version
        logger.debug("audit_package_generator.initialized")

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
        content = {
            "validation": validation.model_dump(),
            "compatibility": compatibility.model_dump(),
            "diagnostics": diagnostics.model_dump(),
            "health": health.model_dump(),
            "manifest": manifest.model_dump(),
        }
        checksum = hashlib.sha256(json.dumps(content, sort_keys=True, default=str).encode()).hexdigest()[:16]

        package = IntegrationAuditPackage(
            audit_id=str(uuid.uuid4()),
            version=self._version,
            validation=validation,
            compatibility=compatibility,
            diagnostics=diagnostics,
            health=health,
            manifest=manifest,
            quality=quality,
            compliance=compliance,
            readiness=readiness,
            checksum=checksum,
        )

        logger.info(
            "audit_package.created",
            audit_id=package.audit_id,
            checksum=checksum,
            has_quality=quality is not None,
            has_compliance=compliance is not None,
            has_readiness=readiness is not None,
        )
        return package
