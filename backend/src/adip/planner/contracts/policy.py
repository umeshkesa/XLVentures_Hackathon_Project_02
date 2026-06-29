"""PlanningPolicy — configurable thresholds and strategies."""

from __future__ import annotations

from pydantic import BaseModel, Field


class PlanningPolicy(BaseModel):
    """Enterprise planning policy with configurable thresholds.

    Controls planner behaviour without hardcoded values.
    """
    auto_execute_threshold: float = Field(
        default=70.0,
        description="Confidence (0-100) above which plans auto-execute",
        ge=0.0,
        le=100.0,
    )
    confirmation_threshold: float = Field(
        default=50.0,
        description="Confidence (0-100) above which user confirmation is requested",
        ge=0.0,
        le=100.0,
    )
    clarification_threshold: float = Field(
        default=30.0,
        description="Confidence (0-100) below which clarification is needed",
        ge=0.0,
        le=100.0,
    )
    max_replans: int = Field(
        default=3,
        description="Maximum number of replanning attempts",
        ge=0,
    )
    max_parallel_tasks: int = Field(
        default=10,
        description="Maximum tasks allowed in a parallel group",
        ge=1,
    )
    optimization_enabled: bool = Field(
        default=True,
        description="Whether plan optimisation is applied",
    )
    confidence_strategy: str = Field(
        default="weighted_average",
        description="Strategy: weighted_average, minimum, maximum",
    )
