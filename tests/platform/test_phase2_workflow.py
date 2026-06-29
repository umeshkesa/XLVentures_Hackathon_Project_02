"""Phase 2 smoke tests — end-to-end workflow validation."""

from __future__ import annotations

import pytest

from adip.platform.contracts.models import PlatformRequest
from adip.platform.enums import ModuleName, PipelineStage, PipelineStatus
from adip.platform.orchestration.coordinator import DefaultPlatformCoordinator
from adip.platform.orchestration.exception_mapper import DefaultExceptionMapper
from adip.platform.orchestration.health_aggregator import DefaultHealthAggregator
from adip.platform.orchestration.manifest_builder import DefaultManifestBuilder
from adip.platform.orchestration.metrics_collector import DefaultPlatformMetricsCollector
from adip.platform.orchestration.pipeline_validator import DefaultPipelineValidator
from adip.platform.orchestration.registry import DefaultServiceRegistry
from adip.platform.orchestration.trace_manager import DefaultTraceManager


@pytest.fixture
def coordinator() -> DefaultPlatformCoordinator:
    registry = DefaultServiceRegistry()
    health = DefaultHealthAggregator()
    trace = DefaultTraceManager()
    metrics = DefaultPlatformMetricsCollector()
    exceptions = DefaultExceptionMapper()
    manifest = DefaultManifestBuilder()

    for mod_name in (ModuleName.PLANNER, ModuleName.WORKFLOW, ModuleName.MEMORY, ModuleName.KNOWLEDGE, ModuleName.RULES):
        registry.register(f"{mod_name.value}_service", object(), mod_name)

    return DefaultPlatformCoordinator(
        registry=registry,
        health_aggregator=health,
        trace_manager=trace,
        metrics_collector=metrics,
        exception_mapper=exceptions,
        manifest_builder=manifest,
    )


@pytest.fixture
def validator() -> DefaultPipelineValidator:
    return DefaultPipelineValidator()


class TestEndToEndWorkflow:
    """Verify the complete pipeline from request to EnergyDecision."""

    async def test_full_pipeline_produces_energy_output(
        self, coordinator: DefaultPlatformCoordinator, validator: DefaultPipelineValidator
    ) -> None:
        request = PlatformRequest(
            correlation_id="e2e-energy",
            payload={"asset_id": "solar-001", "action": "analyze"},
        )
        response = await validator.validate_pipeline(coordinator, request)
        assert response.success
        assert response.status == PipelineStatus.COMPLETED
        assert "energy" in response.output
        energy_output = response.output["energy"]
        assert energy_output is not None

    async def test_pipeline_produces_all_stages(
        self, coordinator: DefaultPlatformCoordinator, validator: DefaultPipelineValidator
    ) -> None:
        request = PlatformRequest(correlation_id="e2e-all-stages")
        response = await validator.validate_pipeline(coordinator, request)
        completed_names = {s.value for s in response.stages_completed}
        expected = {"validation", "planner", "workflow", "memory", "knowledge",
                     "rules", "evidence", "reasoning", "recommendation",
                     "explainability", "decision_review", "action_manager",
                     "action_engine", "energy", "response"}
        assert expected.issubset(completed_names)

    async def test_custom_stages_workflow(
        self, coordinator: DefaultPlatformCoordinator, validator: DefaultPipelineValidator
    ) -> None:
        request = PlatformRequest(
            correlation_id="e2e-custom",
            pipeline=[PipelineStage.MEMORY, PipelineStage.KNOWLEDGE, PipelineStage.RULES],
        )
        response = await validator.validate_pipeline(coordinator, request)
        assert response.success
        assert len(response.stages_completed) == 3

    async def test_single_stage_validation(
        self, coordinator: DefaultPlatformCoordinator, validator: DefaultPipelineValidator
    ) -> None:
        request = PlatformRequest(
            correlation_id="e2e-single",
            pipeline=[PipelineStage.ENERGY],
        )
        response = await validator.validate_pipeline(coordinator, request)
        assert response.success
        assert len(response.stages_completed) == 1
        assert response.stages_completed[0] == PipelineStage.ENERGY

    async def test_empty_request_defaults_to_all(
        self, coordinator: DefaultPlatformCoordinator, validator: DefaultPipelineValidator
    ) -> None:
        request = PlatformRequest(correlation_id="e2e-empty")
        response = await validator.validate_pipeline(coordinator, request)
        assert response.success
        assert len(response.stages_completed) == len(coordinator.ALL_STAGES)


class TestStageOrderValidation:
    """Verify stage order validation."""

    def test_valid_order(self, validator: DefaultPipelineValidator) -> None:
        stages = [
            PipelineStage.VALIDATION,
            PipelineStage.PLANNER,
            PipelineStage.WORKFLOW,
            PipelineStage.MEMORY,
        ]
        assert validator.validate_stage_order(stages)

    def test_invalid_order(self, validator: DefaultPipelineValidator) -> None:
        stages = [
            PipelineStage.ENERGY,
            PipelineStage.PLANNER,
        ]
        assert not validator.validate_stage_order(stages)

    def test_empty_stages(self, validator: DefaultPipelineValidator) -> None:
        assert not validator.validate_stage_order([])

    def test_full_pipeline_order(self, validator: DefaultPipelineValidator) -> None:
        stages = [
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
        assert validator.validate_stage_order(stages)


class TestFullOutputValidation:
    """Verify full pipeline output validation."""

    async def test_full_output_validation_passes(
        self, coordinator: DefaultPlatformCoordinator, validator: DefaultPipelineValidator
    ) -> None:
        request = PlatformRequest(correlation_id="e2e-output")
        response = await coordinator.execute_pipeline(request)
        messages = validator.validate_full_output(response)
        assert any(m.startswith("VALIDATION_OK") for m in messages)

    async def test_output_has_stage_keys(
        self, coordinator: DefaultPlatformCoordinator, validator: DefaultPipelineValidator
    ) -> None:
        request = PlatformRequest(correlation_id="e2e-keys")
        response = await coordinator.execute_pipeline(request)
        assert "energy" in response.output
        assert "planner" in response.output
