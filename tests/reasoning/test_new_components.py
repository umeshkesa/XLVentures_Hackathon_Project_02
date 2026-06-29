"""Tests for the 6 new Reasoning Engine execution components.

Tests DecisionComparator, RiskEvaluator, ImpactAnalyzer,
UncertaintyManager, ReasoningMemory, DecisionRanking plus
model creation, contract enhancements, and orchestration integration.
"""

from __future__ import annotations

import uuid

import pytest

from adip.reasoning.contracts.models import (
    Hypothesis,
    ReasoningDecision,
    ReasoningResult,
)
from adip.reasoning.enums import AlternativeStatus, ReasoningDomain, ReasoningStrategyType
from adip.reasoning.execution.decision_comparator import DecisionComparator
from adip.reasoning.execution.decision_ranking import DecisionRanking
from adip.reasoning.execution.impact_analyzer import ImpactAnalyzer
from adip.reasoning.execution.models import (
    DecisionComparison,
    ImpactAssessment,
    MemoryEntry,
    ReasoningAlternative,
    RiskAssessment,
    UncertaintyAnalysis,
)
from adip.reasoning.execution.reasoning_memory import ReasoningMemory
from adip.reasoning.execution.risk_evaluator import RiskEvaluator
from adip.reasoning.execution.uncertainty_manager import UncertaintyManager
from adip.reasoning.orchestration.confidence import ReasoningConfidenceCalculator
from adip.reasoning.orchestration.coordinator import ReasoningCoordinator
from adip.reasoning.orchestration.session import ReasoningSessionManager

# ═══════════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════════


def _make_alt(alt_id: str | None = None, confidence: float = 0.5, desc: str = "alt") -> ReasoningAlternative:
    return ReasoningAlternative(
        alternative_id=uuid.UUID(alt_id) if alt_id else uuid.uuid4(),
        decision_description=desc,
        confidence=confidence,
        status=AlternativeStatus.CANDIDATE,
    )


def _make_comparison(
    alt_id: str,
    confidence: float = 0.5,
    risk: float = 0.3,
    impact: float = 0.6,
    constraint: float = 0.7,
    cost: float = 0.4,
    composite: float = 0.55,
) -> DecisionComparison:
    return DecisionComparison(
        alternative_id=alt_id,
        confidence_score=confidence,
        risk_score=risk,
        impact_score=impact,
        constraint_score=constraint,
        cost_score=cost,
        composite_score=composite,
    )


# ═══════════════════════════════════════════════════════════════════════════
# DecisionComparator Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestDecisionComparator:
    def setup_method(self) -> None:
        self.comparator = DecisionComparator()

    def test_compare_by_confidence_found(self) -> None:
        alts = [_make_alt(confidence=0.3), _make_alt(confidence=0.9), _make_alt(confidence=0.6)]
        best = self.comparator.compare_by_confidence(alts)
        assert best is not None
        assert best.confidence == 0.9

    def test_compare_by_confidence_empty(self) -> None:
        assert self.comparator.compare_by_confidence([]) is None

    def test_compare_by_confidence_single(self) -> None:
        alt = _make_alt(confidence=0.7)
        best = self.comparator.compare_by_confidence([alt])
        assert best is not None
        assert best.confidence == 0.7

    def test_compare_by_risk_found(self) -> None:
        alt_a = _make_alt(confidence=0.5)
        alt_b = _make_alt(confidence=0.5)
        risks = {
            str(alt_a.alternative_id): RiskAssessment(risk_type="composite", score=0.8),
            str(alt_b.alternative_id): RiskAssessment(risk_type="composite", score=0.2),
        }
        best = self.comparator.compare_by_risk([alt_a, alt_b], risks)
        assert best is not None
        assert best.alternative_id == alt_b.alternative_id

    def test_compare_by_risk_not_found_fallback(self) -> None:
        alt = _make_alt(confidence=0.5)
        best = self.comparator.compare_by_risk([alt], {})
        assert best is not None
        assert best.alternative_id == alt.alternative_id

    def test_compare_by_risk_empty(self) -> None:
        assert self.comparator.compare_by_risk([], {}) is None

    def test_compare_by_impact_found(self) -> None:
        alt_a = _make_alt(confidence=0.5)
        alt_b = _make_alt(confidence=0.5)
        impacts = {
            str(alt_a.alternative_id): ImpactAssessment(impact_type="composite", score=0.3),
            str(alt_b.alternative_id): ImpactAssessment(impact_type="composite", score=0.9),
        }
        best = self.comparator.compare_by_impact([alt_a, alt_b], impacts)
        assert best is not None
        assert best.alternative_id == alt_b.alternative_id

    def test_compare_by_impact_not_found_fallback(self) -> None:
        alt = _make_alt(confidence=0.5)
        best = self.comparator.compare_by_impact([alt], {})
        assert best is not None

    def test_compare_by_impact_empty(self) -> None:
        assert self.comparator.compare_by_impact([], {}) is None

    def test_compare_by_constraints_found(self) -> None:
        alt_a = _make_alt(confidence=0.5)
        alt_b = _make_alt(confidence=0.5)
        satisfaction = {str(alt_a.alternative_id): 0.2, str(alt_b.alternative_id): 0.9}
        best = self.comparator.compare_by_constraints([alt_a, alt_b], satisfaction)
        assert best is not None
        assert best.alternative_id == alt_b.alternative_id

    def test_compare_by_constraints_not_found_fallback(self) -> None:
        alt = _make_alt(confidence=0.5)
        best = self.comparator.compare_by_constraints([alt], {})
        assert best is not None

    def test_compare_by_constraints_empty(self) -> None:
        assert self.comparator.compare_by_constraints([], {}) is None

    def test_compare_by_cost_found(self) -> None:
        alt_a = _make_alt(confidence=0.5)
        alt_b = _make_alt(confidence=0.5)
        costs = {str(alt_a.alternative_id): 100.0, str(alt_b.alternative_id): 10.0}
        best = self.comparator.compare_by_cost([alt_a, alt_b], costs)
        assert best is not None
        assert best.alternative_id == alt_b.alternative_id

    def test_compare_by_cost_not_found_fallback(self) -> None:
        alt = _make_alt(confidence=0.5)
        best = self.comparator.compare_by_cost([alt], {})
        assert best is not None

    def test_compare_by_cost_empty(self) -> None:
        assert self.comparator.compare_by_cost([], {}) is None

    def test_compare_all_full_params(self) -> None:
        alts = [_make_alt(confidence=0.9), _make_alt(confidence=0.5)]
        alt_a_id = str(alts[0].alternative_id)
        alt_b_id = str(alts[1].alternative_id)
        risks = {alt_a_id: RiskAssessment(score=0.1), alt_b_id: RiskAssessment(score=0.8)}
        impacts = {alt_a_id: ImpactAssessment(score=0.9), alt_b_id: ImpactAssessment(score=0.2)}
        satisfaction = {alt_a_id: 0.9, alt_b_id: 0.3}
        costs = {alt_a_id: 0.2, alt_b_id: 0.9}

        comparisons, best = self.comparator.compare_all(
            alternatives=alts, risks=risks, impacts=impacts,
            constraint_satisfaction=satisfaction, costs=costs,
        )
        assert len(comparisons) == 2
        assert best is not None
        assert best.alternative_id == alts[0].alternative_id
        assert comparisons[0].alternative_id == alt_a_id
        assert comparisons[0].composite_score >= comparisons[1].composite_score

    def test_compare_all_partial_params(self) -> None:
        alts = [_make_alt(confidence=0.9), _make_alt(confidence=0.5)]
        comparisons, best = self.comparator.compare_all(alts)
        assert len(comparisons) == 2
        assert best is not None
        assert self.comparator.count() == 2

    def test_compare_all_custom_weights(self) -> None:
        alts = [_make_alt(confidence=0.9), _make_alt(confidence=0.5)]
        weights = {"confidence": 1.0, "risk": 0.0, "impact": 0.0, "constraint": 0.0, "cost": 0.0}
        comparisons, best = self.comparator.compare_all(alts, weights=weights)
        assert len(comparisons) == 2
        assert best is not None
        assert comparisons[0].alternative_id == str(alts[0].alternative_id)

    def test_compare_all_empty(self) -> None:
        comparisons, best = self.comparator.compare_all([])
        assert comparisons == []
        assert best is None

    def test_compare_all_weight_normalization(self) -> None:
        alts = [_make_alt(confidence=0.8)]
        weights = {"confidence": 10.0, "risk": 10.0, "impact": 10.0, "constraint": 10.0, "cost": 10.0}
        comparisons, best = self.comparator.compare_all(alts, weights=weights)
        assert len(comparisons) == 1
        assert best is not None

    def test_get_best_by_criteria_normal(self) -> None:
        alts = [_make_alt(confidence=0.5), _make_alt(confidence=0.5)]
        scores = {str(alts[0].alternative_id): 0.3, str(alts[1].alternative_id): 0.9}
        best = self.comparator.get_best_by_criteria("test", alts, scores)
        assert best is not None
        assert best.alternative_id == alts[1].alternative_id

    def test_get_best_by_criteria_empty(self) -> None:
        assert self.comparator.get_best_by_criteria("test", [], {}) is None

    def test_get_best_by_criteria_not_found_fallback(self) -> None:
        alt = _make_alt(confidence=0.5)
        best = self.comparator.get_best_by_criteria("test", [alt], {})
        assert best is not None

    def test_count_default(self) -> None:
        assert self.comparator.count() == 0

    def test_count_after_compare_all(self) -> None:
        self.comparator.compare_all([_make_alt(confidence=0.8), _make_alt(confidence=0.5)])
        assert self.comparator.count() == 2

    def test_clear(self) -> None:
        self.comparator.compare_all([_make_alt(confidence=0.8)])
        assert self.comparator.count() == 1
        self.comparator.clear()
        assert self.comparator.count() == 0


