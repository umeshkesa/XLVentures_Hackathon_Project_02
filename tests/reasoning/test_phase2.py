"""Phase 2 tests for the Reasoning Engine (Execution Pipeline).

Tests all 15 execution components: ContextBuilder, ReasoningGoalManager,
ConstraintManager, AssumptionManager, StrategySelector, HypothesisGenerator,
InferenceEngine, ContradictionDetector, ReasoningGraphBuilder,
DecisionAlternatives, WeightManager, ReasoningScoreCalculator, PolicyEngine,
ReasoningTrace, and ReasoningMetricsCollector. Also tests execution-layer
models and enums introduced in Phase 2.

Approximately 170+ tests covering creation, modification, edge cases
(empty lists, zero values, missing IDs), and field-level verification.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from adip.reasoning.contracts.models import (
    Hypothesis,
    HypothesisSet,
    Inference,
    InferenceChain,
    ReasoningContext,
)
from adip.reasoning.enums import (
    AlternativeStatus,
    AssumptionStatus,
    ConstraintType,
    ContradictionResolutionStatus,
    ContradictionSeverity,
    HypothesisStatus,
    PolicyType,
    ReasoningDomain,
    ReasoningGoalType,
    ReasoningStrategyType,
)
from adip.reasoning.execution.assumption_manager import AssumptionManager
from adip.reasoning.execution.constraint_manager import ConstraintManager
from adip.reasoning.execution.context_builder import ContextBuilder
from adip.reasoning.execution.contradiction_detector import ContradictionDetector
from adip.reasoning.execution.decision_alternatives import DecisionAlternatives
from adip.reasoning.execution.goal_manager import ReasoningGoalManager
from adip.reasoning.execution.hypothesis_generator import HypothesisGenerator
from adip.reasoning.execution.inference_engine import InferenceEngine
from adip.reasoning.execution.metrics import ReasoningMetricsCollector
from adip.reasoning.execution.models import (
    Assumption,
    Constraint,
    GoalConfig,
    PolicyDecision,
    ReasoningAlternative,
    ReasoningGoal,
    ReasoningGraph,
    ReasoningGraphEdge,
    ReasoningGraphNode,
    ReasoningMetrics,
    ReasoningScore,
    TraceRecord,
)
from adip.reasoning.execution.policy_engine import PolicyEngine
from adip.reasoning.execution.reasoning_graph import ReasoningGraphBuilder
from adip.reasoning.execution.reasoning_score import ReasoningScoreCalculator
from adip.reasoning.execution.strategy_selector import StrategySelector
from adip.reasoning.execution.trace import ReasoningTrace
from adip.reasoning.execution.weight_manager import WeightManager

# ═══════════════════════════════════════════════════════════════════════════
# Execution Models Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestReasoningGoalModel:
    def test_create_default(self) -> None:
        goal = ReasoningGoal(goal_type=ReasoningGoalType.ROOT_CAUSE_ANALYSIS)
        assert isinstance(goal.goal_id, uuid.UUID)
        assert goal.goal_type == ReasoningGoalType.ROOT_CAUSE_ANALYSIS
        assert goal.description == ""
        assert goal.priority == 5
        assert goal.is_primary is True
        assert goal.parameters == {}
        assert goal.metadata == {}

    def test_create_with_all_fields(self) -> None:
        gid = uuid.uuid4()
        goal = ReasoningGoal(
            goal_id=gid,
            goal_type=ReasoningGoalType.RISK_ASSESSMENT,
            description="Test goal",
            priority=9,
            is_primary=False,
            parameters={"key": "val"},
            metadata={"source": "test"},
        )
        assert goal.goal_id == gid
        assert goal.priority == 9
        assert goal.is_primary is False
        assert goal.parameters == {"key": "val"}

    def test_priority_bounds(self) -> None:
        with pytest.raises(ValidationError):
            ReasoningGoal(goal_type=ReasoningGoalType.RISK_ASSESSMENT, priority=11)
        with pytest.raises(ValidationError):
            ReasoningGoal(goal_type=ReasoningGoalType.RISK_ASSESSMENT, priority=-1)


class TestConstraintModel:
    def test_create_default(self) -> None:
        c = Constraint(constraint_type=ConstraintType.BUDGET)
        assert isinstance(c.constraint_id, uuid.UUID)
        assert c.constraint_type == ConstraintType.BUDGET
        assert c.description == ""
        assert c.value == 0.0
        assert c.unit == ""
        assert c.is_hard is True
        assert c.is_active is True

    def test_create_with_all_fields(self) -> None:
        cid = uuid.uuid4()
        c = Constraint(
            constraint_id=cid,
            constraint_type=ConstraintType.TIME,
            description="Time limit",
            value=100.0,
            unit="hours",
            is_hard=False,
            is_active=False,
        )
        assert c.constraint_id == cid
        assert c.value == 100.0
        assert c.unit == "hours"
        assert c.is_hard is False
        assert c.is_active is False


class TestAssumptionModel:
    def test_create_default(self) -> None:
        a = Assumption(description="test assumption")
        assert isinstance(a.assumption_id, uuid.UUID)
        assert a.description == "test assumption"
        assert a.status == AssumptionStatus.ACTIVE
        assert a.source == ""
        assert a.validated_at is None
        assert a.invalidated_at is None

    def test_create_with_all_fields(self) -> None:
        aid = uuid.uuid4()
        now = datetime.now(UTC)
        a = Assumption(
            assumption_id=aid,
            description="assumption",
            source="user",
            status=AssumptionStatus.VALIDATED,
            validated_at=now,
        )
        assert a.assumption_id == aid
        assert a.source == "user"
        assert a.status == AssumptionStatus.VALIDATED
        assert a.validated_at == now


class TestReasoningAlternativeModel:
    def test_create_default(self) -> None:
        alt = ReasoningAlternative(decision_description="alt1")
        assert isinstance(alt.alternative_id, uuid.UUID)
        assert alt.decision_description == "alt1"
        assert alt.confidence == 0.0
        assert alt.reasoning == []
        assert alt.supporting_evidence == []
        assert alt.status == AlternativeStatus.CANDIDATE
        assert alt.score == 0.0

    def test_create_with_all_fields(self) -> None:
        aid = uuid.uuid4()
        alt = ReasoningAlternative(
            alternative_id=aid,
            decision_description="best",
            confidence=0.9,
            reasoning=["step1"],
            supporting_evidence=["ev1"],
            status=AlternativeStatus.SELECTED,
            score=0.85,
        )
        assert alt.alternative_id == aid
        assert alt.confidence == 0.9
        assert alt.status == AlternativeStatus.SELECTED
        assert alt.score == 0.85

    def test_confidence_bounds(self) -> None:
        with pytest.raises(ValidationError):
            ReasoningAlternative(decision_description="x", confidence=1.5)
        with pytest.raises(ValidationError):
            ReasoningAlternative(decision_description="x", confidence=-0.1)
        with pytest.raises(ValidationError):
            ReasoningAlternative(decision_description="x", score=1.5)
        with pytest.raises(ValidationError):
            ReasoningAlternative(decision_description="x", score=-0.1)


class TestReasoningScoreModel:
    def test_create_default(self) -> None:
        s = ReasoningScore()
        assert s.consistency == 0.0
        assert s.coverage == 0.0
        assert s.completeness == 0.0
        assert s.rule_satisfaction == 0.0
        assert s.assumption_quality == 0.0
        assert s.overall == 0.0

    def test_create_with_values(self) -> None:
        s = ReasoningScore(
            consistency=0.9,
            coverage=0.8,
            completeness=0.7,
            rule_satisfaction=1.0,
            assumption_quality=0.6,
            overall=0.8,
        )
        assert s.consistency == 0.9
        assert s.overall == 0.8

    def test_bounds(self) -> None:
        with pytest.raises(ValidationError):
            ReasoningScore(consistency=1.5)
        with pytest.raises(ValidationError):
            ReasoningScore(consistency=-0.1)


class TestPolicyDecisionModel:
    def test_create_default(self) -> None:
        d = PolicyDecision()
        assert d.policy_type == PolicyType.BALANCED
        assert d.allowed is True
        assert d.reasoning == []
        assert d.confidence == 1.0

    def test_create_denied(self) -> None:
        d = PolicyDecision(
            policy_type=PolicyType.STRICT,
            allowed=False,
            reasoning=["not allowed"],
            confidence=0.5,
        )
        assert d.policy_type == PolicyType.STRICT
        assert d.allowed is False
        assert d.confidence == 0.5


class TestReasoningGraphModels:
    def test_node_default(self) -> None:
        n = ReasoningGraphNode(node_type="evidence", label="ev1")
        assert isinstance(n.node_id, uuid.UUID)
        assert n.node_type == "evidence"
        assert n.label == "ev1"
        assert n.data == {}

    def test_edge_default(self) -> None:
        sid, tid = uuid.uuid4(), uuid.uuid4()
        e = ReasoningGraphEdge(source_id=sid, target_id=tid, edge_type="supports")
        assert isinstance(e.edge_id, uuid.UUID)
        assert e.source_id == sid
        assert e.target_id == tid
        assert e.weight == 1.0

    def test_graph_default(self) -> None:
        g = ReasoningGraph()
        assert isinstance(g.graph_id, uuid.UUID)
        assert g.nodes == []
        assert g.edges == []
        assert g.decision_paths == []
        assert g.alternative_paths == []

    def test_graph_with_data(self) -> None:
        n1 = ReasoningGraphNode(node_type="hypothesis", label="h1")
        n2 = ReasoningGraphNode(node_type="decision", label="d1")
        e = ReasoningGraphEdge(
            source_id=n1.node_id, target_id=n2.node_id, edge_type="leads_to", weight=0.8
        )
        g = ReasoningGraph(
            nodes=[n1, n2],
            edges=[e],
            decision_paths=[[n1.node_id, n2.node_id]],
        )
        assert len(g.nodes) == 2
        assert len(g.edges) == 1
        assert len(g.decision_paths) == 1


class TestGoalConfigModel:
    def test_create_default(self) -> None:
        gc = GoalConfig(goal_type=ReasoningGoalType.ROOT_CAUSE_ANALYSIS)
        assert gc.goal_type == ReasoningGoalType.ROOT_CAUSE_ANALYSIS
        assert gc.parameters == {}
        assert gc.priority == 5

    def test_create_with_params(self) -> None:
        gc = GoalConfig(
            goal_type=ReasoningGoalType.NEXT_BEST_ACTION,
            parameters={"count": 3},
            priority=8,
        )
        assert gc.parameters == {"count": 3}
        assert gc.priority == 8


class TestTraceRecordModel:
    def test_create_default(self) -> None:
        tr = TraceRecord()
        assert tr.trace_id == ""
        assert tr.stage_name == ""
        assert tr.operation == ""
        assert tr.reasoning_id == ""
        assert tr.success is True
        assert tr.warnings == []
        assert tr.errors == []

    def test_create_with_fields(self) -> None:
        tr = TraceRecord(
            trace_id="t1",
            stage_name="GOAL",
            operation="goal:test",
            reasoning_id="r1",
            correlation_id="c1",
            duration_ms=12.5,
            success=True,
            warnings=["warn"],
            errors=[],
        )
        assert tr.stage_name == "GOAL"
        assert tr.duration_ms == 12.5
        assert tr.warnings == ["warn"]


class TestReasoningMetricsModel:
    def test_create_default(self) -> None:
        rm = ReasoningMetrics()
        assert rm.hypotheses_count == 0
        assert rm.alternatives_count == 0
        assert rm.constraints_count == 0
        assert rm.contradictions_count == 0
        assert rm.goals_count == 0
        assert rm.average_score == 0.0
        assert rm.trace_count == 0

    def test_create_with_values(self) -> None:
        rm = ReasoningMetrics(
            hypotheses_count=5,
            alternatives_count=3,
            constraints_count=10,
            contradictions_count=2,
            goals_count=1,
            average_score=0.75,
            trace_count=20,
        )
        assert rm.hypotheses_count == 5
        assert rm.average_score == 0.75
        assert rm.trace_count == 20

    def test_non_negative_counts(self) -> None:
        with pytest.raises(ValidationError):
            ReasoningMetrics(hypotheses_count=-1)
        with pytest.raises(ValidationError):
            ReasoningMetrics(average_score=-0.1)
        with pytest.raises(ValidationError):
            ReasoningMetrics(average_score=1.5)


# ═══════════════════════════════════════════════════════════════════════════
# ContextBuilder Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestContextBuilder:
    def setup_method(self) -> None:
        self.builder = ContextBuilder()

    def test_build_context_default(self) -> None:
        ctx = self.builder.build_context()
        assert isinstance(ctx, ReasoningContext)
        assert ctx.metadata["evidence_ids"] == []
        assert ctx.metadata["domain"] == "SYSTEM"
        assert ctx.metadata["planner_goal"] == ""

    def test_build_context_with_evidence(self) -> None:
        ctx = self.builder.build_context(
            evidence_ids=["ev1", "ev2"],
            domain=ReasoningDomain.ENERGY,
            planner_goal="optimize",
            workflow_id="wf1",
            rule_ids=["r1"],
            memory_ids=["m1"],
            knowledge_ids=["k1"],
            correlation_id="corr1",
        )
        assert ctx.metadata["evidence_ids"] == ["ev1", "ev2"]
        assert ctx.metadata["domain"] == "ENERGY"
        assert ctx.metadata["planner_goal"] == "optimize"
        assert ctx.metadata["workflow_id"] == "wf1"
        assert ctx.metadata["rule_ids"] == ["r1"]
        assert ctx.metadata["memory_ids"] == ["m1"]
        assert ctx.metadata["knowledge_ids"] == ["k1"]
        assert ctx.metadata["correlation_id"] == "corr1"

    def test_build_context_none_lists(self) -> None:
        ctx = self.builder.build_context(evidence_ids=None, rule_ids=None)
        assert ctx.metadata["evidence_ids"] == []
        assert ctx.metadata["rule_ids"] == []

    def test_build_context_empty_lists(self) -> None:
        ctx = self.builder.build_context(evidence_ids=[], rule_ids=[])
        assert ctx.metadata["evidence_ids"] == []
        assert ctx.metadata["rule_ids"] == []

    def test_build_context_all_domains(self) -> None:
        for domain in ReasoningDomain:
            ctx = self.builder.build_context(domain=domain)
            assert ctx.metadata["domain"] == domain.value

    def test_merge_contexts_single(self) -> None:
        ctx1 = self.builder.build_context(evidence_ids=["ev1"])
        merged = self.builder.merge_contexts([ctx1])
        assert merged.metadata["evidence_ids"] == ["ev1"]
        assert merged.metadata["merged_count"] == 1

    def test_merge_contexts_multiple(self) -> None:
        ctx1 = self.builder.build_context(
            domain=ReasoningDomain.ENERGY, workflow_id="wf1",
        )
        ctx2 = self.builder.build_context(
            domain=ReasoningDomain.SAFETY, rule_ids=["r1"],
        )
        merged = self.builder.merge_contexts([ctx1, ctx2])
        # ctx2 overwrites ctx1 for domain; workflow_id set to empty by ctx2
        assert merged.metadata["domain"] == "SAFETY"
        assert merged.metadata["rule_ids"] == ["r1"]
        assert merged.metadata["merged_count"] == 2

    def test_merge_empty_contexts(self) -> None:
        merged = self.builder.merge_contexts([])
        assert merged.metadata["merged_count"] == 0

    def test_enrich_context(self) -> None:
        ctx = self.builder.build_context(evidence_ids=["ev1"])
        enriched = self.builder.enrich_context(
            ctx,
            {"new_key": "new_val", "domain": "OVERRIDE"},
        )
        assert enriched.metadata["evidence_ids"] == ["ev1"]
        assert enriched.metadata["new_key"] == "new_val"
        assert enriched.metadata["domain"] == "OVERRIDE"
        assert enriched.metadata["enriched"] is True

    def test_enrich_context_empty_data(self) -> None:
        ctx = self.builder.build_context()
        enriched = self.builder.enrich_context(ctx, {})
        assert enriched.metadata["enriched"] is True
        assert enriched.metadata["domain"] == "SYSTEM"


# ═══════════════════════════════════════════════════════════════════════════
# ReasoningGoalManager Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestReasoningGoalManager:
    def setup_method(self) -> None:
        self.manager = ReasoningGoalManager()

    def test_create_goal_default(self) -> None:
        goal = self.manager.create_goal(ReasoningGoalType.ROOT_CAUSE_ANALYSIS)
        assert goal.goal_type == ReasoningGoalType.ROOT_CAUSE_ANALYSIS
        assert goal.description == "Identify root causes of the issue"
        assert goal.priority == 5
        assert goal.is_primary is True

    def test_create_goal_all_types(self) -> None:
        for goal_type in ReasoningGoalType:
            goal = self.manager.create_goal(goal_type)
            assert goal.goal_type == goal_type
            assert isinstance(goal.goal_id, uuid.UUID)

    def test_create_goal_custom_description(self) -> None:
        goal = self.manager.create_goal(
            ReasoningGoalType.NEXT_BEST_ACTION,
            description="Custom desc",
            priority=9,
            is_primary=False,
            parameters={"risk_weight": 0.5},
        )
        assert goal.description == "Custom desc"
        assert goal.priority == 9
        assert goal.is_primary is False
        assert goal.parameters == {"risk_weight": 0.5}

    def test_create_goal_empty_parameters(self) -> None:
        goal = self.manager.create_goal(ReasoningGoalType.RISK_ASSESSMENT, parameters={})
        assert goal.parameters == {}

    def test_create_goal_none_parameters(self) -> None:
        goal = self.manager.create_goal(ReasoningGoalType.RISK_ASSESSMENT, parameters=None)
        assert goal.parameters == {}

    def test_get_goal_found(self) -> None:
        created = self.manager.create_goal(ReasoningGoalType.COMPLIANCE_VERIFICATION)
        retrieved = self.manager.get_goal(str(created.goal_id))
        assert retrieved is not None
        assert retrieved.goal_id == created.goal_id

    def test_get_goal_not_found(self) -> None:
        assert self.manager.get_goal("nonexistent") is None

    def test_get_all_goals_empty(self) -> None:
        assert self.manager.get_all_goals() == []

    def test_get_all_goals_multiple(self) -> None:
        g1 = self.manager.create_goal(ReasoningGoalType.ROOT_CAUSE_ANALYSIS)
        g2 = self.manager.create_goal(ReasoningGoalType.NEXT_BEST_ACTION)
        g3 = self.manager.create_goal(ReasoningGoalType.RISK_ASSESSMENT)
        all_goals = self.manager.get_all_goals()
        assert len(all_goals) == 3
        goal_ids = {str(g.goal_id) for g in all_goals}
        assert str(g1.goal_id) in goal_ids
        assert str(g2.goal_id) in goal_ids
        assert str(g3.goal_id) in goal_ids

    def test_get_primary_goal_when_exists(self) -> None:
        self.manager.create_goal(ReasoningGoalType.ROOT_CAUSE_ANALYSIS, is_primary=True)
        self.manager.create_goal(ReasoningGoalType.NEXT_BEST_ACTION, is_primary=False)
        primary = self.manager.get_primary_goal()
        assert primary is not None
        assert primary.is_primary is True
        assert primary.goal_type == ReasoningGoalType.ROOT_CAUSE_ANALYSIS

    def test_get_primary_goal_none(self) -> None:
        self.manager.create_goal(ReasoningGoalType.NEXT_BEST_ACTION, is_primary=False)
        assert self.manager.get_primary_goal() is None

    def test_get_primary_goal_empty(self) -> None:
        assert self.manager.get_primary_goal() is None

    def test_set_priority(self) -> None:
        goal = self.manager.create_goal(ReasoningGoalType.ROOT_CAUSE_ANALYSIS, priority=5)
        result = self.manager.set_priority(str(goal.goal_id), 8)
        assert result is True
        updated = self.manager.get_goal(str(goal.goal_id))
        assert updated is not None
        assert updated.priority == 8

    def test_set_priority_clamps_upper(self) -> None:
        goal = self.manager.create_goal(ReasoningGoalType.ROOT_CAUSE_ANALYSIS)
        self.manager.set_priority(str(goal.goal_id), 15)
        updated = self.manager.get_goal(str(goal.goal_id))
        assert updated is not None
        assert updated.priority == 10

    def test_set_priority_clamps_lower(self) -> None:
        goal = self.manager.create_goal(ReasoningGoalType.ROOT_CAUSE_ANALYSIS)
        self.manager.set_priority(str(goal.goal_id), -5)
        updated = self.manager.get_goal(str(goal.goal_id))
        assert updated is not None
        assert updated.priority == 0

    def test_set_priority_not_found(self) -> None:
        assert self.manager.set_priority("nonexistent", 8) is False

    def test_clear_goals(self) -> None:
        self.manager.create_goal(ReasoningGoalType.ROOT_CAUSE_ANALYSIS)
        self.manager.create_goal(ReasoningGoalType.NEXT_BEST_ACTION)
        assert self.manager.count() == 2
        self.manager.clear_goals()
        assert self.manager.count() == 0

    def test_count_empty(self) -> None:
        assert self.manager.count() == 0

    def test_count_after_create(self) -> None:
        self.manager.create_goal(ReasoningGoalType.ROOT_CAUSE_ANALYSIS)
        assert self.manager.count() == 1

    def test_get_goal_config_all_types(self) -> None:
        for goal_type in ReasoningGoalType:
            config = self.manager.get_goal_config(goal_type)
            assert isinstance(config, GoalConfig)
            assert config.goal_type == goal_type
            assert isinstance(config.parameters, dict)
            assert isinstance(config.priority, int)

    def test_get_goal_config_root_cause(self) -> None:
        config = self.manager.get_goal_config(ReasoningGoalType.ROOT_CAUSE_ANALYSIS)
        assert config.parameters == {"max_depth": 5, "require_evidence": True}

    def test_get_goal_config_next_best_action(self) -> None:
        config = self.manager.get_goal_config(ReasoningGoalType.NEXT_BEST_ACTION)
        assert config.parameters == {"alternatives_count": 3, "risk_weight": 0.7}


# ═══════════════════════════════════════════════════════════════════════════
# ConstraintManager Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestConstraintManager:
    def setup_method(self) -> None:
        self.manager = ConstraintManager()

    def test_create_constraint_default(self) -> None:
        c = self.manager.create_constraint(ConstraintType.BUDGET)
        assert c.constraint_type == ConstraintType.BUDGET
        assert c.description == "Budget constraint for reasoning operation"
        assert c.value == 0.0
        assert c.is_hard is True
        assert c.is_active is True

    def test_create_constraint_all_types(self) -> None:
        for ct in ConstraintType:
            c = self.manager.create_constraint(ct)
            assert c.constraint_type == ct
            assert isinstance(c.constraint_id, uuid.UUID)

    def test_create_constraint_custom(self) -> None:
        c = self.manager.create_constraint(
            ConstraintType.TIME,
            description="Must finish in 2h",
            value=120.0,
            unit="minutes",
            is_hard=True,
            is_active=True,
        )
        assert c.description == "Must finish in 2h"
        assert c.value == 120.0
        assert c.unit == "minutes"
        assert c.is_hard is True

    def test_create_soft_constraint(self) -> None:
        c = self.manager.create_constraint(
            ConstraintType.BUDGET,
            is_hard=False,
        )
        assert c.is_hard is False

    def test_create_inactive_constraint(self) -> None:
        c = self.manager.create_constraint(
            ConstraintType.SLA,
            is_active=False,
        )
        assert c.is_active is False

    def test_get_constraint_found(self) -> None:
        created = self.manager.create_constraint(ConstraintType.SAFETY)
        retrieved = self.manager.get_constraint(str(created.constraint_id))
        assert retrieved is not None
        assert retrieved.constraint_id == created.constraint_id

    def test_get_constraint_not_found(self) -> None:
        assert self.manager.get_constraint("nonexistent") is None

    def test_get_all_constraints_empty(self) -> None:
        assert self.manager.get_all_constraints() == []

    def test_get_all_constraints_multiple(self) -> None:
        self.manager.create_constraint(ConstraintType.BUDGET)
        self.manager.create_constraint(ConstraintType.TIME)
        self.manager.create_constraint(ConstraintType.SAFETY)
        assert len(self.manager.get_all_constraints()) == 3

    def test_get_active_constraints_all_active(self) -> None:
        self.manager.create_constraint(ConstraintType.BUDGET)
        self.manager.create_constraint(ConstraintType.TIME)
        assert len(self.manager.get_active_constraints()) == 2

    def test_get_active_constraints_some_inactive(self) -> None:
        c1 = self.manager.create_constraint(ConstraintType.BUDGET, is_active=True)
        self.manager.create_constraint(ConstraintType.TIME, is_active=False)
        active = self.manager.get_active_constraints()
        assert len(active) == 1
        assert active[0].constraint_id == c1.constraint_id

    def test_validate_hard_constraint_pass(self) -> None:
        c = self.manager.create_constraint(ConstraintType.BUDGET, value=100.0)
        assert self.manager.validate_constraint(c, 50.0) is True

    def test_validate_hard_constraint_fail(self) -> None:
        c = self.manager.create_constraint(ConstraintType.BUDGET, value=100.0)
        assert self.manager.validate_constraint(c, 150.0) is False

    def test_validate_hard_constraint_equal(self) -> None:
        c = self.manager.create_constraint(ConstraintType.BUDGET, value=100.0)
        assert self.manager.validate_constraint(c, 100.0) is True

    def test_validate_soft_constraint_always_passes(self) -> None:
        c = self.manager.create_constraint(ConstraintType.BUDGET, value=100.0, is_hard=False)
        assert self.manager.validate_constraint(c, 999.0) is True
        assert self.manager.validate_constraint(c, 0.0) is True

    def test_validate_all_empty_values(self) -> None:
        self.manager.create_constraint(ConstraintType.BUDGET, value=100.0)
        results = self.manager.validate_all()
        assert len(results) == 1
        constraint, satisfied = results[0]
        assert constraint.constraint_type == ConstraintType.BUDGET
        # value = 0.0 <= 100.0, so True
        assert satisfied is True

    def test_validate_all_with_values(self) -> None:
        c1 = self.manager.create_constraint(ConstraintType.BUDGET, value=100.0)
        c2 = self.manager.create_constraint(ConstraintType.TIME, value=60.0)
        results = self.manager.validate_all({
            str(c1.constraint_id): 50.0,
            str(c2.constraint_id): 70.0,
        })
        results_map = {str(r[0].constraint_id): r[1] for r in results}
        assert results_map[str(c1.constraint_id)] is True
        assert results_map[str(c2.constraint_id)] is False

    def test_validate_all_ignores_inactive(self) -> None:
        self.manager.create_constraint(ConstraintType.BUDGET, value=100.0, is_active=True)
        self.manager.create_constraint(ConstraintType.TIME, value=10.0, is_active=False)
        results = self.manager.validate_all()
        assert len(results) == 1

    def test_deactivate(self) -> None:
        c = self.manager.create_constraint(ConstraintType.BUDGET)
        assert c.is_active is True
        result = self.manager.deactivate(str(c.constraint_id))
        assert result is True
        retrieved = self.manager.get_constraint(str(c.constraint_id))
        assert retrieved is not None
        assert retrieved.is_active is False

    def test_deactivate_not_found(self) -> None:
        assert self.manager.deactivate("nonexistent") is False

    def test_clear(self) -> None:
        self.manager.create_constraint(ConstraintType.BUDGET)
        self.manager.create_constraint(ConstraintType.TIME)
        assert self.manager.count() == 2
        self.manager.clear()
        assert self.manager.count() == 0

    def test_count_empty(self) -> None:
        assert self.manager.count() == 0

    def test_count_after_create(self) -> None:
        self.manager.create_constraint(ConstraintType.BUDGET)
        assert self.manager.count() == 1


# ═══════════════════════════════════════════════════════════════════════════
# AssumptionManager Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestAssumptionManager:
    def setup_method(self) -> None:
        self.manager = AssumptionManager()

    def test_create_assumption_default(self) -> None:
        a = self.manager.create_assumption("test assumption")
        assert a.description == "test assumption"
        assert a.source == ""
        assert a.status == AssumptionStatus.ACTIVE

    def test_create_assumption_with_source(self) -> None:
        a = self.manager.create_assumption("test", source="user")
        assert a.source == "user"
        assert a.status == AssumptionStatus.ACTIVE

    def test_get_assumption_found(self) -> None:
        created = self.manager.create_assumption("test")
        retrieved = self.manager.get_assumption(str(created.assumption_id))
        assert retrieved is not None
        assert retrieved.assumption_id == created.assumption_id

    def test_get_assumption_not_found(self) -> None:
        assert self.manager.get_assumption("nonexistent") is None

    def test_get_all_empty(self) -> None:
        assert self.manager.get_all_assumptions() == []

    def test_get_all_multiple(self) -> None:
        self.manager.create_assumption("a1")
        self.manager.create_assumption("a2")
        self.manager.create_assumption("a3")
        assert len(self.manager.get_all_assumptions()) == 3

    def test_get_active_all_active(self) -> None:
        self.manager.create_assumption("a1")
        self.manager.create_assumption("a2")
        assert len(self.manager.get_active_assumptions()) == 2

    def test_get_active_some_inactive(self) -> None:
        a1 = self.manager.create_assumption("active")
        a2 = self.manager.create_assumption("inactive")
        self.manager.invalidate_assumption(str(a2.assumption_id))
        active = self.manager.get_active_assumptions()
        assert len(active) == 1
        assert active[0].assumption_id == a1.assumption_id

    def test_validate_assumption(self) -> None:
        a = self.manager.create_assumption("test")
        result = self.manager.validate_assumption(str(a.assumption_id))
        assert result is True
        retrieved = self.manager.get_assumption(str(a.assumption_id))
        assert retrieved is not None
        assert retrieved.status == AssumptionStatus.VALIDATED
        assert retrieved.validated_at is not None

    def test_validate_assumption_not_found(self) -> None:
        assert self.manager.validate_assumption("nonexistent") is False

    def test_invalidate_assumption(self) -> None:
        a = self.manager.create_assumption("test")
        result = self.manager.invalidate_assumption(str(a.assumption_id))
        assert result is True
        retrieved = self.manager.get_assumption(str(a.assumption_id))
        assert retrieved is not None
        assert retrieved.status == AssumptionStatus.INVALIDATED
        assert retrieved.invalidated_at is not None

    def test_invalidate_assumption_not_found(self) -> None:
        assert self.manager.invalidate_assumption("nonexistent") is False

    def test_suspend_assumption(self) -> None:
        a = self.manager.create_assumption("test")
        result = self.manager.suspend_assumption(str(a.assumption_id))
        assert result is True
        retrieved = self.manager.get_assumption(str(a.assumption_id))
        assert retrieved is not None
        assert retrieved.status == AssumptionStatus.SUSPENDED

    def test_suspend_assumption_not_found(self) -> None:
        assert self.manager.suspend_assumption("nonexistent") is False

    def test_clear(self) -> None:
        self.manager.create_assumption("a1")
        self.manager.create_assumption("a2")
        assert self.manager.count() == 2
        self.manager.clear()
        assert self.manager.count() == 0

    def test_count_empty(self) -> None:
        assert self.manager.count() == 0

    def test_count_after_create(self) -> None:
        self.manager.create_assumption("test")
        assert self.manager.count() == 1


# ═══════════════════════════════════════════════════════════════════════════
# StrategySelector Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestStrategySelector:
    def setup_method(self) -> None:
        self.selector = StrategySelector()

    def test_select_root_cause_analysis(self) -> None:
        strategy = self.selector.select_strategy(
            goal_type=ReasoningGoalType.ROOT_CAUSE_ANALYSIS,
        )
        assert strategy == ReasoningStrategyType.HYPOTHESIS

    def test_select_compliance_verification(self) -> None:
        strategy = self.selector.select_strategy(
            goal_type=ReasoningGoalType.COMPLIANCE_VERIFICATION,
        )
        assert strategy == ReasoningStrategyType.RULE_BASED

    def test_select_next_best_action(self) -> None:
        strategy = self.selector.select_strategy(
            goal_type=ReasoningGoalType.NEXT_BEST_ACTION,
        )
        assert strategy == ReasoningStrategyType.EVIDENCE_BASED

    def test_select_maintenance_planning(self) -> None:
        strategy = self.selector.select_strategy(
            goal_type=ReasoningGoalType.MAINTENANCE_PLANNING,
        )
        assert strategy == ReasoningStrategyType.CONSTRAINT

    def test_select_energy_optimization(self) -> None:
        strategy = self.selector.select_strategy(
            goal_type=ReasoningGoalType.ENERGY_OPTIMIZATION,
        )
        assert strategy == ReasoningStrategyType.CONSTRAINT

    def test_select_risk_assessment(self) -> None:
        strategy = self.selector.select_strategy(
            goal_type=ReasoningGoalType.RISK_ASSESSMENT,
        )
        assert strategy == ReasoningStrategyType.MULTI_STEP

    def test_select_anomaly_investigation(self) -> None:
        strategy = self.selector.select_strategy(
            goal_type=ReasoningGoalType.ANOMALY_INVESTIGATION,
        )
        assert strategy == ReasoningStrategyType.EVIDENCE_BASED

    def test_select_no_goal_high_complexity(self) -> None:
        strategy = self.selector.select_strategy(
            goal_type=None,
            complexity="high",
        )
        assert strategy == ReasoningStrategyType.MULTI_STEP

    def test_select_no_goal_evidence_and_rules(self) -> None:
        strategy = self.selector.select_strategy(
            goal_type=None,
            has_evidence=True,
            has_rules=True,
        )
        assert strategy == ReasoningStrategyType.HYBRID

    def test_select_no_goal_evidence_only(self) -> None:
        strategy = self.selector.select_strategy(
            goal_type=None,
            has_evidence=True,
            has_rules=False,
        )
        assert strategy == ReasoningStrategyType.EVIDENCE_BASED

    def test_select_no_goal_rules_only(self) -> None:
        strategy = self.selector.select_strategy(
            goal_type=None,
            has_evidence=False,
            has_rules=True,
        )
        assert strategy == ReasoningStrategyType.RULE_BASED

    def test_select_no_goal_no_evidence_no_rules(self) -> None:
        strategy = self.selector.select_strategy(
            goal_type=None,
            has_evidence=False,
            has_rules=False,
        )
        assert strategy == ReasoningStrategyType.HYBRID

    def test_available_strategies(self) -> None:
        available = self.selector.get_available_strategies()
        assert len(available) == len(ReasoningStrategyType)
        assert ReasoningStrategyType.RULE_BASED in available
        assert ReasoningStrategyType.HYBRID in available

    def test_available_strategies_domain_ignored(self) -> None:
        available_system = self.selector.get_available_strategies(ReasoningDomain.SYSTEM)
        available_energy = self.selector.get_available_strategies(ReasoningDomain.ENERGY)
        assert available_system == available_energy

    def test_rank_strategies_default(self) -> None:
        ranked = self.selector.rank_strategies()
        assert len(ranked) == 6
        for i in range(len(ranked) - 1):
            assert ranked[i][1] >= ranked[i + 1][1]

    def test_rank_strategies_root_cause(self) -> None:
        ranked = self.selector.rank_strategies(
            goal_type=ReasoningGoalType.ROOT_CAUSE_ANALYSIS,
        )
        assert ranked[0][0] == ReasoningStrategyType.HYPOTHESIS
        assert ranked[0][1] == 0.9

    def test_rank_strategies_compliance(self) -> None:
        ranked = self.selector.rank_strategies(
            goal_type=ReasoningGoalType.COMPLIANCE_VERIFICATION,
        )
        assert ranked[0][0] == ReasoningStrategyType.RULE_BASED
        assert ranked[0][1] == 0.9

    def test_rank_strategies_scores_sum_to_reasonable(self) -> None:
        ranked = self.selector.rank_strategies(
            goal_type=ReasoningGoalType.ROOT_CAUSE_ANALYSIS,
        )
        scores = [s for _, s in ranked]
        assert all(0.0 <= s <= 1.0 for s in scores)


# ═══════════════════════════════════════════════════════════════════════════
# HypothesisGenerator Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestHypothesisGenerator:
    def setup_method(self) -> None:
        self.generator = HypothesisGenerator()

    @staticmethod
    def _evids(n: int = 2) -> list[str]:
        return [str(uuid.uuid4()) for _ in range(n)]

    def test_generate_primary_default(self) -> None:
        h = self.generator.generate_primary(self._evids(2))
        assert isinstance(h, Hypothesis)
        assert h.status == HypothesisStatus.PROPOSED
        assert h.confidence == 0.7
        assert h.priority == 10
        assert len(h.supporting_evidence) == 2

    def test_generate_primary_custom_domain(self) -> None:
        h = self.generator.generate_primary(
            self._evids(1), domain=ReasoningDomain.ENERGY,
        )
        assert ReasoningDomain.ENERGY.value in h.description

    def test_generate_primary_custom_description(self) -> None:
        h = self.generator.generate_primary(
            self._evids(1), description="Custom primary hypothesis",
        )
        assert h.description == "Custom primary hypothesis"

    def test_generate_primary_empty_evidence(self) -> None:
        h = self.generator.generate_primary([])
        assert "0 evidence" in h.description
        assert len(h.supporting_evidence) == 0

    def test_generate_alternatives_default(self) -> None:
        alts = self.generator.generate_alternatives(self._evids(1))
        assert len(alts) == 3
        assert all(isinstance(a, Hypothesis) for a in alts)
        assert alts[0].confidence >= alts[1].confidence >= alts[2].confidence

    def test_generate_alternatives_custom_count(self) -> None:
        alts = self.generator.generate_alternatives(self._evids(1), count=5)
        assert len(alts) == 5

    def test_generate_alternatives_count_zero(self) -> None:
        alts = self.generator.generate_alternatives(self._evids(1), count=0)
        assert len(alts) == 0

    def test_generate_alternatives_confidence_decreases(self) -> None:
        alts = self.generator.generate_alternatives(self._evids(2), count=4)
        for i in range(len(alts) - 1):
            assert alts[i].confidence >= alts[i + 1].confidence

    def test_generate_ranked_default(self) -> None:
        ranked = self.generator.generate_ranked(self._evids(2))
        assert len(ranked) == 5
        assert ranked[0].priority == 10  # primary first by confidence
        for i in range(len(ranked) - 1):
            assert ranked[i].confidence >= ranked[i + 1].confidence

    def test_generate_ranked_custom_count(self) -> None:
        ranked = self.generator.generate_ranked(self._evids(1), count=3)
        assert len(ranked) == 3

    def test_generate_ranked_single(self) -> None:
        ranked = self.generator.generate_ranked(self._evids(1), count=1)
        assert len(ranked) == 1
        assert ranked[0].confidence == 0.7  # primary

    def test_create_hypothesis_set(self) -> None:
        h1 = self.generator.generate_primary(self._evids(1))
        h2 = self.generator.generate_alternatives(self._evids(1), count=2)
        hs = self.generator.create_hypothesis_set(
            request_id=str(uuid.uuid4()),
            hypotheses=[h1] + h2,
            domain=ReasoningDomain.SAFETY,
            description="Test set",
        )
        assert isinstance(hs, HypothesisSet)
        assert len(hs.hypotheses) == 3
        assert hs.domain == ReasoningDomain.SAFETY
        assert hs.description == "Test set"


# ═══════════════════════════════════════════════════════════════════════════
# InferenceEngine Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestInferenceEngine:
    def setup_method(self) -> None:
        self.engine = InferenceEngine()

    def test_rule_inference(self) -> None:
        inf = self.engine.rule_inference(rule_id="r1", premise="p1")
        assert isinstance(inf, Inference)
        assert inf.rule_id == "r1"
        assert inf.premise == "p1"
        assert "r1" in inf.conclusion
        assert inf.confidence == 0.8
        assert inf.inference_type == "deductive"
        assert inf.hypothesis_id is None

    def test_rule_inference_with_hypothesis(self) -> None:
        hid = str(uuid.uuid4())
        inf = self.engine.rule_inference("r1", "p1", hypothesis_id=hid)
        assert inf.hypothesis_id is not None
        assert str(inf.hypothesis_id) == hid

    def test_evidence_inference(self) -> None:
        inf = self.engine.evidence_inference(["ev1", "ev2"])
        assert isinstance(inf, Inference)
        assert "2 evidence items" in inf.conclusion
        assert inf.confidence == 0.7
        assert inf.inference_type == "inductive"

    def test_evidence_inference_empty(self) -> None:
        inf = self.engine.evidence_inference([])
        assert inf.confidence == 0.7
        assert "0" in inf.premise

    def test_evidence_inference_with_hypothesis(self) -> None:
        hid = str(uuid.uuid4())
        inf = self.engine.evidence_inference(["ev1"], hypothesis_id=hid)
        assert inf.hypothesis_id is not None

    def test_constraint_inference(self) -> None:
        inf = self.engine.constraint_inference(
            constraint_id="c1",
            constraint_description="budget limit",
        )
        assert isinstance(inf, Inference)
        assert "c1" in inf.conclusion
        assert inf.confidence == 0.9
        assert inf.inference_type == "deductive"

    def test_constraint_inference_with_hypothesis(self) -> None:
        hid = str(uuid.uuid4())
        inf = self.engine.constraint_inference("c1", "desc", hypothesis_id=hid)
        assert inf.hypothesis_id is not None

    def test_goal_inference(self) -> None:
        inf = self.engine.goal_inference(goal_description="find root cause")
        assert isinstance(inf, Inference)
        assert "find root cause" in inf.conclusion
        assert inf.confidence == 0.85
        assert inf.inference_type == "abductive"

    def test_goal_inference_with_hypothesis(self) -> None:
        hid = str(uuid.uuid4())
        inf = self.engine.goal_inference("goal desc", hypothesis_id=hid)
        assert inf.hypothesis_id is not None

    def test_chain_inferences_empty(self) -> None:
        chain = self.engine.chain_inferences([])
        assert isinstance(chain, InferenceChain)
        assert chain.inferences == []
        assert chain.end_conclusion == ""
        assert chain.confidence == 0.0

    def test_chain_inferences_single(self) -> None:
        inf = self.engine.rule_inference("r1", "p1")
        chain = self.engine.chain_inferences([inf])
        assert len(chain.inferences) == 1
        assert chain.end_conclusion == inf.conclusion
        assert chain.confidence == 0.8

    def test_chain_inferences_multiple(self) -> None:
        i1 = self.engine.rule_inference("r1", "p1")
        i2 = self.engine.evidence_inference(["ev1"])
        i3 = self.engine.goal_inference("goal")
        chain = self.engine.chain_inferences([i1, i2, i3])
        assert len(chain.inferences) == 3
        assert chain.end_conclusion == i3.conclusion
        expected_conf = (0.8 + 0.7 + 0.85) / 3
        assert chain.confidence == round(expected_conf, 4)

    def test_chain_inferences_with_request_id(self) -> None:
        rid = str(uuid.uuid4())
        inf = self.engine.rule_inference("r1", "p1")
        chain = self.engine.chain_inferences([inf], request_id=rid)
        assert str(chain.request_id) == rid

    def test_chain_inferences_with_start_hypothesis(self) -> None:
        hid = str(uuid.uuid4())
        inf = self.engine.rule_inference("r1", "p1")
        chain = self.engine.chain_inferences([inf], start_hypothesis_id=hid)
        assert chain.start_hypothesis_id is not None
        assert str(chain.start_hypothesis_id) == hid

    def test_chain_inferences_auto_request_id(self) -> None:
        inf = self.engine.rule_inference("r1", "p1")
        chain = self.engine.chain_inferences([inf])
        assert isinstance(chain.request_id, uuid.UUID)


# ═══════════════════════════════════════════════════════════════════════════
# ContradictionDetector Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestContradictionDetector:
    def setup_method(self) -> None:
        self.detector = ContradictionDetector()

    def test_detect_rule_contradictions_none(self) -> None:
        result = self.detector.detect_rule_contradictions([])
        assert result == []

    def test_detect_rule_contradictions_single(self) -> None:
        result = self.detector.detect_rule_contradictions(["r1"])
        assert result == []

    def test_detect_rule_contradictions_two(self) -> None:
        result = self.detector.detect_rule_contradictions(["r1", "r2"])
        assert len(result) == 1
        assert result[0].severity == ContradictionSeverity.MEDIUM
        assert result[0].resolution_status == ContradictionResolutionStatus.UNRESOLVED
        assert "r1" and "r2" in result[0].description

    def test_detect_rule_contradictions_many(self) -> None:
        result = self.detector.detect_rule_contradictions(["r1", "r2", "r3"])
        assert len(result) == 1  # Only first pair detected

    def test_detect_evidence_contradictions_none(self) -> None:
        result = self.detector.detect_evidence_contradictions([])
        assert result == []

    def test_detect_evidence_contradictions_single(self) -> None:
        h = Hypothesis(
            description="h1",
            confidence=0.8,
            supporting_evidence=[uuid.uuid4()],
        )
        result = self.detector.detect_evidence_contradictions([h])
        assert result == []

    def test_detect_evidence_contradictions_no_overlap(self) -> None:
        uid1, uid2 = uuid.uuid4(), uuid.uuid4()
        h1 = Hypothesis(description="h1", confidence=0.9, supporting_evidence=[uid1])
        h2 = Hypothesis(description="h2", confidence=0.6, supporting_evidence=[uid2])
        result = self.detector.detect_evidence_contradictions([h1, h2])
        assert result == []

    def test_detect_evidence_contradictions_with_overlap(self) -> None:
        shared = uuid.uuid4()
        h1 = Hypothesis(description="h1", confidence=0.9, supporting_evidence=[shared])
        h2 = Hypothesis(description="h2", confidence=0.55, supporting_evidence=[shared])
        # Both > 0.5, diff = 0.35 > 0.3, overlapping evidence => contradiction
        result = self.detector.detect_evidence_contradictions([h1, h2])
        assert len(result) == 1
        assert result[0].severity == ContradictionSeverity.MEDIUM

    def test_detect_evidence_contradictions_small_diff(self) -> None:
        shared = uuid.uuid4()
        h1 = Hypothesis(description="h1", confidence=0.7, supporting_evidence=[shared])
        h2 = Hypothesis(description="h2", confidence=0.55, supporting_evidence=[shared])
        # diff = 0.15 <= 0.3, no contradiction
        result = self.detector.detect_evidence_contradictions([h1, h2])
        assert result == []

    def test_detect_assumption_contradictions_none(self) -> None:
        result = self.detector.detect_assumption_contradictions([])
        assert result == []

    def test_detect_assumption_contradictions_single(self) -> None:
        a = Assumption(description="a1")
        result = self.detector.detect_assumption_contradictions([a])
        assert result == []

    def test_detect_assumption_contradictions_two(self) -> None:
        a1 = Assumption(description="a1")
        a2 = Assumption(description="a2")
        result = self.detector.detect_assumption_contradictions([a1, a2])
        assert len(result) == 1
        assert result[0].severity == ContradictionSeverity.LOW

    def test_detect_goal_conflicts_none(self) -> None:
        result = self.detector.detect_goal_conflicts([])
        assert result == []

    def test_detect_goal_conflicts_single(self) -> None:
        g = ReasoningGoal(goal_type=ReasoningGoalType.ROOT_CAUSE_ANALYSIS, priority=9)
        result = self.detector.detect_goal_conflicts([g])
        assert result == []

    def test_detect_goal_conflicts_no_high_priority(self) -> None:
        g1 = ReasoningGoal(goal_type=ReasoningGoalType.ROOT_CAUSE_ANALYSIS, priority=5)
        g2 = ReasoningGoal(goal_type=ReasoningGoalType.NEXT_BEST_ACTION, priority=6)
        result = self.detector.detect_goal_conflicts([g1, g2])
        assert result == []

    def test_detect_goal_conflicts_both_high_priority(self) -> None:
        g1 = ReasoningGoal(goal_type=ReasoningGoalType.ROOT_CAUSE_ANALYSIS, priority=8)
        g2 = ReasoningGoal(goal_type=ReasoningGoalType.NEXT_BEST_ACTION, priority=9)
        result = self.detector.detect_goal_conflicts([g1, g2])
        assert len(result) == 1
        assert result[0].severity == ContradictionSeverity.HIGH

    def test_detect_all_empty(self) -> None:
        result = self.detector.detect_all()
        assert result == []

    def test_detect_all_rule_only(self) -> None:
        result = self.detector.detect_all(rule_ids=["r1", "r2"])
        assert len(result) == 1

    def test_detect_all_assumptions_only(self) -> None:
        a1 = Assumption(description="a1")
        a2 = Assumption(description="a2")
        result = self.detector.detect_all(assumptions=[a1, a2])
        assert len(result) == 1

    def test_detect_all_goals_only(self) -> None:
        g1 = ReasoningGoal(goal_type=ReasoningGoalType.ROOT_CAUSE_ANALYSIS, priority=9)
        g2 = ReasoningGoal(goal_type=ReasoningGoalType.NEXT_BEST_ACTION, priority=8)
        result = self.detector.detect_all(goals=[g1, g2])
        assert len(result) == 1

    def test_detect_all_multiple_sources(self) -> None:
        h1 = Hypothesis(description="h1", confidence=0.9)
        h2 = Hypothesis(description="h2", confidence=0.4, supporting_evidence=[uuid.uuid4()])
        # h1 has no evidence, h2 has some, so no overlap — no evidence contradictions
        a1 = Assumption(description="a1")
        a2 = Assumption(description="a2")
        result = self.detector.detect_all(
            hypotheses=[h1, h2],
            rule_ids=["r1", "r2"],
            assumptions=[a1, a2],
        )
        # rule contradiction + assumption contradiction = 2
        assert len(result) == 2


# ═══════════════════════════════════════════════════════════════════════════
# ReasoningGraphBuilder Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestReasoningGraphBuilder:
    def setup_method(self) -> None:
        self.builder = ReasoningGraphBuilder()

    def test_create_graph(self) -> None:
        graph = self.builder.create_graph()
        assert isinstance(graph, ReasoningGraph)
        assert isinstance(graph.graph_id, uuid.UUID)
        assert graph.nodes == []
        assert graph.edges == []
        assert self.builder.count() == 1

    def test_add_node(self) -> None:
        graph = self.builder.create_graph()
        updated = self.builder.add_node(
            graph,
            node_type="evidence",
            label="Evidence 1",
            data={"source": "sensor"},
        )
        assert len(updated.nodes) == 1
        assert updated.nodes[0].node_type == "evidence"
        assert updated.nodes[0].label == "Evidence 1"
        assert updated.nodes[0].data == {"source": "sensor"}

    def test_add_node_defaults(self) -> None:
        graph = self.builder.create_graph()
        self.builder.add_node(graph)
        assert len(graph.nodes) == 1
        assert graph.nodes[0].node_type == ""
        assert graph.nodes[0].label == ""

    def test_add_multiple_nodes(self) -> None:
        graph = self.builder.create_graph()
        self.builder.add_node(graph, node_type="evidence", label="ev1")
        self.builder.add_node(graph, node_type="hypothesis", label="h1")
        self.builder.add_node(graph, node_type="decision", label="d1")
        assert len(graph.nodes) == 3

    def test_add_edge(self) -> None:
        graph = self.builder.create_graph()
        self.builder.add_node(graph, node_type="evidence", label="ev1")
        self.builder.add_node(graph, node_type="hypothesis", label="h1")
        n1, n2 = graph.nodes[0], graph.nodes[1]
        updated = self.builder.add_edge(
            graph,
            source_id=n1.node_id,
            target_id=n2.node_id,
            edge_type="supports",
            weight=0.9,
        )
        assert len(updated.edges) == 1
        assert updated.edges[0].source_id == n1.node_id
        assert updated.edges[0].target_id == n2.node_id
        assert updated.edges[0].edge_type == "supports"
        assert updated.edges[0].weight == 0.9

    def test_add_edge_default_weight(self) -> None:
        graph = self.builder.create_graph()
        self.builder.add_node(graph)
        self.builder.add_node(graph)
        self.builder.add_edge(
            graph,
            source_id=graph.nodes[0].node_id,
            target_id=graph.nodes[1].node_id,
            edge_type="leads_to",
        )
        assert graph.edges[0].weight == 1.0

    def test_add_decision_path(self) -> None:
        graph = self.builder.create_graph()
        self.builder.add_node(graph, node_type="evidence", label="ev1")
        self.builder.add_node(graph, node_type="hypothesis", label="h1")
        self.builder.add_node(graph, node_type="decision", label="d1")
        node_ids = [n.node_id for n in graph.nodes]
        self.builder.add_decision_path(graph, node_ids)
        assert len(graph.decision_paths) == 1
        assert graph.decision_paths[0] == node_ids

    def test_add_alternative_path(self) -> None:
        graph = self.builder.create_graph()
        self.builder.add_node(graph, node_type="evidence", label="ev1")
        self.builder.add_node(graph, node_type="hypothesis", label="h1")
        node_ids = [n.node_id for n in graph.nodes]
        self.builder.add_alternative_path(graph, node_ids)
        assert len(graph.alternative_paths) == 1
        assert graph.alternative_paths[0] == node_ids

    def test_add_empty_path(self) -> None:
        graph = self.builder.create_graph()
        self.builder.add_decision_path(graph, [])
        assert len(graph.decision_paths) == 1
        assert graph.decision_paths[0] == []

    def test_get_graph_found(self) -> None:
        graph = self.builder.create_graph()
        retrieved = self.builder.get_graph(str(graph.graph_id))
        assert retrieved is not None
        assert retrieved.graph_id == graph.graph_id

    def test_get_graph_not_found(self) -> None:
        assert self.builder.get_graph("nonexistent") is None

    def test_clear(self) -> None:
        self.builder.create_graph()
        self.builder.create_graph()
        assert self.builder.count() == 2
        self.builder.clear()
        assert self.builder.count() == 0

    def test_count_empty(self) -> None:
        assert self.builder.count() == 0


# ═══════════════════════════════════════════════════════════════════════════
# DecisionAlternatives Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestDecisionAlternatives:
    def setup_method(self) -> None:
        self.da = DecisionAlternatives()

    def test_generate_alternatives_default(self) -> None:
        alts = self.da.generate_alternatives(evidence_ids=["ev1", "ev2"])
        assert len(alts) == 3
        assert all(isinstance(a, ReasoningAlternative) for a in alts)
        assert alts[0].status == AlternativeStatus.CANDIDATE
        assert alts[0].supporting_evidence == ["ev1", "ev2"]

    def test_generate_alternatives_custom_count(self) -> None:
        alts = self.da.generate_alternatives(["ev1"], count=5)
        assert len(alts) == 5

    def test_generate_alternatives_with_hypotheses(self) -> None:
        alts = self.da.generate_alternatives(
            ["ev1"],
            hypotheses=["Hyp A", "Hyp B"],
            count=2,
        )
        assert alts[0].decision_description == "Hyp A"
        assert alts[1].decision_description == "Hyp B"

    def test_generate_alternatives_hypotheses_shorter_than_count(self) -> None:
        alts = self.da.generate_alternatives(
            ["ev1"],
            hypotheses=["Only"],
            count=3,
        )
        assert alts[0].decision_description == "Only"
        assert alts[1].decision_description == "Alternative 2"
        assert alts[2].decision_description == "Alternative 3"

    def test_generate_alternatives_tracks_internally(self) -> None:
        self.da.generate_alternatives(["ev1"], count=2)
        assert self.da.count() == 2

    def test_evaluate_alternative_found(self) -> None:
        alts = self.da.generate_alternatives(["ev1"], count=2)
        alt_id = str(alts[0].alternative_id)
        result = self.da.evaluate_alternative(alt_id, score=0.85)
        assert result is not None
        assert result.score == 0.85
        assert result.status == AlternativeStatus.EVALUATED

    def test_evaluate_alternative_not_found(self) -> None:
        result = self.da.evaluate_alternative("nonexistent", score=0.5)
        assert result is None

    def test_evaluate_alternative_default_score(self) -> None:
        alts = self.da.generate_alternatives(["ev1"], count=1)
        result = self.da.evaluate_alternative(str(alts[0].alternative_id))
        assert result is not None
        assert result.score == 0.0

    def test_select_alternative(self) -> None:
        alts = self.da.generate_alternatives(["ev1"], count=2)
        result = self.da.select_alternative(str(alts[0].alternative_id))
        assert result is not None
        assert result.status == AlternativeStatus.SELECTED

    def test_select_alternative_not_found(self) -> None:
        assert self.da.select_alternative("nonexistent") is None

    def test_reject_alternative(self) -> None:
        alts = self.da.generate_alternatives(["ev1"], count=2)
        result = self.da.reject_alternative(str(alts[1].alternative_id))
        assert result is not None
        assert result.status == AlternativeStatus.REJECTED

    def test_reject_alternative_not_found(self) -> None:
        assert self.da.reject_alternative("nonexistent") is None

    def test_get_best_alternative(self) -> None:
        alts = self.da.generate_alternatives(["ev1"], count=3)
        self.da.evaluate_alternative(str(alts[0].alternative_id), 0.5)
        self.da.evaluate_alternative(str(alts[1].alternative_id), 0.9)
        self.da.evaluate_alternative(str(alts[2].alternative_id), 0.7)
        best = self.da.get_best_alternative()
        assert best is not None
        assert best.score == 0.9
        assert best.alternative_id == alts[1].alternative_id

    def test_get_best_alternative_no_evaluated(self) -> None:
        self.da.generate_alternatives(["ev1"], count=3)
        assert self.da.get_best_alternative() is None

    def test_get_best_alternative_empty(self) -> None:
        assert self.da.get_best_alternative() is None

    def test_get_all_empty(self) -> None:
        assert self.da.get_all_alternatives() == []

    def test_get_all_multiple(self) -> None:
        self.da.generate_alternatives(["ev1"], count=4)
        assert len(self.da.get_all_alternatives()) == 4

    def test_clear(self) -> None:
        self.da.generate_alternatives(["ev1"], count=3)
        assert self.da.count() == 3
        self.da.clear()
        assert self.da.count() == 0

    def test_count_empty(self) -> None:
        assert self.da.count() == 0


# ═══════════════════════════════════════════════════════════════════════════
# WeightManager Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestWeightManager:
    def setup_method(self) -> None:
        self.wm = WeightManager()

    def test_evidence_weight_default(self) -> None:
        w = self.wm.calculate_evidence_weight()
        # quality=0.5, trust=0.5, count=0 => 0.5*0.4 + 0.5*0.4 + 0*0.2 = 0.4
        assert w == 0.4

    def test_evidence_weight_custom(self) -> None:
        w = self.wm.calculate_evidence_weight(
            evidence_count=10,
            quality_score=0.9,
            trust_score=0.8,
        )
        # 0.9*0.4 + 0.8*0.4 + 1.0*0.2 = 0.36 + 0.32 + 0.2 = 0.88
        assert w == 0.88

    def test_evidence_weight_count_capped(self) -> None:
        w = self.wm.calculate_evidence_weight(evidence_count=100, quality_score=0.5, trust_score=0.5)
        # 0.5*0.4 + 0.5*0.4 + 1.0*0.2 = 0.2 + 0.2 + 0.2 = 0.6
        assert w == 0.6

    def test_evidence_weight_zero_quality(self) -> None:
        w = self.wm.calculate_evidence_weight(evidence_count=5, quality_score=0.0, trust_score=0.0)
        # 0.0*0.4 + 0.0*0.4 + 0.5*0.2 = 0.1
        assert w == 0.1

    def test_rule_weight_default(self) -> None:
        w = self.wm.calculate_rule_weight()
        # 0.5*0.7 + 0*0.3 = 0.35
        assert w == 0.35

    def test_rule_weight_custom(self) -> None:
        w = self.wm.calculate_rule_weight(rule_count=10, rule_strength=1.0)
        # 1.0*0.7 + 1.0*0.3 = 1.0
        assert w == 1.0

    def test_rule_weight_count_capped(self) -> None:
        w = self.wm.calculate_rule_weight(rule_count=50, rule_strength=0.5)
        # 0.5*0.7 + 1.0*0.3 = 0.35 + 0.3 = 0.65
        assert w == 0.65

    def test_memory_weight_default(self) -> None:
        w = self.wm.calculate_memory_weight()
        # 0.5*0.8 + 0*0.2 = 0.4
        assert w == 0.4

    def test_memory_weight_custom(self) -> None:
        w = self.wm.calculate_memory_weight(memory_count=20, relevance_score=1.0)
        # 1.0*0.8 + 1.0*0.2 = 1.0
        assert w == 1.0

    def test_knowledge_weight_default(self) -> None:
        w = self.wm.calculate_knowledge_weight()
        # 0.5*0.7 + 0*0.3 = 0.35
        assert w == 0.35

    def test_knowledge_weight_custom(self) -> None:
        w = self.wm.calculate_knowledge_weight(knowledge_count=20, confidence_score=1.0)
        # 1.0*0.7 + 1.0*0.3 = 1.0
        assert w == 1.0

    def test_constraint_weight_default(self) -> None:
        w = self.wm.calculate_constraint_weight()
        # 0.5*0.6 + 0*0.4 = 0.3
        assert w == 0.3

    def test_constraint_weight_custom(self) -> None:
        w = self.wm.calculate_constraint_weight(constraint_count=10, severity=1.0)
        # 1.0*0.6 + 1.0*0.4 = 1.0
        assert w == 1.0

    def test_goal_weight_high_primary(self) -> None:
        w = self.wm.calculate_goal_weight(goal_priority=10, is_primary=True)
        # 1.0*0.6 + 1.0*0.4 = 1.0
        assert w == 1.0

    def test_goal_weight_low_not_primary(self) -> None:
        w = self.wm.calculate_goal_weight(goal_priority=0, is_primary=False)
        # 0.0*0.6 + 0.5*0.4 = 0.2
        assert w == 0.2

    def test_overall_weight_all_zeros(self) -> None:
        w = self.wm.calculate_overall_weight()
        assert w == 0.0

    def test_overall_weight_all_max(self) -> None:
        w = self.wm.calculate_overall_weight(
            evidence_weight=1.0,
            rule_weight=1.0,
            memory_weight=1.0,
            knowledge_weight=1.0,
            constraint_weight=1.0,
            goal_weight=1.0,
        )
        assert w == 1.0

    def test_overall_weight_mixed(self) -> None:
        w = self.wm.calculate_overall_weight(
            evidence_weight=0.8,
            rule_weight=0.6,
            memory_weight=0.4,
            knowledge_weight=0.2,
            constraint_weight=0.0,
            goal_weight=1.0,
        )
        # (0.8 + 0.6 + 0.4 + 0.2 + 0.0 + 1.0) / 6 = 3.0 / 6 = 0.5
        assert w == 0.5


# ═══════════════════════════════════════════════════════════════════════════
# ReasoningScoreCalculator Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestReasoningScoreCalculator:
    def setup_method(self) -> None:
        self.calc = ReasoningScoreCalculator()

    def test_consistency_no_contradictions(self) -> None:
        s = self.calc.calculate_consistency(contradiction_count=0, total_hypotheses=5)
        assert s == 1.0

    def test_consistency_all_contradictions(self) -> None:
        s = self.calc.calculate_consistency(contradiction_count=5, total_hypotheses=5)
        assert s == 0.0

    def test_consistency_partial(self) -> None:
        s = self.calc.calculate_consistency(contradiction_count=2, total_hypotheses=5)
        # 1.0 - (2/5) = 1.0 - 0.4 = 0.6
        assert s == 0.6

    def test_consistency_zero_hypotheses(self) -> None:
        s = self.calc.calculate_consistency(contradiction_count=0, total_hypotheses=0)
        assert s == 0.0

    def test_consistency_more_contradictions_than_hypotheses(self) -> None:
        s = self.calc.calculate_consistency(contradiction_count=10, total_hypotheses=3)
        assert s == 0.0

    def test_coverage_full(self) -> None:
        s = self.calc.calculate_coverage(evidence_covered=10, total_evidence=10)
        assert s == 1.0

    def test_coverage_partial(self) -> None:
        s = self.calc.calculate_coverage(evidence_covered=3, total_evidence=10)
        assert s == 0.3

    def test_coverage_zero_total(self) -> None:
        s = self.calc.calculate_coverage(evidence_covered=0, total_evidence=0)
        assert s == 0.0

    def test_completeness_full(self) -> None:
        s = self.calc.calculate_completeness(hypotheses_generated=5, hypotheses_evaluated=5)
        assert s == 1.0

    def test_completeness_partial(self) -> None:
        s = self.calc.calculate_completeness(hypotheses_generated=10, hypotheses_evaluated=3)
        assert s == 0.3

    def test_completeness_zero_generated(self) -> None:
        s = self.calc.calculate_completeness(hypotheses_generated=0, hypotheses_evaluated=0)
        assert s == 0.0

    def test_rule_satisfaction_full(self) -> None:
        s = self.calc.calculate_rule_satisfaction(satisfied_rules=10, total_rules=10)
        assert s == 1.0

    def test_rule_satisfaction_partial(self) -> None:
        s = self.calc.calculate_rule_satisfaction(satisfied_rules=7, total_rules=10)
        assert s == 0.7

    def test_rule_satisfaction_zero_total(self) -> None:
        s = self.calc.calculate_rule_satisfaction(satisfied_rules=0, total_rules=0)
        assert s == 1.0  # No rules means no violations

    def test_assumption_quality_all_validated(self) -> None:
        s = self.calc.calculate_assumption_quality(
            validated_assumptions=5,
            invalidated_assumptions=0,
            total_assumptions=5,
        )
        # 1.0 * 0.7 + 1.0 * 0.3 = 1.0
        assert s == 1.0

    def test_assumption_quality_mixed(self) -> None:
        s = self.calc.calculate_assumption_quality(
            validated_assumptions=3,
            invalidated_assumptions=2,
            total_assumptions=5,
        )
        # (3/5)*0.7 + (1-2/5)*0.3 = 0.42 + 0.18 = 0.6
        assert s == 0.6

    def test_assumption_quality_all_invalidated(self) -> None:
        s = self.calc.calculate_assumption_quality(
            validated_assumptions=0,
            invalidated_assumptions=5,
            total_assumptions=5,
        )
        # 0*0.7 + (1-1)*0.3 = 0.0
        assert s == 0.0

    def test_assumption_quality_zero_total(self) -> None:
        s = self.calc.calculate_assumption_quality(
            validated_assumptions=0,
            invalidated_assumptions=0,
            total_assumptions=0,
        )
        assert s == 1.0

    def test_overall_all_perfect(self) -> None:
        score = self.calc.calculate_overall(
            consistency=1.0,
            coverage=1.0,
            completeness=1.0,
            rule_satisfaction=1.0,
            assumption_quality=1.0,
        )
        assert score.consistency == 1.0
        assert score.coverage == 1.0
        assert score.completeness == 1.0
        assert score.rule_satisfaction == 1.0
        assert score.assumption_quality == 1.0
        assert score.overall == 1.0

    def test_overall_mixed(self) -> None:
        score = self.calc.calculate_overall(
            consistency=0.8,
            coverage=0.6,
            completeness=0.4,
            rule_satisfaction=0.2,
            assumption_quality=0.0,
        )
        # (0.8 + 0.6 + 0.4 + 0.2 + 0.0) / 5 = 2.0 / 5 = 0.4
        assert score.overall == 0.4

    def test_overall_all_zeros(self) -> None:
        score = self.calc.calculate_overall()
        assert score.overall == 0.0


# ═══════════════════════════════════════════════════════════════════════════
# PolicyEngine Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestPolicyEngine:
    def setup_method(self) -> None:
        self.policy = PolicyEngine()

    def test_strict_pass(self) -> None:
        result = self.policy.check(
            policy_type=PolicyType.STRICT,
            confidence=0.9,
            contradiction_count=0,
            constraint_violations=0,
        )
        assert result.allowed is True
        assert result.policy_type == PolicyType.STRICT

    def test_strict_fail_low_confidence(self) -> None:
        result = self.policy.check(
            policy_type=PolicyType.STRICT,
            confidence=0.7,
            contradiction_count=0,
            constraint_violations=0,
        )
        assert result.allowed is False

    def test_strict_fail_contradictions(self) -> None:
        result = self.policy.check(
            policy_type=PolicyType.STRICT,
            confidence=0.9,
            contradiction_count=1,
            constraint_violations=0,
        )
        assert result.allowed is False

    def test_strict_fail_violations(self) -> None:
        result = self.policy.check(
            policy_type=PolicyType.STRICT,
            confidence=0.9,
            contradiction_count=0,
            constraint_violations=1,
        )
        assert result.allowed is False

    def test_balanced_pass(self) -> None:
        result = self.policy.check(
            policy_type=PolicyType.BALANCED,
            confidence=0.6,
            contradiction_count=2,
            constraint_violations=1,
        )
        assert result.allowed is True

    def test_balanced_fail_low_confidence(self) -> None:
        result = self.policy.check(
            policy_type=PolicyType.BALANCED,
            confidence=0.4,
            contradiction_count=0,
            constraint_violations=0,
        )
        assert result.allowed is False

    def test_balanced_fail_too_many_contradictions(self) -> None:
        result = self.policy.check(
            policy_type=PolicyType.BALANCED,
            confidence=0.9,
            contradiction_count=3,
            constraint_violations=0,
        )
        assert result.allowed is False

    def test_conservative_pass(self) -> None:
        result = self.policy.check(
            policy_type=PolicyType.CONSERVATIVE,
            confidence=0.8,
            contradiction_count=0,
            constraint_violations=0,
        )
        assert result.allowed is True

    def test_conservative_fail_low_confidence(self) -> None:
        result = self.policy.check(
            policy_type=PolicyType.CONSERVATIVE,
            confidence=0.6,
            contradiction_count=0,
            constraint_violations=0,
        )
        assert result.allowed is False

    def test_conservative_fail_too_many_contradictions(self) -> None:
        result = self.policy.check(
            policy_type=PolicyType.CONSERVATIVE,
            confidence=0.9,
            contradiction_count=2,
            constraint_violations=0,
        )
        assert result.allowed is False

    def test_conservative_fail_violations(self) -> None:
        result = self.policy.check(
            policy_type=PolicyType.CONSERVATIVE,
            confidence=0.9,
            contradiction_count=0,
            constraint_violations=1,
        )
        assert result.allowed is False

    def test_aggressive_pass(self) -> None:
        result = self.policy.check(
            policy_type=PolicyType.AGGRESSIVE,
            confidence=0.4,
            contradiction_count=5,
            constraint_violations=3,
        )
        assert result.allowed is True

    def test_aggressive_fail_low_confidence(self) -> None:
        result = self.policy.check(
            policy_type=PolicyType.AGGRESSIVE,
            confidence=0.2,
            contradiction_count=0,
            constraint_violations=0,
        )
        assert result.allowed is False

    def test_aggressive_fail_too_many_violations(self) -> None:
        result = self.policy.check(
            policy_type=PolicyType.AGGRESSIVE,
            confidence=0.9,
            contradiction_count=0,
            constraint_violations=4,
        )
        assert result.allowed is False

    def test_emergency_always_passes(self) -> None:
        cases = [
            (0.0, 10, 10),
            (0.1, 0, 0),
            (0.9, 0, 0),
            (0.5, 100, 100),
        ]
        for conf, cc, cv in cases:
            result = self.policy.check(
                policy_type=PolicyType.EMERGENCY,
                confidence=conf,
                contradiction_count=cc,
                constraint_violations=cv,
            )
            assert result.allowed is True
            assert result.policy_type == PolicyType.EMERGENCY

    def test_emergency_confidence_floor(self) -> None:
        result = self.policy.check(
            policy_type=PolicyType.EMERGENCY,
            confidence=0.0,
        )
        assert result.confidence == 0.3  # max(0.3, 0.0)

    def test_emergency_confidence_above_floor(self) -> None:
        result = self.policy.check(
            policy_type=PolicyType.EMERGENCY,
            confidence=0.8,
        )
        assert result.confidence == 0.8


# ═══════════════════════════════════════════════════════════════════════════
# ReasoningTrace Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestReasoningTrace:
    def setup_method(self) -> None:
        self.trace = ReasoningTrace()

    def test_record_event_defaults(self) -> None:
        record = self.trace.record_event(
            stage_name="TEST",
            operation="test_op",
            reasoning_id="r1",
        )
        assert isinstance(record, TraceRecord)
        assert record.stage_name == "TEST"
        assert record.operation == "test_op"
        assert record.reasoning_id == "r1"
        assert record.success is True
        assert record.warnings == []
        assert record.errors == []
        assert record.correlation_id == ""

    def test_record_event_with_all_fields(self) -> None:
        record = self.trace.record_event(
            stage_name="INFERENCE",
            operation="infer",
            reasoning_id="r1",
            correlation_id="c1",
            success=False,
            warnings=["warn1"],
            errors=["err1"],
            duration_ms=15.3,
        )
        assert record.correlation_id == "c1"
        assert record.success is False
        assert record.warnings == ["warn1"]
        assert record.errors == ["err1"]
        assert record.duration_ms == 15.3

    def test_record_goal(self) -> None:
        record = self.trace.record_goal(
            goal_type="ROOT_CAUSE_ANALYSIS",
            reasoning_id="r1",
            correlation_id="c1",
            duration_ms=5.0,
        )
        assert record.stage_name == "GOAL"
        assert record.operation == "goal:ROOT_CAUSE_ANALYSIS"
        assert record.duration_ms == 5.0

    def test_record_strategy(self) -> None:
        record = self.trace.record_strategy(
            strategy_type="HYBRID",
            reasoning_id="r1",
            correlation_id="c1",
            duration_ms=3.0,
        )
        assert record.stage_name == "STRATEGY"
        assert record.operation == "strategy:HYBRID"

    def test_record_assumptions(self) -> None:
        record = self.trace.record_assumptions(
            assumption_count=5,
            reasoning_id="r1",
        )
        assert record.stage_name == "ASSUMPTIONS"
        assert record.operation == "assumptions:5"

    def test_record_constraints(self) -> None:
        record = self.trace.record_constraints(
            constraint_count=3,
            reasoning_id="r1",
        )
        assert record.stage_name == "CONSTRAINTS"
        assert record.operation == "constraints:3"

    def test_record_inference(self) -> None:
        record = self.trace.record_inference(
            inference_count=7,
            reasoning_id="r1",
        )
        assert record.stage_name == "INFERENCE"
        assert record.operation == "inference:7"

    def test_record_alternatives(self) -> None:
        record = self.trace.record_alternatives(
            alternative_count=4,
            reasoning_id="r1",
        )
        assert record.stage_name == "ALTERNATIVES"
        assert record.operation == "alternatives:4"

    def test_record_decision(self) -> None:
        record = self.trace.record_decision(
            decision_summary="Selected best alternative",
            reasoning_id="r1",
        )
        assert record.stage_name == "DECISION"
        assert record.operation == "decision:Selected best alternative"

    def test_record_decision_truncated(self) -> None:
        long_summary = "x" * 100
        record = self.trace.record_decision(
            decision_summary=long_summary,
            reasoning_id="r1",
        )
        assert len(record.operation) == len("decision:") + 50

    def test_get_by_reasoning_id(self) -> None:
        self.trace.record_event("STAGE1", "op1", "r1")
        self.trace.record_event("STAGE2", "op2", "r1")
        self.trace.record_event("STAGE3", "op3", "r2")
        records = self.trace.get_by_reasoning_id("r1")
        assert len(records) == 2

    def test_get_by_reasoning_id_empty(self) -> None:
        records = self.trace.get_by_reasoning_id("nonexistent")
        assert records == []

    def test_get_by_stage(self) -> None:
        self.trace.record_event("GOAL", "g1", "r1")
        self.trace.record_event("GOAL", "g2", "r2")
        self.trace.record_event("INFERENCE", "i1", "r1")
        records = self.trace.get_by_stage("GOAL")
        assert len(records) == 2

    def test_get_by_stage_empty(self) -> None:
        assert self.trace.get_by_stage("NONEXISTENT") == []

    def test_get_recent_default(self) -> None:
        for i in range(20):
            self.trace.record_event(f"STAGE{i}", f"op{i}", "r1")
        recent = self.trace.get_recent()
        assert len(recent) == 10
        assert recent[0].operation == "op10"
        assert recent[-1].operation == "op19"

    def test_get_recent_less_than_limit(self) -> None:
        self.trace.record_event("STAGE1", "op1", "r1")
        self.trace.record_event("STAGE2", "op2", "r1")
        recent = self.trace.get_recent(limit=10)
        assert len(recent) == 2

    def test_get_recent_from_empty(self) -> None:
        assert self.trace.get_recent() == []

    def test_clear(self) -> None:
        self.trace.record_event("STAGE1", "op1", "r1")
        self.trace.record_event("STAGE2", "op2", "r1")
        assert self.trace.count() == 2
        self.trace.clear()
        assert self.trace.count() == 0

    def test_count_empty(self) -> None:
        assert self.trace.count() == 0

    def test_count_after_records(self) -> None:
        for i in range(5):
            self.trace.record_event(f"STAGE{i}", f"op{i}", "r1")
        assert self.trace.count() == 5


# ═══════════════════════════════════════════════════════════════════════════
# ReasoningMetricsCollector Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestReasoningMetricsCollector:
    def setup_method(self) -> None:
        self.metrics = ReasoningMetricsCollector()

    def test_increment_hypotheses_default(self) -> None:
        self.metrics.increment_hypotheses()
        snap = self.metrics.snapshot()
        assert snap.hypotheses_count == 1

    def test_increment_hypotheses_custom(self) -> None:
        self.metrics.increment_hypotheses(5)
        snap = self.metrics.snapshot()
        assert snap.hypotheses_count == 5

    def test_increment_alternatives_default(self) -> None:
        self.metrics.increment_alternatives()
        snap = self.metrics.snapshot()
        assert snap.alternatives_count == 1

    def test_increment_alternatives_custom(self) -> None:
        self.metrics.increment_alternatives(10)
        snap = self.metrics.snapshot()
        assert snap.alternatives_count == 10

    def test_increment_constraints_default(self) -> None:
        self.metrics.increment_constraints()
        snap = self.metrics.snapshot()
        assert snap.constraints_count == 1

    def test_increment_constraints_custom(self) -> None:
        self.metrics.increment_constraints(3)
        snap = self.metrics.snapshot()
        assert snap.constraints_count == 3

    def test_increment_contradictions_default(self) -> None:
        self.metrics.increment_contradictions()
        snap = self.metrics.snapshot()
        assert snap.contradictions_count == 1

    def test_increment_contradictions_custom(self) -> None:
        self.metrics.increment_contradictions(7)
        snap = self.metrics.snapshot()
        assert snap.contradictions_count == 7

    def test_increment_goals_default(self) -> None:
        self.metrics.increment_goals()
        snap = self.metrics.snapshot()
        assert snap.goals_count == 1

    def test_increment_goals_custom(self) -> None:
        self.metrics.increment_goals(2)
        snap = self.metrics.snapshot()
        assert snap.goals_count == 2

    def test_record_score(self) -> None:
        self.metrics.record_score(0.85)
        snap = self.metrics.snapshot()
        assert snap.average_score == 0.85

    def test_record_score_multiple(self) -> None:
        self.metrics.record_score(0.8)
        self.metrics.record_score(0.9)
        self.metrics.record_score(1.0)
        snap = self.metrics.snapshot()
        assert snap.average_score == 0.9

    def test_record_score_clamps(self) -> None:
        self.metrics.record_score(-0.5)
        snap = self.metrics.snapshot()
        assert snap.average_score == 0.0

    def test_record_score_clamps_upper(self) -> None:
        self.metrics.record_score(1.5)
        snap = self.metrics.snapshot()
        assert snap.average_score == 1.0

    def test_record_trace(self) -> None:
        self.metrics.record_trace()
        self.metrics.record_trace()
        self.metrics.record_trace()
        snap = self.metrics.snapshot()
        assert snap.trace_count == 3

    def test_snapshot_default(self) -> None:
        snap = self.metrics.snapshot()
        assert snap.hypotheses_count == 0
        assert snap.alternatives_count == 0
        assert snap.constraints_count == 0
        assert snap.contradictions_count == 0
        assert snap.goals_count == 0
        assert snap.average_score == 0.0
        assert snap.trace_count == 0
        assert snap.collected_at is not None

    def test_snapshot_all_counters(self) -> None:
        self.metrics.increment_hypotheses(2)
        self.metrics.increment_alternatives(3)
        self.metrics.increment_constraints(4)
        self.metrics.increment_contradictions(5)
        self.metrics.increment_goals(1)
        self.metrics.record_score(0.75)
        self.metrics.record_trace()
        snap = self.metrics.snapshot()
        assert snap.hypotheses_count == 2
        assert snap.alternatives_count == 3
        assert snap.constraints_count == 4
        assert snap.contradictions_count == 5
        assert snap.goals_count == 1
        assert snap.average_score == 0.75
        assert snap.trace_count == 1

    def test_reset(self) -> None:
        self.metrics.increment_hypotheses(10)
        self.metrics.increment_alternatives(10)
        self.metrics.record_score(0.9)
        self.metrics.record_trace()
        self.metrics.reset()
        snap = self.metrics.snapshot()
        assert snap.hypotheses_count == 0
        assert snap.alternatives_count == 0
        assert snap.constraints_count == 0
        assert snap.contradictions_count == 0
        assert snap.goals_count == 0
        assert snap.average_score == 0.0
        assert snap.trace_count == 0

    def test_reset_preserves_new_state(self) -> None:
        self.metrics.reset()
        snap = self.metrics.snapshot()
        assert snap.hypotheses_count == 0
        assert snap.average_score == 0.0
