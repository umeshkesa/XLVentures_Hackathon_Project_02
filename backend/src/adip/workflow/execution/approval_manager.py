"""Approval manager — placeholder gate for human-in-the-loop approvals."""

from __future__ import annotations

import time
import uuid

import structlog

from adip.workflow.contracts.models import WorkflowTask
from adip.workflow.interfaces import ApprovalManager

log = structlog.get_logger(__name__)


class PlaceholderApprovalManager(ApprovalManager):
    """Deterministic placeholder approval gate.

    For Phase 2 this component checks the task metadata key
    ``requires_human_approval``.  When ``True`` it logs the requirement
    and returns ``False`` (approval pending).  When ``False`` or absent
    it returns ``True`` (automatically approved).

    No UI, no HITL integration — placeholder only.
    """

    async def request_approval(self, task: WorkflowTask) -> bool:
        start = time.monotonic()
        correlation_id = str(uuid.uuid4())
        bound_log = log.bind(
            task_id=str(task.task_id),
            task_name=task.task_name,
            correlation_id=correlation_id,
        )

        requires = task.execution_metadata.get(
            "requires_human_approval", False,
        )

        if requires:
            bound_log.info(
                "approval.required",
                message="Task requires human approval — no HITL available",
            )
            return False

        elapsed = (time.monotonic() - start) * 1000
        bound_log.info(
            "approval.granted",
            duration_ms=round(elapsed, 2),
        )
        return True
