"""Registry API router — service and component registry endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from adip.api.rest.adapters.registry_adapter import RegistryAdapter

router = APIRouter(prefix="/registry", tags=["Registry"])
adapter = RegistryAdapter()


@router.post("/entries")
async def register(body: dict[str, Any] | None = None) -> Any:
    return adapter.register(body or {})


@router.delete("/entries/{registry_id}")
async def unregister(registry_id: str) -> Any:
    return adapter.unregister(registry_id)


@router.get("/entries/{registry_id}")
async def get_entry(registry_id: str) -> Any:
    return adapter.get_entry(registry_id)


@router.get("/search")
async def search(q: str = "") -> Any:
    return adapter.search(q)
