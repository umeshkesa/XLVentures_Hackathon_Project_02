"""PluginSandboxManager — manages plugin sandbox lifecycle.

Supports sandbox creation, validation, namespace isolation,
resource limits, and permissions management.

Deterministic placeholder — no actual sandbox isolation.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import structlog

from adip.plugins.contracts.models import Plugin, PluginSandbox
from adip.plugins.enums import PluginDomain

log = structlog.get_logger(__name__)


class PluginSandboxManager:
    """Manages plugin sandbox creation, validation, and lifecycle.

    Each sandbox provides logical isolation for its plugin with
    configurable resource limits, permissions, and isolation policy.
    """

    def __init__(self) -> None:
        self._sandboxes: dict[str, PluginSandbox] = {}

    def create_sandbox(self, plugin: Plugin, config: dict | None = None) -> PluginSandbox:
        """Create a sandbox for a plugin.

        Generates namespace strings based on the plugin name and
        applies default resource limits and permissions.
        """
        plugin_id_str = str(plugin.plugin_id)
        log.info("sandbox_manager.create_sandbox", plugin=plugin.name, id=plugin_id_str)

        for sandbox in self._sandboxes.values():
            if str(sandbox.plugin_id) == plugin_id_str:
                log.warning(
                    "sandbox_manager.sandbox_exists",
                    plugin=plugin.name,
                    sandbox_id=str(sandbox.sandbox_id),
                )
                return sandbox

        sandbox = PluginSandbox(
            plugin_id=plugin.plugin_id,
            namespace=plugin.namespace,
            domain=plugin.domain,
            configuration=config or {},
            memory_namespace=f"memory_{plugin.name}",
            knowledge_namespace=f"knowledge_{plugin.name}",
            rule_namespace=f"rule_{plugin.name}",
            action_namespace=f"action_{plugin.name}",
            capability_namespace=f"capability_{plugin.name}",
            resource_limits=self._default_resource_limits(),
            permissions=self._default_permissions(plugin.domain),
            isolation_policy="strict",
        )

        sandbox_id_str = str(sandbox.sandbox_id)
        self._sandboxes[sandbox_id_str] = sandbox
        log.info("sandbox_manager.sandbox_created", plugin=plugin.name, sandbox_id=sandbox_id_str)
        return sandbox

    def destroy_sandbox(self, sandbox_id: str) -> bool:
        """Destroy an existing sandbox.

        Removes the sandbox from the managed store.
        """
        log.info("sandbox_manager.destroy_sandbox", sandbox_id=sandbox_id)

        if sandbox_id not in self._sandboxes:
            return False

        del self._sandboxes[sandbox_id]
        return True

    def get_sandbox(self, sandbox_id: str) -> PluginSandbox | None:
        """Retrieve a sandbox by its identifier."""
        return self._sandboxes.get(sandbox_id)

    def get_sandbox_by_plugin(self, plugin_id: str) -> PluginSandbox | None:
        """Retrieve the sandbox for a given plugin ID."""
        for sandbox in self._sandboxes.values():
            if str(sandbox.plugin_id) == plugin_id:
                return sandbox
        return None

    def list_sandboxes(self) -> list[PluginSandbox]:
        """List all active sandboxes."""
        return list(self._sandboxes.values())

    def validate_sandbox(self, sandbox: PluginSandbox) -> list[str]:
        """Validate a sandbox configuration.

        Checks required fields and constraint compliance.
        """
        violations: list[str] = []

        if sandbox.isolation_policy not in ("strict", "moderate", "permissive"):
            violations.append(
                f"Invalid isolation policy: {sandbox.isolation_policy}"
            )

        if not sandbox.namespace.strip():
            violations.append("Sandbox namespace is required")

        return violations

    def update_resource_limits(self, sandbox_id: str, limits: dict[str, Any]) -> bool:
        """Update resource limits for a sandbox.

        Placeholder — updates the resource_limits dictionary.
        """
        sandbox = self._sandboxes.get(sandbox_id)
        if sandbox is None:
            return False

        sandbox.resource_limits.update(limits)
        sandbox.updated_at = datetime.now(UTC)
        return True

    def update_permissions(self, sandbox_id: str, permissions: list[str]) -> bool:
        """Update permissions for a sandbox."""
        sandbox = self._sandboxes.get(sandbox_id)
        if sandbox is None:
            return False

        sandbox.permissions = list(permissions)
        sandbox.updated_at = datetime.now(UTC)
        return True

    def count(self) -> int:
        """Return the number of active sandboxes."""
        return len(self._sandboxes)

    def clear(self) -> int:
        """Clear all sandboxes. Returns the number cleared."""
        count = len(self._sandboxes)
        self._sandboxes.clear()
        return count

    def _default_resource_limits(self) -> dict[str, Any]:
        """Return default resource limits for a sandbox."""
        return {
            "cpu_max_percent": 50.0,
            "memory_max_mb": 256.0,
            "storage_max_mb": 1024.0,
            "network_max_bytes": 10485760,
            "timeout_seconds": 30.0,
            "max_agents": 5,
            "max_tools": 10,
        }

    def _default_permissions(self, domain: PluginDomain) -> list[str]:
        """Return default permissions for a domain."""
        base = ["self.read", "self.write"]
        if domain == PluginDomain.SYSTEM:
            return base + ["system.read", "system.admin"]
        return base



