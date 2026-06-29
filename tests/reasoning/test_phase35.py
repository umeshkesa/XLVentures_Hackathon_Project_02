"""Phase 3.5 tests — Reasoning Engine Enterprise Refinement & Interface Freeze.

Tests for:
- DecisionQualityManager
- ReasoningReview
- DecisionJustification
- ReasoningLineage
- ReasoningSnapshot
- StrategyPerformance
- DecisionReadiness
- Enhanced coordinator stages
- New trace stages (REVIEW, RANKING, READINESS)
- New metrics counters (reviews, readiness, quality)
- Enhanced models (DecisionReadinessStatus, TraceStage values)
- Enhanced ReasoningConfidence consensus field
- Enhanced ReasoningDecision quality_score and readiness_status
- Enhanced ReasoningExplainabilityMetadata why-fields
"""

from __future__ import annotations

import uuid
from datetime import UTC

import pytest
from pydantic import ValidationError

from adip.reasoning.contracts.models import (
    Contradiction,
    ReasoningConfidence,
    ReasoningDecision,
    ReasoningExplainabilityMetadata,
)
from adip.reasoning.enums import (
    AlternativeStatus,
    AssumptionStatus,
    ConstraintType,
    ContradictionResolutionStatus,
    ContradictionSeverity,
    DecisionReadinessStatus,
    ReasoningGoalType,
    ReasoningStrategyType,
    TraceStage,
)
from adip.reasoning.execution.decision_justification import DecisionJustification
from adip.reasoning.execution.decision_quality import DecisionQualityManager
from adip.reasoning.execution.decision_readiness import DecisionReadiness
from adip.reasoning.execution.metrics import ReasoningMetricsCollector
from adip.reasoning.execution.models import (
    Assumption,
    Constraint,
    DecisionQuality,
    ReasoningAlternative,
    ReasoningGoal,
    RiskAssessment,
    StrategyPerformanceRecord,
)
from adip.reasoning.execution.reasoning_lineage import ReasoningLineage
from adip.reasoning.execution.reasoning_review import ReasoningReview
from adip.reasoning.execution.reasoning_snapshot import ReasoningSnapshot
from adip.reasoning.execution.strategy_performance import StrategyPerformance
from adip.reasoning.execution.trace import ReasoningTrace

UTC = UTC


# ── DecisionQualityManager Tests ────────────────────────────────────────

class TestDecisionQualityManager:
    """Tests for DecisionQualityManager — calculates decision quality metrics."""

    def test_default_values(self) -> None:
        mgr = DecisionQualityManager()
        assert mgr.count() == 0

    def test_calculate_evidence_coverage_full(self) -> None:
        mgr = DecisionQualityManager()
        score = mgr.calculate_evidence_coverage(10, 10)
        assert score == 1.0

    def test_calculate_evidence_coverage_partial(self) -> None:
        mgr = DecisionQualityManager()
        score = mgr.calculate_evidence_coverage(5, 10)
        assert score == 0.5

    def test_calculate_evidence_coverage_zero_total(self) -> None:
        mgr = DecisionQualityManager()
        score = mgr.calculate_evidence_coverage(0, 0)
        assert score == 0.0

    def test_calculate_rule_coverage(self) -> None:
        mgr = DecisionQualityManager()
        score = mgr.calculate_rule_coverage(3, 5)
        assert score == 0.6

    def test_calculate_rule_coverage_none(self) -> None:
        mgr = DecisionQualityManager()
        score = mgr.calculate_rule_coverage(0, 0)
        assert score == 0.0

    def test_calculate_goal_satisfaction(self) -> None:
        mgr = DecisionQualityManager()
        score = mgr.calculate_goal_satisfaction(2, 3)
        assert pytest.approx(score, 0.01) == 0.6667

    def test_calculate_goal_satisfaction_none(self) -> None:
        mgr = DecisionQualityManager()
        score = mgr.calculate_goal_satisfaction(0, 0)
        assert score == 0.0

    def test_calculate_constraint_satisfaction(self) -> None:
        mgr = DecisionQualityManager()
        score = mgr.calculate_constraint_satisfaction(4, 5)
        assert score == 0.8

    def test_calculate_constraint_satisfaction_none(self) -> None:
        mgr = DecisionQualityManager()
        score = mgr.calculate_constraint_satisfaction(0, 0)
        assert score == 0.0

    def test_calculate_assumption_completeness(self) -> None:
        mgr = DecisionQualityManager()
        score = mgr.calculate_assumption_completeness(7, 10)
        assert score == 0.7

    def test_calculate_assumption_completeness_none(self) -> None:
        mgr = DecisionQualityManager()
        score = mgr.calculate_assumption_completeness(0, 0)
        assert score == 0.0

    def test_calculate_overall_quality(self) -> None:
        mgr = DecisionQualityManager()
        dq = mgr.calculate_overall_quality(
            evidence_coverage=1.0,
            rule_coverage=0.8,
            goal_satisfaction=1.0,
            constraint_satisfaction=0.9,
            assumption_completeness=0.7,
        )
        assert isinstance(dq, DecisionQuality)
        # Simple average of all 5 dimensions
        expected = (1.0 + 0.8 + 1.0 + 0.9 + 0.7) / 5.0
        assert pytest.approx(dq.overall, 0.01) == expected

    def test_calculate_overall_quality_defaults(self) -> None:
        mgr = DecisionQualityManager()
        dq = mgr.calculate_overall_quality()
        assert dq.overall == 0.0
        assert dq.evidence_coverage == 0.0
        assert dq.rule_coverage == 0.0

    def test_calculate_overall_quality_rejects_out_of_range(self) -> None:
        mgr = DecisionQualityManager()
        with pytest.raises(ValidationError):
            mgr.calculate_overall_quality(evidence_coverage=2.0)

    def test_clear(self) -> None:
        mgr = DecisionQualityManager()
        mgr.calculate_overall_quality(evidence_coverage=0.5, rule_coverage=0.5)
        mgr.clear()
        assert mgr.count() == 0

    def test_count(self) -> None:
        mgr = DecisionQualityManager()
        mgr.calculate_overall_quality(evidence_coverage=0.5, rule_coverage=0.5)
        mgr.calculate_overall_quality(evidence_coverage=0.8, rule_coverage=0.9)
        assert mgr.count() == 2


