"""Reasoning API router — reasoning engine endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query

from adip.api.rest.adapters.reasoning import ReasoningAdapter
from adip.api.rest.dependencies import get_pagination_params
from adip.api.rest.models.pagination import PaginationParams

router = APIRouter(prefix="/reasoning", tags=["Reasoning"])
adapter = ReasoningAdapter()


@router.post("/reason")
async def reason(body: dict[str, Any] | None = None) -> Any:
    query = (body or {}).get("query", "")
    context = (body or {}).get("context")
    return adapter.reason(query, context)


@router.get("/{reasoning_id}")
async def get_reasoning(reasoning_id: str) -> Any:
    return adapter.get_reasoning(reasoning_id)


@router.get("")
async def list_reasonings(
    params: PaginationParams = Depends(get_pagination_params),
    status: str | None = Query(None),
    domain: str | None = Query(None),
    search: str = Query(""),
) -> Any:
    return adapter.list_reasonings(status=status, domain=domain, q=search, page=params.page, limit=params.limit)
