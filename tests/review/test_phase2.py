"""Tests for Decision Review Layer Phase 2 execution components."""

from __future__ import annotations

import uuid
from types import SimpleNamespace

import pytest

from adip.review.execution.approval_strategy import ApprovalStrategyManager
from adip.review.execution.checklist import ReviewChecklist
from adip.review.execution.conflict_resolver import ConflictResolutionManager
from adip.review.execution.escalation_engine import EscalationEngine
from adip.review.execution.metrics import GovernanceMetrics
from adip.review.execution.models import (
    ChecklistItem,
    ConflictResolutionResult,
    EscalationRecord,
    GovernanceMetricsSnapshot,
    ModificationRecord,
    PolicyMatrixResult,
    ReviewerAssignment,
    SLARecord,
    TimelineEvent,
    TraceRecord,
)
from adip.review.execution.modification_manager import ModificationManager
from adip.review.execution.policy_matrix import ReviewPolicyMatrix
from adip.review.execution.reviewer_assignment import ReviewerAssignmentEngine
from adip.review.execution.sla_manager import ReviewSLAManager
from adip.review.execution.timeline import ReviewTimeline
from adip.review.execution.trace import ReviewTrace
from adip.review.execution.validator import ReviewValidator

# ═══════════════════════════════════════════════════════════════════════════════
# Execution Models
# ═══════════════════════════════════════════════════════════════════════════════


class TestPolicyMatrixResult:
    def test_defaults(self) -> None:
        m = PolicyMatrixResult()
        assert m.recommended_workflow == "SINGLE_REVIEW"
        assert m.confidence_level == "MEDIUM"
        assert m.risk_level == "MEDIUM"
        assert m.impact_level == "MEDIUM"
        assert m.criticality_level == "MEDIUM"
        assert m.compliance_required is True
        assert m.requires_escalation is False
        assert m.justification == ""

    def test_custom_values(self) -> None:
        m = PolicyMatrixResult(
            recommended_workflow="MULTI_LEVEL",
            confidence_level="HIGH",
            risk_level="HIGH",
            impact_level="HIGH",
            criticality_level="HIGH",
            compliance_required=False,
            requires_escalation=True,
            justification="test",
        )
        assert m.recommended_workflow == "MULTI_LEVEL"
        assert m.requires_escalation is True

    def test_uuid_generated(self) -> None:
        assert isinstance(PolicyMatrixResult().matrix_id, uuid.UUID)


class TestReviewerAssignment:
    def test_defaults(self) -> None:
        a = ReviewerAssignment()
        assert a.reviewer_id == ""
        assert a.expertise_score == 0.5
        assert a.current_workload == 0
        assert a.is_available is True
        assert a.authority_level == "STANDARD"

    def test_expertise_bounds(self) -> None:
        with pytest.raises(Exception):
            ReviewerAssignment(expertise_score=1.5)
        with pytest.raises(Exception):
            ReviewerAssignment(expertise_score=-0.1)

    def test_uuid_generated(self) -> None:
        assert isinstance(ReviewerAssignment().assignment_id, uuid.UUID)


class TestModificationRecord:
    def test_defaults(self) -> None:
        did = uuid.uuid4()
        r = ModificationRecord(decision_id=did)
        assert r.modification_type == ""
        assert r.previous_value == ""
        assert r.new_value == ""
        assert r.reason == ""
        assert r.modified_by == ""

    def test_requires_decision_id(self) -> None:
        with pytest.raises(Exception):
            ModificationRecord()

    def test_uuid_generated(self) -> None:
        assert isinstance(ModificationRecord(decision_id=uuid.uuid4()).modification_id, uuid.UUID)


class TestEscalationRecord:
    def test_defaults(self) -> None:
        r = EscalationRecord()
        assert r.review_id == ""
        assert r.reason == ""
        assert r.severity == "MEDIUM"
        assert r.resolved is False
        assert r.resolved_at is None

    def test_custom_values(self) -> None:
        r = EscalationRecord(review_id="r1", reason="high risk", severity="HIGH", resolved=True)
        assert r.review_id == "r1"
        assert r.severity == "HIGH"
        assert r.resolved is True


class TestSLARecord:
    def test_defaults(self) -> None:
        s = SLARecord()
        assert s.review_id == ""
        assert s.sla_minutes == 60
        assert s.remaining_minutes == 60.0
        assert s.is_breached is False
        assert s.auto_escalate is False

    def test_sla_minutes_constraint(self) -> None:
        with pytest.raises(Exception):
            SLARecord(sla_minutes=0)


class TestConflictResolutionResult:
    def test_defaults(self) -> None:
        r = ConflictResolutionResult()
        assert r.review_ids == []
        assert r.votes_for == 0
        assert r.votes_against == 0
        assert r.tie_broken is False
        assert r.outcome == ""

    def test_custom_values(self) -> None:
        r = ConflictResolutionResult(
            review_ids=["r1", "r2"],
            votes_for=3,
            votes_against=1,
            outcome="APPROVED",
        )
        assert len(r.review_ids) == 2
        assert r.outcome == "APPROVED"


