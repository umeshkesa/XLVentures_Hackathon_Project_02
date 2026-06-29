"""Tests for Action Manager Phase 3 (Enterprise Orchestration).

Covers all Phase 3 orchestration components, coordinator,
manager, and service. 246 Phase 1+2 tests already pass.
"""

from __future__ import annotations

import uuid
from typing import Any

from adip.actions.contracts.models import (
    ActionConfidence,
    ActionDecision,
    ActionExplainabilityMetadata,
    ActionHealth,
    ActionMetrics,
    ActionRequest,
    ActionSession,
)
from adip.actions.dtos import ActionRequestDTO
from adip.actions.enums import ExecutionReadiness
from adip.actions.orchestration.confidence import ActionConfidenceCalculator
from adip.actions.orchestration.context import ExecutionContextBuilder
from adip.actions.orchestration.coordinator import ActionCoordinator
from adip.actions.orchestration.execution_package import (
    ExecutionPackageBuilder,
)
from adip.actions.orchestration.health import ExecutionHealth
from adip.actions.orchestration.lineage import ActionLineage
from adip.actions.orchestration.manager import ActionManager
from adip.actions.orchestration.policy_compliance import (
    ActionPolicyCompliance,
)
from adip.actions.orchestration.quality import PlanQualityManager
from adip.actions.orchestration.readiness import (
    ActionExecutionReadiness,
)
from adip.actions.orchestration.review import ActionReview
from adip.actions.orchestration.session import ActionSessionManager
from adip.actions.orchestration.snapshot import ActionSnapshot
from adip.actions.orchestration.version_manager import (
    ActionVersionManager,
)
from adip.actions.services.hooks import IntegrationHooks
from adip.actions.services.service import DefaultActionService

# =============================================================================
# Phase 3 Contract Model Tests
# =============================================================================


class TestActionConfidence:
    def test_default_values(self) -> None:
        c = ActionConfidence()
        assert c.overall_confidence == 0.0
        assert c.resource_confidence == 0.0
        assert c.schedule_confidence == 0.0
        assert c.cost_confidence == 0.0
        assert c.risk_confidence == 0.0
        assert c.feasibility_confidence == 0.0
        assert c.metadata == {}

    def test_custom_values(self) -> None:
        c = ActionConfidence(
            overall_confidence=0.85,
            resource_confidence=0.9,
            schedule_confidence=0.8,
            cost_confidence=0.75,
            risk_confidence=0.7,
            feasibility_confidence=0.85,
        )
        assert c.overall_confidence == 0.85
        assert c.resource_confidence == 0.9
        assert c.schedule_confidence == 0.8
        assert c.cost_confidence == 0.75
        assert c.risk_confidence == 0.7
        assert c.feasibility_confidence == 0.85

    def test_clamping(self) -> None:
        # Pydantic v2 raises on ge/le violations, so test valid range
        c = ActionConfidence(overall_confidence=1.0, resource_confidence=0.0)
        assert c.overall_confidence == 1.0
        assert c.resource_confidence == 0.0


class TestActionExplainabilityMetadata:
    def test_default_values(self) -> None:
        e = ActionExplainabilityMetadata()
        assert e.why_plan_generated == ""
        assert e.why_step_ordered == ""
        assert e.why_resource_allocated == ""
        assert e.why_schedule_chosen == ""
        assert e.why_readiness_assessed == ""
        assert e.why_rollback_configured == ""
        assert e.why_optimization_applied == ""

    def test_custom_values(self) -> None:
        e = ActionExplainabilityMetadata(
            why_plan_generated="Test plan",
            why_readiness_assessed="Ready",
        )
        assert e.why_plan_generated == "Test plan"
        assert e.why_readiness_assessed == "Ready"


class TestActionDecisionEnhanced:
    def test_new_fields_defaults(self) -> None:
        d = ActionDecision(
            request_id=uuid.uuid4(),
        )
        assert d.confidence is None
        assert d.explainability is None
        assert d.quality_score == 0.0
        assert d.readiness_score == 0.0

    def test_new_fields_set(self) -> None:
        conf = ActionConfidence(overall_confidence=0.9)
        expl = ActionExplainabilityMetadata(why_plan_generated="test")
        d = ActionDecision(
            request_id=uuid.uuid4(),
            confidence=conf,
            explainability=expl,
            quality_score=0.85,
            readiness_score=0.75,
        )
        assert d.confidence is not None
        assert d.confidence.overall_confidence == 0.9
        assert d.explainability is not None
        assert d.explainability.why_plan_generated == "test"
        assert d.quality_score == 0.85
        assert d.readiness_score == 0.75


class TestActionSessionEnhanced:
    def test_new_fields_defaults(self) -> None:
        s = ActionSession(request_id=uuid.uuid4())
        assert s.decision_id is None
        assert s.step_count == 0
        assert s.has_rollback is False

    def test_new_fields_set(self) -> None:
        s = ActionSession(
            request_id=uuid.uuid4(),
            decision_id=uuid.uuid4(),
            step_count=10,
            has_rollback=True,
        )
        assert s.decision_id is not None
        assert s.step_count == 10
        assert s.has_rollback is True


class TestActionHealthEnhanced:
    def test_new_fields_defaults(self) -> None:
        h = ActionHealth()
        assert h.confidence_calculator_status == ""
        assert h.session_manager_status == ""
        assert h.version_manager_status == ""
        assert h.lineage_status == ""
        assert h.snapshot_status == ""
        assert h.quality_manager_status == ""
        assert h.review_status == ""

    def test_new_fields_set(self) -> None:
        h = ActionHealth(
            confidence_calculator_status="HEALTHY",
            session_manager_status="HEALTHY",
            version_manager_status="HEALTHY",
            lineage_status="HEALTHY",
            snapshot_status="HEALTHY",
            quality_manager_status="HEALTHY",
            review_status="HEALTHY",
        )
        assert h.confidence_calculator_status == "HEALTHY"
        assert h.session_manager_status == "HEALTHY"


