"""ExecutionScheduler — immediate, delayed, maintenance window, and retry scheduling.

Manages execution schedules for tasks and packages,
supporting immediate execution, delayed execution,
maintenance window constraints, and retry scheduling.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import structlog

log = structlog.get_logger(__name__)


class ScheduledExecution:
    """A scheduled execution entry."""

    def __init__(
        self,
        schedule_id: str = "",
        package_id: str = "",
        schedule_type: str = "immediate",
        scheduled_time: datetime | None = None,
        task_ids: list[str] | None = None,
        correlation_id: str = "",
    ) -> None:
        self.schedule_id = schedule_id
        self.package_id = package_id
        self.schedule_type = schedule_type
        self.scheduled_time = scheduled_time or datetime.now(UTC)
        self.task_ids = task_ids or []
        self.correlation_id = correlation_id
        self.created_at = datetime.now(UTC)
        self.executed: bool = False


class ExecutionScheduler:
    """Manages execution schedules for tasks and packages."""

    MAINTENANCE_WINDOWS: list[tuple[str, str, str]] = [
        ("monday", "02:00", "04:00"),
        ("wednesday", "02:00", "04:00"),
        ("saturday", "00:00", "06:00"),
    ]

    def __init__(self) -> None:
        self._schedules: dict[str, ScheduledExecution] = {}

    def schedule_immediate(
        self,
        package_id: str = "",
        task_ids: list[str] | None = None,
        correlation_id: str = "",
    ) -> ScheduledExecution:
        """Schedule for immediate execution.

        Args:
            package_id: The package to execute.
            task_ids: Task IDs to execute.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            A ScheduledExecution with type='immediate'.
        """
        sched = ScheduledExecution(
            schedule_id=f"imm-{package_id[:8]}" if package_id else "imm-unknown",
            package_id=package_id,
            schedule_type="immediate",
            scheduled_time=datetime.now(UTC),
            task_ids=task_ids or [],
            correlation_id=correlation_id,
        )
        self._schedules[sched.schedule_id] = sched
        log.info(
            "scheduler.immediate",
            schedule_id=sched.schedule_id,
            package_id=package_id,
            correlation_id=correlation_id,
        )
        return sched

    def schedule_delayed(
        self,
        package_id: str = "",
        delay_seconds: int = 0,
        task_ids: list[str] | None = None,
        correlation_id: str = "",
    ) -> ScheduledExecution:
        """Schedule for delayed execution.

        Args:
            package_id: The package to execute.
            delay_seconds: Delay in seconds before execution.
            task_ids: Task IDs to execute.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            A ScheduledExecution with type='delayed'.
        """
        scheduled_time = datetime.now(UTC) + timedelta(seconds=max(0, delay_seconds))
        sched = ScheduledExecution(
            schedule_id=f"del-{package_id[:8]}" if package_id else "del-unknown",
            package_id=package_id,
            schedule_type="delayed",
            scheduled_time=scheduled_time,
            task_ids=task_ids or [],
            correlation_id=correlation_id,
        )
        self._schedules[sched.schedule_id] = sched
        log.info(
            "scheduler.delayed",
            schedule_id=sched.schedule_id,
            delay_seconds=delay_seconds,
            correlation_id=correlation_id,
        )
        return sched

    def schedule_maintenance_window(
        self,
        package_id: str = "",
        window_name: str = "next",
        task_ids: list[str] | None = None,
        correlation_id: str = "",
    ) -> ScheduledExecution:
        """Schedule for the next available maintenance window.

        Args:
            package_id: The package to execute.
            window_name: Specific window name or 'next' for the next available.
            task_ids: Task IDs to execute.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            A ScheduledExecution scheduled during a maintenance window.
        """
        scheduled_time = self._find_next_maintenance_window(window_name)
        sched = ScheduledExecution(
            schedule_id=f"mnt-{package_id[:8]}" if package_id else "mnt-unknown",
            package_id=package_id,
            schedule_type="maintenance_window",
            scheduled_time=scheduled_time,
            task_ids=task_ids or [],
            correlation_id=correlation_id,
        )
        self._schedules[sched.schedule_id] = sched
        log.info(
            "scheduler.maintenance_window",
            schedule_id=sched.schedule_id,
            window_name=window_name,
            scheduled_time=scheduled_time.isoformat(),
            correlation_id=correlation_id,
        )
        return sched

    def schedule_retry(
        self,
        package_id: str = "",
        attempt: int = 0,
        delay_seconds: int = 30,
        task_ids: list[str] | None = None,
        correlation_id: str = "",
    ) -> ScheduledExecution:
        """Schedule a retry attempt.

        Args:
            package_id: The package to retry.
            attempt: The retry attempt number.
            delay_seconds: Delay before retry.
            task_ids: Task IDs to retry.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            A ScheduledExecution with type='retry'.
        """
        delay = max(0, delay_seconds)
        scheduled_time = datetime.now(UTC) + timedelta(seconds=delay)
        sched = ScheduledExecution(
            schedule_id=f"ret-{package_id[:8]}-a{attempt}" if package_id else f"ret-unknown-a{attempt}",
            package_id=package_id,
            schedule_type="retry",
            scheduled_time=scheduled_time,
            task_ids=task_ids or [],
            correlation_id=correlation_id,
        )
        self._schedules[sched.schedule_id] = sched
        log.info(
            "scheduler.retry",
            schedule_id=sched.schedule_id,
            attempt=attempt,
            delay_seconds=delay,
            correlation_id=correlation_id,
        )
        return sched

    def get_schedule(self, schedule_id: str) -> ScheduledExecution | None:
        """Get a scheduled execution by ID."""
        return self._schedules.get(schedule_id)

    def get_all_schedules(self) -> list[ScheduledExecution]:
        """Get all scheduled executions."""
        return list(self._schedules.values())

    def get_pending_schedules(self) -> list[ScheduledExecution]:
        """Get schedules that are pending (not yet executed)."""
        now = datetime.now(UTC)
        return [s for s in self._schedules.values() if not s.executed and s.scheduled_time <= now]

    def mark_executed(self, schedule_id: str) -> bool:
        """Mark a schedule as executed.

        Args:
            schedule_id: The schedule ID to mark.

        Returns:
            True if found and marked, False otherwise.
        """
        if schedule_id in self._schedules:
            self._schedules[schedule_id].executed = True
            log.info("scheduler.marked_executed", schedule_id=schedule_id)
            return True
        return False

    def cancel(self, schedule_id: str) -> bool:
        """Cancel a scheduled execution.

        Args:
            schedule_id: The schedule ID to cancel.

        Returns:
            True if cancelled, False if not found.
        """
        if schedule_id in self._schedules:
            del self._schedules[schedule_id]
            log.info("scheduler.cancelled", schedule_id=schedule_id)
            return True
        return False

    def _find_next_maintenance_window(self, window_name: str) -> datetime:
        """Find the next maintenance window time (deterministic placeholder)."""
        now = datetime.now(UTC)
        if window_name != "next":
            for day, start, end in self.MAINTENANCE_WINDOWS:
                if window_name.lower() == f"{day}-{start}-{end}":
                    return now + timedelta(hours=2)
        return now + timedelta(hours=1)
