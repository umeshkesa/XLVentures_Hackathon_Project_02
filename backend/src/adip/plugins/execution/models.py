"""Execution-layer models for the Plugin Manager.

These models support internal processing: discovery results,
dependency graphs, compatibility checks, traces, resource usage,
and capability registrations. They are not exposed through the
public PluginService API.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import UUID4, BaseModel, Field

from adip.plugins.contracts.models import PluginManifest
from adip.plugins.enums import PluginDomain, PluginLifecycleStatus, PluginType

# ─────────────────────────────────────────────────────────────────────────────
# DiscoveryResult
# ─────────────────────────────────────────────────────────────────────────────


class DiscoveryResult(BaseModel):
    """Result of discovering a plugin from a source.

    Contains the discovered plugin metadata, source type, and
    extracted manifest information before full validation.
    """

    discovery_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique discovery identifier",
    )
    plugin_name: str = Field(
        default="",
        description="Discovered plugin name",
    )
    plugin_version: str = Field(
        default="",
        description="Discovered plugin version",
    )
    plugin_type: PluginType | None = Field(
        default=None,
        description="Discovered plugin type (if determinable)",
    )
    domain: PluginDomain = Field(
        default=PluginDomain.GENERAL,
        description="Discovered plugin domain",
    )
    source: str = Field(
        default="",
        description="Discovery source (directory, package, repository, zip)",
    )
    source_type: str = Field(
        default="",
        description="Source type: local_directory, installed_package, plugin_repository, zip_package",
    )
    manifest: PluginManifest | None = Field(
        default=None,
        description="Extracted manifest if available",
    )
    discovered_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the plugin was discovered",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional discovery metadata",
    )


# ─────────────────────────────────────────────────────────────────────────────
# DependencyGraph
# ─────────────────────────────────────────────────────────────────────────────


class DependencyGraph(BaseModel):
    """A directed graph of plugin dependencies.

    Models the dependency relationships between plugins for
    resolution, cycle detection, and load ordering.

    Enhanced in Phase 3.5 with root_plugins, leaf_plugins,
    circular_dependency_reports, dependency_depth, load_order,
    and unused_dependencies.
    """

    graph_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique graph identifier",
    )
    nodes: dict[str, list[str]] = Field(
        default_factory=dict,
        description="Adjacency list: plugin_name -> list of dependency plugin_names",
    )
    root_plugins: list[str] = Field(
        default_factory=list,
        description="Plugins with no dependencies (entry points)",
    )
    leaf_plugins: list[str] = Field(
        default_factory=list,
        description="Plugins that no other plugin depends on",
    )
    circular_dependency_reports: list[list[str]] = Field(
        default_factory=list,
        description="Detected cycles, each as a list of plugin names",
    )
    dependency_depth: int = Field(
        default=0,
        ge=0,
        description="Maximum dependency depth in the graph",
    )
    load_order: list[str] = Field(
        default_factory=list,
        description="Topological load order (dependencies first)",
    )
    unused_dependencies: list[str] = Field(
        default_factory=list,
        description="Dependencies declared but not consumed by any plugin",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the graph was created",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional graph metadata",
    )


# ─────────────────────────────────────────────────────────────────────────────
# DependencyNode
# ─────────────────────────────────────────────────────────────────────────────


class DependencyNode(BaseModel):
    """A single node in the plugin dependency graph.

    Represents a plugin and its direct dependencies with
    resolution status and version constraints.
    """

    plugin_id: str = Field(
        description="The plugin identifier",
    )
    plugin_name: str = Field(
        default="",
        description="The plugin name",
    )
    version: str = Field(
        default="1.0.0",
        description="Plugin version",
    )
    dependencies: list[str] = Field(
        default_factory=list,
        description="Plugin IDs this node depends on",
    )
    dependents: list[str] = Field(
        default_factory=list,
        description="Plugin IDs that depend on this node",
    )
    resolved: bool = Field(
        default=False,
        description="Whether this node's dependencies are resolved",
    )
    level: int = Field(
        default=0,
        ge=0,
        description="Hierarchical level in the dependency tree (0 = root)",
    )


# ─────────────────────────────────────────────────────────────────────────────
# CompatibilityResult
# ─────────────────────────────────────────────────────────────────────────────


class CompatibilityResult(BaseModel):
    """Result of a compatibility check for a plugin.

    Validates platform, manifest, API, plugin, and dependency
    version compatibility. Returns a pass/fail outcome with
    detailed reasons for any incompatibilities.
    """

    result_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique result identifier",
    )
    plugin_id: str = Field(
        default="",
        description="The plugin that was checked",
    )
    plugin_name: str = Field(
        default="",
        description="The plugin name",
    )
    compatible: bool = Field(
        default=True,
        description="Whether the plugin is compatible overall",
    )
    platform_version_compatible: bool = Field(
        default=True,
        description="Whether the platform version is compatible",
    )
    manifest_version_compatible: bool = Field(
        default=True,
        description="Whether the manifest version is compatible",
    )
    api_version_compatible: bool = Field(
        default=True,
        description="Whether the API version is compatible",
    )
    plugin_version_compatible: bool = Field(
        default=True,
        description="Whether the plugin version is compatible",
    )
    dependency_versions_compatible: bool = Field(
        default=True,
        description="Whether all dependency versions are compatible",
    )
    reasons: list[str] = Field(
        default_factory=list,
        description="Reasons for incompatibility (if any)",
    )
    checked_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the check was performed",
    )


# ─────────────────────────────────────────────────────────────────────────────
# LoaderResult
# ─────────────────────────────────────────────────────────────────────────────


class LoaderResult(BaseModel):
    """Result of loading a plugin through the pipeline.

    Tracks the outcome of each pipeline stage: validation,
    dependency resolution, sandbox creation, metadata loading,
    capability registration, initialisation, and activation.
    """

    result_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique result identifier",
    )
    plugin_id: UUID4 = Field(
        description="The plugin that was loaded",
    )
    plugin_name: str = Field(
        default="",
        description="The plugin name",
    )
    success: bool = Field(
        default=True,
        description="Whether loading succeeded overall",
    )
    validated: bool = Field(
        default=False,
        description="Whether validation passed",
    )
    dependencies_resolved: bool = Field(
        default=False,
        description="Whether dependencies were resolved",
    )
    sandbox_created: bool = Field(
        default=False,
        description="Whether a sandbox was created",
    )
    metadata_loaded: bool = Field(
        default=False,
        description="Whether metadata was loaded",
    )
    capabilities_registered: bool = Field(
        default=False,
        description="Whether capabilities were registered",
    )
    initialized: bool = Field(
        default=False,
        description="Whether initialisation completed",
    )
    activated: bool = Field(
        default=False,
        description="Whether activation completed",
    )
    errors: list[str] = Field(
        default_factory=list,
        description="Errors encountered during loading",
    )
    loaded_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the loading completed",
    )


# ─────────────────────────────────────────────────────────────────────────────
# InitializationResult
# ─────────────────────────────────────────────────────────────────────────────


class InitializationResult(BaseModel):
    """Result of initialising a plugin.

    Tracks configuration loading, namespace preparation,
    resource allocation, and lifecycle transition outcome.
    """

    result_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique result identifier",
    )
    plugin_id: UUID4 = Field(
        description="The plugin that was initialised",
    )
    config_loaded: bool = Field(
        default=False,
        description="Whether configuration was loaded",
    )
    namespace_prepared: bool = Field(
        default=False,
        description="Whether namespace was prepared",
    )
    resources_allocated: bool = Field(
        default=False,
        description="Whether resources were allocated",
    )
    lifecycle_transitioned: bool = Field(
        default=False,
        description="Whether lifecycle transitioned to INITIALIZED",
    )
    success: bool = Field(
        default=True,
        description="Whether initialisation succeeded overall",
    )
    errors: list[str] = Field(
        default_factory=list,
        description="Errors encountered during initialisation",
    )
    initialized_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When initialisation completed",
    )


# ─────────────────────────────────────────────────────────────────────────────
# ResourceUsage
# ─────────────────────────────────────────────────────────────────────────────


class ResourceUsage(BaseModel):
    """Snapshot of resource usage for a plugin.

    Tracks CPU, memory, storage, network, timeout limits,
    and agent/tool resource constraints.
    """

    plugin_id: UUID4 = Field(
        description="The plugin this usage belongs to",
    )
    cpu_percent: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="CPU usage percentage",
    )
    memory_mb: float = Field(
        default=0.0,
        ge=0.0,
        description="Memory usage in megabytes",
    )
    storage_mb: float = Field(
        default=0.0,
        ge=0.0,
        description="Storage usage in megabytes",
    )
    network_bytes: int = Field(
        default=0,
        ge=0,
        description="Network bytes transferred",
    )
    timeout_seconds: float = Field(
        default=30.0,
        ge=0.0,
        description="Timeout limit in seconds",
    )
    agent_count: int = Field(
        default=0,
        ge=0,
        description="Number of agent instances",
    )
    tool_count: int = Field(
        default=0,
        ge=0,
        description="Number of tool instances",
    )
    recorded_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the snapshot was recorded",
    )


# ─────────────────────────────────────────────────────────────────────────────
# LifecycleHistoryEntry
# ─────────────────────────────────────────────────────────────────────────────


class LifecycleHistoryEntry(BaseModel):
    """A single lifecycle transition record for a plugin."""

    entry_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique history entry identifier",
    )
    plugin_id: UUID4 = Field(
        description="The plugin that transitioned",
    )
    from_status: PluginLifecycleStatus | None = Field(
        default=None,
        description="Previous lifecycle status",
    )
    to_status: PluginLifecycleStatus = Field(
        description="New lifecycle status",
    )
    reason: str = Field(
        default="",
        description="Reason for the transition",
    )
    changed_by: str = Field(
        default="",
        description="User or system that performed the transition",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the transition occurred",
    )


# ─────────────────────────────────────────────────────────────────────────────
# CapabilityRecord
# ─────────────────────────────────────────────────────────────────────────────


class CapabilityRecord(BaseModel):
    """A registered capability record.

    Tracks the registration state of a plugin capability
    including its plugin owner, registration status,
    and last updated timestamp.
    """

    record_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique record identifier",
    )
    capability_id: UUID4 = Field(
        description="The capability identifier",
    )
    plugin_id: UUID4 = Field(
        description="The plugin that owns this capability",
    )
    name: str = Field(
        default="",
        description="Capability name",
    )
    version: str = Field(
        default="1.0.0",
        description="Capability version",
    )
    category: str = Field(
        default="",
        description="Capability category",
    )
    status: str = Field(
        default="registered",
        description="Registration status: registered, unregistered, deprecated",
    )
    registered_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the capability was registered",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the capability was last updated",
    )


# ─────────────────────────────────────────────────────────────────────────────
# TraceRecord
# ─────────────────────────────────────────────────────────────────────────────


class TraceRecord(BaseModel):
    """A single trace entry recording a stage in a plugin operation.

    Tracks execution stage, operation type, plugin context,
    timing, warnings, errors, and correlation ID for observability.
    """

    trace_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique trace identifier",
    )
    stage_name: str = Field(
        description="Name of the pipeline stage",
    )
    operation: str = Field(
        description="The operation being performed",
    )
    plugin_id: str | None = Field(
        default=None,
        description="The plugin involved (if applicable)",
    )
    plugin_version: str = Field(
        default="",
        description="Plugin version at the time of tracing",
    )
    manifest_version: str = Field(
        default="",
        description="Manifest version at the time of tracing",
    )
    domain: str = Field(
        default="",
        description="Plugin domain of the operation",
    )
    sandbox_id: str = Field(
        default="",
        description="Sandbox ID if applicable",
    )
    lifecycle_state: str = Field(
        default="",
        description="Current lifecycle state",
    )
    started_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the stage began",
    )
    completed_at: datetime | None = Field(
        default=None,
        description="When the stage finished",
    )
    duration_ms: float | None = Field(
        default=None,
        ge=0.0,
        description="Wall-clock duration in milliseconds",
    )
    success: bool = Field(
        default=True,
        description="Whether the stage completed without error",
    )
    warnings: list[str] = Field(
        default_factory=list,
        description="Non-fatal warnings",
    )
    errors: list[str] = Field(
        default_factory=list,
        description="Fatal errors",
    )
    correlation_id: str = Field(
        default="",
        description="Correlation ID for distributed tracing",
    )