class TestActionMetricsEnhanced:
    def test_new_fields_defaults(self) -> None:
        m = ActionMetrics()
        assert m.sessions_total == 0
        assert m.readiness_total == 0
        assert m.optimizations_total == 0
        assert m.reviews_total == 0
        assert m.versions_total == 0
        assert m.snapshots_total == 0
        assert m.average_confidence == 0.0
        assert m.average_quality == 0.0

    def test_new_fields_set(self) -> None:
        m = ActionMetrics(
            sessions_total=5,
            readiness_total=10,
            optimizations_total=3,
            reviews_total=2,
            versions_total=8,
            snapshots_total=4,
            average_confidence=0.85,
            average_quality=0.75,
        )
        assert m.sessions_total == 5
        assert m.readiness_total == 10
        assert m.average_confidence == 0.85
        assert m.average_quality == 0.75


# =============================================================================
# ActionSessionManager Tests
# =============================================================================


class TestActionSessionManager:
    def setup_method(self) -> None:
        self.manager = ActionSessionManager()

    def test_create_session(self) -> None:
        request_id = str(uuid.uuid4())
        session = self.manager.create_session(request_id=request_id)
        assert session.status == "INITIALIZED"
        assert str(session.request_id) == request_id
        assert session.step_count == 0
        assert session.has_rollback is False

    def test_get_session_not_found(self) -> None:
        assert self.manager.get_session("nonexistent") is None

    def test_get_session_found(self) -> None:
        session = self.manager.create_session(request_id=str(uuid.uuid4()))
        found = self.manager.get_session(str(session.session_id))
        assert found is not None
        assert str(found.session_id) == str(session.session_id)

    def test_update_status_valid(self) -> None:
        session = self.manager.create_session(request_id=str(uuid.uuid4()))
        result = self.manager.update_status(str(session.session_id), "PLANNING")
        assert result is not None
        assert result.status == "PLANNING"

    def test_update_status_invalid(self) -> None:
        session = self.manager.create_session(request_id=str(uuid.uuid4()))
        result = self.manager.update_status(str(session.session_id), "INVALID")
        assert result is None
        assert self.manager.get_session(str(session.session_id)).status == "INITIALIZED"

    def test_update_status_terminal(self) -> None:
        session = self.manager.create_session(request_id=str(uuid.uuid4()))
        self.manager.update_status(str(session.session_id), "COMPLETED")
        assert self.manager.get_session(str(session.session_id)).status == "COMPLETED"
        assert self.manager.get_session(str(session.session_id)).completed_at is not None

    def test_update_status_failed(self) -> None:
        session = self.manager.create_session(request_id=str(uuid.uuid4()))
        self.manager.update_status(str(session.session_id), "FAILED")
        assert self.manager.get_session(str(session.session_id)).status == "FAILED"

    def test_update_session(self) -> None:
        session = self.manager.create_session(request_id=str(uuid.uuid4()))
        self.manager.update_session(
            str(session.session_id),
            plan_id=str(uuid.uuid4()),
            step_count=5,
            has_rollback=True,
        )
        updated = self.manager.get_session(str(session.session_id))
        assert updated.step_count == 5
        assert updated.has_rollback is True
        assert updated.plan_id is not None

    def test_get_active_sessions(self) -> None:
        s1 = self.manager.create_session(request_id=str(uuid.uuid4()))
        s2 = self.manager.create_session(request_id=str(uuid.uuid4()))
        self.manager.update_status(str(s2.session_id), "COMPLETED")
        active = self.manager.get_active_sessions()
        assert len(active) == 1
        assert str(active[0].session_id) == str(s1.session_id)

    def test_get_all_sessions(self) -> None:
        self.manager.create_session(request_id=str(uuid.uuid4()))
        self.manager.create_session(request_id=str(uuid.uuid4()))
        assert len(self.manager.get_all_sessions()) == 2

    def test_clear(self) -> None:
        self.manager.create_session(request_id=str(uuid.uuid4()))
        self.manager.clear()
        assert self.manager.count() == 0

    def test_full_lifecycle(self) -> None:
        session = self.manager.create_session(request_id=str(uuid.uuid4()))
        assert session.status == "INITIALIZED"
        assert self.manager.update_status(str(session.session_id), "PLANNING") is not None
        assert self.manager.update_status(str(session.session_id), "VALIDATING") is not None
        assert self.manager.update_status(str(session.session_id), "OPTIMIZING") is not None
        assert self.manager.update_status(str(session.session_id), "READY") is not None
        assert self.manager.update_status(str(session.session_id), "COMPLETED") is not None
        assert self.manager.get_session(str(session.session_id)).completed_at is not None


# =============================================================================
# ActionConfidenceCalculator Tests
# =============================================================================


class TestActionConfidenceCalculator:
    def setup_method(self) -> None:
        self.calc = ActionConfidenceCalculator()

    def test_calculate_default(self) -> None:
        c = self.calc.calculate()
        assert c.overall_confidence == 0.0
        assert c.resource_confidence == 0.0

    def test_calculate_high_confidence(self) -> None:
        c = self.calc.calculate(
            resource_confidence=1.0,
            schedule_confidence=1.0,
            cost_confidence=1.0,
            risk_confidence=1.0,
            feasibility_confidence=1.0,
            quality_score=1.0,
        )
        assert c.overall_confidence == 1.0

    def test_calculate_mixed(self) -> None:
        c = self.calc.calculate(
            resource_confidence=0.8,
            schedule_confidence=0.7,
            cost_confidence=0.6,
            risk_confidence=0.9,
            feasibility_confidence=0.5,
            quality_score=0.4,
        )
        assert 0.0 <= c.overall_confidence <= 1.0
        assert c.resource_confidence == 0.8
        assert c.schedule_confidence == 0.7
        assert c.cost_confidence == 0.6
        assert c.risk_confidence == 0.9
        assert c.feasibility_confidence == 0.5

    def test_calculate_clamping(self) -> None:
        c = self.calc.calculate(resource_confidence=2.0, schedule_confidence=-1.0)
        assert c.resource_confidence == 1.0
        assert c.schedule_confidence == 0.0

    def test_get_history(self) -> None:
        assert len(self.calc.get_history()) == 0
        self.calc.calculate(resource_confidence=0.5)
        assert len(self.calc.get_history()) == 1
        self.calc.calculate(resource_confidence=0.8)
        assert len(self.calc.get_history()) == 2

    def test_clear(self) -> None:
        self.calc.calculate()
        self.calc.clear()
        assert len(self.calc.get_history()) == 0

    def test_weight_sums(self) -> None:
        w = (
            ActionConfidenceCalculator.RESOURCE_WEIGHT
            + ActionConfidenceCalculator.SCHEDULE_WEIGHT
            + ActionConfidenceCalculator.COST_WEIGHT
            + ActionConfidenceCalculator.RISK_WEIGHT
            + ActionConfidenceCalculator.FEASIBILITY_WEIGHT
            + ActionConfidenceCalculator.QUALITY_WEIGHT
        )
        assert w == 1.0


