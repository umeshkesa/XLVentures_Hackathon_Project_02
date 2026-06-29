"""DefaultPlatformManifestGenerator — generates the full platform manifest."""

from __future__ import annotations

from datetime import UTC, datetime

import structlog

from adip.platform.contracts.models import PlatformManifest
from adip.platform.interfaces import PlatformManifestGenerator, ServiceRegistry

logger = structlog.get_logger(__name__)


class DefaultPlatformManifestGenerator(PlatformManifestGenerator):
    """Generates the platform manifest with full service, module, and dependency metadata."""

    def __init__(self, platform_version: str = "1.0.0") -> None:
        self._platform_version = platform_version
        logger.debug("manifest_generator.initialized")

    def generate_manifest(self, registry: ServiceRegistry) -> PlatformManifest:
        services = registry.get_service_descriptors()
        modules = registry.get_modules()

        manifest = PlatformManifest(
            platform_version=self._platform_version,
            modules=modules,
            services=services,
            total_services=len(services),
            total_modules=len(modules),
            metadata={
                "generator": "DefaultPlatformManifestGenerator",
                "framework": "ADIP Platform Integration",
                "generated_at": datetime.now(UTC).isoformat(),
            },
        )

        logger.debug(
            "manifest_generator.generated",
            total_services=manifest.total_services,
            total_modules=manifest.total_modules,
        )
        return manifest