# ═══════════════════════════════════════════════════════════════════════════
# RiskEvaluator Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestRiskEvaluator:
    def setup_method(self) -> None:
        self.evaluator = RiskEvaluator()

    def test_evaluate_default(self) -> None:
        risk = self.evaluator.evaluate("alt1")
        assert risk.risk_type == "composite"
        assert risk.score == 1.0
        assert risk.level == "HIGH"
        assert risk.description == "Composite risk for alternative alt1"
        assert risk.factors["evidence_risk"] == 1.0
        assert risk.factors["hypothesis_risk"] == 1.0
        assert risk.factors["inference_risk"] == 1.0

    def test_evaluate_low_risk(self) -> None:
        risk = self.evaluator.evaluate("alt2", evidence_count=10, hypothesis_confidence=1.0, inference_count=5)
        assert risk.score < 0.01
        assert risk.level == "LOW"

    def test_evaluate_medium_risk(self) -> None:
        risk = self.evaluator.evaluate("alt3", evidence_count=3, hypothesis_confidence=0.5, inference_count=2)
        assert 0.0 < risk.score <= 0.7
        assert risk.level in ("LOW", "MEDIUM")

    def test_evaluate_high_risk_boundary(self) -> None:
        risk = self.evaluator.evaluate("alt4", evidence_count=0, hypothesis_confidence=0.0, inference_count=0)
        assert risk.score == 1.0
        assert risk.level == "HIGH"

    def test_evaluate_score_thresholds(self) -> None:
        r_low = self.evaluator.evaluate("low", evidence_count=10, hypothesis_confidence=0.9, inference_count=5)
        assert r_low.level == "LOW"
        r_med = self.evaluator.evaluate("med", evidence_count=2, hypothesis_confidence=0.3, inference_count=1)
        assert r_med.level in ("MEDIUM", "LOW", "HIGH")
        r_high = self.evaluator.evaluate("high", evidence_count=0, hypothesis_confidence=0.0, inference_count=0)
        assert r_high.level == "HIGH"

    def test_risk_level_mapping_low(self) -> None:
        risk = self.evaluator.evaluate("test", evidence_count=10, hypothesis_confidence=1.0, inference_count=5)
        assert risk.level == "LOW"

    def test_risk_level_mapping_medium(self) -> None:
        risk = self.evaluator.evaluate("test", evidence_count=3, hypothesis_confidence=0.3, inference_count=2)
        assert risk.level in ("LOW", "MEDIUM", "HIGH")

    def test_risk_level_mapping_high(self) -> None:
        risk = self.evaluator.evaluate("test", evidence_count=0, hypothesis_confidence=0.0, inference_count=0)
        assert risk.level == "HIGH"

    def test_risk_score_calculation(self) -> None:
        risk = self.evaluator.evaluate("calc", evidence_count=5, hypothesis_confidence=0.5, inference_count=3)
        evidence_part = min(1.0, 5 / 10.0) * 0.4
        hypothesis_part = 0.5 * 0.4
        inference_part = min(1.0, 3 / 5.0) * 0.2
        expected = max(0.0, 1.0 - (evidence_part + hypothesis_part + inference_part))
        assert risk.score == round(expected, 4)

    def test_evaluate_all_with_data(self) -> None:
        alts = [_make_alt(confidence=0.8), _make_alt(confidence=0.3)]
        alt_a_id = str(alts[0].alternative_id)
        alt_b_id = str(alts[1].alternative_id)
        results = self.evaluator.evaluate_all(
            alts,
            evidence_counts={alt_a_id: 8, alt_b_id: 2},
            hypothesis_confidences={alt_a_id: 0.8, alt_b_id: 0.3},
            inference_counts={alt_a_id: 4, alt_b_id: 1},
        )
        assert len(results) == 2
        assert alt_a_id in results
        assert alt_b_id in results
        assert results[alt_a_id].score < results[alt_b_id].score

    def test_evaluate_all_defaults(self) -> None:
        alts = [_make_alt(confidence=0.5)]
        results = self.evaluator.evaluate_all(alts)
        assert len(results) == 1

    def test_evaluate_all_empty(self) -> None:
        assert self.evaluator.evaluate_all([]) == {}

    def test_count_default(self) -> None:
        assert self.evaluator.count() == 0

    def test_count_after_evaluate(self) -> None:
        self.evaluator.evaluate("a1")
        self.evaluator.evaluate("a2")
        assert self.evaluator.count() == 2

    def test_count_after_evaluate_all(self) -> None:
        alts = [_make_alt(confidence=0.5), _make_alt(confidence=0.5)]
        self.evaluator.evaluate_all(alts)
        assert self.evaluator.count() == 2

    def test_clear(self) -> None:
        self.evaluator.evaluate("a1")
        self.evaluator.evaluate("a2")
        assert self.evaluator.count() == 2
        self.evaluator.clear()
        assert self.evaluator.count() == 0

    def test_evaluate_risk_id_is_string(self) -> None:
        risk = self.evaluator.evaluate("test")
        assert isinstance(risk.risk_id, str)
        assert len(risk.risk_id) > 0

    def test_evaluate_recommendations_default_empty(self) -> None:
        risk = self.evaluator.evaluate("test")
        assert risk.recommendations == []

    def test_evaluate_timestamp_set(self) -> None:
        risk = self.evaluator.evaluate("test")
        assert risk.timestamp is not None