class TestTimelineEvent:
    def test_defaults(self) -> None:
        e = TimelineEvent()
        assert e.review_id == ""
        assert e.event_type == ""
        assert e.description == ""
        assert e.performed_by == ""
        assert e.metadata == {}

    def test_custom_values(self) -> None:
        e = TimelineEvent(review_id="r1", event_type="APPROVED", description="Approved by manager")
        assert e.event_type == "APPROVED"


class TestChecklistItem:
    def test_defaults(self) -> None:
        i = ChecklistItem()
        assert i.item_name == ""
        assert i.is_complete is False
        assert i.required is True

    def test_custom_values(self) -> None:
        i = ChecklistItem(review_id="r1", item_name="Evidence Reviewed", is_complete=True, completed_by="user1")
        assert i.is_complete is True
        assert i.completed_by == "user1"


class TestGovernanceMetricsSnapshot:
    def test_defaults(self) -> None:
        s = GovernanceMetricsSnapshot()
        assert s.reviews_total == 0
        assert s.approval_rate == 0.0
        assert s.rejection_rate == 0.0
        assert s.sla_breaches == 0

    def test_rates_bounds(self) -> None:
        with pytest.raises(Exception):
            GovernanceMetricsSnapshot(approval_rate=101.0)
        with pytest.raises(Exception):
            GovernanceMetricsSnapshot(rejection_rate=-1.0)


class TestTraceRecord:
    def test_defaults(self) -> None:
        t = TraceRecord()
        assert t.review_id == ""
        assert t.stage_name == ""
        assert t.operation == ""
        assert t.success is True
        assert t.duration_ms is None

    def test_duration_constraint(self) -> None:
        with pytest.raises(Exception):
            TraceRecord(duration_ms=-1.0)


# ═══════════════════════════════════════════════════════════════════════════════
# ReviewPolicyMatrix
# ═══════════════════════════════════════════════════════════════════════════════


class TestReviewPolicyMatrix:
    def setup_method(self) -> None:
        self.matrix = ReviewPolicyMatrix()

    def test_auto_approval_path(self) -> None:
        result = self.matrix.evaluate(0.95, "LOW", "LOW", "LOW", True)
        assert result.recommended_workflow == "AUTO_APPROVAL"
        assert result.confidence_level == "HIGH"

    def test_single_review_path(self) -> None:
        result = self.matrix.evaluate(0.8, "MEDIUM", "MEDIUM", "MEDIUM", True)
        assert result.recommended_workflow == "SINGLE_REVIEW"
        assert result.confidence_level == "HIGH"

    def test_sequential_review_path(self) -> None:
        result = self.matrix.evaluate(0.6, "HIGH", "LOW", "LOW", True)
        assert result.recommended_workflow == "SEQUENTIAL"

    def test_multi_level_path(self) -> None:
        result = self.matrix.evaluate(0.4, "HIGH", "HIGH", "LOW", True)
        assert result.recommended_workflow == "MULTI_LEVEL"
        assert result.requires_escalation is True

    def test_emergency_path(self) -> None:
        result = self.matrix.evaluate(0.5, "MEDIUM", "MEDIUM", "EMERGENCY", True)
        assert result.recommended_workflow == "EMERGENCY"
        assert result.requires_escalation is True

    def test_default_path(self) -> None:
        result = self.matrix.evaluate(0.4, "LOW", "LOW", "LOW", False)
        assert result.recommended_workflow == "SINGLE_REVIEW"

    def test_get_matrix(self) -> None:
        matrix = self.matrix.get_matrix(0.95, "LOW", "LOW", "LOW", True)
        assert matrix["recommended_workflow"] == "AUTO_APPROVAL"
        assert matrix["confidence_level"] == "HIGH"
        assert isinstance(matrix, dict)

    def test_clear(self) -> None:
        self.matrix.evaluate(0.9, "LOW", "LOW", "LOW", True)
        self.matrix.clear()


# ═══════════════════════════════════════════════════════════════════════════════
# ApprovalStrategyManager
# ═══════════════════════════════════════════════════════════════════════════════


class TestApprovalStrategyManager:
    def setup_method(self) -> None:
        self.manager = ApprovalStrategyManager()

    def test_get_available_strategies(self) -> None:
        strategies = self.manager.get_available_strategies()
        assert len(strategies) == 6
        assert "AUTO_APPROVAL" in strategies
        assert "EMERGENCY" in strategies

    def test_select_strategy(self) -> None:
        policy_result = PolicyMatrixResult(recommended_workflow="MULTI_LEVEL")
        strategy = self.manager.select_strategy(None, policy_result)
        assert strategy == "MULTI_LEVEL"

    def test_select_strategy_default(self) -> None:
        policy_result = PolicyMatrixResult()
        strategy = self.manager.select_strategy(None, policy_result)
        assert strategy == "SINGLE_REVIEW"

    def test_execute_auto_approval(self) -> None:
        result = self.manager.execute_auto_approval(None)
        assert result["strategy"] == "AUTO_APPROVAL"
        assert result["approved"] is True

    def test_execute_single_review(self) -> None:
        result = self.manager.execute_single_review(None)
        assert result["strategy"] == "SINGLE_REVIEW"

    def test_execute_sequential(self) -> None:
        result = self.manager.execute_sequential(None)
        assert result["strategy"] == "SEQUENTIAL"
        assert len(result["steps"]) > 0

    def test_execute_parallel(self) -> None:
        result = self.manager.execute_parallel(None)
        assert result["strategy"] == "PARALLEL"
        assert result["reviewers_needed"] == 3

    def test_execute_multi_level(self) -> None:
        result = self.manager.execute_multi_level(None)
        assert result["strategy"] == "MULTI_LEVEL"
        assert len(result["levels"]) > 0

    def test_execute_emergency(self) -> None:
        result = self.manager.execute_emergency(None)
        assert result["strategy"] == "EMERGENCY"
        assert result["emergency_protocol"] is True

    def test_correlation_id_propagation(self) -> None:
        result = self.manager.execute_single_review(None, correlation_id="corr-123")
        assert result["correlation_id"] == "corr-123"


