"""DefaultPlatformManager — lightweight internal facade over the coordinator."""

from __future__ import annotations

import structlog

from adip.platform.contracts.models import (
    PlatformHealth,
    PlatformManifest,
    PlatformMetrics,
    PlatformRequest,
    PlatformResponse,
)
from adip.platform.interfaces import PlatformCoordinator, PlatformManager

logger = structlog.get_logger(__name__)


class DefaultPlatformManager(PlatformManager):
    """Default lightweight facade over PlatformCoordinator.

    Provides a thin delegation layer with no additional business logic.
    """

    def __init__(self, coordinator: PlatformCoordinator) -> None:
        self._coordinator = coordinator
        logger.debug("platform_manager.initialized")

    async def execute_pipeline(self, request: PlatformRequest) -> PlatformResponse:
        """Delegate pipeline execution to the coordinator."""
        return await self._coordinator.execute_pipeline(request)

    async def get_health(self) -> PlatformHealth:
        """Delegate health aggregation to the coordinator."""
        return await self._coordinator.get_health()

    async def get_metrics(self) -> PlatformMetrics:
        """Delegate metrics collection to the coordinator."""
        return await self._coordinator.get_metrics()

    async def get_manifest(self) -> PlatformManifest:
        """Delegate manifest generation to the coordinator."""
        return await self._coordinator.get_manifest()
