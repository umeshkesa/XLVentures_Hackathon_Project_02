"""Energy Overview composition — aggregates energy domain data."""

from __future__ import annotations

from typing import Any

from adip.api.rest.composition.base import BaseCompositionService


class EnergyOverviewComposition(BaseCompositionService):
    """Aggregates energy domain data: assets, readings, alerts."""

    def get_name(self) -> str:
        return "energy_overview"

    def get_overview(self) -> dict[str, Any]:
        return {
            "total_assets": 0,
            "active_assets": 0,
            "alerts_count": 0,
            "average_health_score": 0.0,
            "average_efficiency": 0.0,
            "recent_readings": [],
            "topology_status": "healthy",
        }