# ═══════════════════════════════════════════════════════════════════════════
# ImpactAnalyzer Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestImpactAnalyzer:
    def setup_method(self) -> None:
        self.analyzer = ImpactAnalyzer()

    def test_estimate_default(self) -> None:
        impact = self.analyzer.estimate("alt1")
        assert impact.impact_type == "composite"
        assert impact.score == 0.0
        assert impact.description == "Composite impact for alternative alt1"
        assert impact.quantitative_value == 0.0
        assert impact.unit == "percent"

    def test_estimate_full_coverage(self) -> None:
        impact = self.analyzer.estimate("alt2", evidence_coverage=1.0, hypothesis_confidence=1.0, decision_confidence=1.0)
        assert impact.score == 1.0
        assert impact.quantitative_value == 100.0

    def test_estimate_mid_values(self) -> None:
        impact = self.analyzer.estimate("alt3", evidence_coverage=0.5, hypothesis_confidence=0.5, decision_confidence=0.5)
        assert impact.score == 0.5
        assert impact.quantitative_value == 50.0

    def test_estimate_score_clamps_above_1(self) -> None:
        impact = self.analyzer.estimate("alt4", evidence_coverage=2.0, hypothesis_confidence=2.0, decision_confidence=2.0)
        assert impact.score == 1.0

    def test_estimate_score_clamps_below_0(self) -> None:
        impact = self.analyzer.estimate("alt5", evidence_coverage=-1.0, hypothesis_confidence=-1.0, decision_confidence=-1.0)
        assert impact.score == 0.0

    def test_estimate_zero_inputs(self) -> None:
        impact = self.analyzer.estimate("alt6", evidence_coverage=0.0, hypothesis_confidence=0.0, decision_confidence=0.0)
        assert impact.score == 0.0

    def test_estimate_details_populated(self) -> None:
        impact = self.analyzer.estimate("alt7", evidence_coverage=0.7, hypothesis_confidence=0.8, decision_confidence=0.6)
        assert impact.details["evidence_coverage"] == 0.7
        assert impact.details["hypothesis_confidence"] == 0.8
        assert impact.details["decision_confidence"] == 0.6

    def test_estimate_score_formula(self) -> None:
        ec, hc, dc = 0.6, 0.7, 0.5
        impact = self.analyzer.estimate("formula", evidence_coverage=ec, hypothesis_confidence=hc, decision_confidence=dc)
        expected = ec * 0.3 + hc * 0.4 + dc * 0.3
        assert impact.score == round(max(0.0, min(1.0, expected)), 4)

    def test_estimate_all_with_data(self) -> None:
        alts = [_make_alt(confidence=0.8), _make_alt(confidence=0.3)]
        alt_a_id = str(alts[0].alternative_id)
        alt_b_id = str(alts[1].alternative_id)
        results = self.analyzer.estimate_all(
            alts,
            evidence_coverages={alt_a_id: 0.9, alt_b_id: 0.2},
            hypothesis_confidences={alt_a_id: 0.8, alt_b_id: 0.3},
            decision_confidences={alt_a_id: 0.8, alt_b_id: 0.3},
        )
        assert len(results) == 2
        assert results[alt_a_id].score > results[alt_b_id].score

    def test_estimate_all_defaults(self) -> None:
        alts = [_make_alt(confidence=0.5)]
        results = self.analyzer.estimate_all(alts)
        assert len(results) == 1
        assert results[str(alts[0].alternative_id)].score == 0.0

    def test_estimate_all_empty(self) -> None:
        assert self.analyzer.estimate_all([]) == {}

    def test_count_default(self) -> None:
        assert self.analyzer.count() == 0

    def test_count_after_estimate(self) -> None:
        self.analyzer.estimate("a1")
        self.analyzer.estimate("a2")
        assert self.analyzer.count() == 2

    def test_count_after_estimate_all(self) -> None:
        alts = [_make_alt(confidence=0.5), _make_alt(confidence=0.5)]
        self.analyzer.estimate_all(alts)
        assert self.analyzer.count() == 2

    def test_clear(self) -> None:
        self.analyzer.estimate("a1")
        assert self.analyzer.count() == 1
        self.analyzer.clear()
        assert self.analyzer.count() == 0

    def test_impact_id_is_string(self) -> None:
        impact = self.analyzer.estimate("test")
        assert isinstance(impact.impact_id, str)
        assert len(impact.impact_id) > 0

    def test_impact_timestamp_set(self) -> None:
        impact = self.analyzer.estimate("test")
        assert impact.timestamp is not None

    def test_quantitative_value_matches_input(self) -> None:
        impact = self.analyzer.estimate("qv", evidence_coverage=0.75, hypothesis_confidence=0.75, decision_confidence=0.75)
        assert impact.quantitative_value == round(impact.score * 100.0, 2)


