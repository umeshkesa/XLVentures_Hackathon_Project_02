"""Domain-neutral models for capability discovery."""

from __future__ import annotations

import uuid
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, field_validator


def _normalize_terms(value: Any) -> frozenset[str]:
    """Normalize a collection of matching terms for reliable comparison."""
    if isinstance(value, str):
        raise ValueError("Expected a collection of strings, not a single string")
    try:
        raw_terms = tuple(value)
    except TypeError as exc:
        raise ValueError("Expected an iterable of strings") from exc
    if any(not isinstance(item, str) for item in raw_terms):
        raise ValueError("Matching terms must be strings")
    terms = frozenset(item.strip().casefold() for item in raw_terms)
    if "" in terms:
        raise ValueError("Matching terms must not be empty")
    return terms


class Capability(BaseModel):
    """A discoverable operation advertised by any ADIP component.

    The model deliberately contains no executable handler or domain-specific
    state. Other components can associate the stable ID with an implementation.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    name: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=2000)
    category: str = Field(min_length=1, max_length=100)
    tags: frozenset[str] = Field(default_factory=frozenset)
    inputs: frozenset[str] = Field(default_factory=frozenset)
    outputs: frozenset[str] = Field(default_factory=frozenset)
    version: str = Field(default="1.0.0", min_length=1, max_length=50)
    priority: int = 0

    @field_validator("name", "description", "version")
    @classmethod
    def strip_text(cls, value: str, info: ValidationInfo) -> str:
        """Remove accidental surrounding whitespace from display text."""
        normalized = value.strip()
        if not normalized and info.field_name != "description":
            raise ValueError("Value must not be blank")
        return normalized

    @field_validator("category")
    @classmethod
    def normalize_category(cls, value: str) -> str:
        """Normalize category values used for exact matching."""
        normalized = value.strip().casefold()
        if not normalized:
            raise ValueError("Category must not be blank")
        return normalized

    @field_validator("tags", "inputs", "outputs", mode="before")
    @classmethod
    def normalize_matching_terms(cls, value: Any) -> frozenset[str]:
        """Normalize metadata collections used by the matching engine."""
        return _normalize_terms(value)


class CapabilityUpdate(BaseModel):
    """Allowed changes to an existing capability."""

    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    category: str | None = Field(default=None, min_length=1, max_length=100)
    tags: frozenset[str] | None = None
    inputs: frozenset[str] | None = None
    outputs: frozenset[str] | None = None
    version: str | None = Field(default=None, min_length=1, max_length=50)
    priority: int | None = None

    @field_validator("name", "description", "version")
    @classmethod
    def strip_optional_text(cls, value: str | None, info: ValidationInfo) -> str | None:
        """Normalize supplied display fields while retaining omitted values."""
        if value is None:
            return None
        normalized = value.strip()
        if not normalized and info.field_name != "description":
            raise ValueError("Value must not be blank")
        return normalized

    @field_validator("category")
    @classmethod
    def normalize_optional_category(cls, value: str | None) -> str | None:
        """Normalize a supplied category."""
        if value is None:
            return None
        normalized = value.strip().casefold()
        if not normalized:
            raise ValueError("Category must not be blank")
        return normalized

    @field_validator("tags", "inputs", "outputs", mode="before")
    @classmethod
    def normalize_optional_terms(cls, value: Any) -> frozenset[str] | None:
        """Normalize supplied matching metadata."""
        return _normalize_terms(value) if value is not None else None


class CapabilityQuery(BaseModel):
    """Metadata constraints used to search the registry."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    text: str | None = None
    category: str | None = None
    tags: frozenset[str] = Field(default_factory=frozenset)
    inputs: frozenset[str] = Field(default_factory=frozenset)
    outputs: frozenset[str] = Field(default_factory=frozenset)

    @field_validator("text")
    @classmethod
    def normalize_text(cls, value: str | None) -> str | None:
        """Normalize optional free-text search input."""
        normalized = value.strip().casefold() if value is not None else None
        return normalized or None

    @field_validator("category")
    @classmethod
    def normalize_query_category(cls, value: str | None) -> str | None:
        """Normalize optional category search input."""
        normalized = value.strip().casefold() if value is not None else None
        return normalized or None

    @field_validator("tags", "inputs", "outputs", mode="before")
    @classmethod
    def normalize_query_terms(cls, value: Any) -> frozenset[str]:
        """Normalize matching constraints."""
        return _normalize_terms(value)