# ═══════════════════════════════════════════════════════════════════════════════
# ReviewerAssignmentEngine
# ═══════════════════════════════════════════════════════════════════════════════


class TestReviewerAssignmentEngine:
    def setup_method(self) -> None:
        self.engine = ReviewerAssignmentEngine()
        self.engine.register_reviewer("rev-1", "Alice", "ENGINEER", 0.8, 5)
        self.engine.register_reviewer("rev-2", "Bob", "MANAGER", 0.6, 3)
        self.engine.register_reviewer("rev-3", "Charlie", "SUPERVISOR", 0.9, 2)

    def test_register_reviewer(self) -> None:
        assert len(self.engine.get_available_reviewers()) == 3

    def test_register_duplicate(self) -> None:
        self.engine.register_reviewer("rev-1", "Alice", "ENGINEER")
        assert len(self.engine.get_available_reviewers()) == 3

    def test_unregister_reviewer(self) -> None:
        assert self.engine.unregister_reviewer("rev-1") is True
        assert len(self.engine.get_available_reviewers()) == 2

    def test_unregister_nonexistent(self) -> None:
        assert self.engine.unregister_reviewer("nonexistent") is False

    def test_assign_reviewers(self) -> None:
        request = {"request_id": str(uuid.uuid4()), "domain": "ENERGY"}
        assignments = self.engine.assign_reviewers(request, "SINGLE_REVIEW", 1)
        assert len(assignments) >= 1
        assert isinstance(assignments[0], ReviewerAssignment)

    def test_assign_multiple_reviewers(self) -> None:
        request = {"request_id": str(uuid.uuid4()), "domain": "ENERGY"}
        assignments = self.engine.assign_reviewers(request, "SINGLE_REVIEW", 2)
        assert len(assignments) >= 1

    def test_assign_no_reviewers(self) -> None:
        empty_engine = ReviewerAssignmentEngine()
        request = {"request_id": str(uuid.uuid4()), "domain": "ENERGY"}
        assignments = empty_engine.assign_reviewers(request, "SINGLE_REVIEW", 1)
        assert len(assignments) == 0

    def test_get_reviewer_workload(self) -> None:
        request = {"request_id": str(uuid.uuid4()), "domain": "ENERGY"}
        self.engine.assign_reviewers(request, "SINGLE_REVIEW", 2)
        assert self.engine.get_reviewer_workload("rev-3") >= 1

    def test_get_reviewer_workload_nonexistent(self) -> None:
        assert self.engine.get_reviewer_workload("nonexistent") == 0

    def test_update_availability(self) -> None:
        assert self.engine.update_availability("rev-1", False) is True
        assert self.engine.update_availability("nonexistent", False) is False

    def test_assign_after_unavailability(self) -> None:
        self.engine.update_availability("rev-1", False)
        assignments = self.engine.assign_reviewers(None, "SINGLE_REVIEW", 2)
        assert all(a.reviewer_id != "rev-1" for a in assignments)


# ═══════════════════════════════════════════════════════════════════════════════
# ReviewValidator
# ═══════════════════════════════════════════════════════════════════════════════


class TestReviewValidator:
    def setup_method(self) -> None:
        self.validator = ReviewValidator()

    def test_validate_valid_package(self) -> None:
        package = SimpleNamespace(
            package_id="pkg-1",
            recommendation_decision={"id": "rec-1"},
            explanation_decision={"id": "exp-1"},
        )
        result = self.validator.validate_review_package(package)
        assert result["valid"] is True
        assert result["errors"] == []

    def test_validate_invalid_package(self) -> None:
        result = self.validator.validate_review_package(None)
        assert result["valid"] is False
        assert len(result["errors"]) > 0

    def test_validate_valid_reviewer(self) -> None:
        reviewer = SimpleNamespace(name="Alice", role="ENGINEER", is_active=True)
        result = self.validator.validate_reviewer(reviewer)
        assert result["valid"] is True

    def test_validate_invalid_reviewer(self) -> None:
        result = self.validator.validate_reviewer(None)
        assert result["valid"] is False

    def test_validate_inactive_reviewer(self) -> None:
        reviewer = SimpleNamespace(name="Alice", role="ENGINEER", is_active=False)
        result = self.validator.validate_reviewer(reviewer)
        assert result["valid"] is True
        assert len(result["warnings"]) > 0

    def test_validate_valid_policy(self) -> None:
        policy = SimpleNamespace(
            allowed_outcomes=["APPROVED"],
            required_reviewer_roles=["ENGINEER"],
        )
        result = self.validator.validate_policy(policy)
        assert result["valid"] is True

    def test_validate_invalid_policy(self) -> None:
        result = self.validator.validate_policy(None)
        assert result["valid"] is False

    def test_validate_valid_workflow(self) -> None:
        workflow = SimpleNamespace(
            workflow_type="SINGLE_REVIEW",
            steps=[{"role": "ENGINEER"}],
        )
        result = self.validator.validate_workflow(workflow)
        assert result["valid"] is True

    def test_validate_invalid_workflow(self) -> None:
        result = self.validator.validate_workflow(None)
        assert result["valid"] is False

    def test_validate_all(self) -> None:
        package = SimpleNamespace(
            package_id="pkg-1",
            recommendation_decision={"id": "r"},
            explanation_decision={"id": "e"},
        )
        reviewer = SimpleNamespace(name="A", role="ENG", is_active=True)
        policy = SimpleNamespace(
            allowed_outcomes=["APPROVED"],
            required_reviewer_roles=["ENG"],
        )
        workflow = SimpleNamespace(
            workflow_type="SINGLE",
            steps=[{"role": "ENG"}],
        )
        result = self.validator.validate_all(package, reviewer, policy, workflow)
        assert result["valid"] is True

    def test_validate_all_invalid(self) -> None:
        result = self.validator.validate_all(None, None, None, None)
        assert result["valid"] is False
        assert len(result["errors"]) > 0


