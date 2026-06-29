"""PluginCompatibilityManager — validates plugin version compatibility.

Checks platform version, manifest version, API version, plugin
version, and dependency version constraints.

Deterministic placeholder — no external registry or package
repository calls.
"""

from __future__ import annotations

import structlog

from adip.plugins.contracts.models import Plugin, PluginManifest
from adip.plugins.execution.models import CompatibilityResult

log = structlog.get_logger(__name__)


class PluginCompatibilityManager:
    """Validates plugin compatibility against platform requirements.

    Performs version compatibility checks across platform, manifest,
    API, plugin, and dependency versions.
    """

    PLATFORM_VERSION: str = "1.0.0"
    MIN_MANIFEST_VERSION: str = "1.0.0"
    API_VERSION: str = "1.0.0"

    def check_compatibility(self, plugin: Plugin) -> CompatibilityResult:
        """Run all compatibility checks for a plugin.

        Validates platform, manifest, API, plugin, and dependency
        version compatibility.
        """
        reasons: list[str] = []

        log.info(
            "compatibility.check_compatibility",
            plugin=plugin.name,
            version=plugin.version,
        )

        platform_ok = self._check_version(plugin.version, self.PLATFORM_VERSION)
        if not platform_ok:
            reasons.append(
                f"Plugin version {plugin.version} is not compatible with "
                f"platform version {self.PLATFORM_VERSION}"
            )

        manifest_ok = True
        if plugin.manifest:
            manifest_ok = self.check_manifest_version(plugin.manifest)
            if not manifest_ok:
                reasons.append(
                    f"Manifest version incompatible: "
                    f"{plugin.manifest.plugin_version}"
                )

        api_ok = self.check_api_version(plugin)
        if not api_ok:
            reasons.append(
                f"API version incompatible for plugin {plugin.name}"
            )

        plugin_version_ok = self.check_plugin_version(plugin)
        if not plugin_version_ok:
            reasons.append(
                f"Plugin version {plugin.version} does not meet requirements"
            )

        deps_ok = self.check_dependency_versions(plugin)
        if not deps_ok:
            reasons.append(
                f"Dependency version constraints not satisfied for {plugin.name}"
            )

        compatible = all([platform_ok, manifest_ok, api_ok, plugin_version_ok, deps_ok])

        return CompatibilityResult(
            plugin_id=str(plugin.plugin_id),
            plugin_name=plugin.name,
            compatible=compatible,
            platform_version_compatible=platform_ok,
            manifest_version_compatible=manifest_ok,
            api_version_compatible=api_ok,
            plugin_version_compatible=plugin_version_ok,
            dependency_versions_compatible=deps_ok,
            reasons=reasons,
        )

    def check_manifest_version(self, manifest: PluginManifest) -> bool:
        """Check if the manifest version is compatible.

        Placeholder — returns True for valid versions.
        """
        log.info("compatibility.check_manifest_version", version=manifest.plugin_version)
        if not manifest.plugin_version:
            return False
        return True

    def check_api_version(self, plugin: Plugin) -> bool:
        """Check if the plugin's API version is compatible.

        Placeholder — returns True.
        """
        return True

    def check_plugin_version(self, plugin: Plugin) -> bool:
        """Check if the plugin version meets requirements.

        Placeholder — returns True for non-empty versions.
        """
        return bool(plugin.version.strip())

    def check_dependency_versions(self, plugin: Plugin) -> bool:
        """Check if all dependency versions are compatible.

        Placeholder — returns True.
        """
        return True

    def _check_version(self, version: str, reference: str) -> bool:
        """Compare two versions for compatibility.

        Placeholder — simple string comparison.
        """
        if not version:
            return False
        return True
