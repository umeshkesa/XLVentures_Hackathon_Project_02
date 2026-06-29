"""PluginInitializer — prepares a plugin for activation.

Handles configuration loading, namespace preparation, resource
allocation, and lifecycle transition for the initialisation stage.

Deterministic placeholder — no actual initialisation or execution.
"""

from __future__ import annotations

import structlog

from adip.plugins.contracts.models import Plugin, PluginConfiguration
from adip.plugins.enums import PluginLifecycleStatus
from adip.plugins.execution.models import InitializationResult

log = structlog.get_logger(__name__)


class PluginInitializer:
    """Prepares a plugin for activation after loading.

    The initialisation pipeline:
      1. Load configuration
      2. Prepare namespace
      3. Allocate resources
      4. Transition lifecycle to INITIALIZED
    """

    def initialize(self, plugin: Plugin, config: PluginConfiguration | None = None) -> InitializationResult:
        """Execute the plugin initialisation pipeline.

        Returns an InitializationResult tracking each stage outcome.
        """
        log.info("plugin_initializer.initialize.start", plugin=plugin.name)

        errors: list[str] = []

        config_ok, config_errors = self.load_configuration(plugin, config)
        errors.extend(config_errors)

        namespace_ok, namespace_errors = self.prepare_namespace(plugin)
        errors.extend(namespace_errors)

        resources_ok, resource_errors = self.allocate_resources(plugin)
        errors.extend(resource_errors)

        lifecycle_ok = True
        if config_ok and namespace_ok and resources_ok:
            lifecycle_ok = True
        else:
            lifecycle_ok = False

        success = config_ok and namespace_ok and resources_ok and lifecycle_ok

        log.info(
            "plugin_initializer.initialize.complete",
            plugin=plugin.name,
            success=success,
            error_count=len(errors),
        )

        return InitializationResult(
            plugin_id=plugin.plugin_id,
            config_loaded=config_ok,
            namespace_prepared=namespace_ok,
            resources_allocated=resources_ok,
            lifecycle_transitioned=lifecycle_ok,
            success=success,
            errors=errors,
        )

    def load_configuration(self, plugin: Plugin, config: PluginConfiguration | None = None) -> tuple[bool, list[str]]:
        """Load and validate plugin configuration.

        Placeholder — validates configuration if provided.
        """
        errors: list[str] = []

        log.info("plugin_initializer.load_configuration", plugin=plugin.name)

        if config is not None:
            if config.version < 1:
                errors.append(f"Configuration version must be >= 1, got {config.version}")

        return (len(errors) == 0, errors)

    def prepare_namespace(self, plugin: Plugin) -> tuple[bool, list[str]]:
        """Prepare the plugin namespace.

        Placeholder — always succeeds.
        """
        log.info("plugin_initializer.prepare_namespace", plugin=plugin.name, namespace=plugin.namespace)
        return (True, [])

    def allocate_resources(self, plugin: Plugin) -> tuple[bool, list[str]]:
        """Allocate resources for the plugin.

        Placeholder — always succeeds.
        """
        log.info("plugin_initializer.allocate_resources", plugin=plugin.name)
        return (True, [])

    def validate_initialization_readiness(self, plugin: Plugin) -> list[str]:
        """Validate that a plugin is ready for initialisation.

        Checks that the plugin has all required fields populated.
        """
        violations: list[str] = []

        if not plugin.name.strip():
            violations.append("Plugin name is required for initialisation")

        if not plugin.version.strip():
            violations.append("Plugin version is required for initialisation")

        if plugin.status != PluginLifecycleStatus.LOADED:
            violations.append(
                f"Plugin must be in LOADED status for initialisation, "
                f"got {plugin.status.value}"
            )

        return violations
