"""Retry manager — interprets ``RetryPolicy`` to make retry decisions."""

from __future__ import annotations

import asyncio
import uuid

import structlog

from adip.workflow.contracts.models import WorkflowTask
from adip.workflow.enums import RetryPolicy
from adip.workflow.interfaces import RetryManager

log = structlog.get_logger(__name__)

# Default retry limits per policy when the task does not carry its own
# metadata override.
_DEFAULT_MAX_RETRIES: dict[RetryPolicy, int] = {
    RetryPolicy.NEVER: 0,
    RetryPolicy.IMMEDIATE: 3,
    RetryPolicy.FIXED_DELAY: 3,
    RetryPolicy.EXPONENTIAL_BACKOFF: 5,
}

_DEFAULT_BACKOFF_SECONDS: float = 1.0
_DEFAULT_MAX_BACKOFF_SECONDS: float = 60.0


class DefaultRetryManager(RetryManager):
    """Deterministic retry manager.

    Supports all four retry policies:
    * ``NEVER`` — no retries allowed.
    * ``IMMEDIATE`` — retry up to N times with zero delay.
    * ``FIXED_DELAY`` — retry with a constant delay between attempts.
    * ``EXPONENTIAL_BACKOFF`` — retry with exponentially increasing delay
      (capped at ``max_backoff_seconds``).
    """

    def __init__(
        self,
        default_max_retries: int | None = None,
        default_backoff: float = _DEFAULT_BACKOFF_SECONDS,
        max_backoff: float = _DEFAULT_MAX_BACKOFF_SECONDS,
    ) -> None:
        self._default_max_retries = default_max_retries
        self._default_backoff = default_backoff
        self._max_backoff = max_backoff

    async def should_retry(self, task: WorkflowTask) -> bool:
        policy = task.retry_policy
        correlation_id = str(uuid.uuid4())
        bound_log = log.bind(
            task_id=str(task.task_id),
            policy=policy.value,
            retry_count=task.retry_count,
            correlation_id=correlation_id,
        )

        if policy == RetryPolicy.NEVER:
            bound_log.debug("retry.never")
            return False

        max_r = self._resolve_max_retries(task)
        if task.retry_count >= max_r:
            bound_log.info(
                "retry.exhausted",
                max_retries=max_r,
            )
            return False

        bound_log.info("retry.should_retry", remaining=max_r - task.retry_count)
        return True

    async def get_backoff(self, task: WorkflowTask) -> float:
        policy = task.retry_policy
        correlation_id = str(uuid.uuid4())
        bound_log = log.bind(
            task_id=str(task.task_id),
            policy=policy.value,
            retry_count=task.retry_count,
            correlation_id=correlation_id,
        )

        base = self._resolve_backoff(task)

        if policy == RetryPolicy.IMMEDIATE:
            return 0.0
        if policy == RetryPolicy.FIXED_DELAY:
            return base
        if policy == RetryPolicy.EXPONENTIAL_BACKOFF:
            delay = base * (2.0 ** (task.retry_count - 1))
            capped = min(delay, self._max_backoff)
            bound_log.debug(
                "retry.backoff",
                raw_delay=round(delay, 2),
                capped_delay=round(capped, 2),
            )
            return capped

        return 0.0

    async def execute_with_retry(
        self,
        task: WorkflowTask,
        execute_fn,
    ) -> tuple[bool, list[str]]:
        """Convenience helper: call ``execute_fn`` and handle retries.

        Returns ``(success, errors)``.
        """
        attempt = 0
        errors: list[str] = []
        correlation_id = str(uuid.uuid4())

        while True:
            attempt += 1
            try:
                result = await execute_fn(task)
                if result.success:
                    return True, []
                errors.extend(result.errors)
            except Exception as exc:
                errors.append(str(exc))

            task.retry_count = attempt
            if not await self.should_retry(task):
                break

            delay = await self.get_backoff(task)
            if delay > 0:
                await asyncio.sleep(delay)

            log.info(
                "retry.attempt",
                task_id=str(task.task_id),
                attempt=attempt,
                correlation_id=correlation_id,
            )

        return False, errors

    # ── Internal helpers ───────────────────────────────────────────────

    def _resolve_max_retries(self, task: WorkflowTask) -> int:
        if self._default_max_retries is not None:
            return self._default_max_retries
        return _DEFAULT_MAX_RETRIES.get(task.retry_policy, 0)

    def _resolve_backoff(self, task: WorkflowTask) -> float:
        meta_backoff = task.execution_metadata.get("backoff_seconds")
        if meta_backoff is not None:
            return float(meta_backoff)
        return self._default_backoff
