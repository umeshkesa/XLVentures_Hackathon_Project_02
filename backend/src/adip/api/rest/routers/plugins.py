"""Plugins API router — plugin lifecycle management endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends

from adip.api.rest.adapters.plugins import PluginsAdapter
from adip.api.rest.dependencies import get_pagination_params
from adip.api.rest.models.pagination import PaginationParams

router = APIRouter(prefix="/plugins", tags=["Plugins"])
adapter = PluginsAdapter()


@router.post("/install/{plugin_id}")
async def install_plugin(plugin_id: str, body: dict[str, Any] | None = None) -> Any:
    return adapter.install(plugin_id, body or {})


@router.post("/uninstall/{plugin_id}")
async def uninstall_plugin(plugin_id: str) -> Any:
    return adapter.uninstall(plugin_id)


@router.get("/{plugin_id}")
async def get_plugin(plugin_id: str) -> Any:
    return adapter.get_plugin(plugin_id)


@router.get("")
async def list_plugins(params: PaginationParams = Depends(get_pagination_params)) -> Any:
    return adapter.list_plugins()
