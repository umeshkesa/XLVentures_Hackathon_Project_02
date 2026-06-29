"""Data Transfer Objects (DTOs) for planner requests and responses."""

from __future__ import annotations

from adip.planner.contracts.models import (
    PlanningRequest,
    PlanningResult,
)


class InitiatePlanningRequestDTO(PlanningRequest):
    """DTO for initiating a planning request."""
    # Inherits context, goal, metrics from PlanningRequest


class PlannerResponseDTO(PlanningResult):
    """DTO for the planner's response."""
    # Inherits request_id, plan, final_decision, validation_status,
    # execution_status, metrics from PlanningResult
    pass
