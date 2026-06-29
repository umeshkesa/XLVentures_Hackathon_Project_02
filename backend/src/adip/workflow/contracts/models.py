"""Workflow Engine domain models — Graph-First architecture."""

from __future__ import annotations

import uuid
from collections import deque
from datetime import UTC, datetime
from typing import Any

from pydantic import UUID4, BaseModel, Field

from adip.planner.contracts.models import ExecutionPlan
from adip.workflow.enums import RetryPolicy, TaskExecutionStatus, WorkflowStatus

WORKFLOW_VERSION: str = "0.1.0"


class WorkflowDecision(BaseModel):
    """Captures WHY an execution decision was made.

    Every pipeline stage can record a decision that explains the
    reasoning behind a particular choice (strategy selection, task
    ordering, retry decision, etc.).  This feeds the Explainability
    Engine in a future phase.
    """

    decision_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique identifier for this decision",
    )
    decision_type: str = Field(
        description="Category of decision (e.g. strategy, retry, skip)",
    )
    reason: str = Field(
        default="",
        description="Human-readable explanation of why the decision was made",
    )
    evidence: dict[str, Any] = Field(
        default_factory=dict,
        description="Supporting data that informed the decision",
    )
    selected_strategy: str | None = Field(
        default=None,
        description="The strategy that was chosen",
    )
    alternatives: list[str] = Field(
        default_factory=list,
        description="Alternative strategies that were considered but not selected",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the decision was made",
    )


class WorkflowTrace(BaseModel):
    """Execution trace recorded by each pipeline stage.

    Mirrors ``PlanningTrace`` from the Planner module to provide
    consistent observability across the ADIP platform.
    """

    stage_name: str = Field(
        description="Unique name of the pipeline stage",
    )
    started_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the stage began",
    )
    completed_at: datetime | None = Field(
        default=None,
        description="When the stage finished",
    )
    duration_ms: float | None = Field(
        default=None,
        ge=0.0,
        description="Wall-clock duration in milliseconds",
    )
    workflow_state: str | None = Field(
        default=None,
        description="Workflow status at the time the trace was recorded",
    )
    input_summary: dict[str, Any] | None = Field(
        default=None,
        description="Summary of inputs received",
    )
    output_summary: dict[str, Any] | None = Field(
        default=None,
        description="Summary of outputs produced",
    )
    success: bool = Field(
        default=True,
        description="Whether the stage completed without error",
    )
    warnings: list[str] = Field(
        default_factory=list,
        description="Non-fatal warnings emitted by the stage",
    )
    errors: list[str] = Field(
        default_factory=list,
        description="Fatal errors encountered during the stage",
    )
    workflow_version: str = Field(
        default=WORKFLOW_VERSION,
        description="Workflow Engine version that produced this trace",
    )
    correlation_id: str = Field(
        default="",
        description="Correlation ID linking traces across the platform",
    )


class WorkflowPolicy(BaseModel):
    """Configurable policy that governs workflow execution behaviour.

    The engine reads policy values instead of hardcoding behaviour,
    making the system adaptable without code changes.
    """

    max_parallel_tasks: int = Field(
        default=1,
        ge=1,
        description="Maximum number of tasks that may execute concurrently",
    )
    retry_limit: int = Field(
        default=3,
        ge=0,
        description="Default maximum retry attempts per task",
    )
    timeout_policy: str = Field(
        default="fail",
        description="Behaviour on timeout: 'fail', 'retry', or 'skip'",
    )
    approval_policy: str = Field(
        default="auto_approve",
        description="Default approval behaviour: 'auto_approve' or 'require_approval'",
    )
    failure_policy: str = Field(
        default="continue",
        description="Behaviour on task failure: 'continue', 'pause', or 'abort'",
    )
    execution_mode: str = Field(
        default="sequential",
        description="Default execution mode: 'sequential' or 'parallel'",
    )
    compensation_enabled: bool = Field(
        default=False,
        description="Whether compensation (rollback) is enabled for failed workflows",
    )


# ─────────────────────────────────────────────────────────────────────────────
# WorkflowContext
# ─────────────────────────────────────────────────────────────────────────────


class WorkflowContext(BaseModel):
    """Full context available during workflow execution."""
    request_context: dict[str, Any] = Field(
        default_factory=dict,
        description="Original request metadata",
    )
    planner_context: dict[str, Any] = Field(
        default_factory=dict,
        description="Context from the planner phase",
    )
    execution_context: dict[str, Any] = Field(
        default_factory=dict,
        description="Runtime execution state",
    )
    user_context: dict[str, Any] = Field(
        default_factory=dict,
        description="Information about the requesting user",
    )
    environment_context: dict[str, Any] = Field(
        default_factory=dict,
        description="Runtime environment details",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional free-form metadata",
    )