# ── ReasoningReview Tests ──────────────────────────────────────────────

class TestReasoningReview:
    """Tests for ReasoningReview — reviews reasoning across multiple dimensions."""

    def test_review_goals_valid(self) -> None:
        review = ReasoningReview()
        goals = [
            ReasoningGoal(description="Primary goal", goal_type=ReasoningGoalType.ROOT_CAUSE_ANALYSIS, priority=1, is_primary=True),
            ReasoningGoal(description="Secondary goal", goal_type=ReasoningGoalType.ROOT_CAUSE_ANALYSIS, priority=2, is_primary=False),
        ]
        result = review.review_goals(goals)
        assert result["passed"] is True
        assert result["score"] == 1.0
        assert len(result["warnings"]) == 0

    def test_review_goals_empty(self) -> None:
        review = ReasoningReview()
        result = review.review_goals([])
        assert result["passed"] is False
        assert any("No goals defined" in e for e in result["errors"])

    def test_review_goals_no_primary(self) -> None:
        goals = [
            ReasoningGoal(description="Goal", goal_type=ReasoningGoalType.ROOT_CAUSE_ANALYSIS, priority=2, is_primary=False),
        ]
        review = ReasoningReview()
        result = review.review_goals(goals)
        assert result["passed"] is True
        assert any("No primary goal defined" in w for w in result["warnings"])

    def test_review_constraints_valid(self) -> None:
        review = ReasoningReview()
        constraints = [
            Constraint(description="Hard constraint", constraint_type=ConstraintType.SAFETY, is_hard=True),
            Constraint(description="Soft constraint", constraint_type=ConstraintType.TIME, is_hard=False),
        ]
        result = review.review_constraints(constraints)
        assert result["passed"] is True

    def test_review_constraints_empty(self) -> None:
        review = ReasoningReview()
        result = review.review_constraints([])
        assert result["passed"] is True
        assert any("No constraints defined" in w for w in result["warnings"])

    def test_review_assumptions_valid(self) -> None:
        review = ReasoningReview()
        assumptions = [
            Assumption(description="Validated", status=AssumptionStatus.VALIDATED),
            Assumption(description="Active", status=AssumptionStatus.ACTIVE),
        ]
        result = review.review_assumptions(assumptions)
        assert result["passed"] is True

    def test_review_assumptions_with_invalidated(self) -> None:
        review = ReasoningReview()
        assumptions = [
            Assumption(description="Valid", status=AssumptionStatus.VALIDATED),
            Assumption(description="Invalid", status=AssumptionStatus.INVALIDATED),
        ]
        result = review.review_assumptions(assumptions)
        assert any("invalidated" in w.lower() for w in result["warnings"])

    def test_review_contradictions_all_resolved(self) -> None:
        review = ReasoningReview()
        contradictions = [
            Contradiction(
                request_id=uuid.uuid4(),
                description="Test 1",
                severity=ContradictionSeverity.LOW,
                resolution_status=ContradictionResolutionStatus.RESOLVED,
            ),
            Contradiction(
                request_id=uuid.uuid4(),
                description="Test 2",
                severity=ContradictionSeverity.MEDIUM,
                resolution_status=ContradictionResolutionStatus.RESOLVED,
            ),
        ]
        result = review.review_contradictions(contradictions)
        assert result["passed"] is True
        assert result["score"] == 1.0

    def test_review_contradictions_unresolved(self) -> None:
        review = ReasoningReview()
        contradictions = [
            Contradiction(
                request_id=uuid.uuid4(),
                description="Unresolved",
                severity=ContradictionSeverity.HIGH,
                resolution_status=ContradictionResolutionStatus.UNRESOLVED,
            ),
        ]
        result = review.review_contradictions(contradictions)
        assert result["passed"] is True
        assert any("unresolved" in w.lower() for w in result["warnings"])

    def test_review_risks_no_high(self) -> None:
        review = ReasoningReview()
        risks = {
            "op": RiskAssessment(
                risk_type="operational",
                score=0.3,
                level="LOW",
                description="Operational risk",
            ),
        }
        result = review.review_risks(risks)
        assert result["passed"] is True

    def test_review_risks_with_high(self) -> None:
        review = ReasoningReview()
        risks = {
            "critical": RiskAssessment(
                risk_type="critical",
                score=0.85,
                level="HIGH",
                description="Critical risk",
            ),
        }
        result = review.review_risks(risks)
        assert result["passed"] is True
        assert any("HIGH" in w or "CRITICAL" in w for w in result["warnings"])

    def test_review_alternatives_valid(self) -> None:
        review = ReasoningReview()
        alternatives = [
            ReasoningAlternative(
                decision_description="Primary",
                reasoning=["Good"],
                confidence=0.9,
                evidence_ids=[],
                status=AlternativeStatus.EVALUATED,
            ),
            ReasoningAlternative(
                decision_description="Secondary",
                reasoning=["OK"],
                confidence=0.5,
                evidence_ids=[],
                status=AlternativeStatus.EVALUATED,
            ),
        ]
        result = review.review_alternatives(alternatives)
        assert result["passed"] is True

    def test_review_alternatives_empty(self) -> None:
        review = ReasoningReview()
        result = review.review_alternatives([])
        assert result["passed"] is False
        assert any("No alternatives" in e for e in result["errors"])

    def test_review_confidence_high(self) -> None:
        review = ReasoningReview()
        confidence = ReasoningConfidence(overall_confidence=0.85)
        result = review.review_confidence(confidence)
        assert result["passed"] is True

    def test_review_confidence_low(self) -> None:
        review = ReasoningReview()
        confidence = ReasoningConfidence(overall_confidence=0.2)
        result = review.review_confidence(confidence)
        assert result["passed"] is True
        assert any("confidence" in w.lower() for w in result["warnings"])

    def test_review_confidence_none(self) -> None:
        review = ReasoningReview()
        result = review.review_confidence(None)
        assert result["passed"] is False
        assert any("No confidence" in e for e in result["errors"])

    def test_perform_full_review_all_valid(self) -> None:
        review = ReasoningReview()
        goals = [
            ReasoningGoal(description="Goal", goal_type=ReasoningGoalType.ROOT_CAUSE_ANALYSIS, is_primary=True),
        ]
        alternatives = [
            ReasoningAlternative(
                decision_description="Alt",
                reasoning=["OK"],
                confidence=0.8,
                evidence_ids=[],
                status=AlternativeStatus.EVALUATED,
            ),
        ]
        confidence = ReasoningConfidence(overall_confidence=0.85)
        result = review.perform_full_review(
            goals=goals,
            alternatives=alternatives,
            confidence=confidence,
        )
        assert result.passed is True
        assert result.overall_score >= 0.7
        assert len(result.errors) == 0

    def test_perform_full_review_with_issues(self) -> None:
        review = ReasoningReview()
        goals = [
            ReasoningGoal(description="Goal", goal_type=ReasoningGoalType.ROOT_CAUSE_ANALYSIS, is_primary=True),
        ]
        alternatives = [
            ReasoningAlternative(
                decision_description="Alt",
                reasoning=["OK"],
                confidence=0.8,
                evidence_ids=[],
                status=AlternativeStatus.EVALUATED,
            ),
        ]
        contradictions = [
            Contradiction(
                request_id=uuid.uuid4(),
                description="Major issue",
                severity=ContradictionSeverity.CRITICAL,
                resolution_status=ContradictionResolutionStatus.UNRESOLVED,
            ),
        ]
        result = review.perform_full_review(
            goals=goals,
            alternatives=alternatives,
            contradictions=contradictions,
            confidence=ReasoningConfidence(overall_confidence=0.3),
        )
        assert result.passed is False
        assert result.overall_score < 0.7
        assert len(result.warnings) > 0


