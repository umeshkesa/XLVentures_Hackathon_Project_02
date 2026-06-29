"""Recommendation API router — recommendation engine endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query

from adip.api.rest.adapters.recommendation import RecommendationAdapter
from adip.api.rest.dependencies import get_pagination_params
from adip.api.rest.models.pagination import PaginationParams

router = APIRouter(prefix="/recommendation", tags=["Recommendation"])
adapter = RecommendationAdapter()


@router.post("/recommend")
async def recommend(body: dict[str, Any] | None = None) -> Any:
    query = (body or {}).get("query", "")
    params = (body or {}).get("params")
    return adapter.recommend(query, params)


@router.get("/{recommendation_id}")
async def get_recommendation(recommendation_id: str) -> Any:
    return adapter.get_recommendation(recommendation_id)


@router.get("")
async def list_recommendations(
    params: PaginationParams = Depends(get_pagination_params),
    status: str | None = Query(None),
    priority: str | None = Query(None),
    source: str | None = Query(None),
    search: str = Query(""),
) -> Any:
    return adapter.list_recommendations(status=status, priority=priority, source=source, q=search, page=params.page, limit=params.limit)
