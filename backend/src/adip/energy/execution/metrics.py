"""DomainMetrics — collects operational metrics for the energy domain.

Tracks asset count, sensor count, alarm count, incident count,
maintenance count, and average health score with snapshot
capabilities.
"""

from __future__ import annotations

import structlog

from adip.energy.execution.models import DomainMetricsSnapshot

log = structlog.get_logger(__name__)


class DomainMetrics:
    """Collects operational metrics for the energy domain."""

    def __init__(self) -> None:
        self._asset_count: int = 0
        self._sensor_count: int = 0
        self._alarm_count: int = 0
        self._incident_count: int = 0
        self._reading_count: int = 0
        self._maintenance_count: int = 0
        self._quality_count: int = 0
        self._compliance_count: int = 0
        self._diagnostics_count: int = 0
        self._pipeline_version_count: int = 0
        self._audit_count: int = 0
        self._export_count: int = 0
        self._health_scores: list[float] = []

    def increment_asset_count(self, delta: int = 1) -> None:
        """Increment the asset count.

        Args:
            delta: Amount to increment by.
        """
        self._asset_count += max(0, delta)
        log.debug("energy.metrics.asset_count", count=self._asset_count)

    def increment_sensor_count(self, delta: int = 1) -> None:
        """Increment the sensor count.

        Args:
            delta: Amount to increment by.
        """
        self._sensor_count += max(0, delta)
        log.debug("energy.metrics.sensor_count", count=self._sensor_count)

    def increment_alarm_count(self, delta: int = 1) -> None:
        """Increment the alarm count.

        Args:
            delta: Amount to increment by.
        """
        self._alarm_count += max(0, delta)
        log.debug("energy.metrics.alarm_count", count=self._alarm_count)

    def increment_incident_count(self, delta: int = 1) -> None:
        """Increment the incident count.

        Args:
            delta: Amount to increment by.
        """
        self._incident_count += max(0, delta)
        log.debug("energy.metrics.incident_count", count=self._incident_count)

    def increment_maintenance_count(self, delta: int = 1) -> None:
        """Increment the maintenance count.

        Args:
            delta: Amount to increment by.
        """
        self._maintenance_count += max(0, delta)
        log.debug("energy.metrics.maintenance_count", count=self._maintenance_count)

    def record_health_score(self, score: float) -> None:
        """Record a health score for averaging.

        Args:
            score: Health score value (0.0 to 1.0).
        """
        clamped = max(0.0, min(1.0, score))
        self._health_scores.append(clamped)
        log.debug("energy.metrics.health_score", score=clamped)

    def increment_quality_count(self, delta: int = 1) -> None:
        """Increment the quality assessment count.

        Args:
            delta: Amount to increment by.
        """
        self._quality_count += max(0, delta)

    def increment_compliance_count(self, delta: int = 1) -> None:
        """Increment the compliance check count.

        Args:
            delta: Amount to increment by.
        """
        self._compliance_count += max(0, delta)

    def increment_diagnostics_count(self, delta: int = 1) -> None:
        """Increment the diagnostics collection count.

        Args:
            delta: Amount to increment by.
        """
        self._diagnostics_count += max(0, delta)

    def increment_pipeline_version_count(self, delta: int = 1) -> None:
        """Increment the pipeline version count.

        Args:
            delta: Amount to increment by.
        """
        self._pipeline_version_count += max(0, delta)

    def increment_audit_count(self, delta: int = 1) -> None:
        """Increment the audit package count.

        Args:
            delta: Amount to increment by.
        """
        self._audit_count += max(0, delta)

    def increment_export_count(self, delta: int = 1) -> None:
        """Increment the export profile count.

        Args:
            delta: Amount to increment by.
        """
        self._export_count += max(0, delta)

    def get_asset_count(self) -> int:
        """Get the total asset count."""
        return self._asset_count

    def get_sensor_count(self) -> int:
        """Get the total sensor count."""
        return self._sensor_count

    def get_alarm_count(self) -> int:
        """Get the total alarm count."""
        return self._alarm_count

    def get_incident_count(self) -> int:
        """Get the total incident count."""
        return self._incident_count

    def get_maintenance_count(self) -> int:
        """Get the total maintenance count."""
        return self._maintenance_count

    def get_average_health_score(self) -> float:
        """Get the average health score.

        Returns:
            Average health score, or 0.0 if no scores recorded.
        """
        if not self._health_scores:
            return 0.0
        return round(sum(self._health_scores) / len(self._health_scores), 4)

    def get_quality_count(self) -> int:
        """Get the total quality assessment count."""
        return self._quality_count

    def get_compliance_count(self) -> int:
        """Get the total compliance check count."""
        return self._compliance_count

    def get_diagnostics_count(self) -> int:
        """Get the total diagnostics collection count."""
        return self._diagnostics_count

    def get_pipeline_version_count(self) -> int:
        """Get the total pipeline version count."""
        return self._pipeline_version_count

    def get_audit_count(self) -> int:
        """Get the total audit package count."""
        return self._audit_count

    def get_export_count(self) -> int:
        """Get the total export profile count."""
        return self._export_count

    def snapshot(self) -> DomainMetricsSnapshot:
        """Take a metrics snapshot.

        Returns:
            A DomainMetricsSnapshot with current values.
        """
        snapshot = DomainMetricsSnapshot(
            asset_count=self._asset_count,
            sensor_count=self._sensor_count,
            alarm_count=self._alarm_count,
            incident_count=self._incident_count,
            maintenance_count=self._maintenance_count,
            average_health_score=self.get_average_health_score(),
        )
        log.info(
            "energy.metrics.snapshot",
            assets=snapshot.asset_count,
            sensors=snapshot.sensor_count,
            alarms=snapshot.alarm_count,
            incidents=snapshot.incident_count,
            maintenance=snapshot.maintenance_count,
            avg_health=snapshot.average_health_score,
        )
        return snapshot

    def reset(self) -> None:
        """Reset all metrics counters."""
        self._asset_count = 0
        self._sensor_count = 0
        self._alarm_count = 0
        self._incident_count = 0
        self._maintenance_count = 0
        self._quality_count = 0
        self._compliance_count = 0
        self._diagnostics_count = 0
        self._pipeline_version_count = 0
        self._audit_count = 0
        self._export_count = 0
        self._health_scores.clear()
        log.info("energy.metrics.reset")
