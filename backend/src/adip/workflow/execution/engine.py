"""WorkflowEngine — central orchestrator for the execution pipeline."""

from __future__ import annotations

import asyncio
import time
import uuid
from datetime import UTC, datetime
from typing import Any

import structlog

from adip.workflow.contracts.events import (
    ExecutionStarted,
    GraphBuilt,
    TaskCompleted,
    TaskDispatched,
    TaskFailed,
    TasksScheduled,
    WorkflowCompleted,
    WorkflowFailed,
    WorkflowInitialized,
    WorkflowStarted,
)
from adip.workflow.contracts.models import (
    TaskResult,
    WorkflowDecision,
    WorkflowGraph,
    WorkflowMetrics,
    WorkflowPolicy,
    WorkflowRequest,
    WorkflowResult,
    WorkflowTask,
)
from adip.workflow.enums import TaskExecutionStatus, WorkflowStatus
from adip.workflow.execution.confidence import WorkflowConfidenceCalculator
from adip.workflow.execution.state_machine import WorkflowStateMachine
from adip.workflow.execution.strategy import ExecutionStrategy
from adip.workflow.execution.trace import WORKFLOW_VERSION, WorkflowTrace
from adip.workflow.interfaces import (
    ApprovalManager,
    ExecutionMonitor,
    GraphBuilder,
    RetryManager,
    TaskDispatcher,
    TaskScheduler,
    WorkflowEngine,
)

log = structlog.get_logger(__name__)


