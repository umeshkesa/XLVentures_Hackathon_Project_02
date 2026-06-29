"""PluginValidator — validates plugin manifests, configurations,
namespaces, dependencies, capabilities, sandboxes, and lifecycle
transitions.

Deterministic placeholder — validates structural constraints
without external calls or execution.
"""

from __future__ import annotations

import structlog

from adip.plugins.contracts.models import (
    Plugin,
    PluginCapability,
    PluginConfiguration,
    PluginDependency,
    PluginManifest,
    PluginNamespace,
    PluginPolicy,
    PluginSandbox,
)
from adip.plugins.enums import PluginDomain, PluginLifecycleStatus, PluginType

log = structlog.get_logger(__name__)


class PluginValidator:
    """Validates plugin manifests, configurations, and lifecycle transitions.

    Returns lists of violation strings — empty list means valid.
    """

    MAX_PRIORITY: int = 1000

    def validate_manifest(self, manifest: PluginManifest) -> list[str]:
        """Validate a plugin manifest structure.

        Checks required fields, types, and basic constraints.
        """
        violations: list[str] = []

        log.info("plugin_validator.validate_manifest", name=manifest.plugin_name)

        if not manifest.plugin_name.strip():
            violations.append("Plugin name is required in manifest")

        if not manifest.plugin_version.strip():
            violations.append("Plugin version is required in manifest")

        if not isinstance(manifest.plugin_type, PluginType):
            violations.append(f"Unsupported plugin type: {manifest.plugin_type}")

        if not isinstance(manifest.plugin_domain, PluginDomain):
            violations.append(f"Unsupported plugin domain: {manifest.plugin_domain}")

        for i, dep in enumerate(manifest.dependencies):
            dep_violations = self._validate_dependency(dep)
            for v in dep_violations:
                violations.append(f"Dependency {i}: {v}")

        for i, cap in enumerate(manifest.capabilities):
            cap_violations = self._validate_capability(cap)
            for v in cap_violations:
                violations.append(f"Capability {i}: {v}")

        return violations

    def validate_configuration(self, config: PluginConfiguration) -> list[str]:
        """Validate a plugin configuration.

        Checks required fields and structural constraints.
        """
        violations: list[str] = []

        log.info("plugin_validator.validate_configuration", config_id=str(config.config_id))

        if config.version < 1:
            violations.append(f"Configuration version must be >= 1, got {config.version}")

        return violations

    def validate_namespace(self, namespace: PluginNamespace) -> list[str]:
        """Validate a plugin namespace.

        Checks required fields and namespace structure.
        """
        violations: list[str] = []

        log.info("plugin_validator.validate_namespace", name=namespace.name)

        if not namespace.name.strip():
            violations.append("Namespace name is required")

        return violations

    def validate_dependencies(self, dependencies: list[PluginDependency]) -> list[str]:
        """Validate plugin dependency declarations.

        Checks that each dependency has a name and valid constraint.
        """
        violations: list[str] = []

        log.info("plugin_validator.validate_dependencies", count=len(dependencies))

        for i, dep in enumerate(dependencies):
            dep_violations = self._validate_dependency(dep)
            for v in dep_violations:
                violations.append(f"Dependency {i}: {v}")

        return violations

    def validate_capabilities(self, capabilities: list[PluginCapability]) -> list[str]:
        """Validate plugin capability declarations.

        Checks that each capability has a name and category.
        """
        violations: list[str] = []

        log.info("plugin_validator.validate_capabilities", count=len(capabilities))

        for i, cap in enumerate(capabilities):
            cap_violations = self._validate_capability(cap)
            for v in cap_violations:
                violations.append(f"Capability {i}: {v}")

        return violations

    def validate_sandbox(self, sandbox: PluginSandbox) -> list[str]:
        """Validate a sandbox configuration.

        Checks required fields and isolation policy.
        """
        violations: list[str] = []

        log.info("plugin_validator.validate_sandbox", sandbox_id=str(sandbox.sandbox_id))

        if sandbox.isolation_policy not in ("strict", "moderate", "permissive"):
            violations.append(
                f"Invalid isolation policy: {sandbox.isolation_policy}. "
                "Must be strict, moderate, or permissive"
            )

        if not sandbox.namespace.strip():
            violations.append("Sandbox namespace is required")

        return violations

    def validate_plugin(self, plugin: Plugin) -> list[str]:
        """Validate a complete plugin.

        Runs all validators against the plugin and its components.
        """
        violations: list[str] = []

        log.info("plugin_validator.validate_plugin", name=plugin.name, id=str(plugin.plugin_id))

        if not plugin.name.strip():
            violations.append("Plugin name is required")

        if not plugin.version.strip():
            violations.append("Plugin version is required")

        if not isinstance(plugin.plugin_type, PluginType):
            violations.append(f"Unsupported plugin type: {plugin.plugin_type}")

        if not isinstance(plugin.domain, PluginDomain):
            violations.append(f"Unsupported plugin domain: {plugin.domain}")

        if not isinstance(plugin.status, PluginLifecycleStatus):
            violations.append(f"Unsupported lifecycle status: {plugin.status}")

        if plugin.manifest:
            violations.extend(self.validate_manifest(plugin.manifest))

        return violations

    def validate_lifecycle_transition(
        self,
        from_status: PluginLifecycleStatus,
        to_status: PluginLifecycleStatus,
    ) -> list[str]:
        """Validate a proposed lifecycle transition.

        Basic structural checks — core state machine is managed
        by LifecycleManager.
        """
        violations: list[str] = []

        if from_status == to_status:
            return violations

        if not isinstance(from_status, PluginLifecycleStatus):
            violations.append(f"Invalid source status: {from_status}")

        if not isinstance(to_status, PluginLifecycleStatus):
            violations.append(f"Invalid target status: {to_status}")

        return violations

    def validate_policy(self, policy: PluginPolicy) -> list[str]:
        """Validate a plugin policy structure."""
        violations: list[str] = []

        log.info("plugin_validator.validate_policy", name=policy.name)

        if not policy.name.strip():
            violations.append("Policy name is required")

        if policy.version < 1:
            violations.append(f"Policy version must be >= 1, got {policy.version}")

        return violations

    def _validate_dependency(self, dep: PluginDependency) -> list[str]:
        """Validate a single dependency declaration."""
        violations: list[str] = []

        if not dep.plugin_name.strip():
            violations.append("Dependency plugin_name is required")

        if not dep.version_constraint.strip():
            violations.append("Dependency version_constraint is required")

        return violations

    def _validate_capability(self, cap: PluginCapability) -> list[str]:
        """Validate a single capability declaration."""
        violations: list[str] = []

        if not cap.name.strip():
            violations.append("Capability name is required")

        if not cap.category.strip():
            violations.append("Capability category is required")

        return violations
