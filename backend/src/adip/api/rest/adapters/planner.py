"""Planner service adapter."""

from __future__ import annotations

from typing import Any

from adip.api.rest.adapters.base import BaseServiceAdapter


class PlannerAdapter(BaseServiceAdapter):
    """Adapter for the Planner domain service."""

    def get_domain(self) -> str:
        return "planner"

    def create_plan(self, params: dict[str, Any] | None = None) -> Any:
        return self._success_response(data={"plan_id": "plan-001", "status": "created", "params": params or {}})

    def get_plan(self, plan_id: str) -> Any:
        return self._success_response(data={"plan_id": plan_id, "status": "active", "steps": []})

    def list_plans(self) -> Any:
        return self._success_response(data={"plans": [], "total": 0})

    def update_plan(self, plan_id: str, params: dict[str, Any] | None = None) -> Any:
        return self._success_response(data={"plan_id": plan_id, "status": "updated", "params": params or {}})

    def delete_plan(self, plan_id: str) -> Any:
        return self._success_response(data={"plan_id": plan_id, "status": "deleted"})
