"""Phase 3.5 tests for the Evidence Fusion Engine (Enterprise Refinement).

Tests all Phase 3.5 enhancements: weight manager, consensus manager,
lineage, snapshot, FusionPolicy enum, enhanced models, enhanced trace,
enhanced health, enhanced metrics, and backward compatibility.
"""

from __future__ import annotations

import uuid

import pytest
from pydantic import ValidationError

from adip.evidence import (
    ConsensusLevel,
    Evidence,
    EvidenceConfidence,
    EvidenceConsensusManager,
    EvidenceCoordinator,
    EvidenceDecision,
    EvidenceDomain,
    EvidenceExplainabilityMetadata,
    EvidenceHealth,
    EvidenceLineage,
    EvidenceManager,
    EvidenceMetadata,
    EvidenceMetrics,
    EvidenceProvenance,
    EvidenceService,
    EvidenceSnapshot,
    EvidenceSource,
    EvidenceType,
    EvidenceWeightManager,
    FusionPolicyType,
    TraceStage,
)
from adip.evidence.execution.metrics import EvidenceMetricsCollector
from adip.evidence.execution.trace import EvidenceTrace


def _make_evidence(domain: EvidenceDomain = EvidenceDomain.SYSTEM, etype: EvidenceType = EvidenceType.KNOWLEDGE) -> Evidence:
    return Evidence(
        evidence_type=etype,
        domain=domain,
        metadata=EvidenceMetadata(title="Test Evidence", description="A test evidence item"),
        source=EvidenceSource(source_id="src-1", source_type="test"),
        provenance=EvidenceProvenance(owner="admin"),
    )


# ═══════════════════════════════════════════════════════════════════════
# FusionPolicy Enum
# ═══════════════════════════════════════════════════════════════════════


class TestFusionPolicyType:
    def test_values(self) -> None:
        assert FusionPolicyType.STRICT.value == "STRICT"
        assert FusionPolicyType.BALANCED.value == "BALANCED"
        assert FusionPolicyType.PERMISSIVE.value == "PERMISSIVE"
        assert FusionPolicyType.EMERGENCY.value == "EMERGENCY"

    def test_unique_values(self) -> None:
        values = [e.value for e in FusionPolicyType]
        assert len(values) == len(set(values))


class TestConsensusLevel:
    def test_values(self) -> None:
        assert ConsensusLevel.HIGH.value == "HIGH"
        assert ConsensusLevel.MEDIUM.value == "MEDIUM"
        assert ConsensusLevel.LOW.value == "LOW"

    def test_unique_values(self) -> None:
        values = [e.value for e in ConsensusLevel]
        assert len(values) == len(set(values))


# ═══════════════════════════════════════════════════════════════════════
# EvidenceWeightManager
# ═══════════════════════════════════════════════════════════════════════


