"""Execution dispatcher — orchestrates single-task execution lifecycle.

Coordinates the dispatch → execute → retry → monitor flow for a single
task.  Does NOT manage cross-task orchestration — that is the
responsibility of ``WorkflowEngine`` (Phase 3).
"""

from __future__ import annotations

import asyncio
import time
import uuid
from datetime import UTC, datetime

import structlog

from adip.workflow.contracts.exceptions import (
    ApprovalException,
    TaskExecutionException,
)
from adip.workflow.contracts.models import (
    TaskResult,
    WorkflowGraph,
    WorkflowTask,
)
from adip.workflow.enums import TaskExecutionStatus
from adip.workflow.execution.trace import WORKFLOW_VERSION, WorkflowTrace
from adip.workflow.interfaces import (
    AgentExecutor,
    ApprovalManager,
    ExecutionMonitor,
    RetryManager,
    TaskDispatcher,
)

log = structlog.get_logger(__name__)


class DefaultExecutionDispatcher:
    """Orchestrates the full execution lifecycle for a single task.

    Pipeline per task:
        1. **Dispatch** — assign an executor via ``TaskDispatcher``.
        2. **Approve** — check ``ApprovalManager``.
        3. **Execute** — run task via ``AgentExecutor``.
        4. **Monitor** — notify ``ExecutionMonitor`` of outcome.
        5. **Retry** — if failed, consult ``RetryManager`` and loop.

    Each stage records a ``WorkflowTrace`` for observability.
    """

    def __init__(
        self,
        task_dispatcher: TaskDispatcher,
        agent_executor: AgentExecutor,
        execution_monitor: ExecutionMonitor,
        retry_manager: RetryManager,
        approval_manager: ApprovalManager,
    ) -> None:
        self._dispatcher = task_dispatcher
        self._executor = agent_executor
        self._monitor = execution_monitor
        self._retry = retry_manager
        self._approval = approval_manager

    async def execute(
        self,
        task: WorkflowTask,
        graph: WorkflowGraph,
    ) -> tuple[TaskResult, list[WorkflowTrace]]:
        """Execute a single task through the full lifecycle.

        Returns ``(TaskResult, list[WorkflowTrace])``.
        """
        correlation_id = str(uuid.uuid4())
        traces: list[WorkflowTrace] = []
        bound_log = log.bind(
            task_id=str(task.task_id),
            task_name=task.task_name,
            correlation_id=correlation_id,
        )

        bound_log.info("execution_dispatcher.start")

        # ── 1. Dispatch ───────────────────────────────────────────────
        trace, task = await self._run_stage(
            "task_dispatcher",
            lambda: self._dispatcher.dispatch(task),
            correlation_id=correlation_id,
        )
        traces.append(trace)

        # ── 2. Approve ────────────────────────────────────────────────
        trace, approved = await self._run_stage(
            "approval_manager",
            lambda: self._approval.request_approval(task),
            correlation_id=correlation_id,
        )
        traces.append(trace)

        if not approved:
            task.runtime_status = TaskExecutionStatus.WAITING
            err = "Task requires human approval — cannot execute"
            bound_log.warning(err)
            raise ApprovalException(err)

        # ── 3-5. Execute with retry loop ──────────────────────────────
        task.runtime_status = TaskExecutionStatus.RUNNING
        task.started_at = datetime.now(UTC)
        self._monitor.record_task_running(task)

        attempt = 0
        result: TaskResult | None = None

        while True:
            attempt += 1
            try:
                result = await self._executor.execute(task)
                break
            except Exception as exc:
                bound_log.error(
                    "execution_dispatcher.execute_failed",
                    attempt=attempt,
                    error=str(exc),
                )
                task.retry_count = attempt
                retry = await self._retry.should_retry(task)
                if not retry:
                    raise TaskExecutionException(
                        task_id=str(task.task_id),
                        message=str(exc),
                    ) from exc
                delay = await self._retry.get_backoff(task)
                if delay > 0:
                    await asyncio.sleep(delay)
                continue

        task.completed_at = datetime.now(UTC)
        task.runtime_status = (
            TaskExecutionStatus.COMPLETED
            if result.success
            else TaskExecutionStatus.FAILED
        )
        task.outputs = dict(result.outputs)

        if result.success:
            await self._monitor.on_task_completed(task, result, graph)
        else:
            await self._monitor.on_task_failed(task, result, graph)

        started = task.started_at.timestamp() if task.started_at else 0
        elapsed = (time.monotonic() - started) * 1000
        bound_log.info(
            "execution_dispatcher.completed",
            success=result.success,
            attempts=attempt,
            duration_ms=round(elapsed, 2),
        )

        return result, traces

    # ── Internal helpers ───────────────────────────────────────────────

    async def _run_stage(
        self,
        stage_name: str,
        fn,
        correlation_id: str = "",
    ) -> tuple[WorkflowTrace, object]:
        start = time.monotonic()
        trace = WorkflowTrace(
            stage_name=stage_name,
            started_at=datetime.now(UTC),
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
            trace.completed_at = datetime.now(UTC)
            trace.duration_ms = round((time.monotonic() - start) * 1000, 2)
            trace.output_summary = {"error": str(exc)}
            return trace, None