# ═══════════════════════════════════════════════════════════════════════════════
# ModificationManager
# ═══════════════════════════════════════════════════════════════════════════════


class TestModificationManager:
    def setup_method(self) -> None:
        self.manager = ModificationManager()
        self.decision_id = uuid.uuid4()

    def test_approve(self) -> None:
        record = self.manager.approve(self.decision_id, "user-1", "Looks good")
        assert record.modification_type == "APPROVED"
        assert record.decision_id == self.decision_id

    def test_reject(self) -> None:
        record = self.manager.reject(self.decision_id, "user-1", "Not acceptable")
        assert record.modification_type == "REJECTED"

    def test_modify(self) -> None:
        record = self.manager.modify(self.decision_id, "user-1", "old", "new", "Updated")
        assert record.modification_type == "MODIFIED"
        assert record.previous_value == "old"
        assert record.new_value == "new"

    def test_request_information(self) -> None:
        record = self.manager.request_information(self.decision_id, "user-1", "Need more details")
        assert record.modification_type == "MORE_INFORMATION_REQUIRED"

    def test_escalate(self) -> None:
        record = self.manager.escalate(self.decision_id, "user-1", "Needs manager review")
        assert record.modification_type == "ESCALATED"

    def test_defer(self) -> None:
        record = self.manager.defer(self.decision_id, "user-1", "Defer to next sprint")
        assert record.modification_type == "DEFERRED"

    def test_get_modifications(self) -> None:
        self.manager.approve(self.decision_id, "user-1")
        mods = self.manager.get_modifications(self.decision_id)
        assert len(mods) == 1

    def test_get_modifications_none(self) -> None:
        mods = self.manager.get_modifications(uuid.uuid4())
        assert len(mods) == 0

    def test_get_modifications_by_type(self) -> None:
        self.manager.approve(self.decision_id, "user-1")
        self.manager.reject(uuid.uuid4(), "user-1")
        mods = self.manager.get_modifications_by_type("APPROVED")
        assert len(mods) == 1

    def test_clear(self) -> None:
        self.manager.approve(self.decision_id, "user-1")
        self.manager.clear()
        assert len(self.manager.get_modifications(self.decision_id)) == 0


# ═══════════════════════════════════════════════════════════════════════════════
# EscalationEngine
# ═══════════════════════════════════════════════════════════════════════════════


