"""Response Transformer — wraps service responses into ApiResponse format."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

import structlog

from adip.api.rest.enums import ErrorType
from adip.api.rest.models.base import (
    ApiError,
    ApiMetadata,
    ApiResponse,
    ApiVersionInfo,
)

logger = structlog.get_logger(__name__)


class ResponseTransformer:
    """Transforms raw service responses into standardised ApiResponse objects."""

    def __init__(self, api_version: str = "v1") -> None:
        self._api_version = api_version

    def success(self, data: Any = None, processing_time_ms: float | None = None) -> ApiResponse:
        trace_id = str(uuid4())
        metadata = ApiMetadata(
            timestamp=datetime.now(UTC),
            version=ApiVersionInfo(version="1.0.0", api_version=self._api_version),
            trace_id=trace_id,
            processing_time_ms=processing_time_ms,
        )
        return ApiResponse(
            success=True,
            data=data,
            metadata=metadata,
            trace_id=trace_id,
            timestamp=metadata.timestamp,
        )

    def error(
        self,
        error_type: ErrorType = ErrorType.PLATFORM_ERROR,
        message: str = "An error occurred.",
        details: dict[str, Any] | None = None,
        status_code: int = 500,
        processing_time_ms: float | None = None,
    ) -> ApiResponse:
        trace_id = str(uuid4())
        metadata = ApiMetadata(
            timestamp=datetime.now(UTC),
            version=ApiVersionInfo(version="1.0.0", api_version=self._api_version),
            trace_id=trace_id,
            processing_time_ms=processing_time_ms,
        )
        errors = [ApiError(code=error_type.value, message=message, details=details)]
        return ApiResponse(
            success=False,
            data=None,
            metadata=metadata,
            errors=errors,
            trace_id=trace_id,
            timestamp=metadata.timestamp,
        )

    def from_service_response(self, service_response: Any, processing_time_ms: float | None = None) -> ApiResponse:
        if isinstance(service_response, ApiResponse):
            return service_response
        if isinstance(service_response, dict):
            if service_response.get("success") is False:
                return self.error(
                    error_type=ErrorType(service_response.get("code", ErrorType.PLATFORM_ERROR.value)),
                    message=service_response.get("message", "Service error"),
                    details=service_response.get("details"),
                )
            return self.success(data=service_response.get("data", service_response), processing_time_ms=processing_time_ms)
        return self.success(data=service_response, processing_time_ms=processing_time_ms)

    def paginated(
        self,
        items: list[Any],
        total: int,
        limit: int = 100,
        offset: int = 0,
    ) -> ApiResponse:
        return self.success(
            data={
                "items": items,
                "pagination": {
                    "limit": limit,
                    "offset": offset,
                    "total": total,
                },
            }
        )