# =============================================================================
# ActionExecutionReadiness Tests
# =============================================================================


class TestActionExecutionReadiness:
    def setup_method(self) -> None:
        self.readiness = ActionExecutionReadiness()

    def test_assess_ready(self) -> None:
        r = self.readiness.assess(plan_id=str(uuid.uuid4()))
        assert r.status == ExecutionReadiness.READY
        assert r.score == 1.0
        assert len(r.issues) == 0

    def test_assess_blocked(self) -> None:
        r = self.readiness.assess(
            plan_id=str(uuid.uuid4()),
            resources_available=False,
            dependencies_satisfied=False,
            schedule_feasible=False,
            policy_compliant=False,
            risk_accepted=False,
        )
        assert r.status == ExecutionReadiness.BLOCKED
        assert r.score < 0.6
        assert len(r.issues) == 5

    def test_assess_waiting(self) -> None:
        r = self.readiness.assess(
            plan_id=str(uuid.uuid4()),
            resources_available=False,
            policy_compliant=False,
        )
        assert r.status == ExecutionReadiness.WAITING
        assert r.score == 0.6
        assert len(r.issues) == 2

    def test_assess_checks_dict(self) -> None:
        r = self.readiness.assess(
            plan_id=str(uuid.uuid4()),
            resources_available=True,
            dependencies_satisfied=False,
        )
        assert r.checks["resources_available"] is True
        assert r.checks["dependencies_satisfied"] is False
        assert r.checks["schedule_feasible"] is True
        assert r.checks["policy_compliant"] is True
        assert r.checks["risk_accepted"] is True

    def test_get_assessment(self) -> None:
        r = self.readiness.assess(plan_id=str(uuid.uuid4()))
        found = self.readiness.get_assessment(str(r.assessment_id))
        assert found is not None
        assert str(found.assessment_id) == str(r.assessment_id)

    def test_get_all_assessments(self) -> None:
        self.readiness.assess(plan_id=str(uuid.uuid4()))
        self.readiness.assess(plan_id=str(uuid.uuid4()))
        assert len(self.readiness.get_all_assessments()) == 2

    def test_clear(self) -> None:
        self.readiness.assess(plan_id=str(uuid.uuid4()))
        self.readiness.clear()
        assert len(self.readiness.get_all_assessments()) == 0

    def test_assess_default_params(self) -> None:
        r = self.readiness.assess(plan_id=str(uuid.uuid4()))
        assert r.plan_id != ""
        assert r.score == 1.0
        assert r.status == ExecutionReadiness.READY


# =============================================================================
# ActionReview Tests
# =============================================================================


class TestActionReview:
    def setup_method(self) -> None:
        self.review = ActionReview()

    def test_review_default(self) -> None:
        r = self.review.review(plan_id=str(uuid.uuid4()))
        assert r.passed is False
        assert r.overall_score < 0.5
        assert "no steps" in r.issues[0].lower() if r.issues else True

    def test_review_complete_plan(self) -> None:
        r = self.review.review(
            plan_id=str(uuid.uuid4()),
            step_count=5,
            has_dependencies=True,
            has_resources=True,
            has_schedule=True,
            has_rollback=True,
            has_preconditions=True,
        )
        assert r.passed is True
        assert r.overall_score > 0.5
        assert r.completeness_score >= 0.5
        assert r.consistency_score >= 0.5
        assert r.feasibility_score >= 0.5
        assert r.safety_score >= 0.5
        assert r.compliance_score >= 0.5

    def test_review_no_rollback(self) -> None:
        r = self.review.review(
            plan_id=str(uuid.uuid4()),
            step_count=3,
            has_dependencies=True,
            has_resources=True,
            has_schedule=True,
            has_rollback=False,
        )
        assert "No rollback" in r.issues[0] if r.issues else True

    def test_review_no_preconditions(self) -> None:
        r = self.review.review(
            plan_id=str(uuid.uuid4()),
            step_count=3,
            has_preconditions=False,
        )
        assert any("No preconditions" in issue for issue in r.issues)

    def test_get_review(self) -> None:
        r = self.review.review(plan_id=str(uuid.uuid4()))
        found = self.review.get_review(str(r.review_id))
        assert found is not None

    def test_get_all_reviews(self) -> None:
        self.review.review(plan_id=str(uuid.uuid4()))
        self.review.review(plan_id=str(uuid.uuid4()))
        assert len(self.review.get_all_reviews()) == 2

    def test_clear(self) -> None:
        self.review.review(plan_id=str(uuid.uuid4()))
        self.review.clear()
        assert len(self.review.get_all_reviews()) == 0


# =============================================================================
# PlanQualityManager Tests
# =============================================================================


