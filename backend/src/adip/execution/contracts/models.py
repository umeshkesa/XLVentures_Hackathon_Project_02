"""Domain models for the Action Engine.

Defines all domain models used across execution contracts,
interfaces, and execution components.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field
from pydantic.types import UUID4

from adip.execution.enums import ExecutionMode, ExecutionPriority, ExecutionState


class ExecutionRequest(BaseModel):
    """Request to initiate an execution operation.

    Captures the input parameters for executing an action plan,
    including the action decision ID and execution mode.
    """

    request_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique request identifier",
    )
    action_decision_id: UUID4 = Field(
        description="The action decision ID to execute",
    )
    execution_mode: ExecutionMode = Field(
        default=ExecutionMode.LIVE,
        description="Mode of execution",
    )
    priority: ExecutionPriority = Field(
        default=ExecutionPriority.MEDIUM,
        description="Priority of the execution",
    )
    domain: str = Field(
        default="",
        description="Domain for this execution operation",
    )
    target: str = Field(
        default="",
        description="Target entity for the execution",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional request metadata",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the request was created",
    )


class RetryPolicy(BaseModel):
    """Policy for retrying failed execution tasks.

    Defines the conditions and limits for automatic retry
    of tasks that fail during execution.
    """

    max_retries: int = Field(
        default=3,
        ge=0,
        le=100,
        description="Maximum number of retry attempts",
    )
    retry_delay_seconds: int = Field(
        default=30,
        ge=0,
        description="Initial delay before first retry in seconds",
    )
    backoff_multiplier: float = Field(
        default=2.0,
        ge=1.0,
        description="Multiplier for exponential backoff",
    )
    max_delay_seconds: int = Field(
        default=3600,
        ge=0,
        description="Maximum delay between retries in seconds",
    )
    retry_on_timeout: bool = Field(
        default=True,
        description="Whether to retry on timeout",
    )
    retry_on_error: bool = Field(
        default=True,
        description="Whether to retry on error",
    )
    retryable_errors: list[str] = Field(
        default_factory=list,
        description="List of error types that should be retried",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional retry policy metadata",
    )


class CompensationTask(BaseModel):
    """A single compensation step within a CompensationPlan.

    Defines a task that reverses or compensates for a
    previously executed task during rollback.
    """

    compensation_task_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique compensation task identifier",
    )
    original_task_id: UUID4 = Field(
        description="The ID of the task being compensated for",
    )
    name: str = Field(
        default="",
        description="Name of the compensation task",
    )
    description: str = Field(
        default="",
        description="Description of the compensation task",
    )
    order: int = Field(
        default=0,
        ge=0,
        description="Execution order of this compensation step",
    )
    parameters: dict[str, Any] = Field(
        default_factory=dict,
        description="Parameters for compensation execution",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional compensation task metadata",
    )


class CompensationPlan(BaseModel):
    """Plan for compensating or rolling back execution.

    Defines the steps required to safely undo or compensate
    for completed tasks when execution fails or is cancelled.
    """

    compensation_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique compensation identifier",
    )
    package_id: UUID4 = Field(
        description="The execution package this plan belongs to",
    )
    name: str = Field(
        default="",
        description="Name of the compensation plan",
    )
    description: str = Field(
        default="",
        description="Description of the compensation plan",
    )
    tasks: list[CompensationTask] = Field(
        default_factory=list,
        description="Ordered list of compensation tasks",
    )
    auto_compensate: bool = Field(
        default=True,
        description="Whether to compensate automatically on failure",
    )
    timeout_seconds: int = Field(
        default=300,
        ge=0,
        description="Timeout for compensation execution in seconds",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional compensation plan metadata",
    )


class ExecutionSchedule(BaseModel):
    """Schedule for executing an execution package.

    Defines when and under what conditions an execution package
    should be executed, including start time and deadlines.
    """

    schedule_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique schedule identifier",
    )
    package_id: UUID4 = Field(
        description="The execution package this schedule belongs to",
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
        description="Deadline for completing execution",
    )
    max_duration_minutes: int = Field(
        default=0,
        ge=0,
        description="Maximum allowed duration in minutes",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional schedule metadata",
    )


class ExecutionTask(BaseModel):
    """A single executable task within an ExecutionPackage.

    Each task represents one atomic execution unit with its
    own parameters, dependencies, and retry configuration.
    """

    task_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique task identifier",
    )
    package_id: UUID4 = Field(
        description="The execution package this task belongs to",
    )
    name: str = Field(
        default="",
        description="Name of the task",
    )
    description: str = Field(
        default="",
        description="Description of the task",
    )
    order: int = Field(
        default=0,
        ge=0,
        description="Execution order of this task",
    )
    task_type: str = Field(
        default="",
        description="Type of task (script, command, api, etc.)",
    )
    parameters: dict[str, Any] = Field(
        default_factory=dict,
        description="Parameters for task execution",
    )
    dependencies: list[UUID4] = Field(
        default_factory=list,
        description="IDs of tasks this task depends on",
    )
    timeout_seconds: int = Field(
        default=300,
        ge=0,
        description="Timeout for task execution in seconds",
    )
    retry_count: int = Field(
        default=0,
        ge=0,
        description="Number of retry attempts on failure",
    )
    state: ExecutionState = Field(
        default=ExecutionState.PENDING,
        description="Current state of the task",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional task metadata",
    )


class ExecutionTaskResult(BaseModel):
    """Result of executing a single ExecutionTask.

    Captures the outcome, output, and timing of a task
    execution, including error information if it failed.
    """

    result_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique result identifier",
    )
    task_id: UUID4 = Field(
        description="The task this result belongs to",
    )
    success: bool = Field(
        default=False,
        description="Whether the task completed successfully",
    )
    output: str = Field(
        default="",
        description="Output produced by the task",
    )
    error_message: str = Field(
        default="",
        description="Error message if the task failed",
    )
    error_code: str = Field(
        default="",
        description="Error code if the task failed",
    )
    started_at: datetime | None = Field(
        default=None,
        description="When the task started execution",
    )
    completed_at: datetime | None = Field(
        default=None,
        description="When the task completed execution",
    )
    duration_ms: int = Field(
        default=0,
        ge=0,
        description="Duration of task execution in milliseconds",
    )
    retry_attempt: int = Field(
        default=0,
        ge=0,
        description="Which retry attempt this result belongs to",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional result metadata",
    )


class ExecutionResult(BaseModel):
    """Overall result of executing an ExecutionPackage.

    Aggregates all task results and provides a summary
    of the entire execution operation.
    """

    result_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique result identifier",
    )
    request_id: UUID4 = Field(
        description="The request this result belongs to",
    )
    session_id: UUID4 = Field(
        description="The session this result belongs to",
    )
    overall_success: bool = Field(
        default=False,
        description="Whether the overall execution succeeded",
    )
    task_results: list[ExecutionTaskResult] = Field(
        default_factory=list,
        description="Results of individual tasks",
    )
    error_message: str = Field(
        default="",
        description="Overall error message if execution failed",
    )
    started_at: datetime | None = Field(
        default=None,
        description="When execution started",
    )
    completed_at: datetime | None = Field(
        default=None,
        description="When execution completed",
    )
    total_duration_ms: int = Field(
        default=0,
        ge=0,
        description="Total execution duration in milliseconds",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional result metadata",
    )


class ExecutionPackage(BaseModel):
    """Package containing everything needed for execution.

    Combines tasks, dependencies, resources, timeline, retry
    policy, and compensation plan into a single executable unit
    produced by the Action Manager.
    """

    package_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique package identifier",
    )
    action_decision_id: UUID4 = Field(
        description="The action decision this package is based on",
    )
    name: str = Field(
        default="",
        description="Name of the execution package",
    )
    description: str = Field(
        default="",
        description="Description of the execution package",
    )
    tasks: list[ExecutionTask] = Field(
        default_factory=list,
        description="Tasks to be executed",
    )
    dependencies: list[UUID4] = Field(
        default_factory=list,
        description="External dependency IDs",
    )
    schedule: ExecutionSchedule | None = Field(
        default=None,
        description="Schedule for executing tasks",
    )
    retry_policy: RetryPolicy | None = Field(
        default=None,
        description="Retry policy for failed tasks",
    )
    compensation_plan: CompensationPlan | None = Field(
        default=None,
        description="Plan for compensating on failure",
    )
    state: ExecutionState = Field(
        default=ExecutionState.PENDING,
        description="Current state of the package",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional package metadata",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the package was created",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the package was last updated",
    )


class ExecutionSession(BaseModel):
    """Session tracking for an execution operation.

    Captures the lifecycle of an execution session including
    state transitions, timing, and task progress.
    """

    session_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique session identifier",
    )
    request_id: UUID4 = Field(
        description="The request this session belongs to",
    )
    package_id: UUID4 = Field(
        description="The execution package this session is executing",
    )
    state: ExecutionState = Field(
        default=ExecutionState.PENDING,
        description="Current state of the session",
    )
    execution_mode: ExecutionMode = Field(
        default=ExecutionMode.LIVE,
        description="Mode of execution",
    )
    priority: ExecutionPriority = Field(
        default=ExecutionPriority.MEDIUM,
        description="Priority of the execution",
    )
    started_at: datetime | None = Field(
        default=None,
        description="When the session started",
    )
    completed_at: datetime | None = Field(
        default=None,
        description="When the session completed",
    )
    task_count: int = Field(
        default=0,
        ge=0,
        description="Total number of tasks in the package",
    )
    tasks_completed: int = Field(
        default=0,
        ge=0,
        description="Number of completed tasks",
    )
    tasks_failed: int = Field(
        default=0,
        ge=0,
        description="Number of failed tasks",
    )
    tasks_skipped: int = Field(
        default=0,
        ge=0,
        description="Number of skipped tasks",
    )
    error_message: str = Field(
        default="",
        description="Error message if execution failed",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional session metadata",
    )


class ExecutionContext(BaseModel):
    """Contextual information for an execution operation.

    Provides asset, machine, facility, and workflow context
    to inform the execution process.
    """

    context_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique context identifier",
    )
    request_id: UUID4 = Field(
        description="The request this context belongs to",
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
        description="Domain for this execution context",
    )
    sandbox: ExecutionSandbox | None = Field(
        default=None,
        description="Sandbox configuration for isolation",
    )
    adapter: ExecutionAdapter | None = Field(
        default=None,
        description="Adapter configuration for external systems",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context metadata",
    )


class ExecutionSandbox(BaseModel):
    """Sandbox configuration for isolated execution.

    Defines the isolation boundaries, resource limits, and
    permissions for executing tasks in a sandboxed environment.
    """

    sandbox_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique sandbox identifier",
    )
    name: str = Field(
        default="",
        description="Name of the sandbox",
    )
    namespace: str = Field(
        default="default",
        description="Namespace for execution isolation",
    )
    resource_limits: dict[str, float] = Field(
        default_factory=dict,
        description="Resource limits (cpu, memory, etc.)",
    )
    permissions: list[str] = Field(
        default_factory=list,
        description="Permissions granted within the sandbox",
    )
    enabled: bool = Field(
        default=True,
        description="Whether sandbox isolation is enabled",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional sandbox metadata",
    )


class ExecutionAdapter(BaseModel):
    """Adapter configuration for external system integration.

    Defines how the execution engine connects to and communicates
    with external systems, services, or devices.
    """

    adapter_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique adapter identifier",
    )
    name: str = Field(
        default="",
        description="Name of the adapter",
    )
    adapter_type: str = Field(
        default="",
        description="Type of adapter (mqtt, http, k8s, etc.)",
    )
    configuration: dict[str, Any] = Field(
        default_factory=dict,
        description="Adapter configuration parameters",
    )
    enabled: bool = Field(
        default=True,
        description="Whether this adapter is enabled",
    )
    version: str = Field(
        default="1.0.0",
        description="Version of the adapter schema",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional adapter metadata",
    )


class ExecutionMetadata(BaseModel):
    """Metadata describing an execution or execution package.

    Provides classification, tagging, and versioning
    information for execution entities.
    """

    title: str = Field(
        default="",
        description="Title of the execution",
    )
    description: str = Field(
        default="",
        description="Description of the execution",
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Tags for categorizing the execution",
    )
    category: str = Field(
        default="",
        description="Category of the execution",
    )
    source: str = Field(
        default="",
        description="Source system of the execution",
    )
    version: str = Field(
        default="1.0.0",
        description="Version of the execution schema",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata",
    )


class ExecutionHealth(BaseModel):
    """Health status for the Action Engine.

    Provides a comprehensive view of the health of all
    execution sub-components and overall system status.
    Includes Phase 3.5 fields for scheduler, executor,
    retry, compensation, telemetry, and diagnostics.
    """

    overall_status: str = Field(
        default="",
        description="Overall health status",
    )
    coordinator_status: str = Field(
        default="",
        description="Status of the execution coordinator",
    )
    executor_status: str = Field(
        default="",
        description="Status of the task executor",
    )
    scheduler_status: str = Field(
        default="",
        description="Status of the execution scheduler",
    )
    retry_manager_status: str = Field(
        default="",
        description="Status of the retry manager",
    )
    compensation_manager_status: str = Field(
        default="",
        description="Status of the compensation manager",
    )
    monitor_status: str = Field(
        default="",
        description="Status of the execution monitor",
    )
    sandbox_status: str = Field(
        default="",
        description="Status of the sandbox executor",
    )
    telemetry_status: str = Field(
        default="",
        description="Status of the execution telemetry (Phase 3.5)",
    )
    diagnostics_status: str = Field(
        default="",
        description="Status of the runtime diagnostics (Phase 3.5)",
    )
    session_count: int = Field(
        default=0,
        ge=0,
        description="Total number of execution sessions",
    )
    active_tasks: int = Field(
        default=0,
        ge=0,
        description="Number of currently active tasks",
    )
    error_count: int = Field(
        default=0,
        ge=0,
        description="Total number of errors encountered",
    )
    average_latency_ms: float = Field(
        default=0.0,
        ge=0.0,
        description="Average operation latency in milliseconds (Phase 3.5)",
    )
    error_rate: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Error rate as a ratio (Phase 3.5)",
    )
    last_check: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the health was last checked",
    )


class ExecutionMetrics(BaseModel):
    """Metrics for the Action Engine.

    Captures operational metrics including session counts,
    task completions, retries, diagnostics, and performance
    statistics. Enhanced in Phase 3.5 with diagnostics,
    compliance, and recovery tracking.
    """

    sessions_total: int = Field(
        default=0,
        ge=0,
        description="Total number of execution sessions",
    )
    sessions_completed: int = Field(
        default=0,
        ge=0,
        description="Total number of completed sessions",
    )
    sessions_failed: int = Field(
        default=0,
        ge=0,
        description="Total number of failed sessions",
    )
    tasks_total: int = Field(
        default=0,
        ge=0,
        description="Total number of tasks",
    )
    tasks_completed: int = Field(
        default=0,
        ge=0,
        description="Total number of completed tasks",
    )
    tasks_failed: int = Field(
        default=0,
        ge=0,
        description="Total number of failed tasks",
    )
    tasks_skipped: int = Field(
        default=0,
        ge=0,
        description="Total number of skipped tasks",
    )
    retries_total: int = Field(
        default=0,
        ge=0,
        description="Total number of retry attempts",
    )
    compensations_total: int = Field(
        default=0,
        ge=0,
        description="Total number of compensations executed",
    )
    rollbacks_total: int = Field(
        default=0,
        ge=0,
        description="Total number of rollback operations (Phase 3.5)",
    )
    diagnostics_total: int = Field(
        default=0,
        ge=0,
        description="Total number of diagnostics events collected (Phase 3.5)",
    )
    sla_violations: int = Field(
        default=0,
        ge=0,
        description="Total number of SLA violations (Phase 3.5)",
    )
    completion_rate: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Overall completion rate (Phase 3.5)",
    )
    average_task_duration_ms: float = Field(
        default=0.0,
        ge=0.0,
        description="Average task duration in milliseconds",
    )
    average_session_duration_ms: float = Field(
        default=0.0,
        ge=0.0,
        description="Average session duration in milliseconds",
    )
    average_recovery_time_ms: float = Field(
        default=0.0,
        ge=0.0,
        description="Average recovery time in milliseconds (Phase 3.5)",
    )
    success_rate: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Overall execution success rate",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the metrics were captured",
    )


class ExecutionDecision(BaseModel):
    """Decision result of an execution pipeline run.

    Captures the outcome, session state, quality, confidence,
    compliance, diagnostics, and explainability of a completed
    execution operation.
    """

    decision_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique decision identifier",
    )
    request_id: UUID4 = Field(
        description="The execution request this decision belongs to",
    )
    session_id: UUID4 = Field(
        description="The execution session this decision belongs to",
    )
    result_id: UUID4 | None = Field(
        default=None,
        description="The execution result identifier",
    )
    overall_success: bool = Field(
        default=False,
        description="Whether the overall execution succeeded",
    )
    state: ExecutionState = Field(
        default=ExecutionState.PENDING,
        description="Final state of the execution",
    )
    tasks_total: int = Field(
        default=0,
        ge=0,
        description="Total number of tasks",
    )
    tasks_completed: int = Field(
        default=0,
        ge=0,
        description="Number of completed tasks",
    )
    tasks_failed: int = Field(
        default=0,
        ge=0,
        description="Number of failed tasks",
    )
    tasks_skipped: int = Field(
        default=0,
        ge=0,
        description="Number of skipped tasks",
    )
    retries_performed: int = Field(
        default=0,
        ge=0,
        description="Number of retries performed",
    )
    compensations_performed: int = Field(
        default=0,
        ge=0,
        description="Number of compensations performed",
    )
    quality_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Overall execution quality score",
    )
    compliance_status: str = Field(
        default="",
        description="Compliance validation status",
    )
    compliance_report: dict[str, Any] = Field(
        default_factory=dict,
        description="Compliance validation detail report",
    )
    diagnostics: dict[str, Any] = Field(
        default_factory=dict,
        description="Runtime diagnostics summary",
    )
    duration_ms: int = Field(
        default=0,
        ge=0,
        description="Total execution duration in milliseconds",
    )
    issues: list[str] = Field(
        default_factory=list,
        description="Issues encountered during execution",
    )
    warnings: list[str] = Field(
        default_factory=list,
        description="Warnings generated during execution",
    )
    confidence: ExecutionConfidence | None = Field(
        default=None,
        description="Confidence in the execution outcome",
    )
    explainability: ExecutionExplainabilityMetadata | None = Field(
        default=None,
        description="Explainability metadata for this decision",
    )
    correlation_id: str = Field(
        default="",
        description="Correlation ID for distributed tracing",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the decision was created",
    )


class ExecutionConfidence(BaseModel):
    """Multi-dimensional confidence for execution operations.

    Combines 7 weighted dimensions into an overall confidence
    score between 0.0 and 1.0: resource, schedule, risk,
    quality, readiness, retry, compensation.
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
        description="Resource availability confidence",
    )
    schedule_confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Schedule feasibility confidence",
    )
    risk_confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Risk assessment confidence",
    )
    quality_confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Execution quality confidence",
    )
    readiness_confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Readiness assessment confidence",
    )
    retry_confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Retry effectiveness confidence",
    )
    compensation_confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Compensation readiness confidence",
    )


