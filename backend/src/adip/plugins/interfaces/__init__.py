"""Abstract interfaces for the Plugin Manager.

All interfaces follow dependency inversion — consumers depend on
abstractions, not concrete implementations.

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

PluginService is the enterprise facade for external callers.
PluginManager is the internal orchestrator.
PluginCoordinator coordinates all sub-components.
"""

from __future__ import annotations

import abc

from adip.plugins.contracts.models import (
    Plugin,
    PluginCapability,
    PluginConfiguration,
    PluginDecision,
    PluginHealth,
    PluginManifest,
    PluginMetrics,
    PluginSandbox,
    PluginSession,
)
from adip.plugins.enums import PluginDomain, PluginLifecycleStatus, PluginType

# ─────────────────────────────────────────────────────────────────────────────
# PluginService — enterprise facade (ONLY public API)
# ─────────────────────────────────────────────────────────────────────────────


class PluginService(abc.ABC):
    """Enterprise facade for plugin operations.

    Provides validation, authorisation, audit, and observability
    wrapping around the PluginManager. External modules interact
    with this facade rather than with PluginManager directly.
    """

    @abc.abstractmethod
    async def discover_plugin(self, source: str) -> Plugin:
        """Discover a new plugin from a source path or identifier."""
        ...

    @abc.abstractmethod
    async def install_plugin(self, plugin: Plugin) -> Plugin:
        """Validate, authorise, and install a new plugin."""
        ...

    @abc.abstractmethod
    async def get_plugin(self, plugin_id: str) -> Plugin | None:
        """Retrieve a plugin by its identifier."""
        ...

    @abc.abstractmethod
    async def update_plugin(self, plugin: Plugin) -> Plugin:
        """Update an existing plugin with authorisation."""
        ...

    @abc.abstractmethod
    async def uninstall_plugin(self, plugin_id: str) -> bool:
        """Uninstall and remove a plugin."""
        ...

    @abc.abstractmethod
    async def list_plugins(
        self,
        domain: PluginDomain | None = None,
        plugin_type: PluginType | None = None,
        status: PluginLifecycleStatus | None = None,
    ) -> list[Plugin]:
        """List plugins matching the given filters."""
        ...

    @abc.abstractmethod
    async def activate_plugin(self, plugin_id: str) -> Plugin:
        """Activate a plugin (transition to ACTIVE status)."""
        ...

    @abc.abstractmethod
    async def suspend_plugin(self, plugin_id: str, reason: str = "") -> Plugin:
        """Suspend a plugin."""
        ...

    @abc.abstractmethod
    async def load_plugin(self, plugin_id: str) -> Plugin:
        """Load a plugin into memory."""
        ...

    @abc.abstractmethod
    async def unload_plugin(self, plugin_id: str) -> Plugin:
        """Unload a plugin from memory."""
        ...

    @abc.abstractmethod
    async def create_sandbox(self, plugin_id: str, config: dict | None = None) -> PluginSandbox:
        """Create an execution sandbox for a plugin."""
        ...

    @abc.abstractmethod
    async def destroy_sandbox(self, sandbox_id: str) -> bool:
        """Destroy an execution sandbox."""
        ...

    @abc.abstractmethod
    async def get_sandbox(self, sandbox_id: str) -> PluginSandbox | None:
        """Retrieve a sandbox by its identifier."""
        ...

    @abc.abstractmethod
    async def health(self) -> PluginHealth:
        """Return the current health status of the plugin platform."""
        ...

    @abc.abstractmethod
    async def get_metrics(self) -> PluginMetrics:
        """Return aggregated plugin platform metrics."""
        ...


# ─────────────────────────────────────────────────────────────────────────────
# PluginManager — internal orchestrator
# ─────────────────────────────────────────────────────────────────────────────


