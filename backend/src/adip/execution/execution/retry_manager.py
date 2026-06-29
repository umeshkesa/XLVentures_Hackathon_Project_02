"""RetryManager — retry logic with limits, delay, and policy support.

Manages retry attempts for failed tasks, evaluating retry
policies, calculating delays with exponential backoff,
and enforcing retry limits.
"""

from __future__ import annotations

from datetime import UTC, datetime

import structlog

log = structlog.get_logger(__name__)


class RetryRecord:
    """Record of a single retry attempt."""

    def __init__(
        self,
        task_id: str = "",
        attempt: int = 0,
        delay_seconds: int = 0,
        error: str = "",
        success: bool = False,
        timestamp: datetime | None = None,
    ) -> None:
        self.task_id = task_id
        self.attempt = attempt
        self.delay_seconds = delay_seconds
        self.error = error
        self.success = success
        self.timestamp = timestamp or datetime.now(UTC)


class RetryManager:
    """Manages retry attempts with policy evaluation and delay calculation."""

    def __init__(self) -> None:
        self._retry_records: dict[str, list[RetryRecord]] = {}

    def should_retry(
        self,
        task_id: str = "",
        attempt: int = 0,
        max_retries: int = 3,
        retry_on_timeout: bool = True,
        retry_on_error: bool = True,
        retryable_errors: list[str] | None = None,
        error: str = "",
        correlation_id: str = "",
    ) -> bool:
        """Determine if a task should be retried.

        Args:
            task_id: The task ID.
            attempt: Current retry attempt number (0-indexed).
            max_retries: Maximum allowed retries.
            retry_on_timeout: Whether to retry on timeout.
            retry_on_error: Whether to retry on error.
            retryable_errors: List of retryable error types.
            error: The error message.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            True if retry should be attempted, False otherwise.
        """
        if attempt >= max_retries:
            log.info(
                "retry_manager.max_retries_exceeded",
                task_id=task_id,
                attempt=attempt,
                max_retries=max_retries,
                correlation_id=correlation_id,
            )
            return False

        if not retry_on_timeout and "timeout" in error.lower():
            return False
        if not retry_on_error and error:
            return False
        if retryable_errors:
            for retryable in retryable_errors:
                if retryable.lower() in error.lower():
                    return True
            return False

        return True

    def get_delay(
        self,
        attempt: int = 0,
        base_delay_seconds: int = 30,
        backoff_multiplier: float = 2.0,
        max_delay_seconds: int = 3600,
        correlation_id: str = "",
    ) -> int:
        """Calculate delay before the next retry using exponential backoff.

        Args:
            attempt: The retry attempt number (0-indexed).
            base_delay_seconds: Initial delay in seconds.
            backoff_multiplier: Backoff multiplier.
            max_delay_seconds: Maximum delay in seconds.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            Delay in seconds before the next retry.
        """
        delay = int(base_delay_seconds * (backoff_multiplier ** attempt))
        delay = min(delay, max_delay_seconds)
        log.info(
            "retry_manager.delay_calculated",
            attempt=attempt,
            delay_seconds=delay,
            correlation_id=correlation_id,
        )
        return delay

    def record_retry(
        self,
        task_id: str = "",
        attempt: int = 0,
        delay_seconds: int = 0,
        error: str = "",
        success: bool = False,
        correlation_id: str = "",
    ) -> RetryRecord:
        """Record a retry attempt.

        Args:
            task_id: The task ID.
            attempt: The retry attempt number.
            delay_seconds: Delay before this retry.
            error: Error that triggered the retry.
            success: Whether the retry succeeded.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The created RetryRecord.
        """
        record = RetryRecord(
            task_id=task_id,
            attempt=attempt,
            delay_seconds=delay_seconds,
            error=error,
            success=success,
        )
        if task_id not in self._retry_records:
            self._retry_records[task_id] = []
        self._retry_records[task_id].append(record)
        log.info(
            "retry_manager.recorded",
            task_id=task_id,
            attempt=attempt,
            success=success,
            correlation_id=correlation_id,
        )
        return record

    def get_retry_count(self, task_id: str) -> int:
        """Get the number of retry attempts for a task.

        Args:
            task_id: The task ID.

        Returns:
            Number of retry attempts.
        """
        return len(self._retry_records.get(task_id, []))

    def get_retries(self, task_id: str) -> list[RetryRecord]:
        """Get all retry records for a task.

        Args:
            task_id: The task ID.

        Returns:
            List of RetryRecord for the task.
        """
        return list(self._retry_records.get(task_id, []))

    def get_all_retries(self) -> dict[str, list[RetryRecord]]:
        """Get all retry records across all tasks."""
        return {k: list(v) for k, v in self._retry_records.items()}

    def get_total_retries(self) -> int:
        """Get the total number of retry attempts across all tasks."""
        return sum(len(records) for records in self._retry_records.values())