class TestEvidenceWeightManager:
    def test_calculate_weight_defaults(self) -> None:
        mgr = EvidenceWeightManager()
        weight = mgr.calculate_weight()
        # All defaults 0.5, average = 0.5
        assert weight == 0.5

    def test_calculate_weight_with_values(self) -> None:
        mgr = EvidenceWeightManager()
        weight = mgr.calculate_weight(
            quality_score=1.0, trust_score=0.8,
            freshness_score=0.6, correlation_score=0.4,
        )
        assert weight == pytest.approx(0.7, rel=1e-3)

    def test_calculate_weight_partial(self) -> None:
        mgr = EvidenceWeightManager()
        weight = mgr.calculate_weight(quality_score=0.9, trust_score=0.5)
        # (0.9 + 0.5 + 0.5 + 0.5) / 4 = 0.6
        assert weight == pytest.approx(0.6, rel=1e-3)

    def test_normalize_weights_empty(self) -> None:
        mgr = EvidenceWeightManager()
        assert mgr.normalize_weights({}) == {}

    def test_normalize_weights_zero_total(self) -> None:
        mgr = EvidenceWeightManager()
        assert mgr.normalize_weights({"a": 0.0, "b": 0.0}) == {"a": 0.0, "b": 0.0}

    def test_normalize_weights_sums_to_one(self) -> None:
        mgr = EvidenceWeightManager()
        weights = mgr.normalize_weights({"a": 0.8, "b": 0.2})
        assert sum(weights.values()) == pytest.approx(1.0, rel=1e-3)
        assert weights["a"] > weights["b"]

    def test_normalize_weights_three_items(self) -> None:
        mgr = EvidenceWeightManager()
        weights = mgr.normalize_weights({"a": 1.0, "b": 2.0, "c": 3.0})
        assert sum(weights.values()) == pytest.approx(1.0, rel=1e-3)
        assert weights["c"] > weights["b"] > weights["a"]

    def test_aggregate_weights_empty(self) -> None:
        mgr = EvidenceWeightManager()
        assert mgr.aggregate_weights([]) == {}

    def test_aggregate_weights_single_group(self) -> None:
        mgr = EvidenceWeightManager()
        result = mgr.aggregate_weights([{"a": 0.5, "b": 0.5}])
        assert result["a"] == 0.5
        assert result["b"] == 0.5

    def test_aggregate_weights_multiple_groups(self) -> None:
        mgr = EvidenceWeightManager()
        result = mgr.aggregate_weights([
            {"a": 1.0, "b": 0.0},
            {"a": 0.0, "b": 1.0},
        ])
        assert result["a"] == pytest.approx(0.5, rel=1e-3)
        assert result["b"] == pytest.approx(0.5, rel=1e-3)

    def test_aggregate_weights_partial_keys(self) -> None:
        mgr = EvidenceWeightManager()
        result = mgr.aggregate_weights([
            {"a": 1.0},
            {"a": 0.5, "c": 1.0},
        ])
        assert result["a"] == pytest.approx(0.75, rel=1e-3)
        assert result["c"] == pytest.approx(0.5, rel=1e-3)

    def test_get_weight_explainability_all_provided(self) -> None:
        mgr = EvidenceWeightManager()
        reasons = mgr.get_weight_explainability(
            quality_score=0.9, trust_score=0.8,
            freshness_score=0.7, correlation_score=0.6,
        )
        assert len(reasons) == 4
        assert any("Quality" in r for r in reasons)

    def test_get_weight_explainability_none(self) -> None:
        mgr = EvidenceWeightManager()
        reasons = mgr.get_weight_explainability()
        assert len(reasons) == 1
        assert "Default" in reasons[0]


# ═══════════════════════════════════════════════════════════════════════
# EvidenceConsensusManager
# ═══════════════════════════════════════════════════════════════════════