class PluginManager(abc.ABC):
    """Internal orchestrator for all plugin operations.

    Every ADIP module that needs plugin operations goes through
    this interface. The PluginManager:
      1. Validates the operation
      2. Delegates to PluginCoordinator for orchestration
      3. Records events for audit and observability
    """

    @abc.abstractmethod
    async def install_plugin(self, plugin: Plugin) -> Plugin:
        """Install a new plugin."""
        ...

    @abc.abstractmethod
    async def read_plugin(self, plugin_id: str) -> Plugin | None:
        """Retrieve a plugin by ID."""
        ...

    @abc.abstractmethod
    async def update_plugin(self, plugin: Plugin) -> Plugin:
        """Update an existing plugin."""
        ...

    @abc.abstractmethod
    async def uninstall_plugin(self, plugin_id: str) -> bool:
        """Uninstall and remove a plugin."""
        ...

    @abc.abstractmethod
    async def list_plugins(
        self,
        domain: PluginDomain | None = None,
        plugin_type: PluginType | None = None,
        status: PluginLifecycleStatus | None = None,
    ) -> list[Plugin]:
        """List plugins matching the given filters."""
        ...

    @abc.abstractmethod
    async def activate_plugin(self, plugin_id: str) -> Plugin:
        """Activate a plugin (transition to ACTIVE status)."""
        ...

    @abc.abstractmethod
    async def suspend_plugin(self, plugin_id: str, reason: str = "") -> Plugin:
        """Suspend a plugin."""
        ...

    @abc.abstractmethod
    async def load_plugin(self, plugin_id: str) -> Plugin:
        """Load a plugin into memory."""
        ...

    @abc.abstractmethod
    async def unload_plugin(self, plugin_id: str) -> Plugin:
        """Unload a plugin from memory."""
        ...

    @abc.abstractmethod
    async def create_sandbox(self, plugin_id: str, config: dict | None = None) -> PluginSandbox:
        """Create an execution sandbox for a plugin."""
        ...

    @abc.abstractmethod
    async def destroy_sandbox(self, sandbox_id: str) -> bool:
        """Destroy an execution sandbox."""
        ...

    @abc.abstractmethod
    async def get_sandbox(self, sandbox_id: str) -> PluginSandbox | None:
        """Retrieve a sandbox by ID."""
        ...

    @abc.abstractmethod
    async def discover_plugin(self, source: str) -> Plugin:
        """Discover a new plugin from a source."""
        ...

    @abc.abstractmethod
    async def get_health(self) -> PluginHealth:
        """Return the current health status."""
        ...

    @abc.abstractmethod
    async def get_metrics(self) -> PluginMetrics:
        """Return aggregated metrics."""
        ...


# ─────────────────────────────────────────────────────────────────────────────
# PluginCoordinator — sub-component orchestrator
# ─────────────────────────────────────────────────────────────────────────────


class PluginCoordinator(abc.ABC):
    """Sub-component orchestrator for plugin operations.

    Coordinates PluginLoader, PluginValidator, DependencyResolver,
    CapabilityDiscoverer, LifecycleManager, VersionManager,
    SandboxManager, and PluginHealthChecker.

    Contains orchestration only — no business logic.
    """

    @abc.abstractmethod
    async def install_plugin(self, plugin: Plugin) -> Plugin:
        """Orchestrate the full plugin installation pipeline."""
        ...

    @abc.abstractmethod
    async def get_plugin(self, plugin_id: str) -> Plugin | None:
        """Retrieve a plugin by ID."""
        ...

    @abc.abstractmethod
    async def update_plugin(self, plugin: Plugin) -> Plugin:
        """Update an existing plugin."""
        ...

    @abc.abstractmethod
    async def uninstall_plugin(self, plugin_id: str) -> bool:
        """Uninstall and remove a plugin."""
        ...

    @abc.abstractmethod
    async def list_plugins(
        self,
        domain: PluginDomain | None = None,
        plugin_type: PluginType | None = None,
        status: PluginLifecycleStatus | None = None,
    ) -> list[Plugin]:
        """List plugins matching the given filters."""
        ...

    @abc.abstractmethod
    async def activate_plugin(self, plugin_id: str) -> Plugin:
        """Activate a plugin."""
        ...

    @abc.abstractmethod
    async def suspend_plugin(self, plugin_id: str, reason: str = "") -> Plugin:
        """Suspend a plugin."""
        ...

    @abc.abstractmethod
    async def load_plugin(self, plugin_id: str) -> Plugin:
        """Load a plugin into memory."""
        ...

    @abc.abstractmethod
    async def unload_plugin(self, plugin_id: str) -> Plugin:
        """Unload a plugin from memory."""
        ...

    @abc.abstractmethod
    async def discover_plugin(self, source: str) -> Plugin:
        """Discover a new plugin from a source."""
        ...

    @abc.abstractmethod
    async def create_sandbox(self, plugin_id: str, config: dict | None = None) -> PluginSandbox:
        """Create an execution sandbox for a plugin."""
        ...

    @abc.abstractmethod
    async def destroy_sandbox(self, sandbox_id: str) -> bool:
        """Destroy an execution sandbox."""
        ...

    @abc.abstractmethod
    async def get_sandbox(self, sandbox_id: str) -> PluginSandbox | None:
        """Retrieve a sandbox by ID."""
        ...

    @abc.abstractmethod
    async def health(self) -> PluginHealth:
        """Return health status of all sub-components."""
        ...

    @abc.abstractmethod
    async def metrics(self) -> PluginMetrics:
        """Return aggregated metrics from all sub-components."""
        ...