# ─────────────────────────────────────────────────────────────────────────────
# WorkflowTask — runtime version of PlanningTask
# ─────────────────────────────────────────────────────────────────────────────


class WorkflowTask(BaseModel):
    """Runtime representation of a single task within a workflow.

    This is the execution-time counterpart of ``PlanningTask``.
    """
    task_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique identifier for this task instance",
    )
    task_name: str = Field(
        default="",
        description="Human-readable task name",
    )
    description: str = Field(
        default="",
        description="Detailed description of the task",
    )
    runtime_status: TaskExecutionStatus = Field(
        default=TaskExecutionStatus.PENDING,
        description="Current execution status",
    )
    assigned_executor: str | None = Field(
        default=None,
        description="Executor or agent assigned to this task",
    )
    inputs: dict[str, Any] = Field(
        default_factory=dict,
        description="Input parameters for execution",
    )
    outputs: dict[str, Any] = Field(
        default_factory=dict,
        description="Output produced after execution",
    )
    dependencies: list[UUID4] = Field(
        default_factory=list,
        description="Task IDs that must complete before this task",
    )
    retry_count: int = Field(
        default=0,
        ge=0,
        description="Number of times this task has been retried",
    )
    retry_policy: RetryPolicy = Field(
        default=RetryPolicy.NEVER,
        description="Retry strategy for this task",
    )
    timeout: float | None = Field(
        default=None,
        ge=0.0,
        description="Maximum execution time in seconds",
    )
    execution_metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary runtime metadata",
    )
    decision_reason: str | None = Field(
        default=None,
        description="Explainability: why this task was executed, skipped, or retried",
    )
    started_at: datetime | None = Field(
        default=None,
        description="When execution started",
    )
    completed_at: datetime | None = Field(
        default=None,
        description="When execution finished",
    )


# ─────────────────────────────────────────────────────────────────────────────
# TaskResult
# ─────────────────────────────────────────────────────────────────────────────


class TaskResult(BaseModel):
    """Outcome of a single task execution."""
    success: bool = Field(
        default=True,
        description="Whether the task completed successfully",
    )
    outputs: dict[str, Any] = Field(
        default_factory=dict,
        description="Data produced by the task",
    )
    execution_time: float | None = Field(
        default=None,
        ge=0.0,
        description="Wall-clock time in seconds",
    )
    warnings: list[str] = Field(
        default_factory=list,
        description="Non-fatal warnings",
    )
    errors: list[str] = Field(
        default_factory=list,
        description="Fatal error messages",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional result metadata",
    )


# ─────────────────────────────────────────────────────────────────────────────
# WorkflowMetrics
# ─────────────────────────────────────────────────────────────────────────────


class WorkflowMetrics(BaseModel):
    """Performance metrics collected during workflow execution."""
    total_execution_time: float = Field(
        default=0.0,
        ge=0.0,
        description="Total wall-clock time in milliseconds",
    )
    scheduling_time: float = Field(
        default=0.0,
        ge=0.0,
        description="Time spent scheduling tasks in milliseconds",
    )
    execution_time: float = Field(
        default=0.0,
        ge=0.0,
        description="Time spent executing tasks in milliseconds",
    )
    waiting_time: float = Field(
        default=0.0,
        ge=0.0,
        description="Total time spent waiting in milliseconds",
    )
    approval_wait_time: float = Field(
        default=0.0,
        ge=0.0,
        description="Total time waiting for approvals in milliseconds",
    )
    retry_time: float = Field(
        default=0.0,
        ge=0.0,
        description="Total time spent on retry backoff in milliseconds",
    )
    idle_time: float = Field(
        default=0.0,
        ge=0.0,
        description="Total idle time between task executions in milliseconds",
    )
    scheduled_tasks: int = Field(
        default=0,
        ge=0,
        description="Number of tasks scheduled for execution",
    )
    executed_tasks: int = Field(
        default=0,
        ge=0,
        description="Number of tasks that executed",
    )
    successful_tasks: int = Field(
        default=0,
        ge=0,
        description="Number of tasks that completed successfully",
    )
    failed_tasks: int = Field(
        default=0,
        ge=0,
        description="Number of tasks that failed",
    )
    retry_count: int = Field(
        default=0,
        ge=0,
        description="Total retry attempts across all tasks",
    )
    retry_attempts: int = Field(
        default=0,
        ge=0,
        description="Number of individual retry attempts",
    )
    parallel_execution_percentage: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Percentage of execution that ran in parallel",
    )
    parallel_groups: int = Field(
        default=0,
        ge=0,
        description="Number of parallel execution groups identified",
    )
    waiting_tasks: int = Field(
        default=0,
        ge=0,
        description="Number of tasks currently waiting",
    )
    approval_requests: int = Field(
        default=0,
        ge=0,
        description="Number of approval requests made",
    )
    total_runtime: float = Field(
        default=0.0,
        ge=0.0,
        description="Total runtime of the workflow in milliseconds",
    )
    execution_efficiency: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Execution efficiency percentage",
    )
    workflow_confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Confidence score for the workflow execution",
    )
    resource_usage: dict[str, Any] = Field(
        default_factory=dict,
        description="Resource consumption estimates",
    )