# ── DecisionJustification Tests ─────────────────────────────────────────

class TestDecisionJustification:
    """Tests for DecisionJustification — builds justifications for decisions."""

    def test_default_initialization(self) -> None:
        just = DecisionJustification()
        assert just.count() == 0

    def test_add_supporting_evidence(self) -> None:
        just = DecisionJustification()
        just.add_supporting_evidence(
            evidence_ids=["e1", "e2"],
            descriptions=["Evidence one", "Evidence two"],
        )
        assert just.count() == 2

    def test_add_rule_used(self) -> None:
        just = DecisionJustification()
        just.add_rule_used("r1", "Rule one")
        result = just.build_justification()
        assert any(r["rule_id"] == "r1" for r in result.rules_used)

    def test_add_constraint_used(self) -> None:
        just = DecisionJustification()
        just.add_constraint_used("c1", "Constraint one")
        result = just.build_justification()
        assert any(c["constraint_id"] == "c1" for c in result.constraints_used)

    def test_add_assumption_used(self) -> None:
        just = DecisionJustification()
        just.add_assumption_used("a1", "Assumption one")
        result = just.build_justification()
        assert any(a["assumption_id"] == "a1" for a in result.assumptions_used)

    def test_add_alternative_selected(self) -> None:
        just = DecisionJustification()
        alt = ReasoningAlternative(
            decision_description="Best choice",
            reasoning=["Good reasoning"],
            confidence=0.9,
            evidence_ids=[],
        )
        just.add_alternative(alt, was_selected=True)
        result = just.build_justification()
        assert result.selected_alternative.get("alternative_id") == str(alt.alternative_id)

    def test_add_alternative_not_selected(self) -> None:
        just = DecisionJustification()
        alt = ReasoningAlternative(
            decision_description="Fallback",
            reasoning=["OK"],
            confidence=0.5,
            evidence_ids=[],
        )
        just.add_alternative(alt, was_selected=False)
        result = just.build_justification()
        assert len(result.alternatives) == 1
        assert result.alternatives[0]["alternative_id"] == str(alt.alternative_id)

    def test_build_justification_complete(self) -> None:
        just = DecisionJustification()
        just.add_supporting_evidence(["e1"], ["Evidence 1"])
        just.add_rule_used("r1", "Rule 1")
        just.add_constraint_used("c1", "Constraint 1")
        just.add_assumption_used("a1", "Assumption 1")

        risk = RiskAssessment(
            risk_type="test",
            score=0.25,
            level="LOW",
            description="Test Risk",
        )
        just.add_risk_assessed(risk)

        alt = ReasoningAlternative(
            decision_description="Best",
            reasoning=["Good"],
            confidence=0.9,
            evidence_ids=[],
        )
        just.add_alternative(alt, was_selected=True)

        result = just.build_justification()
        assert len(result.supporting_evidence) == 1
        assert len(result.rules_used) == 1
        assert len(result.constraints_used) == 1
        assert len(result.assumptions_used) == 1
        assert len(result.risks_assessed) == 1
        assert result.selected_alternative["alternative_id"] == str(alt.alternative_id)

    def test_clear(self) -> None:
        just = DecisionJustification()
        just.add_supporting_evidence(["e1"])
        just.clear()
        assert just.count() == 0


