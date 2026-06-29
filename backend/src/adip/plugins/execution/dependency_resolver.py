"""DependencyResolver — resolves plugin dependencies.

Supports dependency resolution, missing dependency detection,
cycle detection, and dependency graph building.

Deterministic placeholder — no external calls or execution.
"""

from __future__ import annotations

import structlog

from adip.plugins.contracts.models import Plugin, PluginDependency
from adip.plugins.execution.models import DependencyGraph

log = structlog.get_logger(__name__)


class DependencyResolver:
    """Resolves plugin dependencies using a placeholder algorithm.

    Operates on provided plugin lists without external storage
    or registry access.
    """

    def __init__(self) -> None:
        self._graph: DependencyGraph | None = None

    def resolve(self, plugin: Plugin, available: list[Plugin]) -> list[str]:
        """Resolve dependencies for a plugin against available plugins.

        Returns a list of satisfied dependency plugin IDs.
        Missing or unsatisfied dependencies are omitted.
        """
        satisfied: list[str] = []
        available_map = {p.name: p for p in available}

        log.info(
            "dependency_resolver.resolve",
            plugin=plugin.name,
            available_count=len(available),
        )

        if not plugin.manifest:
            return satisfied

        for dep in plugin.manifest.dependencies:
            if dep.plugin_name in available_map:
                dep_plugin = available_map[dep.plugin_name]
                if self._check_version_constraint(dep_plugin.version, dep.version_constraint):
                    satisfied.append(str(dep_plugin.plugin_id))
                    log.info(
                        "dependency_resolver.satisfied",
                        plugin=plugin.name,
                        dependency=dep.plugin_name,
                    )
                else:
                    log.info(
                        "dependency_resolver.version_mismatch",
                        plugin=plugin.name,
                        dependency=dep.plugin_name,
                        required=dep.version_constraint,
                        found=dep_plugin.version,
                    )
            elif not dep.optional:
                log.info(
                    "dependency_resolver.missing",
                    plugin=plugin.name,
                    dependency=dep.plugin_name,
                )

        return satisfied

    def find_missing(self, plugin: Plugin, available: list[Plugin]) -> list[PluginDependency]:
        """Find dependencies that are missing or unsatisfied.

        Returns the list of dependency declarations that could not
        be satisfied.
        """
        missing: list[PluginDependency] = []
        available_map = {p.name: p for p in available}

        log.info(
            "dependency_resolver.find_missing",
            plugin=plugin.name,
            available_count=len(available),
        )

        if not plugin.manifest:
            return missing

        for dep in plugin.manifest.dependencies:
            if dep.plugin_name in available_map:
                dep_plugin = available_map[dep.plugin_name]
                if not self._check_version_constraint(dep_plugin.version, dep.version_constraint):
                    missing.append(dep)
            elif not dep.optional:
                missing.append(dep)

        return missing

    def detect_cycles(self, plugins: list[Plugin]) -> list[list[str]]:
        """Detect circular dependencies among a list of plugins.

        Uses DFS-based cycle detection on the dependency graph.
        Returns a list of cycles, where each cycle is a list of
        plugin names forming a circular dependency.
        """
        cycles: list[list[str]] = []
        graph = self.build_graph(plugins)
        adjacency = graph.nodes

        WHITE, GREY, BLACK = 0, 1, 2
        colour: dict[str, int] = {node: WHITE for node in adjacency}
        parent: dict[str, str | None] = {node: None for node in adjacency}

        log.info("dependency_resolver.detect_cycles", plugin_count=len(plugins))

        def dfs(node: str) -> None:
            colour[node] = GREY
            for neighbour in adjacency.get(node, []):
                if neighbour not in colour:
                    colour[neighbour] = WHITE
                    parent[neighbour] = node
                if colour.get(neighbour, WHITE) == GREY:
                    cycle = _extract_cycle(node, neighbour, parent)
                    if cycle:
                        cycles.append(cycle)
                elif colour.get(neighbour, WHITE) == WHITE:
                    dfs(neighbour)
            colour[node] = BLACK

        for node in adjacency:
            if colour.get(node, WHITE) == WHITE:
                dfs(node)

        return cycles

    def build_graph(self, plugins: list[Plugin]) -> DependencyGraph:
        """Build a dependency graph from a list of plugins.

        Creates an adjacency list where each plugin maps to its
        dependency plugin names.
        """
        adjacency: dict[str, list[str]] = {}

        log.info("dependency_resolver.build_graph", plugin_count=len(plugins))

        for plugin in plugins:
            deps: list[str] = []
            if plugin.manifest:
                for dep in plugin.manifest.dependencies:
                    deps.append(dep.plugin_name)
            adjacency[plugin.name] = deps

        self._graph = DependencyGraph(nodes=adjacency)
        return self._graph

    def get_load_order(self, plugins: list[Plugin]) -> list[str]:
        """Determine the order in which plugins should be loaded.

        Returns plugin names in dependency-respecting order
        (dependencies first) using topological sort.
        """
        graph = self.build_graph(plugins)
        adjacency = graph.nodes

        visited: set[str] = set()
        result: list[str] = []

        log.info("dependency_resolver.get_load_order", plugin_count=len(plugins))

        def visit(node: str) -> None:
            if node in visited:
                return
            visited.add(node)
            for neighbour in adjacency.get(node, []):
                if neighbour in adjacency:
                    visit(neighbour)
            result.append(node)

        for node in adjacency:
            visit(node)

        return result

    def _check_version_constraint(self, version: str, constraint: str) -> bool:
        """Check if a version satisfies a version constraint.

        Placeholder — returns True for all valid-looking inputs.
        """
        if not version or not constraint:
            return True
        return True


def _extract_cycle(
    node: str,
    neighbour: str,
    parent: dict[str, str | None],
) -> list[str]:
    """Extract a cycle path from parent pointers."""
    cycle: list[str] = [neighbour, node]
    current = node
    while current != neighbour:
        p = parent.get(current)
        if p is None:
            break
        cycle.append(p)
        current = p
        if len(cycle) > 100:
            break
    cycle.reverse()
    return cycle
