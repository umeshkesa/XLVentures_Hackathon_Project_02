"""LLM service adapter — real Gemini-powered AI assistant chat."""

from __future__ import annotations

from typing import Any

from adip.api.rest.adapters.base import BaseServiceAdapter
from adip.api.rest.models.base import ApiResponse
from adip.services.llm import chat as llm_chat


class LLMAdapter(BaseServiceAdapter):
    def get_domain(self) -> str:
        return "llm"

    def chat(self, message: str, conversation_id: str | None = None) -> ApiResponse:
        system_prompt = (
            "You are an AI assistant for the ADIP (Autonomous Decision Intelligence Platform) "
            "enterprise energy management system. You help energy engineers and operators "
            "understand platform data, recommendations, evidence, knowledge, rules, "
            "asset health, and platform status. Answer concisely using Markdown."
        )
        response = llm_chat(message, system_prompt=system_prompt)
        return self._success_response(data={
            "response": response,
            "conversation_id": conversation_id or f"conv-{hash(message) & 0xFFFFFFFF:08x}",
        })

    def get_suggested_questions(self) -> ApiResponse:
        questions = [
            {"id": "SQ-1", "text": "Why was recommendation R-001 generated?", "category": "recommendations"},
            {"id": "SQ-2", "text": "Summarize NovaGrid customer interactions", "category": "customers"},
            {"id": "SQ-3", "text": "Summarize uploaded knowledge documents", "category": "knowledge"},
            {"id": "SQ-4", "text": "Explain evidence EV-003", "category": "evidence"},
            {"id": "SQ-5", "text": "What business rules were triggered for TF-102?", "category": "rules"},
            {"id": "SQ-6", "text": "Explain asset health for WT-102", "category": "assets"},
            {"id": "SQ-7", "text": "Why is recommendation R-002 confidence 0.82?", "category": "recommendations"},
            {"id": "SQ-8", "text": "Compare recommendations R-001 and R-003", "category": "recommendations"},
            {"id": "SQ-9", "text": "Summarize imported datasets from last import", "category": "import"},
            {"id": "SQ-10", "text": "What is the overall platform health status?", "category": "platform"},
        ]
        return self._success_response(data={"questions": questions})
