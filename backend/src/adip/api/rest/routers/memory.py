"""Memory API router — memory management endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from adip.api.rest.adapters.memory import MemoryAdapter

router = APIRouter(prefix="/memory", tags=["Memory"])
adapter = MemoryAdapter()


@router.post("/store/{key}")
async def store(key: str, body: dict[str, Any] | None = None) -> Any:
    return adapter.store(key, body)


@router.get("/retrieve/{key}")
async def retrieve(key: str) -> Any:
    return adapter.retrieve(key)


@router.get("/search")
async def search(query: str) -> Any:
    return adapter.search(query)


@router.delete("/{key}")
async def delete(key: str) -> Any:
    return adapter.delete(key)