class TestEvidenceConsensusManager:
    def test_calculate_agreement_score_single_evidence(self) -> None:
        mgr = EvidenceConsensusManager()
        score = mgr.calculate_agreement_score(evidence_ids=["a"])
        assert score == 1.0

    def test_calculate_agreement_score_no_correlations_no_conflicts(self) -> None:
        mgr = EvidenceConsensusManager()
        score = mgr.calculate_agreement_score(
            evidence_ids=["a", "b", "c"],
            correlation_count=0,
            conflict_count=0,
        )
        assert score == 0.0

    def test_calculate_agreement_score_full(self) -> None:
        mgr = EvidenceConsensusManager()
        score = mgr.calculate_agreement_score(
            evidence_ids=["a", "b", "c"],
            correlation_count=3,
            conflict_count=0,
            total_possible_correlations=3,
        )
        assert score == 1.0

    def test_calculate_agreement_score_with_conflicts(self) -> None:
        mgr = EvidenceConsensusManager()
        score = mgr.calculate_agreement_score(
            evidence_ids=["a", "b", "c"],
            correlation_count=3,
            conflict_count=2,
            total_possible_correlations=3,
        )
        # raw=1.0 * (1 - 2/3) = 0.3333
        assert score == pytest.approx(0.3333, rel=1e-3)

    def test_calculate_conflict_score_single_evidence(self) -> None:
        mgr = EvidenceConsensusManager()
        score = mgr.calculate_conflict_score(evidence_ids=["a"], conflict_count=5)
        assert score == 0.0

    def test_calculate_conflict_score_no_conflicts(self) -> None:
        mgr = EvidenceConsensusManager()
        score = mgr.calculate_conflict_score(
            evidence_ids=["a", "b", "c"], conflict_count=0,
        )
        assert score == 0.0

    def test_calculate_conflict_score_with_conflicts(self) -> None:
        mgr = EvidenceConsensusManager()
        score = mgr.calculate_conflict_score(
            evidence_ids=["a", "b", "c"], conflict_count=2,
        )
        assert score == pytest.approx(2 / 3, rel=1e-3)

    def test_determine_consensus_level_high(self) -> None:
        mgr = EvidenceConsensusManager()
        assert mgr.determine_consensus_level(1.0, 0.0) == ConsensusLevel.HIGH
        assert mgr.determine_consensus_level(0.8, 0.1) == ConsensusLevel.HIGH

    def test_determine_consensus_level_medium(self) -> None:
        mgr = EvidenceConsensusManager()
        assert mgr.determine_consensus_level(0.6, 0.2) == ConsensusLevel.MEDIUM
        assert mgr.determine_consensus_level(0.5, 0.1) == ConsensusLevel.MEDIUM

    def test_determine_consensus_level_low(self) -> None:
        mgr = EvidenceConsensusManager()
        assert mgr.determine_consensus_level(0.3, 0.8) == ConsensusLevel.LOW
        assert mgr.determine_consensus_level(0.0, 1.0) == ConsensusLevel.LOW

    def test_get_consensus_reasoning(self) -> None:
        mgr = EvidenceConsensusManager()
        reasons = mgr.get_consensus_reasoning(0.8, 0.1, 5)
        assert len(reasons) == 5
        assert any("Evidence count" in r for r in reasons)
        assert any("Consensus level" in r for r in reasons)


# ═══════════════════════════════════════════════════════════════════════
# EvidenceLineage
# ═══════════════════════════════════════════════════════════════════════


class TestEvidenceLineage:
    def test_default_lineage(self) -> None:
        eid = uuid.uuid4()
        lineage = EvidenceLineage(evidence_id=eid)
        assert lineage.evidence_id == eid
        assert lineage.original_source == ""
        assert lineage.fusion_history == []
        assert lineage.bundle_history == []
        assert lineage.decision_chain == []
        assert lineage.parent_evidence == []
        assert lineage.derived_evidence == []
        assert lineage.transformations == []

    def test_lineage_with_values(self) -> None:
        eid = uuid.uuid4()
        pid = uuid.uuid4()
        did = uuid.uuid4()
        lineage = EvidenceLineage(
            evidence_id=eid,
            original_source="sensor-01",
            fusion_history=["fusion_1", "fusion_2"],
            bundle_history=["bundle_1"],
            decision_chain=["decision_1"],
            parent_evidence=[pid],
            derived_evidence=[did],
            transformations=["normalized", "classified"],
            metadata={"key": "value"},
        )
        assert lineage.original_source == "sensor-01"
        assert len(lineage.fusion_history) == 2
        assert lineage.parent_evidence == [pid]
        assert lineage.metadata["key"] == "value"


# ═══════════════════════════════════════════════════════════════════════
# EvidenceSnapshot
# ═══════════════════════════════════════════════════════════════════════


class TestEvidenceSnapshot:
    def test_default_snapshot(self) -> None:
        eid = uuid.uuid4()
        snapshot = EvidenceSnapshot(evidence_id=eid)
        assert snapshot.evidence_id == eid
        assert snapshot.bundle_state == {}
        assert snapshot.graph_state == {}
        assert snapshot.timeline == []
        assert snapshot.quality_state == {}
        assert snapshot.trust_score == 0.0
        assert snapshot.weights == {}
        assert snapshot.consensus_level == ""

    def test_snapshot_with_values(self) -> None:
        eid = uuid.uuid4()
        snapshot = EvidenceSnapshot(
            evidence_id=eid,
            bundle_state={"bundle_id": "b1"},
            graph_state={"nodes": 5},
            timeline=[{"ts": "2024-01-01"}],
            quality_state={"overall": 0.85},
            trust_score=0.9,
            weights={"ev-1": 0.7},
            consensus_level="HIGH",
        )
        assert snapshot.bundle_state["bundle_id"] == "b1"
        assert snapshot.trust_score == 0.9
        assert snapshot.weights["ev-1"] == 0.7
        assert snapshot.consensus_level == "HIGH"


