"""Action Engine API router — action execution endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends

from adip.api.rest.adapters.action_engine import ActionEngineAdapter
from adip.api.rest.dependencies import get_pagination_params
from adip.api.rest.models.pagination import PaginationParams

router = APIRouter(prefix="/action-engine", tags=["Action Engine"])
adapter = ActionEngineAdapter()


@router.post("/execute")
async def execute(body: dict[str, Any] | None = None) -> Any:
    action_id = (body or {}).get("action_id", "")
    params = (body or {}).get("params")
    return adapter.execute(action_id, params)


@router.get("/executions/{execution_id}")
async def get_execution(execution_id: str) -> Any:
    return adapter.get_execution(execution_id)


@router.get("/executions")
async def list_executions(params: PaginationParams = Depends(get_pagination_params)) -> Any:
    return adapter.list_executions()