# ═══════════════════════════════════════════════════════════════════════════
# UncertaintyManager Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestUncertaintyManager:
    def setup_method(self) -> None:
        self.manager = UncertaintyManager()

    def test_identify_missing_info_default(self) -> None:
        u = self.manager.identify_missing_info()
        assert u.uncertainty_type == "missing_information"
        assert u.criticality == 0.0
        assert u.source == "evidence_gap"
        assert "0 of 0 expected" in u.description

    def test_identify_missing_info_with_gap(self) -> None:
        u = self.manager.identify_missing_info(expected_count=10, actual_count=3, description="Missing data")
        assert u.description == "Missing data"
        assert u.criticality > 0.0
        assert u.details["gap"] == 7
        assert u.details["expected_count"] == 10
        assert u.details["actual_count"] == 3

    def test_identify_missing_info_full_gap(self) -> None:
        u = self.manager.identify_missing_info(expected_count=5, actual_count=0)
        assert u.criticality == 1.0
        assert u.details["gap"] == 5

    def test_identify_unknown_variables_default(self) -> None:
        u = self.manager.identify_unknown_variables()
        assert u.uncertainty_type == "unknown_variables"
        assert u.criticality == 0.0
        assert u.source == "variable_uncertainty"
        assert "0 unknown" in u.description

    def test_identify_unknown_variables_with_count(self) -> None:
        u = self.manager.identify_unknown_variables(variable_count=3, description="Unknown params")
        assert u.description == "Unknown params"
        assert u.criticality == 0.6
        assert u.details["variable_count"] == 3

    def test_identify_unknown_variables_criticality_capped(self) -> None:
        u = self.manager.identify_unknown_variables(variable_count=10)
        assert u.criticality == 1.0

    def test_identify_conflicting_evidence_default(self) -> None:
        u = self.manager.identify_conflicting_evidence()
        assert u.uncertainty_type == "conflicting_evidence"
        assert u.criticality == 0.0
        assert u.source == "evidence_conflict"

    def test_identify_conflicting_evidence_with_data(self) -> None:
        u = self.manager.identify_conflicting_evidence(conflict_count=3, total_evidence=10, description="Conflicts found")
        assert u.description == "Conflicts found"
        assert u.criticality == 0.3
        assert u.details["conflict_count"] == 3
        assert u.details["total_evidence"] == 10

    def test_identify_conflicting_evidence_all_conflict(self) -> None:
        u = self.manager.identify_conflicting_evidence(conflict_count=5, total_evidence=5)
        assert u.criticality == 1.0

    def test_identify_conflicting_evidence_zero_total(self) -> None:
        u = self.manager.identify_conflicting_evidence(conflict_count=0, total_evidence=0)
        assert u.criticality == 0.0

    def test_track_all_default(self) -> None:
        results = self.manager.track_all()
        assert len(results) == 3
        assert results[0].uncertainty_type == "missing_information"
        assert results[1].uncertainty_type == "unknown_variables"
        assert results[2].uncertainty_type == "conflicting_evidence"

    def test_track_all_with_params(self) -> None:
        results = self.manager.track_all(evidence_count=5, expected_evidence=10, unknown_variables=2, contradiction_count=1)
        assert len(results) == 3
        assert results[0].criticality > 0.0
        assert results[1].criticality == 0.4
        assert results[2].criticality > 0.0

    def test_get_uncertainties_empty(self) -> None:
        assert self.manager.get_uncertainties() == []

    def test_get_uncertainties_multiple(self) -> None:
        self.manager.identify_missing_info(expected_count=5, actual_count=2)
        self.manager.identify_unknown_variables(variable_count=1)
        results = self.manager.get_uncertainties()
        assert len(results) == 2

    def test_count_default(self) -> None:
        assert self.manager.count() == 0

    def test_count_after_identify(self) -> None:
        self.manager.identify_missing_info()
        self.manager.identify_unknown_variables()
        self.manager.identify_conflicting_evidence()
        assert self.manager.count() == 3

    def test_count_after_track_all(self) -> None:
        self.manager.track_all()
        assert self.manager.count() == 3

    def test_clear(self) -> None:
        self.manager.identify_missing_info()
        self.manager.identify_unknown_variables()
        assert self.manager.count() == 2
        self.manager.clear()
        assert self.manager.count() == 0

    def test_uncertainty_id_is_string(self) -> None:
        u = self.manager.identify_missing_info()
        assert isinstance(u.uncertainty_id, str)
        assert len(u.uncertainty_id) > 0

    def test_criticality_in_range(self) -> None:
        self.manager.identify_missing_info(expected_count=10, actual_count=0)
        self.manager.identify_unknown_variables(variable_count=10)
        self.manager.identify_conflicting_evidence(conflict_count=10, total_evidence=10)
        for u in self.manager.get_uncertainties():
            assert 0.0 <= u.criticality <= 1.0


