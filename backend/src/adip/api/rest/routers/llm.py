"""LLM API router — AI assistant chat endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from adip.api.rest.adapters.llm import LLMAdapter

router = APIRouter(prefix="/llm", tags=["AI Assistant"])
adapter = LLMAdapter()


@router.post("/chat")
async def chat(body: dict[str, Any]) -> Any:
    message = (body or {}).get("message", "")
    conversation_id = (body or {}).get("conversation_id")
    return adapter.chat(message, conversation_id)


@router.get("/suggestions")
async def get_suggestions() -> Any:
    return adapter.get_suggested_questions()
