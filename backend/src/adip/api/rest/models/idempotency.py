"""Idempotency models for the REST API Layer."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

from adip.api.rest.enums import IdempotencyStatus


class IdempotencyKey(BaseModel):
    key: str = Field(description="Idempotency key value")
    header_name: str = Field(default="Idempotency-Key", description="HTTP header name")


class IdempotencyRecord(BaseModel):
    key: str = Field(description="The idempotency key")
    status: IdempotencyStatus = Field(default=IdempotencyStatus.IN_FLIGHT)
    response_status: int | None = Field(default=None)
    response_body: dict[str, Any] | None = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    expires_at: datetime | None = Field(default=None)
