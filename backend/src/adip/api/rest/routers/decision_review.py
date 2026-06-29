"""Decision Review API router — HITL review layer endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query

from adip.api.rest.adapters.decision_review import DecisionReviewAdapter
from adip.api.rest.dependencies import get_pagination_params
from adip.api.rest.models.pagination import PaginationParams

router = APIRouter(prefix="/decision-review", tags=["Decision Review"])
adapter = DecisionReviewAdapter()


@router.post("/reviews")
async def create_review(body: dict[str, Any] | None = None) -> Any:
    decision_id = (body or {}).get("decision_id", "")
    params = (body or {}).get("params")
    return adapter.create_review(decision_id, params)


@router.get("/reviews/{review_id}")
async def get_review(review_id: str) -> Any:
    return adapter.get_review(review_id)


@router.post("/reviews/{review_id}/approve")
async def approve_review(review_id: str, body: dict[str, Any] | None = None) -> Any:
    comment = (body or {}).get("comment", "")
    return adapter.approve(review_id, comment)


@router.post("/reviews/{review_id}/reject")
async def reject_review(review_id: str, body: dict[str, Any] | None = None) -> Any:
    reason = (body or {}).get("reason", "")
    return adapter.reject(review_id, reason)


@router.post("/reviews/{review_id}/request-info")
async def request_info(review_id: str, body: dict[str, Any] | None = None) -> Any:
    question = (body or {}).get("question", "")
    return adapter.request_info(review_id, question)


@router.post("/reviews/{review_id}/comments")
async def add_comment(review_id: str, body: dict[str, Any] | None = None) -> Any:
    text = (body or {}).get("text", "")
    author = (body or {}).get("author", "reviewer")
    return adapter.add_comment(review_id, text, author)


@router.post("/reviews/{review_id}/assign")
async def assign_engineer(review_id: str, body: dict[str, Any] | None = None) -> Any:
    engineer = (body or {}).get("engineer", "")
    return adapter.assign_engineer(review_id, engineer)


@router.post("/reviews/{review_id}/schedule")
async def schedule_action(review_id: str, body: dict[str, Any] | None = None) -> Any:
    scheduled_date = (body or {}).get("scheduled_date", "")
    notes = (body or {}).get("notes", "")
    return adapter.schedule_action(review_id, scheduled_date, notes)


@router.get("/reviews")
async def list_reviews(
    status: str | None = Query(None),
    priority: str | None = Query(None),
    q: str | None = Query(None),
    page: int = Query(1),
    limit: int = Query(12),
) -> Any:
    return adapter.list_reviews(status=status, priority=priority, q=q, page=page, limit=limit)
