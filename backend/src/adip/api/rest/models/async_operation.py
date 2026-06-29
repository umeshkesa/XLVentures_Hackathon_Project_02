"""Async operation models for the REST API Layer."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from adip.api.rest.enums import OperationStatus


class OperationRequest(BaseModel):
    operation_type: str = Field(description="Type of operation to perform")
    params: dict[str, Any] = Field(default_factory=dict, description="Operation parameters")
    idempotency_key: str | None = Field(default=None)


class OperationStatusResponse(BaseModel):
    operation_id: UUID = Field(default_factory=uuid4)
    status: OperationStatus = Field(default=OperationStatus.PENDING)
    operation_type: str = Field(description="Type of operation")
    progress: float | None = Field(default=None, ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    started_at: datetime | None = Field(default=None)
    completed_at: datetime | None = Field(default=None)
    estimated_completion_at: datetime | None = Field(default=None)


class OperationResult(BaseModel):
    operation_id: UUID = Field(description="Unique operation identifier")
    status: OperationStatus = Field(default=OperationStatus.COMPLETED)
    result: Any = Field(default=None, description="Operation result data")
    error: str | None = Field(default=None, description="Error message if operation failed")
    started_at: datetime | None = Field(default=None)
    completed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
