"""PluginDiscoverer — discovers plugins from various sources.

Supports placeholder discovery from:
  - Local Directory
  - Installed Packages
  - Plugin Repository
  - ZIP Package

No filesystem scanning is performed.
"""

from __future__ import annotations

import structlog

from adip.plugins.contracts.models import Plugin
from adip.plugins.enums import PluginLifecycleStatus, PluginType
from adip.plugins.execution.models import DiscoveryResult

log = structlog.get_logger(__name__)


class PluginDiscoverer:
    """Discovers plugins from local directories, packages, repositories, and ZIP files.

    Deterministic placeholder — returns pre-configured discovery results
    without actual filesystem scanning or external calls.
    """

    SUPPORTED_SOURCES: list[str] = [
        "local_directory",
        "installed_package",
        "plugin_repository",
        "zip_package",
    ]

    def discover_from_directory(self, path: str) -> DiscoveryResult:
        """Discover a plugin from a local directory path.

        Placeholder — returns a deterministic result with the path
        as the plugin name.
        """
        log.info("plugin_discoverer.discover_from_directory", path=path)
        return DiscoveryResult(
            plugin_name=_extract_name(path),
            plugin_version="1.0.0",
            plugin_type=PluginType.DOMAIN,
            source=path,
            source_type="local_directory",
        )

    def discover_from_package(self, package_name: str) -> DiscoveryResult:
        """Discover a plugin from an installed package name.

        Placeholder — returns a deterministic result.
        """
        log.info("plugin_discoverer.discover_from_package", package=package_name)
        return DiscoveryResult(
            plugin_name=package_name,
            plugin_version="1.0.0",
            plugin_type=PluginType.DOMAIN,
            source=package_name,
            source_type="installed_package",
        )

    def discover_from_repository(self, repository_url: str) -> DiscoveryResult:
        """Discover a plugin from a repository URL.

        Placeholder — returns a deterministic result.
        """
        log.info("plugin_discoverer.discover_from_repository", url=repository_url)
        return DiscoveryResult(
            plugin_name=_extract_name(repository_url),
            plugin_version="1.0.0",
            plugin_type=PluginType.DOMAIN,
            source=repository_url,
            source_type="plugin_repository",
        )

    def discover_from_zip(self, zip_path: str) -> DiscoveryResult:
        """Discover a plugin from a ZIP package path.

        Placeholder — returns a deterministic result.
        """
        log.info("plugin_discoverer.discover_from_zip", path=zip_path)
        return DiscoveryResult(
            plugin_name=_extract_name(zip_path),
            plugin_version="1.0.0",
            plugin_type=PluginType.DOMAIN,
            source=zip_path,
            source_type="zip_package",
        )

    def discover(self, source: str, source_type: str = "") -> DiscoveryResult:
        """Discover a plugin from any supported source type.

        Auto-detects source type if not specified.
        """
        if not source_type:
            source_type = _detect_source_type(source)

        log.info("plugin_discoverer.discover", source=source, source_type=source_type)

        if source_type == "local_directory":
            return self.discover_from_directory(source)
        elif source_type == "installed_package":
            return self.discover_from_package(source)
        elif source_type == "plugin_repository":
            return self.discover_from_repository(source)
        elif source_type == "zip_package":
            return self.discover_from_zip(source)
        else:
            log.warning("plugin_discoverer.unknown_source", source=source, source_type=source_type)
            return DiscoveryResult(
                plugin_name=_extract_name(source),
                plugin_version="1.0.0",
                source=source,
                source_type="unknown",
            )

    def get_supported_sources(self) -> list[str]:
        """Return the list of supported source types."""
        return list(self.SUPPORTED_SOURCES)

    def convert_to_plugin(self, result: DiscoveryResult) -> Plugin:
        """Convert a DiscoveryResult to a Plugin model.

        Creates a Plugin in DISCOVERED status from the discovery result.
        """
        log.info("plugin_discoverer.convert_to_plugin", name=result.plugin_name)
        return Plugin(
            name=result.plugin_name,
            version=result.plugin_version,
            plugin_type=result.plugin_type or PluginType.DOMAIN,
            domain=result.domain,
            status=PluginLifecycleStatus.DISCOVERED,
            manifest=result.manifest,
            namespace=result.source,
        )


def _extract_name(source: str) -> str:
    """Extract a plugin name from a path or URL.

    Placeholder — returns the last path component stripped of extension.
    """
    name = source.rstrip("/").rstrip("\\").split("/")[-1].split("\\")[-1]
    for ext in (".zip", ".tar", ".gz", ".whl"):
        if name.endswith(ext):
            name = name[: -len(ext)]
    return name or "unknown"


def _detect_source_type(source: str) -> str:
    """Detect the source type from a source string.

    Placeholder heuristic based on string patterns.
    """
    if source.startswith(("http://", "https://", "git@")):
        return "plugin_repository"
    if source.endswith(".zip"):
        return "zip_package"
    if "." in source and "/" not in source and "\\" not in source:
        return "installed_package"
    return "local_directory"
