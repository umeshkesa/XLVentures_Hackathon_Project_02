"""Domain models for the Action Manager.

Defines all domain models used across action contracts,
interfaces, and execution components.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field
from pydantic.types import UUID4

from adip.actions.enums import (
    ActionPriority as ActionPriorityEnum,
)
from adip.actions.enums import (
    ActionType as ActionTypeEnum,
)
from adip.actions.enums import (
    ExecutionReadiness as ExecutionReadinessEnum,
)


class ActionRequest(BaseModel):
    """Request to initiate an action planning operation.

    Captures the input parameters for planning an action,
    including the approved review decision ID and contextual
    information needed to build an ActionPlan.
    """

    request_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique request identifier",
    )
    review_decision_id: UUID4 = Field(
        description="The approved review decision ID",
    )
    action_type: ActionTypeEnum = Field(
        default=ActionTypeEnum.AUTOMATED,
        description="Type of action to plan",
    )
    priority: ActionPriorityEnum = Field(
        default=ActionPriorityEnum.MEDIUM,
        description="Priority of the action",
    )
    domain: str = Field(
        default="",
        description="Domain for this action operation",
    )
    target: str = Field(
        default="",
        description="Target entity for the action",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional request metadata",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the request was created",
    )


class ActionPlanStep(BaseModel):
    """A single step within an ActionPlan.

    Each step represents one atomic action with its own
    type, parameters, dependencies, preconditions, and
    rollback information.
    """

    step_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique step identifier",
    )
    plan_id: UUID4 = Field(
        description="The plan this step belongs to",
    )
    name: str = Field(
        default="",
        description="Name of the step",
    )
    description: str = Field(
        default="",
        description="Description of the step",
    )
    action_type: ActionTypeEnum = Field(
        description="Type of action for this step",
    )
    priority: ActionPriorityEnum = Field(
        default=ActionPriorityEnum.MEDIUM,
        description="Priority of this step",
    )
    order: int = Field(
        default=0,
        ge=0,
        description="Execution order of this step",
    )
    parameters: dict[str, Any] = Field(
        default_factory=dict,
        description="Parameters for step execution",
    )
    dependencies: list[UUID4] = Field(
        default_factory=list,
        description="IDs of steps this step depends on",
    )
    preconditions: list[ActionPrecondition] = Field(
        default_factory=list,
        description="Preconditions that must be met before execution",
    )
    postconditions: list[ActionPostcondition] = Field(
        default_factory=list,
        description="Postconditions that must hold after execution",
    )
    rollback_step_id: UUID4 | None = Field(
        default=None,
        description="Step ID to execute for rollback if this step fails",
    )
    timeout_seconds: int = Field(
        default=300,
        ge=0,
        description="Timeout for step execution in seconds",
    )
    retry_count: int = Field(
        default=0,
        ge=0,
        description="Number of retry attempts on failure",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional step metadata",
    )


class ActionPlan(BaseModel):
    """An executable plan comprising multiple ActionPlanSteps.

    The ActionPlan transforms an approved ReviewDecision into
    a structured set of steps with dependencies, resources,
    schedule, and an integrated rollback plan.
    """

    plan_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique plan identifier",
    )
    request_id: UUID4 = Field(
        description="The request this plan belongs to",
    )
    review_decision_id: UUID4 = Field(
        description="The approved review decision ID",
    )
    name: str = Field(
        default="",
        description="Name of the action plan",
    )
    description: str = Field(
        default="",
        description="Description of the action plan",
    )
    steps: list[ActionPlanStep] = Field(
        default_factory=list,
        description="Ordered list of execution steps",
    )
    rollback_plan: RollbackPlan | None = Field(
        default=None,
        description="Rollback plan for reverting this action",
    )
    dependencies: list[ActionDependency] = Field(
        default_factory=list,
        description="External dependencies for this plan",
    )
    resource_allocation: ResourceAllocation | None = Field(
        default=None,
        description="Resources allocated for this plan",
    )
    schedule: ActionSchedule | None = Field(
        default=None,
        description="Schedule for executing this plan",
    )
    is_primary: bool = Field(
        default=True,
        description="Whether this is the primary plan (vs. rollback)",
    )
    status: str = Field(
        default="DRAFT",
        description="Status of the action plan",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional plan metadata",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the plan was created",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the plan was last updated",
    )


class ActionDecision(BaseModel):
    """Decision produced by the Action Manager.

    Captures the complete action planning outcome including
    the generated plan, readiness assessment, and any issues
    encountered during planning.
    """

    decision_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique decision identifier",
    )
    request_id: UUID4 = Field(
        description="The request this decision belongs to",
    )
    plan: ActionPlan | None = Field(
        default=None,
        description="The generated action plan",
    )
    readiness: ExecutionReadinessEnum = Field(
        default=ExecutionReadinessEnum.WAITING,
        description="Readiness status for execution",
    )
    readiness_reason: str = Field(
        default="",
        description="Reason for the readiness assessment",
    )
    is_ready: bool = Field(
        default=False,
        description="Whether the plan is ready for execution",
    )
    issues: list[str] = Field(
        default_factory=list,
        description="Issues identified during planning",
    )
    warnings: list[str] = Field(
        default_factory=list,
        description="Warnings identified during planning",
    )
    confidence: ActionConfidence | None = Field(
        default=None,
        description="Confidence assessment for this decision",
    )
    explainability: ActionExplainabilityMetadata | None = Field(
        default=None,
        description="Explainability metadata for this decision",
    )
    quality_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Quality score of the plan",
    )
    readiness_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Readiness score for execution",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional decision metadata",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the decision was made",
    )


class ActionSession(BaseModel):
    """Session tracking for an action planning operation.

    Captures the lifecycle of an action planning session,
    including status transitions, timing, and contextual
    information.
    """

    session_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique session identifier",
    )
    request_id: UUID4 = Field(
        description="The request this session belongs to",
    )
    plan_id: UUID4 | None = Field(
        default=None,
        description="The plan this session is associated with",
    )
    status: str = Field(
        default="INITIALIZED",
        description="Current status of the session",
    )
    started_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the session was started",
    )
    completed_at: datetime | None = Field(
        default=None,
        description="When the session was completed",
    )
    action_type: ActionTypeEnum = Field(
        default=ActionTypeEnum.AUTOMATED,
        description="Type of action being planned",
    )
    priority: ActionPriorityEnum = Field(
        default=ActionPriorityEnum.MEDIUM,
        description="Priority of the action",
    )
    decision_id: UUID4 | None = Field(
        default=None,
        description="The decision associated with this session",
    )
    step_count: int = Field(
        default=0,
        ge=0,
        description="Number of steps in the plan",
    )
    has_rollback: bool = Field(
        default=False,
        description="Whether the plan has rollback configured",
    )
    statistics: dict[str, Any] = Field(
        default_factory=dict,
        description="Session statistics",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional session metadata",
    )


class ActionContext(BaseModel):
    """Contextual information for an action planning operation.

    Provides asset, machine, facility, and workflow context
    to inform the action planning process.
    """

    context_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique context identifier",
    )
    request_id: UUID4 = Field(
        description="The request this context belongs to",
    )
    review_decision_id: UUID4 = Field(
        description="The review decision providing context",
    )
    asset_id: str = Field(
        default="",
        description="Identifier of the related asset",
    )
    machine_id: str = Field(
        default="",
        description="Identifier of the related machine",
    )
    facility_id: str = Field(
        default="",
        description="Identifier of the related facility",
    )
    workflow_id: str = Field(
        default="",
        description="Identifier of the related workflow",
    )
    domain: str = Field(
        default="",
        description="Domain for this action context",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context metadata",
    )


class ActionDependency(BaseModel):
    """Dependency definition for an action plan.

    Describes an external dependency that must be satisfied
    before the action plan can be executed.
    """

    dependency_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique dependency identifier",
    )
    plan_id: UUID4 = Field(
        description="The plan this dependency belongs to",
    )
    name: str = Field(
        default="",
        description="Name of the dependency",
    )
    description: str = Field(
        default="",
        description="Description of the dependency",
    )
    dependency_type: str = Field(
        default="",
        description="Type of dependency (resource, service, approval, etc.)",
    )
    required: bool = Field(
        default=True,
        description="Whether this dependency is required",
    )
    satisfied: bool = Field(
        default=False,
        description="Whether this dependency has been satisfied",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional dependency metadata",
    )


class ActionPrecondition(BaseModel):
    """Precondition that must be met before action execution.

    Defines a condition that must evaluate to true before
    an action step can be executed.
    """

    precondition_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique precondition identifier",
    )
    step_id: UUID4 = Field(
        description="The step this precondition belongs to",
    )
    name: str = Field(
        default="",
        description="Name of the precondition",
    )
    description: str = Field(
        default="",
        description="Description of the precondition",
    )
    condition: str = Field(
        default="",
        description="The condition expression or description",
    )
    met: bool = Field(
        default=False,
        description="Whether this precondition is currently met",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional precondition metadata",
    )


class ActionPostcondition(BaseModel):
    """Postcondition that must hold after action execution.

    Defines a condition that must evaluate to true after
    an action step has been executed to confirm success.
    """

    postcondition_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique postcondition identifier",
    )
    step_id: UUID4 = Field(
        description="The step this postcondition belongs to",
    )
    name: str = Field(
        default="",
        description="Name of the postcondition",
    )
    description: str = Field(
        default="",
        description="Description of the postcondition",
    )
    condition: str = Field(
        default="",
        description="The condition expression or description",
    )
    verified: bool = Field(
        default=False,
        description="Whether this postcondition has been verified",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional postcondition metadata",
    )


class RollbackPlan(BaseModel):
    """Rollback plan for reverting an action.

    Defines the steps and dependencies required to safely
    roll back an action plan in case of failure or
    cancellation.
    """

    rollback_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique rollback identifier",
    )
    plan_id: UUID4 = Field(
        description="The plan this rollback belongs to",
    )
    name: str = Field(
        default="",
        description="Name of the rollback plan",
    )
    description: str = Field(
        default="",
        description="Description of the rollback plan",
    )
    steps: list[ActionPlanStep] = Field(
        default_factory=list,
        description="Ordered list of rollback steps",
    )
    dependencies: list[ActionDependency] = Field(
        default_factory=list,
        description="Dependencies for the rollback plan",
    )
    resource_allocation: ResourceAllocation | None = Field(
        default=None,
        description="Resources allocated for rollback",
    )
    schedule: ActionSchedule | None = Field(
        default=None,
        description="Schedule for executing rollback",
    )
    auto_rollback: bool = Field(
        default=True,
        description="Whether rollback should execute automatically on failure",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional rollback metadata",
    )


class ResourceAllocation(BaseModel):
    """Resource allocation for an action plan.

    Specifies the resources required to execute an action
    plan, including personnel, equipment, and materials.
    """

    allocation_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique allocation identifier",
    )
    plan_id: UUID4 = Field(
        description="The plan this allocation belongs to",
    )
    personnel: list[str] = Field(
        default_factory=list,
        description="Personnel assigned to this plan",
    )
    equipment: list[str] = Field(
        default_factory=list,
        description="Equipment assigned to this plan",
    )
    materials: list[str] = Field(
        default_factory=list,
        description="Materials assigned to this plan",
    )
    estimated_duration_minutes: int = Field(
        default=0,
        ge=0,
        description="Estimated duration in minutes",
    )
    cost_estimate: float = Field(
        default=0.0,
        ge=0.0,
        description="Estimated cost of execution",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional allocation metadata",
    )


class ActionSchedule(BaseModel):
    """Schedule for executing an action plan.

    Defines when and under what conditions an action plan
    should be executed, including start time, deadlines,
    and scheduling constraints.
    """

    schedule_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique schedule identifier",
    )
    plan_id: UUID4 = Field(
        description="The plan this schedule belongs to",
    )
    scheduled_start: datetime | None = Field(
        default=None,
        description="Scheduled start time",
    )
    scheduled_end: datetime | None = Field(
        default=None,
        description="Scheduled end time",
    )
    deadline: datetime | None = Field(
        default=None,
        description="Deadline for completing the action",
    )
    max_duration_minutes: int = Field(
        default=0,
        ge=0,
        description="Maximum allowed duration in minutes",
    )
    schedule_window: str = Field(
        default="",
        description="Scheduling window or constraint description",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional schedule metadata",
    )


class ActionMetadata(BaseModel):
    """Metadata describing an action or action plan.

    Provides classification, tagging, and versioning
    information for action entities.
    """

    title: str = Field(
        default="",
        description="Title of the action",
    )
    description: str = Field(
        default="",
        description="Description of the action",
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Tags for categorizing the action",
    )
    category: str = Field(
        default="",
        description="Category of the action",
    )
    source: str = Field(
        default="",
        description="Source system of the action",
    )
    version: str = Field(
        default="1.0.0",
        description="Version of the action schema",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata",
    )


class ActionConfidence(BaseModel):
    """Confidence assessment for an action planning decision.

    Multi-dimensional confidence evaluation of the action plan
    covering resource, schedule, cost, risk, and feasibility
    dimensions.
    """

    overall_confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Overall confidence score",
    )
    resource_confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Confidence in resource availability",
    )
    schedule_confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Confidence in schedule feasibility",
    )
    cost_confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Confidence in cost estimates",
    )
    risk_confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Confidence in risk assessment",
    )
    feasibility_confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Confidence in plan feasibility",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional confidence metadata",
    )


class ActionExplainabilityMetadata(BaseModel):
    """Explainability metadata for action planning decisions.

    Provides human-readable explanations for key decisions
    made during the action planning pipeline.
    """

    why_plan_generated: str = Field(
        default="",
        description="Why the plan was generated this way",
    )
    why_step_ordered: str = Field(
        default="",
        description="Why steps are ordered as they are",
    )
    why_resource_allocated: str = Field(
        default="",
        description="Why resources were allocated as they were",
    )
    why_schedule_chosen: str = Field(
        default="",
        description="Why the schedule was chosen",
    )
    why_readiness_assessed: str = Field(
        default="",
        description="Why readiness was assessed as it was",
    )
    why_rollback_configured: str = Field(
        default="",
        description="Why rollback was (or was not) configured",
    )
    why_optimization_applied: str = Field(
        default="",
        description="Why optimization was applied as it was",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional explainability metadata",
    )


class ActionHealth(BaseModel):
    """Health status for the Action Manager.

    Provides a comprehensive view of the health of all
    action sub-components and overall system status.
    """

    overall_status: str = Field(
        default="",
        description="Overall health status",
    )
    service_status: str = Field(
        default="",
        description="Status of the action service",
    )
    manager_status: str = Field(
        default="",
        description="Status of the action manager",
    )
    coordinator_status: str = Field(
        default="",
        description="Status of the action coordinator",
    )
    planner_status: str = Field(
        default="",
        description="Status of the action planner",
    )
    dependency_resolver_status: str = Field(
        default="",
        description="Status of the dependency resolver",
    )
    resource_allocator_status: str = Field(
        default="",
        description="Status of the resource allocator",
    )
    schedule_planner_status: str = Field(
        default="",
        description="Status of the schedule planner",
    )
    rollback_planner_status: str = Field(
        default="",
        description="Status of the rollback planner",
    )
    readiness_validator_status: str = Field(
        default="",
        description="Status of the readiness validator",
    )
    confidence_calculator_status: str = Field(
        default="",
        description="Status of the confidence calculator",
    )
    session_manager_status: str = Field(
        default="",
        description="Status of the session manager",
    )
    version_manager_status: str = Field(
        default="",
        description="Status of the version manager",
    )
    lineage_status: str = Field(
        default="",
        description="Status of the lineage tracker",
    )
    snapshot_status: str = Field(
        default="",
        description="Status of the snapshot manager",
    )
    quality_manager_status: str = Field(
        default="",
        description="Status of the quality manager",
    )
    review_status: str = Field(
        default="",
        description="Status of the action review",
    )
    plan_count: int = Field(
        default=0,
        ge=0,
        description="Total number of action plans processed",
    )
    error_count: int = Field(
        default=0,
        ge=0,
        description="Total number of errors encountered",
    )
    average_planning_time_ms: float = Field(
        default=0.0,
        ge=0.0,
        description="Average planning time in milliseconds",
    )
    last_check: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the health was last checked",
    )


class ActionMetrics(BaseModel):
    """Metrics for the Action Manager.

    Captures operational metrics including plan counts,
    action types distribution, priority breakdowns, and
    readiness statuses.
    """

    plans_total: int = Field(
        default=0,
        ge=0,
        description="Total number of action plans created",
    )
    plans_ready: int = Field(
        default=0,
        ge=0,
        description="Total number of ready action plans",
    )
    plans_blocked: int = Field(
        default=0,
        ge=0,
        description="Total number of blocked action plans",
    )
    plans_waiting: int = Field(
        default=0,
        ge=0,
        description="Total number of waiting action plans",
    )
    plans_scheduled: int = Field(
        default=0,
        ge=0,
        description="Total number of scheduled action plans",
    )
    plans_with_rollback: int = Field(
        default=0,
        ge=0,
        description="Total number of plans with rollback configured",
    )
    average_steps_per_plan: float = Field(
        default=0.0,
        ge=0.0,
        description="Average number of steps per plan",
    )
    average_planning_time_ms: float = Field(
        default=0.0,
        ge=0.0,
        description="Average planning time in milliseconds",
    )
    plans_per_action_type: dict[str, int] = Field(
        default_factory=dict,
        description="Number of plans per action type",
    )
    plans_per_priority: dict[str, int] = Field(
        default_factory=dict,
        description="Number of plans per priority",
    )
    plans_per_domain: dict[str, int] = Field(
        default_factory=dict,
        description="Number of plans per domain",
    )
    sessions_total: int = Field(
        default=0,
        ge=0,
        description="Total number of action sessions",
    )
    readiness_total: int = Field(
        default=0,
        ge=0,
        description="Total number of readiness assessments",
    )
    optimizations_total: int = Field(
        default=0,
        ge=0,
        description="Total number of optimization runs",
    )
    reviews_total: int = Field(
        default=0,
        ge=0,
        description="Total number of plan reviews",
    )
    versions_total: int = Field(
        default=0,
        ge=0,
        description="Total number of plan versions",
    )
    snapshots_total: int = Field(
        default=0,
        ge=0,
        description="Total number of plan snapshots",
    )
    average_confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Average confidence across all decisions",
    )
    average_quality: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Average quality score across all plans",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the metrics were captured",
    )