# ═══════════════════════════════════════════════════════════════════════
# Enhanced EvidenceDecision
# ═══════════════════════════════════════════════════════════════════════


class TestEnhancedEvidenceDecision:
    def test_default_decision_has_new_fields(self) -> None:
        d = EvidenceDecision(evidence_id=uuid.uuid4())
        assert d.evidence_weights == {}
        assert d.consensus_result == ""

    def test_decision_with_weights_and_consensus(self) -> None:
        d = EvidenceDecision(
            evidence_id=uuid.uuid4(),
            evidence_weights={"ev-1": 0.7, "ev-2": 0.3},
            consensus_result="HIGH",
        )
        assert d.evidence_weights["ev-1"] == 0.7
        assert d.consensus_result == "HIGH"

    def test_decision_backward_compatible(self) -> None:
        d = EvidenceDecision(evidence_id=uuid.uuid4(), allowed=True)
        assert d.allowed is True
        assert d.confidence == 0.0
        assert d.reasoning == []
        assert d.evidence_weights == {}
        assert d.consensus_result == ""


# ═══════════════════════════════════════════════════════════════════════
# Enhanced EvidenceConfidence
# ═══════════════════════════════════════════════════════════════════════


class TestEnhancedEvidenceConfidence:
    def test_new_dimensions_default(self) -> None:
        c = EvidenceConfidence()
        assert c.quality == 0.0
        assert c.trust == 0.0
        assert c.correlation == 0.0
        assert c.freshness == 0.0
        assert c.completeness == 0.0
        assert c.consensus == 0.0
        assert c.weight_distribution == 0.0

    def test_new_dimensions_with_values(self) -> None:
        c = EvidenceConfidence(
            quality=0.9,
            trust=0.8,
            correlation=0.7,
            freshness=0.6,
            completeness=0.5,
            consensus=0.4,
            weight_distribution=0.3,
            overall_confidence=0.6,
        )
        assert c.quality == 0.9
        assert c.weight_distribution == 0.3
        assert c.overall_confidence == 0.6

    def test_new_dimensions_bounds(self) -> None:
        with pytest.raises(ValidationError):
            EvidenceConfidence(quality=-0.1)
        with pytest.raises(ValidationError):
            EvidenceConfidence(quality=1.1)


# ═══════════════════════════════════════════════════════════════════════
# Enhanced EvidenceExplainabilityMetadata
# ═══════════════════════════════════════════════════════════════════════


class TestEnhancedEvidenceExplainability:
    def test_new_fields_default(self) -> None:
        e = EvidenceExplainabilityMetadata()
        assert e.why_weight_assigned == []
        assert e.why_consensus_reached == []

    def test_new_fields_with_values(self) -> None:
        e = EvidenceExplainabilityMetadata(
            why_weight_assigned=["Quality: 0.9", "Trust: 0.8"],
            why_consensus_reached=["Agreement: HIGH"],
        )
        assert len(e.why_weight_assigned) == 2
        assert len(e.why_consensus_reached) == 1


# ═══════════════════════════════════════════════════════════════════════
# Enhanced EvidenceTrace
# ═══════════════════════════════════════════════════════════════════════


class TestEnhancedTrace:
    def test_new_trace_stages_exist(self) -> None:
        assert hasattr(TraceStage, "WEIGHT")
        assert hasattr(TraceStage, "CONSENSUS")
        assert hasattr(TraceStage, "FUSION")
        assert hasattr(TraceStage, "PACKAGING")

    def test_new_stage_values(self) -> None:
        assert TraceStage.WEIGHT.value == "WEIGHT"
        assert TraceStage.CONSENSUS.value == "CONSENSUS"
        assert TraceStage.FUSION.value == "FUSION"
        assert TraceStage.PACKAGING.value == "PACKAGING"

    def test_trace_with_new_stages(self) -> None:
        trace = EvidenceTrace()
        r = trace.record_event(TraceStage.WEIGHT, "test", "ev-1", duration_ms=5.0)
        assert r.stage_name == "WEIGHT"
        assert r.duration_ms == 5.0

        r2 = trace.record_event(TraceStage.CONSENSUS, "test", "ev-1", duration_ms=3.0)
        assert r2.stage_name == "CONSENSUS"

        r3 = trace.record_event(TraceStage.FUSION, "test", "ev-1")
        assert r3.stage_name == "FUSION"

        r4 = trace.record_event(TraceStage.PACKAGING, "test", "ev-1")
        assert r4.stage_name == "PACKAGING"


