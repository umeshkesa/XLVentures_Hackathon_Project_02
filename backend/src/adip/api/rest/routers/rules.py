"""Rules API router — rule management and evaluation endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends

from adip.api.rest.adapters.rules import RulesAdapter
from adip.api.rest.dependencies import get_pagination_params
from adip.api.rest.models.pagination import PaginationParams

router = APIRouter(prefix="/rules", tags=["Rules"])
adapter = RulesAdapter()


@router.post("/evaluate/{rule_id}")
async def evaluate_rule(rule_id: str, body: dict[str, Any] | None = None) -> Any:
    return adapter.evaluate(rule_id, body or {})


@router.post("/rules")
async def create_rule(body: dict[str, Any] | None = None) -> Any:
    return adapter.create_rule(body or {})


@router.get("/rules/{rule_id}")
async def get_rule(rule_id: str) -> Any:
    return adapter.get_rule(rule_id)


@router.get("/rules-list")
async def list_rules(params: PaginationParams = Depends(get_pagination_params)) -> Any:
    return adapter.list_rules()


@router.delete("/rules/{rule_id}")
async def delete_rule(rule_id: str) -> Any:
    return adapter.delete_rule(rule_id)