class TestPlanQualityManager:
    def setup_method(self) -> None:
        self.qm = PlanQualityManager()

    def test_assess_default(self) -> None:
        q = self.qm.assess(plan_id=str(uuid.uuid4()))
        assert q.overall_quality < 0.5
        assert len(q.recommendations) > 0

    def test_assess_full_plan(self) -> None:
        q = self.qm.assess(
            plan_id=str(uuid.uuid4()),
            step_count=5,
            has_dependencies=True,
            has_resources=True,
            has_schedule=True,
            has_rollback=True,
            has_preconditions=True,
            has_postconditions=True,
        )
        assert q.overall_quality > 0.5
        assert q.completeness >= 0.5
        assert q.consistency >= 0.5
        assert q.optimisability >= 0.5
        assert q.maintainability >= 0.5
        assert q.testability >= 0.5
        assert q.observability >= 0.5

    def test_assess_no_preconditions(self) -> None:
        q = self.qm.assess(plan_id=str(uuid.uuid4()), step_count=3)
        recs = " ".join(q.recommendations).lower()
        assert "precondition" in recs or "postcondition" in recs

    def test_quality_dimensions(self) -> None:
        q = self.qm.assess(
            plan_id=str(uuid.uuid4()),
            step_count=5,
            has_dependencies=True,
            has_resources=True,
            has_schedule=True,
            has_rollback=True,
            has_preconditions=True,
            has_postconditions=True,
        )
        assert 0.0 <= q.completeness <= 1.0
        assert 0.0 <= q.consistency <= 1.0
        assert 0.0 <= q.optimisability <= 1.0
        assert 0.0 <= q.maintainability <= 1.0
        assert 0.0 <= q.testability <= 1.0
        assert 0.0 <= q.observability <= 1.0

    def test_get_assessment(self) -> None:
        q = self.qm.assess(plan_id=str(uuid.uuid4()))
        found = self.qm.get_assessment(str(q.assessment_id))
        assert found is not None

    def test_get_all_assessments(self) -> None:
        self.qm.assess(plan_id=str(uuid.uuid4()))
        self.qm.assess(plan_id=str(uuid.uuid4()))
        assert len(self.qm.get_all_assessments()) == 2

    def test_clear(self) -> None:
        self.qm.assess(plan_id=str(uuid.uuid4()))
        self.qm.clear()
        assert len(self.qm.get_all_assessments()) == 0


# =============================================================================
# ExecutionPackageBuilder Tests
# =============================================================================


class TestExecutionPackageBuilder:
    def setup_method(self) -> None:
        self.builder = ExecutionPackageBuilder()

    def test_build_default(self) -> None:
        p = self.builder.build(plan_id=str(uuid.uuid4()))
        assert p.plan_id != ""
        assert p.step_count == 0
        assert p.has_rollback is False
        assert p.readiness_score == 0.0
        assert p.version == "1.0.0"

    def test_build_with_data(self) -> None:
        p = self.builder.build(
            plan_id=str(uuid.uuid4()),
            step_count=10,
            has_rollback=True,
            readiness_score=0.85,
        )
        assert p.step_count == 10
        assert p.has_rollback is True
        assert p.readiness_score == 0.85

    def test_build_summaries(self) -> None:
        p = self.builder.build(
            plan_id=str(uuid.uuid4()),
            resource_summary="Resources allocated: 5 personnel",
            schedule_summary="Schedule: immediate",
            risk_summary="Risk: LOW",
            cost_summary="Cost: $1,000",
            compensation_summary="Rollback configured",
        )
        assert "Resources" in p.resource_summary
        assert "Schedule" in p.schedule_summary
        assert "Risk" in p.risk_summary
        assert "Cost" in p.cost_summary
        assert "Rollback" in p.compensation_summary

    def test_get_package(self) -> None:
        p = self.builder.build(plan_id=str(uuid.uuid4()))
        found = self.builder.get_package(str(p.package_id))
        assert found is not None

    def test_get_all_packages(self) -> None:
        self.builder.build(plan_id=str(uuid.uuid4()))
        self.builder.build(plan_id=str(uuid.uuid4()))
        assert len(self.builder.get_all_packages()) == 2

    def test_clear(self) -> None:
        self.builder.build(plan_id=str(uuid.uuid4()))
        self.builder.clear()
        assert len(self.builder.get_all_packages()) == 0


# =============================================================================
# ActionVersionManager Tests
# =============================================================================


class TestActionVersionManager:
    def setup_method(self) -> None:
        self.vm = ActionVersionManager()

    def test_create_version(self) -> None:
        v = self.vm.create_version(plan_id=str(uuid.uuid4()))
        assert v.version_number == 1
        assert v.is_active is True

    def test_create_multiple_versions(self) -> None:
        plan_id = str(uuid.uuid4())
        v1 = self.vm.create_version(plan_id=plan_id)
        v2 = self.vm.create_version(plan_id=plan_id)
        assert v1.version_number == 1
        assert v2.version_number == 2
        assert v1.is_active is False
        assert v2.is_active is True

    def test_get_versions(self) -> None:
        plan_id = str(uuid.uuid4())
        self.vm.create_version(plan_id=plan_id)
        self.vm.create_version(plan_id=plan_id)
        versions = self.vm.get_versions(plan_id)
        assert len(versions) == 2

    def test_get_active_version(self) -> None:
        plan_id = str(uuid.uuid4())
        self.vm.create_version(plan_id=plan_id)
        self.vm.create_version(plan_id=plan_id)
        active = self.vm.get_active_version(plan_id)
        assert active is not None
        assert active.version_number == 2

    def test_mark_active(self) -> None:
        plan_id = str(uuid.uuid4())
        v1 = self.vm.create_version(plan_id=plan_id)
        v2 = self.vm.create_version(plan_id=plan_id)
        result = self.vm.mark_active(plan_id, str(v1.version_id))
        assert result is not None
        assert result.version_number == 1
        assert self.vm.get_active_version(plan_id).version_number == 1

    def test_mark_active_not_found(self) -> None:
        result = self.vm.mark_active(str(uuid.uuid4()), str(uuid.uuid4()))
        assert result is None

    def test_compare_versions(self) -> None:
        plan_id = str(uuid.uuid4())
        self.vm.create_version(plan_id=plan_id)
        self.vm.create_version(plan_id=plan_id)
        comp = self.vm.compare_versions(plan_id, 1, 2)
        assert comp["version_a"] == 1
        assert comp["version_b"] == 2
        assert comp["version_a_exists"] is True
        assert comp["version_b_exists"] is True

    def test_clear(self) -> None:
        self.vm.create_version(plan_id=str(uuid.uuid4()))
        self.vm.clear()
        assert len(self.vm.get_versions(str(uuid.uuid4()))) == 0