# ── ReasoningLineage Tests ──────────────────────────────────────────────

class TestReasoningLineage:
    """Tests for ReasoningLineage — traces the lineage of a reasoning operation."""

    def test_default_initialization(self) -> None:
        lineage = ReasoningLineage()
        assert lineage.count() == 0

    def test_add_evidence(self) -> None:
        lineage = ReasoningLineage()
        lineage.add_evidence("e1", "Evidence description")
        assert lineage.count("evidence") == 1

    def test_add_hypothesis(self) -> None:
        lineage = ReasoningLineage()
        lineage.add_hypothesis("h1", "Hypothesis description", 0.85)
        assert lineage.count("hypothesis") == 1

    def test_add_inference(self) -> None:
        lineage = ReasoningLineage()
        lineage.add_inference("i1", "Premise", "Conclusion")
        assert lineage.count("inference") == 1

    def test_add_alternative(self) -> None:
        lineage = ReasoningLineage()
        lineage.add_alternative("a1", "Alternative description", 0.75)
        assert lineage.count("alternative") == 1

    def test_set_final_decision(self) -> None:
        lineage = ReasoningLineage()
        lineage.set_final_decision("d1", "Final decision", 0.95)
        result = lineage.build_lineage()
        assert result.final_decision["decision_id"] == "d1"

    def test_build_lineage_complete(self) -> None:
        lineage = ReasoningLineage()
        lineage.add_evidence("e1", "Evidence 1")
        lineage.add_hypothesis("h1", "Hypothesis 1", 0.8)
        lineage.add_inference("i1", "Premise", "Conclusion")
        lineage.add_alternative("a1", "Alternative 1", 0.7)
        lineage.set_final_decision("a1", "Chosen alternative", 0.7)
        result = lineage.build_lineage()
        assert len(result.evidence) == 1
        assert len(result.hypotheses) == 1
        assert len(result.inferences) == 1
        assert len(result.alternatives) == 1
        assert result.final_decision["decision_id"] == "a1"

    def test_clear(self) -> None:
        lineage = ReasoningLineage()
        lineage.add_evidence("e1")
        lineage.clear()
        assert lineage.count() == 0

    def test_count_total(self) -> None:
        lineage = ReasoningLineage()
        lineage.add_evidence("e1")
        lineage.add_hypothesis("h1")
        lineage.add_inference("i1")
        assert lineage.count() == 3


# ── ReasoningSnapshot Tests ─────────────────────────────────────────────

