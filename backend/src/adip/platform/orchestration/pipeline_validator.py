"""DefaultPipelineValidator — validates the complete end-to-end pipeline."""

from __future__ import annotations

import structlog

from adip.platform.contracts.models import PlatformRequest, PlatformResponse
from adip.platform.enums import PipelineStage
from adip.platform.interfaces import PipelineValidator, PlatformCoordinator

logger = structlog.get_logger(__name__)

# ── Correct pipeline stage order ─────────────────────────────────────
_CORRECT_ORDER: list[PipelineStage] = [
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

# ── Expected minimum output keys from a full pipeline run ────────────
_EXPECTED_STAGES: set[str] = {s.value for s in _CORRECT_ORDER}


class DefaultPipelineValidator(PipelineValidator):
    """Validates the complete end-to-end pipeline.

    Executes the full pipeline and validates:
    - All expected stages are present in the response
    - Stage order is correct
    - The pipeline produces a response with all expected keys
    """

    async def validate_pipeline(
        self,
        coordinator: PlatformCoordinator,
        request: PlatformRequest,
    ) -> PlatformResponse:
        logger.info("pipeline_validator.starting", stages=len(request.pipeline) if request.pipeline else "all")
        response = await coordinator.execute_pipeline(request)

        if response.success:
            logger.info(
                "pipeline_validator.completed",
                status=response.status.value,
                stages_completed=len(response.stages_completed),
                duration_ms=response.duration_ms,
            )
        else:
            logger.warning(
                "pipeline_validator.failed",
                status=response.status.value,
                errors=response.errors,
            )

        return response

    def validate_stage_order(self, stages: list[PipelineStage]) -> bool:
        if not stages:
            logger.warning("pipeline_validator.empty_stages")
            return False

        # Build position map for correct order
        correct_positions: dict[str, int] = {
            s.value: i for i, s in enumerate(_CORRECT_ORDER)
        }

        previous_pos = -1
        for stage in stages:
            pos = correct_positions.get(stage.value)
            if pos is None:
                logger.warning("pipeline_validator.unknown_stage", stage=stage.value)
                return False
            if pos <= previous_pos:
                logger.warning(
                    "pipeline_validator.out_of_order",
                    stage=stage.value,
                    pos=pos,
                    previous_pos=previous_pos,
                )
                return False
            previous_pos = pos

        logger.debug("pipeline_validator.order_valid", stages=[s.value for s in stages])
        return True

    def validate_full_output(self, response: PlatformResponse) -> list[str]:
        """Validate that the response contains all expected stages.

        Returns a list of validation messages.
        """
        messages: list[str] = []

        if response.success:
            messages.append("VALIDATION_OK: pipeline completed successfully")
        else:
            messages.append(f"VALIDATION_FAILED: pipeline status={response.status.value}")

        completed_set = {s.value for s in response.stages_completed}
        expected = _EXPECTED_STAGES
        missing = expected - completed_set
        if missing:
            messages.append(f"VALIDATION_WARNING: missing stages: {', '.join(sorted(missing))}")

        if response.stages_failed:
            messages.append(f"VALIDATION_WARNING: failed stages: {', '.join(s.value for s in response.stages_failed)}")

        if response.output:
            output_keys = set(response.output.keys())
            overlap = output_keys & expected
            messages.append(f"VALIDATION_OK: {len(overlap)}/{len(expected)} stages produced output")

        return messages
