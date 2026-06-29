"""Energy Domain API router — energy domain operations endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends

from adip.api.rest.adapters.energy import EnergyAdapter
from adip.api.rest.dependencies import get_pagination_params
from adip.api.rest.models.pagination import PaginationParams

router = APIRouter(prefix="/energy", tags=["Energy"])
adapter = EnergyAdapter()


@router.get("/assets")
async def list_assets(params: PaginationParams = Depends(get_pagination_params)) -> Any:
    return adapter.list_assets()


@router.get("/assets/{asset_id}")
async def get_asset(asset_id: str) -> Any:
    return adapter.get_asset(asset_id)


@router.get("/assets/{asset_id}/readings")
async def get_readings(asset_id: str) -> Any:
    return adapter.get_readings(asset_id)


@router.get("/assets/{asset_id}/alerts")
async def get_alerts(asset_id: str) -> Any:
    return adapter.get_alerts(asset_id)


@router.post("/assets/{asset_id}/analyze")
async def analyze(asset_id: str, body: dict[str, Any] | None = None) -> Any:
    return adapter.analyze(asset_id, body or {})