# ═══════════════════════════════════════════════════════════════════════
# Enhanced EvidenceHealth
# ═══════════════════════════════════════════════════════════════════════


class TestEnhancedEvidenceHealth:
    def test_new_fields_default(self) -> None:
        h = EvidenceHealth()
        assert h.weight_manager_status == "UNKNOWN"
        assert h.consensus_status == "UNKNOWN"

    def test_new_fields_with_values(self) -> None:
        h = EvidenceHealth(weight_manager_status="HEALTHY", consensus_status="HEALTHY")
        assert h.weight_manager_status == "HEALTHY"
        assert h.consensus_status == "HEALTHY"


# ═══════════════════════════════════════════════════════════════════════
# Enhanced EvidenceMetrics (contract)
# ═══════════════════════════════════════════════════════════════════════


class TestEnhancedEvidenceMetrics:
    def test_new_distribution_fields_default(self) -> None:
        m = EvidenceMetrics()
        assert m.consistency_distribution == {}
        assert m.consensus_distribution == {}
        assert m.weight_distribution == {}

    def test_new_distribution_fields_with_values(self) -> None:
        m = EvidenceMetrics(
            evidence_total=10,
            consistency_distribution={"HIGH": 5, "LOW": 5},
            consensus_distribution={"HIGH": 3, "MEDIUM": 7},
            weight_distribution={"high": 8, "low": 2},
            trust_distribution={"high": 10},
            quality_distribution={"high": 9, "medium": 1},
            correlation_distribution={"high": 6, "low": 4},
        )
        assert m.consistency_distribution["HIGH"] == 5
        assert m.consensus_distribution["MEDIUM"] == 7
        assert m.weight_distribution["high"] == 8


# ═══════════════════════════════════════════════════════════════════════
# Enhanced EvidenceMetricsCollector (execution)
# ═══════════════════════════════════════════════════════════════════════


class TestEnhancedMetricsCollector:
    def test_record_consensus(self) -> None:
        c = EvidenceMetricsCollector()
        c.record_consensus("HIGH")
        c.record_consensus("MEDIUM")
        c.record_consensus("HIGH")
        snap = c.snapshot()
        assert snap.consensus_distribution == {"HIGH": 2, "MEDIUM": 1}

    def test_record_weight(self) -> None:
        c = EvidenceMetricsCollector()
        c.record_weight(0.8)
        c.record_weight(0.2)
        c.record_weight(0.5)
        snap = c.snapshot()
        assert snap.weight_distribution.get("high") == 1
        assert snap.weight_distribution.get("low") == 1
        assert snap.weight_distribution.get("medium") == 1

    def test_record_quality_distribution(self) -> None:
        c = EvidenceMetricsCollector()
        c.record_quality_distribution(0.9)
        c.record_quality_distribution(0.1)
        snap = c.snapshot()
        assert snap.quality_distribution.get("high") == 1
        assert snap.quality_distribution.get("low") == 1

    def test_record_correlation_distribution(self) -> None:
        c = EvidenceMetricsCollector()
        c.record_correlation_distribution(0.8)
        c.record_correlation_distribution(0.2)
        snap = c.snapshot()
        assert snap.correlation_distribution.get("high") == 1
        assert snap.correlation_distribution.get("low") == 1

    def test_reset_clears_distributions(self) -> None:
        c = EvidenceMetricsCollector()
        c.record_consensus("HIGH")
        c.record_weight(0.8)
        c.reset()
        snap = c.snapshot()
        assert snap.consensus_distribution == {}
        assert snap.weight_distribution == {}