class TestReasoningSnapshot:
    """Tests for ReasoningSnapshot — captures immutable snapshots of reasoning state."""

    def test_default_initialization(self) -> None:
        snap = ReasoningSnapshot()
        assert snap.count() == 0

    def test_create_snapshot_minimal(self) -> None:
        snap = ReasoningSnapshot()
        result = snap.create_snapshot()
        assert result.snapshot_id is not None
        assert snap.count() == 1

    def test_create_snapshot_full(self) -> None:
        snap = ReasoningSnapshot()
        alternatives = [
            ReasoningAlternative(
                decision_description="Test",
                reasoning=["OK"],
                confidence=0.8,
                evidence_ids=[],
            ),
        ]
        confidence = ReasoningConfidence(overall_confidence=0.75)
        result = snap.create_snapshot(
            alternatives=alternatives,
            confidence=confidence,
            metadata={"key": "value"},
        )
        assert result.snapshot_id is not None
        assert snap.count() == 1

    def test_get_snapshot(self) -> None:
        snap = ReasoningSnapshot()
        snap1 = snap.create_snapshot(metadata={"test": "data"})
        retrieved = snap.get_snapshot(snap1.snapshot_id)
        assert retrieved is not None
        assert retrieved.snapshot_id == snap1.snapshot_id

    def test_get_snapshot_not_found(self) -> None:
        snap = ReasoningSnapshot()
        result = snap.get_snapshot("nonexistent")
        assert result is None

    def test_get_all_snapshots(self) -> None:
        snap = ReasoningSnapshot()
        snap.create_snapshot()
        snap.create_snapshot()
        all_snaps = snap.get_all_snapshots()
        assert len(all_snaps) == 2

    def test_clear(self) -> None:
        snap = ReasoningSnapshot()
        snap.create_snapshot()
        snap.clear()
        assert snap.count() == 0


# ── StrategyPerformance Tests ────────────────────────────────────────────

class TestStrategyPerformance:
    """Tests for StrategyPerformance — tracks execution performance of reasoning strategies."""

    def test_default_initialization(self) -> None:
        sp = StrategyPerformance()
        assert sp.count() == 0

    def test_record_execution_success(self) -> None:
        sp = StrategyPerformance()
        record = sp.record_execution(
            strategy=ReasoningStrategyType.RULE_BASED,
            success=True,
            latency_ms=100.0,
            confidence=0.85,
        )
        assert isinstance(record, StrategyPerformanceRecord)
        assert record.strategy == ReasoningStrategyType.RULE_BASED
        assert record.successful == 1
        assert record.failed == 0
        assert sp.count() == 1

    def test_record_execution_failure(self) -> None:
        sp = StrategyPerformance()
        sp.record_execution(
            strategy=ReasoningStrategyType.EVIDENCE_BASED,
            success=False,
            latency_ms=50.0,
            confidence=0.3,
        )
        record = sp.get_performance(ReasoningStrategyType.EVIDENCE_BASED)
        assert record is not None
        assert record.successful == 0
        assert record.failed == 1

    def test_record_multiple_executions(self) -> None:
        sp = StrategyPerformance()
        sp.record_execution(ReasoningStrategyType.RULE_BASED, True, 100.0, 0.9)
        sp.record_execution(ReasoningStrategyType.RULE_BASED, True, 200.0, 0.8)
        sp.record_execution(ReasoningStrategyType.RULE_BASED, False, 150.0, 0.4)
        record = sp.get_performance(ReasoningStrategyType.RULE_BASED)
        assert record.total_executions == 3
        assert record.successful == 2
        assert record.failed == 1

    def test_get_performance_nonexistent(self) -> None:
        sp = StrategyPerformance()
        result = sp.get_performance(ReasoningStrategyType.HYPOTHESIS)
        assert result is None

    def test_get_all_performance(self) -> None:
        sp = StrategyPerformance()
        sp.record_execution(ReasoningStrategyType.RULE_BASED, True, 100.0, 0.9)
        sp.record_execution(ReasoningStrategyType.EVIDENCE_BASED, False, 50.0, 0.3)
        all_perf = sp.get_all_performance()
        assert len(all_perf) == 2

    def test_get_success_rate(self) -> None:
        sp = StrategyPerformance()
        sp.record_execution(ReasoningStrategyType.RULE_BASED, True, 100.0, 0.9)
        sp.record_execution(ReasoningStrategyType.RULE_BASED, True, 100.0, 0.9)
        sp.record_execution(ReasoningStrategyType.RULE_BASED, False, 100.0, 0.3)
        rate = sp.get_success_rate(ReasoningStrategyType.RULE_BASED)
        assert pytest.approx(rate, 0.01) == 2.0 / 3.0

    def test_get_success_rate_all_none(self) -> None:
        sp = StrategyPerformance()
        rate = sp.get_success_rate()
        assert rate == 0.0

    def test_get_failure_rate(self) -> None:
        sp = StrategyPerformance()
        sp.record_execution(ReasoningStrategyType.RULE_BASED, True, 100.0, 0.9)
        sp.record_execution(ReasoningStrategyType.RULE_BASED, False, 100.0, 0.3)
        rate = sp.get_failure_rate(ReasoningStrategyType.RULE_BASED)
        assert pytest.approx(rate, 0.01) == 0.5

    def test_get_average_latency(self) -> None:
        sp = StrategyPerformance()
        sp.record_execution(ReasoningStrategyType.RULE_BASED, True, 100.0, 0.9)
        sp.record_execution(ReasoningStrategyType.RULE_BASED, True, 200.0, 0.8)
        avg = sp.get_average_latency(ReasoningStrategyType.RULE_BASED)
        assert avg == 150.0

    def test_get_average_confidence(self) -> None:
        sp = StrategyPerformance()
        sp.record_execution(ReasoningStrategyType.RULE_BASED, True, 100.0, 0.9)
        sp.record_execution(ReasoningStrategyType.RULE_BASED, True, 100.0, 0.7)
        avg = sp.get_average_confidence(ReasoningStrategyType.RULE_BASED)
        assert pytest.approx(avg, 0.01) == 0.8

    def test_clear(self) -> None:
        sp = StrategyPerformance()
        sp.record_execution(ReasoningStrategyType.RULE_BASED, True, 100.0, 0.9)
        sp.clear()
        assert sp.count() == 0


