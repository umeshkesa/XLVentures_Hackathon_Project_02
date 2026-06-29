"""Workflow Overview composition — aggregates workflow data."""

from __future__ import annotations

from typing import Any

from adip.api.rest.composition.base import BaseCompositionService


class WorkflowOverviewComposition(BaseCompositionService):
    """Aggregates workflow and planner data."""

    def get_name(self) -> str:
        return "workflow_overview"

    def get_overview(self) -> dict[str, Any]:
        return {
            "active_workflows": 0,
            "completed_workflows": 0,
            "failed_workflows": 0,
            "pending_plans": 0,
            "average_execution_time_ms": 0.0,
            "recent_workflows": [],
            "workflow_success_rate": 1.0,
        }
