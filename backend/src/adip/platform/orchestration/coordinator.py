"""DefaultPlatformCoordinator — orchestrates the end-to-end pipeline."""

from __future__ import annotations

import time
import uuid
from typing import Any

import structlog

from adip.platform.contracts.models import (
    PlatformHealth,
    PlatformManifest,
    PlatformMetrics,
    PlatformRequest,
    PlatformResponse,
)
from adip.platform.enums import ModuleName, PipelineStage, PipelineStatus
from adip.platform.interfaces import (
    ExceptionMapper,
    HealthAggregator,
    ManifestBuilder,
    PlatformCoordinator,
    PlatformMetricsCollector,
    ServiceRegistry,
    TraceManager,
)

logger = structlog.get_logger(__name__)


class DefaultPlatformCoordinator(PlatformCoordinator):
    """Default platform coordinator.

    Orchestrates the full end-to-end pipeline by delegating to
    sub-components for each stage. Each stage is try-catch isolated
    so a single stage failure does not break the entire pipeline.
    """

    MODULE_TO_STAGE: dict[str, PipelineStage] = {
        ModuleName.PLANNER.value: PipelineStage.PLANNER,
        ModuleName.WORKFLOW.value: PipelineStage.WORKFLOW,
        ModuleName.MEMORY.value: PipelineStage.MEMORY,
        ModuleName.KNOWLEDGE.value: PipelineStage.KNOWLEDGE,
        ModuleName.RULES.value: PipelineStage.RULES,
        ModuleName.EVIDENCE.value: PipelineStage.EVIDENCE,
        ModuleName.REASONING.value: PipelineStage.REASONING,
        ModuleName.RECOMMENDATION.value: PipelineStage.RECOMMENDATION,
        ModuleName.EXPLAINABILITY.value: PipelineStage.EXPLAINABILITY,
        ModuleName.DECISION_REVIEW.value: PipelineStage.DECISION_REVIEW,
        ModuleName.ACTION_MANAGER.value: PipelineStage.ACTION_MANAGER,
        ModuleName.ACTION_ENGINE.value: PipelineStage.ACTION_ENGINE,
        ModuleName.ENERGY.value: PipelineStage.ENERGY,
    }

    ALL_STAGES: list[PipelineStage] = [
        PipelineStage.VALIDATION,
        PipelineStage.PLANNER,
        PipelineStage.WORKFLOW,
        PipelineStage.MEMORY,
        PipelineStage.KNOWLEDGE,
        PipelineStage.RULES,
        PipelineStage.EVIDENCE,
        PipelineStage.REASONING,
        PipelineStage.RECOMMENDATION,
        PipelineStage.EXPLAINABILITY,
        PipelineStage.DECISION_REVIEW,
        PipelineStage.ACTION_MANAGER,
        PipelineStage.ACTION_ENGINE,
        PipelineStage.ENERGY,
        PipelineStage.RESPONSE,
    ]

    def __init__(
        self,
        registry: ServiceRegistry,
        health_aggregator: HealthAggregator,
        trace_manager: TraceManager,
        metrics_collector: PlatformMetricsCollector,
        exception_mapper: ExceptionMapper,
        manifest_builder: ManifestBuilder,
    ) -> None:
        self._registry = registry
        self._health = health_aggregator
        self._trace = trace_manager
        self._metrics = metrics_collector
        self._exceptions = exception_mapper
        self._manifest = manifest_builder
        logger.debug("platform_coordinator.initialized")

    async def execute_pipeline(self, request: PlatformRequest) -> PlatformResponse:
        """Coordinate the full pipeline execution.

        Each stage is executed in order with per-stage timing, tracing,
        metrics, and exception isolation.
        """
        correlation_id = request.correlation_id or str(uuid.uuid4())
        pipeline_start = time.monotonic()

        stages_to_run = request.pipeline if request.pipeline else self.ALL_STAGES
        context: dict[str, Any] = dict(request.context)
        output: dict[str, Any] = {}
        stages_completed: list[PipelineStage] = []
        stages_failed: list[PipelineStage] = []
        errors: list[str] = []

        trace = self._trace.create_trace(correlation_id)

        for stage in stages_to_run:
            stage_start = time.monotonic()
            module_name = self._get_module_for_stage(stage)

            try:
                stage_result = self._execute_stage(stage, module_name, request.payload, context, output)
                context.update(stage_result.get("context", {}))
                output[stage.value] = stage_result.get("output", {})
                stages_completed.append(stage)

                stage_duration = (time.monotonic() - stage_start) * 1000
                self._trace.record_stage(
                    trace_id=str(trace.trace_id),
                    stage=stage,
                    module=module_name,
                    status="success",
                    duration_ms=round(stage_duration, 2),
                    details=stage_result.get("details", {}),
                )

                logger.debug("pipeline.stage_completed", stage=stage.value, duration_ms=round(stage_duration, 2))

            except Exception as exc:
                stage_duration = (time.monotonic() - stage_start) * 1000
                error_message = self._exceptions.map_exception(exc, stage)
                errors.append(error_message)
                stages_failed.append(stage)
                self._metrics.record_stage_error(stage)

                self._trace.record_stage(
                    trace_id=str(trace.trace_id),
                    stage=stage,
                    module=module_name,
                    status="failure",
                    duration_ms=round(stage_duration, 2),
                    details={"error": error_message, "exception": type(exc).__name__},
                )

                logger.warning("pipeline.stage_failed", stage=stage.value, error=error_message)
                # Continue to next stage (partial execution)

        total_duration = (time.monotonic() - pipeline_start) * 1000
        self._trace.complete_trace(str(trace.trace_id), round(total_duration, 2))

        # Determine final status
        if not stages_failed and len(stages_completed) == len(stages_to_run):
            status = PipelineStatus.COMPLETED
            success = True
        elif stages_completed and stages_failed:
            status = PipelineStatus.PARTIAL
            success = True
        else:
            status = PipelineStatus.FAILED
            success = False

        self._metrics.record_request(
            success=success,
            duration_ms=round(total_duration, 2),
            stages=stages_to_run,
        )

        logger.info(
            "pipeline.completed",
            correlation_id=correlation_id,
            status=status.value,
            stages_completed=len(stages_completed),
            stages_failed=len(stages_failed),
            duration_ms=round(total_duration, 2),
        )

        return PlatformResponse(
            request_id=request.request_id,
            correlation_id=correlation_id,
            success=success,
            status=status,
            stages_completed=stages_completed,
            stages_failed=stages_failed,
            output=output,
            errors=errors,
            duration_ms=round(total_duration, 2),
        )

    async def get_health(self) -> PlatformHealth:
        """Coordinate health aggregation."""
        return self._health.aggregate(self._registry)

    async def get_metrics(self) -> PlatformMetrics:
        """Coordinate metrics collection."""
        return self._metrics.get_snapshot()

    async def get_manifest(self) -> PlatformManifest:
        """Coordinate manifest generation."""
        return self._manifest.build(self._registry)

    def _execute_stage(
        self,
        stage: PipelineStage,
        module_name: str,
        payload: dict[str, Any],
        context: dict[str, Any],
        output: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute a single pipeline stage.

        Deterministic placeholder — returns stage-specific output
        based on the module.
        """
        if stage == PipelineStage.VALIDATION:
            return {
                "output": {"validated": True, "payload_size": len(str(payload))},
                "details": {"validation_type": "schema"},
            }

        if stage == PipelineStage.RESPONSE:
            return {
                "output": {"assembled": True, "modules_processed": len(output)},
                "details": {"response_format": "standard"},
            }

        # For domain stages, attempt to resolve the module's service
        stage_name = stage.value
        service_names = [
            f"{stage_name}_service",
            f"{stage_name}_manager",
            f"{module_name}_service",
        ]

        for svc_name in service_names:
            try:
                service = self._registry.resolve(svc_name)
                if hasattr(service, "handle_operation"):
                    result = service.handle_operation(stage_name, {
                        "payload": payload,
                        "context": context,
                        "previous_output": output,
                    })
                    return {
                        "output": result.data if hasattr(result, "data") else {"handled": True},
                        "context": {"last_stage": stage_name},
                        "details": {"service": svc_name, "operation": stage_name},
                    }
            except KeyError:
                continue

        # Default placeholder: return context-passing output
        return {
            "output": {
                "stage": stage_name,
                "module": module_name,
                "processed": True,
                "context_keys": list(context.keys()),
            },
            "context": {"last_stage": stage_name, "last_module": module_name},
            "details": {"resolved_service": None, "placeholder": True},
        }

    def _get_module_for_stage(self, stage: PipelineStage) -> str:
        """Get the module name for a pipeline stage."""
        for mod, stg in self.MODULE_TO_STAGE.items():
            if stg == stage:
                return mod
        return stage.value