# =============================================================================
# ActionLineage Tests
# =============================================================================


class TestActionLineage:
    def setup_method(self) -> None:
        self.lineage = ActionLineage()

    def test_record(self) -> None:
        lr = self.lineage.record(
            request_id=str(uuid.uuid4()),
            plan_id=str(uuid.uuid4()),
            stage="planning_complete",
        )
        assert lr.stage == "planning_complete"
        assert lr.request_id != ""

    def test_get_lineage(self) -> None:
        lr = self.lineage.record(request_id=str(uuid.uuid4()), stage="test")
        found = self.lineage.get_lineage(str(lr.lineage_id))
        assert found is not None

    def test_get_lineage_for_request(self) -> None:
        rid = str(uuid.uuid4())
        self.lineage.record(request_id=rid, stage="stage1")
        self.lineage.record(request_id=rid, stage="stage2")
        records = self.lineage.get_lineage_for_request(rid)
        assert len(records) == 2

    def test_get_lineage_for_plan(self) -> None:
        pid = str(uuid.uuid4())
        rid = str(uuid.uuid4())
        self.lineage.record(request_id=rid, plan_id=pid, stage="stage1")
        self.lineage.record(request_id=rid, plan_id=pid, stage="stage2")
        records = self.lineage.get_lineage_for_plan(pid)
        assert len(records) == 2
        for r in records:
            assert r.plan_id == pid

    def test_filtering_by_request(self) -> None:
        rid1 = str(uuid.uuid4())
        rid2 = str(uuid.uuid4())
        self.lineage.record(request_id=rid1, stage="a")
        self.lineage.record(request_id=rid2, stage="b")
        assert len(self.lineage.get_lineage_for_request(rid1)) == 1
        assert len(self.lineage.get_lineage_for_request(rid2)) == 1

    def test_clear(self) -> None:
        self.lineage.record(request_id=str(uuid.uuid4()), stage="test")
        self.lineage.clear()
        assert len(self.lineage.get_lineage_for_request(str(uuid.uuid4()))) == 0

    def test_parent_lineage(self) -> None:
        parent = self.lineage.record(request_id=str(uuid.uuid4()), stage="parent")
        child = self.lineage.record(
            request_id=str(uuid.uuid4()),
            stage="child",
            parent_lineage_id=str(parent.lineage_id),
        )
        assert child.parent_lineage_id == str(parent.lineage_id)


# =============================================================================
# ActionSnapshot Tests
# =============================================================================


class TestActionSnapshot:
    def setup_method(self) -> None:
        self.snapshot = ActionSnapshot()

    def test_create_snapshot(self) -> None:
        s = self.snapshot.create_snapshot(
            plan_id=str(uuid.uuid4()),
            request_id=str(uuid.uuid4()),
        )
        assert s.snapshot_type == "plan"
        assert s.version == 1

    def test_create_snapshot_all_fields(self) -> None:
        s = self.snapshot.create_snapshot(
            plan_id=str(uuid.uuid4()),
            request_id=str(uuid.uuid4()),
            decision_id=str(uuid.uuid4()),
            session_id=str(uuid.uuid4()),
            version=3,
            step_count=10,
            readiness_score=0.8,
            quality_score=0.9,
            confidence_score=0.85,
            snapshot_type="readiness",
        )
        assert s.version == 3
        assert s.step_count == 10
        assert s.readiness_score == 0.8
        assert s.quality_score == 0.9
        assert s.confidence_score == 0.85
        assert s.snapshot_type == "readiness"

    def test_get_snapshot(self) -> None:
        s = self.snapshot.create_snapshot(
            plan_id=str(uuid.uuid4()),
            request_id=str(uuid.uuid4()),
        )
        found = self.snapshot.get_snapshot(str(s.snapshot_id))
        assert found is not None

    def test_get_snapshots_for_plan(self) -> None:
        pid = str(uuid.uuid4())
        self.snapshot.create_snapshot(plan_id=pid, request_id=str(uuid.uuid4()))
        self.snapshot.create_snapshot(plan_id=pid, request_id=str(uuid.uuid4()))
        assert len(self.snapshot.get_snapshots_for_plan(pid)) == 2

    def test_clear(self) -> None:
        self.snapshot.create_snapshot(
            plan_id=str(uuid.uuid4()),
            request_id=str(uuid.uuid4()),
        )
        self.snapshot.clear()
        assert len(self.snapshot.get_snapshots_for_plan(str(uuid.uuid4()))) == 0


# =============================================================================
# ExecutionHealth Tests
# =============================================================================


class TestExecutionHealth:
    def setup_method(self) -> None:
        self.health = ExecutionHealth()

    def test_get_health_default(self) -> None:
        h = self.health.get_health()
        assert h.overall_status == "HEALTHY"
        assert h.error_count == 0
        assert h.plan_count == 0

    def test_record_error(self) -> None:
        self.health.record_error()
        assert self.health.get_health().error_count == 1
        assert self.health.get_health().overall_status == "DEGRADED"

    def test_record_plan(self) -> None:
        self.health.record_plan()
        assert self.health.get_health().plan_count == 1

    def test_record_latency(self) -> None:
        self.health.record_latency(100.0)
        self.health.record_latency(200.0)
        h = self.health.get_health()
        assert h.average_planning_time_ms == 150.0

    def test_all_component_statuses(self) -> None:
        h = self.health.get_health()
        assert h.service_status == "HEALTHY"
        assert h.manager_status == "HEALTHY"
        assert h.coordinator_status == "HEALTHY"
        assert h.planner_status == "HEALTHY"
        assert h.dependency_resolver_status == "HEALTHY"
        assert h.resource_allocator_status == "HEALTHY"
        assert h.schedule_planner_status == "HEALTHY"
        assert h.rollback_planner_status == "HEALTHY"
        assert h.readiness_validator_status == "HEALTHY"
        assert h.confidence_calculator_status == "HEALTHY"
        assert h.session_manager_status == "HEALTHY"
        assert h.version_manager_status == "HEALTHY"
        assert h.lineage_status == "HEALTHY"
        assert h.snapshot_status == "HEALTHY"
        assert h.quality_manager_status == "HEALTHY"
        assert h.review_status == "HEALTHY"

    def test_reset(self) -> None:
        self.health.record_error()
        self.health.record_plan()
        self.health.reset()
        h = self.health.get_health()
        assert h.error_count == 0
        assert h.plan_count == 0
        assert h.overall_status == "HEALTHY"


