"""Pagination models for the REST API Layer."""

from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    limit: int = Field(default=100, ge=1, le=1000, description="Maximum items to return")
    offset: int = Field(default=0, ge=0, description="Number of items to skip")
    page: int | None = Field(default=None, ge=1, description="Page number (alternative to offset)")
    page_size: int | None = Field(default=None, ge=1, le=1000, description="Items per page (alternative to limit)")


class PaginationResult(BaseModel):
    limit: int = Field(description="Items per page")
    offset: int = Field(description="Number of items skipped")
    page: int | None = Field(default=None, description="Current page number")
    page_size: int | None = Field(default=None, description="Items per page")
    total: int = Field(default=0, description="Total number of items available")
    total_pages: int | None = Field(default=None, description="Total number of pages")


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T] = Field(default_factory=list)
    pagination: PaginationResult = Field(description="Pagination information")
