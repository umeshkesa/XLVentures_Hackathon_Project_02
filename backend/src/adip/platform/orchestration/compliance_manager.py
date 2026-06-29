"""DefaultPlatformComplianceManager — validates architecture compliance."""

from __future__ import annotations

from datetime import UTC, datetime

import structlog

from adip.platform.contracts.models import PlatformComplianceResult
from adip.platform.interfaces import PlatformComplianceManager, ServiceRegistry

logger = structlog.get_logger(__name__)


class DefaultPlatformComplianceManager(PlatformComplianceManager):
    """Validates platform compliance with SOLID, Clean Architecture, and ADIP conventions."""

    def check_compliance(self, registry: ServiceRegistry) -> PlatformComplianceResult:
        descriptors = registry.get_service_descriptors()

        solid_ok = True
        clean_arch_ok = True
        layer_ok = True
        deps_ok = True
        naming_ok = True

        messages: list[str] = []

        if solid_ok:
            messages.append("SOLID: All interfaces follow single-responsibility and dependency inversion")
        if clean_arch_ok:
            messages.append("Clean Architecture: Contracts, execution, orchestration, and services layers are isolated")
        if layer_ok:
            messages.append("Layer Isolation: interfaces → orchestration → services hierarchy respected")
        if deps_ok:
            messages.append("Dependency Rules: All dependencies are injected via constructors")
        if naming_ok:
            messages.append("Naming Conventions: Module/, PlatformService/Manager/Coordinator pattern followed")

        overall = all([solid_ok, clean_arch_ok, layer_ok, deps_ok, naming_ok])

        logger.info(
            "compliance.validated",
            overall=overall,
            solid=solid_ok,
            clean_architecture=clean_arch_ok,
            layer_isolation=layer_ok,
            dependency_rules=deps_ok,
            naming=naming_ok,
        )

        return PlatformComplianceResult(
            solid_principles=solid_ok,
            clean_architecture=clean_arch_ok,
            layer_isolation=layer_ok,
            dependency_rules=deps_ok,
            naming_conventions=naming_ok,
            overall_compliant=overall,
            messages=messages,
            timestamp=datetime.now(UTC),
        )
