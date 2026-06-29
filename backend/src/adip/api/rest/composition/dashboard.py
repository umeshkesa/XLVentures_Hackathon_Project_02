"""Dashboard composition — aggregates platform-wide overview data."""

from __future__ import annotations

from typing import Any

from adip.api.rest.composition.base import BaseCompositionService


class DashboardComposition(BaseCompositionService):
    """Aggregates data for the platform dashboard."""

    def get_name(self) -> str:
        return "dashboard"

    def get_overview(self) -> dict[str, Any]:
        return {
            "active_workflows": 0,
            "pending_reviews": 0,
            "active_rules": 0,
            "active_plugins": 0,
            "recent_decisions": [],
            "system_health": "healthy",
            "energy_assets": 0,
            "alerts": [],
        }
