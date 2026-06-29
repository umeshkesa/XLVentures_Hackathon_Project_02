"""TopologyService — provides asset topology information.

Deterministic placeholder for discovering upstream, downstream,
connected, and neighbor assets within the energy asset graph.
"""

from __future__ import annotations

import structlog

from adip.energy.execution.models import AssetGraphModel, TopologyResult

log = structlog.get_logger(__name__)


class TopologyService:
    """Provides topology analysis for energy assets."""

    def get_topology(
        self,
        graph: AssetGraphModel,
        asset_id: str,
        correlation_id: str = "",
    ) -> TopologyResult:
        """Get topology information for an asset in the graph.

        Args:
            graph: The asset graph to analyse.
            asset_id: The asset to get topology for.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            TopologyResult with upstream, downstream, connected, and neighbor assets.
        """
        upstream = self.get_upstream(graph, asset_id)
        downstream = self.get_downstream(graph, asset_id)
        connected = self.get_connected(graph, asset_id)
        neighbors = self.get_neighbors(graph, asset_id)

        result = TopologyResult(
            asset_id=self._parse_uuid(asset_id),
            upstream=upstream,
            downstream=downstream,
            connected=connected,
            neighbors=neighbors,
        )
        log.info(
            "energy.topology.resolved",
            asset_id=asset_id,
            upstream_count=len(upstream),
            downstream_count=len(downstream),
            connected_count=len(connected),
            neighbor_count=len(neighbors),
            correlation_id=correlation_id,
        )
        return result

    def get_upstream(
        self,
        graph: AssetGraphModel,
        asset_id: str,
    ) -> list[str]:
        """Get upstream assets (towards source/parent).

        Args:
            graph: The asset graph.
            asset_id: The starting asset.

        Returns:
            List of upstream asset IDs as strings.
        """
        result: list[str] = []
        visited: set[str] = set()
        edges_by_target: dict[str, list[str]] = {}

        for edge in graph.edges:
            tgt = str(edge.target_asset_id)
            src = str(edge.source_asset_id)
            if tgt not in edges_by_target:
                edges_by_target[tgt] = []
            edges_by_target[tgt].append(src)

        def traverse(current: str) -> None:
            for src in edges_by_target.get(current, []):
                if src not in visited:
                    visited.add(src)
                    result.append(src)
                    traverse(src)

        traverse(asset_id)
        return result

    def get_downstream(
        self,
        graph: AssetGraphModel,
        asset_id: str,
    ) -> list[str]:
        """Get downstream assets (towards load/children).

        Args:
            graph: The asset graph.
            asset_id: The starting asset.

        Returns:
            List of downstream asset IDs as strings.
        """
        result: list[str] = []
        visited: set[str] = set()
        edges_by_source: dict[str, list[str]] = {}

        for edge in graph.edges:
            src = str(edge.source_asset_id)
            tgt = str(edge.target_asset_id)
            if src not in edges_by_source:
                edges_by_source[src] = []
            edges_by_source[src].append(tgt)

        def traverse(current: str) -> None:
            for tgt in edges_by_source.get(current, []):
                if tgt not in visited:
                    visited.add(tgt)
                    result.append(tgt)
                    traverse(tgt)

        traverse(asset_id)
        return result

    def get_connected(
        self,
        graph: AssetGraphModel,
        asset_id: str,
    ) -> list[str]:
        """Get directly connected assets (both directions).

        Args:
            graph: The asset graph.
            asset_id: The starting asset.

        Returns:
            List of directly connected asset IDs as strings.
        """
        connected: set[str] = set()
        for edge in graph.edges:
            src = str(edge.source_asset_id)
            tgt = str(edge.target_asset_id)
            if src == asset_id:
                connected.add(tgt)
            if tgt == asset_id:
                connected.add(src)
        return list(connected)

    def get_neighbors(
        self,
        graph: AssetGraphModel,
        asset_id: str,
    ) -> list[str]:
        """Get neighboring assets (same level/hierarchy).

        Neighbors are assets at the same topological level
        that share a common parent.
        """
        target_level = None
        for node in graph.nodes:
            if str(node.asset_id) == asset_id:
                target_level = node.level
                break

        if target_level is None:
            return []

        parent_ids: set[str] = set()
        for edge in graph.edges:
            if str(edge.target_asset_id) == asset_id:
                parent_ids.add(str(edge.source_asset_id))

        neighbors: list[str] = []
        for node in graph.nodes:
            nid = str(node.asset_id)
            if nid == asset_id:
                continue
            if node.level == target_level:
                node_parents: set[str] = set()
                for edge in graph.edges:
                    if str(edge.target_asset_id) == nid:
                        node_parents.add(str(edge.source_asset_id))
                if parent_ids & node_parents:
                    neighbors.append(nid)

        return neighbors

    def _parse_uuid(self, value: str) -> str:
        return value