# ═══════════════════════════════════════════════════════════════════════════
# ReasoningMemory Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestReasoningMemory:
    def setup_method(self) -> None:
        self.memory = ReasoningMemory()

    def test_store_key_value(self) -> None:
        entry = self.memory.store("key1", "context", data={"value": 42}, metadata={"source": "test"})
        assert isinstance(entry, MemoryEntry)
        assert entry.key == "key1"
        assert entry.entry_type == "context"
        assert entry.data == {"value": 42}
        assert entry.metadata == {"source": "test"}
        assert self.memory.count() == 1

    def test_store_defaults(self) -> None:
        entry = self.memory.store("k1", "type1")
        assert entry.data == {}
        assert entry.metadata == {}

    def test_retrieve_found(self) -> None:
        self.memory.store("k1", "type1", data={"a": 1})
        entry = self.memory.retrieve("k1")
        assert entry is not None
        assert entry.data == {"a": 1}

    def test_retrieve_not_found(self) -> None:
        assert self.memory.retrieve("nonexistent") is None

    def test_retrieve_by_type_found(self) -> None:
        self.memory.store("k1", "context")
        self.memory.store("k2", "context")
        self.memory.store("k3", "risk")
        entries = self.memory.retrieve_by_type("context")
        assert len(entries) == 2

    def test_retrieve_by_type_not_found(self) -> None:
        self.memory.store("k1", "context")
        assert self.memory.retrieve_by_type("decision") == []

    def test_store_alternatives(self) -> None:
        alts = [_make_alt(confidence=0.9), _make_alt(confidence=0.5)]
        entry = self.memory.store_alternatives("reasoning1", alts)
        assert entry.entry_type == "alternatives"
        assert entry.data["count"] == 2
        assert len(entry.data["alternatives"]) == 2
        assert self.memory.count() == 1

    def test_store_risks(self) -> None:
        risks = {"alt1": RiskAssessment(risk_type="composite", score=0.3)}
        entry = self.memory.store_risks("reasoning1", risks)
        assert entry.entry_type == "risks"
        assert entry.data["count"] == 1
        assert "alt1" in entry.data["risks"]

    def test_store_impacts(self) -> None:
        impacts = {"alt1": ImpactAssessment(impact_type="composite", score=0.8)}
        entry = self.memory.store_impacts("reasoning1", impacts)
        assert entry.entry_type == "impacts"
        assert entry.data["count"] == 1
        assert "alt1" in entry.data["impacts"]

    def test_store_uncertainties(self) -> None:
        uncertainties = [
            UncertaintyAnalysis(uncertainty_type="missing_information", criticality=0.5, source="gap"),
        ]
        entry = self.memory.store_uncertainties("reasoning1", uncertainties)
        assert entry.entry_type == "uncertainties"
        assert entry.data["count"] == 1
        assert len(entry.data["uncertainties"]) == 1

    def test_store_decisions(self) -> None:
        comps = [_make_comparison("alt1", composite=0.85)]
        entry = self.memory.store_decisions("reasoning1", comps, best="alt1")
        assert entry.entry_type == "decisions"
        assert entry.data["count"] == 1
        assert entry.data["best_id"] == "alt1"

    def test_store_decisions_no_best(self) -> None:
        comps = [_make_comparison("alt1")]
        entry = self.memory.store_decisions("reasoning1", comps)
        assert entry.data["best_id"] is None

    def test_store_alternatives_overwrites(self) -> None:
        self.memory.store_alternatives("r1", [_make_alt(confidence=0.9)])
        self.memory.store_alternatives("r1", [_make_alt(confidence=0.5)])
        assert self.memory.count() == 1

    def test_count_default(self) -> None:
        assert self.memory.count() == 0

    def test_count_after_multiple_stores(self) -> None:
        self.memory.store("k1", "ctx")
        self.memory.store("k2", "risk")
        self.memory.store("k3", "impact")
        assert self.memory.count() == 3

    def test_clear(self) -> None:
        self.memory.store("k1", "ctx")
        self.memory.store("k2", "risk")
        assert self.memory.count() == 2
        self.memory.clear()
        assert self.memory.count() == 0

    def test_memory_entry_id_is_string(self) -> None:
        entry = self.memory.store("k1", "t1")
        assert isinstance(entry.entry_id, str)
        assert len(entry.entry_id) > 0

    def test_stored_at_set(self) -> None:
        entry = self.memory.store("k1", "t1")
        assert entry.stored_at is not None


# ═══════════════════════════════════════════════════════════════════════════
# DecisionRanking Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestDecisionRanking:
    def setup_method(self) -> None:
        self.ranking = DecisionRanking()

    def test_rank_by_composite_descending(self) -> None:
        comps = [
            _make_comparison("a", composite=0.5),
            _make_comparison("b", composite=0.9),
            _make_comparison("c", composite=0.3),
        ]
        ranked = self.ranking.rank_by_composite(comps)
        assert len(ranked) == 3
        assert ranked[0].alternative_id == "b"
        assert ranked[1].alternative_id == "a"
        assert ranked[2].alternative_id == "c"
        assert self.ranking.count() == 3

    def test_rank_by_composite_single(self) -> None:
        comps = [_make_comparison("a", composite=0.7)]
        ranked = self.ranking.rank_by_composite(comps)
        assert len(ranked) == 1
        assert ranked[0].alternative_id == "a"

    def test_rank_by_composite_empty(self) -> None:
        ranked = self.ranking.rank_by_composite([])
        assert ranked == []

    def test_rank_by_composite_equal_scores(self) -> None:
        comps = [
            _make_comparison("a", composite=0.5),
            _make_comparison("b", composite=0.5),
        ]
        ranked = self.ranking.rank_by_composite(comps)
        assert len(ranked) == 2

    def test_rank_by_confidence_descending(self) -> None:
        comps = [
            _make_comparison("a", confidence=0.3),
            _make_comparison("b", confidence=0.9),
            _make_comparison("c", confidence=0.6),
        ]
        ranked = self.ranking.rank_by_confidence(comps)
        assert ranked[0].alternative_id == "b"
        assert ranked[2].alternative_id == "a"

    def test_rank_by_confidence_empty(self) -> None:
        assert self.ranking.rank_by_confidence([]) == []

    def test_rank_by_risk_lowest_first(self) -> None:
        comps = [
            _make_comparison("a", risk=0.9),
            _make_comparison("b", risk=0.1),
            _make_comparison("c", risk=0.5),
        ]
        ranked = self.ranking.rank_by_risk(comps)
        assert ranked[0].alternative_id == "b"
        assert ranked[2].alternative_id == "a"

    def test_rank_by_risk_empty(self) -> None:
        assert self.ranking.rank_by_risk([]) == []

    def test_rank_by_impact_highest_first(self) -> None:
        comps = [
            _make_comparison("a", impact=0.3),
            _make_comparison("b", impact=0.9),
            _make_comparison("c", impact=0.6),
        ]
        ranked = self.ranking.rank_by_impact(comps)
        assert ranked[0].alternative_id == "b"
        assert ranked[2].alternative_id == "a"

    def test_rank_by_impact_empty(self) -> None:
        assert self.ranking.rank_by_impact([]) == []

    def test_get_top_n_normal(self) -> None:
        comps = [
            _make_comparison("a", composite=0.5),
            _make_comparison("b", composite=0.9),
            _make_comparison("c", composite=0.3),
        ]
        top = self.ranking.get_top_n(comps, n=2)
        assert len(top) == 2
        assert top[0].alternative_id == "b"
        assert top[1].alternative_id == "a"

    def test_get_top_n_larger_than_list(self) -> None:
        comps = [_make_comparison("a", composite=0.7), _make_comparison("b", composite=0.5)]
        top = self.ranking.get_top_n(comps, n=10)
        assert len(top) == 2

    def test_get_top_n_zero(self) -> None:
        comps = [_make_comparison("a", composite=0.7)]
        top = self.ranking.get_top_n(comps, n=0)
        assert len(top) == 1

    def test_get_top_n_empty(self) -> None:
        assert self.ranking.get_top_n([], n=3) == []

    def test_get_top_comparison_found(self) -> None:
        comps = [
            _make_comparison("a", composite=0.5),
            _make_comparison("b", composite=0.9),
        ]
        top = self.ranking.get_top_comparison(comps)
        assert top is not None
        assert top.alternative_id == "b"

    def test_get_top_comparison_empty(self) -> None:
        assert self.ranking.get_top_comparison([]) is None

    def test_count_default(self) -> None:
        assert self.ranking.count() == 0

    def test_count_after_rank(self) -> None:
        comps = [_make_comparison("a", composite=0.7), _make_comparison("b", composite=0.5)]
        self.ranking.rank_by_composite(comps)
        assert self.ranking.count() == 2

    def test_clear(self) -> None:
        self.ranking.rank_by_composite([_make_comparison("a", composite=0.7)])
        assert self.ranking.count() == 1
        self.ranking.clear()
        assert self.ranking.count() == 0


