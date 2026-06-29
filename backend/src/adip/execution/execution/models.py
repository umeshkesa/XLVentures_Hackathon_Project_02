"""Execution-layer models for the Action Engine Phase 2.

These models support internal processing: graph nodes/edges,
parallel groups, failure classifications, checkpoints, audit
records, progress tracking, telemetry, trace records, metrics
snapshots, and execution reports.
They are not exposed through the public ExecutionService API.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import UUID4, BaseModel, Field

from adip.execution.enums import ExecutionState


class ExecutionGraphNode(BaseModel):
    """A node in the execution dependency graph."""

    node_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique node identifier",
    )
    task_id: str = Field(
        default="",
        description="The execution task ID this node represents",
    )
    name: str = Field(
        default="",
        description="Name of the node/task",
    )
    duration_seconds: int = Field(
        default=0,
        ge=0,
        description="Estimated duration in seconds",
    )
    level: int = Field(
        default=0,
        ge=0,
        description="Topological level in the graph",
    )
    parallel_group: int = Field(
        default=0,
        ge=0,
        description="Parallel execution group ID",
    )
    state: ExecutionState = Field(
        default=ExecutionState.PENDING,
        description="Current state of this node",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional node metadata",
    )


class ExecutionGraphEdge(BaseModel):
    """A directed edge in the execution dependency graph."""

    edge_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique edge identifier",
    )
    source_node_id: str = Field(
        default="",
        description="Source node task ID",
    )
    target_node_id: str = Field(
        default="",
        description="Target node task ID",
    )
    dependency_type: str = Field(
        default="hard",
        description="Type of dependency (hard, soft, optional)",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional edge metadata",
    )


class ExecutionGraph(BaseModel):
    """Directed Acyclic Graph representing execution dependencies."""

    graph_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique graph identifier",
    )
    package_id: str = Field(
        default="",
        description="The execution package this graph belongs to",
    )
    nodes: list[ExecutionGraphNode] = Field(
        default_factory=list,
        description="Nodes in the graph",
    )
    edges: list[ExecutionGraphEdge] = Field(
        default_factory=list,
        description="Edges in the graph",
    )
    has_cycle: bool = Field(
        default=False,
        description="Whether the graph contains a cycle",
    )
    is_dag: bool = Field(
        default=True,
        description="Whether the graph is a valid DAG",
    )
    topological_order: list[str] = Field(
        default_factory=list,
        description="Topologically sorted task IDs",
    )
    parallel_groups: list[list[str]] = Field(
        default_factory=list,
        description="Groups of task IDs that can run in parallel",
    )


class FailureClassification(BaseModel):
    """Classification of an execution failure."""

    classification_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique classification identifier",
    )
    task_id: str = Field(
        default="",
        description="The task ID that failed",
    )
    failure_type: str = Field(
        default="transient",
        description="Type of failure: transient, permanent, infrastructure, dependency, policy, timeout",
    )
    error_message: str = Field(
        default="",
        description="Error message describing the failure",
    )
    is_retryable: bool = Field(
        default=True,
        description="Whether the failure is retryable",
    )
    requires_compensation: bool = Field(
        default=False,
        description="Whether compensation is required",
    )
    recovery_hint: str = Field(
        default="",
        description="Hint for recovery action",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional classification metadata",
    )


class Checkpoint(BaseModel):
    """A snapshot of execution state for resumption."""

    checkpoint_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique checkpoint identifier",
    )
    session_id: str = Field(
        default="",
        description="The session this checkpoint belongs to",
    )
    package_id: str = Field(
        default="",
        description="The package being checkpointed",
    )
    completed_task_ids: list[str] = Field(
        default_factory=list,
        description="Task IDs that have been completed",
    )
    failed_task_ids: list[str] = Field(
        default_factory=list,
        description="Task IDs that have failed",
    )
    in_progress_task_ids: list[str] = Field(
        default_factory=list,
        description="Task IDs that are in progress",
    )
    pending_task_ids: list[str] = Field(
        default_factory=list,
        description="Task IDs that are pending",
    )
    task_states: dict[str, ExecutionState] = Field(
        default_factory=dict,
        description="Map of task ID to current state",
    )
    state: ExecutionState = Field(
        default=ExecutionState.PENDING,
        description="Execution state at checkpoint",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the checkpoint was created",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional checkpoint metadata",
    )


class AuditRecord(BaseModel):
    """A single audit trail entry for execution."""

    record_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique audit record identifier",
    )
    session_id: str = Field(
        default="",
        description="The session this record belongs to",
    )
    event_type: str = Field(
        default="",
        description="Type of event (task_started, task_completed, checkpoint, retry, rollback, etc.)",
    )
    task_id: str = Field(
        default="",
        description="The task ID related to this event",
    )
    description: str = Field(
        default="",
        description="Description of the event",
    )
    details: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional event details",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the event occurred",
    )


class EventBusMessage(BaseModel):
    """A message published on the runtime event bus."""

    message_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique message identifier",
    )
    topic: str = Field(
        default="",
        description="Event topic (task, execution, checkpoint, retry, compensation)",
    )
    event_type: str = Field(
        default="",
        description="Type of event within the topic",
    )
    session_id: str = Field(
        default="",
        description="Session ID associated with this event",
    )
    task_id: str = Field(
        default="",
        description="Task ID associated with this event",
    )
    payload: dict[str, Any] = Field(
        default_factory=dict,
        description="Event payload data",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the message was published",
    )


class ProgressReport(BaseModel):
    """Report of execution progress at a point in time."""

    report_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique report identifier",
    )
    session_id: str = Field(
        default="",
        description="Session this progress relates to",
    )
    total_tasks: int = Field(
        default=0,
        ge=0,
        description="Total number of tasks",
    )
    completed_tasks: int = Field(
        default=0,
        ge=0,
        description="Number of completed tasks",
    )
    failed_tasks: int = Field(
        default=0,
        ge=0,
        description="Number of failed tasks",
    )
    in_progress_tasks: int = Field(
        default=0,
        ge=0,
        description="Number of in-progress tasks",
    )
    pending_tasks: int = Field(
        default=0,
        ge=0,
        description="Number of pending tasks",
    )
    overall_progress: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Overall progress as a ratio (0.0 to 1.0)",
    )
    state: ExecutionState = Field(
        default=ExecutionState.PENDING,
        description="Current execution state",
    )
    elapsed_seconds: float = Field(
        default=0.0,
        ge=0.0,
        description="Elapsed time in seconds",
    )
    estimated_remaining_seconds: float = Field(
        default=0.0,
        ge=0.0,
        description="Estimated remaining time in seconds",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the report was generated",
    )


class ResourceUsage(BaseModel):
    """Resource usage snapshot for monitoring."""

    usage_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique usage identifier",
    )
    session_id: str = Field(
        default="",
        description="Session this usage relates to",
    )
    active_workers: int = Field(
        default=0,
        ge=0,
        description="Number of active workers",
    )
    max_workers: int = Field(
        default=10,
        ge=0,
        description="Maximum available workers",
    )
    cpu_usage_percent: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="CPU usage percentage",
    )
    memory_usage_mb: float = Field(
        default=0.0,
        ge=0.0,
        description="Memory usage in MB",
    )
    runtime_seconds: float = Field(
        default=0.0,
        ge=0.0,
        description="Runtime in seconds",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the usage was captured",
    )


class TelemetryRecord(BaseModel):
    """A single telemetry data point."""

    record_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique telemetry record identifier",
    )
    session_id: str = Field(
        default="",
        description="Session this record belongs to",
    )
    metric_name: str = Field(
        default="",
        description="Name of the metric",
    )
    metric_value: float = Field(
        default=0.0,
        description="Value of the metric",
    )
    unit: str = Field(
        default="",
        description="Unit of measurement",
    )
    tags: dict[str, str] = Field(
        default_factory=dict,
        description="Tags associated with this metric",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the metric was recorded",
    )


class TraceRecord(BaseModel):
    """A single trace span for execution observability."""

    trace_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique trace identifier",
    )
    stage_name: str = Field(
        default="",
        description="Name of the pipeline stage",
    )
    session_id: str = Field(
        default="",
        description="Session ID for this trace",
    )
    task_id: str = Field(
        default="",
        description="Task ID for this trace",
    )
    operation: str = Field(
        default="",
        description="Operation being traced",
    )
    details: str = Field(
        default="",
        description="Details about the trace span",
    )
    duration_ms: float | None = Field(
        default=None,
        ge=0.0,
        description="Duration of the span in milliseconds",
    )
    success: bool = Field(
        default=True,
        description="Whether the operation succeeded",
    )
    correlation_id: str = Field(
        default="",
        description="Correlation ID for distributed tracing",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the trace was recorded",
    )


class MetricsSnapshot(BaseModel):
    """Snapshot of execution metrics at a point in time.

    Enhanced in Phase 3.5 with diagnostics, SLA violations,
    audit count, version count, and recovery time tracking.
    """

    snapshot_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique snapshot identifier",
    )
    sessions_total: int = Field(
        default=0,
        ge=0,
        description="Total number of execution sessions",
    )
    sessions_completed: int = Field(
        default=0,
        ge=0,
        description="Total number of completed sessions (Phase 3.5)",
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
    retries_total: int = Field(
        default=0,
        ge=0,
        description="Total number of retry attempts",
    )
    rollbacks_total: int = Field(
        default=0,
        ge=0,
        description="Total number of rollback operations",
    )
    compensations_total: int = Field(
        default=0,
        ge=0,
        description="Total number of compensations executed",
    )
    average_task_duration_ms: float = Field(
        default=0.0,
        ge=0.0,
        description="Average task duration in milliseconds",
    )
    total_runtime_ms: float = Field(
        default=0.0,
        ge=0.0,
        description="Total runtime in milliseconds",
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
    audit_count: int = Field(
        default=0,
        ge=0,
        description="Total number of audit operations (Phase 3.5)",
    )
    version_count: int = Field(
        default=0,
        ge=0,
        description="Total number of pipeline versions created (Phase 3.5)",
    )
    recovery_time_total_ms: float = Field(
        default=0.0,
        ge=0.0,
        description="Total recovery time in milliseconds (Phase 3.5)",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the snapshot was taken",
    )


class ExecutionReport(BaseModel):
    """Comprehensive execution report."""

    report_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique report identifier",
    )
    session_id: str = Field(
        default="",
        description="Session this report describes",
    )
    package_id: str = Field(
        default="",
        description="Package this report describes",
    )
    overall_success: bool = Field(
        default=False,
        description="Whether execution was successful",
    )
    final_state: ExecutionState = Field(
        default=ExecutionState.PENDING,
        description="Final state of execution",
    )
    total_tasks: int = Field(
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
    rollbacks_performed: int = Field(
        default=0,
        ge=0,
        description="Number of rollbacks performed",
    )
    compensations_performed: int = Field(
        default=0,
        ge=0,
        description="Number of compensations performed",
    )
    total_duration_ms: float = Field(
        default=0.0,
        ge=0.0,
        description="Total execution duration in milliseconds",
    )
    failure_summary: str = Field(
        default="",
        description="Summary of failures encountered",
    )
    failure_details: list[FailureClassification] = Field(
        default_factory=list,
        description="Details of each failure",
    )
    audit_entries: list[AuditRecord] = Field(
        default_factory=list,
        description="Audit trail entries",
    )
    metrics: MetricsSnapshot | None = Field(
        default=None,
        description="Metrics snapshot at report time",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the report was generated",
    )
