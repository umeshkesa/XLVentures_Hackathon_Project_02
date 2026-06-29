"""Knowledge API router — knowledge management endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from adip.api.rest.adapters.knowledge import KnowledgeAdapter

router = APIRouter(prefix="/knowledge", tags=["Knowledge"])
adapter = KnowledgeAdapter()


@router.post("/ingest")
async def ingest(body: dict[str, Any] | None = None) -> Any:
    return adapter.ingest(body or {})


@router.get("/query")
async def query(
    q: str = "",
    category: str | None = None,
    status: str | None = None,
    page: int = 1,
    limit: int = 12,
) -> Any:
    return adapter.query(q, category, status, page, limit)


@router.get("/documents/{document_id}")
async def get_document(document_id: str) -> Any:
    return adapter.get_document(document_id)


@router.delete("/documents/{document_id}")
async def delete_document(document_id: str) -> Any:
    return adapter.delete_document(document_id)
