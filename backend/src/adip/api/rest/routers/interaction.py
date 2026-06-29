"""Interaction API router — customer interaction endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from adip.api.rest.adapters.interaction import InteractionAdapter

router = APIRouter(prefix="/interactions", tags=["Interactions"])
adapter = InteractionAdapter()


@router.get("")
async def list_interactions(
    type: str | None = None,
    status: str | None = None,
    search: str | None = None,
    customer_id: str | None = None,
    page: int = 1,
    limit: int = 12,
) -> Any:
    return adapter.list(type, status, search, customer_id, page, limit)


@router.get("/timeline")
async def timeline(
    customer_id: str | None = None,
    type: str | None = None,
) -> Any:
    return adapter.get_timeline(customer_id, type)


@router.get("/{interaction_id}")
async def get_interaction(interaction_id: str) -> Any:
    return adapter.get_by_id(interaction_id)
