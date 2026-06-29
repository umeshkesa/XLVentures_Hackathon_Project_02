"""Registry Framework Data Transfer Objects (DTOs).

DTOs provide stable, versioned contracts for external API consumers.
They decouple the public API surface from internal domain models.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import UUID4, BaseModel, Field

from adip.registry.enums import RegistryLifecycleStatus, RegistryScope, RegistryType


class RegistryRequestDTO(BaseModel):
    """DTO for incoming registry entry creation and update requests.

    Provides a clean API contract for registry operations that is
    independent of the internal RegistryEntry domain model.
    """

    name: str = Field(
        default="",
        description="Human-readable entry name",
    )
    version: str = Field(
        default="1.0.0",
        description="Entry version (semver)",
    )
    registry_type: RegistryType = Field(
        default=RegistryType.CAPABILITY,
        description="The type of registry this entry belongs to",
    )
    scope: RegistryScope = Field(
        default=RegistryScope.GLOBAL,
        description="The scope of this entry",
    )
    owner_id: str = Field(
        default="",
        description="The user or system that owns this entry",
    )
    namespace: str = Field(
        default="default",
        description="Logical namespace for multi-tenant isolation",
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Tags for classification and discovery",
    )
    description: str = Field(
        default="",
        description="Human-readable description",
    )
    display_name: str = Field(
        default="",
        description="Display-friendly name for UIs",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata key-value pairs",
    )


class RegistryResponseDTO(BaseModel):
    """DTO for registry operation responses.

    Provides a stable API response contract independent of the
    internal domain model structure.
    """

    entry_id: UUID4 = Field(
        description="The registry entry identifier",
    )
    name: str = Field(
        default="",
        description="Human-readable entry name",
    )
    version: str = Field(
        default="1.0.0",
        description="Entry version",
    )
    registry_type: RegistryType = Field(
        description="The type of registry this entry belongs to",
    )
    scope: RegistryScope = Field(
        default=RegistryScope.GLOBAL,
        description="The scope of this entry",
    )
    status: RegistryLifecycleStatus = Field(
        default=RegistryLifecycleStatus.REGISTERED,
        description="Current lifecycle status",
    )
    enabled: bool = Field(
        default=True,
        description="Whether the entry is enabled",
    )
    created_at: datetime = Field(
        description="When the entry was registered",
    )
    updated_at: datetime = Field(
        description="When the entry was last updated",
    )


class RegistrySearchDTO(BaseModel):
    """DTO for registry search requests.

    Provides a clean API contract for search operations that is
    independent of the internal RegistryFilter domain model.
    """

    query: str = Field(
        default="",
        description="Free-text search query",
    )
    registry_type: RegistryType | None = Field(
        default=None,
        description="Filter by registry type",
    )
    scope: RegistryScope | None = Field(
        default=None,
        description="Filter by scope",
    )
    status: RegistryLifecycleStatus | None = Field(
        default=None,
        description="Filter by lifecycle status",
    )
    namespace: str = Field(
        default="",
        description="Filter by namespace (empty = all namespaces)",
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Filter by tags (entries matching any tag)",
    )
    correlation_id: str = Field(
        default="",
        description="Correlation ID for distributed tracing",
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


class RegistryRegistrationDTO(BaseModel):
    """DTO for registry entry registration requests.

    Provides the minimum contract needed to register a new entry
    in the registry.
    """

    name: str = Field(
        default="",
        description="Unique entry name",
    )
    version: str = Field(
        default="1.0.0",
        description="Entry version (semver)",
    )
    registry_type: RegistryType = Field(
        default=RegistryType.CAPABILITY,
        description="The type of registry this entry belongs to",
    )
    scope: RegistryScope = Field(
        default=RegistryScope.GLOBAL,
        description="The scope of this entry",
    )
    namespace: str = Field(
        default="default",
        description="Logical namespace for multi-tenant isolation",
    )
    owner_id: str = Field(
        default="",
        description="The user or system that owns this entry",
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Tags for classification and discovery",
    )
    entry_data: dict[str, Any] = Field(
        default_factory=dict,
        description="Entry-specific data as key-value pairs",
    )