# ── DecisionReadiness Tests ─────────────────────────────────────────────

class TestDecisionReadiness:
    """Tests for DecisionReadiness — assesses whether a decision is ready to be made."""

    def test_default_initialization(self) -> None:
        dr = DecisionReadiness()
        assert dr.count() == 0

    def test_assess_readiness_ready(self) -> None:
        dr = DecisionReadiness()
        result = dr.assess_readiness(
            confidence=0.85,
            risk_score=0.2,
            contradiction_count=0,
            constraint_violations=0,
            alternatives_count=3,
            quality_score=0.9,
        )
        assert result.readiness == "READY"
        assert result.overall_score >= 0.7

    def test_assess_readiness_not_ready(self) -> None:
        dr = DecisionReadiness()
        result = dr.assess_readiness(
            confidence=0.2,
            risk_score=0.9,
            contradiction_count=5,
            constraint_violations=3,
            alternatives_count=0,
            quality_score=0.1,
        )
        assert result.readiness == "NOT_READY"
        assert result.overall_score < 0.5

    def test_assess_readiness_more_info(self) -> None:
        dr = DecisionReadiness()
        result = dr.assess_readiness(
            confidence=0.5,
            risk_score=0.5,
            contradiction_count=1,
            constraint_violations=0,
            alternatives_count=1,
            quality_score=0.5,
        )
        assert result.readiness == "MORE_INFORMATION_REQUIRED"

    def test_assess_readiness_boundary_ready(self) -> None:
        dr = DecisionReadiness()
        result = dr.assess_readiness(
            confidence=0.7,
            risk_score=0.49,
            contradiction_count=0,
            constraint_violations=0,
            alternatives_count=2,
            quality_score=0.7,
        )
        assert result.readiness == "READY"

    def test_assess_readiness_boundary_not_ready_high_risk(self) -> None:
        dr = DecisionReadiness()
        result = dr.assess_readiness(
            confidence=0.6,
            risk_score=0.8,
            contradiction_count=0,
            constraint_violations=0,
            alternatives_count=2,
            quality_score=0.6,
        )
        assert result.readiness == "NOT_READY"

    def test_assess_readiness_boundary_not_ready_low_confidence(self) -> None:
        dr = DecisionReadiness()
        result = dr.assess_readiness(
            confidence=0.29,
            risk_score=0.4,
            contradiction_count=0,
            constraint_violations=0,
            alternatives_count=2,
            quality_score=0.6,
        )
        assert result.readiness == "NOT_READY"

    def test_assess_readiness_boundary_not_ready_low_quality(self) -> None:
        dr = DecisionReadiness()
        result = dr.assess_readiness(
            confidence=0.7,
            risk_score=0.4,
            contradiction_count=0,
            constraint_violations=0,
            alternatives_count=2,
            quality_score=0.29,
        )
        assert result.readiness == "NOT_READY"

    def test_get_readiness(self) -> None:
        dr = DecisionReadiness()
        result = dr.assess_readiness(
            confidence=0.85,
            risk_score=0.2,
            contradiction_count=0,
            constraint_violations=0,
            alternatives_count=3,
            quality_score=0.9,
        )
        retrieved = dr.get_readiness(result.decision_id)
        assert retrieved is not None
        assert retrieved.readiness == "READY"

    def test_get_readiness_not_found(self) -> None:
        dr = DecisionReadiness()
        result = dr.get_readiness("nonexistent")
        assert result is None

    def test_get_all_readiness(self) -> None:
        dr = DecisionReadiness()
        dr.assess_readiness(confidence=0.8, risk_score=0.2, contradiction_count=0, constraint_violations=0, alternatives_count=2, quality_score=0.8)
        dr.assess_readiness(confidence=0.3, risk_score=0.7, contradiction_count=3, constraint_violations=2, alternatives_count=0, quality_score=0.2)
        all_r = dr.get_all_readiness()
        assert len(all_r) == 2

    def test_clear(self) -> None:
        dr = DecisionReadiness()
        dr.assess_readiness(confidence=0.8, risk_score=0.2, contradiction_count=0, constraint_violations=0, alternatives_count=2, quality_score=0.8)
        dr.clear()
        assert dr.count() == 0


# ── ReasoningExplainabilityMetadata Tests ──────────────────────────────