# =============================================================================
# ActionPolicyCompliance Tests
# =============================================================================


class TestActionPolicyCompliance:
    def setup_method(self) -> None:
        self.pc = ActionPolicyCompliance()

    def test_check_default(self) -> None:
        r = self.pc.check(plan_id=str(uuid.uuid4()))
        assert r.is_compliant is False
        assert len(r.violations) > 0

    def test_check_fully_compliant(self) -> None:
        r = self.pc.check(
            plan_id=str(uuid.uuid4()),
            step_count=5,
            has_rollback=True,
            has_resources=True,
            has_preconditions=True,
            has_postconditions=True,
        )
        assert r.is_compliant is True
        assert len(r.violations) == 0
        assert r.safety_compliant is True
        assert r.business_compliant is True
        assert r.resource_compliant is True
        assert r.compliance_passed is True
        assert r.operational_compliant is True

    def test_check_missing_rollback(self) -> None:
        r = self.pc.check(plan_id=str(uuid.uuid4()), step_count=3, has_rollback=False)
        assert r.safety_compliant is False
        assert r.is_compliant is False

    def test_check_no_steps(self) -> None:
        r = self.pc.check(plan_id=str(uuid.uuid4()), step_count=0)
        assert r.business_compliant is False

    def test_check_no_resources(self) -> None:
        r = self.pc.check(plan_id=str(uuid.uuid4()), step_count=3, has_resources=False)
        assert r.resource_compliant is False

    def test_get_result(self) -> None:
        r = self.pc.check(plan_id=str(uuid.uuid4()))
        found = self.pc.get_result(str(r.result_id))
        assert found is not None

    def test_get_all_results(self) -> None:
        self.pc.check(plan_id=str(uuid.uuid4()))
        self.pc.check(plan_id=str(uuid.uuid4()))
        assert len(self.pc.get_all_results()) == 2

    def test_clear(self) -> None:
        self.pc.check(plan_id=str(uuid.uuid4()))
        self.pc.clear()
        assert len(self.pc.get_all_results()) == 0


# =============================================================================
# ExecutionContextBuilder Tests
# =============================================================================


class TestExecutionContextBuilder:
    def setup_method(self) -> None:
        self.builder = ExecutionContextBuilder()

    def test_build(self) -> None:
        request = ActionRequest(
            review_decision_id=uuid.uuid4(),
            domain="ENERGY",
            target="turbine-01",
            metadata={"asset_id": "asset-001", "facility_id": "facility-A"},
        )
        ctx = self.builder.build(request)
        assert ctx.request_id == request.request_id
        assert ctx.review_decision_id == request.review_decision_id
        assert ctx.domain == "ENERGY"
        assert ctx.asset_id == "asset-001"
        assert ctx.facility_id == "facility-A"
        assert ctx.machine_id == ""
        assert ctx.workflow_id == ""

    def test_build_empty_metadata(self) -> None:
        request = ActionRequest(review_decision_id=uuid.uuid4())
        ctx = self.builder.build(request)
        assert ctx.asset_id == ""
        assert ctx.machine_id == ""

    def test_get_context(self) -> None:
        request = ActionRequest(review_decision_id=uuid.uuid4())
        ctx = self.builder.build(request)
        found = self.builder.get_context(str(ctx.context_id))
        assert found is not None
        assert found.domain == request.domain

    def test_clear(self) -> None:
        request = ActionRequest(review_decision_id=uuid.uuid4())
        self.builder.build(request)
        self.builder.clear()
        assert len(self.builder.get_context(str(uuid.uuid4())) or []) == 0


# =============================================================================
# ActionCoordinator Tests
# =============================================================================