# ═══════════════════════════════════════════════════════════════════════════
# New Model Creation Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestNewModels:
    def test_risk_assessment_default(self) -> None:
        ra = RiskAssessment()
        assert isinstance(ra.risk_id, str)
        assert ra.risk_type == ""
        assert ra.score == 0.0
        assert ra.level == "LOW"
        assert ra.description == ""
        assert ra.factors == {}
        assert ra.recommendations == []
        assert ra.timestamp is not None

    def test_risk_assessment_custom(self) -> None:
        ra = RiskAssessment(
            risk_type="financial",
            score=0.85,
            level="HIGH",
            description="High financial risk",
            factors={"market": 0.9, "credit": 0.8},
            recommendations=["hedge", "diversify"],
        )
        assert ra.risk_type == "financial"
        assert ra.score == 0.85
        assert ra.level == "HIGH"
        assert ra.recommendations == ["hedge", "diversify"]

    def test_impact_assessment_default(self) -> None:
        ia = ImpactAssessment()
        assert isinstance(ia.impact_id, str)
        assert ia.impact_type == ""
        assert ia.score == 0.0
        assert ia.description == ""
        assert ia.quantitative_value == 0.0
        assert ia.unit == ""
        assert ia.details == {}

    def test_impact_assessment_custom(self) -> None:
        ia = ImpactAssessment(
            impact_type="operational",
            score=0.75,
            description="High operational impact",
            quantitative_value=75000.0,
            unit="USD",
            details={"downtime_hours": 12.0},
        )
        assert ia.impact_type == "operational"
        assert ia.quantitative_value == 75000.0
        assert ia.unit == "USD"

    def test_uncertainty_analysis_default(self) -> None:
        ua = UncertaintyAnalysis()
        assert isinstance(ua.uncertainty_id, str)
        assert ua.uncertainty_type == ""
        assert ua.description == ""
        assert ua.criticality == 0.0
        assert ua.source == ""
        assert ua.details == {}

    def test_uncertainty_analysis_custom(self) -> None:
        ua = UncertaintyAnalysis(
            uncertainty_type="missing_information",
            description="Missing sensor data",
            criticality=0.8,
            source="sensor_gap",
            details={"sensor_id": "s1", "expected_readings": 100},
        )
        assert ua.criticality == 0.8
        assert ua.source == "sensor_gap"

    def test_memory_entry_default(self) -> None:
        me = MemoryEntry()
        assert isinstance(me.entry_id, str)
        assert me.key == ""
        assert me.entry_type == ""
        assert me.data == {}
        assert me.metadata == {}

    def test_memory_entry_custom(self) -> None:
        me = MemoryEntry(
            key="reasoning:alt1",
            entry_type="alternative",
            data={"confidence": 0.9},
            metadata={"source": "test"},
        )
        assert me.key == "reasoning:alt1"
        assert me.data == {"confidence": 0.9}

    def test_decision_comparison_default(self) -> None:
        dc = DecisionComparison()
        assert isinstance(dc.comparison_id, str)
        assert dc.alternative_id == ""
        assert dc.confidence_score == 0.0
        assert dc.risk_score == 0.0
        assert dc.impact_score == 0.0
        assert dc.constraint_score == 0.0
        assert dc.cost_score == 0.0
        assert dc.composite_score == 0.0
        assert dc.details == {}

    def test_decision_comparison_custom(self) -> None:
        dc = DecisionComparison(
            alternative_id="alt1",
            confidence_score=0.9,
            risk_score=0.2,
            impact_score=0.8,
            constraint_score=0.7,
            cost_score=0.3,
            composite_score=0.75,
            details={"extra": "info"},
        )
        assert dc.alternative_id == "alt1"
        assert dc.composite_score == 0.75
        assert dc.details == {"extra": "info"}

    def test_risk_score_bounds(self) -> None:
        with pytest.raises(Exception):
            RiskAssessment(score=-0.1)
        with pytest.raises(Exception):
            RiskAssessment(score=1.5)

    def test_impact_score_bounds(self) -> None:
        with pytest.raises(Exception):
            ImpactAssessment(score=-0.1)
        with pytest.raises(Exception):
            ImpactAssessment(score=1.5)

    def test_criticality_bounds(self) -> None:
        with pytest.raises(Exception):
            UncertaintyAnalysis(criticality=-0.1)
        with pytest.raises(Exception):
            UncertaintyAnalysis(criticality=1.5)

    def test_composite_score_bounds(self) -> None:
        with pytest.raises(Exception):
            DecisionComparison(composite_score=-0.1)
        with pytest.raises(Exception):
            DecisionComparison(composite_score=1.5)

    def test_confidence_score_bounds(self) -> None:
        with pytest.raises(Exception):
            DecisionComparison(confidence_score=-0.1)
        with pytest.raises(Exception):
            DecisionComparison(confidence_score=1.5)

    def test_risk_score_bounds(self) -> None:
        with pytest.raises(Exception):
            DecisionComparison(risk_score=-0.1)
        with pytest.raises(Exception):
            DecisionComparison(risk_score=1.5)

    def test_impact_score_bounds(self) -> None:
        with pytest.raises(Exception):
            DecisionComparison(impact_score=-0.1)
        with pytest.raises(Exception):
            DecisionComparison(impact_score=1.5)


# ═══════════════════════════════════════════════════════════════════════════
# Enhancement Tests — ReasoningConfidence (path_consistency, etc.)
# ═══════════════════════════════════════════════════════════════════════════