class TestEscalationEngine:
    def setup_method(self) -> None:
        self.engine = EscalationEngine()
        self.engine.add_rule("rule-1", "CONFIDENCE", "ENGINEER", "MANAGER", "HIGH")

    def test_add_rule(self) -> None:
        self.engine.add_rule("rule-2", "RISK", "MANAGER", "ADMIN", "CRITICAL")
        result = self.engine.check_escalation("rev-1", 0.2, "MEDIUM")
        assert result["should_escalate"] is True

    def test_remove_rule(self) -> None:
        assert self.engine.remove_rule("rule-1") is True
        assert self.engine.remove_rule("nonexistent") is False

    def test_check_escalation_low_confidence(self) -> None:
        result = self.engine.check_escalation("rev-1", 0.2, "MEDIUM")
        assert result["should_escalate"] is True
        assert result["escalation_type"] == "LOW_CONFIDENCE"

    def test_check_escalation_high_risk(self) -> None:
        result = self.engine.check_escalation("rev-1", 0.5, "HIGH")
        assert result["should_escalate"] is True
        assert result["escalation_type"] == "HIGH_RISK"

    def test_check_escalation_timeout(self) -> None:
        result = self.engine.check_escalation("rev-1", 0.5, "MEDIUM", timeout_hours=48)
        assert result["should_escalate"] is True
        assert result["escalation_type"] == "TIMEOUT"

    def test_check_escalation_critical(self) -> None:
        result = self.engine.check_escalation("rev-1", 0.5, "MEDIUM", criticality="CRITICAL")
        assert result["should_escalate"] is True
        assert result["escalation_type"] == "CRITICALITY"

    def test_check_no_escalation(self) -> None:
        result = self.engine.check_escalation("rev-1", 0.8, "LOW")
        assert result["should_escalate"] is False

    def test_escalate(self) -> None:
        record = self.engine.escalate("rev-1", "Low confidence", "LOW_CONFIDENCE", "user-1", "ENGINEER", "MANAGER")
        assert isinstance(record, EscalationRecord)
        assert record.review_id == "rev-1"
        assert record.resolved is False

    def test_resolve_escalation(self) -> None:
        record = self.engine.escalate("rev-1", "test", "TEST")
        assert self.engine.resolve_escalation(str(record.escalation_id)) is True

    def test_resolve_nonexistent(self) -> None:
        assert self.engine.resolve_escalation("nonexistent") is False

    def test_get_active_escalations(self) -> None:
        self.engine.escalate("rev-1", "test", "TEST")
        assert len(self.engine.get_active_escalations()) == 1

    def test_get_escalations_by_review(self) -> None:
        self.engine.escalate("rev-1", "test", "TEST")
        self.engine.escalate("rev-2", "test2", "TEST2")
        assert len(self.engine.get_escalations_by_review("rev-1")) == 1
        assert len(self.engine.get_escalations_by_review("rev-2")) == 1

    def test_get_escalations_by_review_none(self) -> None:
        assert len(self.engine.get_escalations_by_review("nonexistent")) == 0

    def test_clear(self) -> None:
        self.engine.escalate("rev-1", "test", "TEST")
        self.engine.clear()
        assert len(self.engine.get_active_escalations()) == 0


# ═══════════════════════════════════════════════════════════════════════════════
# ReviewSLAManager
# ═══════════════════════════════════════════════════════════════════════════════


class TestReviewSLAManager:
    def setup_method(self) -> None:
        self.sla = ReviewSLAManager()

    def test_start_sla(self) -> None:
        record = self.sla.start_sla("rev-1", 60, False)
        assert record.review_id == "rev-1"
        assert record.sla_minutes == 60
        assert record.is_breached is False

    def test_start_sla_with_auto_escalate(self) -> None:
        record = self.sla.start_sla("rev-1", 30, True)
        assert record.auto_escalate is True

    def test_get_sla(self) -> None:
        self.sla.start_sla("rev-1", 60)
        record = self.sla.get_sla("rev-1")
        assert record is not None
        assert record.review_id == "rev-1"

    def test_get_sla_nonexistent(self) -> None:
        assert self.sla.get_sla("nonexistent") is None

    def test_get_remaining_time(self) -> None:
        self.sla.start_sla("rev-1", 60)
        remaining = self.sla.get_remaining_time("rev-1")
        assert 0 <= remaining <= 60

    def test_get_remaining_time_nonexistent(self) -> None:
        assert self.sla.get_remaining_time("nonexistent") == 0.0

    def test_is_breached(self) -> None:
        self.sla.start_sla("rev-1", 60)
        assert self.sla.is_breached("rev-1") is False

    def test_is_breached_nonexistent(self) -> None:
        assert self.sla.is_breached("nonexistent") is False

    def test_check_breaches(self) -> None:
        self.sla.start_sla("rev-1", 60)
        breaches = self.sla.check_breaches()
        assert isinstance(breaches, list)

    def test_update_sla_minutes(self) -> None:
        self.sla.start_sla("rev-1", 60)
        assert self.sla.update_sla_minutes("rev-1", 120) is True
        assert self.sla.get_sla("rev-1").sla_minutes == 120

    def test_update_sla_nonexistent(self) -> None:
        assert self.sla.update_sla_minutes("nonexistent", 60) is False

    def test_get_all_slas(self) -> None:
        self.sla.start_sla("rev-1", 60)
        self.sla.start_sla("rev-2", 30)
        assert len(self.sla.get_all_slas()) == 2

    def test_clear(self) -> None:
        self.sla.start_sla("rev-1", 60)
        self.sla.clear()
        assert len(self.sla.get_all_slas()) == 0


# ═══════════════════════════════════════════════════════════════════════════════
# ConflictResolutionManager
# ═══════════════════════════════════════════════════════════════════════════════


