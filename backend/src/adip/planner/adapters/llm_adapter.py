"""Abstract interfaces for LLM provider adapters.

Concrete implementations for Claude, OpenAI, Gemini are created by
subclassing ``LLMAdapter`` and registering via ``LLMAdapterFactory``.
"""

from __future__ import annotations

import abc
from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass
class LLMResponse:
    """Structured response from an LLM call."""
    content: str
    model: str = ""
    usage: dict[str, Any] = field(default_factory=dict)
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class LLMMessage:
    """A single message in a conversation with an LLM."""
    role: str  # "system", "user", "assistant"
    content: str


class LLMAdapter(abc.ABC):
    """Abstract adapter for LLM provider integration."""

    @abc.abstractmethod
    async def generate(
        self,
        messages: list[LLMMessage],
        *,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs: Any,
    ) -> LLMResponse:
        """Send messages to the LLM and return a response."""
        pass

    @abc.abstractmethod
    async def generate_structured(
        self,
        messages: list[LLMMessage],
        response_model: type,
        *,
        temperature: float = 0.3,
        **kwargs: Any,
    ) -> Any:
        """Send messages and receive a structured (typed) response."""
        pass


class LLMAdapterFactory(Protocol):
    """Factory protocol for creating LLM adapters by provider name."""

    def __call__(self, provider: str, **config: Any) -> LLMAdapter:
        """Create an LLM adapter for *provider* with *config*.

        Supported provider values: "claude", "openai", "gemini".
        """
        ...
