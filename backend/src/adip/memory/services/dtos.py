"""Data Transfer Objects for the Memory Manager API layer."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from adip.memory.contracts.models import MemoryRecord
from adip.memory.enums import MemoryType


class MemoryRequestDTO(BaseModel):
    """DTO for creating or updating a memory record via the API.

    Allows clients to specify the memory type, owner, namespace,
    tags, metadata, and type-specific data fields.
    """

    memory_type: MemoryType = Field(
        description="Category of memory to create or update",
    )
    owner_id: str = Field(
        default="",
        description="Owner of the memory record",
    )
    namespace: str = Field(
        default="default",
        description="Logical namespace for grouping",
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Tags for filtering and discovery",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary key-value metadata",
    )
    payload: dict[str, Any] = Field(
        default_factory=dict,
        description="Type-specific data payload",
    )


class MemoryResponseDTO(BaseModel):
    """DTO for returning memory records via the API.

    Wraps a ``MemoryRecord`` (or subtype) with additional response
    metadata.
    """

    record: MemoryRecord = Field(
        description="The memory record (or subtype)",
    )
    tier: str = Field(
        default="",
        description="The storage tier the record resides in",
    )
    duration_ms: float = Field(
        default=0.0,
        ge=0.0,
        description="Time taken to fulfil the request in milliseconds",
    )


class MemorySearchRequestDTO(BaseModel):
    """DTO for searching memory records."""

    memory_type: MemoryType | None = Field(
        default=None,
        description="Filter by memory type",
    )
    owner_id: str = Field(
        default="",
        description="Filter by owner",
    )
    namespace: str = Field(
        default="",
        description="Filter by namespace",
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Filter by tags (records matching any tag are returned)",
    )
    query: str = Field(
        default="",
        description="Free-text search query",
    )
    limit: int = Field(
        default=20,
        ge=1,
        le=1000,
        description="Maximum number of results to return",
    )
    offset: int = Field(
        default=0,
        ge=0,
        description="Number of results to skip for pagination",
    )


class MemorySearchResponseDTO(BaseModel):
    """DTO for returning search results."""

    results: list[MemoryRecord] = Field(
        default_factory=list,
        description="Matching memory records",
    )
    total_count: int = Field(
        default=0,
        ge=0,
        description="Total number of matching records (ignoring pagination)",
    )
    limit: int = Field(
        default=20,
        description="The limit used for this search",
    )
    offset: int = Field(
        default=0,
        description="The offset used for this search",
    )
    duration_ms: float = Field(
        default=0.0,
        ge=0.0,
        description="Time taken to fulfil the search in milliseconds",
    )
