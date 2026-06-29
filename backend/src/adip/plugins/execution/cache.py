"""PluginCache — synchronous in-memory cache for plugin data.

Caches manifests, configurations, dependencies, capabilities,
and compatibility results with TTL support.

Deterministic placeholder — synchronous in-memory only.
"""

from __future__ import annotations

import structlog

from adip.plugins.contracts.models import (
    PluginCapability,
    PluginConfiguration,
    PluginManifest,
)
from adip.plugins.execution.models import CompatibilityResult, DependencyGraph

log = structlog.get_logger(__name__)


class PluginCache:
    """In-memory cache for plugin-related objects.

    Supports caching of manifests, configurations, dependencies,
    capabilities, and compatibility results.
    """

    def __init__(self) -> None:
        self._manifests: dict[str, PluginManifest] = {}
        self._configurations: dict[str, PluginConfiguration] = {}
        self._dependencies: dict[str, list[str]] = {}
        self._capabilities: dict[str, list[PluginCapability]] = {}
        self._compatibility_results: dict[str, CompatibilityResult] = {}
        self._dependency_graphs: dict[str, DependencyGraph] = {}
        self._ttls: dict[str, int] = {}

    def get_manifest(self, cache_key: str) -> PluginManifest | None:
        """Retrieve a cached manifest by key."""
        if cache_key not in self._manifests:
            return None
        log.info("plugin_cache.get_manifest", key=cache_key)
        return self._manifests[cache_key]

    def set_manifest(self, cache_key: str, manifest: PluginManifest, ttl_seconds: int = 300) -> None:
        """Cache a manifest with an optional TTL."""
        log.info("plugin_cache.set_manifest", key=cache_key, ttl=ttl_seconds)
        self._manifests[cache_key] = manifest
        self._ttls[cache_key] = ttl_seconds

    def get_configuration(self, cache_key: str) -> PluginConfiguration | None:
        """Retrieve a cached configuration by key."""
        if cache_key not in self._configurations:
            return None
        return self._configurations[cache_key]

    def set_configuration(self, cache_key: str, config: PluginConfiguration, ttl_seconds: int = 300) -> None:
        """Cache a configuration with an optional TTL."""
        log.info("plugin_cache.set_configuration", key=cache_key, ttl=ttl_seconds)
        self._configurations[cache_key] = config
        self._ttls[cache_key] = ttl_seconds

    def get_dependencies(self, cache_key: str) -> list[str] | None:
        """Retrieve cached dependency IDs by key."""
        return self._dependencies.get(cache_key)

    def set_dependencies(self, cache_key: str, dependencies: list[str], ttl_seconds: int = 300) -> None:
        """Cache dependency IDs with an optional TTL."""
        log.info("plugin_cache.set_dependencies", key=cache_key, count=len(dependencies), ttl=ttl_seconds)
        self._dependencies[cache_key] = list(dependencies)
        self._ttls[cache_key] = ttl_seconds

    def get_capabilities(self, cache_key: str) -> list[PluginCapability] | None:
        """Retrieve cached capabilities by key."""
        return self._capabilities.get(cache_key)

    def set_capabilities(self, cache_key: str, capabilities: list[PluginCapability], ttl_seconds: int = 300) -> None:
        """Cache capabilities with an optional TTL."""
        log.info("plugin_cache.set_capabilities", key=cache_key, count=len(capabilities), ttl=ttl_seconds)
        self._capabilities[cache_key] = list(capabilities)
        self._ttls[cache_key] = ttl_seconds

    def get_compatibility_result(self, cache_key: str) -> CompatibilityResult | None:
        """Retrieve a cached compatibility result by key."""
        return self._compatibility_results.get(cache_key)

    def set_compatibility_result(self, cache_key: str, result: CompatibilityResult, ttl_seconds: int = 600) -> None:
        """Cache a compatibility result with an optional TTL."""
        log.info("plugin_cache.set_compatibility_result", key=cache_key, ttl=ttl_seconds)
        self._compatibility_results[cache_key] = result
        self._ttls[cache_key] = ttl_seconds

    def get_dependency_graph(self, cache_key: str) -> DependencyGraph | None:
        """Retrieve a cached dependency graph by key."""
        return self._dependency_graphs.get(cache_key)

    def set_dependency_graph(self, cache_key: str, graph: DependencyGraph, ttl_seconds: int = 600) -> None:
        """Cache a dependency graph with an optional TTL."""
        log.info("plugin_cache.set_dependency_graph", key=cache_key, ttl=ttl_seconds)
        self._dependency_graphs[cache_key] = graph
        self._ttls[cache_key] = ttl_seconds

    def invalidate(self, cache_key: str) -> bool:
        """Invalidate a single cache entry across all stores."""
        existed = (
            cache_key in self._manifests
            or cache_key in self._configurations
            or cache_key in self._dependencies
            or cache_key in self._capabilities
            or cache_key in self._compatibility_results
            or cache_key in self._dependency_graphs
        )
        self._manifests.pop(cache_key, None)
        self._configurations.pop(cache_key, None)
        self._dependencies.pop(cache_key, None)
        self._capabilities.pop(cache_key, None)
        self._compatibility_results.pop(cache_key, None)
        self._dependency_graphs.pop(cache_key, None)
        self._ttls.pop(cache_key, None)
        if existed:
            log.info("plugin_cache.invalidate", key=cache_key)
        return existed

    def clear(self) -> int:
        """Clear all cache entries. Returns the number cleared."""
        total = (
            len(self._manifests)
            + len(self._configurations)
            + len(self._dependencies)
            + len(self._capabilities)
            + len(self._compatibility_results)
            + len(self._dependency_graphs)
        )
        self._manifests.clear()
        self._configurations.clear()
        self._dependencies.clear()
        self._capabilities.clear()
        self._compatibility_results.clear()
        self._dependency_graphs.clear()
        self._ttls.clear()
        log.info("plugin_cache.clear", cleared=total)
        return total

    def size(self) -> int:
        """Return the total number of cached entries across all stores."""
        return (
            len(self._manifests)
            + len(self._configurations)
            + len(self._dependencies)
            + len(self._capabilities)
            + len(self._compatibility_results)
            + len(self._dependency_graphs)
        )