class TestReasoningExplainabilityMetadataPhase35:
    """Tests for Phase 3.5 enhancements to ReasoningExplainabilityMetadata."""

    def test_new_why_fields_exist(self) -> None:
        metadata = ReasoningExplainabilityMetadata(
            why_strategy_selected="Deductive reasoning selected for energy domain",
            why_goal_chosen="Root cause analysis selected for fault detection",
            why_assumption_made="Assumed sensor data is accurate",
            why_constraint_applied="Safety constraint applied due to high voltage",
            why_primary_selected="Alternative A1 had highest confidence score",
            why_alternative_rejected="Alternative A2 had unresolved contradictions",
        )
        assert metadata.why_strategy_selected == "Deductive reasoning selected for energy domain"
        assert metadata.why_goal_chosen == "Root cause analysis selected for fault detection"
        assert metadata.why_assumption_made == "Assumed sensor data is accurate"
        assert metadata.why_constraint_applied == "Safety constraint applied due to high voltage"
        assert metadata.why_primary_selected == "Alternative A1 had highest confidence score"
        assert metadata.why_alternative_rejected == "Alternative A2 had unresolved contradictions"

    def test_new_why_fields_default(self) -> None:
        metadata = ReasoningExplainabilityMetadata()
        assert metadata.why_strategy_selected == ""
        assert metadata.why_goal_chosen == ""
        assert metadata.why_assumption_made == ""
        assert metadata.why_constraint_applied == ""
        assert metadata.why_primary_selected == ""
        assert metadata.why_alternative_rejected == ""

    def test_backward_compatibility(self) -> None:
        metadata = ReasoningExplainabilityMetadata()
        assert hasattr(metadata, "why_strategy_selected")
        assert hasattr(metadata, "why_goal_chosen")
        assert hasattr(metadata, "why_assumption_made")
        assert hasattr(metadata, "why_constraint_applied")
        assert hasattr(metadata, "why_primary_selected")
        assert hasattr(metadata, "why_alternative_rejected")


# ── ReasoningConfidence Consensus Field Tests ──────────────────────────

class TestReasoningConfidencePhase35:
    """Tests for Phase 3.5 consensus field in ReasoningConfidence."""

    def test_consensus_field_default(self) -> None:
        confidence = ReasoningConfidence(overall_confidence=0.75)
        assert confidence.consensus == 0.0

    def test_consensus_field_custom(self) -> None:
        confidence = ReasoningConfidence(overall_confidence=0.75, consensus=0.85)
        assert confidence.consensus == 0.85

    def test_consensus_field_clamping(self) -> None:
        with pytest.raises(ValidationError):
            ReasoningConfidence(overall_confidence=0.75, consensus=1.5)
        with pytest.raises(ValidationError):
            ReasoningConfidence(overall_confidence=0.75, consensus=-0.5)

    def test_consensus_field_in_confidence(self) -> None:
        confidence = ReasoningConfidence(
            overall_confidence=0.8,
            evidence_support=0.7,
            contradiction_resolution=0.9,
            inference_strength=0.75,
            hypothesis_coverage=0.8,
            uncertainty_level=0.1,
            path_consistency=0.85,
            goal_alignment=0.9,
            policy_compliance=1.0,
            risk_level=0.8,
            impact_score=0.7,
            ranking_quality=0.75,
            consensus=0.82,
        )
        assert confidence.consensus == 0.82
        assert confidence.overall_confidence == 0.8


# ── ReasoningDecision Quality Score & Readiness Status Tests ────────────

class TestReasoningDecisionPhase35:
    """Tests for Phase 3.5 quality_score and readiness_status fields in ReasoningDecision."""

    def test_quality_score_default(self) -> None:
        decision = ReasoningDecision(
            result_id=uuid.uuid4(),
            conclusion="Test",
            reasoning_summary="Summary",
            confidence=0.8,
            selected_hypotheses=[],
            rejected_hypotheses=[],
        )
        assert decision.quality_score == 0.0

    def test_readiness_status_default(self) -> None:
        decision = ReasoningDecision(
            result_id=uuid.uuid4(),
            conclusion="Test",
            reasoning_summary="Summary",
            confidence=0.8,
            selected_hypotheses=[],
            rejected_hypotheses=[],
        )
        assert decision.readiness_status == "NOT_READY"

    def test_quality_score_custom(self) -> None:
        decision = ReasoningDecision(
            result_id=uuid.uuid4(),
            conclusion="Test",
            reasoning_summary="Summary",
            confidence=0.8,
            selected_hypotheses=[],
            rejected_hypotheses=[],
            quality_score=0.85,
            readiness_status="READY",
        )
        assert decision.quality_score == 0.85
        assert decision.readiness_status == "READY"

    def test_quality_score_validates_range(self) -> None:
        with pytest.raises(ValidationError):
            ReasoningDecision(
                result_id=uuid.uuid4(),
                conclusion="Test",
                reasoning_summary="Summary",
                confidence=0.8,
                selected_hypotheses=[],
                rejected_hypotheses=[],
                quality_score=1.5,
            )

    def test_readiness_status_values(self) -> None:
        for status in ("READY", "NOT_READY", "MORE_INFORMATION_REQUIRED"):
            decision = ReasoningDecision(
                result_id=uuid.uuid4(),
                conclusion="Test",
                reasoning_summary="Summary",
                confidence=0.8,
                selected_hypotheses=[],
                rejected_hypotheses=[],
                readiness_status=status,
            )
            assert decision.readiness_status == status


# ── DecisionReadinessStatus Enum Tests ──────────────────────────────────

