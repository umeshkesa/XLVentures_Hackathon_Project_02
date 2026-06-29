"""Action Manager API router — execution planning and management endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Query

from adip.api.rest.adapters.action_manager import ActionManagerAdapter

router = APIRouter(prefix="/action-manager", tags=["Action Manager"])
adapter = ActionManagerAdapter()


@router.post("/actions")
async def create_action(body: dict[str, Any] | None = None) -> Any:
    action_type = (body or {}).get("action_type", "")
    params = (body or {}).get("params")
    return adapter.create_action(action_type, params)


@router.get("/actions/{action_id}")
async def get_action(action_id: str) -> Any:
    return adapter.get_action(action_id)


@router.get("/actions")
async def list_actions(
    status: str | None = Query(None),
    priority: str | None = Query(None),
    q: str | None = Query(None),
    page: int = Query(1),
    limit: int = Query(12),
) -> Any:
    return adapter.list_actions(status=status, priority=priority, q=q, page=page, limit=limit)


@router.post("/actions/{action_id}/cancel")
async def cancel_action(action_id: str) -> Any:
    return adapter.cancel_action(action_id)


@router.post("/actions/{action_id}/status")
async def update_status(action_id: str, body: dict[str, Any] | None = None) -> Any:
    status = (body or {}).get("status", "")
    return adapter.update_status(action_id, status)
