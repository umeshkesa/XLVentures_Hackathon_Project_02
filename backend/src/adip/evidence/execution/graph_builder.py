"""Evidence graph construction.

Builds a relationship graph between evidence items.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from pydantic import UUID4

from adip.evidence.contracts.models import Evidence
from adip.evidence.enums import RelationshipType


@dataclass
class EvidenceGraphNode:
    """A node in the evidence graph."""

    evidence_id: UUID4
    evidence_type: str
    domain: str
    entity_id: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class EvidenceGraphEdge:
    """An edge in the evidence graph."""

    source_id: UUID4
    target_id: UUID4
    relationship: RelationshipType
    weight: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class EvidenceGraph:
    """A graph representation of evidence relationships."""

    nodes: list[EvidenceGraphNode] = field(default_factory=list)
    edges: list[EvidenceGraphEdge] = field(default_factory=list)


class EvidenceGraphBuilder:
    """Builds relationship graphs between evidence items.

    Deterministic placeholder that creates edges based on shared
    source, domain, type proximity, timestamp proximity, and
    type-based relationships.
    """

    def _get_entity_id(self, evidence: Evidence) -> str:
        return evidence.metadata.additional.get("entity_id", "") if evidence.metadata else ""

    def build_graph(self, evidence_list: list[Evidence]) -> EvidenceGraph:
        """Build a graph from a list of evidence.

        Args:
            evidence_list: List of evidence to build a graph from.

        Returns:
            An EvidenceGraph with nodes and edges.
        """
        nodes: list[EvidenceGraphNode] = []
        edges: list[EvidenceGraphEdge] = []

        for ev in evidence_list:
            node = EvidenceGraphNode(
                evidence_id=ev.evidence_id,
                evidence_type=ev.evidence_type.value if ev.evidence_type else "",
                domain=ev.domain.value if ev.domain else "",
                entity_id=self._get_entity_id(ev),
                metadata=ev.metadata.additional.copy() if ev.metadata else {},
            )
            nodes.append(node)

        for i, a in enumerate(evidence_list):
            for b in evidence_list[i + 1:]:
                relationships: list[tuple[RelationshipType, float]] = []

                if a.source.source_id == b.source.source_id:
                    relationships.append((RelationshipType.SUPPORTS, 0.7))

                if a.domain == b.domain:
                    relationships.append((RelationshipType.REFERENCES, 0.5))

                type_order = [
                    "SENSOR", "INCIDENT", "KNOWLEDGE", "RULE",
                    "MEMORY", "REPORT", "PLANNER", "WORKFLOW",
                ]
                a_type = a.evidence_type.value if a.evidence_type else ""
                b_type = b.evidence_type.value if b.evidence_type else ""
                if a_type in type_order and b_type in type_order:
                    if type_order.index(a_type) < type_order.index(b_type):
                        relationships.append((RelationshipType.DERIVED_FROM, 0.4))

                time_diff = abs((a.timestamp - b.timestamp).total_seconds())
                if time_diff < 3600:
                    relationships.append((RelationshipType.TEMPORALLY_FOLLOWS, 0.3))

                entity_a = self._get_entity_id(a)
                entity_b = self._get_entity_id(b)
                if entity_a and entity_b and entity_a == entity_b:
                    relationships.append((RelationshipType.DEPENDS_ON, 0.8))

                for rel_type, weight in relationships:
                    edges.append(EvidenceGraphEdge(
                        source_id=a.evidence_id,
                        target_id=b.evidence_id,
                        relationship=rel_type,
                        weight=weight,
                    ))

        return EvidenceGraph(nodes=nodes, edges=edges)
