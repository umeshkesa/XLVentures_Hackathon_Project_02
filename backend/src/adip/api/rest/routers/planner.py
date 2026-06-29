"""Planner API router — planning and goal management endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends

from adip.api.rest.adapters.planner import PlannerAdapter
from adip.api.rest.dependencies import get_pagination_params
from adip.api.rest.models.pagination import PaginationParams

router = APIRouter(prefix="/planner", tags=["Planner"])
adapter = PlannerAdapter()


@router.get("/plans")
async def list_plans(params: PaginationParams = Depends(get_pagination_params)) -> Any:
    return adapter.list_plans()


@router.post("/plans")
async def create_plan(body: dict[str, Any] | None = None) -> Any:
    return adapter.create_plan(body or {})


@router.get("/plans/{plan_id}")
async def get_plan(plan_id: str) -> Any:
    return adapter.get_plan(plan_id)


@router.put("/plans/{plan_id}")
async def update_plan(plan_id: str, body: dict[str, Any] | None = None) -> Any:
    return adapter.update_plan(plan_id, body or {})


@router.delete("/plans/{plan_id}")
async def delete_plan(plan_id: str) -> Any:
    return adapter.delete_plan(plan_id)
