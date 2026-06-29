"""RegistryDependencyGraph — generic dependency graph for registry entries.

Supports parent/child queries, cycle detection, dependency tree
construction, and topological ordering.
"""

from __future__ import annotations

import structlog

from adip.registry.contracts.models import RegistryEntry
from adip.registry.execution.models import DependencyGraph, DependencyNode

log = structlog.get_logger(__name__)


class RegistryDependencyGraph:
    """Generic dependency graph for registry entries.

    Tracks dependencies between entries using an adjacency list.
    Supports cycle detection, topological ordering, and tree queries.
    """

    def __init__(self) -> None:
        self._graph: DependencyGraph | None = None
        self._nodes: dict[str, DependencyNode] = {}

    def create(self, entries: list[RegistryEntry]) -> DependencyGraph:
        """Create a dependency graph from a list of entries.

        Builds adjacency lists and dependency nodes for each entry.
        """
        log.info("registry_dependency_graph.create", entry_count=len(entries))
        adjacency: dict[str, list[str]] = {}
        node_map: dict[str, DependencyNode] = {}

        for entry in entries:
            name = entry.name
            deps = entry.metadata.get("dependencies", [])
            if isinstance(deps, list):
                deps = [str(d) for d in deps]
            else:
                deps = []
            adjacency[name] = deps
            node_map[name] = DependencyNode(
                entry_name=name,
                entry_id=str(entry.entry_id),
                version=entry.version,
                dependencies=deps,
            )

        entry_names = set(adjacency.keys())
        all_deps: set[str] = set()
        for deps in adjacency.values():
            all_deps.update(deps)
        unused = sorted(all_deps - entry_names)
        roots = sorted(n for n, d in adjacency.items() if not d)
        leaves = sorted(n for n in entry_names if n not in all_deps or all(adjacency.get(d, []) for d in adjacency if n in adjacency[d]))

        self._graph = DependencyGraph(
            nodes=adjacency,
            root_entries=roots,
            leaf_entries=leaves,
            unused_dependencies=unused,
        )

        self._graph.circular_dependency_reports = self.detect_cycles()
        self._graph.load_order = self.compute_load_order()
        self._graph.dependency_depth = self._compute_max_depth()
        self._nodes = node_map
        self._populate_dependents()
        return self._graph

    def detect_cycles(self) -> list[list[str]]:
        """Detect circular dependencies using DFS with coloring."""
        if self._graph is None:
            return []
        adjacency = self._graph.nodes
        WHITE, GREY, BLACK = 0, 1, 2
        colour: dict[str, int] = {n: WHITE for n in adjacency}
        parent: dict[str, str | None] = {}
        cycles: list[list[str]] = []

        def dfs(node: str) -> None:
            colour[node] = GREY
            for neighbour in adjacency.get(node, []):
                if neighbour not in colour:
                    colour[neighbour] = WHITE
                    parent[neighbour] = node
                if colour.get(neighbour, WHITE) == GREY:
                    cycle = self._extract_cycle_path(node, neighbour, parent)
                    if cycle:
                        cycles.append(cycle)
                elif colour.get(neighbour, WHITE) == WHITE:
                    parent[neighbour] = node
                    dfs(neighbour)
            colour[node] = BLACK

        for node in adjacency:
            if colour.get(node, WHITE) == WHITE:
                dfs(node)
        return cycles

    def compute_load_order(self) -> list[str]:
        """Compute topological load order using DFS."""
        if self._graph is None:
            return []
        adjacency = self._graph.nodes
        visited: set[str] = set()
        order: list[str] = []

        def dfs(node: str) -> None:
            if node in visited:
                return
            visited.add(node)
            for dep in adjacency.get(node, []):
                if dep in adjacency:
                    dfs(dep)
            order.append(node)

        for node in adjacency:
            dfs(node)
        return order

    def get_parents(self, entry_name: str) -> list[str]:
        """Get entries that depend on the given entry."""
        if self._graph is None:
            return []
        parents: list[str] = []
        for name, deps in self._graph.nodes.items():
            if entry_name in deps:
                parents.append(name)
        return parents

    def get_children(self, entry_name: str) -> list[str]:
        """Get entries that the given entry depends on."""
        if self._graph is None:
            return []
        return list(self._graph.nodes.get(entry_name, []))

    def get_dependency_tree(self, entry_name: str, max_depth: int = 100) -> dict[str, list[str]]:
        """Build a dependency tree for an entry (level → list of names)."""
        tree: dict[str, list[str]] = {}
        visited: set[str] = set()

        def walk(name: str, depth: int) -> None:
            if depth > max_depth or name in visited:
                return
            visited.add(name)
            if str(depth) not in tree:
                tree[str(depth)] = []
            tree[str(depth)].append(name)
            for child in self.get_children(name):
                walk(child, depth + 1)

        walk(entry_name, 0)
        return tree

    def get_node(self, entry_name: str) -> DependencyNode | None:
        """Get a dependency node by entry name."""
        return self._nodes.get(entry_name)

    def get_all_nodes(self) -> dict[str, DependencyNode]:
        """Get all dependency nodes."""
        return dict(self._nodes)

    def clear(self) -> None:
        """Clear the graph."""
        self._graph = None
        self._nodes.clear()

    def has_cycles(self) -> bool:
        """Return whether the graph contains cycles."""
        return len(self.detect_cycles()) > 0 if self._graph else False

    # ── private helpers ───────────────────────────────────────────

    def _extract_cycle_path(
        self,
        node: str,
        neighbour: str,
        parent: dict[str, str | None],
        max_len: int = 100,
    ) -> list[str]:
        path: list[str] = [neighbour, node]
        safe = 0
        cur: str | None = node
        while cur != neighbour and cur is not None and safe < max_len:
            cur = parent.get(cur)
            if cur is not None:
                path.append(cur)
            safe += 1
        path.reverse()
        return path

    def _populate_dependents(self) -> None:
        """Back-fill dependent lists on each node."""
        for node in self._nodes.values():
            for dep_name in node.dependencies:
                dep_node = self._nodes.get(dep_name)
                if dep_node and node.entry_name not in dep_node.dependents:
                    dep_node.dependents.append(node.entry_name)

    def _compute_max_depth(self) -> int:
        if self._graph is None:
            return 0
        max_depth = 0
        for name in self._graph.nodes:
            tree = self.get_dependency_tree(name)
            depth = max((int(k) for k in tree), default=0)
            max_depth = max(max_depth, depth)
        return max_depth
