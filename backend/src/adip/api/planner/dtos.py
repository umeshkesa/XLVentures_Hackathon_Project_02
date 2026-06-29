"""Transport contracts for future Planner API adapters."""

from __future__ import annotations

import uuid

from pydantic import BaseModel, ConfigDict, Field, JsonValue

from adip.core.planner.enums import PlannerStatus, PlanningStrategy, Priority
from adip.core.planner.models import PlanningResult


class PlannerRequestDTO(BaseModel):
    """External request payload accepted by a future Planner endpoint."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    goal: str = Field(min_length=1, max_length=5000)
    user_id: str | None = Field(default=None, min_length=1, max_length=200)
    session_id: str | None = Field(default=None, min_length=1, max_length=200)
    priority: Priority = Priority.NORMAL
    strategy: PlanningStrategy = PlanningStrategy.ADAPTIVE
    context: dict[str, JsonValue] = Field(default_factory=dict)


class PlannerResponseDTO(BaseModel):
    """External response envelope for a future Planner endpoint."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    request_id: uuid.UUID
    status: PlannerStatus
    result: PlanningResult | None = None
    message: str = ""
    errors: tuple[str, ...] = ()
