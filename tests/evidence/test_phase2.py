"""Tests for Evidence Fusion Engine Phase 2 (Execution Pipeline).

Covers all 20+ execution components with deterministic placeholder tests.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from adip.evidence.contracts.models import (
    Evidence,
    EvidenceMetadata,
    EvidenceProvenance,
    EvidenceSource,
)
from adip.evidence.enums import (
    BundleType,
    EvidenceClassification,
    EvidenceDomain,
    EvidencePriority,
    EvidenceStatus,
    EvidenceType,
    RelationshipType,
)

# ═══════════════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════════════

def make_evidence(
    evidence_id: uuid.UUID | None = None,
    source_id: str = "test-source",
    source_type: str = "TEST",
    evidence_type: EvidenceType = EvidenceType.KNOWLEDGE,
    domain: EvidenceDomain = EvidenceDomain.SYSTEM,
    status: EvidenceStatus = EvidenceStatus.COLLECTED,
    payload: dict[str, Any] | None = None,
    entity_id: str | None = "entity-123",
    metadata: dict[str, Any] | None = None,
    timestamp: datetime | None = None,
    provenance_source: str | None = None,
) -> Evidence:
    """Create a test Evidence object with sensible defaults."""
    now = timestamp or datetime.now(UTC)
    extra = dict(metadata or {})
    if entity_id:
        extra["entity_id"] = entity_id
    source = EvidenceSource(
        source_id=source_id,
        source_type=source_type,
        manager=f"{source_type.lower()}_manager",
        version="1.0",
    )
    provenance = EvidenceProvenance(
        source=provenance_source or source_id,
        source_type=source_type,
        manager="test-manager",
        version="1.0",
        retrieved_at=now,
        owner="test-owner",
        original_identifier=str(uuid.uuid4()),
    )
    return Evidence(
        evidence_id=evidence_id or uuid.uuid4(),
        evidence_type=evidence_type,
        domain=domain,
        status=status,
        source=source,
        metadata=EvidenceMetadata(
            title="Test evidence",
            description="Test description",
            additional=extra,
        ),
        provenance=provenance,
        payload=payload or {},
        timestamp=now,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# EvidenceCollector Tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestEvidenceCollector:
    def test_collect_single(self):
        from adip.evidence.execution.collector import EvidenceCollector
        collector = EvidenceCollector()
        result = collector.collect(
            evidence_type=EvidenceType.SENSOR,
            domain=EvidenceDomain.ENERGY,
            payload={"temperature": 25.5},
        )
        assert result.evidence_type == EvidenceType.SENSOR
        assert result.domain == EvidenceDomain.ENERGY
        assert result.status == EvidenceStatus.COLLECTED
        assert result.payload == {"temperature": 25.5}
        assert result.provenance is not None
        assert result.source is not None

    def test_collect_with_custom_ids(self):
        from adip.evidence.execution.collector import EvidenceCollector
        collector = EvidenceCollector()
        result = collector.collect(
            evidence_type=EvidenceType.KNOWLEDGE,
            domain=EvidenceDomain.SECURITY,
            source_id="custom-source",
            entity_id="entity-999",
        )
        assert result.source.source_id == "custom-source"
        assert result.metadata.additional.get("entity_id") == "entity-999"

    def test_collect_batch(self):
        from adip.evidence.execution.collector import EvidenceCollector
        collector = EvidenceCollector()
        items = [{"id": 1}, {"id": 2}, {"id": 3}]
        results = collector.collect_batch(
            evidence_type=EvidenceType.MEMORY,
            domain=EvidenceDomain.OPERATIONS,
            items=items,
        )
        assert len(results) == 3
        for r in results:
            assert r.evidence_type == EvidenceType.MEMORY
            assert r.domain == EvidenceDomain.OPERATIONS
            assert r.status == EvidenceStatus.COLLECTED

    def test_collect_all_evidence_types(self):
        from adip.evidence.execution.collector import EvidenceCollector
        collector = EvidenceCollector()
        for etype in EvidenceType:
            result = collector.collect(
                evidence_type=etype,
                domain=EvidenceDomain.SYSTEM,
            )
            assert result.evidence_type == etype
            assert result.status == EvidenceStatus.COLLECTED

    def test_collect_provenance_generated(self):
        from adip.evidence.execution.collector import EvidenceCollector
        collector = EvidenceCollector()
        result = collector.collect(
            evidence_type=EvidenceType.SENSOR,
            domain=EvidenceDomain.ENERGY,
        )
        assert result.provenance.source is not None
        assert result.provenance.manager is not None

    def test_collect_metadata_propagation(self):
        from adip.evidence.execution.collector import EvidenceCollector
        collector = EvidenceCollector()
        result = collector.collect(
            evidence_type=EvidenceType.RULE,
            domain=EvidenceDomain.COMPLIANCE,
            metadata={"priority": "high", "version": "2.0"},
        )
        assert result.metadata.additional["priority"] == "high"
        assert result.metadata.additional["version"] == "2.0"

    def test_collect_empty_payload(self):
        from adip.evidence.execution.collector import EvidenceCollector
        collector = EvidenceCollector()
        result = collector.collect(
            evidence_type=EvidenceType.REPORT,
            domain=EvidenceDomain.WORKFLOW,
        )
        assert result.payload == {}


# ═══════════════════════════════════════════════════════════════════════════════
# EvidenceValidator Tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestEvidenceValidator:
    def test_valid_evidence(self):
        from adip.evidence.execution.validator import EvidenceValidator
        validator = EvidenceValidator()
        ev = make_evidence()
        violations = validator.validate(ev)
        assert violations == []

    def test_empty_source_id(self):
        from adip.evidence.execution.validator import EvidenceValidator
        validator = EvidenceValidator()
        ev = make_evidence(source_id="")
        violations = validator.validate(ev)
        assert any("source_id" in v for v in violations)

    def test_timestamp_future(self):
        from adip.evidence.execution.validator import EvidenceValidator
        validator = EvidenceValidator()
        future = datetime.now(UTC) + timedelta(hours=1)
        ev = make_evidence(timestamp=future)
        violations = validator.validate(ev)
        assert any("future" in v for v in violations)

    def test_missing_provenance(self):
        from adip.evidence.execution.validator import EvidenceValidator
        validator = EvidenceValidator()
        ev = make_evidence()
        ev.provenance = None
        violations = validator.validate(ev)
        assert any("provenance" in v for v in violations)


# ═══════════════════════════════════════════════════════════════════════════════
# EvidenceNormalizer Tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestEvidenceNormalizer:
    def test_normalize_source_id_lowercase(self):
        from adip.evidence.execution.normalizer import EvidenceNormalizer
        normalizer = EvidenceNormalizer()
        ev = make_evidence(source_id="UPPER-CASE-SOURCE")
        result = normalizer.normalize(ev)
        assert result.source.source_id == "upper-case-source"

    def test_normalize_domain_uppercase(self):
        from adip.evidence.execution.normalizer import EvidenceNormalizer
        normalizer = EvidenceNormalizer()
        ev = make_evidence(domain=EvidenceDomain.SYSTEM)
        result = normalizer.normalize(ev)
        assert result.domain == "SYSTEM"

    def test_normalize_timestamps_utc(self):
        from adip.evidence.execution.normalizer import EvidenceNormalizer
        normalizer = EvidenceNormalizer()
        naive = datetime(2024, 1, 1, 12, 0, 0)
        ev = make_evidence(timestamp=naive)
        result = normalizer.normalize(ev)
        assert result.timestamp.tzinfo is not None

    def test_normalize_null_metadata(self):
        from adip.evidence.execution.normalizer import EvidenceNormalizer
        normalizer = EvidenceNormalizer()
        ev = make_evidence(metadata={"key": None, "other": "value"})
        result = normalizer.normalize(ev)
        assert result.metadata.additional["key"] == ""
        assert result.metadata.additional["other"] == "value"

    def test_normalize_batch(self):
        from adip.evidence.execution.normalizer import EvidenceNormalizer
        normalizer = EvidenceNormalizer()
        evs = [
            make_evidence(source_id="SRC-A"),
            make_evidence(source_id="SRC-B"),
        ]
        results = normalizer.normalize_batch(evs)
        assert len(results) == 2
        assert results[0].source.source_id == "src-a"
        assert results[1].source.source_id == "src-b"

    def test_normalize_provenance_source_lowercase(self):
        from adip.evidence.execution.normalizer import EvidenceNormalizer
        normalizer = EvidenceNormalizer()
        ev = make_evidence(provenance_source="MIXED-CASE")
        result = normalizer.normalize(ev)
        assert result.provenance.source == "mixed-case"


# ═══════════════════════════════════════════════════════════════════════════════
# EvidenceClassificationManager Tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestEvidenceClassificationManager:
    def test_sensor_classification(self):
        from adip.evidence.execution.classification_manager import (
            EvidenceClassificationManager,
        )
        mgr = EvidenceClassificationManager()
        ev = make_evidence(evidence_type=EvidenceType.SENSOR)
        assert mgr.classify(ev) == EvidenceClassification.REAL_TIME

    def test_knowledge_classification(self):
        from adip.evidence.execution.classification_manager import (
            EvidenceClassificationManager,
        )
        mgr = EvidenceClassificationManager()
        ev = make_evidence(evidence_type=EvidenceType.KNOWLEDGE)
        assert mgr.classify(ev) == EvidenceClassification.PRIMARY

    def test_rule_classification(self):
        from adip.evidence.execution.classification_manager import (
            EvidenceClassificationManager,
        )
        mgr = EvidenceClassificationManager()
        ev = make_evidence(evidence_type=EvidenceType.RULE)
        assert mgr.classify(ev) == EvidenceClassification.DERIVED

    def test_planner_classification(self):
        from adip.evidence.execution.classification_manager import (
            EvidenceClassificationManager,
        )
        mgr = EvidenceClassificationManager()
        ev = make_evidence(evidence_type=EvidenceType.PLANNER)
        assert mgr.classify(ev) == EvidenceClassification.PREDICTIVE

    def test_memory_classification(self):
        from adip.evidence.execution.classification_manager import (
            EvidenceClassificationManager,
        )
        mgr = EvidenceClassificationManager()
        ev = make_evidence(evidence_type=EvidenceType.MEMORY)
        assert mgr.classify(ev) == EvidenceClassification.HISTORICAL

    def test_unknown_classification_defaults_to_secondary(self):
        from adip.evidence.execution.classification_manager import (
            EvidenceClassificationManager,
        )
        mgr = EvidenceClassificationManager()
        ev = make_evidence(evidence_type=EvidenceType.EMAIL)
        assert mgr.classify(ev) == EvidenceClassification.SECONDARY


# ═══════════════════════════════════════════════════════════════════════════════
# EvidencePriorityAssigner Tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestEvidencePriorityAssigner:
    def test_sensor_priority(self):
        from adip.evidence.execution.priority import EvidencePriorityAssigner
        assigner = EvidencePriorityAssigner()
        ev = make_evidence(evidence_type=EvidenceType.SENSOR)
        assert assigner.assign_priority(ev) == EvidencePriority.HIGH

    def test_incident_priority(self):
        from adip.evidence.execution.priority import EvidencePriorityAssigner
        assigner = EvidencePriorityAssigner()
        ev = make_evidence(evidence_type=EvidenceType.INCIDENT)
        assert assigner.assign_priority(ev) == EvidencePriority.CRITICAL

    def test_planner_priority(self):
        from adip.evidence.execution.priority import EvidencePriorityAssigner
        assigner = EvidencePriorityAssigner()
        ev = make_evidence(evidence_type=EvidenceType.PLANNER)
        assert assigner.assign_priority(ev) == EvidencePriority.CRITICAL

    def test_email_priority(self):
        from adip.evidence.execution.priority import EvidencePriorityAssigner
        assigner = EvidencePriorityAssigner()
        ev = make_evidence(evidence_type=EvidenceType.EMAIL)
        assert assigner.assign_priority(ev) == EvidencePriority.INFORMATIONAL


# ═══════════════════════════════════════════════════════════════════════════════
# EvidenceTrustManager Tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestEvidenceTrustManager:
    def test_calculate_trust_score(self):
        from adip.evidence.execution.trust_manager import EvidenceTrustManager
        mgr = EvidenceTrustManager()
        ev = make_evidence()
        score = mgr.calculate_trust_score(ev)
        assert 0.0 <= score.score <= 1.0
        assert 0.0 <= score.source_reliability <= 1.0
        assert 0.0 <= score.historical_accuracy <= 1.0
        assert 0.0 <= score.validation_status <= 1.0
        assert 0.0 <= score.provenance <= 1.0

    def test_trust_score_missing_provenance(self):
        from adip.evidence.execution.trust_manager import EvidenceTrustManager
        mgr = EvidenceTrustManager()
        ev = make_evidence()
        ev.provenance = None
        score = mgr.calculate_trust_score(ev)
        assert score.provenance == 0.0


# ═══════════════════════════════════════════════════════════════════════════════
# EvidenceCorrelator Tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestEvidenceCorrelator:
    def test_correlate_single(self):
        from adip.evidence.execution.correlator import EvidenceCorrelator
        correlator = EvidenceCorrelator()
        ev = make_evidence()
        pool = [make_evidence(source_id="other")]
        result = correlator.correlate(ev, pool)
        assert result.source_evidence_id == ev.evidence_id

    def test_correlate_same_source(self):
        from adip.evidence.execution.correlator import EvidenceCorrelator
        correlator = EvidenceCorrelator()
        ev = make_evidence(source_id="shared-source")
        pool = [make_evidence(source_id="shared-source")]
        result = correlator.correlate(ev, pool)
        assert len(result.correlated_evidence_ids) == 1
        assert result.source_score > 0

    def test_correlate_same_domain(self):
        from adip.evidence.execution.correlator import EvidenceCorrelator
        correlator = EvidenceCorrelator()
        ev = make_evidence(domain=EvidenceDomain.ENERGY)
        pool = [make_evidence(domain=EvidenceDomain.ENERGY)]
        result = correlator.correlate(ev, pool)
        assert len(result.correlated_evidence_ids) >= 1

    def test_correlate_batch(self):
        from adip.evidence.execution.correlator import EvidenceCorrelator
        correlator = EvidenceCorrelator()
        evs = [make_evidence() for _ in range(5)]
        results = correlator.correlate_batch(evs)
        assert len(results) == 5

    def test_correlate_no_match(self):
        from adip.evidence.execution.correlator import EvidenceCorrelator
        correlator = EvidenceCorrelator()
        now = datetime.now(UTC)
        ev1 = make_evidence(source_id="src-a", domain=EvidenceDomain.ENERGY, entity_id="entity-a", timestamp=now)
        ev2 = make_evidence(source_id="src-b", domain=EvidenceDomain.SECURITY, entity_id="entity-b", timestamp=now - timedelta(hours=2))
        result = correlator.correlate(ev1, [ev2])
        assert len(result.correlated_evidence_ids) == 0


# ═══════════════════════════════════════════════════════════════════════════════
# EvidenceConflictDetector Tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestEvidenceConflictDetector:
    def test_no_conflicts(self):
        from adip.evidence.execution.conflict_detector import EvidenceConflictDetector
        detector = EvidenceConflictDetector()
        evs = [
            make_evidence(source_id="src-a", payload={"a": 1}, entity_id="entity-a"),
            make_evidence(source_id="src-b", payload={"b": 2}, entity_id="entity-b"),
        ]
        report = detector.detect(evs)
        assert not report.has_conflicts

    def test_duplicate_payload(self):
        from adip.evidence.execution.conflict_detector import EvidenceConflictDetector
        detector = EvidenceConflictDetector()
        payload = {"value": 42}
        evs = [
            make_evidence(payload=payload, entity_id="entity-a"),
            make_evidence(payload=payload, entity_id="entity-b"),
        ]
        report = detector.detect(evs)
        assert len(report.duplicate_pairs) >= 1

    def test_contradictory_same_source(self):
        from adip.evidence.execution.conflict_detector import EvidenceConflictDetector
        detector = EvidenceConflictDetector()
        evs = [
            make_evidence(source_id="same", payload={"status": "ok"}, entity_id="entity-a"),
            make_evidence(source_id="same", payload={"status": "error"}, entity_id="entity-b"),
        ]
        report = detector.detect(evs)
        assert len(report.contradictory_pairs) >= 1

    def test_missing_entity_id(self):
        from adip.evidence.execution.conflict_detector import EvidenceConflictDetector
        detector = EvidenceConflictDetector()
        evs = [make_evidence(entity_id="")]
        report = detector.detect(evs)
        assert len(report.missing_evidence_ids) >= 1

    def test_stale_evidence(self):
        from adip.evidence.execution.conflict_detector import EvidenceConflictDetector
        detector = EvidenceConflictDetector()
        old = datetime.now(UTC) - timedelta(days=2)
        evs = [make_evidence(timestamp=old)]
        report = detector.detect(evs)
        assert len(report.stale_evidence_ids) >= 1

    def test_conflict_count(self):
        from adip.evidence.execution.conflict_detector import EvidenceConflictDetector
        detector = EvidenceConflictDetector()
        payload = {"value": 42}
        evs = [
            make_evidence(payload=payload, entity_id="entity-a"),
            make_evidence(payload=payload, entity_id="entity-b"),
        ]
        report = detector.detect(evs)
        assert report.conflict_count > 0

    def test_report_id_generated(self):
        from adip.evidence.execution.conflict_detector import EvidenceConflictDetector
        detector = EvidenceConflictDetector()
        report = detector.detect([])
        assert report.report_id != ""


# ═══════════════════════════════════════════════════════════════════════════════
# EvidenceDeduplicator Tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestEvidenceDeduplicator:
    def test_no_duplicates(self):
        from adip.evidence.execution.deduplicator import EvidenceDeduplicator
        dedup = EvidenceDeduplicator()
        evs = [
            make_evidence(source_id="src-a", payload={"a": 1}, entity_id="entity-a"),
            make_evidence(source_id="src-b", payload={"b": 2}, entity_id="entity-b"),
        ]
        result = dedup.deduplicate(evs)
        assert len(result) == 2

    def test_exact_duplicate_payload(self):
        from adip.evidence.execution.deduplicator import EvidenceDeduplicator
        dedup = EvidenceDeduplicator()
        payload = {"value": 42}
        evs = [
            make_evidence(payload=payload, entity_id="entity-a"),
            make_evidence(payload=payload, entity_id="entity-b"),
        ]
        result = dedup.deduplicate(evs)
        assert len(result) == 1

    def test_source_entity_duplicate(self):
        from adip.evidence.execution.deduplicator import EvidenceDeduplicator
        dedup = EvidenceDeduplicator()
        evs = [
            make_evidence(source_id="same", entity_id="same-entity", payload={"a": 1}),
            make_evidence(source_id="same", entity_id="same-entity", payload={"b": 2}),
        ]
        result = dedup.deduplicate(evs)
        assert len(result) == 1

    def test_timeline_duplicate(self):
        from adip.evidence.execution.deduplicator import EvidenceDeduplicator
        dedup = EvidenceDeduplicator()
        now = datetime.now(UTC)
        evs = [
            make_evidence(source_id="same", timestamp=now, payload={"a": 1}),
            make_evidence(source_id="same", timestamp=now + timedelta(seconds=30), payload={"b": 2}),
        ]
        result = dedup.deduplicate(evs)
        assert len(result) == 1

    def test_is_duplicate_exact(self):
        from adip.evidence.execution.deduplicator import EvidenceDeduplicator
        dedup = EvidenceDeduplicator()
        payload = {"x": 1}
        a = make_evidence(payload=payload)
        b = make_evidence(payload=payload)
        assert dedup.is_duplicate(a, b)

    def test_not_duplicate(self):
        from adip.evidence.execution.deduplicator import EvidenceDeduplicator
        dedup = EvidenceDeduplicator()
        a = make_evidence(source_id="src-a", payload={"x": 1})
        b = make_evidence(source_id="src-b", payload={"y": 2})
        assert not dedup.is_duplicate(a, b)


# ═══════════════════════════════════════════════════════════════════════════════
# EvidenceGraphBuilder Tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestEvidenceGraphBuilder:
    def test_empty_list(self):
        from adip.evidence.execution.graph_builder import EvidenceGraphBuilder
        builder = EvidenceGraphBuilder()
        graph = builder.build_graph([])
        assert len(graph.nodes) == 0
        assert len(graph.edges) == 0

    def test_single_evidence_no_edges(self):
        from adip.evidence.execution.graph_builder import EvidenceGraphBuilder
        builder = EvidenceGraphBuilder()
        graph = builder.build_graph([make_evidence()])
        assert len(graph.nodes) == 1
        assert len(graph.edges) == 0

    def test_same_source_edge(self):
        from adip.evidence.execution.graph_builder import EvidenceGraphBuilder
        builder = EvidenceGraphBuilder()
        evs = [
            make_evidence(source_id="shared"),
            make_evidence(source_id="shared"),
        ]
        graph = builder.build_graph(evs)
        assert len(graph.nodes) == 2
        assert any(e.relationship == RelationshipType.SUPPORTS for e in graph.edges)

    def test_same_domain_edge(self):
        from adip.evidence.execution.graph_builder import EvidenceGraphBuilder
        builder = EvidenceGraphBuilder()
        evs = [
            make_evidence(domain=EvidenceDomain.ENERGY),
            make_evidence(domain=EvidenceDomain.ENERGY),
        ]
        graph = builder.build_graph(evs)
        assert any(e.relationship == RelationshipType.REFERENCES for e in graph.edges)

    def test_same_entity_dependency(self):
        from adip.evidence.execution.graph_builder import EvidenceGraphBuilder
        builder = EvidenceGraphBuilder()
        evs = [
            make_evidence(entity_id="entity-x"),
            make_evidence(entity_id="entity-x"),
        ]
        graph = builder.build_graph(evs)
        assert any(e.relationship == RelationshipType.DEPENDS_ON for e in graph.edges)

    def test_node_attributes(self):
        from adip.evidence.execution.graph_builder import EvidenceGraphBuilder
        builder = EvidenceGraphBuilder()
        ev = make_evidence(evidence_type=EvidenceType.SENSOR, domain=EvidenceDomain.ENERGY)
        graph = builder.build_graph([ev])
        node = graph.nodes[0]
        assert node.evidence_type == "SENSOR"
        assert node.domain == "ENERGY"


# ═══════════════════════════════════════════════════════════════════════════════
# EvidenceBundleManager Tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestEvidenceBundleManager:
    def test_create_bundle(self):
        from adip.evidence.execution.bundle import EvidenceBundleManager
        mgr = EvidenceBundleManager()
        evs = [make_evidence(), make_evidence()]
        bundle = mgr.create_bundle(
            bundle_type=BundleType.INCIDENT,
            bundle_key="incident-001",
            evidence_list=evs,
        )
        assert bundle.bundle_type == BundleType.INCIDENT
        assert bundle.entity_id == "incident-001"
        assert len(bundle.evidence_ids) == 2

    def test_add_to_bundle(self):
        from adip.evidence.execution.bundle import EvidenceBundleManager
        mgr = EvidenceBundleManager()
        ev1 = make_evidence()
        ev2 = make_evidence()
        bundle = mgr.create_bundle(BundleType.ASSET, "asset-001", [ev1])
        updated = mgr.add_to_bundle(bundle, ev2)
        assert len(updated.evidence_ids) == 2

    def test_get_bundle(self):
        from adip.evidence.execution.bundle import EvidenceBundleManager
        mgr = EvidenceBundleManager()
        evs = [make_evidence()]
        bundle = mgr.create_bundle(BundleType.WORKFLOW, "wf-001", evs)
        fetched = mgr.get_bundle(bundle.bundle_id)
        assert fetched is not None
        assert fetched.bundle_id == bundle.bundle_id

    def test_get_nonexistent_bundle(self):
        from adip.evidence.execution.bundle import EvidenceBundleManager
        mgr = EvidenceBundleManager()
        result = mgr.get_bundle(uuid.uuid4())
        assert result is None

    def test_list_bundles(self):
        from adip.evidence.execution.bundle import EvidenceBundleManager
        mgr = EvidenceBundleManager()
        mgr.create_bundle(BundleType.CUSTOMER, "cust-001", [make_evidence()])
        mgr.create_bundle(BundleType.FACILITY, "fac-001", [make_evidence()])
        assert len(mgr.list_bundles()) == 2

    def test_remove_bundle(self):
        from adip.evidence.execution.bundle import EvidenceBundleManager
        mgr = EvidenceBundleManager()
        bundle = mgr.create_bundle(BundleType.INVESTIGATION, "inv-001", [make_evidence()])
        assert mgr.remove_bundle(bundle.bundle_id) is True
        assert mgr.get_bundle(bundle.bundle_id) is None

    def test_remove_nonexistent_bundle(self):
        from adip.evidence.execution.bundle import EvidenceBundleManager
        mgr = EvidenceBundleManager()
        assert mgr.remove_bundle(uuid.uuid4()) is False


# ═══════════════════════════════════════════════════════════════════════════════
# EvidenceTimelineManager Tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestEvidenceTimelineManager:
    def test_build_timeline(self):
        from adip.evidence.execution.timeline import EvidenceTimelineManager
        mgr = EvidenceTimelineManager()
        evs = [make_evidence(), make_evidence()]
        timeline = mgr.build_timeline(evs)
        assert len(timeline.entries) == 2
        assert timeline.timeline_id != ""

    def test_timeline_chronological_order(self):
        from adip.evidence.execution.timeline import EvidenceTimelineManager
        mgr = EvidenceTimelineManager()
        old = datetime.now(UTC) - timedelta(hours=2)
        recent = datetime.now(UTC)
        evs = [
            make_evidence(timestamp=recent),
            make_evidence(timestamp=old),
        ]
        timeline = mgr.build_timeline(evs)
        assert timeline.entries[0].event_time <= timeline.entries[1].event_time

    def test_get_by_time_range(self):
        from adip.evidence.execution.timeline import EvidenceTimelineManager
        mgr = EvidenceTimelineManager()
        now = datetime.now(UTC)
        evs = [
            make_evidence(timestamp=now - timedelta(hours=2)),
            make_evidence(timestamp=now),
        ]
        timeline = mgr.build_timeline(evs)
        start = now - timedelta(hours=1)
        filtered = mgr.get_by_time_range(timeline, start, now)
        assert len(filtered) >= 1


# ═══════════════════════════════════════════════════════════════════════════════
# EvidenceQualityManager Tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestEvidenceQualityManager:
    def test_assess_quality(self):
        from adip.evidence.execution.quality_manager import EvidenceQualityManager
        mgr = EvidenceQualityManager()
        ev = make_evidence()
        assessment = mgr.assess_quality(ev)
        assert 0.0 <= assessment.freshness <= 1.0
        assert 0.0 <= assessment.completeness <= 1.0
        assert 0.0 <= assessment.reliability <= 1.0
        assert 0.0 <= assessment.consistency <= 1.0
        assert 0.0 <= assessment.overall <= 1.0

    def test_assess_batch(self):
        from adip.evidence.execution.quality_manager import EvidenceQualityManager
        mgr = EvidenceQualityManager()
        evs = [make_evidence(), make_evidence()]
        assessments = mgr.assess_batch(evs)
        assert len(assessments) == 2


# ═══════════════════════════════════════════════════════════════════════════════
# EvidenceFreshnessPolicy Tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestEvidenceFreshnessPolicy:
    def test_fresh_evidence(self):
        from adip.evidence.execution.freshness_policy import EvidenceFreshnessPolicy
        policy = EvidenceFreshnessPolicy()
        ev = make_evidence()
        assert policy.is_fresh(ev)

    def test_stale_evidence(self):
        from adip.evidence.execution.freshness_policy import EvidenceFreshnessPolicy
        policy = EvidenceFreshnessPolicy()
        old = datetime.now(UTC) - timedelta(days=2)
        ev = make_evidence(timestamp=old)
        assert not policy.is_fresh(ev)

    def test_custom_threshold(self):
        from adip.evidence.execution.freshness_policy import EvidenceFreshnessPolicy
        policy = EvidenceFreshnessPolicy(thresholds={EvidenceType.KNOWLEDGE: 0.0})
        ev = make_evidence()
        assert not policy.is_fresh(ev)

    def test_get_freshness_score(self):
        from adip.evidence.execution.freshness_policy import EvidenceFreshnessPolicy
        policy = EvidenceFreshnessPolicy()
        ev = make_evidence()
        score = policy.get_freshness(ev)
        assert 0.0 <= score <= 1.0

    def test_get_freshness_zero_for_stale(self):
        from adip.evidence.execution.freshness_policy import EvidenceFreshnessPolicy
        policy = EvidenceFreshnessPolicy()
        old = datetime.now(UTC) - timedelta(days=2)
        ev = make_evidence(timestamp=old)
        assert policy.get_freshness(ev) == 0.0

    def test_set_threshold_updates(self):
        from adip.evidence.execution.freshness_policy import EvidenceFreshnessPolicy
        policy = EvidenceFreshnessPolicy()
        policy.set_threshold(EvidenceType.SENSOR, 999.0)
        assert policy.get_threshold(EvidenceType.SENSOR) == 999.0


# ═══════════════════════════════════════════════════════════════════════════════
# EvidenceSourceReliability Tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestEvidenceSourceReliability:
    def test_default_reliability(self):
        from adip.evidence.execution.source_reliability import EvidenceSourceReliability
        rel = EvidenceSourceReliability()
        assert rel.get_reliability("unknown-source") == 0.5

    def test_record_valid_observation_increases_score(self):
        from adip.evidence.execution.source_reliability import EvidenceSourceReliability
        rel = EvidenceSourceReliability()
        rel.record_observation("src-1", is_valid=True)
        score = rel.get_reliability("src-1")
        assert score > 0.5 or score == 0.5 + 0.3 * 0.5

    def test_record_invalid_observation_decreases_score(self):
        from adip.evidence.execution.source_reliability import EvidenceSourceReliability
        rel = EvidenceSourceReliability()
        rel.record_observation("src-1", is_valid=False)
        assert rel.get_reliability("src-1") < 0.5

    def test_ranking(self):
        from adip.evidence.execution.source_reliability import EvidenceSourceReliability
        rel = EvidenceSourceReliability()
        rel.record_observation("good-src", is_valid=True)
        rel.record_observation("good-src", is_valid=True)
        rel.record_observation("bad-src", is_valid=False)
        ranking = rel.get_ranking()
        assert len(ranking) == 2
        assert ranking[0].source_id == "good-src"


# ═══════════════════════════════════════════════════════════════════════════════
# EvidenceCorrelationScorer Tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestEvidenceCorrelationScorer:
    def test_calculate_scores(self):
        from adip.evidence.execution.correlation_score import EvidenceCorrelationScorer
        scorer = EvidenceCorrelationScorer()
        ev = make_evidence()
        pool = [make_evidence(source_id="other")]
        scores = scorer.calculate(ev, pool)
        assert len(scores) == 1

    def test_same_source_full_match(self):
        from adip.evidence.execution.correlation_score import EvidenceCorrelationScorer
        scorer = EvidenceCorrelationScorer()
        ev = make_evidence(source_id="same")
        pool = [make_evidence(source_id="same")]
        scores = scorer.calculate(ev, pool)
        assert scores[0].source_agreement == 1.0

    def test_no_match(self):
        from adip.evidence.execution.correlation_score import EvidenceCorrelationScorer
        scorer = EvidenceCorrelationScorer()
        ev = make_evidence(source_id="a", domain=EvidenceDomain.ENERGY, entity_id="entity-a")
        pool = [make_evidence(source_id="b", domain=EvidenceDomain.SECURITY, entity_id="entity-b")]
        scores = scorer.calculate(ev, pool)
        assert scores[0].overall < 0.5


# ═══════════════════════════════════════════════════════════════════════════════
# EvidenceCache Tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestEvidenceCache:
    def test_set_and_get_evidence(self):
        from adip.evidence.execution.cache import EvidenceCache
        cache = EvidenceCache()
        ev = make_evidence()
        cache.set_evidence(ev.evidence_id, ev)
        cached = cache.get_evidence(ev.evidence_id)
        assert cached is not None
        assert cached.evidence_id == ev.evidence_id

    def test_get_nonexistent(self):
        from adip.evidence.execution.cache import EvidenceCache
        cache = EvidenceCache()
        assert cache.get_evidence(uuid.uuid4()) is None

    def test_invalidate_evidence(self):
        from adip.evidence.execution.cache import EvidenceCache
        cache = EvidenceCache()
        ev = make_evidence()
        cache.set_evidence(ev.evidence_id, ev)
        assert cache.invalidate_evidence(ev.evidence_id) is True
        assert cache.get_evidence(ev.evidence_id) is None

    def test_bundle_cache(self):
        from adip.evidence.execution.cache import EvidenceCache
        from adip.evidence.execution.models import EvidenceBundle
        cache = EvidenceCache()
        bundle = EvidenceBundle(bundle_type=BundleType.INCIDENT, entity_id="test")
        cache.set_bundle(bundle.bundle_id, bundle)
        cached = cache.get_bundle(bundle.bundle_id)
        assert cached is not None
        assert cached.entity_id == "test"

    def test_size(self):
        from adip.evidence.execution.cache import EvidenceCache
        cache = EvidenceCache()
        for _ in range(5):
            cache.set_evidence(uuid.uuid4(), make_evidence())
        assert cache.size() == 5

    def test_invalidate_all(self):
        from adip.evidence.execution.cache import EvidenceCache
        cache = EvidenceCache()
        cache.set_evidence(uuid.uuid4(), make_evidence())
        cache.invalidate_all()
        assert cache.size() == 0

    def test_set_and_get_graph(self):
        from adip.evidence.execution.cache import EvidenceCache
        from adip.evidence.execution.graph_builder import EvidenceGraph
        cache = EvidenceCache()
        graph = EvidenceGraph(nodes=[], edges=[])
        cache.set_graph("graph-1", graph)
        assert cache.get_graph("graph-1") is not None

    def test_set_and_get_correlation(self):
        from adip.evidence.execution.cache import EvidenceCache
        from adip.evidence.execution.models import CorrelationResult
        cache = EvidenceCache()
        result = CorrelationResult(source_evidence_id=uuid.uuid4())
        cache.set_correlation("corr-1", result)
        assert cache.get_correlation("corr-1") is not None

    def test_set_and_get_timeline(self):
        from adip.evidence.execution.cache import EvidenceCache
        from adip.evidence.execution.models import Timeline
        cache = EvidenceCache()
        timeline = Timeline(timeline_id="tl-1")
        cache.set_timeline("tl-1", timeline)
        assert cache.get_timeline("tl-1") is not None

    def test_invalidate_bundle(self):
        from adip.evidence.execution.cache import EvidenceCache
        from adip.evidence.execution.models import EvidenceBundle
        cache = EvidenceCache()
        bundle = EvidenceBundle(bundle_type=BundleType.INCIDENT, entity_id="test")
        cache.set_bundle(bundle.bundle_id, bundle)
        assert cache.invalidate_bundle(bundle.bundle_id) is True
        assert cache.get_bundle(bundle.bundle_id) is None


# ═══════════════════════════════════════════════════════════════════════════════
# EvidencePolicyEngine Tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestEvidencePolicyEngine:
    def test_check_all_valid(self):
        from adip.evidence.execution.policy import EvidencePolicyEngine
        engine = EvidencePolicyEngine()
        ev = make_evidence()
        violations = engine.check_all(ev)
        assert len(violations) == 0

    def test_check_invalid_domain(self):
        from adip.evidence.execution.policy import EvidencePolicyEngine
        engine = EvidencePolicyEngine(
            allowed_domains=[EvidenceDomain.SYSTEM],
        )
        ev = make_evidence(domain=EvidenceDomain.ENERGY)
        violations = engine.check_domain(ev)
        assert len(violations) > 0

    def test_check_missing_provenance_source(self):
        from adip.evidence.execution.policy import EvidencePolicyEngine
        engine = EvidencePolicyEngine()
        ev = make_evidence()
        ev.provenance.source = ""
        violations = engine.check_provenance(ev)
        assert len(violations) > 0

    def test_check_retention_exceeded(self):
        from adip.evidence.execution.policy import EvidencePolicyEngine
        engine = EvidencePolicyEngine(max_retention_days=0)
        old = datetime.now(UTC) - timedelta(days=1)
        ev = make_evidence(timestamp=old)
        violations = engine.check_retention(ev)
        assert len(violations) > 0

    def test_check_trust_negative(self):
        from adip.evidence.execution.policy import EvidencePolicyEngine
        engine = EvidencePolicyEngine()
        ev = make_evidence()
        violations = engine.check_trust(ev, trust_score=-0.5)
        assert len(violations) > 0

    def test_check_missing_source_id(self):
        from adip.evidence.execution.policy import EvidencePolicyEngine
        engine = EvidencePolicyEngine()
        ev = make_evidence(source_id="")
        violations = engine.check_provenance(ev)
        assert len(violations) > 0


# ═══════════════════════════════════════════════════════════════════════════════
# EvidenceTrace Tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestEvidenceTrace:
    def test_record_event(self):
        from adip.evidence.execution.trace import EvidenceTrace, TraceStage
        trace = EvidenceTrace()
        record = trace.record_event(
            stage=TraceStage.COLLECTION,
            operation="collect",
            evidence_id="ev-001",
        )
        assert record.stage_name == "COLLECTION"
        assert record.operation == "collect"
        assert record.evidence_id == "ev-001"
        assert record.success is True

    def test_get_by_evidence_id(self):
        from adip.evidence.execution.trace import EvidenceTrace, TraceStage
        trace = EvidenceTrace()
        trace.record_event(TraceStage.VALIDATION, "validate", "ev-001")
        trace.record_event(TraceStage.COLLECTION, "collect", "ev-002")
        results = trace.get_by_evidence_id("ev-001")
        assert len(results) == 1

    def test_get_by_stage(self):
        from adip.evidence.execution.trace import EvidenceTrace, TraceStage
        trace = EvidenceTrace()
        trace.record_event(TraceStage.COLLECTION, "collect", "ev-001")
        trace.record_event(TraceStage.COLLECTION, "collect", "ev-002")
        trace.record_event(TraceStage.VALIDATION, "validate", "ev-003")
        results = trace.get_by_stage(TraceStage.COLLECTION)
        assert len(results) == 2

    def test_get_recent(self):
        from adip.evidence.execution.trace import EvidenceTrace, TraceStage
        trace = EvidenceTrace()
        for i in range(20):
            trace.record_event(TraceStage.COLLECTION, "collect", f"ev-{i:03d}")
        recent = trace.get_recent(5)
        assert len(recent) == 5

    def test_clear(self):
        from adip.evidence.execution.trace import EvidenceTrace, TraceStage
        trace = EvidenceTrace()
        trace.record_event(TraceStage.COLLECTION, "collect", "ev-001")
        trace.clear()
        assert trace.count() == 0

    def test_count(self):
        from adip.evidence.execution.trace import EvidenceTrace, TraceStage
        trace = EvidenceTrace()
        for _ in range(5):
            trace.record_event(TraceStage.COLLECTION, "collect", "ev-001")
        assert trace.count() == 5

    def test_all_stages(self):
        from adip.evidence.execution.trace import EvidenceTrace, TraceStage
        trace = EvidenceTrace()
        for stage in TraceStage:
            trace.record_event(stage, "test", "ev-001")
        assert trace.count() == len(TraceStage)


# ═══════════════════════════════════════════════════════════════════════════════
# EvidenceMetricsCollector Tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestEvidenceMetricsCollector:
    def test_snapshot_defaults(self):
        from adip.evidence.execution.metrics import EvidenceMetricsCollector
        collector = EvidenceMetricsCollector()
        metrics = collector.snapshot()
        assert metrics.evidence_count == 0
        assert metrics.bundle_count == 0
        assert metrics.source_count == 0
        assert metrics.domain_count == 0
        assert metrics.correlations_count == 0
        assert metrics.conflicts_count == 0
        assert metrics.average_quality == 0.0

    def test_increment_evidence(self):
        from adip.evidence.execution.metrics import EvidenceMetricsCollector
        collector = EvidenceMetricsCollector()
        collector.increment_evidence(domain="ENERGY", source_id="src-1")
        metrics = collector.snapshot()
        assert metrics.evidence_count == 1
        assert metrics.source_count == 1
        assert metrics.domain_count == 1

    def test_multiple_domains(self):
        from adip.evidence.execution.metrics import EvidenceMetricsCollector
        collector = EvidenceMetricsCollector()
        collector.increment_evidence(domain="ENERGY")
        collector.increment_evidence(domain="SECURITY")
        metrics = collector.snapshot()
        assert metrics.domain_count == 2

    def test_bundle_count(self):
        from adip.evidence.execution.metrics import EvidenceMetricsCollector
        collector = EvidenceMetricsCollector()
        collector.increment_bundle()
        collector.increment_bundle()
        metrics = collector.snapshot()
        assert metrics.bundle_count == 2

    def test_classification_count(self):
        from adip.evidence.execution.metrics import EvidenceMetricsCollector
        collector = EvidenceMetricsCollector()
        collector.record_classification("PRIMARY")
        collector.record_classification("PRIMARY")
        collector.record_classification("SECONDARY")
        metrics = collector.snapshot()
        assert metrics.classification_count["PRIMARY"] == 2
        assert metrics.classification_count["SECONDARY"] == 1

    def test_priority_distribution(self):
        from adip.evidence.execution.metrics import EvidenceMetricsCollector
        collector = EvidenceMetricsCollector()
        collector.record_priority("HIGH")
        collector.record_priority("LOW")
        metrics = collector.snapshot()
        assert metrics.priority_distribution["HIGH"] == 1
        assert metrics.priority_distribution["LOW"] == 1

    def test_trust_distribution(self):
        from adip.evidence.execution.metrics import EvidenceMetricsCollector
        collector = EvidenceMetricsCollector()
        collector.record_trust_score(0.9)
        collector.record_trust_score(0.5)
        collector.record_trust_score(0.1)
        metrics = collector.snapshot()
        assert metrics.trust_distribution["high"] == 1
        assert metrics.trust_distribution["medium"] == 1
        assert metrics.trust_distribution["low"] == 1

    def test_average_quality(self):
        from adip.evidence.execution.metrics import EvidenceMetricsCollector
        collector = EvidenceMetricsCollector()
        collector.record_quality(0.5)
        collector.record_quality(1.0)
        metrics = collector.snapshot()
        assert metrics.average_quality == 0.75

    def test_correlation_count(self):
        from adip.evidence.execution.metrics import EvidenceMetricsCollector
        collector = EvidenceMetricsCollector()
        collector.increment_correlation()
        collector.increment_correlation()
        metrics = collector.snapshot()
        assert metrics.correlations_count == 2

    def test_conflict_count(self):
        from adip.evidence.execution.metrics import EvidenceMetricsCollector
        collector = EvidenceMetricsCollector()
        collector.increment_conflict()
        metrics = collector.snapshot()
        assert metrics.conflicts_count == 1

    def test_trace_count(self):
        from adip.evidence.execution.metrics import EvidenceMetricsCollector
        collector = EvidenceMetricsCollector()
        collector.record_trace()
        collector.record_trace()
        collector.record_trace()
        metrics = collector.snapshot()
        assert metrics.trace_count == 3

    def test_reset(self):
        from adip.evidence.execution.metrics import EvidenceMetricsCollector
        collector = EvidenceMetricsCollector()
        collector.increment_evidence(domain="TEST", source_id="src")
        collector.reset()
        metrics = collector.snapshot()
        assert metrics.evidence_count == 0
        assert metrics.source_count == 0

    def test_metrics_id_generated(self):
        from adip.evidence.execution.metrics import EvidenceMetricsCollector
        collector = EvidenceMetricsCollector()
        metrics = collector.snapshot()
        assert metrics.metrics_id != ""

    def test_multiple_evidence_increments(self):
        from adip.evidence.execution.metrics import EvidenceMetricsCollector
        collector = EvidenceMetricsCollector()
        collector.increment_evidence()
        collector.increment_evidence()
        collector.increment_evidence()
        metrics = collector.snapshot()
        assert metrics.evidence_count == 3

    def test_duplicate_source_count(self):
        from adip.evidence.execution.metrics import EvidenceMetricsCollector
        collector = EvidenceMetricsCollector()
        collector.increment_evidence(source_id="src-A")
        collector.increment_evidence(source_id="src-A")
        metrics = collector.snapshot()
        assert metrics.source_count == 1


# ═══════════════════════════════════════════════════════════════════════════════
# Enum Tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestPhase2Enums:
    def test_evidence_classification_values(self):
        assert EvidenceClassification.PRIMARY.value == "PRIMARY"
        assert EvidenceClassification.SECONDARY.value == "SECONDARY"
        assert EvidenceClassification.SUPPORTING.value == "SUPPORTING"
        assert EvidenceClassification.CONTRADICTORY.value == "CONTRADICTORY"
        assert EvidenceClassification.HISTORICAL.value == "HISTORICAL"
        assert EvidenceClassification.REAL_TIME.value == "REAL_TIME"
        assert EvidenceClassification.PREDICTIVE.value == "PREDICTIVE"
        assert EvidenceClassification.DERIVED.value == "DERIVED"

    def test_evidence_priority_values(self):
        assert EvidencePriority.CRITICAL.value == "CRITICAL"
        assert EvidencePriority.HIGH.value == "HIGH"
        assert EvidencePriority.MEDIUM.value == "MEDIUM"
        assert EvidencePriority.LOW.value == "LOW"
        assert EvidencePriority.INFORMATIONAL.value == "INFORMATIONAL"

    def test_relationship_type_values(self):
        assert RelationshipType.SUPPORTS.value == "SUPPORTS"
        assert RelationshipType.CONTRADICTS.value == "CONTRADICTS"
        assert RelationshipType.CAUSES.value == "CAUSES"
        assert RelationshipType.DEPENDS_ON.value == "DEPENDS_ON"
        assert RelationshipType.DERIVED_FROM.value == "DERIVED_FROM"
        assert RelationshipType.REFERENCES.value == "REFERENCES"
        assert RelationshipType.TEMPORALLY_FOLLOWS.value == "TEMPORALLY_FOLLOWS"

    def test_bundle_type_values(self):
        assert BundleType.ASSET.value == "ASSET"
        assert BundleType.INCIDENT.value == "INCIDENT"
        assert BundleType.CUSTOMER.value == "CUSTOMER"
        assert BundleType.FACILITY.value == "FACILITY"
        assert BundleType.WORKFLOW.value == "WORKFLOW"
        assert BundleType.INVESTIGATION.value == "INVESTIGATION"

    def test_trace_stage_values(self):
        from adip.evidence.execution.trace import TraceStage
        assert TraceStage.COLLECTION.value == "COLLECTION"
        assert TraceStage.VALIDATION.value == "VALIDATION"
        assert TraceStage.NORMALIZATION.value == "NORMALIZATION"
        assert TraceStage.CORRELATION.value == "CORRELATION"
        assert TraceStage.GRAPH_BUILDING.value == "GRAPH_BUILDING"