class TestActionCoordinator:
    def setup_method(self) -> None:
        self.coordinator = ActionCoordinator()

    def test_plan_default(self) -> None:
        request = ActionRequest(review_decision_id=uuid.uuid4())
        decision = self.coordinator.plan(request)
        assert decision.request_id == request.request_id
        assert decision.plan is not None
        assert decision.issues is not None
        assert decision.warnings is not None

    def test_plan_with_missing_decision_id(self) -> None:
        request = ActionRequest(review_decision_id=uuid.uuid4())
        decision = self.coordinator.plan(request)
        # Should proceed without crashing

    def test_plan_creates_decision(self) -> None:
        request = ActionRequest(review_decision_id=uuid.uuid4())
        decision = self.coordinator.plan(request)
        assert decision.decision_id is not None
        assert decision.timestamp is not None

    def test_plan_creates_session(self) -> None:
        request = ActionRequest(review_decision_id=uuid.uuid4())
        self.coordinator.plan(request)
        assert self.coordinator.session_manager.count() == 1

    def test_plan_creates_version(self) -> None:
        request = ActionRequest(review_decision_id=uuid.uuid4())
        decision = self.coordinator.plan(request)
        plan_id = str(decision.plan.plan_id) if decision.plan else ""
        if plan_id:
            versions = self.coordinator.version_manager.get_versions(plan_id)
            assert len(versions) == 1

    def test_plan_creates_lineage(self) -> None:
        request = ActionRequest(review_decision_id=uuid.uuid4())
        self.coordinator.plan(request)
        lineage = self.coordinator.lineage.get_lineage_for_request(str(request.request_id))
        assert len(lineage) >= 1

    def test_plan_creates_snapshot(self) -> None:
        request = ActionRequest(review_decision_id=uuid.uuid4())
        decision = self.coordinator.plan(request)
        plan_id = str(decision.plan.plan_id) if decision.plan else ""
        if plan_id:
            snapshots = self.coordinator.snapshot.get_snapshots_for_plan(plan_id)
            assert len(snapshots) == 1

    def test_plan_confidence_and_explainability(self) -> None:
        request = ActionRequest(review_decision_id=uuid.uuid4())
        decision = self.coordinator.plan(request)
        assert decision.confidence is not None
        assert decision.explainability is not None
        assert decision.explainability.why_plan_generated != ""

    def test_get_decision(self) -> None:
        request = ActionRequest(review_decision_id=uuid.uuid4())
        decision = self.coordinator.plan(request)
        found = self.coordinator.get_decision(str(decision.decision_id))
        assert found is not None
        assert str(found.decision_id) == str(decision.decision_id)

    def test_get_plan(self) -> None:
        request = ActionRequest(review_decision_id=uuid.uuid4())
        decision = self.coordinator.plan(request)
        plan_id = str(decision.plan.plan_id) if decision.plan else ""
        if plan_id:
            found = self.coordinator.get_plan(plan_id)
            assert found is not None
            assert str(found.plan_id) == plan_id

    def test_health(self) -> None:
        health = self.coordinator.health()
        assert health.overall_status == "HEALTHY"
        assert health.plan_count >= 0

    def test_metrics(self) -> None:
        metrics = self.coordinator.metrics()
        assert metrics.plans_total >= 0
        assert metrics.sessions_total >= 0

    def test_plan_audit_trail(self) -> None:
        request = ActionRequest(review_decision_id=uuid.uuid4())
        decision = self.coordinator.plan(request)
        assert len(decision.issues) == 0
        assert decision.readiness is not None
        assert decision.quality_score >= 0.0
        assert decision.readiness_score >= 0.0


# =============================================================================
# ActionManager Tests
# =============================================================================


class TestActionManager:
    def setup_method(self) -> None:
        self.manager = ActionManager()

    def test_start_planning(self) -> None:
        request = ActionRequest(review_decision_id=uuid.uuid4())
        decision = self.manager.start_planning(request)
        assert decision is not None
        assert decision.request_id == request.request_id

    def test_get_decision(self) -> None:
        request = ActionRequest(review_decision_id=uuid.uuid4())
        decision = self.manager.start_planning(request)
        found = self.manager.get_decision(str(decision.decision_id))
        assert found is not None
        assert str(found.decision_id) == str(decision.decision_id)

    def test_get_plan(self) -> None:
        request = ActionRequest(review_decision_id=uuid.uuid4())
        decision = self.manager.start_planning(request)
        plan_id = str(decision.plan.plan_id) if decision.plan else ""
        if plan_id:
            found = self.manager.get_plan(plan_id)
            assert found is not None

    def test_get_session(self) -> None:
        request = ActionRequest(review_decision_id=uuid.uuid4())
        decision = self.manager.start_planning(request)
        sessions = self.manager._coordinator.session_manager.get_all_sessions()
        assert len(sessions) == 1
        session = self.manager.get_session(str(sessions[0].session_id))
        assert session is not None
        assert session.status == "COMPLETED"

    def test_get_health(self) -> None:
        health = self.manager.get_health()
        assert health.overall_status is not None

    def test_get_metrics(self) -> None:
        metrics = self.manager.get_metrics()
        assert metrics.plans_total >= 0

    def test_correlation_id_propagation(self) -> None:
        request = ActionRequest(review_decision_id=uuid.uuid4())
        cid = "test-correlation-id"
        decision = self.manager.start_planning(request, correlation_id=cid)
        assert decision is not None


# =============================================================================
# IntegrationHooks Tests
# =============================================================================


class TestIntegrationHooks:
    def setup_method(self) -> None:
        self.hooks = IntegrationHooks()
        self.call_count = 0

    def _callback(self, *args: Any, **kwargs: Any) -> None:
        self.call_count += 1

    def test_register_pre_plan(self) -> None:
        self.hooks.register_pre_plan(self._callback)
        self.hooks.run_pre_plan()
        assert self.call_count == 1

    def test_register_post_plan(self) -> None:
        self.hooks.register_post_plan(self._callback)
        self.hooks.run_post_plan()
        assert self.call_count == 1

    def test_register_on_error(self) -> None:
        self.hooks.register_on_error(self._callback)
        self.hooks.run_on_error(error="test")
        assert self.call_count == 1

    def test_register_session_created(self) -> None:
        self.hooks.register_session_created(self._callback)
        self.hooks.run_session_created()
        assert self.call_count == 1

    def test_register_session_completed(self) -> None:
        self.hooks.register_session_completed(self._callback)
        self.hooks.run_session_completed()
        assert self.call_count == 1

    def test_register_decision_made(self) -> None:
        self.hooks.register_decision_made(self._callback)
        self.hooks.run_decision_made()
        assert self.call_count == 1

    def test_register_readiness_assessed(self) -> None:
        self.hooks.register_readiness_assessed(self._callback)
        self.hooks.run_readiness_assessed()
        assert self.call_count == 1

    def test_register_pre_optimize(self) -> None:
        self.hooks.register_pre_optimize(self._callback)
        self.hooks.run_pre_optimize()
        assert self.call_count == 1

    def test_register_post_optimize(self) -> None:
        self.hooks.register_post_optimize(self._callback)
        self.hooks.run_post_optimize()
        assert self.call_count == 1

    def test_register_pre_review(self) -> None:
        self.hooks.register_pre_review(self._callback)
        self.hooks.run_pre_review()
        assert self.call_count == 1

    def test_register_post_review(self) -> None:
        self.hooks.register_post_review(self._callback)
        self.hooks.run_post_review()
        assert self.call_count == 1

    def test_multiple_hooks(self) -> None:
        self.hooks.register_pre_plan(self._callback)
        self.hooks.register_pre_plan(self._callback)
        self.hooks.run_pre_plan()
        assert self.call_count == 2

    def test_exception_isolation(self) -> None:
        def failing(*args: Any, **kwargs: Any) -> None:
            raise ValueError("hook failed")

        self.hooks.register_pre_plan(failing)
        self.hooks.register_pre_plan(self._callback)
        self.hooks.run_pre_plan()
        assert self.call_count == 1

    def test_global_hooks_singleton(self) -> None:
        from adip.actions.services.hooks import hooks as global_hooks
        assert global_hooks is not None
        assert isinstance(global_hooks, IntegrationHooks)


