"""Plugin Manager Data Transfer Objects (DTOs).

DTOs provide stable, versioned contracts for external API consumers.
They decouple the public API surface from internal domain models.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import UUID4, BaseModel, Field

from adip.plugins.enums import PluginDomain, PluginLifecycleStatus, PluginType


class PluginRequestDTO(BaseModel):
    """DTO for incoming plugin registration requests.

    Provides a clean API contract for plugin operations that is
    independent of the internal Plugin domain model.
    """

    name: str = Field(
        default="",
        description="Unique plugin name",
    )
    version: str = Field(
        default="1.0.0",
        description="Plugin version (semver)",
    )
    plugin_type: PluginType = Field(
        default=PluginType.DOMAIN,
        description="The type of plugin",
    )
    domain: PluginDomain = Field(
        default=PluginDomain.GENERAL,
        description="The domain this plugin belongs to",
    )
    owner_id: str = Field(
        default="",
        description="The user or system that owns this plugin",
    )
    namespace: str = Field(
        default="default",
        description="Logical namespace for multi-tenant isolation",
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Tags for classification and discovery",
    )
    manifest: dict[str, Any] = Field(
        default_factory=dict,
        description="Plugin manifest as a serialisable dictionary",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata key-value pairs",
    )


class PluginResponseDTO(BaseModel):
    """DTO for plugin operation responses.

    Provides a stable API response contract independent of the
    internal domain model structure.
    """

    plugin_id: UUID4 = Field(
        description="The plugin identifier",
    )
    name: str = Field(
        default="",
        description="Unique plugin name",
    )
    version: str = Field(
        default="1.0.0",
        description="Plugin version",
    )
    plugin_type: PluginType = Field(
        description="The type of plugin",
    )
    domain: PluginDomain = Field(
        default=PluginDomain.GENERAL,
        description="The plugin domain",
    )
    status: PluginLifecycleStatus = Field(
        default=PluginLifecycleStatus.DISCOVERED,
        description="Current lifecycle status",
    )
    enabled: bool = Field(
        default=True,
        description="Whether the plugin is enabled",
    )
    created_at: datetime = Field(
        description="When the plugin was created",
    )
    updated_at: datetime = Field(
        description="When the plugin was last updated",
    )


class PluginInstallDTO(BaseModel):
    """DTO for plugin installation requests.

    Provides the minimum contract needed to install a plugin.
    """

    source: str = Field(
        default="",
        description="Plugin source path or identifier",
    )
    name: str = Field(
        default="",
        description="Unique plugin name",
    )
    version: str = Field(
        default="1.0.0",
        description="Plugin version (semver)",
    )
    plugin_type: PluginType = Field(
        default=PluginType.DOMAIN,
        description="The type of plugin",
    )
    domain: PluginDomain = Field(
        default=PluginDomain.GENERAL,
        description="The domain this plugin belongs to",
    )
    namespace: str = Field(
        default="default",
        description="Logical namespace for multi-tenant isolation",
    )
    config: dict[str, Any] = Field(
        default_factory=dict,
        description="Initial configuration as key-value pairs",
    )


class PluginDiscoveryDTO(BaseModel):
    """DTO for plugin discovery results.

    Represents a plugin that was discovered from a source but not
    yet installed or validated.
    """

    discovery_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique discovery identifier",
    )
    name: str = Field(
        default="",
        description="Discovered plugin name",
    )
    version: str = Field(
        default="",
        description="Discovered plugin version",
    )
    plugin_type: PluginType | None = Field(
        default=None,
        description="Detected plugin type (if determinable)",
    )
    domain: PluginDomain = Field(
        default=PluginDomain.GENERAL,
        description="Detected plugin domain",
    )
    source: str = Field(
        default="",
        description="Discovery source path or identifier",
    )
    discovered_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the plugin was discovered",
    )
    manifest_summary: dict[str, Any] = Field(
        default_factory=dict,
        description="Summary of the manifest if available",
    )


class PluginSandboxDTO(BaseModel):
    """DTO for sandbox configuration.

    Provides a clean contract for requesting or reporting sandbox
    configuration that is independent of the internal PluginSandbox
    model.
    """

    plugin_id: UUID4 = Field(
        description="The plugin this sandbox is for",
    )
    namespace: str = Field(
        default="",
        description="Desired namespace for the sandbox",
    )
    domain: PluginDomain = Field(
        default=PluginDomain.GENERAL,
        description="The domain this sandbox operates in",
    )
    resource_limits: dict[str, Any] = Field(
        default_factory=dict,
        description="Resource limits (cpu, memory, io, network)",
    )
    permissions: list[str] = Field(
        default_factory=list,
        description="Requested permissions for the sandbox",
    )
    isolation_policy: str = Field(
        default="strict",
        description="Isolation level: strict, moderate, permissive",
    )
