"""Pydantic v2 models for planner contracts."""

from __future__ import annotations

import uuid
from collections import deque
from datetime import UTC, datetime
from typing import Any

from pydantic import UUID4, BaseModel, Field

from adip.planner.contracts.entities import DetectedEntity
from adip.planner.enums import (
    ConfidenceLevelEnum,
    PlanningStatusEnum,
    PlanningStrategyEnum,
    PriorityEnum,
    TaskStatusEnum,
)

# ─────────────────────────────────────────────────────────────────────────────
# PlanningContext
# ─────────────────────────────────────────────────────────────────────────────


class CustomerContext(BaseModel):
    customer_id: str = ""
    customer_segment: str = ""
    preferences: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ConversationContext(BaseModel):
    conversation_id: str = ""
    turn_count: int = 0
    recent_messages: list[dict[str, Any]] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class MemoryContext(BaseModel):
    relevant_facts: list[str] = Field(default_factory=list)
    previous_interactions: list[dict[str, Any]] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class KnowledgeContext(BaseModel):
    knowledge_base_ids: list[str] = Field(default_factory=list)
    relevant_documents: list[dict[str, Any]] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class WorkflowContext(BaseModel):
    workflow_id: str = ""
    workflow_state: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class EnvironmentContext(BaseModel):
    environment_name: str = ""
    region: str = ""
    available_tools: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class AttachmentContext(BaseModel):
    attachment_ids: list[str] = Field(default_factory=list)
    attachment_metadata: list[dict[str, Any]] = Field(default_factory=list)


class PlanningContext(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    customer_context: CustomerContext = Field(default_factory=CustomerContext)
    conversation_context: ConversationContext = Field(default_factory=ConversationContext)
    memory_context: MemoryContext = Field(default_factory=MemoryContext)
    knowledge_context: KnowledgeContext = Field(default_factory=KnowledgeContext)
    workflow_context: WorkflowContext = Field(default_factory=WorkflowContext)
    environment_context: EnvironmentContext = Field(default_factory=EnvironmentContext)
    attachment_context: AttachmentContext = Field(default_factory=AttachmentContext)
    metadata: dict[str, Any] = Field(default_factory=dict)
    available_capabilities: list[str] = Field(default_factory=list)


# ─────────────────────────────────────────────────────────────────────────────
# PlanningGoal
# ─────────────────────────────────────────────────────────────────────────────


class PlanningGoal(BaseModel):
    goal_id: UUID4 = Field(default_factory=uuid.uuid4)
    objective: str
    intent: str | None = None
    domain: str | None = None
    entities: list[DetectedEntity] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    urgency: PriorityEnum = PriorityEnum.MEDIUM
    priority: PriorityEnum = PriorityEnum.MEDIUM
    success_criteria: list[str] = Field(default_factory=list)
    ambiguity_score: float = 0.0
    selected_strategy: PlanningStrategyEnum = PlanningStrategyEnum.DEFAULT


# ─────────────────────────────────────────────────────────────────────────────
# CapabilityMatch
# ─────────────────────────────────────────────────────────────────────────────


class CapabilityMatch(BaseModel):
    capability_id: str
    score: float
    confidence: ConfidenceLevelEnum = ConfidenceLevelEnum.MEDIUM
    estimated_execution_time: float | None = None
    estimated_resource_cost: float | None = None
    estimated_risk: float | None = None
    required_permissions: list[str] = Field(default_factory=list)
    capability_version: str = "1.0.0"
    provider: str = ""
    match_details: dict[str, Any] = Field(default_factory=dict)


# ─────────────────────────────────────────────────────────────────────────────
# PlanningTask
# ─────────────────────────────────────────────────────────────────────────────


class RetryPolicy(BaseModel):
    max_retries: int = 3
    backoff_seconds: float = 1.0
    max_backoff_seconds: float = 60.0


class PlanningTask(BaseModel):
    task_id: UUID4 = Field(default_factory=uuid.uuid4)
    task_name: str = ""
    description: str
    required_capability: str | None = None
    inputs: dict[str, Any] = Field(default_factory=dict)
    outputs: dict[str, Any] = Field(default_factory=dict)
    dependencies: list[UUID4] = Field(default_factory=list)
    priority: PriorityEnum = PriorityEnum.MEDIUM
    estimated_duration: float | None = None
    estimated_cost: float | None = None
    retry_policy: RetryPolicy | None = None
    parallelizable: bool = True
    requires_human_approval: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)
    status: TaskStatusEnum = TaskStatusEnum.PENDING
    matched_capabilities: list[CapabilityMatch] = Field(default_factory=list)


# ─────────────────────────────────────────────────────────────────────────────
# DependencyGraph
# ─────────────────────────────────────────────────────────────────────────────