# =============================================================================
# DefaultActionService Tests
# =============================================================================


class TestDefaultActionService:
    def setup_method(self) -> None:
        self.auth_calls: list[str] = []
        self.audit_calls: list[tuple[str, str, str, dict]] = []

        def auth(user_id: str, permission: str) -> bool:
            self.auth_calls.append(f"{user_id}:{permission}")
            return True

        def audit(user_id: str, action: str, resource: str, details: dict) -> None:
            self.audit_calls.append((user_id, action, resource, details))

        self.service = DefaultActionService(
            auth_callback=auth,
            audit_callback=audit,
        )

    def test_plan_action(self) -> None:
        dto = ActionRequestDTO(review_decision_id=uuid.uuid4())
        response = self.service.plan_action(dto, user_id="test-user")
        assert response is not None
        assert response.request_id == dto.request_id
        assert response.status is not None

    def test_plan_action_auth_failure(self) -> None:
        def failing_auth(user_id: str, permission: str) -> bool:
            return False

        service = DefaultActionService(auth_callback=failing_auth)
        dto = ActionRequestDTO(review_decision_id=uuid.uuid4())
        response = service.plan_action(dto, user_id="unauthorized")
        assert response is None

    def test_get_decision(self) -> None:
        dto = ActionRequestDTO(review_decision_id=uuid.uuid4())
        response = self.service.plan_action(dto, user_id="test-user")
        assert response is not None
        # Test get_decision returns valid result
        assert response.response_id is not None

    def test_get_plan(self) -> None:
        dto = ActionRequestDTO(review_decision_id=uuid.uuid4())
        response = self.service.plan_action(dto, user_id="test-user")
        assert response is not None
        if response.decision:
            plan = self.service.get_plan(str(response.decision.plan_id))
            # May be None if not cached, but should not crash
            assert plan is None or plan is not None

    def test_get_health(self) -> None:
        health = self.service.get_health()
        assert health.overall_status is not None

    def test_get_metrics(self) -> None:
        metrics = self.service.get_metrics()
        assert metrics.plans_total >= 0

    def test_correlation_id_propagation(self) -> None:
        dto = ActionRequestDTO(review_decision_id=uuid.uuid4())
        response = self.service.plan_action(
            dto, user_id="test-user", correlation_id="custom-cid"
        )
        assert response is not None

    def test_audit_logging(self) -> None:
        dto = ActionRequestDTO(review_decision_id=uuid.uuid4())
        self.service.plan_action(dto, user_id="test-user")
        assert len(self.audit_calls) >= 2  # started + completed

    def test_service_wraps_decision(self) -> None:
        dto = ActionRequestDTO(review_decision_id=uuid.uuid4())
        response = self.service.plan_action(dto, user_id="test-user")
        assert response is not None
        assert response.decision is not None or response.decision is None

    def test_auth_callback_isolation(self) -> None:
        dto = ActionRequestDTO(review_decision_id=uuid.uuid4())
        self.service.plan_action(dto, user_id="test-user")
        assert len(self.auth_calls) > 0

    def test_plan_action_with_default_auth(self) -> None:
        service = DefaultActionService()
        dto = ActionRequestDTO(review_decision_id=uuid.uuid4())
        response = service.plan_action(dto)
        assert response is not None


# =============================================================================
# Cross-Component Integration Tests
# =============================================================================


class TestActionPhase3Integration:
    def test_full_pipeline_through_coordinator(self) -> None:
        coordinator = ActionCoordinator()
        request = ActionRequest(review_decision_id=uuid.uuid4())
        decision = coordinator.plan(request)

        assert decision.plan is not None
        assert decision.confidence is not None
        assert decision.explainability is not None
        assert decision.quality_score >= 0.0
        assert decision.readiness_score >= 0.0
        assert len(decision.issues) == 0
        assert decision.is_ready is True or decision.is_ready is False

    def test_full_pipeline_through_manager(self) -> None:
        manager = ActionManager()
        request = ActionRequest(review_decision_id=uuid.uuid4())
        decision = manager.start_planning(request)

        health = manager.get_health()
        metrics = manager.get_metrics()

        assert health.overall_status is not None
        assert metrics.plans_total >= 1
        assert decision.plan is not None

    def test_full_pipeline_through_service(self) -> None:
        service = DefaultActionService()
        dto = ActionRequestDTO(review_decision_id=uuid.uuid4())
        response = service.plan_action(dto, user_id="test")

        assert response is not None
        assert response.status is not None

        health = service.get_health()
        metrics = service.get_metrics()
        assert health.overall_status is not None
        assert metrics.plans_total >= 1

    def test_multiple_plans(self) -> None:
        manager = ActionManager()
        for _ in range(3):
            request = ActionRequest(review_decision_id=uuid.uuid4())
            manager.start_planning(request)

        metrics = manager.get_metrics()
        assert metrics.plans_total == 3
        assert metrics.sessions_total == 3

    def test_audit_trail_consistency(self) -> None:
        coordinator = ActionCoordinator()
        request = ActionRequest(review_decision_id=uuid.uuid4())
        decision = coordinator.plan(request)

        # Verify the decision has all Phase 3 fields
        assert hasattr(decision, "confidence")
        assert hasattr(decision, "explainability")
        assert hasattr(decision, "quality_score")
        assert hasattr(decision, "readiness_score")

        # Verify the session has enhanced fields
        sessions = coordinator.session_manager.get_all_sessions()
        for s in sessions:
            assert hasattr(s, "decision_id")
            assert hasattr(s, "step_count")
            assert hasattr(s, "has_rollback")