# ─────────────────────────────────────────────────────────────────────────────
# PluginLoader
# ─────────────────────────────────────────────────────────────────────────────


class PluginLoader(abc.ABC):
    """Loads plugins from various sources.

    Supports loading from filesystem paths, package references,
    registry URLs, and other discoverable sources.
    """

    @abc.abstractmethod
    async def load(self, source: str) -> Plugin:
        """Load a plugin from the given source."""
        ...

    @abc.abstractmethod
    async def load_from_module(self, module_name: str) -> Plugin:
        """Load a plugin from a Python module."""
        ...

    @abc.abstractmethod
    async def get_supported_sources(self) -> list[str]:
        """Return the source types this loader supports."""
        ...


# ─────────────────────────────────────────────────────────────────────────────
# PluginValidator
# ─────────────────────────────────────────────────────────────────────────────


class PluginValidator(abc.ABC):
    """Validates plugin manifests, configurations, and dependencies.

    Ensures plugins are structurally valid, meet policy constraints,
    and are safe to install and execute.
    """

    @abc.abstractmethod
    async def validate_manifest(self, manifest: PluginManifest) -> list[str]:
        """Validate a plugin manifest. Returns list of violations."""
        ...

    @abc.abstractmethod
    async def validate_configuration(self, config: PluginConfiguration) -> list[str]:
        """Validate a plugin configuration. Returns list of violations."""
        ...

    @abc.abstractmethod
    async def validate_plugin(self, plugin: Plugin) -> list[str]:
        """Validate a complete plugin. Returns list of violations."""
        ...

    @abc.abstractmethod
    async def validate_sandbox(self, sandbox: PluginSandbox) -> list[str]:
        """Validate a sandbox configuration. Returns list of violations."""
        ...


# ─────────────────────────────────────────────────────────────────────────────
# DependencyResolver
# ─────────────────────────────────────────────────────────────────────────────


class DependencyResolver(abc.ABC):
    """Resolves plugin dependencies.

    Checks dependency graphs, validates version constraints,
    detects circular dependencies, and determines installability.
    """

    @abc.abstractmethod
    async def resolve(self, plugin: Plugin, available: list[Plugin]) -> list[str]:
        """Resolve dependencies for a plugin. Returns list of satisfied dependency IDs."""
        ...

    @abc.abstractmethod
    async def check_compatibility(
        self,
        plugin: Plugin,
        dependency: Plugin,
    ) -> bool:
        """Check if two plugins are compatible (version constraints, etc.)."""
        ...

    @abc.abstractmethod
    async def detect_circular_dependencies(self, plugin: Plugin, available: list[Plugin]) -> list[str]:
        """Detect circular dependencies involving the given plugin."""
        ...


# ─────────────────────────────────────────────────────────────────────────────
# CapabilityDiscoverer
# ─────────────────────────────────────────────────────────────────────────────


class CapabilityDiscoverer(abc.ABC):
    """Discovers and registers plugin capabilities.

    Examines plugin manifests and runtime introspection to
    discover available capabilities and make them available
    to other ADIP components.
    """

    @abc.abstractmethod
    async def discover_capabilities(self, plugin: Plugin) -> list[PluginCapability]:
        """Discover all capabilities provided by a plugin."""
        ...

    @abc.abstractmethod
    async def get_capability(self, capability_id: str) -> PluginCapability | None:
        """Retrieve a registered capability by ID."""
        ...

    @abc.abstractmethod
    async def list_capabilities(
        self,
        category: str | None = None,
        plugin_id: str | None = None,
    ) -> list[PluginCapability]:
        """List registered capabilities, optionally filtered."""
        ...


