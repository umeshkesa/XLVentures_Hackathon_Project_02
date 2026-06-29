"""Graph builder — converts ``ExecutionPlan`` to ``WorkflowGraph``."""

from __future__ import annotations

import time
import uuid
from datetime import UTC, datetime

import structlog

from adip.workflow.contracts.exceptions import WorkflowValidationException
from adip.workflow.contracts.models import (
    WorkflowGraph,
    WorkflowRequest,
    WorkflowTask,
)
from adip.workflow.enums import RetryPolicy as WorkflowRetryPolicy
from adip.workflow.enums import TaskExecutionStatus
from adip.workflow.execution.trace import WORKFLOW_VERSION, WorkflowTrace
from adip.workflow.interfaces import GraphBuilder

log = structlog.get_logger(__name__)


class DefaultGraphBuilder(GraphBuilder):
    """Deterministic graph builder that preserves planner task order.

    Pipeline steps:
        1. Convert each ``PlanningTask`` to a ``WorkflowTask``.
        2. Add all nodes to the graph.
        3. Add dependency edges.
        4. Detect and reject duplicate nodes.
        5. Validate that every dependency references an existing node.
        6. Reject cyclic graphs.
        7. Populate execution levels.
        8. Populate parallel groups.
    """

    async def build(self, request: WorkflowRequest) -> WorkflowGraph:
        graph = WorkflowGraph()
        start = time.monotonic()
        correlation_id = str(uuid.uuid4())
        bound_log = log.bind(correlation_id=correlation_id)

        bound_log.info(
            "graph_builder.build",
            plan_id=str(request.execution_plan.plan_id),
            task_count=len(request.execution_plan.tasks),
        )

        # ── Step 1-2: Convert tasks and add nodes ─────────────────────
        seen_ids: set[uuid.UUID] = set()
        for pt in request.execution_plan.tasks:
            if pt.task_id in seen_ids:
                raise WorkflowValidationException(
                    f"Duplicate task_id {pt.task_id} in execution plan",
                )
            seen_ids.add(pt.task_id)

            retry_policy = WorkflowRetryPolicy.NEVER
            if pt.retry_policy is not None and pt.retry_policy.max_retries > 0:
                    retry_policy = WorkflowRetryPolicy.EXPONENTIAL_BACKOFF

            wt = WorkflowTask(
                task_id=pt.task_id,
                task_name=pt.task_name or pt.description[:60],
                description=pt.description,
                runtime_status=self._map_status(pt.status),
                inputs=dict(pt.inputs),
                outputs=dict(pt.outputs),
                dependencies=list(pt.dependencies),
                retry_policy=retry_policy,
                retry_count=0,
                execution_metadata={
                    "requires_human_approval": pt.requires_human_approval,
                    "parallelizable": pt.parallelizable,
                    "priority": pt.priority.value if pt.priority else "MEDIUM",
                    "estimated_duration": pt.estimated_duration,
                    "required_capability": pt.required_capability,
                },
            )
            graph.add_node(wt)

        # ── Step 3: Add dependency edges ──────────────────────────────
        for pt in request.execution_plan.tasks:
            for dep_id in pt.dependencies:
                graph.add_edge(pt.task_id, dep_id)

        # ── Step 4: Duplicate node detection (already done above) ─────

        # ── Step 5: Validate dependency integrity ─────────────────────
        for task_node in graph.nodes.values():
            for dep_id in task_node.dependencies:
                if dep_id not in graph.nodes:
                    raise WorkflowValidationException(
                        f"Task {task_node.task_id} depends on missing task {dep_id}",
                    )

        # ── Step 6: Reject cycles ─────────────────────────────────────
        cycles = graph.detect_cycles()
        if cycles:
            cycle_desc = "; ".join(
                " -> ".join(str(tid) for tid in c) for c in cycles
            )
            raise WorkflowValidationException(
                f"Graph contains {len(cycles)} cycle(s): {cycle_desc}",
            )

        # ── Steps 7-8: Populate levels & parallel groups ──────────────
        _ = graph.get_execution_levels()
        _ = graph.get_parallel_groups()

        elapsed = (time.monotonic() - start) * 1000
        bound_log.info(
            "graph_builder.completed",
            nodes=len(graph.nodes),
            edges=sum(len(e) for e in graph.edges.values()),
            duration_ms=round(elapsed, 2),
        )

        return graph

    # ── Internal helpers ───────────────────────────────────────────────

    @staticmethod
    def _map_status(
        planner_status: object,
    ) -> TaskExecutionStatus:
        try:
            from adip.planner.enums import TaskStatusEnum

            mapping = {
                TaskStatusEnum.PENDING: TaskExecutionStatus.PENDING,
                TaskStatusEnum.IN_PROGRESS: TaskExecutionStatus.READY,
                TaskStatusEnum.COMPLETED: TaskExecutionStatus.COMPLETED,
                TaskStatusEnum.FAILED: TaskExecutionStatus.FAILED,
                TaskStatusEnum.SKIPPED: TaskExecutionStatus.CANCELLED,
            }
            return mapping.get(planner_status, TaskExecutionStatus.PENDING)
        except ImportError:
            return TaskExecutionStatus.PENDING

    # ── Trace helper ──────────────────────────────────────────────────

    @staticmethod
    def _build_trace(
        stage_name: str,
        success: bool,
        duration_ms: float,
        input_summary: dict | None = None,
        output_summary: dict | None = None,
        warnings: list[str] | None = None,
        correlation_id: str = "",
    ) -> WorkflowTrace:
        return WorkflowTrace(
            stage_name=stage_name,
            started_at=datetime.now(UTC),
            completed_at=datetime.now(UTC),
            duration_ms=round(duration_ms, 2),
            input_summary=input_summary or {},
            output_summary=output_summary or {},
            success=success,
            warnings=warnings or [],
            workflow_version=WORKFLOW_VERSION,
            correlation_id=correlation_id,
        )