class TestConflictResolutionManager:
    def setup_method(self) -> None:
        self.resolver = ConflictResolutionManager()

    def test_resolve_conflicting_reviews_approve(self) -> None:
        result = self.resolver.resolve_conflicting_reviews(["r1", "r2"], 3, 1, "vote")
        assert result.outcome == "APPROVED"
        assert len(result.review_ids) == 2

    def test_resolve_conflicting_reviews_reject(self) -> None:
        result = self.resolver.resolve_conflicting_reviews(["r1", "r2"], 1, 3, "vote")
        assert result.outcome == "REJECTED"

    def test_resolve_conflicting_reviews_tie(self) -> None:
        result = self.resolver.resolve_conflicting_reviews(["r1", "r2"], 2, 2, "vote")
        assert result.outcome == "TIE_BROKEN"
        assert result.tie_broken is True

    def test_resolve_tie_vote(self) -> None:
        result = self.resolver.resolve_tie_vote(["r1", "r2"], "MANAGER")
        assert result.outcome == "TIE_BROKEN"
        assert result.tie_broken is True
        assert result.tie_breaker_role == "MANAGER"

    def test_resolve_tie_vote_custom_role(self) -> None:
        result = self.resolver.resolve_tie_vote(["r1"], "ADMIN")
        assert result.tie_breaker_role == "ADMIN"

    def test_resolve_split_decision(self) -> None:
        decisions = [{"outcome": "APPROVED"}, {"outcome": "APPROVED"}, {"outcome": "REJECTED"}]
        result = self.resolver.resolve_split_decision(decisions)
        assert result.outcome == "APPROVED"
        assert result.votes_for == 2
        assert result.votes_against == 1

    def test_resolve_split_decision_tie(self) -> None:
        decisions = [{"outcome": "APPROVED"}, {"outcome": "REJECTED"}]
        result = self.resolver.resolve_split_decision(decisions)
        assert result.votes_for == 1
        assert result.votes_against == 1

    def test_get_conflicts(self) -> None:
        self.resolver.resolve_conflicting_reviews(["r1", "r2"], 3, 1)
        conflicts = self.resolver.get_conflicts("r1")
        assert len(conflicts) == 1

    def test_get_conflicts_none(self) -> None:
        assert len(self.resolver.get_conflicts("nonexistent")) == 0

    def test_get_all_conflicts(self) -> None:
        self.resolver.resolve_conflicting_reviews(["r1", "r2"], 3, 1)
        self.resolver.resolve_conflicting_reviews(["r3", "r4"], 1, 3)
        assert len(self.resolver.get_all_conflicts()) == 2

    def test_clear(self) -> None:
        self.resolver.resolve_conflicting_reviews(["r1", "r2"], 3, 1)
        self.resolver.clear()
        assert len(self.resolver.get_all_conflicts()) == 0


# ═══════════════════════════════════════════════════════════════════════════════
# ReviewTimeline
# ═══════════════════════════════════════════════════════════════════════════════


class TestReviewTimeline:
    def setup_method(self) -> None:
        self.timeline = ReviewTimeline()
        self.review_id = str(uuid.uuid4())

    def test_record_submitted(self) -> None:
        event = self.timeline.record_submitted(self.review_id, "user-1", "Review submitted")
        assert event.event_type == "submitted"
        assert event.review_id == self.review_id

    def test_record_assigned(self) -> None:
        event = self.timeline.record_assigned(self.review_id, "user-1", "Assigned to reviewer")
        assert event.event_type == "assigned"

    def test_record_started(self) -> None:
        event = self.timeline.record_started(self.review_id, "user-1", "Review started")
        assert event.event_type == "started"

    def test_record_modified(self) -> None:
        event = self.timeline.record_modified(self.review_id, "user-1", "Narrative modified")
        assert event.event_type == "modified"

    def test_record_approved(self) -> None:
        event = self.timeline.record_approved(self.review_id, "user-1", "Review approved")
        assert event.event_type == "approved"

    def test_record_rejected(self) -> None:
        event = self.timeline.record_rejected(self.review_id, "user-1", "Review rejected")
        assert event.event_type == "rejected"

    def test_record_escalated(self) -> None:
        event = self.timeline.record_escalated(self.review_id, "user-1", "Escalated to manager")
        assert event.event_type == "escalated"

    def test_record_event_custom(self) -> None:
        event = self.timeline.record_event(self.review_id, "COMMENTED", "user-1", "Comment added")
        assert event.event_type == "COMMENTED"

    def test_get_timeline_chronological(self) -> None:
        self.timeline.record_submitted(self.review_id, "sys")
        self.timeline.record_approved(self.review_id, "user-1")
        timeline = self.timeline.get_timeline(self.review_id)
        assert len(timeline) == 2
        assert timeline[0].event_type == "submitted"

    def test_get_timeline_empty(self) -> None:
        assert len(self.timeline.get_timeline("nonexistent")) == 0

    def test_get_events_by_type(self) -> None:
        self.timeline.record_submitted(self.review_id, "sys")
        self.timeline.record_approved(self.review_id, "user-1")
        self.timeline.record_submitted(str(uuid.uuid4()), "sys")
        events = self.timeline.get_events_by_type(self.review_id, "submitted")
        assert len(events) == 1

    def test_get_all_events(self) -> None:
        self.timeline.record_submitted(self.review_id, "sys")
        self.timeline.record_submitted(str(uuid.uuid4()), "sys")
        assert len(self.timeline.get_all_events()) == 2

    def test_clear(self) -> None:
        self.timeline.record_submitted(self.review_id, "sys")
        self.timeline.clear()
        assert len(self.timeline.get_all_events()) == 0


# ═══════════════════════════════════════════════════════════════════════════════
# ReviewChecklist
# ═══════════════════════════════════════════════════════════════════════════════


