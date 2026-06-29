"""HealthScoreCalculator — calculates asset health scores.

Deterministic placeholder health score using sensor readings,
maintenance history, asset age, and alarm history.
"""

from __future__ import annotations

import uuid
from typing import Any

import structlog

from adip.energy.execution.models import HealthScoreResult

log = structlog.get_logger(__name__)


class HealthScoreCalculator:
    """Calculates deterministic health scores for energy assets."""

    def calculate(
        self,
        asset_id: str,
        sensor_readings: list[dict[str, Any]] | None = None,
        maintenance_count: int = 0,
        asset_age_days: float = 0.0,
        active_alarm_count: int = 0,
        correlation_id: str = "",
    ) -> HealthScoreResult:
        """Calculate a deterministic health score for an asset.

        Args:
            asset_id: The asset identifier.
            sensor_readings: List of sensor readings with 'type' and 'value'.
            maintenance_count: Number of completed maintenance activities.
            asset_age_days: Age of the asset in days.
            active_alarm_count: Number of currently active alarms.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            HealthScoreResult with component and overall scores.
        """
        sensor_readings = sensor_readings or []

        sensor_score = self._calculate_sensor_score(sensor_readings)

        maintenance_score = self._calculate_maintenance_score(maintenance_count)

        age_score = self._calculate_age_score(asset_age_days)

        alarm_score = self._calculate_alarm_score(active_alarm_count)

        overall_score = round(
            sensor_score * 0.35
            + maintenance_score * 0.25
            + age_score * 0.15
            + alarm_score * 0.25,
            4,
        )
        overall_score = max(0.0, min(1.0, overall_score))

        result = HealthScoreResult(
            asset_id=self._parse_uuid(asset_id),
            overall_score=overall_score,
            sensor_score=sensor_score,
            maintenance_score=maintenance_score,
            age_score=age_score,
            alarm_score=alarm_score,
        )
        log.info(
            "energy.health_score.calculated",
            asset_id=asset_id,
            overall_score=overall_score,
            correlation_id=correlation_id,
        )
        return result

    def _calculate_sensor_score(
        self,
        readings: list[dict[str, Any]],
    ) -> float:
        """Calculate sensor-based health score.

        Base score 1.0, subtract 0.05 for each reading outside
        normal ranges.
        """
        if not readings:
            return 0.8

        score = 1.0
        for reading in readings:
            sensor_type = str(reading.get("type", "")).upper()
            value = float(reading.get("value", 0.0))

            if sensor_type == "TEMPERATURE" and value > 80.0 or sensor_type == "VIBRATION" and value > 50.0:
                score -= 0.1
            elif sensor_type == "PRESSURE" and value > 500.0:
                score -= 0.05

        return max(0.0, score)

    def _calculate_maintenance_score(self, maintenance_count: int) -> float:
        """Calculate maintenance-based health score.

        Assets with regular maintenance score higher.
        More than 5 maintenance activities = well maintained.
        No maintenance = poor score.
        """
        if maintenance_count >= 5:
            return 1.0
        if maintenance_count >= 3:
            return 0.8
        if maintenance_count >= 1:
            return 0.6
        return 0.3

    def _calculate_age_score(self, age_days: float) -> float:
        """Calculate age-based health score.

        Newer assets score higher. Linear degradation from
        1.0 at day 0 to 0.3 at 20 years (7300 days).
        """
        if age_days <= 0:
            return 1.0

        degradation = age_days / 7300.0
        score = 1.0 - (degradation * 0.7)
        return max(0.3, min(1.0, score))

    def _calculate_alarm_score(self, active_alarm_count: int) -> float:
        """Calculate alarm-based health score.

        Each active alarm reduces the score by 0.15.
        """
        if active_alarm_count <= 0:
            return 1.0

        score = 1.0 - (active_alarm_count * 0.15)
        return max(0.0, score)

    @staticmethod
    def _parse_uuid(value: str | uuid.UUID) -> uuid.UUID:
        if isinstance(value, uuid.UUID):
            return value
        try:
            return uuid.UUID(value)
        except ValueError:
            return uuid.uuid5(uuid.NAMESPACE_DNS, value)
