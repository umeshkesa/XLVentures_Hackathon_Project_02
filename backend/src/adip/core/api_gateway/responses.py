"""Reusable Pydantic v2 response models for all ADIP API endpoints.

Every endpoint should return one of these three wrappers to guarantee
a consistent on-the-wire shape for clients.

Usage::

    from adip.core.api_gateway.responses import SuccessResponse, PaginatedResponse

    @router.get("/users/{user_id}")
    async def get_user(user_id: str) -> SuccessResponse[UserOut]:
        user = await fetch_user(user_id)
        return SuccessResponse(data=UserOut.model_validate(user))

    @router.get("/users")
    async def list_users(page: int = 1) -> PaginatedResponse[UserOut]:
        items, total = await fetch_users(page=page)
        return PaginatedResponse(
            data=[UserOut.model_validate(u) for u in items],
            page=page,
            page_size=20,
            total=total,
        )
"""

from __future__ import annotations

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")
"""Type parameter for the payload carried by a response."""


# ── Success ──────────────────────────────────────────────────────────────


class SuccessResponse(BaseModel, Generic[T]):  # noqa: UP046
    """Standard wrapper for a single successful result."""

    model_config = ConfigDict(ser_json_timedelta="float", ser_json_bytes="utf8")

    success: bool = Field(default=True, description="Indicates the request succeeded")
    data: T = Field(description="The response payload")


# ── Error ────────────────────────────────────────────────────────────────


class ErrorDetail(BaseModel):
    """A single machine-readable error descriptor."""

    code: str = Field(description="Machine-readable error code (e.g. ``user_not_found``)")
    message: str = Field(description="Human-readable explanation")
    details: dict[str, Any] | None = Field(default=None, description="Optional metadata")


class ErrorResponse(BaseModel):
    """Standard wrapper for an unsuccessful result.

    The shape matches the envelope produced by the exception handlers
    in :mod:`adip.core.exceptions.handlers`.
    """

    model_config = ConfigDict(ser_json_timedelta="float", ser_json_bytes="utf8")

    error: ErrorDetail = Field(description="Error descriptor")


# ── Pagination ───────────────────────────────────────────────────────────


class PaginationMeta(BaseModel):
    """Metadata describing a paginated collection."""

    page: int = Field(ge=1, description="Current page number (1-indexed)")
    page_size: int = Field(ge=1, description="Number of items per page")
    total: int = Field(ge=0, description="Total number of items across all pages")
    total_pages: int = Field(ge=0, description="Total number of pages")

    @classmethod
    def compute(cls, total: int, page: int, page_size: int) -> PaginationMeta:
        """Calculate *total_pages* and return a fully populated instance."""
        total_pages = max(1, (total + page_size - 1) // page_size) if total else 1
        return cls(page=page, page_size=page_size, total=total, total_pages=total_pages)


class PaginatedResponse(BaseModel, Generic[T]):  # noqa: UP046
    """Standard wrapper for a paginated collection."""

    model_config = ConfigDict(ser_json_timedelta="float", ser_json_bytes="utf8")

    success: bool = Field(default=True, description="Indicates the request succeeded")
    data: list[T] = Field(description="The page of items")
    meta: PaginationMeta = Field(description="Pagination metadata")
