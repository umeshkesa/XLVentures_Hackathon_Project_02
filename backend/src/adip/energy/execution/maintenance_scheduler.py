"""MaintenanceScheduler — schedules maintenance activities.

Deterministic placeholder for scheduling preventive, predictive,
corrective, and emergency maintenance on energy assets.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from enum import StrEnum

import structlog

from adip.energy.enums import MaintenanceType
from adip.energy.execution.models import MaintenanceSchedule

log = structlog.get_logger(__name__)

_PREVENTIVE_INTERVAL_DAYS = 90
_PREDICTIVE_INTERVAL_DAYS = 30
_CORRECTIVE_PRIORITY = "high"
_EMERGENCY_PRIORITY = "critical"
_NORMAL_PRIORITY = "normal"


class SchedulePriority(StrEnum):
    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class MaintenanceScheduler:
    """Schedules maintenance activities for energy assets."""

    def __init__(self) -> None:
        self._schedules: list[MaintenanceSchedule] = []

    def schedule(
        self,
        asset_id: str,
        maintenance_type: str,
        due_date: datetime | None = None,
        description: str = "",
        correlation_id: str = "",
    ) -> MaintenanceSchedule:
        """Schedule a maintenance activity.

        Args:
            asset_id: The asset to schedule maintenance for.
            maintenance_type: Type of maintenance.
            due_date: When the maintenance is due (auto-calculated if None).
            description: Description of the scheduled maintenance.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The created MaintenanceSchedule.
        """
        maint_type = self._parse_maintenance_type(maintenance_type)
        actual_due = due_date or self._calculate_due_date(maint_type)
        priority = self._determine_priority(maint_type)

        schedule = MaintenanceSchedule(
            asset_id=self._parse_uuid(asset_id),
            maintenance_type=maint_type,
            due_date=actual_due,
            priority=priority,
            description=description or f"{maint_type.value} maintenance",
        )
        self._schedules.append(schedule)

        log.info(
            "energy.maintenance.scheduled",
            asset_id=asset_id,
            maintenance_type=maint_type.value,
            due_date=actual_due.isoformat(),
            priority=priority,
            correlation_id=correlation_id,
        )
        return schedule

    def get_schedules_for_asset(
        self,
        asset_id: str,
    ) -> list[MaintenanceSchedule]:
        """Get all schedules for an asset.

        Args:
            asset_id: The asset identifier.

        Returns:
            List of MaintenanceSchedule for the asset.
        """
        return [
            s
            for s in self._schedules
            if str(s.asset_id) == asset_id
        ]

    def get_upcoming_schedules(
        self,
        days_ahead: int = 30,
    ) -> list[MaintenanceSchedule]:
        """Get schedules due within a given number of days.

        Args:
            days_ahead: Number of days to look ahead.

        Returns:
            List of upcoming MaintenanceSchedule objects.
        """
        now = datetime.now(UTC)
        cutoff = now + timedelta(days=days_ahead)
        return [
            s
            for s in self._schedules
            if now <= s.due_date <= cutoff
        ]

    def get_overdue_schedules(self) -> list[MaintenanceSchedule]:
        """Get schedules that are past their due date.

        Returns:
            List of overdue MaintenanceSchedule objects.
        """
        now = datetime.now(UTC)
        return [
            s
            for s in self._schedules
            if s.due_date < now
        ]

    def get_all_schedules(self) -> list[MaintenanceSchedule]:
        """Get all maintenance schedules.

        Returns:
            List of all MaintenanceSchedule objects.
        """
        return list(self._schedules)

    def cancel_schedule(self, schedule_id: str) -> bool:
        """Cancel a maintenance schedule.

        Args:
            schedule_id: The schedule identifier to cancel.

        Returns:
            True if cancelled, False if not found.
        """
        for i, s in enumerate(self._schedules):
            if str(s.schedule_id) == schedule_id:
                self._schedules.pop(i)
                log.info("energy.maintenance.schedule_cancelled", schedule_id=schedule_id)
                return True
        return False

    def _calculate_due_date(
        self,
        maint_type: MaintenanceType,
    ) -> datetime:
        """Calculate a deterministic due date based on maintenance type."""
        now = datetime.now(UTC)
        if maint_type == MaintenanceType.PREVENTIVE:
            return now + timedelta(days=_PREVENTIVE_INTERVAL_DAYS)
        if maint_type == MaintenanceType.PREDICTIVE:
            return now + timedelta(days=_PREDICTIVE_INTERVAL_DAYS)
        if maint_type == MaintenanceType.CORRECTIVE:
            return now + timedelta(days=7)
        if maint_type == MaintenanceType.EMERGENCY:
            return now + timedelta(hours=4)
        return now + timedelta(days=30)

    def _determine_priority(
        self,
        maint_type: MaintenanceType,
    ) -> str:
        """Determine priority based on maintenance type."""
        if maint_type == MaintenanceType.EMERGENCY:
            return SchedulePriority.CRITICAL.value
        if maint_type == MaintenanceType.CORRECTIVE:
            return SchedulePriority.HIGH.value
        return SchedulePriority.NORMAL.value

    def _parse_maintenance_type(self, value: str) -> MaintenanceType:
        """Parse a string into MaintenanceType."""
        for mt in MaintenanceType:
            if mt.value == value or mt.name == value:
                return mt
        return MaintenanceType.PREVENTIVE

    @staticmethod
    def _parse_uuid(value: str | uuid.UUID) -> uuid.UUID:
        if isinstance(value, uuid.UUID):
            return value
        try:
            return uuid.UUID(value)
        except ValueError:
            return uuid.uuid5(uuid.NAMESPACE_DNS, value)
