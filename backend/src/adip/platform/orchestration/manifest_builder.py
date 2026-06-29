"""DefaultManifestBuilder — generates the platform manifest."""

from __future__ import annotations

import structlog

from adip.platform.contracts.models import PlatformManifest
from adip.platform.interfaces import ManifestBuilder, ServiceRegistry

logger = structlog.get_logger(__name__)


class DefaultManifestBuilder(ManifestBuilder):
    """Default manifest builder.

    Generates a PlatformManifest from the service registry containing
    all registered modules, services, versions, and dependencies.
    """

    def __init__(self) -> None:
        self._platform_version: str = "1.0.0"
        logger.debug("manifest_builder.initialized")

    def build(self, registry: ServiceRegistry) -> PlatformManifest:
        """Build the platform manifest from the registry."""
        services = registry.get_service_descriptors()
        modules = registry.get_modules()

        manifest = PlatformManifest(
            platform_version=self._platform_version,
            modules=modules,
            services=services,
            total_services=len(services),
            total_modules=len(modules),
            metadata={
                "generator": "DefaultManifestBuilder",
                "framework": "ADIP Platform Integration",
            },
        )

        logger.debug(
            "manifest_builder.built",
            total_services=manifest.total_services,
            total_modules=manifest.total_modules,
        )
        return manifest
