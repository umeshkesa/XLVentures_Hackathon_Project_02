"""Workflow API router — workflow orchestration endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends

from adip.api.rest.adapters.workflow import WorkflowAdapter
from adip.api.rest.dependencies import get_pagination_params
from adip.api.rest.models.pagination import PaginationParams

router = APIRouter(prefix="/workflow", tags=["Workflow"])
adapter = WorkflowAdapter()


@router.get("/workflows")
async def list_workflows(params: PaginationParams = Depends(get_pagination_params)) -> Any:
    return adapter.list_workflows()


@router.post("/workflows")
async def create_workflow(body: dict[str, Any] | None = None) -> Any:
    return adapter.create_workflow(body or {})


@router.get("/workflows/{workflow_id}")
async def get_workflow(workflow_id: str) -> Any:
    return adapter.get_workflow(workflow_id)


@router.post("/workflows/{workflow_id}/execute")
async def execute_workflow(workflow_id: str, body: dict[str, Any] | None = None) -> Any:
    return adapter.execute_workflow(workflow_id, body or {})