# ─────────────────────────────────────────────────────────────────────────────
# WorkflowGraph — PRIMARY execution model
# ─────────────────────────────────────────────────────────────────────────────


class WorkflowGraph(BaseModel):
    """Graph-First execution model for the Workflow Engine.

    Nodes are ``WorkflowTask`` instances keyed by ``task_id``.
    Edges define dependency relationships.

    All engine operations operate on this graph rather than on
    ``ExecutionPlan`` directly.
    """
    nodes: dict[UUID4, WorkflowTask] = Field(
        default_factory=dict,
        description="All tasks in the graph, keyed by task_id",
    )
    edges: dict[UUID4, list[UUID4]] = Field(
        default_factory=dict,
        description="Dependency edges: task_id → list of dependency task_ids",
    )

    # ── Construction ────────────────────────────────────────────────────

    def add_node(self, task: WorkflowTask) -> None:
        """Add or replace a task node."""
        self.nodes[task.task_id] = task
        self.edges.setdefault(task.task_id, [])

    def add_edge(self, from_id: UUID4, to_id: UUID4) -> None:
        """Add a dependency: ``from_id`` depends on ``to_id``."""
        if from_id not in self.nodes or to_id not in self.nodes:
            return
        if to_id not in self.edges.setdefault(from_id, []):
            self.edges[from_id].append(to_id)

    @classmethod
    def from_workflow_tasks(cls, tasks: list[WorkflowTask]) -> WorkflowGraph:
        """Build a graph from a flat list of WorkflowTasks."""
        nodes = {t.task_id: t for t in tasks}
        edges = {t.task_id: list(t.dependencies) for t in tasks}
        return cls(nodes=nodes, edges=edges)

    # ── Queries ─────────────────────────────────────────────────────────

    def get_root_nodes(self) -> list[WorkflowTask]:
        """Tasks with no dependencies — can execute first."""
        return [
            self.nodes[tid]
            for tid, deps in self.edges.items()
            if not deps
        ]

    def get_leaf_nodes(self) -> list[WorkflowTask]:
        """Tasks that no other task depends on — final tasks."""
        has_dependents: set[UUID4] = set()
        for _tid, deps in self.edges.items():
            has_dependents.update(deps)
        return [
            self.nodes[tid]
            for tid in self.nodes
            if tid not in has_dependents
        ]

    def topological_sort(self) -> list[WorkflowTask]:
        """Return tasks in topological (dependency-respecting) order."""
        in_degree: dict[UUID4, int] = {
            tid: len(deps) for tid, deps in self.edges.items()
        }
        queue = deque(tid for tid, deg in in_degree.items() if deg == 0)
        ordered: list[WorkflowTask] = []
        while queue:
            tid = queue.popleft()
            ordered.append(self.nodes[tid])
            for other_tid, other_deps in self.edges.items():
                if tid in other_deps:
                    in_degree[other_tid] -= 1
                    if in_degree[other_tid] == 0:
                        queue.append(other_tid)
        return ordered

    def get_execution_levels(self) -> list[list[UUID4]]:
        """Group task IDs by topological execution level.

        Level 0: tasks with no dependencies.
        Level N: tasks whose dependencies all reside in levels < N.
        """
        order = self.topological_sort()
        task_ids = [t.task_id for t in order]
        level_map: dict[UUID4, int] = {}
        levels: list[list[UUID4]] = []

        remaining = set(task_ids)
        current = [tid for tid in task_ids if not self.edges.get(tid, [])]
        if current:
            for tid in current:
                level_map[tid] = 0
            levels.append(sorted(current))
            remaining -= set(current)

        level_num = 1
        while remaining:
            current = []
            for tid in list(remaining):
                deps = self.edges.get(tid, [])
                if all(d in level_map for d in deps):
                    current.append(tid)
            if not current:
                break
            for tid in current:
                level_map[tid] = level_num
            levels.append(sorted(current))
            remaining -= set(current)
            level_num += 1

        return levels

    def get_parallel_groups(self) -> list[list[UUID4]]:
        """Task IDs sharing identical dependency sets can run in parallel."""
        groups: dict[frozenset, list[UUID4]] = {}
        for tid, deps in self.edges.items():
            key = frozenset(deps)
            groups.setdefault(key, []).append(tid)
        return [g for g in groups.values() if len(g) > 1]

    def detect_cycles(self) -> list[list[UUID4]]:
        """Return every cycle detected via DFS coloring."""
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

    def validate(self) -> list[str]:
        """Run all integrity checks on the graph.

        Returns a list of error messages (empty = graph is valid).
        Checks: node existence, dependency integrity, cycles, orphans.
        """
        errors: list[str] = []

        # All referenced dependencies must exist
        for tid, deps in self.edges.items():
            for dep_id in deps:
                if dep_id not in self.nodes:
                    errors.append(
                        f"Task {tid} depends on missing task {dep_id}",
                    )

        # Cycles
        cycles = self.detect_cycles()
        if cycles:
            errors.append(f"Graph contains {len(cycles)} cycle(s)")

        # Orphans — tasks not in the edge set (disconnected nodes)
        orphans = self.detect_orphans()
        if orphans:
            errors.append(f"Graph contains {len(orphans)} orphan node(s)")

        return errors

    def detect_orphans(self) -> list[UUID4]:
        """Return task IDs that are disconnected from the rest of the graph.

        An orphan is a task that has no dependencies and no dependents.
        """
        has_dependents: set[UUID4] = set()
        for _tid, deps in self.edges.items():
            has_dependents.update(deps)
        orphans: list[UUID4] = []
        for tid in self.nodes:
            has_deps = bool(self.edges.get(tid, []))
            is_depended = tid in has_dependents
            if not has_deps and not is_depended:
                orphans.append(tid)
        return orphans

    def get_critical_path(self) -> list[WorkflowTask]:
        """Return the longest dependency chain (critical path).

        Uses the number of transitive dependencies as a proxy for
        path length.  Returns tasks in topological order along the
        critical path.
        """
        if not self.nodes:
            return []

        order = self.topological_sort()
        longest_path: dict[UUID4, list[UUID4]] = {
            tid: [] for tid in self.nodes
        }

        for task in order:
            tid = task.task_id
            deps = self.edges.get(tid, [])
            if not deps:
                longest_path[tid] = [tid]
            else:
                best_dep = max(deps, key=lambda d: len(longest_path.get(d, [])))
                longest_path[tid] = longest_path[best_dep] + [tid]

        if not longest_path:
            return []

        best_tid = max(longest_path, key=lambda k: len(longest_path[k]))
        return [self.nodes[t] for t in longest_path[best_tid]]