class TestDecisionReadinessStatus:
    """Tests for DecisionReadinessStatus enum."""

    def test_values(self) -> None:
        assert DecisionReadinessStatus.READY.value == "READY"
        assert DecisionReadinessStatus.NOT_READY.value == "NOT_READY"
        assert DecisionReadinessStatus.MORE_INFORMATION_REQUIRED.value == "MORE_INFORMATION_REQUIRED"

    def test_membership(self) -> None:
        assert "READY" in [e.value for e in DecisionReadinessStatus]


# ── TraceStage Enum Phase 3.5 Tests ─────────────────────────────────────

class TestTraceStagePhase35:
    """Tests for Phase 3.5 TraceStage values."""

    def test_review_stage_exists(self) -> None:
        assert TraceStage.REVIEW.value == "REVIEW"

    def test_ranking_stage_exists(self) -> None:
        assert TraceStage.RANKING.value == "RANKING"

    def test_readiness_stage_exists(self) -> None:
        assert TraceStage.READINESS.value == "READINESS"

    def test_new_stages_registered(self) -> None:
        stages = [s.value for s in TraceStage]
        assert "REVIEW" in stages
        assert "RANKING" in stages
        assert "READINESS" in stages


# ── Trace Stage Recording Methods Tests ─────────────────────────────────

class TestReasoningTracePhase35:
    """Tests for Phase 3.5 trace stage recording methods."""

    def test_record_review_stage(self) -> None:
        trace = ReasoningTrace()
        record = trace.record_review_stage(reasoning_id="r1", correlation_id="c1", duration_ms=10.0)
        assert record.stage_name == "REVIEW"
        assert record.reasoning_id == "r1"
        assert record.correlation_id == "c1"
        assert record.duration_ms == 10.0

    def test_record_ranking_stage(self) -> None:
        trace = ReasoningTrace()
        record = trace.record_ranking_stage(reasoning_id="r1", correlation_id="c1")
        assert record.stage_name == "RANKING"
        assert record.reasoning_id == "r1"

    def test_record_readiness_stage(self) -> None:
        trace = ReasoningTrace()
        record = trace.record_readiness_stage(reasoning_id="r1", correlation_id="c1")
        assert record.stage_name == "READINESS"
        assert record.reasoning_id == "r1"

    def test_get_by_reasoning_id(self) -> None:
        trace = ReasoningTrace()
        trace.record_review_stage(reasoning_id="r1")
        trace.record_ranking_stage(reasoning_id="r1")
        trace.record_readiness_stage(reasoning_id="r1")
        records = trace.get_by_reasoning_id("r1")
        stage_names = [r.stage_name for r in records]
        assert "REVIEW" in stage_names
        assert "RANKING" in stage_names
        assert "READINESS" in stage_names


# ── Metrics Phase 3.5 Tests ─────────────────────────────────────────────

class TestReasoningMetricsCollectorPhase35:
    """Tests for Phase 3.5 metrics counters."""

    def test_increment_reviews(self) -> None:
        metrics = ReasoningMetricsCollector()
        metrics.increment_reviews()
        snap = metrics.snapshot()
        assert snap.review_count == 1

    def test_increment_reviews_multiple(self) -> None:
        metrics = ReasoningMetricsCollector()
        metrics.increment_reviews(5)
        snap = metrics.snapshot()
        assert snap.review_count == 5

    def test_increment_readiness_ready(self) -> None:
        metrics = ReasoningMetricsCollector()
        metrics.increment_readiness_ready()
        snap = metrics.snapshot()
        assert snap.readiness_ready == 1

    def test_increment_readiness_not_ready(self) -> None:
        metrics = ReasoningMetricsCollector()
        metrics.increment_readiness_not_ready()
        snap = metrics.snapshot()
        assert snap.readiness_not_ready == 1

    def test_increment_readiness_more_info(self) -> None:
        metrics = ReasoningMetricsCollector()
        metrics.increment_readiness_more_info()
        snap = metrics.snapshot()
        assert snap.readiness_more_info == 1

    def test_record_quality_score(self) -> None:
        metrics = ReasoningMetricsCollector()
        metrics.record_quality_score(0.85)
        snap = metrics.snapshot()
        assert snap.average_quality == 0.85

    def test_record_quality_score_multiple(self) -> None:
        metrics = ReasoningMetricsCollector()
        metrics.record_quality_score(0.8)
        metrics.record_quality_score(0.9)
        metrics.record_quality_score(1.0)
        snap = metrics.snapshot()
        assert snap.average_quality == 0.9
        assert snap.review_count == 0

    def test_reset_resets_new_fields(self) -> None:
        metrics = ReasoningMetricsCollector()
        metrics.increment_reviews()
        metrics.increment_readiness_ready()
        metrics.record_quality_score(0.85)
        metrics.reset()
        snap = metrics.snapshot()
        assert snap.review_count == 0
        assert snap.readiness_ready == 0
        assert snap.average_quality == 0.0

    def test_snapshot_includes_new_fields(self) -> None:
        metrics = ReasoningMetricsCollector()
        snap = metrics.snapshot()
        assert hasattr(snap, "review_count")
        assert hasattr(snap, "readiness_ready")
        assert hasattr(snap, "readiness_not_ready")
        assert hasattr(snap, "readiness_more_info")
        assert hasattr(snap, "average_quality")
