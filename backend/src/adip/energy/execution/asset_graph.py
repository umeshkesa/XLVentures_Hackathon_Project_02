"""AssetGraph — graph construction, cycle detection, and topology analysis.

Builds and validates an asset dependency graph from node/edge
data, detects cycles, computes topological ordering, and
identifies root and leaf nodes.
"""

from __future__ import annotations

import uuid
from collections import deque

import structlog

from adip.energy.enums import AssetType
from adip.energy.execution.models import AssetEdge, AssetGraphModel, AssetNode

log = structlog.get_logger(__name__)


class AssetGraph:
    """Constructs and validates energy asset dependency graphs."""

    def build_graph(
        self,
        assets: list[tuple[str, str, str]] | None = None,
        relationships: list[tuple[str, str, str, float]] | None = None,
        correlation_id: str = "",
    ) -> AssetGraphModel:
        """Build an asset graph from asset and relationship data.

        Args:
            assets: List of (asset_id, name, asset_type_str) tuples.
            relationships: List of (source_id, target_id, rel_type, weight) tuples.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            An AssetGraphModel with nodes, edges, and topology analysis.
        """
        assets = assets or []
        relationships = relationships or []

        nodes = [
            AssetNode(
                asset_id=self._parse_uuid(aid),
                asset_name=name,
                asset_type=self._parse_asset_type(atype),
            )
            for aid, name, atype in assets
        ]

        edges = [
            AssetEdge(
                source_asset_id=self._parse_uuid(src),
                target_asset_id=self._parse_uuid(tgt),
                relationship_type=rel_type,
                weight=weight,
            )
            for src, tgt, rel_type, weight in relationships
        ]

        node_ids: list[str] = [aid for aid, _, _ in assets]
        dep_list: list[tuple[str, str]] = [
            (src, tgt) for src, tgt, _, _ in relationships
        ]

        has_cycle, _ = self._detect_cycle(node_ids, dep_list)
        topo_order = (
            self._topological_sort(node_ids, dep_list) if not has_cycle else []
        )
        roots = self._find_root_nodes(node_ids, dep_list)
        leaves = self._find_leaf_nodes(node_ids, dep_list)

        topo_uuid = [self._parse_uuid(tid) for tid in topo_order]
        root_uuid = [self._parse_uuid(rid) for rid in roots]
        leaf_uuid = [self._parse_uuid(lid) for lid in leaves]

        for node in nodes:
            tid_str = str(node.asset_id)
            if tid_str in topo_order:
                node.level = topo_order.index(tid_str)

        graph = AssetGraphModel(
            nodes=nodes,
            edges=edges,
            has_cycle=has_cycle,
            topological_order=topo_uuid,
            root_nodes=root_uuid,
            leaf_nodes=leaf_uuid,
        )
        log.info(
            "energy.asset_graph.built",
            node_count=len(nodes),
            edge_count=len(edges),
            has_cycle=has_cycle,
            correlation_id=correlation_id,
        )
        return graph

    def validate_graph(
        self,
        graph: AssetGraphModel,
        correlation_id: str = "",
    ) -> list[str]:
        """Validate an asset graph for consistency.

        Args:
            graph: The graph to validate.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            List of validation issues (empty if valid).
        """
        issues: list[str] = []
        if graph.has_cycle:
            issues.append("Graph contains a cycle")
        if not graph.nodes:
            issues.append("Graph has no nodes")

        node_ids = {str(n.asset_id) for n in graph.nodes}
        for edge in graph.edges:
            src_str = str(edge.source_asset_id)
            tgt_str = str(edge.target_asset_id)
            if src_str not in node_ids:
                issues.append(f"Edge references unknown source node: {src_str}")
            if tgt_str not in node_ids:
                issues.append(f"Edge references unknown target node: {tgt_str}")

        log.info(
            "energy.asset_graph.validated",
            graph_id=str(graph.graph_id),
            valid=len(issues) == 0,
            issues_count=len(issues),
            correlation_id=correlation_id,
        )
        return issues

    def get_downstream(
        self,
        graph: AssetGraphModel,
        asset_id: str,
    ) -> list[str]:
        """Get all downstream assets from a given asset.

        Args:
            graph: The asset graph.
            asset_id: The starting asset ID.

        Returns:
            List of downstream asset IDs as strings.
        """
        adj: dict[str, list[str]] = {}
        for edge in graph.edges:
            src = str(edge.source_asset_id)
            tgt = str(edge.target_asset_id)
            if src not in adj:
                adj[src] = []
            adj[src].append(tgt)

        visited: set[str] = set()
        result: list[str] = []

        def dfs(node: str) -> None:
            for neighbor in adj.get(node, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    result.append(neighbor)
                    dfs(neighbor)

        dfs(asset_id)
        return result

    @staticmethod
    def _parse_uuid(value: str | uuid.UUID) -> uuid.UUID:
        """Parse a string or UUID into a UUID."""
        if isinstance(value, uuid.UUID):
            return value
        try:
            return uuid.UUID(value)
        except ValueError:
            return uuid.uuid5(uuid.NAMESPACE_DNS, value)

    def _parse_asset_type(self, type_str: str) -> AssetType:
        """Parse a string into an AssetType enum."""
        for at in AssetType:
            if at.value == type_str or at.name == type_str:
                return at
        return AssetType.SENSOR

    def _detect_cycle(
        self,
        node_ids: list[str],
        dependencies: list[tuple[str, str]],
    ) -> tuple[bool, list[str]]:
        """Detect cycles using DFS."""
        adj: dict[str, list[str]] = {nid: [] for nid in node_ids}
        for src, tgt in dependencies:
            if src in adj:
                adj[src].append(tgt)

        visited: set[str] = set()
        rec_stack: set[str] = set()

        def dfs(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)
            for neighbor in adj.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            rec_stack.discard(node)
            return False

        for nid in node_ids:
            if nid not in visited:
                if dfs(nid):
                    return True, list(rec_stack)
        return False, []

    def _topological_sort(
        self,
        node_ids: list[str],
        dependencies: list[tuple[str, str]],
    ) -> list[str]:
        """Kahn's algorithm for topological ordering."""
        in_degree: dict[str, int] = {nid: 0 for nid in node_ids}
        adj: dict[str, list[str]] = {nid: [] for nid in node_ids}
        for src, tgt in dependencies:
            if src in adj and tgt in in_degree:
                adj[src].append(tgt)
                in_degree[tgt] += 1

        queue = deque([nid for nid, deg in in_degree.items() if deg == 0])
        result: list[str] = []
        while queue:
            node = queue.popleft()
            result.append(node)
            for neighbor in adj.get(node, []):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        return result

    def _find_root_nodes(
        self,
        node_ids: list[str],
        dependencies: list[tuple[str, str]],
    ) -> list[str]:
        """Find nodes with no incoming edges."""
        has_incoming: set[str] = {tgt for _, tgt in dependencies}
        return [nid for nid in node_ids if nid not in has_incoming]

    def _find_leaf_nodes(
        self,
        node_ids: list[str],
        dependencies: list[tuple[str, str]],
    ) -> list[str]:
        """Find nodes with no outgoing edges."""
        has_outgoing: set[str] = {src for src, _ in dependencies}
        return [nid for nid in node_ids if nid not in has_outgoing]
