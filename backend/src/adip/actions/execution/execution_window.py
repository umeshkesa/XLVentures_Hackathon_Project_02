"""ExecutionWindowManager — execution window type management.

Manages execution windows for scheduling action steps,
supporting immediate, scheduled, maintenance window,
business hours, and emergency window types.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import structlog

from adip.actions.execution.models import ExecutionWindow

log = structlog.get_logger(__name__)


class ExecutionWindowManager:
    """Manages execution windows of different types."""

    WINDOW_TYPES = ["immediate", "scheduled", "maintenance", "business_hours", "emergency"]

    def create_window(
        self,
        window_type: str = "immediate",
        step_ids: list[str] | None = None,
        scheduled_start: datetime | None = None,
        correlation_id: str = "",
    ) -> ExecutionWindow:
        """Create an execution window of the specified type.

        Args:
            window_type: Type of window (immediate, scheduled, maintenance, business_hours, emergency).
            step_ids: Step IDs to assign to this window.
            scheduled_start: Scheduled start time (for scheduled type).
            correlation_id: Optional correlation ID for tracing.

        Returns:
            An ExecutionWindow with appropriate time bounds.
        """
        step_ids = step_ids or []
        now = datetime.now(UTC)

        if window_type == "immediate":
            start = now
            scheduled_end = now + timedelta(hours=1)
            description = "Immediate execution window"
        elif window_type == "scheduled":
            start = scheduled_start or (now + timedelta(hours=2))
            scheduled_end = start + timedelta(hours=4)
            description = f"Scheduled execution window starting at {start.isoformat()}"
        elif window_type == "maintenance":
            start = now + timedelta(hours=1)
            scheduled_end = start + timedelta(hours=3)
            description = "Planned maintenance window"
        elif window_type == "business_hours":
            start = now
            scheduled_end = start + timedelta(hours=8)
            description = "Business hours execution window (08:00-18:00)"
        elif window_type == "emergency":
            start = now
            scheduled_end = start + timedelta(minutes=30)
            description = "Emergency execution window — immediate override"
        else:
            start = now
            scheduled_end = start + timedelta(hours=1)
            description = "Default execution window"

        window = ExecutionWindow(
            window_type=window_type,
            step_ids=step_ids,
            scheduled_start=start,
            scheduled_end=scheduled_end,
            description=description,
        )
        log.info(
            "execution_window.created",
            window_type=window_type,
            step_count=len(step_ids),
            scheduled_start=start.isoformat(),
            correlation_id=correlation_id,
        )
        return window

    def validate_window(
        self,
        window: ExecutionWindow,
        correlation_id: str = "",
    ) -> list[str]:
        """Validate an execution window.

        Args:
            window: The execution window to validate.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            List of validation violations (empty if valid).
        """
        violations: list[str] = []
        if window.window_type not in self.WINDOW_TYPES:
            violations.append(f"Invalid window type: {window.window_type}")
        if window.scheduled_start and window.scheduled_end:
            if window.scheduled_start >= window.scheduled_end:
                violations.append("Window start must be before end")
        return violations

    def get_window_types(self) -> list[str]:
        """Return the list of supported window types."""
        return list(self.WINDOW_TYPES)

    def estimate_duration_minutes(
        self,
        window_type: str = "immediate",
    ) -> int:
        """Estimate the duration of a window type in minutes."""
        estimates = {
            "immediate": 60,
            "scheduled": 240,
            "maintenance": 180,
            "business_hours": 480,
            "emergency": 30,
        }
        return estimates.get(window_type, 60)
