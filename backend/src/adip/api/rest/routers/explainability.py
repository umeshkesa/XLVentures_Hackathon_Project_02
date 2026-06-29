"""Explainability API router — explainability engine endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends

from adip.api.rest.adapters.explainability import ExplainabilityAdapter
from adip.api.rest.dependencies import get_pagination_params
from adip.api.rest.models.pagination import PaginationParams

router = APIRouter(prefix="/explainability", tags=["Explainability"])
adapter = ExplainabilityAdapter()


@router.post("/explain")
async def explain(body: dict[str, Any] | None = None) -> Any:
    decision_id = (body or {}).get("decision_id", "")
    params = (body or {}).get("params")
    return adapter.explain(decision_id, params)


@router.get("/{explanation_id}")
async def get_explanation(explanation_id: str) -> Any:
    return adapter.get_explanation(explanation_id)


@router.get("")
async def list_explanations(params: PaginationParams = Depends(get_pagination_params)) -> Any:
    return adapter.list_explanations(page=params.page, limit=params.limit)