# ─────────────────────────────────────────────────────────────────────────────
# WorkflowRequest
# ─────────────────────────────────────────────────────────────────────────────


class WorkflowRequest(BaseModel):
    """Request payload to initiate a workflow execution."""
    execution_plan: ExecutionPlan = Field(
        description="The plan produced by the Planner",
    )
    workflow_context: WorkflowContext = Field(
        default_factory=WorkflowContext,
        description="Execution context",
    )
    policy: WorkflowPolicy = Field(
        default_factory=WorkflowPolicy,
        description="Execution policy governing this workflow run",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional request metadata",
    )


# ─────────────────────────────────────────────────────────────────────────────
# WorkflowResult
# ─────────────────────────────────────────────────────────────────────────────


class WorkflowResult(BaseModel):
    """Final result of a workflow execution."""
    workflow_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique workflow instance identifier",
    )
    workflow_status: WorkflowStatus = Field(
        default=WorkflowStatus.CREATED,
        description="Final workflow status",
    )
    completed_tasks: int = Field(
        default=0,
        ge=0,
        description="Number of tasks that completed",
    )
    failed_tasks: int = Field(
        default=0,
        ge=0,
        description="Number of tasks that failed",
    )
    skipped_tasks: int = Field(
        default=0,
        ge=0,
        description="Number of tasks that were skipped",
    )
    execution_time: float = Field(
        default=0.0,
        ge=0.0,
        description="Total wall-clock time in milliseconds",
    )
    execution_summary: str = Field(
        default="",
        description="Human-readable summary of the execution",
    )
    task_results: dict[UUID4, TaskResult] = Field(
        default_factory=dict,
        description="Results keyed by task_id",
    )
    decisions: list[WorkflowDecision] = Field(
        default_factory=list,
        description="Execution decisions recorded during the workflow",
    )
    events: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Recorded workflow events",
    )
    traces: list[WorkflowTrace] = Field(
        default_factory=list,
        description="Ordered execution traces for each pipeline stage",
    )
    metrics: WorkflowMetrics = Field(
        default_factory=lambda: _empty_metrics(),
        description="Aggregated workflow execution metrics",
    )
    execution_efficiency: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Execution efficiency percentage",
    )


def _empty_metrics() -> WorkflowMetrics:
    return WorkflowMetrics()