# ─────────────────────────────────────────────────────────────────────────────
# LifecycleManager
# ─────────────────────────────────────────────────────────────────────────────


class LifecycleManager(abc.ABC):
    """Manages plugin lifecycle transitions.

    Enforces the allowed state machine transitions and records
    lifecycle history for audit and observability.
    """

    @abc.abstractmethod
    async def transition(
        self,
        plugin: Plugin,
        target_status: PluginLifecycleStatus,
        reason: str = "",
    ) -> Plugin:
        """Transition a plugin to a new lifecycle status."""
        ...

    @abc.abstractmethod
    async def get_current_status(self, plugin: Plugin) -> PluginLifecycleStatus:
        """Return the current lifecycle status of a plugin."""
        ...

    @abc.abstractmethod
    async def is_transition_allowed(
        self,
        current: PluginLifecycleStatus,
        target: PluginLifecycleStatus,
    ) -> bool:
        """Check if a lifecycle transition is allowed."""
        ...

    @abc.abstractmethod
    async def get_transition_history(self, plugin_id: str) -> list[dict[str, str]]:
        """Return the lifecycle transition history for a plugin."""
        ...


# ─────────────────────────────────────────────────────────────────────────────
# VersionManager
# ─────────────────────────────────────────────────────────────────────────────


class VersionManager(abc.ABC):
    """Manages plugin versions and compatibility checking.

    Tracks version history, supports semantic version comparison,
    and validates version constraints for dependency resolution.
    """

    @abc.abstractmethod
    async def register_version(self, plugin: Plugin) -> bool:
        """Register a new version of a plugin."""
        ...

    @abc.abstractmethod
    async def get_latest_version(self, plugin_id: str) -> str:
        """Return the latest version of a plugin."""
        ...

    @abc.abstractmethod
    async def list_versions(self, plugin_id: str) -> list[str]:
        """List all registered versions of a plugin."""
        ...

    @abc.abstractmethod
    async def satisfies_constraint(self, version: str, constraint: str) -> bool:
        """Check if a version satisfies a semver constraint."""
        ...


# ─────────────────────────────────────────────────────────────────────────────
# SandboxManager
# ─────────────────────────────────────────────────────────────────────────────


class SandboxManager(abc.ABC):
    """Manages plugin sandbox lifecycle.

    Creates, configures, monitors, and destroys execution sandboxes
    for plugins. Each sandbox provides logical isolation for its
    plugin's runtime.
    """

    @abc.abstractmethod
    async def create_sandbox(self, plugin: Plugin, config: dict | None = None) -> PluginSandbox:
        """Create a sandbox for a plugin."""
        ...

    @abc.abstractmethod
    async def destroy_sandbox(self, sandbox_id: str) -> bool:
        """Destroy an existing sandbox."""
        ...

    @abc.abstractmethod
    async def get_sandbox(self, sandbox_id: str) -> PluginSandbox | None:
        """Retrieve a sandbox by ID."""
        ...

    @abc.abstractmethod
    async def get_sandbox_by_plugin(self, plugin_id: str) -> PluginSandbox | None:
        """Retrieve the sandbox for a given plugin."""
        ...

    @abc.abstractmethod
    async def list_sandboxes(self) -> list[PluginSandbox]:
        """List all active sandboxes."""
        ...


# ─────────────────────────────────────────────────────────────────────────────
# PluginHealthChecker
# ─────────────────────────────────────────────────────────────────────────────


class PluginHealthChecker(abc.ABC):
    """Monitors and reports plugin health.

    Periodically checks plugin status, validates sandbox integrity,
    and reports health metrics for monitoring and alerting.
    """

    @abc.abstractmethod
    async def check_health(self, plugin: Plugin) -> PluginHealth:
        """Perform a health check on a plugin."""
        ...

    @abc.abstractmethod
    async def check_all(self) -> list[PluginHealth]:
        """Perform health checks on all registered plugins."""
        ...

    @abc.abstractmethod
    async def get_health_summary(self) -> dict[str, Any]:
        """Return a summary of all plugin health statuses."""
        ...


# Type alias for Any to avoid import issues at the interface level
from typing import Any  # noqa: F811, E402
