"""PluginPolicyEngine — enforces plugin management policies.

Validates installation policy, version policy, sandbox policy,
security policy, and dependency policy for plugin operations.

Deterministic placeholder — no real security enforcement.
"""

from __future__ import annotations

import uuid

import structlog

from adip.plugins.contracts.models import Plugin, PluginPolicy, PluginSandbox
from adip.plugins.enums import PluginDomain

log = structlog.get_logger(__name__)


class PluginPolicyEngine:
    """Enforces configurable policies for plugin operations."""

    def __init__(self, policy: PluginPolicy | None = None) -> None:
        self._policy: PluginPolicy = policy or PluginPolicy(plugin_id=uuid.uuid4())

    def set_policy(self, policy: PluginPolicy) -> None:
        """Set the active policy."""
        self._policy = policy
        log.info("policy_engine.set_policy", policy_id=str(policy.policy_id))

    def get_policy(self) -> PluginPolicy:
        """Return the current policy."""
        return self._policy

    def check_installation_policy(self, plugin: Plugin) -> list[str]:
        """Validate installation against policy constraints.

        Checks domain, type, and capability constraints.
        """
        violations: list[str] = []

        log.info("policy_engine.check_installation", plugin=plugin.name)

        if self._policy.allowed_domains:
            if plugin.domain not in self._policy.allowed_domains:
                violations.append(
                    f"Plugin domain {plugin.domain.value} is not in allowed domains: "
                    f"{[d.value for d in self._policy.allowed_domains]}"
                )

        if self._policy.allowed_capabilities and plugin.manifest:
            manifest_cap_names = {c.name for c in plugin.manifest.capabilities}
            allowed = set(self._policy.allowed_capabilities)
            denied = manifest_cap_names - allowed
            for cap in denied:
                violations.append(
                    f"Capability '{cap}' is not in the allowed list"
                )

        if self._policy.denied_capabilities and plugin.manifest:
            for cap in plugin.manifest.capabilities:
                if cap.name in self._policy.denied_capabilities:
                    violations.append(
                        f"Capability '{cap.name}' is explicitly denied by policy"
                    )

        return violations

    def check_version_policy(self, plugin: Plugin, new_version: str) -> list[str]:
        """Validate a version change against policy."""
        violations: list[str] = []

        log.info("policy_engine.check_version", plugin=plugin.name, new_version=new_version)

        if not new_version.strip():
            violations.append("New version string is empty")

        return violations

    def check_sandbox_policy(self, sandbox: PluginSandbox) -> list[str]:
        """Validate a sandbox against policy constraints."""
        violations: list[str] = []

        log.info("policy_engine.check_sandbox", sandbox_id=str(sandbox.sandbox_id))

        if sandbox.isolation_policy not in ("strict", "moderate", "permissive"):
            violations.append(
                f"Sandbox isolation policy '{sandbox.isolation_policy}' is not valid"
            )

        if self._policy.network_access is False and "network" in sandbox.permissions:
            violations.append("Network access is denied by policy but sandbox requests it")

        if self._policy.filesystem_access is False and "filesystem" in sandbox.permissions:
            violations.append("Filesystem access is denied by policy but sandbox requests it")

        return violations

    def check_security_policy(self, plugin: Plugin) -> list[str]:
        """Validate a plugin against security policy.

        Placeholder — returns empty violations.
        """
        violations: list[str] = []

        log.info("policy_engine.check_security", plugin=plugin.name)

        if plugin.domain == PluginDomain.SYSTEM and not plugin.owner_id:
            violations.append("System plugins must have an owner")

        return violations

    def check_dependency_policy(self, plugin: Plugin) -> list[str]:
        """Validate plugin dependencies against policy.

        Placeholder — returns empty violations.
        """
        violations: list[str] = []

        log.info("policy_engine.check_dependency", plugin=plugin.name)

        if plugin.manifest:
            for dep in plugin.manifest.dependencies:
                if dep.optional and dep.required:
                    violations.append(
                        f"Dependency '{dep.plugin_name}' is marked both optional and required"
                    )

        return violations

    def check_all(self, plugin: Plugin) -> list[str]:
        """Run all policy checks against a plugin."""
        violations: list[str] = []
        violations.extend(self.check_installation_policy(plugin))
        violations.extend(self.check_security_policy(plugin))
        violations.extend(self.check_dependency_policy(plugin))
        return violations