class ExecutionExplainabilityMetadata(BaseModel):
    """Explainability metadata for execution decisions.

    Provides human-readable reasons for key decisions made
    during the execution pipeline.
    """

    why_session_created: str = Field(
        default="",
        description="Why the execution session was created",
    )
    why_task_ordered: str = Field(
        default="",
        description="Why tasks were ordered this way",
    )
    why_retry_used: str = Field(
        default="",
        description="Why retry was or was not used",
    )
    why_compensation_triggered: str = Field(
        default="",
        description="Why compensation was or was not triggered",
    )
    why_readiness_assessed: str = Field(
        default="",
        description="Why readiness was assessed this way",
    )
    why_cancelled: str = Field(
        default="",
        description="Why execution was cancelled (if applicable)",
    )


class ExecutionManifest(BaseModel):
    """Declaration of execution capabilities and requirements.

    Defines what an execution package requires in terms of
    adapters, sandboxes, resources, and policy constraints.
    """

    manifest_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique manifest identifier",
    )
    package_id: UUID4 = Field(
        description="The execution package this manifest belongs to",
    )
    required_adapters: list[str] = Field(
        default_factory=list,
        description="Required adapter types",
    )
    required_sandbox: bool = Field(
        default=False,
        description="Whether sandbox execution is required",
    )
    resource_limits: dict[str, float] = Field(
        default_factory=dict,
        description="Resource limit requirements",
    )
    timeout_seconds: int = Field(
        default=300,
        ge=0,
        description="Maximum execution timeout",
    )
    retry_policy: RetryPolicy | None = Field(
        default=None,
        description="Required retry policy",
    )
    compensation_required: bool = Field(
        default=False,
        description="Whether compensation must be configured",
    )
    policy_tags: list[str] = Field(
        default_factory=list,
        description="Policy tags for validation",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional manifest metadata",
    )
