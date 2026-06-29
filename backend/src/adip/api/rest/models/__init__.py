"""REST API Layer models."""

from __future__ import annotations

from adip.api.rest.models.async_operation import (
    OperationRequest,
    OperationResult,
    OperationStatusResponse,
)
from adip.api.rest.models.base import (
    ApiError,
    ApiMetadata,
    ApiRequest,
    ApiResponse,
    ApiVersionInfo,
    ErrorDetail,
    ResponseWrapper,
)
from adip.api.rest.models.errors import (
    AuthenticationError,
    AuthorizationError,
    BusinessError,
    IntegrationError,
    PlatformError,
    ValidationError,
)
from adip.api.rest.models.filtering import FilterCriteria, FilterGroup, FilterParams
from adip.api.rest.models.health import HealthResponse, LiveResponse, ReadyResponse, VersionResponse
from adip.api.rest.models.idempotency import IdempotencyKey, IdempotencyRecord
from adip.api.rest.models.pagination import (
    PaginatedResponse,
    PaginationParams,
    PaginationResult,
)
from adip.api.rest.models.rate_limit import RateLimitConfig, RateLimitHeaders, RateLimitPolicy
from adip.api.rest.models.sorting import SortCriteria, SortParams

__all__ = [
    "ApiRequest",
    "ApiResponse",
    "ApiMetadata",
    "ApiError",
    "ApiVersionInfo",
    "ErrorDetail",
    "ResponseWrapper",
    "PaginatedResponse",
    "PaginationParams",
    "PaginationResult",
    "FilterCriteria",
    "FilterGroup",
    "FilterParams",
    "SortCriteria",
    "SortParams",
    "ValidationError",
    "AuthenticationError",
    "AuthorizationError",
    "BusinessError",
    "PlatformError",
    "IntegrationError",
    "HealthResponse",
    "LiveResponse",
    "ReadyResponse",
    "VersionResponse",
    "IdempotencyKey",
    "IdempotencyRecord",
    "OperationRequest",
    "OperationResult",
    "OperationStatusResponse",
    "RateLimitConfig",
    "RateLimitHeaders",
    "RateLimitPolicy",
]
