"""Plugin Manager domain models.

Defines the core data contracts for the plugin platform including
plugins, manifests, metadata, capabilities, dependencies, sandboxes,
namespaces, configuration, health, metrics, sessions, decisions,
and policies.

All models are Pydantic v2 BaseModel subclasses with full type
annotations, validation, and documentation.

Architecture:
    PluginService  →  PluginManager  →  PluginCoordinator
                                           ├── PluginLoader
                                           ├── PluginValidator
                                           ├── DependencyResolver
                                           ├── CapabilityDiscoverer
                                           ├── LifecycleManager
                                           ├── VersionManager
                                           ├── SandboxManager
                                           └── PluginHealthChecker

Domain boundaries follow the ADIP pattern with component-level
interfaces and dependency injection throughout.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import UUID4, BaseModel, Field

from adip.plugins.enums import PluginDomain, PluginLifecycleStatus, PluginType

# ─────────────────────────────────────────────────────────────────────────────
# PluginCapability
# ─────────────────────────────────────────────────────────────────────────────


class PluginCapability(BaseModel):
    """A capability exposed by a plugin.

    Capabilities define what a plugin can do — they are the
    functional units that other ADIP components can discover
    and consume.
    """

    capability_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique capability identifier",
    )
    name: str = Field(
        default="",
        description="Human-readable capability name",
    )
    description: str = Field(
        default="",
        description="Description of what this capability provides",
    )
    version: str = Field(
        default="1.0.0",
        description="Capability version (semver)",
    )
    dependencies: list[str] = Field(
        default_factory=list,
        description="Capability IDs this capability depends on",
    )
    category: str = Field(
        default="",
        description="Capability category for grouping and filtering",
    )
    visibility: str = Field(
        default="public",
        description="Visibility level: public, protected, private",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional capability metadata",
    )


# ─────────────────────────────────────────────────────────────────────────────
# PluginDependency
# ─────────────────────────────────────────────────────────────────────────────


class PluginDependency(BaseModel):
    """A dependency of a plugin on another plugin.

    Defines which plugins are required or optional, with version
    constraints for dependency resolution.
    """

    dependency_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique dependency identifier",
    )
    plugin_id: str = Field(
        default="",
        description="The plugin ID this dependency refers to",
    )
    plugin_name: str = Field(
        default="",
        description="The plugin name this dependency refers to",
    )
    version_constraint: str = Field(
        default=">=1.0.0",
        description="Semver version constraint (e.g. >=1.0.0, ~=2.0, >=1.0 <2.0)",
    )
    optional: bool = Field(
        default=False,
        description="Whether this dependency is optional",
    )
    required: bool = Field(
        default=True,
        description="Whether this dependency is required (inverse shorthand)",
    )
    status: str = Field(
        default="pending",
        description="Dependency resolution status: pending, satisfied, unsatisfied, incompatible",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional dependency metadata",
    )

    @property
    def is_required(self) -> bool:
        """Return True if this dependency is required (not optional)."""
        return self.required and not self.optional


# ─────────────────────────────────────────────────────────────────────────────
# PluginManifest
# ─────────────────────────────────────────────────────────────────────────────


class PluginManifest(BaseModel):
    """The manifest of a plugin.

    Contains all metadata required to identify, validate, and load
    a plugin. Every plugin must provide a valid manifest.
    """

    manifest_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique manifest identifier",
    )
    plugin_name: str = Field(
        default="",
        description="Unique plugin name",
    )
    plugin_version: str = Field(
        default="1.0.0",
        description="Plugin version (semver)",
    )
    plugin_type: PluginType = Field(
        description="The type of plugin",
    )
    plugin_domain: PluginDomain = Field(
        default=PluginDomain.GENERAL,
        description="The domain this plugin belongs to",
    )
    description: str = Field(
        default="",
        description="Human-readable plugin description",
    )
    author: str = Field(
        default="",
        description="Plugin author or organisation",
    )
    license: str = Field(
        default="",
        description="Plugin license identifier",
    )
    entry_point: str = Field(
        default="",
        description="Plugin entry point module path",
    )
    capabilities: list[PluginCapability] = Field(
        default_factory=list,
        description="Capabilities exposed by this plugin",
    )
    dependencies: list[PluginDependency] = Field(
        default_factory=list,
        description="Dependencies on other plugins",
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Tags for classification and discovery",
    )
    homepage: str = Field(
        default="",
        description="Plugin homepage URL",
    )
    repository: str = Field(
        default="",
        description="Plugin source repository URL",
    )
    documentation: str = Field(
        default="",
        description="Plugin documentation URL",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Extensibility dictionary for additional manifest data",
    )


# ─────────────────────────────────────────────────────────────────────────────
# PluginMetadata
# ─────────────────────────────────────────────────────────────────────────────


class PluginMetadata(BaseModel):
    """Runtime metadata for a plugin.

    Tracks runtime information that is not part of the static
    manifest but is needed for operations and observability.
    """

    installed_at: datetime | None = Field(
        default=None,
        description="When the plugin was installed",
    )
    loaded_at: datetime | None = Field(
        default=None,
        description="When the plugin was last loaded",
    )
    activated_at: datetime | None = Field(
        default=None,
        description="When the plugin was last activated",
    )
    last_error: str = Field(
        default="",
        description="Last error message (if any)",
    )
    error_count: int = Field(
        default=0,
        ge=0,
        description="Total error count since installation",
    )
    load_count: int = Field(
        default=0,
        ge=0,
        description="Total number of times loaded",
    )
    total_executions: int = Field(
        default=0,
        ge=0,
        description="Total number of executions",
    )
    custom: dict[str, Any] = Field(
        default_factory=dict,
        description="Custom runtime metadata",
    )


# ─────────────────────────────────────────────────────────────────────────────
# Plugin
# ─────────────────────────────────────────────────────────────────────────────


class Plugin(BaseModel):
    """A plugin in the ADIP platform.

    Represents a dynamically-loaded extension that enhances the
    platform with domain-specific logic, agents, tools, or
    integrations.
    """

    plugin_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique plugin identifier",
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
    status: PluginLifecycleStatus = Field(
        default=PluginLifecycleStatus.DISCOVERED,
        description="Current lifecycle status",
    )
    manifest: PluginManifest | None = Field(
        default=None,
        description="The plugin manifest",
    )
    metadata: PluginMetadata = Field(
        default_factory=PluginMetadata,
        description="Runtime metadata",
    )
    enabled: bool = Field(
        default=True,
        description="Whether the plugin is currently enabled",
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Tags for classification and discovery",
    )
    namespace: str = Field(
        default="default",
        description="Logical namespace for multi-tenant isolation",
    )
    owner_id: str = Field(
        default="",
        description="The user or system that owns this plugin",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the plugin was created",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the plugin was last updated",
    )
    extra: dict[str, Any] = Field(
        default_factory=dict,
        description="Extensibility dictionary for arbitrary additional data",
    )


# ─────────────────────────────────────────────────────────────────────────────
# PluginConfiguration
# ─────────────────────────────────────────────────────────────────────────────


class PluginConfiguration(BaseModel):
    """Configuration for a plugin instance.

    Provides type-safe configuration parameters that are passed
    to a plugin during initialisation.
    """

    config_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique configuration identifier",
    )
    plugin_id: UUID4 = Field(
        description="The plugin this configuration belongs to",
    )
    settings: dict[str, Any] = Field(
        default_factory=dict,
        description="Configuration key-value pairs",
    )
    environment: str = Field(
        default="production",
        description="Deployment environment (development, staging, production)",
    )
    secrets: dict[str, str] = Field(
        default_factory=dict,
        description="Secret configuration keys (masked in logs)",
    )
    version: int = Field(
        default=1,
        ge=1,
        description="Configuration version number",
    )
    enabled: bool = Field(
        default=True,
        description="Whether this configuration is active",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the configuration was created",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the configuration was last updated",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional configuration metadata",
    )


# ─────────────────────────────────────────────────────────────────────────────
# PluginNamespace
# ─────────────────────────────────────────────────────────────────────────────


class PluginNamespace(BaseModel):
    """A logical namespace for plugin isolation.

    Each plugin operates within its own namespace to prevent
    resource collision and provide logical isolation across
    the ADIP platform components.
    """

    namespace_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique namespace identifier",
    )
    plugin_id: UUID4 = Field(
        description="The plugin that owns this namespace",
    )
    name: str = Field(
        default="",
        description="Namespace name (e.g. energy, healthcare)",
    )
    memory_namespace: str = Field(
        default="",
        description="Memory Manager namespace for this plugin",
    )
    knowledge_namespace: str = Field(
        default="",
        description="Knowledge Manager namespace for this plugin",
    )
    rule_namespace: str = Field(
        default="",
        description="Rule Manager namespace for this plugin",
    )
    action_namespace: str = Field(
        default="",
        description="Action namespace for this plugin",
    )
    capability_namespace: str = Field(
        default="",
        description="Capability namespace for this plugin",
    )
    enabled: bool = Field(
        default=True,
        description="Whether this namespace is active",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the namespace was created",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional namespace metadata",
    )


# ─────────────────────────────────────────────────────────────────────────────
# PluginSandbox
# ─────────────────────────────────────────────────────────────────────────────


class PluginSandbox(BaseModel):
    """A logical sandbox for plugin execution isolation.

    Every plugin executes inside its own logical sandbox. Each
    sandbox owns its ID, namespace, configuration, resource limits,
    permissions, isolation policy, health, lifecycle, and assigned
    capabilities.

    No runtime isolation is enforced — the model serves as the
    contract for future sandbox implementation.

    Enhanced in Phase 3.5 with health, lifecycle, and
    assigned_capabilities fields.
    """

    sandbox_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique sandbox identifier",
    )
    plugin_id: UUID4 = Field(
        description="The plugin this sandbox belongs to",
    )
    namespace: str = Field(
        default="",
        description="Logical namespace for this sandbox",
    )
    domain: PluginDomain = Field(
        default=PluginDomain.GENERAL,
        description="The domain this sandbox operates in",
    )
    configuration: dict[str, Any] = Field(
        default_factory=dict,
        description="Sandbox-specific configuration",
    )
    memory_namespace: str = Field(
        default="",
        description="Isolated Memory Manager namespace",
    )
    knowledge_namespace: str = Field(
        default="",
        description="Isolated Knowledge Manager namespace",
    )
    rule_namespace: str = Field(
        default="",
        description="Isolated Rule Manager namespace",
    )
    action_namespace: str = Field(
        default="",
        description="Isolated Action namespace",
    )
    capability_namespace: str = Field(
        default="",
        description="Isolated capability namespace",
    )
    resource_limits: dict[str, Any] = Field(
        default_factory=dict,
        description="Resource limits (cpu, memory, io, network)",
    )
    permissions: list[str] = Field(
        default_factory=list,
        description="Granted permissions for this sandbox",
    )
    isolation_policy: str = Field(
        default="strict",
        description="Isolation level: strict, moderate, permissive",
    )
    health: str = Field(
        default="UNKNOWN",
        description="Sandbox health: HEALTHY, DEGRADED, UNHEALTHY, UNKNOWN",
    )
    lifecycle: str = Field(
        default="created",
        description="Sandbox lifecycle: created, initialized, active, suspended, destroyed",
    )
    assigned_capabilities: list[str] = Field(
        default_factory=list,
        description="Capability names assigned to this sandbox",
    )
    enabled: bool = Field(
        default=True,
        description="Whether this sandbox is active",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the sandbox was created",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the sandbox was last updated",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional sandbox metadata",
    )


# ─────────────────────────────────────────────────────────────────────────────
# PluginPolicy
# ─────────────────────────────────────────────────────────────────────────────


class PluginPolicy(BaseModel):
    """A policy governing plugin behaviour.

    Defines constraints on what a plugin can do, what resources
    it can access, and what actions are permitted.
    """

    policy_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique policy identifier",
    )
    plugin_id: UUID4 = Field(
        description="The plugin this policy applies to",
    )
    name: str = Field(
        default="",
        description="Human-readable policy name",
    )
    description: str = Field(
        default="",
        description="Policy description and intent",
    )
    allowed_capabilities: list[str] = Field(
        default_factory=list,
        description="Capability names permitted by this policy",
    )
    denied_capabilities: list[str] = Field(
        default_factory=list,
        description="Capability names explicitly denied",
    )
    allowed_domains: list[PluginDomain] = Field(
        default_factory=list,
        description="Domains the plugin is permitted to access",
    )
    max_resource_usage: dict[str, Any] = Field(
        default_factory=dict,
        description="Maximum resource usage limits",
    )
    network_access: bool = Field(
        default=False,
        description="Whether network access is allowed",
    )
    filesystem_access: bool = Field(
        default=False,
        description="Whether filesystem access is allowed",
    )
    enabled: bool = Field(
        default=True,
        description="Whether this policy is active",
    )
    version: int = Field(
        default=1,
        ge=1,
        description="Policy version number",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the policy was created",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the policy was last updated",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional policy metadata",
    )


# ─────────────────────────────────────────────────────────────────────────────
# PluginDecision
# ─────────────────────────────────────────────────────────────────────────────


class PluginDecision(BaseModel):
    """The outcome of a plugin lifecycle decision.

    Tracks decisions made about a plugin — installation approval,
    activation, suspension, removal, or capability access grant.

    Enhanced in Phase 3 with operation, allowed, compatibility_result,
    dependency_result, sandbox_result, security_result, and confidence.
    Enhanced in Phase 3.5 with lifecycle_result and reasoning.
    """

    decision_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique decision identifier",
    )
    plugin_id: UUID4 = Field(
        description="The plugin this decision relates to",
    )
    operation: str = Field(
        default="",
        description="The operation that prompted this decision",
    )
    allowed: bool = Field(
        default=True,
        description="Whether the operation was allowed",
    )
    decision: str = Field(
        default="",
        description="The decision outcome (approve, deny, defer)",
    )
    reason: str = Field(
        default="",
        description="Human-readable reason for the decision",
    )
    compatibility_result: str = Field(
        default="",
        description="Summary of compatibility check result",
    )
    dependency_result: str = Field(
        default="",
        description="Summary of dependency resolution result",
    )
    sandbox_result: str = Field(
        default="",
        description="Summary of sandbox creation result",
    )
    security_result: str = Field(
        default="",
        description="Summary of security policy check result",
    )
    lifecycle_result: str = Field(
        default="",
        description="Summary of lifecycle transition result",
    )
    reasoning: list[str] = Field(
        default_factory=list,
        description="Step-by-step reasoning that led to this decision",
    )
    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Overall confidence score for this decision",
    )
    decided_by: str = Field(
        default="",
        description="The user or system that made the decision",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the decision was made",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional decision metadata",
    )


# ─────────────────────────────────────────────────────────────────────────────
# PluginHealth
# ─────────────────────────────────────────────────────────────────────────────


class PluginHealth(BaseModel):
    """Health status of the plugin platform.

    Tracks overall and per-component health for monitoring and
    observability of the plugin manager and all installed plugins.

    Enhanced in Phase 3.5 with discovery_status, validation_status,
    dependency_resolver_status, average_load_time, error_rate,
    and active_plugins.
    """

    overall_status: str = Field(
        default="UNKNOWN",
        description="Overall health: HEALTHY, DEGRADED, UNHEALTHY, UNKNOWN",
    )
    plugin_id: UUID4 = Field(
        description="The plugin this health record belongs to",
    )
    plugin_name: str = Field(
        default="",
        description="The plugin name",
    )
    status: str = Field(
        default="",
        description="Plugin lifecycle status string",
    )
    discovery_status: str = Field(
        default="UNKNOWN",
        description="PluginDiscoverer health",
    )
    validation_status: str = Field(
        default="UNKNOWN",
        description="PluginValidator health",
    )
    loader_status: str = Field(
        default="UNKNOWN",
        description="PluginLoader health",
    )
    dependency_resolver_status: str = Field(
        default="UNKNOWN",
        description="DependencyResolver health",
    )
    sandbox_status: str = Field(
        default="UNKNOWN",
        description="SandboxManager health",
    )
    compatibility_status: str = Field(
        default="UNKNOWN",
        description="PluginCompatibilityManager health",
    )
    lifecycle_status: str = Field(
        default="UNKNOWN",
        description="PluginLifecycleManager health",
    )
    capability_status: str = Field(
        default="UNKNOWN",
        description="CapabilityDiscoverer health",
    )
    uptime_seconds: float = Field(
        default=0.0,
        ge=0.0,
        description="Uptime in seconds since last load",
    )
    error_count: int = Field(
        default=0,
        ge=0,
        description="Total number of errors encountered",
    )
    error_rate: float = Field(
        default=0.0,
        ge=0.0,
        description="Error rate (errors per execution)",
    )
    total_executions: int = Field(
        default=0,
        ge=0,
        description="Total number of executions",
    )
    average_load_time_ms: float = Field(
        default=0.0,
        ge=0.0,
        description="Average plugin load time in milliseconds",
    )
    active_plugins: int = Field(
        default=0,
        ge=0,
        description="Number of currently active plugins",
    )
    last_checked_at: str = Field(
        default_factory=lambda: datetime.now(UTC).isoformat(),
        description="When the health check was last performed",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional health metadata",
    )

    def is_healthy(self) -> bool:
        """Return True if overall status is HEALTHY."""
        return self.overall_status == "HEALTHY"


# ─────────────────────────────────────────────────────────────────────────────
# PluginMetrics
# ─────────────────────────────────────────────────────────────────────────────


class PluginMetrics(BaseModel):
    """Aggregated metrics snapshot for the plugin platform.

    Provides a point-in-time view of key operational metrics for
    monitoring and observability of plugin usage.

    Enhanced in Phase 3.5 with lifecycle_transitions, domain_usage,
    plugin_types, and load_latency fields.
    """

    plugin_id: UUID4 = Field(
        description="The plugin these metrics belong to",
    )
    plugin_name: str = Field(
        default="",
        description="The plugin name",
    )
    plugins_total: int = Field(
        default=0,
        ge=0,
        description="Total registered plugins",
    )
    active_plugins: int = Field(
        default=0,
        ge=0,
        description="Currently active plugins",
    )
    executions_total: int = Field(
        default=0,
        ge=0,
        description="Total execution count",
    )
    executions_success: int = Field(
        default=0,
        ge=0,
        description="Successful execution count",
    )
    executions_failed: int = Field(
        default=0,
        ge=0,
        description="Failed execution count",
    )
    average_execution_time_ms: float = Field(
        default=0.0,
        ge=0.0,
        description="Average execution time in milliseconds",
    )
    errors_total: int = Field(
        default=0,
        ge=0,
        description="Total errors since install",
    )
    cache_hits: int = Field(
        default=0,
        ge=0,
        description="Total cache hits",
    )
    cache_misses: int = Field(
        default=0,
        ge=0,
        description="Total cache misses",
    )
    compatibility_failures: int = Field(
        default=0,
        ge=0,
        description="Total compatibility check failures",
    )
    dependency_failures: int = Field(
        default=0,
        ge=0,
        description="Total dependency resolution failures",
    )
    lifecycle_transitions: int = Field(
        default=0,
        ge=0,
        description="Total lifecycle transitions",
    )
    sandbox_count: int = Field(
        default=0,
        ge=0,
        description="Total active sandboxes",
    )
    discoveries_total: int = Field(
        default=0,
        ge=0,
        description="Total plugin discoveries",
    )
    load_latency_ms: float = Field(
        default=0.0,
        ge=0.0,
        description="Average load latency in milliseconds",
    )
    domain_usage: dict[str, int] = Field(
        default_factory=dict,
        description="Plugin counts per domain",
    )
    plugin_types: dict[str, int] = Field(
        default_factory=dict,
        description="Plugin counts per type",
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.now(UTC).isoformat(),
        description="When the metrics snapshot was taken",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metrics metadata",
    )


# ─────────────────────────────────────────────────────────────────────────────
# PluginSession
# ─────────────────────────────────────────────────────────────────────────────


class PluginSession(BaseModel):
    """A plugin execution session.

    Tracks a single invocation or interaction with a plugin —
    who triggered it, which capabilities were used, timing,
    and outcome.

    Enhanced in Phase 3 with operation, dependency_summary,
    sandbox_id, lifecycle_state, and statistics fields.
    """

    session_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique session identifier",
    )
    plugin_id: UUID4 = Field(
        description="The plugin being executed",
    )
    capability_id: UUID4 | None = Field(
        default=None,
        description="The capability being invoked (if applicable)",
    )
    user_id: str = Field(
        default="",
        description="The user or system that initiated the session",
    )
    correlation_id: str = Field(
        default="",
        description="Correlation ID for distributed tracing",
    )
    operation: str = Field(
        default="",
        description="The operation being performed (discover, install, load, activate, etc.)",
    )
    dependency_summary: str = Field(
        default="",
        description="Summary of dependency resolution outcome",
    )
    sandbox_id: str = Field(
        default="",
        description="Sandbox ID assigned to this session",
    )
    lifecycle_state: str = Field(
        default="",
        description="Current lifecycle state during the session",
    )
    inputs: dict[str, Any] = Field(
        default_factory=dict,
        description="Session input data",
    )
    outputs: dict[str, Any] = Field(
        default_factory=dict,
        description="Session output data",
    )
    statistics: dict[str, Any] = Field(
        default_factory=dict,
        description="Session statistics (timing, counts, etc.)",
    )
    status: str = Field(
        default="PENDING",
        description="Session status (PENDING, RUNNING, COMPLETED, FAILED)",
    )
    error_message: str = Field(
        default="",
        description="Error details if session failed",
    )
    started_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the session started",
    )
    completed_at: datetime | None = Field(
        default=None,
        description="When the session completed",
    )
    duration_ms: float = Field(
        default=0.0,
        ge=0.0,
        description="Total session duration in milliseconds",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional session metadata",
    )


# ─────────────────────────────────────────────────────────────────────────────
# PluginConfidence
# ─────────────────────────────────────────────────────────────────────────────


class PluginConfidence(BaseModel):
    """Confidence assessment for a plugin operation.

    Evaluates manifest quality, dependency completeness,
    compatibility score, sandbox readiness, lifecycle validity,
    configuration quality, and signature status.
    Placeholder implementation.
    """

    overall_confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Overall confidence score (0.0 — 1.0)",
    )
    manifest_quality: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Quality score for the plugin manifest",
    )
    dependency_completeness: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Score for dependency resolution completeness",
    )
    compatibility_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Score for platform/version compatibility",
    )
    sandbox_readiness: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Score for sandbox readiness and isolation",
    )
    lifecycle_validity: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Score for lifecycle state validity",
    )
    configuration_quality: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Score for configuration completeness",
    )
    signature_status: str = Field(
        default="unknown",
        description="Signature verification status: verified, unverified, unknown, not_signed",
    )
    calculated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the confidence was calculated",
    )


# ─────────────────────────────────────────────────────────────────────────────
# PluginExplainabilityMetadata
# ─────────────────────────────────────────────────────────────────────────────


class PluginExplainabilityMetadata(BaseModel):
    """Explainability metadata for plugin lifecycle decisions.

    Stores human-readable reasons for why the plugin platform
    made specific decisions about loading, rejecting, dependency
    resolution, sandbox creation, capability registration,
    and dependency selection.

    Enhanced in Phase 3.5 with why_dependency_selected.
    """

    why_plugin_loaded: str = Field(
        default="",
        description="Why the plugin was loaded (validation, dependency, policy)",
    )
    why_plugin_rejected: str = Field(
        default="",
        description="Why the plugin was rejected (validation failure, policy violation)",
    )
    why_dependency_selected: str = Field(
        default="",
        description="Why a specific dependency was selected (compatibility, version, priority)",
    )
    why_dependency_failed: str = Field(
        default="",
        description="Why dependency resolution failed (missing, incompatible, cycle)",
    )
    why_sandbox_created: str = Field(
        default="",
        description="Why a sandbox was created or re-used for this plugin",
    )
    why_capability_registered: str = Field(
        default="",
        description="Why capabilities were registered or skipped",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When this explainability metadata was recorded",
    )
