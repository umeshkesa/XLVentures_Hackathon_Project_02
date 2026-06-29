"""PluginDependencyGraph — models the plugin dependency graph.

Supports graph creation, cycle detection, load order computation,
parent/child queries, and dependency tree traversal.

Deterministic placeholder — in-memory only.
"""

from __future__ import annotations

import structlog

from adip.plugins.contracts.models import Plugin
from adip.plugins.execution.models import DependencyGraph, DependencyNode

log = structlog.get_logger(__name__)


class PluginDependencyGraph:
    """Manages the plugin dependency graph.

    Provides structured access to dependency relationships
    including cycle detection, load ordering, and tree traversal.
    """

    def __init__(self) -> None:
        self._graph: DependencyGraph | None = None
        self._nodes: dict[str, DependencyNode] = {}

    def create(self, plugins: list[Plugin]) -> DependencyGraph:
        """Create a dependency graph from a list of plugins.

        Builds adjacency lists and creates dependency nodes for
        each plugin.
        """
        adjacency: dict[str, list[str]] = {}
        self._nodes = {}

        log.info("dep_graph.create", plugin_count=len(plugins))

        for plugin in plugins:
            plugin_id = str(plugin.plugin_id)
            deps: list[str] = []
            if plugin.manifest:
                for dep in plugin.manifest.dependencies:
                    deps.append(dep.plugin_name)
            adjacency[plugin.name] = deps

            self._nodes[plugin.name] = DependencyNode(
                plugin_id=plugin_id,
                plugin_name=plugin.name,
                version=plugin.version,
                dependencies=deps,
            )

        all_names = set(adjacency.keys())
        all_dep_names: set[str] = set()
        for deps in adjacency.values():
            all_dep_names.update(deps)

        root_plugins = [n for n in all_names if not adjacency.get(n)]
        leaf_plugins = [n for n in all_names if n not in all_dep_names]
        unused_dependencies = sorted(all_dep_names - all_names)

        cycles = self.detect_cycles()
        load_order = self.compute_load_order()

        max_depth = 0
        for plugin in plugins:
            tree = self.get_dependency_tree(plugin.name)
            if tree:
                max_depth = max(max_depth, max(tree.keys()))

        self._graph = DependencyGraph(
            nodes=adjacency,
            root_plugins=root_plugins,
            leaf_plugins=leaf_plugins,
            circular_dependency_reports=cycles,
            dependency_depth=max_depth,
            load_order=load_order,
            unused_dependencies=unused_dependencies,
        )

        for plugin in plugins:
            node = self._nodes.get(plugin.name)
            if node is None:
                continue
            for dep_name in node.dependencies:
                if dep_name in self._nodes:
                    self._nodes[dep_name].dependents.append(plugin.name)

        return self._graph

    def detect_cycles(self) -> list[list[str]]:
        """Detect circular dependencies in the graph.

        Uses DFS-based cycle detection. Returns a list of cycles,
        where each cycle is a list of plugin names.
        """
        cycles: list[list[str]] = []
        if not self._graph:
            log.warning("dep_graph.detect_cycles.no_graph")
            return cycles

        adjacency = self._graph.nodes
        WHITE, GREY, BLACK = 0, 1, 2
        colour: dict[str, int] = {n: WHITE for n in adjacency}
        parent: dict[str, str | None] = {n: None for n in adjacency}

        log.info("dep_graph.detect_cycles")

        def dfs(node: str) -> None:
            colour[node] = GREY
            for neighbour in adjacency.get(node, []):
                if neighbour not in colour:
                    colour[neighbour] = WHITE
                    parent[neighbour] = node
                if colour.get(neighbour, WHITE) == GREY:
                    cycle = _extract_cycle_path(node, neighbour, parent)
                    if cycle:
                        cycles.append(cycle)
                elif colour.get(neighbour, WHITE) == WHITE:
                    dfs(neighbour)
            colour[node] = BLACK

        for node in adjacency:
            if colour.get(node, WHITE) == WHITE:
                dfs(node)

        return cycles

    def compute_load_order(self) -> list[str]:
        """Compute the topological load order for plugins.

        Returns plugin names in dependency-first order.
        """
        if not self._graph:
            log.warning("dep_graph.compute_load_order.no_graph")
            return []

        adjacency = self._graph.nodes
        visited: set[str] = set()
        result: list[str] = []

        log.info("dep_graph.compute_load_order")

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

    def get_parents(self, plugin_name: str) -> list[str]:
        """Get the immediate parent plugins (dependents) of a plugin.

        Returns plugin names that depend directly on the given plugin.
        """
        node = self._nodes.get(plugin_name)
        if node is None:
            return []
        return list(node.dependents)

    def get_children(self, plugin_name: str) -> list[str]:
        """Get the immediate child plugins (dependencies) of a plugin.

        Returns plugin names that the given plugin depends on directly.
        """
        node = self._nodes.get(plugin_name)
        if node is None:
            return []
        return list(node.dependencies)

    def get_dependency_tree(self, plugin_name: str) -> dict[str, list[str]]:
        """Get the full dependency tree for a plugin.

        Returns a hierarchical dictionary of all recursive
        dependencies organised by level.
        """
        tree: dict[str, list[str]] = {}
        visited: set[str] = set()

        def walk(name: str, level: int = 0) -> None:
            if name in visited or level > 100:
                return
            visited.add(name)
            if level not in tree:
                tree[level] = []
            tree[level].append(name)
            node = self._nodes.get(name)
            if node:
                for dep in node.dependencies:
                    walk(dep, level + 1)

        walk(plugin_name)
        return tree

    def get_node(self, plugin_name: str) -> DependencyNode | None:
        """Get a dependency node by plugin name."""
        return self._nodes.get(plugin_name)

    def get_all_nodes(self) -> dict[str, DependencyNode]:
        """Get all dependency nodes."""
        return dict(self._nodes)

    def clear(self) -> None:
        """Clear the graph and all nodes."""
        self._graph = None
        self._nodes.clear()

    def has_cycles(self) -> bool:
        """Return True if the graph contains cycles."""
        return len(self.detect_cycles()) > 0


def _extract_cycle_path(
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
