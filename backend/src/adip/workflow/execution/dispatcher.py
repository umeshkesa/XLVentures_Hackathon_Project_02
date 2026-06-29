"""Task dispatcher — routes tasks to placeholder executors."""

from __future__ import annotations

import time
import uuid

import structlog

from adip.workflow.contracts.models import WorkflowTask
from adip.workflow.interfaces import TaskDispatcher

log = structlog.get_logger(__name__)


class PlaceholderDispatcher(TaskDispatcher):
    """Deterministic placeholder task router.

    For Phase 2 the dispatcher assigns a fixed executor name based on
    the task metadata.  Future phases will integrate with the Agent
    Registry to select Knowledge, Memory, Rule, Tool, Sensor, Action,
    or custom executors.
    """

    EXECUTOR_MAP: dict[str, str] = {
        "data_search": "search_agent",
        "computation": "compute_agent",
        "analytics": "analytics_agent",
        "summarization": "summary_agent",
        "translation": "translate_agent",
        "database": "db_agent",
        "api_call": "api_agent",
        "default": "default_agent",
    }

    async def dispatch(self, task: WorkflowTask) -> WorkflowTask:
        start = time.monotonic()
        correlation_id = str(uuid.uuid4())
        bound_log = log.bind(
            task_id=str(task.task_id),
            correlation_id=correlation_id,
        )

        capability = task.execution_metadata.get(
            "required_capability", "default",
        )
        executor = self.EXECUTOR_MAP.get(capability, "default_agent")
        task.assigned_executor = executor

        elapsed = (time.monotonic() - start) * 1000
        bound_log.info(
            "dispatcher.dispatched",
            executor=executor,
            duration_ms=round(elapsed, 2),
        )

        return task
