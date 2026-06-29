"""Operations Overview composition — aggregates operational data."""

from __future__ import annotations

from typing import Any

from adip.api.rest.composition.base import BaseCompositionService


class OperationsOverviewComposition(BaseCompositionService):
    """Aggregates operational data: actions, executions, rules, decisions."""

    def get_name(self) -> str:
        return "operations_overview"

    def get_overview(self) -> dict[str, Any]:
        return {
            "pending_actions": 0,
            "running_executions": 0,
            "completed_executions": 0,
            "failed_executions": 0,
            "active_rules": 0,
            "pending_reviews": 0,
            "recent_decisions": [],
            "operation_success_rate": 1.0,
        }