# ═══════════════════════════════════════════════════════════════════════
# Coordinator - weight & consensus integration
# ═══════════════════════════════════════════════════════════════════════


class TestCoordinatorPhase35:
    def test_decision_has_evidence_weights(self) -> None:
        coord = EvidenceCoordinator()
        decision = coord.collect_and_process(
            evidence_type=EvidenceType.SENSOR,
            domain=EvidenceDomain.ENERGY,
        )
        assert decision.evidence_weights is not None
        assert len(decision.evidence_weights) > 0
        assert all(0.0 <= w <= 1.0 for w in decision.evidence_weights.values())

    def test_decision_has_consensus_result(self) -> None:
        coord = EvidenceCoordinator()
        decision = coord.collect_and_process()
        assert decision.consensus_result in ("HIGH", "MEDIUM", "LOW", "")

    def test_collect_and_process_full_weights(self) -> None:
        coord = EvidenceCoordinator()
        decision = coord.collect_and_process()
        # Weights should sum to 1.0 after normalization
        total = sum(decision.evidence_weights.values())
        assert total == pytest.approx(1.0, rel=1e-3) if decision.evidence_weights else True

    def test_process_existing_has_weights_and_consensus(self) -> None:
        coord = EvidenceCoordinator()
        evs = [_make_evidence(), _make_evidence(EvidenceDomain.ENERGY)]
        decision = coord.process_existing(evs)
        assert len(decision.evidence_weights) == 2
        assert decision.consensus_result != ""
        total = sum(decision.evidence_weights.values())
        assert total == pytest.approx(1.0, rel=1e-3) if decision.evidence_weights else True

    def test_trace_contains_weight_stage(self) -> None:
        coord = EvidenceCoordinator()
        decision = coord.collect_and_process()
        traces = coord.trace.get_by_evidence_id(str(decision.evidence_id))
        stages = [t.stage_name for t in traces]
        assert "WEIGHT" in stages

    def test_trace_contains_consensus_stage(self) -> None:
        coord = EvidenceCoordinator()
        decision = coord.collect_and_process()
        traces = coord.trace.get_by_evidence_id(str(decision.evidence_id))
        stages = [t.stage_name for t in traces]
        assert "CONSENSUS" in stages

    def test_health_has_weight_and_consensus_status(self) -> None:
        coord = EvidenceCoordinator()
        health = coord.health()
        assert hasattr(health, "weight_manager_status")
        assert hasattr(health, "consensus_status")
        assert health.weight_manager_status == "HEALTHY"
        assert health.consensus_status == "HEALTHY"

    def test_metrics_has_new_distributions(self) -> None:
        coord = EvidenceCoordinator()
        coord.collect_and_process()
        metrics = coord.metrics()
        assert hasattr(metrics, "consensus_distribution")
        assert hasattr(metrics, "weight_distribution")
        assert hasattr(metrics, "quality_distribution")
        assert hasattr(metrics, "trust_distribution")
        assert hasattr(metrics, "correlation_distribution")
        assert hasattr(metrics, "consistency_distribution")

    def test_confidence_calculator_accepts_new_params(self) -> None:
        from adip.evidence.orchestration.confidence import EvidenceConfidenceCalculator
        calc = EvidenceConfidenceCalculator()
        conf = calc.calculate(
            quality_score=0.9,
            trust_score=0.8,
            is_correlated=True,
            freshness_score=0.7,
            consensus_level="HIGH",
            weight_distribution_score=0.6,
        )
        assert conf.quality == 0.9
        assert conf.trust == 0.8
        assert conf.freshness == 0.7
        assert conf.consensus == 1.0
        assert conf.weight_distribution == 0.6

    def test_confidence_dimensions_affect_overall(self) -> None:
        from adip.evidence.orchestration.confidence import EvidenceConfidenceCalculator
        calc = EvidenceConfidenceCalculator()
        conf = calc.calculate(
            quality_score=1.0, trust_score=1.0,
            is_correlated=True, freshness_score=1.0,
            consensus_level="HIGH", weight_distribution_score=1.0,
        )
        # All dimensions at 1.0, but completeness requires evidence
        assert conf.completeness == 0.0
        assert conf.overall_confidence == pytest.approx(6 / 7, rel=1e-3)


