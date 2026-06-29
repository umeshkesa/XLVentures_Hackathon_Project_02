"""Foundation request / response models for the REST API Layer."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Generic, TypeVar
from uuid import uuid4

from pydantic import BaseModel, Field

from adip.api.rest.enums import ApiVersion

T = TypeVar("T")
DataT = TypeVar("DataT")


class ApiVersionInfo(BaseModel):
    version: str = Field(default="1.0.0", description="API version string")
    api_version: ApiVersion = Field(default=ApiVersion.V1, description="API version identifier")


class ApiMetadata(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    version: ApiVersionInfo = Field(default_factory=ApiVersionInfo)
    trace_id: str = Field(default_factory=lambda: str(uuid4()))
    processing_time_ms: float | None = Field(default=None)


class ErrorDetail(BaseModel):
    code: str = Field(description="Machine-readable error code")
    message: str = Field(description="Human-readable error description")
    field: str | None = Field(default=None, description="Field that caused the error")
    details: dict[str, Any] | None = Field(default=None)


class ApiError(BaseModel):
    code: str = Field(description="Machine-readable error code")
    message: str = Field(description="Human-readable error description")
    details: dict[str, Any] | None = Field(default=None)
    errors: list[ErrorDetail] | None = Field(default=None)


class ApiRequest(BaseModel, Generic[T]):
    data: T | None = Field(default=None, description="Request payload")
    idempotency_key: str | None = Field(default=None, description="Idempotency key for safe retries")
    metadata: dict[str, Any] | None = Field(default=None)


class ApiResponse(BaseModel, Generic[DataT]):
    success: bool = Field(default=True, description="Indicates if the request succeeded")
    data: DataT | None = Field(default=None, description="Response payload")
    metadata: ApiMetadata = Field(default_factory=ApiMetadata)
    errors: list[ApiError] | None = Field(default=None)
    trace_id: str | None = Field(default=None)
    timestamp: datetime | None = Field(default=None)

    def model_post_init(self, _context: Any) -> None:
        if self.trace_id is None:
            self.trace_id = self.metadata.trace_id
        if self.timestamp is None:
            self.timestamp = self.metadata.timestamp


class ResponseWrapper(BaseModel, Generic[DataT]):
    success: bool = Field(default=True)
    data: DataT | None = Field(default=None)
    metadata: ApiMetadata = Field(default_factory=ApiMetadata)
    errors: list[ApiError] | None = Field(default=None)
    trace_id: str | None = Field(default=None)
    timestamp: datetime | None = Field(default=None)
