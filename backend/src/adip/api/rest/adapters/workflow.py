"""Workflow service adapter."""

from __future__ import annotations

from typing import Any

from adip.api.rest.adapters.base import BaseServiceAdapter


class WorkflowAdapter(BaseServiceAdapter):
    def get_domain(self) -> str:
        return "workflow"

    def create_workflow(self, params: dict[str, Any] | None = None) -> Any:
        return self._success_response(data={"workflow_id": "wf-001", "status": "created", "params": params or {}})

    def get_workflow(self, workflow_id: str) -> Any:
        return self._success_response(data={"workflow_id": workflow_id, "status": "active", "steps": []})

    def list_workflows(self) -> Any:
        return self._success_response(data={"workflows": [], "total": 0})

    def execute_workflow(self, workflow_id: str, params: dict[str, Any] | None = None) -> Any:
        return self._success_response(data={"workflow_id": workflow_id, "execution_id": "exec-001", "status": "started", "params": params or {}})