class TestReviewChecklist:
    def setup_method(self) -> None:
        self.checklist = ReviewChecklist()
        self.review_id = str(uuid.uuid4())

    def test_initialize_checklist(self) -> None:
        items = self.checklist.initialize_checklist(self.review_id)
        assert len(items) == 5
        names = {i.item_name for i in items}
        assert "Evidence Reviewed" in names
        assert "Explanation Reviewed" in names
        assert "Policies Reviewed" in names
        assert "Risk Reviewed" in names
        assert "Recommendation Reviewed" in names

    def test_initialize_checklist_idempotent(self) -> None:
        self.checklist.initialize_checklist(self.review_id)
        items = self.checklist.initialize_checklist(self.review_id)
        assert len(items) == 5

    def test_complete_item(self) -> None:
        self.checklist.initialize_checklist(self.review_id)
        assert self.checklist.complete_item(self.review_id, "Evidence Reviewed", "user-1") is True

    def test_complete_item_nonexistent(self) -> None:
        self.checklist.initialize_checklist(self.review_id)
        assert self.checklist.complete_item(self.review_id, "Nonexistent Item", "user-1") is False

    def test_is_item_complete(self) -> None:
        self.checklist.initialize_checklist(self.review_id)
        assert self.checklist.is_item_complete(self.review_id, "Evidence Reviewed") is False
        self.checklist.complete_item(self.review_id, "Evidence Reviewed", "user-1")
        assert self.checklist.is_item_complete(self.review_id, "Evidence Reviewed") is True

    def test_is_checklist_complete_partial(self) -> None:
        self.checklist.initialize_checklist(self.review_id)
        self.checklist.complete_item(self.review_id, "Evidence Reviewed", "user-1")
        assert self.checklist.is_checklist_complete(self.review_id) is False

    def test_is_checklist_complete_full(self) -> None:
        self.checklist.initialize_checklist(self.review_id)
        for name in ["Evidence Reviewed", "Explanation Reviewed", "Policies Reviewed", "Risk Reviewed", "Recommendation Reviewed"]:
            self.checklist.complete_item(self.review_id, name, "user-1")
        assert self.checklist.is_checklist_complete(self.review_id) is True

    def test_get_checklist(self) -> None:
        self.checklist.initialize_checklist(self.review_id)
        items = self.checklist.get_checklist(self.review_id)
        assert len(items) == 5

    def test_get_summary(self) -> None:
        self.checklist.initialize_checklist(self.review_id)
        summary = self.checklist.get_summary(self.review_id)
        assert summary["total"] == 5
        assert summary["completed"] == 0
        assert summary["complete"] is False

    def test_add_custom_item(self) -> None:
        self.checklist.initialize_checklist(self.review_id)
        item = self.checklist.add_custom_item(self.review_id, "Security Reviewed", "Check security compliance", True)
        assert item.item_name == "Security Reviewed"
        assert item.required is True
        assert len(self.checklist.get_checklist(self.review_id)) == 6

    def test_remove_item(self) -> None:
        self.checklist.initialize_checklist(self.review_id)
        self.checklist.add_custom_item(self.review_id, "Security Reviewed", "Check security", required=False)
        assert self.checklist.remove_item(self.review_id, "Security Reviewed") is True
        assert len(self.checklist.get_checklist(self.review_id)) == 5

    def test_remove_item_nonexistent(self) -> None:
        self.checklist.initialize_checklist(self.review_id)
        assert self.checklist.remove_item(self.review_id, "Nonexistent") is False

    def test_clear(self) -> None:
        self.checklist.initialize_checklist(self.review_id)
        self.checklist.clear()
        assert len(self.checklist.get_checklist(self.review_id)) == 0


# ═══════════════════════════════════════════════════════════════════════════════
# GovernanceMetrics
# ═══════════════════════════════════════════════════════════════════════════════


class TestGovernanceMetrics:
    def setup_method(self) -> None:
        self.metrics = GovernanceMetrics()

    def test_defaults(self) -> None:
        assert self.metrics.get_approval_rate() == 0.0
        assert self.metrics.get_rejection_rate() == 0.0
        assert self.metrics.get_escalation_rate() == 0.0
        assert self.metrics.get_average_review_time() == 0.0
        assert self.metrics.get_sla_compliance_rate() == 0.0

    def test_record_approval(self) -> None:
        self.metrics.record_approval("ENERGY", "ENGINEER")
        assert self.metrics.get_approval_rate() == 100.0

    def test_record_rejection(self) -> None:
        self.metrics.record_rejection("ENERGY", "MANAGER")
        assert self.metrics.get_rejection_rate() == 100.0
        assert self.metrics.snapshot().rejected_total == 1

    def test_record_escalation(self) -> None:
        self.metrics.record_escalation("ENERGY", "SUPERVISOR")
        assert self.metrics.get_escalation_rate() == 100.0

    def test_record_modification(self) -> None:
        self.metrics.record_modification("ENERGY", "ENGINEER")
        snap = self.metrics.snapshot()
        assert snap.modified_total == 1

    def test_multiple_outcomes(self) -> None:
        self.metrics.record_approval("ENERGY")
        self.metrics.record_approval("ENERGY")
        self.metrics.record_rejection("ENERGY")
        self.metrics.record_escalation("ENERGY")
        assert self.metrics.get_approval_rate() == 50.0
        assert self.metrics.get_rejection_rate() == 25.0
        assert self.metrics.get_escalation_rate() == 25.0

    def test_record_review_time(self) -> None:
        self.metrics.record_review_time(100.0)
        self.metrics.record_review_time(200.0)
        assert self.metrics.get_average_review_time() == 150.0

    def test_record_sla_compliance(self) -> None:
        self.metrics.record_sla_compliance(True)
        self.metrics.record_sla_compliance(True)
        self.metrics.record_sla_compliance(False)
        assert self.metrics.get_sla_compliance_rate() == pytest.approx(66.6667, rel=0.01)
        assert self.metrics.snapshot().sla_breaches == 1

    def test_snapshot(self) -> None:
        self.metrics.record_approval("ENERGY")
        self.metrics.record_review_time(50.0)
        snap = self.metrics.snapshot()
        assert isinstance(snap, GovernanceMetricsSnapshot)
        assert snap.reviews_total == 1
        assert snap.approval_rate == 100.0
        assert snap.average_review_time_ms == 50.0

    def test_snapshot_review_totals(self) -> None:
        self.metrics.record_approval("SAFETY", "ADMIN")
        self.metrics.record_rejection("ENERGY", "ENGINEER")
        self.metrics.record_escalation("COMPLIANCE", "AUDITOR")
        self.metrics.record_modification("GENERAL", "SUPERVISOR")
        snap = self.metrics.snapshot()
        assert snap.reviews_total == 4
        assert snap.approved_total == 1
        assert snap.rejected_total == 1
        assert snap.escalated_total == 1
        assert snap.modified_total == 1

    def test_reset(self) -> None:
        self.metrics.record_approval("ENERGY")
        self.metrics.record_review_time(100.0)
        self.metrics.reset()
        assert self.metrics.get_approval_rate() == 0.0
        assert self.metrics.get_average_review_time() == 0.0
        assert self.metrics.get_sla_compliance_rate() == 0.0