class DefaultWorkflowEngine(WorkflowEngine):
    """Orchestrates the full workflow execution pipeline.

    Pipeline order:
      1. Build graph via ``GraphBuilder``
      2. Schedule via ``TaskScheduler`` (uses ``ExecutionStrategy``)
      3. For each task: dispatch → approval → execute → monitor
      4. Aggregate metrics and return ``WorkflowResult``

    Every pipeline stage records a ``WorkflowTrace``, publishes a
    ``WorkflowEvent``, and may produce a ``WorkflowDecision`` for
    explainability.
    """

    def __init__(
        self,
        graph_builder: GraphBuilder,
        scheduler: TaskScheduler,
        dispatcher: TaskDispatcher,
        retry_manager: RetryManager,
        approval_manager: ApprovalManager,
        execution_monitor: ExecutionMonitor,
        execution_strategy: ExecutionStrategy,
        confidence_calculator: WorkflowConfidenceCalculator | None = None,
        policy: WorkflowPolicy | None = None,
    ) -> None:
        self._graph_builder = graph_builder
        self._scheduler = scheduler
        self._dispatcher = dispatcher
        self._retry = retry_manager
        self._approval = approval_manager
        self._monitor = execution_monitor
        self._strategy = execution_strategy
        self._confidence = confidence_calculator or WorkflowConfidenceCalculator()
        self._policy = policy or WorkflowPolicy()
        self._state = WorkflowStateMachine()

    # ── WorkflowEngine interface ─────────────────────────────────────────

    async def execute(self, request: WorkflowRequest) -> WorkflowResult:
        start_time = time.monotonic()
        correlation_id = str(uuid.uuid4())
        workflow_id = uuid.uuid4()
        traces: list[WorkflowTrace] = []
        events: list[dict[str, Any]] = []
        decisions: list[WorkflowDecision] = []
        task_results: dict[uuid.UUID, TaskResult] = {}
        metrics = WorkflowMetrics()
        policy = request.policy or self._policy

        bound_log = log.bind(
            workflow_id=str(workflow_id),
            plan_id=str(request.execution_plan.plan_id),
            correlation_id=correlation_id,
        )

        bound_log.info("engine.execute.start")

        try:
            # ── 0. Start ───────────────────────────────────────────────
            self._state.transition_to(WorkflowStatus.INITIALIZED)
            plan_id_str = str(request.execution_plan.plan_id)
            self._record_event(
                events, WorkflowStarted(
                    workflow_id=workflow_id, correlation_id=correlation_id,
                    execution_plan_id=plan_id_str,
                    payload={"plan_id": plan_id_str},
                ),
            )
            self._record_event(
                events, WorkflowInitialized(
                    workflow_id=workflow_id, correlation_id=correlation_id,
                    execution_plan_id=plan_id_str,
                ),
            )

            # ── 1. Build graph ─────────────────────────────────────────
            bound_log.info("engine.state.graph_building")
            trace, graph = await self._traced_stage(
                "graph_builder",
                lambda: self._graph_builder.build(request),
                correlation_id=correlation_id,
                workflow_state=self._state.current.value,
            )
            traces.append(trace)
            self._state.transition_to(WorkflowStatus.GRAPH_BUILT)
            self._record_event(
                events, GraphBuilt(
                    workflow_id=workflow_id, correlation_id=correlation_id,
                    execution_plan_id=plan_id_str,
                    node_count=len(graph.nodes),
                    edge_count=sum(len(e) for e in graph.edges.values()),
                    cycle_free=not bool(graph.detect_cycles()),
                ),
            )
            bound_log.info(
                "engine.graph_built",
                nodes=len(graph.nodes),
                edges=sum(len(e) for e in graph.edges.values()),
            )

            # ── 2. Schedule ────────────────────────────────────────────
            bound_log.info("engine.state.scheduling")
            self._state.transition_to(WorkflowStatus.SCHEDULED)
            schedule_start = time.monotonic()
            trace, schedule = await self._traced_stage(
                "scheduler",
                lambda: self._scheduler.schedule(graph),
                correlation_id=correlation_id,
            )
            traces.append(trace)
            metrics.scheduling_time = (time.monotonic() - schedule_start) * 1000
            self._record_event(
                events, TasksScheduled(
                    workflow_id=workflow_id, correlation_id=correlation_id,
                    execution_plan_id=plan_id_str,
                    wave_count=1,
                    total_tasks=len(schedule),
                ),
            )
            bound_log.info("engine.scheduled", tasks=len(schedule))

            if not schedule:
                self._state.transition_to(WorkflowStatus.COMPLETED)
                elapsed = (time.monotonic() - start_time) * 1000
                result = self._build_result(
                    workflow_id, WorkflowStatus.COMPLETED,
                    traces, events, decisions, task_results, metrics, elapsed,
                    summary="No tasks to execute",
                )
                self._record_event(
                    events, WorkflowCompleted(
                        workflow_id=workflow_id, correlation_id=correlation_id,
                        execution_plan_id=plan_id_str,
                        summary="No tasks to execute",
                    ),
                )
                bound_log.info("engine.completed.empty")
                return result

            # ── 3. Execute tasks ──────────────────────────────────────
            self._state.transition_to(WorkflowStatus.READY)
            self._state.transition_to(WorkflowStatus.RUNNING)
            self._record_event(
                events, ExecutionStarted(
                    workflow_id=workflow_id, correlation_id=correlation_id,
                    execution_plan_id=plan_id_str,
                    total_tasks=len(schedule),
                ),
            )
            bound_log.info("engine.state.running", tasks=len(schedule))

            for task in schedule:
                await self._execute_single_task(
                    task, graph, workflow_id, correlation_id, plan_id_str,
                    traces, events, task_results, metrics, bound_log, policy,
                )

            # ── 4. Complete ────────────────────────────────────────────
            all_success = all(r.success for r in task_results.values())
            final_status = (
                WorkflowStatus.COMPLETED if all_success
                else WorkflowStatus.FAILED
            )
            self._state.transition_to(final_status)

            elapsed = (time.monotonic() - start_time) * 1000
            metrics.total_execution_time = elapsed
            metrics.total_runtime = elapsed

            confidence = await self._confidence.calculate(graph, metrics)
            metrics.workflow_confidence = confidence
            efficiency = await self._compute_efficiency(metrics, elapsed)
            metrics.execution_efficiency = efficiency

            result = self._build_result(
                workflow_id, final_status,
                traces, events, decisions, task_results, metrics, elapsed,
                summary=f"Executed {len(task_results)} tasks",
                efficiency=efficiency,
            )

            if final_status == WorkflowStatus.COMPLETED:
                self._record_event(
                    events, WorkflowCompleted(
                        workflow_id=workflow_id, correlation_id=correlation_id,
                        execution_plan_id=plan_id_str,
                        summary=f"Completed {metrics.successful_tasks} tasks successfully",
                    ),
                )
                bound_log.info(
                    "engine.completed",
                    duration_ms=round(elapsed, 2),
                    tasks=metrics.executed_tasks,
                    confidence=confidence,
                )
            else:
                self._record_event(
                    events, WorkflowFailed(
                        workflow_id=workflow_id, correlation_id=correlation_id,
                        execution_plan_id=plan_id_str,
                        error=f"{metrics.failed_tasks} task(s) failed",
                    ),
                )
                bound_log.warning(
                    "engine.failed",
                    duration_ms=round(elapsed, 2),
                    failed=metrics.failed_tasks,
                )

            return result

        except Exception as exc:
            bound_log.exception("engine.failed", error=str(exc))
            self._state.transition_to(WorkflowStatus.FAILED)
            elapsed = (time.monotonic() - start_time) * 1000
            metrics.total_execution_time = elapsed
            metrics.total_runtime = elapsed
            self._record_event(
                events, WorkflowFailed(
                    workflow_id=workflow_id, correlation_id=correlation_id,
                    error=str(exc),
                ),
            )
            return self._build_result(
                workflow_id, WorkflowStatus.FAILED,
                traces, events, decisions, task_results, metrics, elapsed,
                summary=f"Engine error: {exc}",
            )

    async def pause(self, workflow_id: str) -> None:
        self._state.transition_to(WorkflowStatus.PAUSED)
        log.info("engine.paused", workflow_id=workflow_id)

    async def resume(self, workflow_id: str) -> None:
        self._state.transition_to(WorkflowStatus.RUNNING)
        log.info("engine.resumed", workflow_id=workflow_id)

    async def cancel(self, workflow_id: str) -> None:
        self._state.transition_to(WorkflowStatus.CANCELLED)
        log.info("engine.cancelled", workflow_id=workflow_id)

    # ── Internal: single task execution ─────────────────────────────────

    async def _execute_single_task(
        self,
        task: WorkflowTask,
        graph: WorkflowGraph,
        workflow_id: uuid.UUID,
        correlation_id: str,
        plan_id_str: str,
        traces: list[WorkflowTrace],
        events: list[dict[str, Any]],
        task_results: dict[uuid.UUID, TaskResult],
        metrics: WorkflowMetrics,
        bound_log,
        policy: WorkflowPolicy,
    ) -> None:
        bound_log.info("engine.task.start", task_id=str(task.task_id))

        # Dispatch
        trace, dispatched = await self._traced_stage(
            "task_dispatcher",
            lambda: self._dispatcher.dispatch(task),
            correlation_id=correlation_id,
        )
        traces.append(trace)
        self._record_event(
            events, TaskDispatched(
                workflow_id=workflow_id, correlation_id=correlation_id,
                execution_plan_id=plan_id_str,
                task_id=task.task_id,
                executor=dispatched.assigned_executor or "",
            ),
        )

        # Approval
        trace, approved = await self._traced_stage(
            "approval_manager",
            lambda: self._approval.request_approval(dispatched),
            correlation_id=correlation_id,
        )
        traces.append(trace)
        if not approved:
            task.decision_reason = "Awaiting human approval"
            bound_log.warning("engine.task.awaiting_approval", task_id=str(task.task_id))
            task.runtime_status = TaskExecutionStatus.WAITING
            return

        # Execute
        task.runtime_status = TaskExecutionStatus.RUNNING
        task.started_at = datetime.now(UTC)
        self._monitor.record_task_running(task)

        success = False
        errors: list[str] = []
        attempt = 0
        max_retries = policy.retry_limit

        while attempt == 0 or await self._retry.should_retry(task):
            if attempt > 0:
                task.decision_reason = f"Retry attempt {attempt}/{max_retries}"
                bound_log.info(
                    "engine.task.retrying",
                    task_id=str(task.task_id),
                    attempt=attempt,
                )
                delay = await self._retry.get_backoff(task)
                if delay > 0:
                    await asyncio.sleep(delay)
                    metrics.retry_time += delay * 1000

            try:
                from adip.workflow.execution.agent_executor import PlaceholderExecutor
                executor = PlaceholderExecutor()
                result_obj = await executor.execute(task)
                success = result_obj.success
                errors = list(result_obj.errors)
                if success:
                    break
            except Exception as exc:
                errors.append(str(exc))
                success = False

            task.retry_count = attempt + 1
            attempt += 1

        task.completed_at = datetime.now(UTC)
        task_results[task.task_id] = TaskResult(
            success=success,
            outputs=dict(task.outputs),
            execution_time=(
                task.completed_at - task.started_at
            ).total_seconds() if task.started_at else 0.0,
            warnings=[],
            errors=errors,
        )

        if success:
            task.runtime_status = TaskExecutionStatus.COMPLETED
            task.decision_reason = "Executed successfully"
            await self._monitor.on_task_completed(task, task_results[task.task_id], graph)
            metrics.successful_tasks += 1
            self._record_event(
                events, TaskCompleted(
                    workflow_id=workflow_id, correlation_id=correlation_id,
                    execution_plan_id=plan_id_str,
                    task_id=task.task_id,
                ),
            )
            bound_log.info("engine.task.completed", task_id=str(task.task_id))
        else:
            task.runtime_status = TaskExecutionStatus.FAILED
            task.decision_reason = f"Failed after {attempt} attempt(s): {'; '.join(errors)}"
            await self._monitor.on_task_failed(task, task_results[task.task_id], graph)
            metrics.failed_tasks += 1
            self._record_event(
                events, TaskFailed(
                    workflow_id=workflow_id, correlation_id=correlation_id,
                    execution_plan_id=plan_id_str,
                    task_id=task.task_id,
                    error="; ".join(errors),
                ),
            )
            bound_log.warning(
                "engine.task.failed",
                task_id=str(task.task_id),
                errors=errors,
            )

            if policy.failure_policy == "abort":
                raise RuntimeError(f"Task {task.task_id} failed; aborting per policy")

        metrics.executed_tasks += 1

    # ── Internal helpers ────────────────────────────────────────────────

    async def _traced_stage(
        self,
        stage_name: str,
        fn,
        input_summary: dict | None = None,
        correlation_id: str = "",
        workflow_state: str | None = None,
    ) -> tuple[WorkflowTrace, Any]:
        start = time.monotonic()
        trace = WorkflowTrace(
            stage_name=stage_name,
            started_at=datetime.now(UTC),
            workflow_state=workflow_state,
            input_summary=input_summary or {},
            workflow_version=WORKFLOW_VERSION,
            correlation_id=correlation_id,
        )
        try:
            output = await fn()
            trace.success = True
            trace.completed_at = datetime.now(UTC)
            trace.duration_ms = round((time.monotonic() - start) * 1000, 2)
            trace.output_summary = {"type": type(output).__name__}
            return trace, output
        except Exception as exc:
            trace.success = False
            trace.warnings.append(str(exc))
            trace.errors.append(str(exc))
            trace.completed_at = datetime.now(UTC)
            trace.duration_ms = round((time.monotonic() - start) * 1000, 2)
            trace.output_summary = {"error": str(exc)}
            return trace, None

    @staticmethod
    def _record_event(
        events: list[dict[str, Any]],
        event,
    ) -> None:
        payload = event.model_dump() if hasattr(event, "model_dump") else {}
        events.append(payload)

    @staticmethod
    def _build_result(
        workflow_id: uuid.UUID,
        status: WorkflowStatus,
        traces: list[WorkflowTrace],
        events: list[dict[str, Any]],
        decisions: list[WorkflowDecision],
        task_results: dict[uuid.UUID, TaskResult],
        metrics: WorkflowMetrics,
        elapsed: float,
        summary: str = "",
        efficiency: float = 0.0,
    ) -> WorkflowResult:
        return WorkflowResult(
            workflow_id=workflow_id,
            workflow_status=status,
            completed_tasks=metrics.successful_tasks,
            failed_tasks=metrics.failed_tasks,
            execution_time=elapsed,
            execution_summary=summary,
            task_results=task_results,
            decisions=decisions,
            events=events,
            traces=traces,
            metrics=metrics,
            execution_efficiency=efficiency,
        )

    @staticmethod
    async def _compute_efficiency(
        metrics: WorkflowMetrics,
        elapsed: float,
    ) -> float:
        if elapsed <= 0:
            return 0.0
        total = metrics.executed_tasks or 1
        success_ratio = metrics.successful_tasks / total
        retry_penalty = max(0.0, 1.0 - (metrics.retry_attempts * 0.05))
        return round(min(100.0, success_ratio * retry_penalty * 100.0), 1)