class DependencyGraph(BaseModel):
    """A directed acyclic dependency graph for planning tasks."""
    nodes: dict[UUID4, PlanningTask] = {}
    edges: dict[UUID4, list[UUID4]] = {}

    @classmethod
    def from_tasks(cls, tasks: list[PlanningTask]) -> DependencyGraph:
        nodes = {t.task_id: t for t in tasks}
        edges = {t.task_id: list(t.dependencies) for t in tasks}
        return cls(nodes=nodes, edges=edges)

    def add_task(self, task: PlanningTask) -> None:
        self.nodes[task.task_id] = task
        self.edges[task.task_id] = list(task.dependencies)

    def get_root_tasks(self) -> list[PlanningTask]:
        return [
            self.nodes[tid] for tid, deps in self.edges.items() if not deps
        ]

    def get_leaf_tasks(self) -> list[PlanningTask]:
        has_dependents: set[UUID4] = set()
        for _tid, deps in self.edges.items():
            has_dependents.update(deps)
        return [
            self.nodes[tid]
            for tid in self.nodes
            if tid not in has_dependents
        ]

    def get_execution_order(self) -> list[PlanningTask]:
        in_degree: dict[UUID4, int] = {
            tid: len(deps) for tid, deps in self.edges.items()
        }
        queue = deque(tid for tid, deg in in_degree.items() if deg == 0)
        ordered: list[PlanningTask] = []
        while queue:
            tid = queue.popleft()
            ordered.append(self.nodes[tid])
            for other_tid, other_deps in self.edges.items():
                if tid in other_deps:
                    in_degree[other_tid] -= 1
                    if in_degree[other_tid] == 0:
                        queue.append(other_tid)
        return ordered

    def detect_cycles(self) -> list[list[UUID4]]:
        WHITE, GRAY, BLACK = 0, 1, 2
        color: dict[UUID4, int] = {tid: WHITE for tid in self.nodes}
        cycles: list[list[UUID4]] = []

        def _dfs(node: UUID4, path: list[UUID4]) -> None:
            color[node] = GRAY
            path.append(node)
            for dep_id in self.edges.get(node, []):
                if dep_id not in self.nodes:
                    continue
                if color[dep_id] == GRAY:
                    idx = path.index(dep_id)
                    cycles.append(path[idx:])
                elif color[dep_id] == WHITE:
                    _dfs(dep_id, path)
            path.pop()
            color[node] = BLACK

        for tid in self.nodes:
            if color[tid] == WHITE:
                _dfs(tid, [])
        return cycles

    def get_parallel_groups(self) -> list[list[UUID4]]:
        groups: dict[frozenset, list[UUID4]] = {}
        for tid, deps in self.edges.items():
            key = frozenset(deps)
            groups.setdefault(key, []).append(tid)
        return [g for g in groups.values() if len(g) > 1]


# ─────────────────────────────────────────────────────────────────────────────
# ExecutionPlan
# ─────────────────────────────────────────────────────────────────────────────


class ExecutionPlan(BaseModel):
    plan_id: UUID4 = Field(default_factory=uuid.uuid4)
    version: str = "1.0.0"
    parent_plan_id: UUID4 | None = None
    goal: PlanningGoal
    planning_strategy: PlanningStrategyEnum = PlanningStrategyEnum.DEFAULT
    confidence: float | None = None
    tasks: list[PlanningTask] = Field(default_factory=list)
    graph: DependencyGraph | None = None
    dependency_graph: dict[str, list[str]] = Field(default_factory=dict)
    parallel_groups: list[list[UUID4]] = Field(default_factory=list)
    estimated_duration: float | None = None
    estimated_cost: float | None = None
    planning_model: str = "deterministic"
    planning_timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    planner_version: str = "0.1.0"
    status: PlanningStatusEnum = PlanningStatusEnum.CREATED


# ─────────────────────────────────────────────────────────────────────────────
# PlanningDecision
# ─────────────────────────────────────────────────────────────────────────────


class PlanningDecision(BaseModel):
    decision_id: UUID4 = Field(default_factory=uuid.uuid4)
    task_id: UUID4 | None = None
    reasoning: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


# ─────────────────────────────────────────────────────────────────────────────
# PlanningTrace
# ─────────────────────────────────────────────────────────────────────────────


class PlanningTrace(BaseModel):
    stage_name: str
    started_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime | None = None
    duration_ms: float | None = None
    input_summary: dict[str, Any] | None = None
    output_summary: dict[str, Any] | None = None
    success: bool = True
    warnings: list[str] = Field(default_factory=list)
    planner_version: str = "0.1.0"
    correlation_id: str = ""


# ─────────────────────────────────────────────────────────────────────────────
# PlanningMetrics
# ─────────────────────────────────────────────────────────────────────────────


class PlanningMetrics(BaseModel):
    total_planning_time: float = 0.0
    planning_confidence: float = 0.0
    llm_latency: float = 0.0
    capabilities_considered: int = 0
    capabilities_matched: int = 0
    tasks_processed: int = 0
    generated_tasks: int = 0
    decisions_made: int = 0
    optimization_percentage: float = 0.0
    validation_errors: int = 0
    replans: int = 0
    cpu_time: float = 0.0
    memory_usage: float = 0.0
    execution_time_ms: float = 0.0
    planning_duration_ms: float = 0.0
    llm_tokens_used: int = 0
    parallel_tasks: int = 0


# ─────────────────────────────────────────────────────────────────────────────
# ValidationResult
# ─────────────────────────────────────────────────────────────────────────────


class ValidationResult(BaseModel):
    is_valid: bool = True
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


# ─────────────────────────────────────────────────────────────────────────────
# PlanningResult
# ─────────────────────────────────────────────────────────────────────────────


class PlanningResult(BaseModel):
    request_id: UUID4
    plan: ExecutionPlan | None = None
    final_decision: PlanningDecision | None = None
    validation_status: ValidationResult = Field(default_factory=ValidationResult)
    execution_status: PlanningStatusEnum = PlanningStatusEnum.CREATED
    traces: list[PlanningTrace] = Field(default_factory=list)
    metrics: PlanningMetrics = Field(default_factory=PlanningMetrics)


# ─────────────────────────────────────────────────────────────────────────────
# PlanningRequest
# ─────────────────────────────────────────────────────────────────────────────


class PlanningRequest(BaseModel):
    context: PlanningContext = Field(default_factory=PlanningContext)
    goal: PlanningGoal
    metrics: PlanningMetrics = Field(default_factory=PlanningMetrics)