# ═══════════════════════════════════════════════════════════════════════════════
# ReviewTrace
# ═══════════════════════════════════════════════════════════════════════════════


class TestReviewTrace:
    def setup_method(self) -> None:
        self.trace = ReviewTrace()
        self.review_id = str(uuid.uuid4())

    def test_record(self) -> None:
        t = TraceRecord(review_id=self.review_id, stage_name="init", operation="start")
        self.trace.record(t)
        assert self.trace.count() == 1

    def test_record_assignment(self) -> None:
        t = self.trace.record_assignment(self.review_id, "user-1", "corr-1")
        assert t.stage_name == "assignment"
        assert t.operation == "assignment"
        assert t.review_id == self.review_id

    def test_record_policy(self) -> None:
        t = self.trace.record_policy(self.review_id, "policy evaluated", "corr-1")
        assert t.stage_name == "policy"
        assert t.operation == "policy"

    def test_record_workflow(self) -> None:
        t = self.trace.record_workflow(self.review_id, "user-1", "corr-1")
        assert t.stage_name == "workflow"
        assert t.operation == "workflow"

    def test_record_decision(self) -> None:
        t = self.trace.record_decision(self.review_id, "user-1", "APPROVED", "corr-1")
        assert t.stage_name == "decision"
        assert t.operation == "decision"
        assert "APPROVED" in t.details

    def test_record_escalation(self) -> None:
        t = self.trace.record_escalation(self.review_id, "user-1", "corr-1")
        assert t.stage_name == "escalation"
        assert t.operation == "escalation"

    def test_record_stage(self) -> None:
        t = self.trace.record_stage("custom_stage", self.review_id, "user-1", "custom action")
        assert t.stage_name == "custom_stage"
        assert t.details == "custom action"

    def test_record_stage_with_duration(self) -> None:
        t = self.trace.record_stage("stage", self.review_id, duration_ms=150.0)
        assert t.duration_ms == 150.0

    def test_get_by_review_id(self) -> None:
        self.trace.record_assignment(self.review_id)
        self.trace.record_policy(self.review_id)
        records = self.trace.get_by_review_id(self.review_id)
        assert len(records) == 2

    def test_get_by_review_id_none(self) -> None:
        assert len(self.trace.get_by_review_id("nonexistent")) == 0

    def test_get_by_operation(self) -> None:
        self.trace.record_assignment(self.review_id)
        self.trace.record_decision(self.review_id)
        self.trace.record_assignment(str(uuid.uuid4()))
        records = self.trace.get_by_operation("assignment")
        assert len(records) == 2

    def test_get_by_stage(self) -> None:
        self.trace.record_policy(self.review_id)
        self.trace.record_assignment(self.review_id)
        records = self.trace.get_by_stage("policy")
        assert len(records) == 1

    def test_get_recent(self) -> None:
        for i in range(5):
            self.trace.record_stage(f"stage_{i}", self.review_id)
        recent = self.trace.get_recent(3)
        assert len(recent) == 3

    def test_get_recent_limit(self) -> None:
        for i in range(3):
            self.trace.record_stage("stage", self.review_id)
        assert len(self.trace.get_recent(10)) == 3

    def test_clear(self) -> None:
        self.trace.record_assignment(self.review_id)
        self.trace.clear()
        assert self.trace.count() == 0

    def test_count(self) -> None:
        assert self.trace.count() == 0
        self.trace.record_assignment(self.review_id)
        assert self.trace.count() == 1

    def test_correlation_id_propagation(self) -> None:
        t = self.trace.record_stage("stage", self.review_id, correlation_id="corr-xyz")
        assert t.correlation_id == "corr-xyz"
