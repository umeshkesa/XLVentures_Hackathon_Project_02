"""Phase 1 tests for the Recommendation Engine (Architecture, Contracts & Models).

Tests all Phase 1 components: enums, models, DTOs, events, exceptions,
and their relationships. Validates that all contracts are correctly
defined and behave as expected.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from adip.recommendation import (
    BenefitType,
    ConstraintType,
    RecommendationBenefit,
    RecommendationCandidate,
    RecommendationCompleted,
    RecommendationConfidence,
    RecommendationConstraint,
    RecommendationContext,
    RecommendationDecision,
    RecommendationDomain,
    RecommendationEvent,
    RecommendationException,
    RecommendationExplainabilityMetadata,
    RecommendationGenerated,
    RecommendationGoal,
    RecommendationGoalModel,
    RecommendationHealth,
    RecommendationImpact,
    RecommendationMetadata,
    RecommendationMetrics,
    RecommendationPackage,
    RecommendationPackageDTO,
    RecommendationPolicy,
    RecommendationPolicyException,
    RecommendationPriority,
    RecommendationPriorityModel,
    RecommendationRanked,
    RecommendationRankingException,
    RecommendationRequest,
    RecommendationRequestDTO,
    RecommendationRequested,
    RecommendationResponseDTO,
    RecommendationResult,
    RecommendationRisk,
    RecommendationSession,
    RecommendationStatus,
    RecommendationStrategy,
    RecommendationStrategyModel,
    RecommendationTrace,
    RecommendationValidated,
    RecommendationValidationException,
)

# ═══════════════════════════════════════════════════════════════════════
# Enums
# ═══════════════════════════════════════════════════════════════════════


class TestRecommendationStrategy:
    def test_values(self) -> None:
        assert RecommendationStrategy.NEXT_BEST_ACTION.value == "NEXT_BEST_ACTION"
        assert RecommendationStrategy.RISK_MITIGATION.value == "RISK_MITIGATION"
        assert RecommendationStrategy.PREVENTIVE_MAINTENANCE.value == "PREVENTIVE_MAINTENANCE"
        assert RecommendationStrategy.COST_OPTIMIZATION.value == "COST_OPTIMIZATION"
        assert RecommendationStrategy.ENERGY_OPTIMIZATION.value == "ENERGY_OPTIMIZATION"
        assert RecommendationStrategy.SLA_RECOVERY.value == "SLA_RECOVERY"
        assert RecommendationStrategy.HYBRID_RECOMMENDATION.value == "HYBRID_RECOMMENDATION"

    def test_unique_values(self) -> None:
        values = [e.value for e in RecommendationStrategy]
        assert len(values) == len(set(values))

    def test_count(self) -> None:
        assert len(RecommendationStrategy) == 7


class TestRecommendationGoal:
    def test_values(self) -> None:
        assert RecommendationGoal.REDUCE_DOWNTIME.value == "REDUCE_DOWNTIME"
        assert RecommendationGoal.REDUCE_COST.value == "REDUCE_COST"
        assert RecommendationGoal.INCREASE_SAFETY.value == "INCREASE_SAFETY"
        assert RecommendationGoal.REDUCE_ENERGY_CONSUMPTION.value == "REDUCE_ENERGY_CONSUMPTION"
        assert RecommendationGoal.MEET_SLA.value == "MEET_SLA"
        assert RecommendationGoal.IMPROVE_CUSTOMER_SATISFACTION.value == "IMPROVE_CUSTOMER_SATISFACTION"
        assert RecommendationGoal.INCREASE_ASSET_RELIABILITY.value == "INCREASE_ASSET_RELIABILITY"

    def test_unique_values(self) -> None:
        values = [e.value for e in RecommendationGoal]
        assert len(values) == len(set(values))

    def test_count(self) -> None:
        assert len(RecommendationGoal) == 7


class TestRecommendationStatus:
    def test_values(self) -> None:
        assert RecommendationStatus.INITIALIZED.value == "INITIALIZED"
        assert RecommendationStatus.GENERATED.value == "GENERATED"
        assert RecommendationStatus.RANKED.value == "RANKED"
        assert RecommendationStatus.VALIDATED.value == "VALIDATED"
        assert RecommendationStatus.APPROVED.value == "APPROVED"
        assert RecommendationStatus.COMPLETED.value == "COMPLETED"
        assert RecommendationStatus.FAILED.value == "FAILED"

    def test_unique_values(self) -> None:
        values = [e.value for e in RecommendationStatus]
        assert len(values) == len(set(values))

    def test_count(self) -> None:
        assert len(RecommendationStatus) == 7


class TestRecommendationDomain:
    def test_values(self) -> None:
        assert RecommendationDomain.SYSTEM.value == "SYSTEM"
        assert RecommendationDomain.ENERGY.value == "ENERGY"
        assert RecommendationDomain.MAINTENANCE.value == "MAINTENANCE"
        assert RecommendationDomain.OPERATIONS.value == "OPERATIONS"
        assert RecommendationDomain.CUSTOMER.value == "CUSTOMER"
        assert RecommendationDomain.SAFETY.value == "SAFETY"
        assert RecommendationDomain.COMPLIANCE.value == "COMPLIANCE"
        assert RecommendationDomain.WORKFLOW.value == "WORKFLOW"
        assert RecommendationDomain.PLANNING.value == "PLANNING"
        assert RecommendationDomain.GENERAL.value == "GENERAL"

    def test_unique_values(self) -> None:
        values = [e.value for e in RecommendationDomain]
        assert len(values) == len(set(values))

    def test_count(self) -> None:
        assert len(RecommendationDomain) == 10


class TestRecommendationPriority:
    def test_values(self) -> None:
        assert RecommendationPriority.CRITICAL.value == "CRITICAL"
        assert RecommendationPriority.HIGH.value == "HIGH"
        assert RecommendationPriority.MEDIUM.value == "MEDIUM"
        assert RecommendationPriority.LOW.value == "LOW"
        assert RecommendationPriority.OPTIONAL.value == "OPTIONAL"

    def test_unique_values(self) -> None:
        values = [e.value for e in RecommendationPriority]
        assert len(values) == len(set(values))

    def test_count(self) -> None:
        assert len(RecommendationPriority) == 5


class TestConstraintType:
    def test_values(self) -> None:
        assert ConstraintType.HARD.value == "HARD"
        assert ConstraintType.SOFT.value == "SOFT"
        assert ConstraintType.BUDGET.value == "BUDGET"
        assert ConstraintType.TIME.value == "TIME"

    def test_unique_values(self) -> None:
        values = [e.value for e in ConstraintType]
        assert len(values) == len(set(values))

    def test_count(self) -> None:
        assert len(ConstraintType) == 4


class TestBenefitType:
    def test_values(self) -> None:
        assert BenefitType.COST_SAVING.value == "COST_SAVING"
        assert BenefitType.EFFICIENCY_GAIN.value == "EFFICIENCY_GAIN"
        assert BenefitType.SAFETY_IMPROVEMENT.value == "SAFETY_IMPROVEMENT"
        assert BenefitType.RISK_REDUCTION.value == "RISK_REDUCTION"
        assert BenefitType.RELIABILITY_IMPROVEMENT.value == "RELIABILITY_IMPROVEMENT"

    def test_unique_values(self) -> None:
        values = [e.value for e in BenefitType]
        assert len(values) == len(set(values))

    def test_count(self) -> None:
        assert len(BenefitType) == 5


# ═══════════════════════════════════════════════════════════════════════
# RecommendationRequest
# ═══════════════════════════════════════════════════════════════════════


class TestRecommendationRequest:
    def test_default_request(self) -> None:
        req = RecommendationRequest()
        assert req.request_id is not None
        assert req.reasoning_result_id is not None
        assert req.domain == RecommendationDomain.GENERAL
        assert req.strategy == RecommendationStrategy.NEXT_BEST_ACTION
        assert req.goals == []
        assert req.context == {}
        assert req.metadata == {}

    def test_request_with_values(self) -> None:
        rid = uuid.uuid4()
        req = RecommendationRequest(
            reasoning_result_id=rid,
            domain=RecommendationDomain.ENERGY,
            strategy=RecommendationStrategy.RISK_MITIGATION,
            goals=[RecommendationGoal.REDUCE_COST],
            context={"asset_id": "asset-1"},
            metadata={"source": "test"},
        )
        assert req.domain == RecommendationDomain.ENERGY
        assert req.strategy == RecommendationStrategy.RISK_MITIGATION
        assert len(req.goals) == 1
        assert req.context["asset_id"] == "asset-1"

    def test_request_unique_ids(self) -> None:
        r1 = RecommendationRequest()
        r2 = RecommendationRequest()
        assert r1.request_id != r2.request_id

    def test_request_roundtrip(self) -> None:
        rid = uuid.uuid4()
        req = RecommendationRequest(
            reasoning_result_id=rid,
            domain=RecommendationDomain.SAFETY,
        )
        data = req.model_dump()
        restored = RecommendationRequest.model_validate(data)
        assert restored.domain == RecommendationDomain.SAFETY
        assert restored.reasoning_result_id == rid
        assert restored.request_id == req.request_id


# ═══════════════════════════════════════════════════════════════════════
# RecommendationResult
# ═══════════════════════════════════════════════════════════════════════


class TestRecommendationResult:
    def test_default_result(self) -> None:
        rid = uuid.uuid4()
        result = RecommendationResult(request_id=rid)
        assert result.request_id == rid
        assert result.decision is None
        assert result.package is None
        assert result.candidates == []
        assert result.confidence is None
        assert result.status == RecommendationStatus.INITIALIZED

    def test_result_requires_request_id(self) -> None:
        with pytest.raises(ValidationError):
            RecommendationResult()

    def test_result_with_decision(self) -> None:
        rid = uuid.uuid4()
        decision = RecommendationDecision(result_id=rid, conclusion="Proceed with action")
        result = RecommendationResult(
            request_id=rid,
            decision=decision,
            status=RecommendationStatus.COMPLETED,
        )
        assert result.decision is not None
        assert result.decision.conclusion == "Proceed with action"
        assert result.status == RecommendationStatus.COMPLETED

    def test_result_roundtrip(self) -> None:
        rid = uuid.uuid4()
        result = RecommendationResult(
            request_id=rid,
            status=RecommendationStatus.COMPLETED,
        )
        data = result.model_dump()
        restored = RecommendationResult.model_validate(data)
        assert restored.status == RecommendationStatus.COMPLETED


# ═══════════════════════════════════════════════════════════════════════
# RecommendationDecision
# ═══════════════════════════════════════════════════════════════════════


class TestRecommendationDecision:
    def test_default_decision(self) -> None:
        rid = uuid.uuid4()
        d = RecommendationDecision(result_id=rid)
        assert d.result_id == rid
        assert d.conclusion == ""
        assert d.reasoning_summary == ""
        assert d.confidence == 0.0
        assert d.selected_candidates == []
        assert d.rejected_candidates == []

    def test_decision_with_values(self) -> None:
        rid = uuid.uuid4()
        d = RecommendationDecision(
            result_id=rid,
            conclusion="Schedule maintenance",
            reasoning_summary="Based on risk analysis",
            confidence=0.85,
            selected_candidates=["candidate-1"],
            rejected_candidates=["candidate-2"],
        )
        assert d.conclusion == "Schedule maintenance"
        assert d.confidence == 0.85
        assert len(d.selected_candidates) == 1
        assert len(d.rejected_candidates) == 1

    def test_decision_requires_result_id(self) -> None:
        with pytest.raises(ValidationError):
            RecommendationDecision()

    def test_decision_confidence_bounds(self) -> None:
        rid = uuid.uuid4()
        with pytest.raises(ValidationError):
            RecommendationDecision(result_id=rid, confidence=-0.1)
        with pytest.raises(ValidationError):
            RecommendationDecision(result_id=rid, confidence=1.1)

    def test_decision_with_package(self) -> None:
        rid = uuid.uuid4()
        pkg = RecommendationPackage(result_id=rid)
        d = RecommendationDecision(
            result_id=rid,
            conclusion="Approved",
            package=pkg,
        )
        assert d.package is not None
        assert d.package.result_id == rid


# ═══════════════════════════════════════════════════════════════════════
# RecommendationPackage
# ═══════════════════════════════════════════════════════════════════════


class TestRecommendationPackage:
    def test_default_package(self) -> None:
        rid = uuid.uuid4()
        pkg = RecommendationPackage(result_id=rid)
        assert pkg.result_id == rid
        assert pkg.primary_candidate is None
        assert pkg.alternate_candidates == []
        assert pkg.merged_benefits == []
        assert pkg.merged_risks == []
        assert pkg.overall_confidence == 0.0

    def test_package_requires_result_id(self) -> None:
        with pytest.raises(ValidationError):
            RecommendationPackage()

    def test_package_with_primary_candidate(self) -> None:
        rid = uuid.uuid4()
        candidate = RecommendationCandidate(
            description="Replace filter",
            action="Replace air filter HEPA-123",
        )
        pkg = RecommendationPackage(
            result_id=rid,
            primary_candidate=candidate,
            overall_confidence=0.85,
        )
        assert pkg.primary_candidate is not None
        assert pkg.primary_candidate.description == "Replace filter"
        assert pkg.overall_confidence == 0.85

    def test_package_with_alternates(self) -> None:
        rid = uuid.uuid4()
        primary = RecommendationCandidate(description="Primary action")
        alternate = RecommendationCandidate(description="Alternate action")
        pkg = RecommendationPackage(
            result_id=rid,
            primary_candidate=primary,
            alternate_candidates=[alternate],
        )
        assert len(pkg.alternate_candidates) == 1
        assert pkg.alternate_candidates[0].description == "Alternate action"

    def test_package_with_benefits_and_risks(self) -> None:
        rid = uuid.uuid4()
        benefit = RecommendationBenefit(description="Cost saving")
        risk = RecommendationRisk(description="Implementation delay")
        pkg = RecommendationPackage(
            result_id=rid,
            merged_benefits=[benefit],
            merged_risks=[risk],
        )
        assert len(pkg.merged_benefits) == 1
        assert len(pkg.merged_risks) == 1


# ═══════════════════════════════════════════════════════════════════════
# RecommendationCandidate
# ═══════════════════════════════════════════════════════════════════════


class TestRecommendationCandidate:
    def test_default_candidate(self) -> None:
        c = RecommendationCandidate()
        assert c.candidate_id is not None
        assert c.description == ""
        assert c.action == ""
        assert c.domain == RecommendationDomain.GENERAL
        assert c.priority == RecommendationPriority.MEDIUM
        assert c.confidence == 0.0
        assert c.expected_benefits == []
        assert c.expected_risks == []
        assert c.score == 0.0

    def test_candidate_with_values(self) -> None:
        benefit = RecommendationBenefit(description="Reduce downtime")
        risk = RecommendationRisk(description="Initial investment")
        c = RecommendationCandidate(
            description="Upgrade to energy-efficient motor",
            action="Replace motor Model X with Model Y",
            domain=RecommendationDomain.ENERGY,
            priority=RecommendationPriority.HIGH,
            confidence=0.9,
            expected_benefits=[benefit],
            expected_risks=[risk],
            score=0.85,
            reasoning="High ROI with low implementation risk",
        )
        assert c.description == "Upgrade to energy-efficient motor"
        assert c.confidence == 0.9
        assert len(c.expected_benefits) == 1
        assert len(c.expected_risks) == 1
        assert c.score == 0.85

    def test_candidate_confidence_bounds(self) -> None:
        with pytest.raises(ValidationError):
            RecommendationCandidate(confidence=-0.1)
        with pytest.raises(ValidationError):
            RecommendationCandidate(confidence=1.1)

    def test_candidate_score_bounds(self) -> None:
        with pytest.raises(ValidationError):
            RecommendationCandidate(score=-0.1)
        with pytest.raises(ValidationError):
            RecommendationCandidate(score=1.1)


# ═══════════════════════════════════════════════════════════════════════
# RecommendationStrategy (Model)
# ═══════════════════════════════════════════════════════════════════════


class TestRecommendationStrategyModel:
    def test_default_strategy_model(self) -> None:
        s = RecommendationStrategyModel()
        assert s.strategy_id is not None
        assert s.strategy_type == RecommendationStrategy.NEXT_BEST_ACTION
        assert s.name == ""
        assert s.description == ""
        assert s.configuration == {}
        assert s.domain is None
        assert s.is_active is True
        assert s.priority == 0

    def test_strategy_model_with_values(self) -> None:
        s = RecommendationStrategyModel(
            strategy_type=RecommendationStrategy.RISK_MITIGATION,
            name="Risk Mitigation Engine",
            description="Standard risk mitigation strategy",
            configuration={"max_risk_score": 0.8},
            domain=RecommendationDomain.SAFETY,
            is_active=True,
            priority=5,
        )
        assert s.name == "Risk Mitigation Engine"
        assert s.configuration["max_risk_score"] == 0.8
        assert s.domain == RecommendationDomain.SAFETY
        assert s.priority == 5


# ═══════════════════════════════════════════════════════════════════════
# RecommendationGoal (Model)
# ═══════════════════════════════════════════════════════════════════════


class TestRecommendationGoalModel:
    def test_default_goal_model(self) -> None:
        g = RecommendationGoalModel()
        assert g.goal_id is not None
        assert g.goal_type == RecommendationGoal.REDUCE_DOWNTIME
        assert g.name == ""
        assert g.target_value is None
        assert g.priority == 0
        assert g.is_primary is False

    def test_goal_model_with_values(self) -> None:
        g = RecommendationGoalModel(
            goal_type=RecommendationGoal.REDUCE_COST,
            name="Cost Reduction",
            description="Reduce operational costs by 15%",
            target_value=15.0,
            priority=10,
            is_primary=True,
        )
        assert g.goal_type == RecommendationGoal.REDUCE_COST
        assert g.name == "Cost Reduction"
        assert g.target_value == 15.0
        assert g.priority == 10
        assert g.is_primary is True


# ═══════════════════════════════════════════════════════════════════════
# RecommendationContext
# ═══════════════════════════════════════════════════════════════════════


class TestRecommendationContext:
    def test_default_context(self) -> None:
        c = RecommendationContext()
        assert c.asset_id == ""
        assert c.machine_id == ""
        assert c.facility_id == ""
        assert c.customer_id == ""
        assert c.workflow_id == ""
        assert c.incident_id == ""
        assert c.planner_goal == ""
        assert c.time_window_start is None
        assert c.time_window_end is None

    def test_context_with_values(self) -> None:
        now = datetime.now(UTC)
        c = RecommendationContext(
            asset_id="asset-1",
            machine_id="machine-1",
            facility_id="facility-1",
            planner_goal="optimize production",
            time_window_start=now,
        )
        assert c.asset_id == "asset-1"
        assert c.planner_goal == "optimize production"
        assert c.time_window_start == now

    def test_context_without_required_ids(self) -> None:
        c = RecommendationContext()
        assert c.context_id is not None


# ═══════════════════════════════════════════════════════════════════════
# RecommendationConstraint
# ═══════════════════════════════════════════════════════════════════════


class TestRecommendationConstraint:
    def test_default_constraint(self) -> None:
        c = RecommendationConstraint()
        assert c.constraint_id is not None
        assert c.constraint_type == ConstraintType.HARD
        assert c.name == ""
        assert c.description == ""
        assert c.value is None
        assert c.unit == ""
        assert c.is_active is True

    def test_constraint_with_values(self) -> None:
        c = RecommendationConstraint(
            constraint_type=ConstraintType.BUDGET,
            name="Budget cap",
            description="Total project budget cannot exceed $50,000",
            value=50000.0,
            unit="USD",
            is_active=True,
        )
        assert c.constraint_type == ConstraintType.BUDGET
        assert c.name == "Budget cap"
        assert c.value == 50000.0
        assert c.unit == "USD"


# ═══════════════════════════════════════════════════════════════════════
# RecommendationPriority (Model)
# ═══════════════════════════════════════════════════════════════════════


class TestRecommendationPriorityModel:
    def test_default_priority_model(self) -> None:
        p = RecommendationPriorityModel()
        assert p.priority_id is not None
        assert p.level == RecommendationPriority.MEDIUM
        assert p.score == 0.0
        assert p.order == 0
        assert p.reason == ""

    def test_priority_model_with_values(self) -> None:
        p = RecommendationPriorityModel(
            level=RecommendationPriority.CRITICAL,
            score=0.95,
            order=1,
            reason="Urgent safety issue",
        )
        assert p.level == RecommendationPriority.CRITICAL
        assert p.score == 0.95
        assert p.order == 1

    def test_priority_score_bounds(self) -> None:
        with pytest.raises(ValidationError):
            RecommendationPriorityModel(score=-0.1)
        with pytest.raises(ValidationError):
            RecommendationPriorityModel(score=1.1)


# ═══════════════════════════════════════════════════════════════════════
# RecommendationImpact
# ═══════════════════════════════════════════════════════════════════════


class TestRecommendationImpact:
    def test_default_impact(self) -> None:
        imp = RecommendationImpact()
        assert imp.impact_id is not None
        assert imp.cost_impact == 0.0
        assert imp.time_impact == 0.0
        assert imp.safety_impact == 0.0
        assert imp.quality_impact == 0.0
        assert imp.description == ""

    def test_impact_with_values(self) -> None:
        imp = RecommendationImpact(
            cost_impact=50000.0,
            time_impact=120.0,
            safety_impact=0.9,
            quality_impact=0.75,
            description="Significant positive impact on operations",
        )
        assert imp.cost_impact == 50000.0
        assert imp.time_impact == 120.0
        assert imp.safety_impact == 0.9
        assert imp.quality_impact == 0.75

    def test_impact_safety_bounds(self) -> None:
        with pytest.raises(ValidationError):
            RecommendationImpact(safety_impact=-0.1)
        with pytest.raises(ValidationError):
            RecommendationImpact(safety_impact=1.1)

    def test_impact_quality_bounds(self) -> None:
        with pytest.raises(ValidationError):
            RecommendationImpact(quality_impact=-0.1)
        with pytest.raises(ValidationError):
            RecommendationImpact(quality_impact=1.1)


# ═══════════════════════════════════════════════════════════════════════
# RecommendationBenefit
# ═══════════════════════════════════════════════════════════════════════


class TestRecommendationBenefit:
    def test_default_benefit(self) -> None:
        b = RecommendationBenefit()
        assert b.benefit_id is not None
        assert b.benefit_type == BenefitType.COST_SAVING
        assert b.description == ""
        assert b.estimated_value == 0.0
        assert b.probability == 0.0
        assert b.time_horizon == ""

    def test_benefit_with_values(self) -> None:
        b = RecommendationBenefit(
            benefit_type=BenefitType.EFFICIENCY_GAIN,
            description="15% improvement in throughput",
            estimated_value=100000.0,
            probability=0.85,
            time_horizon="medium",
        )
        assert b.benefit_type == BenefitType.EFFICIENCY_GAIN
        assert b.estimated_value == 100000.0
        assert b.probability == 0.85
        assert b.time_horizon == "medium"

    def test_benefit_probability_bounds(self) -> None:
        with pytest.raises(ValidationError):
            RecommendationBenefit(probability=-0.1)
        with pytest.raises(ValidationError):
            RecommendationBenefit(probability=1.1)


# ═══════════════════════════════════════════════════════════════════════
# RecommendationRisk
# ═══════════════════════════════════════════════════════════════════════


class TestRecommendationRisk:
    def test_default_risk(self) -> None:
        r = RecommendationRisk()
        assert r.risk_id is not None
        assert r.description == ""
        assert r.probability == 0.0
        assert r.impact_severity == 0.0
        assert r.risk_score == 0.0
        assert r.mitigation == ""
        assert r.category == ""

    def test_risk_with_values(self) -> None:
        r = RecommendationRisk(
            description="Supply chain disruption",
            probability=0.3,
            impact_severity=0.8,
            risk_score=0.6,
            mitigation="Maintain safety stock of critical components",
            category="operational",
        )
        assert r.description == "Supply chain disruption"
        assert r.probability == 0.3
        assert r.impact_severity == 0.8
        assert r.risk_score == 0.6
        assert r.category == "operational"

    def test_risk_probability_bounds(self) -> None:
        with pytest.raises(ValidationError):
            RecommendationRisk(probability=-0.1)
        with pytest.raises(ValidationError):
            RecommendationRisk(probability=1.1)

    def test_risk_impact_severity_bounds(self) -> None:
        with pytest.raises(ValidationError):
            RecommendationRisk(impact_severity=-0.1)
        with pytest.raises(ValidationError):
            RecommendationRisk(impact_severity=1.1)

    def test_risk_score_bounds(self) -> None:
        with pytest.raises(ValidationError):
            RecommendationRisk(risk_score=-0.1)
        with pytest.raises(ValidationError):
            RecommendationRisk(risk_score=1.1)


# ═══════════════════════════════════════════════════════════════════════
# RecommendationPolicy
# ═══════════════════════════════════════════════════════════════════════


class TestRecommendationPolicy:
    def test_default_policy(self) -> None:
        p = RecommendationPolicy()
        assert p.policy_id is not None
        assert p.name == ""
        assert p.description == ""
        assert p.allowed_domains == []
        assert p.allowed_strategies == []
        assert p.max_candidates == 10
        assert p.min_confidence == 0.0
        assert p.is_active is True

    def test_policy_with_values(self) -> None:
        p = RecommendationPolicy(
            name="Energy Policy",
            description="Policy for energy-related recommendations",
            allowed_domains=[RecommendationDomain.ENERGY, RecommendationDomain.SAFETY],
            allowed_strategies=[RecommendationStrategy.COST_OPTIMIZATION],
            max_candidates=5,
            min_confidence=0.7,
            is_active=True,
        )
        assert p.name == "Energy Policy"
        assert len(p.allowed_domains) == 2
        assert len(p.allowed_strategies) == 1
        assert p.max_candidates == 5
        assert p.min_confidence == 0.7

    def test_policy_max_candidates_positive(self) -> None:
        with pytest.raises(ValidationError):
            RecommendationPolicy(max_candidates=0)

    def test_policy_min_confidence_bounds(self) -> None:
        with pytest.raises(ValidationError):
            RecommendationPolicy(min_confidence=-0.1)
        with pytest.raises(ValidationError):
            RecommendationPolicy(min_confidence=1.1)


# ═══════════════════════════════════════════════════════════════════════
# RecommendationConfidence
# ═══════════════════════════════════════════════════════════════════════


class TestRecommendationConfidence:
    def test_default_confidence(self) -> None:
        c = RecommendationConfidence()
        assert c.overall_confidence == 0.0
        assert c.strategy_confidence == 0.0
        assert c.impact_accuracy == 0.0
        assert c.benefit_reliability == 0.0
        assert c.risk_assessment == 0.0
        assert c.constraint_compliance == 0.0

    def test_confidence_with_values(self) -> None:
        c = RecommendationConfidence(
            overall_confidence=0.85,
            strategy_confidence=0.9,
            impact_accuracy=0.75,
            benefit_reliability=0.8,
            risk_assessment=0.85,
            constraint_compliance=0.95,
        )
        assert c.overall_confidence == 0.85
        assert c.strategy_confidence == 0.9
        assert c.constraint_compliance == 0.95

    def test_confidence_bounds(self) -> None:
        with pytest.raises(ValidationError):
            RecommendationConfidence(overall_confidence=-0.1)
        with pytest.raises(ValidationError):
            RecommendationConfidence(overall_confidence=1.1)
        with pytest.raises(ValidationError):
            RecommendationConfidence(strategy_confidence=-0.1)
        with pytest.raises(ValidationError):
            RecommendationConfidence(strategy_confidence=1.1)
        with pytest.raises(ValidationError):
            RecommendationConfidence(impact_accuracy=-0.1)
        with pytest.raises(ValidationError):
            RecommendationConfidence(impact_accuracy=1.1)
        with pytest.raises(ValidationError):
            RecommendationConfidence(benefit_reliability=-0.1)
        with pytest.raises(ValidationError):
            RecommendationConfidence(benefit_reliability=1.1)
        with pytest.raises(ValidationError):
            RecommendationConfidence(risk_assessment=-0.1)
        with pytest.raises(ValidationError):
            RecommendationConfidence(risk_assessment=1.1)
        with pytest.raises(ValidationError):
            RecommendationConfidence(constraint_compliance=-0.1)
        with pytest.raises(ValidationError):
            RecommendationConfidence(constraint_compliance=1.1)


# ═══════════════════════════════════════════════════════════════════════
# RecommendationMetadata
# ═══════════════════════════════════════════════════════════════════════


class TestRecommendationMetadata:
    def test_default_metadata(self) -> None:
        m = RecommendationMetadata()
        assert m.title == ""
        assert m.tags == []
        assert m.version == "1.0.0"

    def test_metadata_with_values(self) -> None:
        m = RecommendationMetadata(
            title="Energy Analysis Recommendation",
            description="Recommendations from energy efficiency analysis",
            tags=["energy", "optimization"],
            category="analysis",
            source="energy-service",
        )
        assert m.title == "Energy Analysis Recommendation"
        assert len(m.tags) == 2
        assert m.source == "energy-service"


# ═══════════════════════════════════════════════════════════════════════
# RecommendationHealth
# ═══════════════════════════════════════════════════════════════════════


class TestRecommendationHealth:
    def test_default_health(self) -> None:
        h = RecommendationHealth()
        assert h.overall_status == "UNKNOWN"
        assert h.recommendation_count == 0
        assert h.error_count == 0
        assert h.uptime_seconds >= 0.0

    def test_health_with_values(self) -> None:
        h = RecommendationHealth(
            overall_status="HEALTHY",
            recommendation_count=10,
            coordinator_status="HEALTHY",
            generator_status="HEALTHY",
            ranker_status="DEGRADED",
        )
        assert h.overall_status == "HEALTHY"
        assert h.ranker_status == "DEGRADED"

    def test_health_counts_non_negative(self) -> None:
        with pytest.raises(ValidationError):
            RecommendationHealth(error_count=-1)
        with pytest.raises(ValidationError):
            RecommendationHealth(recommendation_count=-1)


# ═══════════════════════════════════════════════════════════════════════
# RecommendationMetrics
# ═══════════════════════════════════════════════════════════════════════


class TestRecommendationMetrics:
    def test_default_metrics(self) -> None:
        m = RecommendationMetrics()
        assert m.recommendation_total == 0
        assert m.candidates_total == 0
        assert m.decisions_total == 0
        assert m.packages_total == 0
        assert m.validated_total == 0
        assert m.failed_total == 0

    def test_metrics_with_values(self) -> None:
        m = RecommendationMetrics(
            recommendation_total=10,
            candidates_total=25,
            decisions_total=8,
            packages_total=5,
            validated_total=20,
            failed_total=2,
            candidates_per_domain={"ENERGY": 15},
        )
        assert m.candidates_total == 25
        assert m.candidates_per_domain["ENERGY"] == 15

    def test_metrics_non_negative(self) -> None:
        with pytest.raises(ValidationError):
            RecommendationMetrics(recommendation_total=-1)
        with pytest.raises(ValidationError):
            RecommendationMetrics(candidates_total=-1)
        with pytest.raises(ValidationError):
            RecommendationMetrics(decisions_total=-1)


# ═══════════════════════════════════════════════════════════════════════
# RecommendationSession
# ═══════════════════════════════════════════════════════════════════════


class TestRecommendationSession:
    def test_default_session(self) -> None:
        rid = uuid.uuid4()
        s = RecommendationSession(request_id=rid)
        assert s.request_id == rid
        assert s.domain == RecommendationDomain.GENERAL
        assert s.status == RecommendationStatus.INITIALIZED
        assert s.completed_at is None

    def test_session_with_values(self) -> None:
        rid = uuid.uuid4()
        now = datetime.now(UTC)
        s = RecommendationSession(
            request_id=rid,
            domain=RecommendationDomain.ENERGY,
            status=RecommendationStatus.COMPLETED,
            completed_at=now,
            statistics={"duration_ms": 150},
        )
        assert s.status == RecommendationStatus.COMPLETED
        assert s.completed_at == now
        assert s.statistics["duration_ms"] == 150

    def test_session_requires_request_id(self) -> None:
        with pytest.raises(ValidationError):
            RecommendationSession()


# ═══════════════════════════════════════════════════════════════════════
# RecommendationExplainabilityMetadata
# ═══════════════════════════════════════════════════════════════════════


class TestRecommendationExplainabilityMetadata:
    def test_default_explainability(self) -> None:
        e = RecommendationExplainabilityMetadata()
        assert e.why_candidate_selected == ""
        assert e.why_candidate_rejected == ""
        assert e.why_strategy_chosen == ""
        assert e.why_priority_assigned == ""
        assert e.why_policy_applied == ""
        assert e.why_confidence_calculated == ""

    def test_explainability_with_values(self) -> None:
        e = RecommendationExplainabilityMetadata(
            why_candidate_selected="Highest confidence score",
            why_candidate_rejected="Low ROI",
            why_strategy_chosen="Best fit for domain",
            why_priority_assigned="Safety critical",
            why_policy_applied="Energy domain requires policy check",
            why_confidence_calculated="Multiple dimensions evaluated",
        )
        assert e.why_candidate_selected == "Highest confidence score"
        assert e.why_priority_assigned == "Safety critical"
        assert e.why_policy_applied == "Energy domain requires policy check"


# ═══════════════════════════════════════════════════════════════════════
# RecommendationTrace
# ═══════════════════════════════════════════════════════════════════════


class TestRecommendationTrace:
    def test_default_trace(self) -> None:
        t = RecommendationTrace()
        assert t.stage_name == ""
        assert t.success is True
        assert t.warnings == []
        assert t.errors == []
        assert t.duration_ms is None

    def test_trace_with_values(self) -> None:
        now = datetime.now(UTC)
        t = RecommendationTrace(
            stage_name="GENERATION",
            operation="generate",
            recommendation_id="rec-1",
            correlation_id="corr-1",
            started_at=now,
            completed_at=now,
            duration_ms=42.5,
            success=True,
        )
        assert t.stage_name == "GENERATION"
        assert t.duration_ms == 42.5
        assert t.success is True

    def test_trace_with_warnings(self) -> None:
        t = RecommendationTrace(
            stage_name="VALIDATION",
            operation="validate",
            recommendation_id="r-1",
            success=False,
            warnings=["Missing context data"],
            errors=["Validation failed"],
        )
        assert len(t.warnings) == 1
        assert len(t.errors) == 1


# ═══════════════════════════════════════════════════════════════════════
# DTOs
# ═══════════════════════════════════════════════════════════════════════


class TestRecommendationRequestDTO:
    def test_default_request_dto(self) -> None:
        rid = uuid.uuid4()
        dto = RecommendationRequestDTO(reasoning_result_id=str(rid))
        assert dto.reasoning_result_id == str(rid)
        assert dto.domain == RecommendationDomain.GENERAL
        assert dto.strategy == RecommendationStrategy.NEXT_BEST_ACTION

    def test_request_dto_with_values(self) -> None:
        rid = uuid.uuid4()
        dto = RecommendationRequestDTO(
            reasoning_result_id=str(rid),
            domain=RecommendationDomain.ENERGY,
            strategy=RecommendationStrategy.RISK_MITIGATION,
            context={"priority": "high"},
        )
        assert dto.domain == RecommendationDomain.ENERGY
        assert dto.context["priority"] == "high"

    def test_request_dto_requires_reasoning_result_id(self) -> None:
        with pytest.raises(ValidationError):
            RecommendationRequestDTO()


class TestRecommendationResponseDTO:
    def test_default_response_dto(self) -> None:
        rid = uuid.uuid4()
        req_id = uuid.uuid4()
        dto = RecommendationResponseDTO(result_id=rid, request_id=req_id)
        assert dto.result_id == rid
        assert dto.request_id == req_id
        assert dto.candidates_count == 0
        assert dto.status == RecommendationStatus.COMPLETED

    def test_response_dto_with_values(self) -> None:
        rid = uuid.uuid4()
        req_id = uuid.uuid4()
        dto = RecommendationResponseDTO(
            result_id=rid,
            request_id=req_id,
            candidates_count=5,
            packages_count=2,
            confidence=0.85,
            status=RecommendationStatus.COMPLETED,
            decision={"conclusion": "Proceed with action"},
        )
        assert dto.candidates_count == 5
        assert dto.confidence == 0.85
        assert dto.decision["conclusion"] == "Proceed with action"

    def test_response_dto_requires_ids(self) -> None:
        with pytest.raises(ValidationError):
            RecommendationResponseDTO()
        with pytest.raises(ValidationError):
            RecommendationResponseDTO(result_id=uuid.uuid4())
        with pytest.raises(ValidationError):
            RecommendationResponseDTO(request_id=uuid.uuid4())


class TestRecommendationPackageDTO:
    def test_default_package_dto(self) -> None:
        dto = RecommendationPackageDTO()
        assert dto.package_id is not None
        assert dto.primary_candidate_id == ""
        assert dto.alternate_candidate_ids == []
        assert dto.overall_confidence == 0.0
        assert dto.summary == ""

    def test_package_dto_with_values(self) -> None:
        dto = RecommendationPackageDTO(
            primary_candidate_id="candidate-1",
            alternate_candidate_ids=["candidate-2", "candidate-3"],
            overall_confidence=0.85,
            summary="Recommended maintenance package",
        )
        assert dto.primary_candidate_id == "candidate-1"
        assert len(dto.alternate_candidate_ids) == 2
        assert dto.overall_confidence == 0.85
        assert dto.summary == "Recommended maintenance package"


# ═══════════════════════════════════════════════════════════════════════
# Events
# ═══════════════════════════════════════════════════════════════════════


class TestRecommendationEvent:
    def test_base_event(self) -> None:
        e = RecommendationEvent(event_type="test.event")
        assert e.event_type == "test.event"
        assert e.recommendation_id == ""
        assert e.correlation_id == ""

    def test_recommendation_requested(self) -> None:
        e = RecommendationRequested(
            recommendation_id="r-1",
            correlation_id="corr-1",
            domain="ENERGY",
            strategy="RISK_MITIGATION",
            goals=["REDUCE_COST"],
        )
        assert e.event_type == "recommendation.requested"
        assert e.domain == "ENERGY"
        assert e.strategy == "RISK_MITIGATION"
        assert len(e.goals) == 1

    def test_recommendation_generated(self) -> None:
        e = RecommendationGenerated(
            recommendation_id="r-1",
            candidate_count=5,
            primary_candidate_id="c-1",
        )
        assert e.event_type == "recommendation.generated"
        assert e.candidate_count == 5
        assert e.primary_candidate_id == "c-1"

    def test_recommendation_ranked(self) -> None:
        e = RecommendationRanked(
            recommendation_id="r-1",
            ranked_candidate_ids=["c-1", "c-2", "c-3"],
            best_candidate_id="c-1",
        )
        assert e.event_type == "recommendation.ranked"
        assert len(e.ranked_candidate_ids) == 3
        assert e.best_candidate_id == "c-1"

    def test_recommendation_validated(self) -> None:
        e = RecommendationValidated(
            recommendation_id="r-1",
            validator="policy-engine",
            passed=True,
            violations=[],
        )
        assert e.event_type == "recommendation.validated"
        assert e.validator == "policy-engine"
        assert e.passed is True

    def test_recommendation_completed(self) -> None:
        e = RecommendationCompleted(
            recommendation_id="r-1",
            status="COMPLETED",
            result_id="res-1",
            duration_ms=150.5,
        )
        assert e.event_type == "recommendation.completed"
        assert e.status == "COMPLETED"
        assert e.duration_ms == 150.5
        assert e.result_id == "res-1"

    def test_event_inheritance(self) -> None:
        e = RecommendationRequested(recommendation_id="r-1")
        assert isinstance(e, RecommendationEvent)
        assert e.timestamp is not None

    def test_generated_candidate_count_non_negative(self) -> None:
        with pytest.raises(ValidationError):
            RecommendationGenerated(candidate_count=-1)

    def test_completed_duration_non_negative(self) -> None:
        with pytest.raises(ValidationError):
            RecommendationCompleted(duration_ms=-1.0)


# ═══════════════════════════════════════════════════════════════════════
# Exceptions
# ═══════════════════════════════════════════════════════════════════════


class TestRecommendationException:
    def test_base_exception(self) -> None:
        e = RecommendationException("base error")
        assert str(e) == "base error"
        assert isinstance(e, Exception)

    def test_validation_exception(self) -> None:
        e = RecommendationValidationException("validation error")
        assert str(e) == "validation error"
        assert isinstance(e, RecommendationException)

    def test_ranking_exception(self) -> None:
        e = RecommendationRankingException("ranking error")
        assert str(e) == "ranking error"
        assert isinstance(e, RecommendationException)

    def test_policy_exception(self) -> None:
        e = RecommendationPolicyException("policy error")
        assert str(e) == "policy error"
        assert isinstance(e, RecommendationException)

    def test_default_messages(self) -> None:
        assert "recommendation error" in str(RecommendationException())
        assert "recommendation validation error" in str(RecommendationValidationException())
        assert "recommendation ranking error" in str(RecommendationRankingException())
        assert "recommendation policy error" in str(RecommendationPolicyException())

    def test_exception_hierarchy(self) -> None:
        assert issubclass(RecommendationValidationException, RecommendationException)
        assert issubclass(RecommendationRankingException, RecommendationException)
        assert issubclass(RecommendationPolicyException, RecommendationException)


# ═══════════════════════════════════════════════════════════════════════
# Model Relationships
# ═══════════════════════════════════════════════════════════════════════


class TestModelRelationships:
    def test_candidate_in_package(self) -> None:
        rid = uuid.uuid4()
        candidate = RecommendationCandidate(
            description="Replace equipment",
            confidence=0.8,
        )
        pkg = RecommendationPackage(
            result_id=rid,
            primary_candidate=candidate,
        )
        assert pkg.primary_candidate is not None
        assert pkg.primary_candidate.confidence == 0.8

    def test_package_in_decision(self) -> None:
        rid = uuid.uuid4()
        candidate = RecommendationCandidate(description="Primary action")
        pkg = RecommendationPackage(
            result_id=rid,
            primary_candidate=candidate,
        )
        decision = RecommendationDecision(
            result_id=rid,
            conclusion="Approved",
            package=pkg,
        )
        assert decision.package is not None
        assert decision.package.primary_candidate is not None
        assert decision.package.primary_candidate.description == "Primary action"

    def test_benefits_and_risks_in_candidate(self) -> None:
        benefit = RecommendationBenefit(
            description="Cost reduction",
            benefit_type=BenefitType.COST_SAVING,
            probability=0.8,
        )
        risk = RecommendationRisk(
            description="Implementation delay",
            probability=0.3,
            risk_score=0.5,
        )
        candidate = RecommendationCandidate(
            description="Upgrade system",
            expected_benefits=[benefit],
            expected_risks=[risk],
        )
        assert len(candidate.expected_benefits) == 1
        assert len(candidate.expected_risks) == 1
        assert candidate.expected_benefits[0].benefit_type == BenefitType.COST_SAVING
        assert candidate.expected_risks[0].risk_score == 0.5

    def test_decision_in_result(self) -> None:
        rid = uuid.uuid4()
        decision = RecommendationDecision(
            result_id=rid,
            conclusion="Proceed with maintenance",
            reasoning_summary="Risk assessment supports action",
        )
        result = RecommendationResult(
            request_id=rid,
            decision=decision,
            status=RecommendationStatus.COMPLETED,
        )
        assert result.decision is not None
        assert result.decision.conclusion == "Proceed with maintenance"
        assert result.decision.reasoning_summary == "Risk assessment supports action"

    def test_candidates_in_result(self) -> None:
        rid = uuid.uuid4()
        c1 = RecommendationCandidate(description="Option A", confidence=0.8)
        c2 = RecommendationCandidate(description="Option B", confidence=0.6)
        result = RecommendationResult(
            request_id=rid,
            candidates=[c1, c2],
        )
        assert len(result.candidates) == 2
        assert result.candidates[0].confidence == 0.8
        assert result.candidates[1].description == "Option B"

    def test_dto_to_model_flow(self) -> None:
        rid = uuid.uuid4()
        dto = RecommendationRequestDTO(
            reasoning_result_id=str(rid),
            domain=RecommendationDomain.ENERGY,
            strategy=RecommendationStrategy.RISK_MITIGATION,
        )
        req = RecommendationRequest(
            reasoning_result_id=uuid.UUID(dto.reasoning_result_id),
            domain=dto.domain,
            strategy=dto.strategy,
        )
        assert req.reasoning_result_id == rid
        assert req.domain == RecommendationDomain.ENERGY
        assert req.strategy == RecommendationStrategy.RISK_MITIGATION

    def test_confidence_in_result(self) -> None:
        rid = uuid.uuid4()
        confidence = RecommendationConfidence(
            overall_confidence=0.85,
            strategy_confidence=0.9,
        )
        result = RecommendationResult(
            request_id=rid,
            confidence=confidence,
        )
        assert result.confidence is not None
        assert result.confidence.overall_confidence == 0.85
        assert result.confidence.strategy_confidence == 0.9


# ═══════════════════════════════════════════════════════════════════════
# Cross-Module Validation
# ═══════════════════════════════════════════════════════════════════════


class TestPydanticValidation:
    def test_invalid_enum_value(self) -> None:
        with pytest.raises(ValidationError):
            RecommendationRequest(domain="INVALID_DOMAIN")

    def test_invalid_confidence_type(self) -> None:
        with pytest.raises(ValidationError):
            RecommendationConfidence(overall_confidence="high")

    def test_invalid_priority_type(self) -> None:
        with pytest.raises(ValidationError):
            RecommendationCandidate(priority="URGENT")

    def test_negative_score(self) -> None:
        with pytest.raises(ValidationError):
            RecommendationCandidate(score=-0.5)

    def test_excessive_score(self) -> None:
        with pytest.raises(ValidationError):
            RecommendationCandidate(score=1.5)

    def test_invalid_constraint_type(self) -> None:
        with pytest.raises(ValidationError):
            RecommendationConstraint(constraint_type="FLEXIBLE")

    def test_invalid_benefit_type(self) -> None:
        with pytest.raises(ValidationError):
            RecommendationBenefit(benefit_type="TAX_SAVING")

    def test_invalid_domain(self) -> None:
        with pytest.raises(ValidationError):
            RecommendationCandidate(domain="FINANCE")


class TestContextValidation:
    def test_context_with_all_fields(self) -> None:
        c = RecommendationContext(
            asset_id="a-1",
            machine_id="m-1",
            facility_id="f-1",
            customer_id="c-1",
            workflow_id="w-1",
            incident_id="i-1",
            planner_goal="optimize",
        )
        assert c.asset_id == "a-1"
        assert c.customer_id == "c-1"
        assert c.planner_goal == "optimize"


class TestDomainValidation:
    def test_recommendation_domain_consistency(self) -> None:
        domains = [
            RecommendationDomain.SYSTEM,
            RecommendationDomain.ENERGY,
            RecommendationDomain.MAINTENANCE,
            RecommendationDomain.OPERATIONS,
            RecommendationDomain.CUSTOMER,
            RecommendationDomain.SAFETY,
            RecommendationDomain.COMPLIANCE,
            RecommendationDomain.WORKFLOW,
            RecommendationDomain.PLANNING,
            RecommendationDomain.GENERAL,
        ]
        assert len(domains) == 10


class TestStrategyValidation:
    def test_strategy_consistency(self) -> None:
        strategies = [
            RecommendationStrategy.NEXT_BEST_ACTION,
            RecommendationStrategy.RISK_MITIGATION,
            RecommendationStrategy.PREVENTIVE_MAINTENANCE,
            RecommendationStrategy.COST_OPTIMIZATION,
            RecommendationStrategy.ENERGY_OPTIMIZATION,
            RecommendationStrategy.SLA_RECOVERY,
            RecommendationStrategy.HYBRID_RECOMMENDATION,
        ]
        assert len(strategies) == 7


class TestGoalValidation:
    def test_goal_consistency(self) -> None:
        goals = [
            RecommendationGoal.REDUCE_DOWNTIME,
            RecommendationGoal.REDUCE_COST,
            RecommendationGoal.INCREASE_SAFETY,
            RecommendationGoal.REDUCE_ENERGY_CONSUMPTION,
            RecommendationGoal.MEET_SLA,
            RecommendationGoal.IMPROVE_CUSTOMER_SATISFACTION,
            RecommendationGoal.INCREASE_ASSET_RELIABILITY,
        ]
        assert len(goals) == 7


class TestPriorityValidation:
    def test_priority_consistency(self) -> None:
        priorities = [
            RecommendationPriority.CRITICAL,
            RecommendationPriority.HIGH,
            RecommendationPriority.MEDIUM,
            RecommendationPriority.LOW,
            RecommendationPriority.OPTIONAL,
        ]
        assert len(priorities) == 5


class TestConstraintValidation:
    def test_constraint_type_consistency(self) -> None:
        types = [
            ConstraintType.HARD,
            ConstraintType.SOFT,
            ConstraintType.BUDGET,
            ConstraintType.TIME,
        ]
        assert len(types) == 4

    def test_constraint_with_value_and_unit(self) -> None:
        c = RecommendationConstraint(
            constraint_type=ConstraintType.TIME,
            name="Completion deadline",
            value=7.0,
            unit="days",
        )
        assert c.constraint_type == ConstraintType.TIME
        assert c.value == 7.0
        assert c.unit == "days"


class TestBenefitValidation:
    def test_benefit_type_consistency(self) -> None:
        types = [
            BenefitType.COST_SAVING,
            BenefitType.EFFICIENCY_GAIN,
            BenefitType.SAFETY_IMPROVEMENT,
            BenefitType.RISK_REDUCTION,
            BenefitType.RELIABILITY_IMPROVEMENT,
        ]
        assert len(types) == 5


class TestPolicyValidation:
    def test_policy_with_domains(self) -> None:
        p = RecommendationPolicy(
            name="Safety Policy",
            allowed_domains=[RecommendationDomain.SAFETY, RecommendationDomain.COMPLIANCE],
            max_candidates=3,
            min_confidence=0.8,
        )
        assert RecommendationDomain.SAFETY in p.allowed_domains
        assert p.min_confidence == 0.8

    def test_policy_inactive(self) -> None:
        p = RecommendationPolicy(
            name="Inactive Policy",
            is_active=False,
        )
        assert p.is_active is False


class TestTraceValidation:
    def test_trace_stage_timing(self) -> None:
        start = datetime.now(UTC)
        end = datetime.now(UTC)
        t = RecommendationTrace(
            stage_name="RANKING",
            operation="rank",
            recommendation_id="r-1",
            started_at=start,
            completed_at=end,
            duration_ms=25.0,
        )
        assert t.started_at == start
        assert t.completed_at == end
        assert t.duration_ms == 25.0
