"""Filtering models for the REST API Layer."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from adip.api.rest.enums import FilterOperator


class FilterCriteria(BaseModel):
    field: str = Field(description="Field name to filter on")
    operator: FilterOperator = Field(default=FilterOperator.EQ, description="Comparison operator")
    value: Any = Field(default=None, description="Value to compare against")


class FilterGroup(BaseModel):
    filters: list[FilterCriteria] = Field(default_factory=list, description="List of filter criteria")
    combinator: str = Field(default="AND", pattern="^(AND|OR)$", description="Logical combinator for filters")


class FilterParams(BaseModel):
    groups: list[FilterGroup] = Field(default_factory=list, description="Filter groups combined with AND")
    raw: str | None = Field(default=None, description="Raw filter string expression")
