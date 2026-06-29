"""AlarmCorrelationEngine — groups related alarms into incidents.

Deterministic placeholder implementation that correlates
alarms by asset proximity, temporal proximity, and severity
to form incident groups.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

import structlog

from adip.energy.enums import AlarmSeverity
from adip.energy.execution.models import CorrelationGroup

log = structlog.get_logger(__name__)

_CORRELATION_WINDOW_MINUTES = 30

_SEVERITY_ORDER: dict[AlarmSeverity, int] = {
    AlarmSeverity.CRITICAL: 5,
    AlarmSeverity.MAJOR: 4,
    AlarmSeverity.MINOR: 3,
    AlarmSeverity.WARNING: 2,
    AlarmSeverity.INFO: 1,
}


class AlarmCorrelationEngine:
    """Correlates related alarms into groups for incident creation."""

    def correlate(
        self,
        alarms: list[dict[str, Any]] | None = None,
        correlation_id: str = "",
    ) -> list[CorrelationGroup]:
        """Correlate a list of alarms into groups.

        Args:
            alarms: List of alarm dicts with 'alarm_id', 'asset_id',
                    'severity', and 'raised_at'.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            List of CorrelationGroup objects.
        """
        alarms = alarms or []
        if not alarms:
            return []

        groups: list[CorrelationGroup] = []
        assigned: set[str] = set()

        sorted_alarms = sorted(
            alarms,
            key=lambda a: a.get("raised_at", datetime.min),
        )

        for i, alarm in enumerate(sorted_alarms):
            alarm_id = str(alarm.get("alarm_id", f"alarm_{i}"))
            if alarm_id in assigned:
                continue

            asset_id = str(alarm.get("asset_id", ""))
            severity_str = str(alarm.get("severity", "INFO"))
            raised_at = alarm.get("raised_at", datetime.now(UTC))

            group_ids: list[str] = [alarm_id]
            group_assets: set[str] = {asset_id} if asset_id else set()
            assigned.add(alarm_id)

            for j, other in enumerate(sorted_alarms):
                other_id = str(other.get("alarm_id", f"alarm_{j}"))
                if other_id in assigned:
                    continue

                other_asset = str(other.get("asset_id", ""))
                other_time = other.get("raised_at", datetime.now(UTC))

                same_asset = other_asset == asset_id if asset_id else False
                same_asset = same_asset or (asset_id == "")

                time_diff = abs((raised_at - other_time).total_seconds())
                within_window = time_diff <= _CORRELATION_WINDOW_MINUTES * 60

                if same_asset and within_window:
                    group_ids.append(other_id)
                    if other_asset:
                        group_assets.add(other_asset)
                    assigned.add(other_id)

            highest = max(
                (self._parse_severity(
                    str(a.get("severity", "INFO"))
                ) for a in sorted_alarms
                 if str(a.get("alarm_id", "")) in group_ids),
                key=lambda s: _SEVERITY_ORDER.get(s, 0),
                default=AlarmSeverity.INFO,
            )

            reason = (
                f"{len(group_ids)} alarms correlated by asset proximity"
                if len(group_ids) > 1
                else "Uncorrelated alarm (standalone)"
            )

            group = CorrelationGroup(
                alarm_ids=[self._parse_uuid(aid) for aid in group_ids],
                asset_ids=[self._parse_uuid(aid) for aid in group_assets],
                highest_severity=highest,
                correlation_reason=reason,
            )
            groups.append(group)

        log.info(
            "energy.alarm_correlation.complete",
            input_count=len(alarms),
            group_count=len(groups),
            correlation_id=correlation_id,
        )
        return groups

    def _parse_severity(self, value: str) -> AlarmSeverity:
        """Parse a string into AlarmSeverity."""
        for s in AlarmSeverity:
            if s.value == value or s.name == value:
                return s
        return AlarmSeverity.INFO

    @staticmethod
    def _parse_uuid(value: str) -> uuid.UUID:
        try:
            return uuid.UUID(value)
        except ValueError:
            return uuid.uuid5(uuid.NAMESPACE_DNS, value)
