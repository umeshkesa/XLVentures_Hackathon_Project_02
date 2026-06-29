"""REST API Layer — Architecture, Contracts & API Foundation.

This module implements Phase 1 of the ADIP REST API Layer providing:

- API contracts (request/response models, error models)
- Versioned routers for all 16 platform domains
- Middleware (correlation IDs, request logging, exception handling, metrics)
- OpenAPI / Swagger / Redoc configuration
- Pagination, filtering, and sorting support
- Idempotency key support
- Async operation model
- Rate limiting interfaces (contracts only, no implementation)

The API layer contains NO business logic. Business logic must remain
inside domain services.
"""

from __future__ import annotations

from adip.api.rest.middleware.registration import register_middleware
from adip.api.rest.models import (
    ApiError,
    ApiMetadata,
    ApiRequest,
    ApiResponse,
    ApiVersionInfo,
    ErrorDetail,
    FilterCriteria,
    FilterGroup,
    FilterParams,
    HealthResponse,
    IdempotencyKey,
    IdempotencyRecord,
    LiveResponse,
    OperationRequest,
    OperationResult,
    OperationStatusResponse,
    PaginatedResponse,
    PaginationParams,
    PaginationResult,
    RateLimitConfig,
    RateLimitHeaders,
    RateLimitPolicy,
    ReadyResponse,
    SortCriteria,
    SortParams,
    VersionResponse,
)
from adip.api.rest.openapi import configure_openapi
from adip.api.rest.versioning import API_V1_PREFIX, API_V2_PREFIX, create_versioned_router

__all__ = [
    "register_middleware",
    "configure_openapi",
    "API_V1_PREFIX",
    "API_V2_PREFIX",
    "create_versioned_router",
    "ApiRequest",
    "ApiResponse",
    "ApiMetadata",
    "ApiError",
    "ApiVersionInfo",
    "ErrorDetail",
    "PaginatedResponse",
    "PaginationParams",
    "PaginationResult",
    "FilterCriteria",
    "FilterGroup",
    "FilterParams",
    "SortCriteria",
    "SortParams",
    "HealthResponse",
    "LiveResponse",
    "ReadyResponse",
    "VersionResponse",
    "OperationRequest",
    "OperationResult",
    "OperationStatusResponse",
    "IdempotencyKey",
    "IdempotencyRecord",
    "RateLimitConfig",
    "RateLimitHeaders",
    "RateLimitPolicy",
]
