"""Planner event models — recorded during the planning lifecycle."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import UUID4, BaseModel, Field

from adip.planner.contracts.models import (
    ExecutionPlan,
    PlanningContext,
    PlanningDecision,
    PlanningGoal,
    PlanningMetrics,
    PlanningTask,
    PlanningTrace,
    ValidationResult,
)
from adip.planner.enums import PlanningStrategyEnum


class PlannerEvent(BaseModel):
    """Base event with enterprise fields."""
    event_id: UUID4 = Field(default_factory=uuid.uuid4)
    timestamp: datetime = Field(default_factory=datetime.now)
    planner_version: str = "0.1.0"
    request_id: UUID4 | None = None
    correlation_id: str = ""
    event_type: str = ""
    payload: dict[str, Any] = Field(default_factory=dict)


class PlanningStarted(PlannerEvent):
    goal: PlanningGoal
    context: PlanningContext
    strategy: PlanningStrategyEnum | None = None


class GoalAnalyzed(PlannerEvent):
    trace: PlanningTrace


class ContextAnalyzed(PlannerEvent):
    trace: PlanningTrace
    enriched_capabilities: list[str]


class StrategySelected(PlannerEvent):
    strategy: PlanningStrategyEnum
    trace: PlanningTrace


class CapabilitiesMatched(PlannerEvent):
    task_capability_pairs: list[dict[str, Any]]
    trace: PlanningTrace


class TasksDecomposed(PlannerEvent):
    tasks: list[PlanningTask]
    trace: PlanningTrace


class PlanGenerated(PlannerEvent):
    plan: ExecutionPlan
    trace: PlanningTrace


class PlanValidated(PlannerEvent):
    validation: ValidationResult
    trace: PlanningTrace


class PlanOptimized(PlannerEvent):
    original_task_count: int
    optimized_task_count: int
    optimization_reduction: float
    trace: PlanningTrace


class PlanningCompleted(PlannerEvent):
    plan: ExecutionPlan
    decision: PlanningDecision
    traces: list[PlanningTrace]
    metrics: PlanningMetrics


class PlanningFailed(PlannerEvent):
    error: str
    traces: list[PlanningTrace]
    metrics: PlanningMetrics
