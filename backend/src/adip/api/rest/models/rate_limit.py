"""Rate limiting models for the REST API Layer."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class RateLimitConfig(BaseModel):
    requests_per_second: int = Field(default=10, ge=1, description="Maximum requests per second")
    burst_size: int = Field(default=20, ge=1, description="Maximum burst size")
    enabled: bool = Field(default=True, description="Whether rate limiting is enabled")


class RateLimitHeaders(BaseModel):
    limit: int = Field(description="Rate limit ceiling")
    remaining: int = Field(description="Requests remaining in the current window")
    reset: int = Field(description="Unix timestamp when the rate limit resets")


class RateLimitPolicy(BaseModel):
    name: str = Field(description="Policy name")
    config: RateLimitConfig = Field(default_factory=RateLimitConfig)
    routes: list[str] = Field(default_factory=list, description="Route patterns this policy applies to")
    metadata: dict[str, Any] = Field(default_factory=dict)
