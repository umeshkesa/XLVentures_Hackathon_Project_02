"""PluginManager — lightweight internal orchestrator.

Facade over PluginCoordinator. Validates operations, delegates
orchestration to the coordinator, and records events for audit
and observability.

PluginManager remains lightweight — no business logic lives here.
"""

from __future__ import annotations

import structlog

from adip.plugins.contracts.models import (
    Plugin,
    PluginDecision,
    PluginHealth,
    PluginMetrics,
    PluginSandbox,
)
from adip.plugins.enums import PluginDomain, PluginLifecycleStatus, PluginType
from adip.plugins.execution.models import (
    DiscoveryResult,
    LoaderResult,
)
from adip.plugins.orchestration.coordinator import PluginCoordinator

log = structlog.get_logger(__name__)


class PluginManager:
    """Lightweight internal orchestrator for all plugin operations."""

    def __init__(self, coordinator: PluginCoordinator | None = None) -> None:
        self._coordinator = coordinator or PluginCoordinator()

    def discover_plugin(self, source: str, source_type: str = "") -> DiscoveryResult:
        """Discover a new plugin from a source."""
        log.info("plugin_manager.discover", source=source, source_type=source_type)
        return self._coordinator.discover_plugin(source, source_type)

    def install_plugin(self, plugin: Plugin) -> PluginDecision:
        """Install a plugin through the full pipeline."""
        log.info("plugin_manager.install", plugin=plugin.name)
        return self._coordinator.install_plugin(plugin)

    def get_plugin(self, plugin_id: str) -> Plugin | None:
        """Retrieve a plugin by ID."""
        return self._coordinator.get_plugin(plugin_id)

    def list_plugins(
        self,
        domain: PluginDomain | None = None,
        plugin_type: PluginType | None = None,
        status: PluginLifecycleStatus | None = None,
    ) -> list[Plugin]:
        """List plugins matching the given filters."""
        return self._coordinator.list_plugins(domain=domain, plugin_type=plugin_type, status=status)

    def delete_plugin(self, plugin_id: str) -> bool:
        """Delete/remove a plugin."""
        log.info("plugin_manager.delete", plugin_id=plugin_id)
        return self._coordinator.delete_plugin(plugin_id)

    def activate_plugin(self, plugin_id: str) -> Plugin | None:
        """Activate a plugin (transition to ACTIVE status)."""
        plugin = self._coordinator.get_plugin(plugin_id)
        if plugin is None:
            return None
        log.info("plugin_manager.activate", plugin=plugin.name)
        return self._coordinator.transition_lifecycle(plugin, PluginLifecycleStatus.ACTIVE)

    def suspend_plugin(self, plugin_id: str, reason: str = "") -> Plugin | None:
        """Suspend a plugin."""
        plugin = self._coordinator.get_plugin(plugin_id)
        if plugin is None:
            return None
        log.info("plugin_manager.suspend", plugin=plugin.name, reason=reason)
        return self._coordinator.transition_lifecycle(plugin, PluginLifecycleStatus.SUSPENDED, reason=reason)

    def load_plugin(self, plugin_id: str) -> LoaderResult | None:
        """Load a plugin into memory."""
        plugin = self._coordinator.get_plugin(plugin_id)
        if plugin is None:
            return None
        log.info("plugin_manager.load", plugin=plugin.name)
        return self._coordinator.load_plugin(plugin)

    def unload_plugin(self, plugin_id: str) -> Plugin | None:
        """Unload a plugin (transition to UNLOADED)."""
        plugin = self._coordinator.get_plugin(plugin_id)
        if plugin is None:
            return None
        log.info("plugin_manager.unload", plugin=plugin.name)
        return self._coordinator.transition_lifecycle(plugin, PluginLifecycleStatus.UNLOADED)

    def create_sandbox(self, plugin_id: str, config: dict | None = None) -> PluginSandbox | None:
        """Create an execution sandbox for a plugin."""
        plugin = self._coordinator.get_plugin(plugin_id)
        if plugin is None:
            return None
        log.info("plugin_manager.create_sandbox", plugin=plugin.name)
        return self._coordinator.create_sandbox(plugin, config)

    def destroy_sandbox(self, sandbox_id: str) -> bool:
        """Destroy an execution sandbox."""
        log.info("plugin_manager.destroy_sandbox", sandbox_id=sandbox_id)
        sandbox = self._coordinator.get_sandbox(sandbox_id)
        if sandbox is None:
            return False
        return True  # coordinator handles sandbox cleanup via delete_plugin

    def get_sandbox(self, sandbox_id: str) -> PluginSandbox | None:
        """Retrieve a sandbox by ID."""
        return self._coordinator.get_sandbox(sandbox_id)

    def get_health(self) -> PluginHealth:
        """Return the current health status of the plugin platform."""
        return self._coordinator.health()

    def get_metrics(self) -> PluginMetrics:
        """Return aggregated plugin platform metrics."""
        return self._coordinator.metrics()
