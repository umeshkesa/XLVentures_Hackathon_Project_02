"""DefaultPlatformService — the ONLY public API for platform operations.

Wraps PlatformManager with correlation ID propagation, hook firing,
and error wrapping. External modules MUST go through this facade.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import structlog

from adip.platform.contracts.models import (
    PlatformHealth,
    PlatformManifest,
    PlatformMetrics,
    PlatformRequest,
    PlatformResponse,
    PlatformTrace,
)
from adip.platform.enums import PipelineStage
from adip.platform.interfaces import PlatformManager, PlatformService
from adip.platform.services.hooks import hooks

log = structlog.get_logger(__name__)


class DefaultPlatformService(PlatformService):
    """Enterprise facade for platform pipeline operations.

    Provides:
    - Correlation ID propagation
    - Integration hook firing (pre/post pipeline, error)
    - Error wrapping
    - Delegation to PlatformManager
    """

    def __init__(self, manager: PlatformManager) -> None:
        self._manager = manager
        log.debug("platform_service.initialized")

    async def execute_pipeline(self, request: PlatformRequest) -> PlatformResponse:
        """Execute the end-to-end platform pipeline with hooks and audit."""
        correlation_id = request.correlation_id or str(uuid.uuid4())
        bound_log = log.bind(correlation_id=correlation_id)

        pipeline_context = {
            "correlation_id": correlation_id,
            "request_id": str(request.request_id),
            "timestamp": datetime.now(UTC).isoformat(),
        }

        hooks.fire_pre_pipeline(pipeline_context)
        bound_log.info("platform_service.pipeline_started", stages=len(request.pipeline) if request.pipeline else "all")

        try:
            response = await self._manager.execute_pipeline(request)

            if response.success:
                bound_log.info(
                    "platform_service.pipeline_completed",
                    status=response.status.value,
                    duration_ms=response.duration_ms,
                )
            else:
                bound_log.warning(
                    "platform_service.pipeline_failed",
                    status=response.status.value,
                    errors=response.errors,
                )

            hooks.fire_post_pipeline({**pipeline_context, "response": response.model_dump()})
            return response

        except Exception as exc:
            error_msg = f"Platform pipeline error: {exc}"
            bound_log.error("platform_service.pipeline_error", error=error_msg)
            hooks.fire_on_error(PipelineStage.VALIDATION, error_msg, pipeline_context)

            return PlatformResponse(
                request_id=request.request_id,
                correlation_id=correlation_id,
                success=False,
                errors=[error_msg],
                duration_ms=0.0,
            )

    async def get_health(self) -> PlatformHealth:
        """Get aggregated platform health."""
        pipeline_context = {
            "timestamp": datetime.now(UTC).isoformat(),
        }
        hooks.fire_on_health_check(pipeline_context)
        return await self._manager.get_health()

    async def get_metrics(self) -> PlatformMetrics:
        """Get aggregated platform metrics."""
        pipeline_context = {
            "timestamp": datetime.now(UTC).isoformat(),
        }
        hooks.fire_on_metrics(pipeline_context)
        return await self._manager.get_metrics()

    async def get_manifest(self) -> PlatformManifest:
        """Get the platform manifest."""
        pipeline_context = {
            "timestamp": datetime.now(UTC).isoformat(),
        }
        hooks.fire_on_manifest(pipeline_context)
        return await self._manager.get_manifest()

    async def get_trace(self, trace_id: str) -> PlatformTrace | None:
        """Get a specific trace by ID.

        This is a convenience method — the actual trace data is
        managed by the TraceManager inside the coordinator.
        For now, returns a not-found response.
        """
        return None

    async def list_traces(self) -> list[PlatformTrace]:
        """List all platform traces.

        This is a convenience method — delegates to the coordinator's
        trace manager. For now, returns an empty list.
        """
        return []
