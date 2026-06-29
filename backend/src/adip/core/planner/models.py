"""Validated data contracts shared by all planner pipeline components."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, JsonValue, model_validator

from adip.core.planner.enums import (
    ConfidenceLevel,
    PlannerStatus,
    PlanningStrategy,
    Priority,
    TaskStatus,
)

NonEmptyText = Annotated[str, Field(min_length=1)]


def utc_now() -> datetime:
    """Return a timezone-aware UTC timestamp for model factories."""
    return datetime.now(UTC)


class PlannerModel(BaseModel):
    """Strict, immutable base configuration for planner contracts."""

    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)


class PlanningContext(PlannerModel):
    """Domain-neutral facts and constraints available during planning."""

    user_id: str | None = Field(default=None, min_length=1, max_length=200)
    session_id: str | None = Field(default=None, min_length=1, max_length=200)
    correlation_id: str | None = Field(default=None, min_length=1, max_length=200)
    locale: str = Field(default="en", min_length=2, max_length=35)
    timezone: str = Field(default="UTC", min_length=1, max_length=100)
    available_inputs: frozenset[NonEmptyText] = Field(default_factory=frozenset)
    constraints: tuple[NonEmptyText, ...] = ()
    variables: dict[str, JsonValue] = Field(default_factory=dict)
    metadata: dict[str, JsonValue] = Field(default_factory=dict)
    prior_plan_id: uuid.UUID | None = None


class PlanningRequest(PlannerModel):
    """Normalized request accepted by a planner implementation."""

    request_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    goal: str = Field(min_length=1, max_length=5000)
    context: PlanningContext = Field(default_factory=PlanningContext)
    priority: Priority = Priority.NORMAL
    strategy: PlanningStrategy = PlanningStrategy.ADAPTIVE
    requested_at: datetime = Field(default_factory=utc_now)
    deadline: datetime | None = None

    @model_validator(mode="after")
    def validate_timestamps(self) -> PlanningRequest:
        """Require aware timestamps and a deadline after submission."""
        if self.requested_at.tzinfo is None:
            raise ValueError("requested_at must be timezone-aware")
        if self.deadline is not None:
            if self.deadline.tzinfo is None:
                raise ValueError("deadline must be timezone-aware")
            if self.deadline <= self.requested_at:
                raise ValueError("deadline must be after requested_at")
        return self


class PlanningGoal(PlannerModel):
    """A normalized goal produced by goal analysis."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    statement: str = Field(min_length=1, max_length=5000)
    success_criteria: tuple[NonEmptyText, ...] = Field(min_length=1)
    required_inputs: frozenset[NonEmptyText] = Field(default_factory=frozenset)
    desired_outputs: frozenset[NonEmptyText] = Field(default_factory=frozenset)
    priority: Priority = Priority.NORMAL
    confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM
    parent_goal_id: uuid.UUID | None = None

    @model_validator(mode="after")
    def reject_self_parent(self) -> PlanningGoal:
        """Prevent a goal from declaring itself as its parent."""
        if self.parent_goal_id == self.id:
            raise ValueError("A goal cannot be its own parent")
        return self


class CapabilityMatch(PlannerModel):
    """Planner-facing projection of one registry capability match."""

    capability_id: uuid.UUID
    capability_name: str = Field(min_length=1, max_length=200)
    category: str = Field(min_length=1, max_length=100)
    score: float = Field(ge=0.0, le=1.0)
    matched_tags: frozenset[NonEmptyText] = Field(default_factory=frozenset)
    matched_inputs: frozenset[NonEmptyText] = Field(default_factory=frozenset)
    matched_outputs: frozenset[NonEmptyText] = Field(default_factory=frozenset)
    missing_inputs: frozenset[NonEmptyText] = Field(default_factory=frozenset)
    reasons: tuple[NonEmptyText, ...] = ()