# ═══════════════════════════════════════════════════════════════════════
# Integration with EvidenceManager
# ═══════════════════════════════════════════════════════════════════════


class TestManagerPhase35:
    def test_collect_returns_weights(self) -> None:
        mgr = EvidenceManager()
        decision = mgr.collect_evidence()
        assert decision.evidence_weights is not None
        assert decision.consensus_result != ""

    def test_health_has_new_fields(self) -> None:
        mgr = EvidenceManager()
        health = mgr.get_health()
        assert health.weight_manager_status == "HEALTHY"
        assert health.consensus_status == "HEALTHY"

    def test_metrics_has_new_distributions(self) -> None:
        mgr = EvidenceManager()
        mgr.collect_evidence()
        metrics = mgr.get_metrics()
        assert metrics.consensus_distribution is not None


# ═══════════════════════════════════════════════════════════════════════
# Integration with EvidenceService
# ═══════════════════════════════════════════════════════════════════════


class TestServicePhase35:
    def test_collect_evidence_has_weights(self) -> None:
        svc = EvidenceService()
        decision = svc.collect_evidence()
        assert decision is not None
        assert len(decision.evidence_weights) > 0
        assert decision.consensus_result != ""

    def test_process_existing_has_weights(self) -> None:
        svc = EvidenceService()
        decision = svc.process_existing([_make_evidence(), _make_evidence(EvidenceDomain.ENERGY)])
        assert decision is not None
        assert len(decision.evidence_weights) > 0

    def test_health_has_new_fields(self) -> None:
        svc = EvidenceService()
        health = svc.health()
        assert health.weight_manager_status == "HEALTHY"
        assert health.consensus_status == "HEALTHY"

    def test_metrics_has_new_distributions(self) -> None:
        svc = EvidenceService()
        svc.collect_evidence()
        metrics = svc.metrics()
        assert metrics.consensus_distribution is not None
        assert metrics.weight_distribution is not None

    def test_backward_compatible_decision(self) -> None:
        svc = EvidenceService()
        decision = svc.collect_evidence()
        assert decision.allowed is True
        assert decision.confidence > 0.0
        assert decision.quality_score > 0.0
        assert decision.trust_score > 0.0
        assert len(decision.reasoning) > 0


# ═══════════════════════════════════════════════════════════════════════
# Full Pipeline Integration
# ═══════════════════════════════════════════════════════════════════════


class TestPipelinePhase35:
    def test_full_pipeline_produces_weighted_decision(self) -> None:
        svc = EvidenceService()
        decision = svc.collect_evidence(
            evidence_type=EvidenceType.SENSOR,
            domain=EvidenceDomain.ENERGY,
            source_id="sensor-01",
            user_id="admin",
        )
        assert decision is not None
        assert "Weight assigned" in str(decision.reasoning)
        assert "Consensus" in str(decision.reasoning)
        assert sum(decision.evidence_weights.values()) > 0

    def test_multiple_collects_accumulate_weights(self) -> None:
        svc = EvidenceService()
        d1 = svc.collect_evidence(domain=EvidenceDomain.ENERGY)
        d2 = svc.collect_evidence(domain=EvidenceDomain.OPERATIONS)
        assert d1 is not None and d2 is not None
        assert len(d1.evidence_weights) > 0
        assert len(d2.evidence_weights) > 0

    def test_confidence_calculator_backward_compat(self) -> None:
        from adip.evidence.orchestration.confidence import EvidenceConfidenceCalculator
        calc = EvidenceConfidenceCalculator()
        # Call with old-style params (should still work)
        conf = calc.calculate(
            is_normalized=True,
            is_correlated=False,
            trust_score=0.5,
            quality_score=0.5,
            is_classified=True,
        )
        assert conf.overall_confidence > 0.0

    def test_duplicate_evidence_handling(self) -> None:
        svc = EvidenceService()
        ev = _make_evidence()
        d1 = svc.process_existing([ev])
        d2 = svc.process_existing([ev])
        assert d1 is not None and d2 is not None
        assert d1.evidence_weights is not None
        assert d2.evidence_weights is not None
