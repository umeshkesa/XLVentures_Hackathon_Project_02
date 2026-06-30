"""Real LLM client — uses Gemini via google.genai SDK."""

from __future__ import annotations

import google.genai as genai
from adip.config import get_settings


_client: genai.Client | None = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        cfg = get_settings().llm
        _client = genai.Client(api_key=cfg.api_key.get_secret_value())
    return _client


def chat(
    message: str,
    system_prompt: str | None = None,
    model: str | None = None,
    temperature: float | None = None,
    max_tokens: int | None = None,
) -> str:
    cfg = get_settings().llm
    client = _get_client()

    content: str
    if system_prompt:
        content = f"{system_prompt}\n\n{message}"
    else:
        content = message

    resp = client.models.generate_content(
        model=model or cfg.model,
        contents=content,
        config=genai.types.GenerateContentConfig(
            temperature=temperature if temperature is not None else cfg.temperature,
            max_output_tokens=max_tokens or cfg.max_tokens,
        ),
    )
    return resp.text