class PlanningTask(PlannerModel):
    """A single capability-backed node in an execution plan."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    goal_id: uuid.UUID
    name: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=2000)
    capability: CapabilityMatch
    inputs: dict[str, JsonValue] = Field(default_factory=dict)
    expected_outputs: frozenset[NonEmptyText] = Field(default_factory=frozenset)
    dependencies: frozenset[uuid.UUID] = Field(default_factory=frozenset)
    priority: Priority = Priority.NORMAL
    status: TaskStatus = TaskStatus.PENDING
    timeout_seconds: float = Field(default=60.0, gt=0)
    retry_limit: int = Field(default=0, ge=0)

    @model_validator(mode="after")
    def reject_self_dependency(self) -> PlanningTask:
        """Prevent a task from depending on itself."""
        if self.id in self.dependencies:
            raise ValueError("A task cannot depend on itself")
        return self


class ExecutionPlan(PlannerModel):
    """Validated task graph generated for one planning request."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    request_id: uuid.UUID
    goal: PlanningGoal
    tasks: tuple[PlanningTask, ...] = Field(min_length=1)
    strategy: PlanningStrategy
    status: PlannerStatus = PlannerStatus.READY
    version: int = Field(default=1, ge=1)
    created_at: datetime = Field(default_factory=utc_now)
    metadata: dict[str, JsonValue] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_task_graph_references(self) -> ExecutionPlan:
        """Require unique task IDs and dependencies contained in the plan."""
        task_ids = [task.id for task in self.tasks]
        if len(task_ids) != len(set(task_ids)):
            raise ValueError("Execution plan task IDs must be unique")
        known_ids = set(task_ids)
        for task in self.tasks:
            unknown = task.dependencies - known_ids
            if unknown:
                raise ValueError(f"Task '{task.id}' has dependencies outside the plan")
            if task.goal_id != self.goal.id:
                raise ValueError(f"Task '{task.id}' does not belong to the plan goal")
        if self.created_at.tzinfo is None:
            raise ValueError("created_at must be timezone-aware")
        return self


class PlanningDecision(PlannerModel):
    """Auditable decision emitted while producing a plan."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    plan_id: uuid.UUID
    decision_type: str = Field(min_length=1, max_length=100)
    rationale: str = Field(min_length=1, max_length=5000)
    selected_task_ids: tuple[uuid.UUID, ...] = ()
    alternatives: tuple[NonEmptyText, ...] = ()
    confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM
    created_at: datetime = Field(default_factory=utc_now)

    @model_validator(mode="after")
    def validate_created_at(self) -> PlanningDecision:
        """Require an auditable timezone-aware decision timestamp."""
        if self.created_at.tzinfo is None:
            raise ValueError("created_at must be timezone-aware")
        return self


class PlanningMetrics(PlannerModel):
    """Non-domain operational measurements for one planning run."""

    planning_duration_ms: float = Field(default=0.0, ge=0.0)
    goal_count: int = Field(default=0, ge=0)
    capability_match_count: int = Field(default=0, ge=0)
    task_count: int = Field(default=0, ge=0)
    validation_issue_count: int = Field(default=0, ge=0)
    optimization_count: int = Field(default=0, ge=0)
    replanning_count: int = Field(default=0, ge=0)


class ValidationResult(PlannerModel):
    """Structural validation outcome for a candidate execution plan."""

    is_valid: bool
    errors: tuple[NonEmptyText, ...] = ()
    warnings: tuple[NonEmptyText, ...] = ()
    checked_at: datetime = Field(default_factory=utc_now)

    @model_validator(mode="after")
    def validate_consistency(self) -> ValidationResult:
        """Keep the validity flag consistent with the error collection."""
        if self.is_valid and self.errors:
            raise ValueError("A valid result cannot contain errors")
        if not self.is_valid and not self.errors:
            raise ValueError("An invalid result must contain at least one error")
        if self.checked_at.tzinfo is None:
            raise ValueError("checked_at must be timezone-aware")
        return self


class PlanningResult(PlannerModel):
    """Final contract returned by a planner implementation."""

    request_id: uuid.UUID
    status: PlannerStatus
    plan: ExecutionPlan | None = None
    decisions: tuple[PlanningDecision, ...] = ()
    validation: ValidationResult | None = None
    metrics: PlanningMetrics = Field(default_factory=PlanningMetrics)
    clarification_question: str | None = Field(default=None, min_length=1)
    error_code: str | None = Field(default=None, min_length=1)
    error_message: str | None = Field(default=None, min_length=1)
    completed_at: datetime = Field(default_factory=utc_now)

    @model_validator(mode="after")
    def validate_status_payload(self) -> PlanningResult:
        """Require the payload associated with terminal result states."""
        if (
            self.status in {PlannerStatus.READY, PlannerStatus.DISPATCHED, PlannerStatus.COMPLETED}
            and self.plan is None
        ):
            raise ValueError(f"Status '{self.status}' requires an execution plan")
        if self.status is PlannerStatus.NEEDS_CLARIFICATION and not self.clarification_question:
            raise ValueError("Clarification status requires a question")
        if self.status is PlannerStatus.FAILED and not self.error_message:
            raise ValueError("Failed status requires an error message")
        if self.plan is not None and self.plan.request_id != self.request_id:
            raise ValueError("Result and execution plan request IDs must match")
        if self.plan is not None and any(
            decision.plan_id != self.plan.id for decision in self.decisions
        ):
            raise ValueError("Planning decisions must reference the result plan")
        if self.completed_at.tzinfo is None:
            raise ValueError("completed_at must be timezone-aware")
        return self