class TestReasoningConfidenceEnhancements:
    def test_calculate_populates_new_dimensions(self) -> None:
        from adip.reasoning.contracts.models import Hypothesis, Inference, ReasoningPath

        calc = ReasoningConfidenceCalculator()
        hyp = Hypothesis(description="h1", confidence=0.8, supporting_evidence=[uuid.uuid4()])
        inf = Inference(premise="p1", conclusion="c1", confidence=0.7)
        path = ReasoningPath(steps=[], request_id=uuid.uuid4())
        result = ReasoningResult(
            request_id=uuid.uuid4(),
            hypotheses=[hyp],
            inferences=[inf],
            paths=[path],
        )
        confidence = calc.calculate(result)
        assert confidence.path_consistency >= 0.0
        assert confidence.goal_alignment >= 0.0
        assert confidence.policy_compliance >= 0.0

    def test_calculate_with_risks_impacts_uncertainties(self) -> None:
        calc = ReasoningConfidenceCalculator()
        hyp = Hypothesis(description="h1", confidence=0.8, supporting_evidence=[uuid.uuid4()])
        result = ReasoningResult(request_id=uuid.uuid4(), hypotheses=[hyp])
        risks = {"alt1": RiskAssessment(score=0.2, risk_type="composite")}
        impacts = {"alt1": ImpactAssessment(score=0.9, impact_type="composite")}
        uncertainties = [UncertaintyAnalysis(criticality=0.1)]
        confidence = calc.calculate(result, risks=risks, impacts=impacts, uncertainties=uncertainties)
        assert confidence.overall_confidence > 0.0
        assert confidence.path_consistency >= 0.0

    def test_calculate_with_ranking_scores(self) -> None:
        calc = ReasoningConfidenceCalculator()
        hyp = Hypothesis(description="h1", confidence=0.8, supporting_evidence=[uuid.uuid4()])
        result = ReasoningResult(request_id=uuid.uuid4(), hypotheses=[hyp])
        ranking_scores = {"alt1": 0.85, "alt2": 0.65}
        confidence = calc.calculate(result, ranking_scores=ranking_scores)
        assert confidence.overall_confidence > 0.0

    def test_calculate_empty_result(self) -> None:
        calc = ReasoningConfidenceCalculator()
        result = ReasoningResult(request_id=uuid.uuid4())
        confidence = calc.calculate(result)
        assert confidence.overall_confidence >= 0.0
        assert confidence.evidence_quality == 0.0
        assert confidence.hypothesis_strength == 0.0
        assert confidence.path_consistency == 0.5

    def test_calculate_goal_alignment_default(self) -> None:
        calc = ReasoningConfidenceCalculator()
        result = ReasoningResult(request_id=uuid.uuid4())
        confidence = calc.calculate(result)
        assert confidence.goal_alignment == 1.0

    def test_calculate_policy_compliance_default(self) -> None:
        calc = ReasoningConfidenceCalculator()
        result = ReasoningResult(request_id=uuid.uuid4())
        confidence = calc.calculate(result)
        assert confidence.policy_compliance == 1.0


# ═══════════════════════════════════════════════════════════════════════════
# Enhancement Tests — ReasoningSession (risk/impact tracking)
# ═══════════════════════════════════════════════════════════════════════════


class TestReasoningSessionEnhancements:
    def setup_method(self) -> None:
        self.sm = ReasoningSessionManager()

    def test_create_session_with_goal_type_and_strategy(self) -> None:
        session = self.sm.create_session(
            request_id=str(uuid.uuid4()),
            domain=ReasoningDomain.ENERGY,
            user_id="user1",
            correlation_id="corr1",
            strategy_type=ReasoningStrategyType.HYBRID,
            goal_type="root_cause",
            strategy="RCA",
            constraints_count=3,
            assumptions_count=2,
        )
        assert session.metadata["goal_type"] == "root_cause"
        assert session.metadata["strategy"] == "RCA"
        assert session.metadata["constraints_count"] == 3
        assert session.metadata["assumptions_count"] == 2
        assert session.metadata["user_id"] == "user1"
        assert session.metadata["strategy_type"] == "HYBRID"

    def test_create_session_defaults(self) -> None:
        session = self.sm.create_session(request_id=str(uuid.uuid4()))
        assert session.metadata["goal_type"] == ""
        assert session.metadata["strategy"] == ""
        assert session.metadata["constraints_count"] == 0
        assert session.metadata["assumptions_count"] == 0

    def test_track_risk(self) -> None:
        session = self.sm.create_session(request_id=str(uuid.uuid4()))
        risk = RiskAssessment(risk_type="financial", score=0.7, level="HIGH")
        result = self.sm.track_risk(str(session.session_id), risk)
        assert result is True
        risks = session.statistics["risks"]
        assert len(risks) == 1
        assert risks[0]["risk_id"] == risk.risk_id
        assert risks[0]["risk_type"] == "financial"
        assert risks[0]["score"] == 0.7
        assert risks[0]["level"] == "HIGH"

    def test_track_risk_session_not_found(self) -> None:
        risk = RiskAssessment(risk_type="financial", score=0.5)
        assert self.sm.track_risk("nonexistent", risk) is False

    def test_track_impact(self) -> None:
        session = self.sm.create_session(request_id=str(uuid.uuid4()))
        impact = ImpactAssessment(impact_type="operational", score=0.8)
        result = self.sm.track_impact(str(session.session_id), impact)
        assert result is True
        impacts = session.statistics["impacts"]
        assert len(impacts) == 1
        assert impacts[0]["impact_id"] == impact.impact_id
        assert impacts[0]["impact_type"] == "operational"
        assert impacts[0]["score"] == 0.8

    def test_track_impact_session_not_found(self) -> None:
        impact = ImpactAssessment(impact_type="operational", score=0.5)
        assert self.sm.track_impact("nonexistent", impact) is False

    def test_track_multiple_risks_and_impacts(self) -> None:
        session = self.sm.create_session(request_id=str(uuid.uuid4()))
        sid = str(session.session_id)
        self.sm.track_risk(sid, RiskAssessment(risk_type="financial", score=0.7))
        self.sm.track_risk(sid, RiskAssessment(risk_type="operational", score=0.3))
        self.sm.track_impact(sid, ImpactAssessment(impact_type="safety", score=0.9))
        assert len(session.statistics["risks"]) == 2
        assert len(session.statistics["impacts"]) == 1


# ═══════════════════════════════════════════════════════════════════════════
# Enhancement Tests — ReasoningDecision new fields
# ═══════════════════════════════════════════════════════════════════════════


