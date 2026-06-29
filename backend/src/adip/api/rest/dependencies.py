"""FastAPI dependencies for the REST API Layer."""

from __future__ import annotations

from fastapi import Header, Query

from adip.api.rest.models.filtering import FilterParams
from adip.api.rest.models.pagination import PaginationParams
from adip.api.rest.models.sorting import SortParams


async def get_pagination_params(
    limit: int = Query(default=100, ge=1, le=1000, description="Maximum items to return"),
    offset: int = Query(default=0, ge=0, description="Number of items to skip"),
    page: int | None = Query(default=None, ge=1, description="Page number"),
    page_size: int | None = Query(default=None, ge=1, le=1000, description="Items per page"),
) -> PaginationParams:
    return PaginationParams(limit=limit, offset=offset, page=page, page_size=page_size)


async def get_filter_params(
    filter_raw: str | None = Query(default=None, alias="filter", description="Filter expression"),
) -> FilterParams:
    return FilterParams(raw=filter_raw)


async def get_sort_params(
    sort_by: str | None = Query(default=None, alias="sort", description="Sort field"),
    sort_dir: str | None = Query(default=None, alias="sort_dir", description="Sort direction (asc/desc)"),
) -> SortParams:
    from adip.api.rest.enums import SortDirection

    sorts = []
    if sort_by:
        direction = SortDirection.DESC if sort_dir and sort_dir.lower() == "desc" else SortDirection.ASC
        from adip.api.rest.models.sorting import SortCriteria
        sorts.append(SortCriteria(field=sort_by, direction=direction))
    return SortParams(sorts=sorts)


async def get_idempotency_key(
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key", description="Idempotency key for safe retries"),
) -> str | None:
    return idempotency_key


async def get_correlation_id(
    x_correlation_id: str | None = Header(default=None, alias="X-Correlation-ID", description="Correlation ID for distributed tracing"),
) -> str | None:
    return x_correlation_id
