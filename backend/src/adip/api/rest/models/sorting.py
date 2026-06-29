"""Sorting models for the REST API Layer."""

from __future__ import annotations

from pydantic import BaseModel, Field

from adip.api.rest.enums import SortDirection


class SortCriteria(BaseModel):
    field: str = Field(description="Field name to sort by")
    direction: SortDirection = Field(default=SortDirection.ASC, description="Sort direction")


class SortParams(BaseModel):
    sorts: list[SortCriteria] = Field(default_factory=list, description="List of sort criteria")
