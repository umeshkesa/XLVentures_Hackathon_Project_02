"""AssetContextManager — manages asset context for energy operations.

Collects and provides contextual information about energy assets
to inform domain decisions. Deterministic placeholder.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import structlog

log = structlog.get_logger(__name__)


class AssetContextManager:
    """Collects and manages asset context for energy operations.

    Gathers sensor readings, health status, maintenance history,
    alarm state, topology, and operational context for a given asset.
    Deterministic placeholder implementation.
    """

    def __init__(self) -> None:
        self._contexts: dict[str, dict[str, Any]] = {}

    def collect_context(
        self,
        asset_id: str,
        include_readings: bool = True,
        include_health: bool = True,
        include_maintenance: bool = True,
        include_alarms: bool = True,
        include_topology: bool = True,
        correlation_id: str = "",
    ) -> dict[str, Any]:
        """Collect full context for an asset.

        Args:
            asset_id: The asset identifier.
            include_readings: Whether to include sensor readings.
            include_health: Whether to include health status.
            include_maintenance: Whether to include maintenance history.
            include_alarms: Whether to include active alarms.
            include_topology: Whether to include topology information.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            Dict with context data for the asset.
        """
        context: dict[str, Any] = {
            "asset_id": asset_id,
            "timestamp": datetime.now(UTC).isoformat(),
            "sensor_readings": [],
            "health_status": {},
            "maintenance_history": [],
            "active_alarms": [],
            "topology": {},
        }

        if include_readings:
            context["sensor_readings"] = [
                {"sensor_id": "sensor-001", "type": "temperature", "value": 45.2, "unit": "°C"},
                {"sensor_id": "sensor-002", "type": "vibration", "value": 2.1, "unit": "mm/s"},
            ]

        if include_health:
            context["health_status"] = {
                "overall_score": 0.85,
                "state": "NORMAL",
                "last_assessment": datetime.now(UTC).isoformat(),
            }

        if include_maintenance:
            context["maintenance_history"] = [
                {"type": "PREVENTIVE", "date": "2026-01-15", "technician": "tech-001"},
                {"type": "PREDICTIVE", "date": "2026-03-20", "technician": "tech-002"},
            ]

        if include_alarms:
            context["active_alarms"] = [
                {"alarm_id": "alarm-001", "severity": "WARNING", "description": "Temperature above threshold"},
            ]

        if include_topology:
            context["topology"] = {
                "upstream": ["asset-002"],
                "downstream": ["asset-003", "asset-004"],
                "level": 2,
            }

        self._contexts[asset_id] = context
        log.info(
            "context.collected",
            asset_id=asset_id,
            correlation_id=correlation_id,
        )
        return context

    def get_cached_context(self, asset_id: str) -> dict[str, Any] | None:
        """Get cached context for an asset.

        Args:
            asset_id: The asset identifier.

        Returns:
            Cached context dict if available, None otherwise.
        """
        return self._contexts.get(asset_id)

    def get_context_summary(self, asset_id: str) -> str:
        """Get a human-readable summary of asset context.

        Args:
            asset_id: The asset identifier.

        Returns:
            Summary string describing the asset context.
        """
        context = self._contexts.get(asset_id, {})
        health = context.get("health_status", {})
        alarms = context.get("active_alarms", [])
        readings = context.get("sensor_readings", [])

        parts = [
            f"Asset {asset_id}",
            f"health: {health.get('state', 'UNKNOWN')} ({health.get('overall_score', 0.0):.2f})",
            f"sensors: {len(readings)} readings",
            f"alarms: {len(alarms)} active",
        ]
        return " | ".join(parts)

    def clear(self) -> None:
        """Clear all cached contexts."""
        self._contexts.clear()
        log.info("context.cleared")
