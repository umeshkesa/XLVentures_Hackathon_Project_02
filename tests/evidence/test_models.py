"""Tests for Evidence Fusion Engine domain models."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from adip.evidence.contracts.models import (
    Evidence,
    EvidenceDecision,
    EvidenceEdge,
    EvidenceGraph,
    EvidenceHealth,
    EvidenceMetadata,
    EvidenceMetrics,
    EvidenceNode,
    EvidencePackage,
    EvidenceProvenance,
    EvidenceQuality,
    EvidenceSession,
    EvidenceSource,
)
from adip.evidence.enums import EvidenceDomain, EvidenceStatus, EvidenceType

# ═══════════════════════════════════════════════════════════════════════════════
# EvidenceSource
# ═══════════════════════════════════════════════════════════════════════════════

class TestEvidenceSource:
    def test_defaults(self) -> None:
        s = EvidenceSource()
        assert s.source_id == ""
        assert s.source_type == ""
        assert s.manager == ""
        assert s.version == ""

    def test_with_values(self) -> None:
        s = EvidenceSource(
            source_id="src-1",
            source_type="knowledge",
            manager="KnowledgeManager",
            version="1.0.0",
        )
        assert s.source_id == "src-1"
        assert s.source_type == "knowledge"
        assert s.manager == "KnowledgeManager"
        assert s.version == "1.0.0"

    def test_serialisation(self) -> None:
        s = EvidenceSource(source_id="src-1")
        data = s.model_dump()
        assert data["source_id"] == "src-1"

    def test_deserialisation(self) -> None:
        data = {"source_id": "src-1", "source_type": "memory", "manager": "MemoryManager", "version": "2.0.0"}
        s = EvidenceSource.model_validate(data)
        assert s.source_id == "src-1"
        assert s.source_type == "memory"


# ═══════════════════════════════════════════════════════════════════════════════
# EvidenceMetadata
# ═══════════════════════════════════════════════════════════════════════════════

class TestEvidenceMetadata:
    def test_defaults(self) -> None:
        m = EvidenceMetadata()
        assert m.title == ""
        assert m.description == ""
        assert m.tags == []
        assert m.category == ""
        assert m.source == ""
        assert m.additional == {}

    def test_with_values(self) -> None:
        m = EvidenceMetadata(
            title="Sensor Reading",
            description="Temperature sensor reading from zone A",
            tags=["sensor", "temperature"],
            category="telemetry",
            source="sensor-01",
            additional={"unit": "celsius"},
        )
        assert m.title == "Sensor Reading"
        assert len(m.tags) == 2
        assert m.additional["unit"] == "celsius"

    def test_tags_mutable(self) -> None:
        m = EvidenceMetadata(tags=["a"])
        m.tags.append("b")
        assert m.tags == ["a", "b"]

    def test_serialisation(self) -> None:
        m = EvidenceMetadata(title="Test")
        data = m.model_dump()
        assert data["title"] == "Test"
        assert data["tags"] == []


# ═══════════════════════════════════════════════════════════════════════════════
# EvidenceProvenance
# ═══════════════════════════════════════════════════════════════════════════════

class TestEvidenceProvenance:
    def test_defaults(self) -> None:
        p = EvidenceProvenance()
        assert p.source == ""
        assert p.source_type == ""
        assert p.manager == ""
        assert p.version == ""
        assert p.owner == ""
        assert p.original_identifier == ""
        assert p.retrieved_at is not None

    def test_with_values(self) -> None:
        now = datetime.now(UTC)
        p = EvidenceProvenance(
            source="KnowledgeManager",
            source_type="service",
            manager="KnowledgeManager",
            version="1.0.0",
            retrieved_at=now,
            owner="user1",
            original_identifier="doc-123",
        )
        assert p.source == "KnowledgeManager"
        assert p.retrieved_at == now
        assert p.original_identifier == "doc-123"

    def test_timestamp_generated(self) -> None:
        p1 = EvidenceProvenance()
        p2 = EvidenceProvenance()
        assert p1.retrieved_at is not None
        assert p2.retrieved_at is not None


# ═══════════════════════════════════════════════════════════════════════════════
# EvidenceQuality
# ═══════════════════════════════════════════════════════════════════════════════

class TestEvidenceQuality:
    def test_defaults(self) -> None:
        q = EvidenceQuality()
        assert q.freshness == 0.0
        assert q.completeness == 0.0
        assert q.consistency == 0.0
        assert q.reliability == 0.0
        assert q.quality_score == 0.0

    def test_with_values(self) -> None:
        q = EvidenceQuality(
            freshness=0.9,
            completeness=0.8,
            consistency=0.7,
            reliability=0.95,
            quality_score=0.84,
        )
        assert q.freshness == 0.9
        assert q.quality_score == 0.84

    def test_bounds_validation(self) -> None:
        with pytest.raises(ValidationError):
            EvidenceQuality(freshness=1.5)
        with pytest.raises(ValidationError):
            EvidenceQuality(completeness=-0.1)
        with pytest.raises(ValidationError):
            EvidenceQuality(quality_score=1.01)

    def test_serialisation(self) -> None:
        q = EvidenceQuality(freshness=0.5, completeness=0.5, consistency=0.5, reliability=0.5, quality_score=0.5)
        data = q.model_dump()
        assert data["freshness"] == 0.5


# ═══════════════════════════════════════════════════════════════════════════════
# Evidence
# ═══════════════════════════════════════════════════════════════════════════════

class TestEvidence:
    def test_defaults(self) -> None:
        e = Evidence()
        assert e.evidence_type == EvidenceType.KNOWLEDGE
        assert e.domain == EvidenceDomain.SYSTEM
        assert e.status == EvidenceStatus.COLLECTED
        assert e.payload == {}

    def test_with_values(self) -> None:
        e = Evidence(
            evidence_id=uuid.uuid4(),
            evidence_type=EvidenceType.SENSOR,
            domain=EvidenceDomain.ENERGY,
            status=EvidenceStatus.VALIDATED,
            payload={"temperature": 25.5, "unit": "celsius"},
        )
        assert e.evidence_type == EvidenceType.SENSOR
        assert e.domain == EvidenceDomain.ENERGY
        assert e.status == EvidenceStatus.VALIDATED
        assert e.payload["temperature"] == 25.5

    def test_evidence_id_generated(self) -> None:
        e1 = Evidence()
        e2 = Evidence()
        assert e1.evidence_id != e2.evidence_id

    def test_timestamp_generated(self) -> None:
        e = Evidence()
        assert e.timestamp is not None

    def test_nested_models(self) -> None:
        e = Evidence(
            source=EvidenceSource(source_id="src-1"),
            metadata=EvidenceMetadata(title="Test Evidence"),
            provenance=EvidenceProvenance(owner="user1"),
            quality=EvidenceQuality(quality_score=0.95),
        )
        assert e.source.source_id == "src-1"
        assert e.metadata.title == "Test Evidence"
        assert e.provenance.owner == "user1"
        assert e.quality.quality_score == 0.95

    def test_serialisation(self) -> None:
        e = Evidence(evidence_type=EvidenceType.REPORT)
        data = e.model_dump()
        assert data["evidence_type"] == "REPORT"

    def test_deserialisation(self) -> None:
        data = {
            "evidence_type": "SENSOR",
            "domain": "ENERGY",
            "status": "COLLECTED",
            "payload": {"value": 42},
        }
        e = Evidence.model_validate(data)
        assert e.evidence_type == EvidenceType.SENSOR
        assert e.payload["value"] == 42


# ═══════════════════════════════════════════════════════════════════════════════
# EvidenceNode
# ═══════════════════════════════════════════════════════════════════════════════

class TestEvidenceNode:
    def test_defaults(self) -> None:
        n = EvidenceNode(evidence_id=uuid.uuid4())
        assert n.node_id == ""
        assert n.label == ""
        assert n.metadata == {}

    def test_with_values(self) -> None:
        eid = uuid.uuid4()
        n = EvidenceNode(
            node_id="node-1",
            evidence_id=eid,
            evidence_type=EvidenceType.SENSOR,
            domain=EvidenceDomain.ENERGY,
            label="Temperature Sensor",
            metadata={"location": "Zone A"},
        )
        assert n.node_id == "node-1"
        assert n.evidence_id == eid
        assert n.label == "Temperature Sensor"

    def test_evidence_id_required(self) -> None:
        with pytest.raises(ValidationError):
            EvidenceNode()

    def test_serialisation(self) -> None:
        n = EvidenceNode(evidence_id=uuid.uuid4(), node_id="n1", label="Node 1")
        data = n.model_dump()
        assert data["node_id"] == "n1"
        assert data["label"] == "Node 1"


# ═══════════════════════════════════════════════════════════════════════════════
# EvidenceEdge
# ═══════════════════════════════════════════════════════════════════════════════

class TestEvidenceEdge:
    def test_defaults(self) -> None:
        e = EvidenceEdge()
        assert e.edge_id == ""
        assert e.source_node_id == ""
        assert e.target_node_id == ""
        assert e.relationship == ""
        assert e.weight == 0.0
        assert e.metadata == {}

    def test_with_values(self) -> None:
        e = EvidenceEdge(
            edge_id="edge-1",
            source_node_id="node-1",
            target_node_id="node-2",
            relationship="supports",
            weight=0.85,
            metadata={"strength": "strong"},
        )
        assert e.edge_id == "edge-1"
        assert e.relationship == "supports"
        assert e.weight == 0.85

    def test_weight_bounds(self) -> None:
        with pytest.raises(ValidationError):
            EvidenceEdge(weight=1.5)
        with pytest.raises(ValidationError):
            EvidenceEdge(weight=-0.1)

    def test_serialisation(self) -> None:
        e = EvidenceEdge(edge_id="e1", source_node_id="a", target_node_id="b", relationship="related")
        data = e.model_dump()
        assert data["relationship"] == "related"


# ═══════════════════════════════════════════════════════════════════════════════
# EvidenceGraph
# ═══════════════════════════════════════════════════════════════════════════════

class TestEvidenceGraph:
    def test_defaults(self) -> None:
        g = EvidenceGraph()
        assert g.nodes == []
        assert g.edges == []

    def test_with_values(self) -> None:
        eid = uuid.uuid4()
        node = EvidenceNode(evidence_id=eid, node_id="n1", label="Node 1")
        edge = EvidenceEdge(edge_id="e1", source_node_id="n1", target_node_id="n2", relationship="connects")
        g = EvidenceGraph(nodes=[node], edges=[edge])
        assert len(g.nodes) == 1
        assert len(g.edges) == 1
        assert g.nodes[0].label == "Node 1"

    def test_nodes_mutable(self) -> None:
        g = EvidenceGraph()
        g.nodes.append(EvidenceNode(evidence_id=uuid.uuid4(), node_id="n1", label="N1"))
        assert len(g.nodes) == 1

    def test_serialisation(self) -> None:
        g = EvidenceGraph()
        data = g.model_dump()
        assert data["nodes"] == []
        assert data["edges"] == []


# ═══════════════════════════════════════════════════════════════════════════════
# EvidencePackage
# ═══════════════════════════════════════════════════════════════════════════════

class TestEvidencePackage:
    def test_defaults(self) -> None:
        p = EvidencePackage()
        assert p.evidence_ids == []
        assert p.fused_evidence == {}
        assert p.graph is None
        assert p.confidence == 0.0

    def test_with_values(self) -> None:
        eid1 = uuid.uuid4()
        eid2 = uuid.uuid4()
        p = EvidencePackage(
            evidence_ids=[eid1, eid2],
            fused_evidence={"key": "value"},
            confidence=0.85,
        )
        assert len(p.evidence_ids) == 2
        assert p.fused_evidence["key"] == "value"
        assert p.confidence == 0.85

    def test_package_id_generated(self) -> None:
        p1 = EvidencePackage()
        p2 = EvidencePackage()
        assert p1.package_id != p2.package_id

    def test_confidence_bounds(self) -> None:
        with pytest.raises(ValidationError):
            EvidencePackage(confidence=1.1)
        with pytest.raises(ValidationError):
            EvidencePackage(confidence=-0.1)

    def test_with_graph(self) -> None:
        g = EvidenceGraph()
        p = EvidencePackage(graph=g)
        assert p.graph is not None

    def test_serialisation(self) -> None:
        p = EvidencePackage(confidence=0.5)
        data = p.model_dump()
        assert data["confidence"] == 0.5

    def test_deserialisation(self) -> None:
        data = {"confidence": 0.75, "evidence_ids": []}
        p = EvidencePackage.model_validate(data)
        assert p.confidence == 0.75


# ═══════════════════════════════════════════════════════════════════════════════
# EvidenceHealth
# ═══════════════════════════════════════════════════════════════════════════════

class TestEvidenceHealth:
    def test_defaults(self) -> None:
        h = EvidenceHealth()
        assert h.overall_status == "UNKNOWN"
        assert h.evidence_count == 0
        assert h.collector_status == "UNKNOWN"
        assert h.validator_status == "UNKNOWN"
        assert h.normalizer_status == "UNKNOWN"
        assert h.correlator_status == "UNKNOWN"
        assert h.scorer_status == "UNKNOWN"
        assert h.graph_builder_status == "UNKNOWN"
        assert h.error_count == 0
        assert h.uptime_seconds == 0.0

    def test_with_values(self) -> None:
        h = EvidenceHealth(
            overall_status="HEALTHY",
            evidence_count=100,
            collector_status="HEALTHY",
            validator_status="HEALTHY",
            normalizer_status="HEALTHY",
            correlator_status="HEALTHY",
            scorer_status="HEALTHY",
            graph_builder_status="HEALTHY",
            error_count=0,
            uptime_seconds=3600.0,
        )
        assert h.overall_status == "HEALTHY"
        assert h.evidence_count == 100
        assert h.uptime_seconds == 3600.0

    def test_negative_values_rejected(self) -> None:
        with pytest.raises(ValidationError):
            EvidenceHealth(evidence_count=-1)
        with pytest.raises(ValidationError):
            EvidenceHealth(error_count=-1)
        with pytest.raises(ValidationError):
            EvidenceHealth(uptime_seconds=-1.0)

    def test_timestamp_generated(self) -> None:
        h = EvidenceHealth()
        assert h.last_check is not None

    def test_serialisation(self) -> None:
        h = EvidenceHealth(overall_status="DEGRADED")
        data = h.model_dump()
        assert data["overall_status"] == "DEGRADED"


# ═══════════════════════════════════════════════════════════════════════════════
# EvidenceMetrics
# ═══════════════════════════════════════════════════════════════════════════════

class TestEvidenceMetrics:
    def test_defaults(self) -> None:
        m = EvidenceMetrics()
        assert m.evidence_total == 0
        assert m.packages_total == 0
        assert m.graph_nodes_total == 0
        assert m.graph_edges_total == 0
        assert m.validations_total == 0
        assert m.normalizations_total == 0
        assert m.correlations_total == 0
        assert m.fusions_total == 0
        assert m.errors_total == 0
        assert m.average_quality_score == 0.0

    def test_with_values(self) -> None:
        m = EvidenceMetrics(
            evidence_total=500,
            packages_total=50,
            graph_nodes_total=1000,
            graph_edges_total=2000,
            validations_total=500,
            normalizations_total=500,
            correlations_total=300,
            fusions_total=100,
            errors_total=5,
            average_quality_score=0.82,
        )
        assert m.evidence_total == 500
        assert m.graph_edges_total == 2000
        assert m.average_quality_score == 0.82

    def test_negative_values_rejected(self) -> None:
        with pytest.raises(ValidationError):
            EvidenceMetrics(evidence_total=-1)

    def test_quality_score_bounds(self) -> None:
        with pytest.raises(ValidationError):
            EvidenceMetrics(average_quality_score=1.1)

    def test_timestamp_generated(self) -> None:
        m = EvidenceMetrics()
        assert m.timestamp is not None

    def test_serialisation(self) -> None:
        m = EvidenceMetrics(evidence_total=10)
        data = m.model_dump()
        assert data["evidence_total"] == 10


# ═══════════════════════════════════════════════════════════════════════════════
# EvidenceSession
# ═══════════════════════════════════════════════════════════════════════════════

class TestEvidenceSession:
    def test_defaults(self) -> None:
        s = EvidenceSession()
        assert s.operation == ""
        assert s.user_id == ""
        assert s.correlation_id == ""
        assert s.evidence_count == 0
        assert s.package_count == 0
        assert s.completed_at is None
        assert s.status == "ACTIVE"
        assert s.statistics == {}

    def test_with_values(self) -> None:
        now = datetime.now(UTC)
        s = EvidenceSession(
            session_id=uuid.uuid4(),
            operation="collect",
            user_id="user1",
            correlation_id="corr-1",
            evidence_count=10,
            package_count=2,
            started_at=now,
            completed_at=now,
            status="COMPLETED",
            statistics={"duration_ms": 150.0},
        )
        assert s.operation == "collect"
        assert s.status == "COMPLETED"
        assert s.statistics["duration_ms"] == 150.0

    def test_session_id_generated(self) -> None:
        s1 = EvidenceSession()
        s2 = EvidenceSession()
        assert s1.session_id != s2.session_id

    def test_completed_at_none_when_active(self) -> None:
        s = EvidenceSession()
        assert s.completed_at is None
        assert s.status == "ACTIVE"

    def test_serialisation(self) -> None:
        s = EvidenceSession(operation="fuse")
        data = s.model_dump()
        assert data["operation"] == "fuse"


# ═══════════════════════════════════════════════════════════════════════════════
# EvidenceDecision
# ═══════════════════════════════════════════════════════════════════════════════

class TestEvidenceDecision:
    def test_defaults(self) -> None:
        d = EvidenceDecision(evidence_id=uuid.uuid4())
        assert d.operation == ""
        assert d.allowed is True
        assert d.reasoning == []
        assert d.confidence == 0.0
        assert d.performed_by == ""
        assert d.metadata == {}

    def test_with_values(self) -> None:
        eid = uuid.uuid4()
        d = EvidenceDecision(
            evidence_id=eid,
            operation="validate",
            allowed=True,
            reasoning=["Evidence passed validation"],
            confidence=0.95,
            performed_by="system",
            metadata={"source": "validator"},
        )
        assert d.evidence_id == eid
        assert d.operation == "validate"
        assert d.reasoning[0] == "Evidence passed validation"
        assert d.confidence == 0.95

    def test_decision_id_generated(self) -> None:
        d1 = EvidenceDecision(evidence_id=uuid.uuid4())
        d2 = EvidenceDecision(evidence_id=uuid.uuid4())
        assert d1.decision_id != d2.decision_id

    def test_evidence_id_required(self) -> None:
        with pytest.raises(ValidationError):
            EvidenceDecision()

    def test_confidence_bounds(self) -> None:
        with pytest.raises(ValidationError):
            EvidenceDecision(evidence_id=uuid.uuid4(), confidence=1.5)

    def test_serialisation(self) -> None:
        eid = uuid.uuid4()
        d = EvidenceDecision(evidence_id=eid, operation="fuse")
        data = d.model_dump()
        assert data["operation"] == "fuse"
        assert str(data["evidence_id"]) == str(eid)

    def test_deserialisation(self) -> None:
        eid = uuid.uuid4()
        data = {"evidence_id": str(eid), "operation": "collect", "allowed": False}
        d = EvidenceDecision.model_validate(data)
        assert d.evidence_id == eid
        assert d.allowed is False
