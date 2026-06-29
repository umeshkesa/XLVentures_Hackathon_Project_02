"""Phase 1 tests for the Reasoning Engine (Architecture, Contracts & Models).

Tests all Phase 1 components: enums, models, DTOs, events, exceptions,
and their relationships. Validates that all contracts are correctly
defined and behave as expected.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from adip.reasoning import (
    Contradiction,
    ContradictionDetected,
    ContradictionException,
    ContradictionResolutionStatus,
    ContradictionSeverity,
    Hypothesis,
    HypothesisException,
    HypothesisGenerated,
    HypothesisSet,
    HypothesisStatus,
    Inference,
    InferenceChain,
    InferenceCompleted,
    InferenceException,
    ReasoningCompleted,
    ReasoningConfidence,
    ReasoningContext,
    ReasoningDecision,
    ReasoningDecisionDTO,
    ReasoningDomain,
    ReasoningEvent,
    ReasoningException,
    ReasoningHealth,
    ReasoningMetadata,
    ReasoningMetrics,
    ReasoningPath,
    ReasoningRequest,
    ReasoningRequestDTO,
    ReasoningResponseDTO,
    ReasoningResult,
    ReasoningSession,
    ReasoningStarted,
    ReasoningStatus,
    ReasoningStep,
    ReasoningStrategyConfig,
    ReasoningStrategyType,
    ReasoningTrace,
)

# ═══════════════════════════════════════════════════════════════════════
# Enums
# ═══════════════════════════════════════════════════════════════════════


class TestReasoningDomain:
    def test_values(self) -> None:
        assert ReasoningDomain.SYSTEM.value == "SYSTEM"
        assert ReasoningDomain.ENERGY.value == "ENERGY"
        assert ReasoningDomain.MAINTENANCE.value == "MAINTENANCE"
        assert ReasoningDomain.OPERATIONS.value == "OPERATIONS"
        assert ReasoningDomain.CUSTOMER.value == "CUSTOMER"
        assert ReasoningDomain.SAFETY.value == "SAFETY"
        assert ReasoningDomain.COMPLIANCE.value == "COMPLIANCE"
        assert ReasoningDomain.WORKFLOW.value == "WORKFLOW"
        assert ReasoningDomain.PLANNING.value == "PLANNING"

    def test_unique_values(self) -> None:
        values = [e.value for e in ReasoningDomain]
        assert len(values) == len(set(values))

    def test_count(self) -> None:
        assert len(ReasoningDomain) == 9


class TestReasoningStatus:
    def test_values(self) -> None:
        assert ReasoningStatus.INITIALIZED.value == "INITIALIZED"
        assert ReasoningStatus.ANALYZING.value == "ANALYZING"
        assert ReasoningStatus.GENERATING_HYPOTHESES.value == "GENERATING_HYPOTHESES"
        assert ReasoningStatus.EVALUATING.value == "EVALUATING"
        assert ReasoningStatus.VALIDATED.value == "VALIDATED"
        assert ReasoningStatus.COMPLETED.value == "COMPLETED"
        assert ReasoningStatus.FAILED.value == "FAILED"

    def test_unique_values(self) -> None:
        values = [e.value for e in ReasoningStatus]
        assert len(values) == len(set(values))

    def test_count(self) -> None:
        assert len(ReasoningStatus) == 7


class TestReasoningStrategyType:
    def test_values(self) -> None:
        assert ReasoningStrategyType.RULE_BASED.value == "RULE_BASED"
        assert ReasoningStrategyType.EVIDENCE_BASED.value == "EVIDENCE_BASED"
        assert ReasoningStrategyType.HYPOTHESIS.value == "HYPOTHESIS"
        assert ReasoningStrategyType.CONSTRAINT.value == "CONSTRAINT"
        assert ReasoningStrategyType.MULTI_STEP.value == "MULTI_STEP"
        assert ReasoningStrategyType.HYBRID.value == "HYBRID"

    def test_unique_values(self) -> None:
        values = [e.value for e in ReasoningStrategyType]
        assert len(values) == len(set(values))

    def test_count(self) -> None:
        assert len(ReasoningStrategyType) == 6


class TestHypothesisStatus:
    def test_values(self) -> None:
        assert HypothesisStatus.PROPOSED.value == "PROPOSED"
        assert HypothesisStatus.SUPPORTED.value == "SUPPORTED"
        assert HypothesisStatus.CONTRADICTED.value == "CONTRADICTED"
        assert HypothesisStatus.VALIDATED.value == "VALIDATED"
        assert HypothesisStatus.REJECTED.value == "REJECTED"

    def test_unique_values(self) -> None:
        values = [e.value for e in HypothesisStatus]
        assert len(values) == len(set(values))

    def test_count(self) -> None:
        assert len(HypothesisStatus) == 5


class TestContradictionSeverity:
    def test_values(self) -> None:
        assert ContradictionSeverity.LOW.value == "LOW"
        assert ContradictionSeverity.MEDIUM.value == "MEDIUM"
        assert ContradictionSeverity.HIGH.value == "HIGH"
        assert ContradictionSeverity.CRITICAL.value == "CRITICAL"

    def test_unique_values(self) -> None:
        values = [e.value for e in ContradictionSeverity]
        assert len(values) == len(set(values))

    def test_count(self) -> None:
        assert len(ContradictionSeverity) == 4


class TestContradictionResolutionStatus:
    def test_values(self) -> None:
        assert ContradictionResolutionStatus.UNRESOLVED.value == "UNRESOLVED"
        assert ContradictionResolutionStatus.INVESTIGATING.value == "INVESTIGATING"
        assert ContradictionResolutionStatus.RESOLVED.value == "RESOLVED"
        assert ContradictionResolutionStatus.DISMISSED.value == "DISMISSED"

    def test_unique_values(self) -> None:
        values = [e.value for e in ContradictionResolutionStatus]
        assert len(values) == len(set(values))


# ═══════════════════════════════════════════════════════════════════════
# ReasoningRequest
# ═══════════════════════════════════════════════════════════════════════


class TestReasoningRequest:
    def test_default_request(self) -> None:
        eid = uuid.uuid4()
        req = ReasoningRequest(evidence_package_id=eid)
        assert req.evidence_package_id == eid
        assert req.domain == ReasoningDomain.SYSTEM
        assert req.strategy == ReasoningStrategyType.HYBRID
        assert req.context == {}
        assert req.metadata == {}

    def test_request_with_values(self) -> None:
        eid = uuid.uuid4()
        req = ReasoningRequest(
            evidence_package_id=eid,
            domain=ReasoningDomain.ENERGY,
            strategy=ReasoningStrategyType.EVIDENCE_BASED,
            context={"asset_id": "asset-1"},
            metadata={"source": "test"},
        )
        assert req.domain == ReasoningDomain.ENERGY
        assert req.strategy == ReasoningStrategyType.EVIDENCE_BASED
        assert req.context["asset_id"] == "asset-1"

    def test_request_requires_evidence_package_id(self) -> None:
        with pytest.raises(ValidationError):
            ReasoningRequest()

    def test_request_unique_ids(self) -> None:
        eid = uuid.uuid4()
        r1 = ReasoningRequest(evidence_package_id=eid)
        r2 = ReasoningRequest(evidence_package_id=eid)
        assert r1.request_id != r2.request_id


# ═══════════════════════════════════════════════════════════════════════
# ReasoningResult
# ═══════════════════════════════════════════════════════════════════════


class TestReasoningResult:
    def test_default_result(self) -> None:
        rid = uuid.uuid4()
        result = ReasoningResult(request_id=rid)
        assert result.request_id == rid
        assert result.decision is None
        assert result.paths == []
        assert result.hypotheses == []
        assert result.inferences == []
        assert result.contradictions == []
        assert result.confidence is None
        assert result.status == ReasoningStatus.INITIALIZED

    def test_result_requires_request_id(self) -> None:
        with pytest.raises(ValidationError):
            ReasoningResult()

    def test_result_roundtrip(self) -> None:
        rid = uuid.uuid4()
        result = ReasoningResult(
            request_id=rid,
            status=ReasoningStatus.COMPLETED,
        )
        assert result.status == ReasoningStatus.COMPLETED


# ═══════════════════════════════════════════════════════════════════════
# ReasoningDecision
# ═══════════════════════════════════════════════════════════════════════


class TestReasoningDecision:
    def test_default_decision(self) -> None:
        rid = uuid.uuid4()
        d = ReasoningDecision(result_id=rid)
        assert d.result_id == rid
        assert d.conclusion == ""
        assert d.reasoning_summary == ""
        assert d.confidence == 0.0
        assert d.selected_hypotheses == []
        assert d.rejected_hypotheses == []

    def test_decision_with_values(self) -> None:
        rid = uuid.uuid4()
        hid = uuid.uuid4()
        d = ReasoningDecision(
            result_id=rid,
            conclusion="The system is operating normally",
            reasoning_summary="Based on evidence analysis",
            confidence=0.85,
            selected_hypotheses=[hid],
        )
        assert d.conclusion == "The system is operating normally"
        assert d.confidence == 0.85
        assert hid in d.selected_hypotheses

    def test_decision_requires_result_id(self) -> None:
        with pytest.raises(ValidationError):
            ReasoningDecision()

    def test_decision_confidence_bounds(self) -> None:
        rid = uuid.uuid4()
        with pytest.raises(ValidationError):
            ReasoningDecision(result_id=rid, confidence=-0.1)
        with pytest.raises(ValidationError):
            ReasoningDecision(result_id=rid, confidence=1.1)


# ═══════════════════════════════════════════════════════════════════════
# ReasoningSession
# ═══════════════════════════════════════════════════════════════════════


class TestReasoningSession:
    def test_default_session(self) -> None:
        rid = uuid.uuid4()
        s = ReasoningSession(request_id=rid)
        assert s.request_id == rid
        assert s.domain == ReasoningDomain.SYSTEM
        assert s.status == ReasoningStatus.INITIALIZED
        assert s.completed_at is None

    def test_session_with_values(self) -> None:
        rid = uuid.uuid4()
        now = datetime.now(UTC)
        s = ReasoningSession(
            request_id=rid,
            domain=ReasoningDomain.ENERGY,
            status=ReasoningStatus.COMPLETED,
            completed_at=now,
            statistics={"duration_ms": 150},
        )
        assert s.status == ReasoningStatus.COMPLETED
        assert s.completed_at == now
        assert s.statistics["duration_ms"] == 150

    def test_session_requires_request_id(self) -> None:
        with pytest.raises(ValidationError):
            ReasoningSession()


# ═══════════════════════════════════════════════════════════════════════
# ReasoningContext
# ═══════════════════════════════════════════════════════════════════════


class TestReasoningContext:
    def test_default_context(self) -> None:
        c = ReasoningContext()
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
        c = ReasoningContext(
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
        c = ReasoningContext()
        assert c.context_id is not None


# ═══════════════════════════════════════════════════════════════════════
# ReasoningMetadata
# ═══════════════════════════════════════════════════════════════════════


class TestReasoningMetadata:
    def test_default_metadata(self) -> None:
        m = ReasoningMetadata()
        assert m.title == ""
        assert m.tags == []
        assert m.version == "1.0.0"

    def test_metadata_with_values(self) -> None:
        m = ReasoningMetadata(
            title="Energy Analysis",
            description="Analysis of energy consumption",
            tags=["energy", "optimization"],
            category="analysis",
            source="energy-service",
        )
        assert m.title == "Energy Analysis"
        assert len(m.tags) == 2
        assert m.source == "energy-service"


# ═══════════════════════════════════════════════════════════════════════
# ReasoningConfidence
# ═══════════════════════════════════════════════════════════════════════


class TestReasoningConfidence:
    def test_default_confidence(self) -> None:
        c = ReasoningConfidence()
        assert c.overall_confidence == 0.0
        assert c.evidence_quality == 0.0
        assert c.hypothesis_strength == 0.0
        assert c.inference_validity == 0.0
        assert c.contradiction_resolution == 0.0

    def test_confidence_with_values(self) -> None:
        c = ReasoningConfidence(
            overall_confidence=0.85,
            evidence_quality=0.9,
            hypothesis_strength=0.8,
            inference_validity=0.85,
            contradiction_resolution=0.75,
        )
        assert c.overall_confidence == 0.85
        assert c.inference_validity == 0.85

    def test_confidence_bounds(self) -> None:
        with pytest.raises(ValidationError):
            ReasoningConfidence(overall_confidence=-0.1)
        with pytest.raises(ValidationError):
            ReasoningConfidence(overall_confidence=1.1)


# ═══════════════════════════════════════════════════════════════════════
# ReasoningHealth
# ═══════════════════════════════════════════════════════════════════════


class TestReasoningHealth:
    def test_default_health(self) -> None:
        h = ReasoningHealth()
        assert h.overall_status == "UNKNOWN"
        assert h.reasoning_count == 0
        assert h.error_count == 0
        assert h.uptime_seconds >= 0.0

    def test_health_with_values(self) -> None:
        h = ReasoningHealth(
            overall_status="HEALTHY",
            reasoning_count=10,
            coordinator_status="HEALTHY",
            hypothesis_generator_status="HEALTHY",
            inference_engine_status="DEGRADED",
        )
        assert h.overall_status == "HEALTHY"
        assert h.inference_engine_status == "DEGRADED"

    def test_health_counts_non_negative(self) -> None:
        with pytest.raises(ValidationError):
            ReasoningHealth(error_count=-1)


# ═══════════════════════════════════════════════════════════════════════
# ReasoningMetrics
# ═══════════════════════════════════════════════════════════════════════


class TestReasoningMetrics:
    def test_default_metrics(self) -> None:
        m = ReasoningMetrics()
        assert m.reasoning_total == 0
        assert m.hypotheses_total == 0
        assert m.inferences_total == 0
        assert m.contradictions_total == 0
        assert m.decisions_total == 0

    def test_metrics_with_values(self) -> None:
        m = ReasoningMetrics(
            reasoning_total=10,
            hypotheses_total=25,
            inferences_total=50,
            contradictions_total=3,
            decisions_total=8,
            hypotheses_per_domain={"ENERGY": 15},
        )
        assert m.hypotheses_total == 25
        assert m.hypotheses_per_domain["ENERGY"] == 15

    def test_metrics_non_negative(self) -> None:
        with pytest.raises(ValidationError):
            ReasoningMetrics(reasoning_total=-1)


# ═══════════════════════════════════════════════════════════════════════
# ReasoningTrace
# ═══════════════════════════════════════════════════════════════════════


class TestReasoningTrace:
    def test_default_trace(self) -> None:
        t = ReasoningTrace()
        assert t.stage_name == ""
        assert t.success is True
        assert t.warnings == []
        assert t.errors == []
        assert t.duration_ms is None

    def test_trace_with_values(self) -> None:
        now = datetime.now(UTC)
        t = ReasoningTrace(
            stage_name="HYPOTHESIS_GENERATION",
            operation="reason",
            reasoning_id="reasoning-1",
            correlation_id="corr-1",
            started_at=now,
            completed_at=now,
            duration_ms=42.5,
            success=True,
        )
        assert t.stage_name == "HYPOTHESIS_GENERATION"
        assert t.duration_ms == 42.5
        assert t.success is True

    def test_trace_with_warnings(self) -> None:
        t = ReasoningTrace(
            stage_name="VALIDATION",
            operation="validate",
            reasoning_id="r-1",
            success=False,
            warnings=["Missing evidence"],
            errors=["Validation failed"],
        )
        assert len(t.warnings) == 1
        assert len(t.errors) == 1


# ═══════════════════════════════════════════════════════════════════════
# ReasoningStep
# ═══════════════════════════════════════════════════════════════════════


class TestReasoningStep:
    def test_default_step(self) -> None:
        pid = uuid.uuid4()
        s = ReasoningStep(path_id=pid)
        assert s.path_id == pid
        assert s.step_type == ""
        assert s.inputs == []
        assert s.outputs == []
        assert s.confidence == 0.0

    def test_step_with_values(self) -> None:
        pid = uuid.uuid4()
        s = ReasoningStep(
            path_id=pid,
            step_type="deduction",
            description="Deduced from observed patterns",
            inputs=["evidence-1", "evidence-2"],
            outputs=["conclusion-1"],
            confidence=0.9,
        )
        assert s.step_type == "deduction"
        assert len(s.inputs) == 2
        assert s.confidence == 0.9

    def test_step_requires_path_id(self) -> None:
        with pytest.raises(ValidationError):
            ReasoningStep()


# ═══════════════════════════════════════════════════════════════════════
# ReasoningPath
# ═══════════════════════════════════════════════════════════════════════


class TestReasoningPath:
    def test_default_path(self) -> None:
        rid = uuid.uuid4()
        p = ReasoningPath(request_id=rid)
        assert p.request_id == rid
        assert p.strategy == ReasoningStrategyType.HYBRID
        assert p.steps == []
        assert p.is_active is True
        assert p.confidence == 0.0

    def test_path_with_values(self) -> None:
        rid = uuid.uuid4()
        pid = uuid.uuid4()
        step = ReasoningStep(path_id=pid, step_type="deduction", description="First step")
        p = ReasoningPath(
            request_id=rid,
            strategy=ReasoningStrategyType.EVIDENCE_BASED,
            steps=[step],
            is_active=True,
            confidence=0.75,
        )
        assert p.strategy == ReasoningStrategyType.EVIDENCE_BASED
        assert len(p.steps) == 1
        assert p.confidence == 0.75

    def test_path_requires_request_id(self) -> None:
        with pytest.raises(ValidationError):
            ReasoningPath()


# ═══════════════════════════════════════════════════════════════════════
# Hypothesis
# ═══════════════════════════════════════════════════════════════════════


class TestHypothesis:
    def test_default_hypothesis(self) -> None:
        h = Hypothesis()
        assert h.description == ""
        assert h.supporting_evidence == []
        assert h.contradicting_evidence == []
        assert h.confidence == 0.0
        assert h.priority == 0
        assert h.status == HypothesisStatus.PROPOSED

    def test_hypothesis_with_values(self) -> None:
        eid1 = uuid.uuid4()
        eid2 = uuid.uuid4()
        h = Hypothesis(
            description="The temperature sensor is malfunctioning",
            supporting_evidence=[eid1],
            contradicting_evidence=[eid2],
            confidence=0.75,
            priority=5,
            status=HypothesisStatus.SUPPORTED,
        )
        assert h.description == "The temperature sensor is malfunctioning"
        assert len(h.supporting_evidence) == 1
        assert h.confidence == 0.75
        assert h.priority == 5
        assert h.status == HypothesisStatus.SUPPORTED

    def test_hypothesis_confidence_bounds(self) -> None:
        with pytest.raises(ValidationError):
            Hypothesis(confidence=-0.1)
        with pytest.raises(ValidationError):
            Hypothesis(confidence=1.1)

    def test_hypothesis_priority_non_negative(self) -> None:
        with pytest.raises(ValidationError):
            Hypothesis(priority=-1)


# ═══════════════════════════════════════════════════════════════════════
# HypothesisSet
# ═══════════════════════════════════════════════════════════════════════


class TestHypothesisSet:
    def test_default_hypothesis_set(self) -> None:
        rid = uuid.uuid4()
        hs = HypothesisSet(request_id=rid)
        assert hs.request_id == rid
        assert hs.hypotheses == []
        assert hs.domain == ReasoningDomain.SYSTEM
        assert hs.description == ""

    def test_hypothesis_set_with_values(self) -> None:
        rid = uuid.uuid4()
        h1 = Hypothesis(description="Hypothesis 1")
        h2 = Hypothesis(description="Hypothesis 2")
        hs = HypothesisSet(
            request_id=rid,
            hypotheses=[h1, h2],
            domain=ReasoningDomain.ENERGY,
            description="Energy-related hypotheses",
        )
        assert len(hs.hypotheses) == 2
        assert hs.domain == ReasoningDomain.ENERGY
        assert hs.description == "Energy-related hypotheses"

    def test_hypothesis_set_requires_request_id(self) -> None:
        with pytest.raises(ValidationError):
            HypothesisSet()


# ═══════════════════════════════════════════════════════════════════════
# Inference
# ═══════════════════════════════════════════════════════════════════════


class TestInference:
    def test_default_inference(self) -> None:
        inf = Inference()
        assert inf.premise == ""
        assert inf.conclusion == ""
        assert inf.confidence == 0.0
        assert inf.inference_type == ""

    def test_inference_with_values(self) -> None:
        hid = uuid.uuid4()
        inf = Inference(
            hypothesis_id=hid,
            rule_id="rule-1",
            premise="If temperature > 100, then alert",
            conclusion="Alert should be raised",
            confidence=0.9,
            inference_type="deductive",
        )
        assert inf.hypothesis_id == hid
        assert inf.rule_id == "rule-1"
        assert inf.confidence == 0.9
        assert inf.inference_type == "deductive"

    def test_inference_confidence_bounds(self) -> None:
        with pytest.raises(ValidationError):
            Inference(confidence=-0.1)
        with pytest.raises(ValidationError):
            Inference(confidence=1.1)


# ═══════════════════════════════════════════════════════════════════════
# InferenceChain
# ═══════════════════════════════════════════════════════════════════════


class TestInferenceChain:
    def test_default_chain(self) -> None:
        rid = uuid.uuid4()
        ic = InferenceChain(request_id=rid)
        assert ic.request_id == rid
        assert ic.inferences == []
        assert ic.end_conclusion == ""
        assert ic.confidence == 0.0

    def test_chain_with_values(self) -> None:
        rid = uuid.uuid4()
        inf1 = Inference(premise="A", conclusion="B", confidence=0.8)
        inf2 = Inference(premise="B", conclusion="C", confidence=0.9)
        ic = InferenceChain(
            request_id=rid,
            inferences=[inf1, inf2],
            end_conclusion="C is true",
            confidence=0.85,
        )
        assert len(ic.inferences) == 2
        assert ic.end_conclusion == "C is true"
        assert ic.confidence == 0.85

    def test_chain_requires_request_id(self) -> None:
        with pytest.raises(ValidationError):
            InferenceChain()


# ═══════════════════════════════════════════════════════════════════════
# Contradiction
# ═══════════════════════════════════════════════════════════════════════


class TestContradiction:
    def test_default_contradiction(self) -> None:
        rid = uuid.uuid4()
        c = Contradiction(request_id=rid)
        assert c.request_id == rid
        assert c.conflicting_items == []
        assert c.severity == ContradictionSeverity.MEDIUM
        assert c.resolution_status == ContradictionResolutionStatus.UNRESOLVED
        assert c.description == ""
        assert c.resolved_at is None

    def test_contradiction_with_values(self) -> None:
        rid = uuid.uuid4()
        now = datetime.now(UTC)
        c = Contradiction(
            request_id=rid,
            conflicting_items=["hypothesis-1", "hypothesis-2"],
            severity=ContradictionSeverity.HIGH,
            resolution_status=ContradictionResolutionStatus.RESOLVED,
            description="Hypotheses 1 and 2 contradict each other",
            resolved_at=now,
        )
        assert len(c.conflicting_items) == 2
        assert c.severity == ContradictionSeverity.HIGH
        assert c.resolution_status == ContradictionResolutionStatus.RESOLVED
        assert c.resolved_at == now

    def test_contradiction_requires_request_id(self) -> None:
        with pytest.raises(ValidationError):
            Contradiction()


# ═══════════════════════════════════════════════════════════════════════
# ReasoningStrategyConfig
# ═══════════════════════════════════════════════════════════════════════


class TestReasoningStrategyConfig:
    def test_default_strategy(self) -> None:
        s = ReasoningStrategyConfig(strategy_type=ReasoningStrategyType.HYBRID)
        assert s.strategy_type == ReasoningStrategyType.HYBRID
        assert s.name == ""
        assert s.description == ""
        assert s.configuration == {}
        assert s.domain is None
        assert s.is_active is True
        assert s.priority == 0

    def test_strategy_with_values(self) -> None:
        s = ReasoningStrategyConfig(
            strategy_type=ReasoningStrategyType.RULE_BASED,
            name="Rule-Based Engine",
            description="Standard rule-based reasoning",
            configuration={"max_depth": 10},
            domain=ReasoningDomain.ENERGY,
            is_active=True,
            priority=5,
        )
        assert s.name == "Rule-Based Engine"
        assert s.configuration["max_depth"] == 10
        assert s.domain == ReasoningDomain.ENERGY
        assert s.priority == 5

    def test_strategy_requires_strategy_type(self) -> None:
        with pytest.raises(ValidationError):
            ReasoningStrategyConfig()
        assert s.strategy_type == ReasoningStrategyType.HYBRID
        assert s.name == ""
        assert s.description == ""
        assert s.configuration == {}
        assert s.domain is None
        assert s.is_active is True
        assert s.priority == 0

    def test_strategy_with_values(self) -> None:
        s = ReasoningStrategyConfig(
            strategy_type=ReasoningStrategyType.RULE_BASED,
            name="Rule-Based Engine",
            description="Standard rule-based reasoning",
            configuration={"max_depth": 10},
            domain=ReasoningDomain.ENERGY,
            is_active=True,
            priority=5,
        )
        assert s.name == "Rule-Based Engine"
        assert s.configuration["max_depth"] == 10
        assert s.domain == ReasoningDomain.ENERGY
        assert s.priority == 5

    def test_strategy_requires_strategy_type(self) -> None:
        with pytest.raises(ValidationError):
            ReasoningStrategyConfig()


# ═══════════════════════════════════════════════════════════════════════
# DTOs
# ═══════════════════════════════════════════════════════════════════════


class TestReasoningRequestDTO:
    def test_default_request_dto(self) -> None:
        eid = uuid.uuid4()
        dto = ReasoningRequestDTO(evidence_package_id=eid)
        assert dto.evidence_package_id == eid
        assert dto.domain == ReasoningDomain.SYSTEM
        assert dto.strategy == ReasoningStrategyType.HYBRID

    def test_request_dto_with_values(self) -> None:
        eid = uuid.uuid4()
        dto = ReasoningRequestDTO(
            evidence_package_id=eid,
            domain=ReasoningDomain.ENERGY,
            strategy=ReasoningStrategyType.RULE_BASED,
            context={"priority": "high"},
        )
        assert dto.domain == ReasoningDomain.ENERGY
        assert dto.context["priority"] == "high"

    def test_request_dto_requires_evidence_package_id(self) -> None:
        with pytest.raises(ValidationError):
            ReasoningRequestDTO()


class TestReasoningResponseDTO:
    def test_default_response_dto(self) -> None:
        rid = uuid.uuid4()
        req_id = uuid.uuid4()
        dto = ReasoningResponseDTO(result_id=rid, request_id=req_id)
        assert dto.result_id == rid
        assert dto.request_id == req_id
        assert dto.hypotheses_count == 0
        assert dto.status == ReasoningStatus.COMPLETED

    def test_response_dto_with_values(self) -> None:
        rid = uuid.uuid4()
        req_id = uuid.uuid4()
        dto = ReasoningResponseDTO(
            result_id=rid,
            request_id=req_id,
            hypotheses_count=5,
            inferences_count=10,
            contradictions_count=2,
            confidence=0.85,
            status=ReasoningStatus.COMPLETED,
            decision={"conclusion": "All clear"},
        )
        assert dto.hypotheses_count == 5
        assert dto.confidence == 0.85
        assert dto.decision["conclusion"] == "All clear"

    def test_response_dto_requires_ids(self) -> None:
        with pytest.raises(ValidationError):
            ReasoningResponseDTO()
        with pytest.raises(ValidationError):
            ReasoningResponseDTO(result_id=uuid.uuid4())
        with pytest.raises(ValidationError):
            ReasoningResponseDTO(request_id=uuid.uuid4())


class TestReasoningDecisionDTO:
    def test_default_decision_dto(self) -> None:
        dto = ReasoningDecisionDTO()
        assert dto.conclusion == ""
        assert dto.reasoning_summary == ""
        assert dto.confidence == 0.0
        assert dto.selected_hypotheses == []

    def test_decision_dto_with_values(self) -> None:
        dto = ReasoningDecisionDTO(
            conclusion="System OK",
            reasoning_summary="Evidence supports normal operation",
            confidence=0.85,
            selected_hypotheses=["Hypothesis A", "Hypothesis B"],
        )
        assert "System OK" in dto.conclusion
        assert len(dto.selected_hypotheses) == 2


# ═══════════════════════════════════════════════════════════════════════
# Events
# ═══════════════════════════════════════════════════════════════════════


class TestReasoningEvent:
    def test_base_event(self) -> None:
        e = ReasoningEvent(event_type="test.event")
        assert e.event_type == "test.event"
        assert e.reasoning_id == ""
        assert e.correlation_id == ""

    def test_reasoning_started(self) -> None:
        e = ReasoningStarted(
            reasoning_id="r-1",
            correlation_id="corr-1",
            domain="ENERGY",
            strategy="RULE_BASED",
        )
        assert e.event_type == "reasoning.started"
        assert e.domain == "ENERGY"
        assert e.strategy == "RULE_BASED"

    def test_hypothesis_generated(self) -> None:
        e = HypothesisGenerated(
            reasoning_id="r-1",
            hypothesis_id="h-1",
            hypothesis_count=5,
        )
        assert e.event_type == "reasoning.hypothesis_generated"
        assert e.hypothesis_id == "h-1"
        assert e.hypothesis_count == 5

    def test_inference_completed(self) -> None:
        e = InferenceCompleted(
            reasoning_id="r-1",
            inference_id="i-1",
            inference_type="deductive",
        )
        assert e.event_type == "reasoning.inference_completed"
        assert e.inference_id == "i-1"

    def test_contradiction_detected(self) -> None:
        e = ContradictionDetected(
            reasoning_id="r-1",
            contradiction_id="c-1",
            severity="HIGH",
        )
        assert e.event_type == "reasoning.contradiction_detected"
        assert e.severity == "HIGH"

    def test_reasoning_completed(self) -> None:
        e = ReasoningCompleted(
            reasoning_id="r-1",
            status="COMPLETED",
            result_id="res-1",
            duration_ms=150.5,
        )
        assert e.event_type == "reasoning.completed"
        assert e.status == "COMPLETED"
        assert e.duration_ms == 150.5
        assert e.result_id == "res-1"

    def test_event_inheritance(self) -> None:
        e = ReasoningStarted(reasoning_id="r-1")
        assert isinstance(e, ReasoningEvent)
        assert e.timestamp is not None


# ═══════════════════════════════════════════════════════════════════════
# Exceptions
# ═══════════════════════════════════════════════════════════════════════


class TestReasoningException:
    def test_base_exception(self) -> None:
        e = ReasoningException("base error")
        assert str(e) == "base error"
        assert isinstance(e, Exception)

    def test_hypothesis_exception(self) -> None:
        e = HypothesisException("hypothesis error")
        assert str(e) == "hypothesis error"
        assert isinstance(e, ReasoningException)

    def test_inference_exception(self) -> None:
        e = InferenceException("inference error")
        assert str(e) == "inference error"
        assert isinstance(e, ReasoningException)

    def test_contradiction_exception(self) -> None:
        e = ContradictionException("contradiction error")
        assert str(e) == "contradiction error"
        assert isinstance(e, ReasoningException)

    def test_default_messages(self) -> None:
        assert "reasoning error" in str(ReasoningException())
        assert "hypothesis error" in str(HypothesisException())
        assert "inference error" in str(InferenceException())
        assert "contradiction error" in str(ContradictionException())

    def test_exception_hierarchy(self) -> None:
        assert issubclass(HypothesisException, ReasoningException)
        assert issubclass(InferenceException, ReasoningException)
        assert issubclass(ContradictionException, ReasoningException)


# ═══════════════════════════════════════════════════════════════════════
# Model Relationships
# ═══════════════════════════════════════════════════════════════════════


class TestModelRelationships:
    def test_hypothesis_in_hypothesis_set(self) -> None:
        rid = uuid.uuid4()
        h1 = Hypothesis(description="H1", confidence=0.8)
        h2 = Hypothesis(description="H2", confidence=0.6)
        hs = HypothesisSet(request_id=rid, hypotheses=[h1, h2])
        assert len(hs.hypotheses) == 2
        assert hs.hypotheses[0].confidence == 0.8

    def test_inference_in_inference_chain(self) -> None:
        rid = uuid.uuid4()
        i1 = Inference(premise="A", conclusion="B")
        i2 = Inference(premise="B", conclusion="C")
        chain = InferenceChain(request_id=rid, inferences=[i1, i2])
        assert chain.inferences[0].premise == "A"
        assert chain.inferences[1].conclusion == "C"

    def test_step_in_path(self) -> None:
        rid = uuid.uuid4()
        pid = uuid.uuid4()
        step = ReasoningStep(path_id=pid, step_type="deduction")
        path = ReasoningPath(request_id=rid, steps=[step])
        assert path.steps[0].step_type == "deduction"

    def test_decision_in_result(self) -> None:
        rid = uuid.uuid4()
        did = uuid.uuid4()
        decision = ReasoningDecision(
            result_id=did,
            conclusion="System OK",
            reasoning_summary="Analysis complete",
        )
        result = ReasoningResult(
            request_id=rid,
            decision=decision,
            status=ReasoningStatus.COMPLETED,
        )
        assert result.decision is not None
        assert result.decision.conclusion == "System OK"
        assert result.decision.reasoning_summary == "Analysis complete"

    def test_contradiction_in_result(self) -> None:
        rid = uuid.uuid4()
        c = Contradiction(
            request_id=rid,
            description="Test contradiction",
            severity=ContradictionSeverity.LOW,
        )
        result = ReasoningResult(
            request_id=rid,
            contradictions=[c],
        )
        assert len(result.contradictions) == 1
        assert result.contradictions[0].severity == ContradictionSeverity.LOW

    def test_dto_to_model_flow(self) -> None:
        eid = uuid.uuid4()
        dto = ReasoningRequestDTO(
            evidence_package_id=eid,
            domain=ReasoningDomain.ENERGY,
            strategy=ReasoningStrategyType.RULE_BASED,
        )
        req = ReasoningRequest(
            evidence_package_id=dto.evidence_package_id,
            domain=dto.domain,
            strategy=dto.strategy,
        )
        assert req.evidence_package_id == eid
        assert req.domain == ReasoningDomain.ENERGY
        assert req.strategy == ReasoningStrategyType.RULE_BASED


# ═══════════════════════════════════════════════════════════════════════
# Cross-Module Validation
# ═══════════════════════════════════════════════════════════════════════


class TestContextValidation:
    def test_context_with_all_fields(self) -> None:
        c = ReasoningContext(
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
    def test_reasoning_domain_consistency(self) -> None:
        domains = [
            ReasoningDomain.SYSTEM,
            ReasoningDomain.ENERGY,
            ReasoningDomain.MAINTENANCE,
            ReasoningDomain.OPERATIONS,
            ReasoningDomain.CUSTOMER,
            ReasoningDomain.SAFETY,
            ReasoningDomain.COMPLIANCE,
            ReasoningDomain.WORKFLOW,
            ReasoningDomain.PLANNING,
        ]
        assert len(domains) == 9


class TestStrategyValidation:
    def test_strategy_types_consistency(self) -> None:
        strategies = [
            ReasoningStrategyType.RULE_BASED,
            ReasoningStrategyType.EVIDENCE_BASED,
            ReasoningStrategyType.HYPOTHESIS,
            ReasoningStrategyType.CONSTRAINT,
            ReasoningStrategyType.MULTI_STEP,
            ReasoningStrategyType.HYBRID,
        ]
        assert len(strategies) == 6


class TestHypothesisValidation:
    def test_hypothesis_with_evidence(self) -> None:
        supporting = [uuid.uuid4(), uuid.uuid4()]
        contradicting = [uuid.uuid4()]
        h = Hypothesis(
            description="Test hypothesis",
            supporting_evidence=supporting,
            contradicting_evidence=contradicting,
            confidence=0.8,
            priority=3,
        )
        assert len(h.supporting_evidence) == 2
        assert len(h.contradicting_evidence) == 1
        assert h.supporting_evidence != h.contradicting_evidence

    def test_hypothesis_status_transition(self) -> None:
        h = Hypothesis(status=HypothesisStatus.PROPOSED)
        assert h.status == HypothesisStatus.PROPOSED
        h.status = HypothesisStatus.SUPPORTED
        assert h.status == HypothesisStatus.SUPPORTED
        h.status = HypothesisStatus.VALIDATED
        assert h.status == HypothesisStatus.VALIDATED


class TestInferenceChainValidation:
    def test_inference_chain_ordering(self) -> None:
        rid = uuid.uuid4()
        inferences = [
            Inference(premise="A", conclusion="B", confidence=0.9),
            Inference(premise="B", conclusion="C", confidence=0.8),
            Inference(premise="C", conclusion="D", confidence=0.7),
        ]
        chain = InferenceChain(
            request_id=rid,
            inferences=inferences,
            start_hypothesis_id=uuid.uuid4(),
            end_conclusion="D",
        )
        assert len(chain.inferences) == 3
        assert chain.inferences[0].premise == "A"
        assert chain.inferences[-1].conclusion == "D"
        assert chain.end_conclusion == "D"


class TestContradictionValidation:
    def test_contradiction_severity_mapping(self) -> None:
        rid = uuid.uuid4()
        c = Contradiction(
            request_id=rid,
            conflicting_items=["h-1", "h-2"],
            severity=ContradictionSeverity.CRITICAL,
            resolution_status=ContradictionResolutionStatus.UNRESOLVED,
        )
        assert c.severity == ContradictionSeverity.CRITICAL
        assert not c.resolved_at

    def test_contradiction_resolution(self) -> None:
        rid = uuid.uuid4()
        now = datetime.now(UTC)
        c = Contradiction(
            request_id=rid,
            conflicting_items=["h-1", "h-2"],
            severity=ContradictionSeverity.HIGH,
            resolution_status=ContradictionResolutionStatus.RESOLVED,
            resolved_at=now,
        )
        assert c.resolution_status == ContradictionResolutionStatus.RESOLVED
        assert c.resolved_at == now


class TestReasoningPathValidation:
    def test_path_with_multiple_steps(self) -> None:
        rid = uuid.uuid4()
        pid = uuid.uuid4()
        steps = [
            ReasoningStep(path_id=pid, step_type="observation", description="Observed data"),
            ReasoningStep(path_id=pid, step_type="deduction", description="Drew conclusion"),
            ReasoningStep(path_id=pid, step_type="verification", description="Verified result"),
        ]
        path = ReasoningPath(
            request_id=rid,
            strategy=ReasoningStrategyType.MULTI_STEP,
            steps=steps,
            confidence=0.85,
        )
        assert len(path.steps) == 3
        assert path.steps[0].step_type == "observation"
        assert path.steps[-1].step_type == "verification"
        assert path.confidence == 0.85
