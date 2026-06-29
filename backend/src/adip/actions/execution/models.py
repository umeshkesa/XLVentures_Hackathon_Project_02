"""Execution-layer models for the Action Manager Phase 2.

These models support internal processing: graph nodes/edges,
parallel groups, critical paths, dependency resolution results,
resource allocations, conflicts, execution windows, compensation
strategies, cost estimates, risk evaluations, policy results,
timeline entries, optimization results, feasibility results,
trace records, and metrics snapshots.
They are not exposed through the public ActionService API.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import UUID4, BaseModel, Field

from adip.actions.enums import ActionType


class ActionGraphNode(BaseModel):
    """A node in the action dependency graph."""

    node_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique node identifier",
    )
    step_id: str = Field(
        default="",
        description="The action plan step ID this node represents",
    )
    name: str = Field(
        default="",
        description="Name of the node/step",
    )
    action_type: ActionType = Field(
        default=ActionType.AUTOMATED,
        description="Type of action at this node",
    )
    duration_minutes: int = Field(
        default=0,
        ge=0,
        description="Estimated duration in minutes",
    )
    level: int = Field(
        default=0,
        ge=0,
        description="Topological level in the graph",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional node metadata",
    )


class ActionGraphEdge(BaseModel):
    """A directed edge in the action dependency graph."""

    edge_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique edge identifier",
    )
    source_node_id: str = Field(
        default="",
        description="Source node step ID",
    )
    target_node_id: str = Field(
        default="",
        description="Target node step ID",
    )
    dependency_type: str = Field(
        default="hard",
        description="Type of dependency (hard, soft, optional)",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional edge metadata",
    )


class ActionGraph(BaseModel):
    """Directed Acyclic Graph representing action dependencies."""

    graph_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique graph identifier",
    )
    plan_id: str = Field(
        default="",
        description="The plan this graph belongs to",
    )
    nodes: list[ActionGraphNode] = Field(
        default_factory=list,
        description="Nodes in the graph",
    )
    edges: list[ActionGraphEdge] = Field(
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
        description="Topologically sorted step IDs",
    )


class ParallelGroup(BaseModel):
    """A group of steps that can execute in parallel."""

    group_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique group identifier",
    )
    level: int = Field(
        default=0,
        ge=0,
        description="Parallel execution level",
    )
    step_ids: list[str] = Field(
        default_factory=list,
        description="Step IDs in this parallel group",
    )
    estimated_duration_minutes: int = Field(
        default=0,
        ge=0,
        description="Estimated duration for this group (max of steps)",
    )


class CriticalPath(BaseModel):
    """Result of critical path analysis."""

    path_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique path identifier",
    )
    step_ids: list[str] = Field(
        default_factory=list,
        description="Step IDs on the critical path",
    )
    total_duration_minutes: int = Field(
        default=0,
        ge=0,
        description="Total critical path duration",
    )
    bottleneck_step_ids: list[str] = Field(
        default_factory=list,
        description="Step IDs identified as bottlenecks",
    )


class DependencyResolution(BaseModel):
    """Result of dependency resolution for a plan."""

    resolution_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique resolution identifier",
    )
    plan_id: str = Field(
        default="",
        description="The plan this resolution belongs to",
    )
    hard_dependencies: list[str] = Field(
        default_factory=list,
        description="Hard dependency step IDs",
    )
    soft_dependencies: list[str] = Field(
        default_factory=list,
        description="Soft dependency step IDs",
    )
    optional_dependencies: list[str] = Field(
        default_factory=list,
        description="Optional dependency step IDs",
    )
    unresolved_dependencies: list[str] = Field(
        default_factory=list,
        description="Dependency step IDs that could not be resolved",
    )
    resolution_order: list[str] = Field(
        default_factory=list,
        description="Step IDs in dependency resolution order",
    )


class ResourceAllocationResult(BaseModel):
    """Result of resource allocation for a plan."""

    allocation_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique allocation identifier",
    )
    plan_id: str = Field(
        default="",
        description="The plan this allocation belongs to",
    )
    personnel: dict[str, list[str]] = Field(
        default_factory=dict,
        description="Step ID -> list of personnel assigned",
    )
    equipment: dict[str, list[str]] = Field(
        default_factory=dict,
        description="Step ID -> list of equipment assigned",
    )
    inventory: dict[str, list[str]] = Field(
        default_factory=dict,
        description="Step ID -> list of inventory items assigned",
    )
    budget: float = Field(
        default=0.0,
        ge=0.0,
        description="Allocated budget",
    )
    total_personnel: int = Field(
        default=0,
        ge=0,
        description="Total personnel allocated",
    )
    total_equipment: int = Field(
        default=0,
        ge=0,
        description="Total equipment units allocated",
    )


class ResourceConflict(BaseModel):
    """A detected resource conflict."""

    conflict_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique conflict identifier",
    )
    plan_id: str = Field(
        default="",
        description="The plan this conflict belongs to",
    )
    resource_type: str = Field(
        default="",
        description="Type of resource (personnel, equipment, inventory)",
    )
    resource_id: str = Field(
        default="",
        description="The specific resource with the conflict",
    )
    conflict_type: str = Field(
        default="",
        description="Type of conflict (double_booking, capacity, scheduling)",
    )
    step_ids: list[str] = Field(
        default_factory=list,
        description="Step IDs involved in the conflict",
    )
    description: str = Field(
        default="",
        description="Description of the conflict",
    )


class ExecutionWindow(BaseModel):
    """An execution window for scheduling action steps."""

    window_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique window identifier",
    )
    window_type: str = Field(
        default="immediate",
        description="Window type: immediate, scheduled, maintenance, business_hours, emergency",
    )
    step_ids: list[str] = Field(
        default_factory=list,
        description="Step IDs assigned to this window",
    )
    scheduled_start: datetime | None = Field(
        default=None,
        description="Scheduled start time",
    )
    scheduled_end: datetime | None = Field(
        default=None,
        description="Scheduled end time",
    )
    description: str = Field(
        default="",
        description="Description of the execution window",
    )


class CompensationStrategy(BaseModel):
    """A compensation strategy for handling action failures."""

    strategy_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique strategy identifier",
    )
    step_id: str = Field(
        default="",
        description="The step this strategy applies to",
    )
    strategy_type: str = Field(
        default="rollback",
        description="Strategy type: rollback, compensation, retry, manual_recovery, alternative",
    )
    description: str = Field(
        default="",
        description="Description of the strategy",
    )
    parameters: dict[str, Any] = Field(
        default_factory=dict,
        description="Strategy parameters",
    )


class CostEstimate(BaseModel):
    """Estimated cost breakdown for an action plan."""

    estimate_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique estimate identifier",
    )
    plan_id: str = Field(
        default="",
        description="The plan this estimate belongs to",
    )
    labor_cost: float = Field(
        default=0.0,
        ge=0.0,
        description="Estimated labor cost",
    )
    equipment_cost: float = Field(
        default=0.0,
        ge=0.0,
        description="Estimated equipment cost",
    )
    downtime_cost: float = Field(
        default=0.0,
        ge=0.0,
        description="Estimated downtime cost",
    )
    materials_cost: float = Field(
        default=0.0,
        ge=0.0,
        description="Estimated materials cost",
    )
    external_services_cost: float = Field(
        default=0.0,
        ge=0.0,
        description="Estimated external services cost",
    )
    total_cost: float = Field(
        default=0.0,
        ge=0.0,
        description="Total estimated cost",
    )
    currency: str = Field(
        default="USD",
        description="Currency for the estimate",
    )


class RiskEvaluation(BaseModel):
    """Risk evaluation result for an action plan."""

    evaluation_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique evaluation identifier",
    )
    plan_id: str = Field(
        default="",
        description="The plan this evaluation belongs to",
    )
    operational_risk: str = Field(
        default="LOW",
        description="Operational risk level: LOW, MEDIUM, HIGH, CRITICAL",
    )
    safety_risk: str = Field(
        default="LOW",
        description="Safety risk level: LOW, MEDIUM, HIGH, CRITICAL",
    )
    financial_risk: str = Field(
        default="LOW",
        description="Financial risk level: LOW, MEDIUM, HIGH, CRITICAL",
    )
    compliance_risk: str = Field(
        default="LOW",
        description="Compliance risk level: LOW, MEDIUM, HIGH, CRITICAL",
    )
    execution_risk: str = Field(
        default="LOW",
        description="Execution risk level: LOW, MEDIUM, HIGH, CRITICAL",
    )
    overall_risk: str = Field(
        default="LOW",
        description="Overall risk level: LOW, MEDIUM, HIGH, CRITICAL",
    )
    risk_factors: list[str] = Field(
        default_factory=list,
        description="Identified risk factors",
    )


class PolicyResult(BaseModel):
    """Result of policy validation for an action plan."""

    result_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique result identifier",
    )
    plan_id: str = Field(
        default="",
        description="The plan this result belongs to",
    )
    safety_policy_violations: list[str] = Field(
        default_factory=list,
        description="Safety policy violations",
    )
    business_policy_violations: list[str] = Field(
        default_factory=list,
        description="Business policy violations",
    )
    resource_policy_violations: list[str] = Field(
        default_factory=list,
        description="Resource policy violations",
    )
    compliance_policy_violations: list[str] = Field(
        default_factory=list,
        description="Compliance policy violations",
    )
    is_policy_compliant: bool = Field(
        default=True,
        description="Whether the plan is fully policy-compliant",
    )
    total_violations: int = Field(
        default=0,
        ge=0,
        description="Total number of policy violations",
    )


class TimelineEntry(BaseModel):
    """A single entry in the execution timeline."""

    entry_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique entry identifier",
    )
    plan_id: str = Field(
        default="",
        description="The plan this entry belongs to",
    )
    step_id: str = Field(
        default="",
        description="The step ID this entry represents",
    )
    step_name: str = Field(
        default="",
        description="Name of the step",
    )
    sequence: int = Field(
        default=0,
        ge=0,
        description="Sequence order in the timeline",
    )
    parallel_group: int = Field(
        default=0,
        ge=0,
        description="Parallel execution group number",
    )
    estimated_start: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Estimated start time",
    )
    estimated_end: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Estimated end time",
    )
    duration_minutes: int = Field(
        default=0,
        ge=0,
        description="Duration in minutes",
    )
    is_critical: bool = Field(
        default=False,
        description="Whether this step is on the critical path",
    )


class OptimizationResult(BaseModel):
    """Result of action plan optimization."""

    result_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique result identifier",
    )
    plan_id: str = Field(
        default="",
        description="The plan this result belongs to",
    )
    original_cost: float = Field(
        default=0.0,
        ge=0.0,
    )
    optimized_cost: float = Field(
        default=0.0,
        ge=0.0,
    )
    original_duration_minutes: int = Field(
        default=0,
        ge=0,
    )
    optimized_duration_minutes: int = Field(
        default=0,
        ge=0,
    )
    original_resource_utilization: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
    )
    optimized_resource_utilization: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
    )
    original_safety_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
    )
    optimized_safety_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
    )
    original_downtime_minutes: int = Field(
        default=0,
        ge=0,
    )
    optimized_downtime_minutes: int = Field(
        default=0,
        ge=0,
    )
    cost_savings: float = Field(
        default=0.0,
        ge=0.0,
    )
    duration_reduction_minutes: int = Field(
        default=0,
        ge=0,
    )
    optimization_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
    )
    improvements: list[str] = Field(
        default_factory=list,
        description="List of improvements made",
    )


class FeasibilityResult(BaseModel):
    """Result of feasibility analysis for an action plan."""

    result_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique result identifier",
    )
    plan_id: str = Field(
        default="",
        description="The plan this result belongs to",
    )
    resource_available: bool = Field(
        default=True,
        description="Whether required resources are available",
    )
    budget_available: bool = Field(
        default=True,
        description="Whether budget is sufficient",
    )
    skills_available: bool = Field(
        default=True,
        description="Whether required skills are available",
    )
    schedule_feasible: bool = Field(
        default=True,
        description="Whether the schedule is feasible",
    )
    dependencies_satisfied: bool = Field(
        default=True,
        description="Whether dependencies are satisfiable",
    )
    is_feasible: bool = Field(
        default=True,
        description="Overall feasibility",
    )
    issues: list[str] = Field(
        default_factory=list,
        description="List of feasibility issues",
    )


class TraceRecord(BaseModel):
    """A single trace entry for an action planning stage."""

    trace_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique trace identifier",
    )
    plan_id: str = Field(
        default="",
        description="The plan being traced",
    )
    session_id: str = Field(
        default="",
        description="The session being traced",
    )
    stage_name: str = Field(
        default="",
        description="Name of the pipeline stage",
    )
    operation: str = Field(
        default="",
        description="The operation being performed",
    )
    details: str = Field(
        default="",
        description="Detailed description of the operation",
    )
    duration_ms: float | None = Field(
        default=None,
        ge=0.0,
        description="Wall-clock duration in milliseconds",
    )
    success: bool = Field(
        default=True,
        description="Whether the stage completed without error",
    )
    correlation_id: str = Field(
        default="",
        description="Correlation ID for distributed tracing",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the trace entry was created",
    )


class ActionMetricsSnapshot(BaseModel):
    """Snapshot of metrics for the Action Manager system."""

    snapshot_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique snapshot identifier",
    )
    plans_total: int = Field(
        default=0,
        ge=0,
    )
    tasks_total: int = Field(
        default=0,
        ge=0,
    )
    resources_allocated: int = Field(
        default=0,
        ge=0,
    )
    conflicts_detected: int = Field(
        default=0,
        ge=0,
    )
    planning_times_ms: list[float] = Field(
        default_factory=list,
    )
    optimization_scores: list[float] = Field(
        default_factory=list,
    )
    average_cost: float = Field(
        default=0.0,
        ge=0.0,
    )
    average_duration_minutes: float = Field(
        default=0.0,
        ge=0.0,
    )
    plans_per_action_type: dict[str, int] = Field(
        default_factory=dict,
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the snapshot was taken",
    )