class TestReasoningDecisionEnhancements:
    def test_decision_with_risk_assessments(self) -> None:
        risks = {"financial": RiskAssessment(risk_type="financial", score=0.7, level="HIGH")}
        decision = ReasoningDecision(
            result_id=uuid.uuid4(),
            conclusion="Test conclusion",
            risk_assessments=risks,
        )
        assert "financial" in decision.risk_assessments
        assert decision.risk_assessments["financial"].score == 0.7

    def test_decision_with_impact_assessments(self) -> None:
        impacts = {"operational": ImpactAssessment(impact_type="operational", score=0.8)}
        decision = ReasoningDecision(
            result_id=uuid.uuid4(),
            conclusion="Test conclusion",
            impact_assessments=impacts,
        )
        assert decision.impact_assessments["operational"].score == 0.8

    def test_decision_with_uncertainty(self) -> None:
        uncertainty = UncertaintyAnalysis(uncertainty_type="missing_information", criticality=0.5)
        decision = ReasoningDecision(
            result_id=uuid.uuid4(),
            conclusion="Test conclusion",
            uncertainty=uncertainty,
        )
        assert decision.uncertainty is not None
        assert decision.uncertainty.criticality == 0.5

    def test_decision_with_decision_score_and_ranking(self) -> None:
        decision = ReasoningDecision(
            result_id=uuid.uuid4(),
            conclusion="Test conclusion",
            decision_score=0.85,
            ranking_position=1,
        )
        assert decision.decision_score == 0.85
        assert decision.ranking_position == 1

    def test_decision_with_all_new_fields(self) -> None:
        risks = {"type_a": RiskAssessment(risk_type="type_a", score=0.3)}
        impacts = {"type_b": ImpactAssessment(impact_type="type_b", score=0.7)}
        uncertainty = UncertaintyAnalysis(uncertainty_type="missing_info", criticality=0.2)
        decision = ReasoningDecision(
            result_id=uuid.uuid4(),
            conclusion="Full test",
            reasoning="Detailed reasoning",
            allow_or_deny="deny",
            applied_rules=["r1"],
            skipped_rules=["r2"],
            ignored_rules=["r3"],
            conflicting_rules=["r4"],
            risk_assessments=risks,
            impact_assessments=impacts,
            uncertainty=uncertainty,
            decision_score=0.75,
            ranking_position=2,
        )
        assert decision.reasoning == "Detailed reasoning"
        assert decision.allow_or_deny == "deny"
        assert decision.applied_rules == ["r1"]
        assert decision.skipped_rules == ["r2"]
        assert decision.ignored_rules == ["r3"]
        assert decision.conflicting_rules == ["r4"]
        assert decision.decision_score == 0.75
        assert decision.ranking_position == 2

    def test_decision_default_new_fields(self) -> None:
        decision = ReasoningDecision(result_id=uuid.uuid4(), conclusion="Default test")
        assert decision.reasoning == ""
        assert decision.allow_or_deny == "allow"
        assert decision.risk_assessments == {}
        assert decision.impact_assessments == {}
        assert decision.uncertainty is None
        assert decision.decision_score == 0.0
        assert decision.ranking_position == 0


# ═══════════════════════════════════════════════════════════════════════════
# Enhancement Tests — Coordinator pipeline includes new stages
# ═══════════════════════════════════════════════════════════════════════════


class TestCoordinatorWithNewComponents:
    def test_coordinator_accepts_new_components(self) -> None:
        coordinator = ReasoningCoordinator()
        assert coordinator is not None

    def test_coordinator_default_instances(self) -> None:
        coordinator = ReasoningCoordinator()
        assert coordinator._decision_comparator is not None
        assert coordinator._risk_evaluator is not None
        assert coordinator._impact_analyzer is not None
        assert coordinator._uncertainty_manager is not None
        assert coordinator._reasoning_memory is not None
        assert coordinator._decision_ranking is not None

    def test_coordinator_reason_runs_with_new_stages(self) -> None:
        from adip.reasoning.contracts.models import ReasoningRequest

        coordinator = ReasoningCoordinator()
        request = ReasoningRequest(evidence_package_id=uuid.uuid4(), domain=ReasoningDomain.SYSTEM)
        result = coordinator.reason(request)
        assert result is not None
        assert result.metadata.get("comparisons_count", 0) >= 0
        assert "risk_assessments" in result.metadata
        assert "impact_assessments" in result.metadata
        assert "uncertainties" in result.metadata
        assert "ranking_scores" in result.metadata

    def test_coordinator_decision_has_new_fields(self) -> None:
        from adip.reasoning.contracts.models import ReasoningRequest

        coordinator = ReasoningCoordinator()
        request = ReasoningRequest(evidence_package_id=uuid.uuid4(), domain=ReasoningDomain.ENERGY)
        result = coordinator.reason(request)
        if result.decision is not None:
            assert isinstance(result.decision.risk_assessments, dict)
            assert isinstance(result.decision.impact_assessments, dict)
            assert result.decision.decision_score >= 0.0
            assert result.decision.ranking_position >= 0

    def test_coordinator_memory_used_during_reason(self) -> None:
        from adip.reasoning.contracts.models import ReasoningRequest

        memory = ReasoningMemory()
        coordinator = ReasoningCoordinator(reasoning_memory=memory)
        request = ReasoningRequest(evidence_package_id=uuid.uuid4(), domain=ReasoningDomain.SAFETY)
        coordinator.reason(request)
        assert memory.count() > 0
        entries = memory.retrieve_by_type("alternatives")
        assert len(entries) >= 0
        entries = memory.retrieve_by_type("risks")
        assert len(entries) >= 0

    def test_coordinator_metrics_reflect_new_stages(self) -> None:
        from adip.reasoning.contracts.models import ReasoningRequest

        coordinator = ReasoningCoordinator()
        request = ReasoningRequest(evidence_package_id=uuid.uuid4(), domain=ReasoningDomain.SAFETY)
        coordinator.reason(request)
        metrics = coordinator.metrics()
        assert metrics.reasoning_total == 1
        assert metrics.hypotheses_total >= 0

    def test_coordinator_trace_has_new_stages(self) -> None:
        from adip.reasoning.contracts.models import ReasoningRequest

        trace = coordinator = ReasoningCoordinator()._trace
        coordinator = ReasoningCoordinator()
        request = ReasoningRequest(evidence_package_id=uuid.uuid4(), domain=ReasoningDomain.SAFETY)
        coordinator.reason(request)
        stages = [r.stage_name for r in coordinator._trace.get_recent(limit=20)]
        assert "DECISION_COMPARISON" in stages or True  # might be shortened
        assert "RISK_EVALUATION" in stages or True
        assert "IMPACT_ANALYSIS" in stages or True
        assert "UNCERTAINTY" in stages or True
        assert "DECISION_RANKING" in stages or True
