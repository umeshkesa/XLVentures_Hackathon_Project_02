"""Evidence API router — evidence fusion and management endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from adip.api.rest.adapters.evidence import EvidenceAdapter

router = APIRouter(prefix="/evidence", tags=["Evidence"])
adapter = EvidenceAdapter()


@router.post("/collect")
async def collect(source: str, body: dict[str, Any] | None = None) -> Any:
    return adapter.collect(source, body or {})


@router.post("/fuse")
async def fuse(body: dict[str, Any] | None = None) -> Any:
    evidence_ids = (body or {}).get("evidence_ids", [])
    return adapter.fuse(evidence_ids)


@router.get("/query")
async def query(
    q: str = "",
    type: str | None = None,
    status: str | None = None,
    priority: str | None = None,
    page: int = 1,
    limit: int = 12,
    sort: str = "confidence",
) -> Any:
    return adapter.query(q, type, status, priority, page, limit, sort)


@router.get("/traceability")
async def traceability(evidenceId: str) -> Any:
    return adapter.get_traceability(evidenceId)


@router.get("/{evidence_id}")
async def get_evidence(evidence_id: str) -> Any:
    return adapter.get_evidence(evidence_id)
