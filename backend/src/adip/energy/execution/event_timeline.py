"""EnergyEventTimeline — tracks chronological energy domain events.

Records and queries timeline entries for sensor updates, alarms,
incidents, maintenance, and recovery events.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

import structlog

from adip.energy.execution.models import TimelineEntry

log = structlog.get_logger(__name__)


class EnergyEventTimeline:
    """Tracks chronological events in the energy domain."""

    def __init__(self) -> None:
        self._entries: list[TimelineEntry] = []

    def record_sensor_update(
        self,
        asset_id: str,
        sensor_id: str = "",
        value: float = 0.0,
        unit: str = "",
        correlation_id: str = "",
    ) -> TimelineEntry:
        """Record a sensor update event.

        Args:
            asset_id: The asset identifier.
            sensor_id: The sensor identifier.
            value: The sensor reading value.
            unit: The measurement unit.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The created TimelineEntry.
        """
        entry = TimelineEntry(
            asset_id=self._parse_uuid(asset_id),
            event_type="sensor_update",
            description=f"Sensor {sensor_id}: {value} {unit}".strip(),
            details={
                "sensor_id": sensor_id,
                "value": value,
                "unit": unit,
            },
        )
        self._entries.append(entry)
        log.info(
            "energy.timeline.sensor_update",
            asset_id=asset_id,
            sensor_id=sensor_id,
            correlation_id=correlation_id,
        )
        return entry

    def record_alarm(
        self,
        asset_id: str,
        alarm_id: str = "",
        severity: str = "",
        description: str = "",
        correlation_id: str = "",
    ) -> TimelineEntry:
        """Record an alarm event.

        Args:
            asset_id: The asset identifier.
            alarm_id: The alarm identifier.
            severity: Alarm severity.
            description: Alarm description.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The created TimelineEntry.
        """
        entry = TimelineEntry(
            asset_id=self._parse_uuid(asset_id),
            event_type="alarm",
            description=description or f"Alarm {alarm_id} ({severity})",
            details={
                "alarm_id": alarm_id,
                "severity": severity,
            },
        )
        self._entries.append(entry)
        log.info(
            "energy.timeline.alarm",
            asset_id=asset_id,
            alarm_id=alarm_id,
            severity=severity,
            correlation_id=correlation_id,
        )
        return entry

    def record_incident(
        self,
        asset_id: str,
        incident_id: str = "",
        priority: str = "",
        description: str = "",
        correlation_id: str = "",
    ) -> TimelineEntry:
        """Record an incident event.

        Args:
            asset_id: The asset identifier.
            incident_id: The incident identifier.
            priority: Incident priority.
            description: Incident description.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The created TimelineEntry.
        """
        entry = TimelineEntry(
            asset_id=self._parse_uuid(asset_id),
            event_type="incident",
            description=description or f"Incident {incident_id} ({priority})",
            details={
                "incident_id": incident_id,
                "priority": priority,
            },
        )
        self._entries.append(entry)
        log.info(
            "energy.timeline.incident",
            asset_id=asset_id,
            incident_id=incident_id,
            correlation_id=correlation_id,
        )
        return entry

    def record_maintenance(
        self,
        asset_id: str,
        maintenance_type: str = "",
        description: str = "",
        correlation_id: str = "",
    ) -> TimelineEntry:
        """Record a maintenance event.

        Args:
            asset_id: The asset identifier.
            maintenance_type: Type of maintenance.
            description: Maintenance description.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The created TimelineEntry.
        """
        entry = TimelineEntry(
            asset_id=self._parse_uuid(asset_id),
            event_type="maintenance",
            description=description or f"Maintenance: {maintenance_type}",
            details={
                "maintenance_type": maintenance_type,
            },
        )
        self._entries.append(entry)
        log.info(
            "energy.timeline.maintenance",
            asset_id=asset_id,
            maintenance_type=maintenance_type,
            correlation_id=correlation_id,
        )
        return entry

    def record_recovery(
        self,
        asset_id: str,
        recovery_type: str = "",
        description: str = "",
        correlation_id: str = "",
    ) -> TimelineEntry:
        """Record a recovery event.

        Args:
            asset_id: The asset identifier.
            recovery_type: Type of recovery.
            description: Recovery description.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The created TimelineEntry.
        """
        entry = TimelineEntry(
            asset_id=self._parse_uuid(asset_id),
            event_type="recovery",
            description=description or f"Recovery: {recovery_type}",
            details={
                "recovery_type": recovery_type,
            },
        )
        self._entries.append(entry)
        log.info(
            "energy.timeline.recovery",
            asset_id=asset_id,
            recovery_type=recovery_type,
            correlation_id=correlation_id,
        )
        return entry

    def get_events_for_asset(
        self,
        asset_id: str,
        event_type: str | None = None,
    ) -> list[TimelineEntry]:
        """Get timeline events for an asset.

        Args:
            asset_id: The asset identifier.
            event_type: Optional event type filter.

        Returns:
            List of matching TimelineEntry objects.
        """
        result = [
            e
            for e in self._entries
            if str(e.asset_id) == asset_id
        ]
        if event_type:
            result = [e for e in result if e.event_type == event_type]
        return result

    def get_events_by_type(
        self,
        event_type: str,
    ) -> list[TimelineEntry]:
        """Get all events of a specific type.

        Args:
            event_type: The event type to filter by.

        Returns:
            List of matching TimelineEntry objects.
        """
        return [
            e
            for e in self._entries
            if e.event_type == event_type
        ]

    def get_recent_events(
        self,
        minutes: int = 60,
    ) -> list[TimelineEntry]:
        """Get events from the last N minutes.

        Args:
            minutes: Number of minutes to look back.

        Returns:
            List of recent TimelineEntry objects.
        """
        cutoff = datetime.now(UTC) - timedelta(minutes=minutes)
        return [
            e
            for e in self._entries
            if e.timestamp >= cutoff
        ]

    def get_all_events(self) -> list[TimelineEntry]:
        """Get all timeline events.

        Returns:
            List of all TimelineEntry objects.
        """
        return list(self._entries)

    def clear(self) -> None:
        """Clear all timeline entries."""
        self._entries.clear()

    @staticmethod
    def _parse_uuid(value: str | uuid.UUID) -> uuid.UUID:
        if isinstance(value, uuid.UUID):
            return value
        try:
            return uuid.UUID(value)
        except ValueError:
            return uuid.uuid5(uuid.NAMESPACE_DNS, value)
