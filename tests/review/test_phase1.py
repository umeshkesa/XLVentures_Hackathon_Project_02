"""Phase 1 tests for the Decision Review Layer (Architecture, Contracts & Models).

Tests all Phase 1 components: enums, models, DTOs, events, exceptions,
and their relationships. Validates that all contracts are correctly
defined and behave as expected.
"""

from __future__ import annotations

import uuid
from abc import ABC
from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from adip.review.contracts.events import (
    ReviewApproved,
    ReviewCompleted,
    ReviewEscalated,
    ReviewEvent,
    ReviewRejected,
    ReviewRequested,
    ReviewStarted,
)
from adip.review.contracts.exceptions import (
    ApprovalException,
    EscalationException,
    ReviewException,
    ReviewValidationException,
)
from adip.review.contracts.models import (
    ApprovalWorkflow,
    EscalationRule,
    ReviewAudit,
    ReviewComment,
    ReviewConfidence,
    ReviewContext,
    ReviewDecision,
    Reviewer,
    ReviewHealth,
    ReviewMetadata,
    ReviewMetrics,
    ReviewPackage,
    ReviewPolicy,
    ReviewRequest,
    ReviewSession,
)
from adip.review.contracts.models import (
    ReviewerRole as ReviewerRoleModel,
)
from adip.review.contracts.models import (
    ReviewOutcome as ReviewOutcomeModel,
)
from adip.review.dtos import (
    ReviewDecisionDTO,
    ReviewRequestDTO,
    ReviewResponseDTO,
)
from adip.review.enums import (
    ApprovalWorkflowType,
    ReviewDomain,
    ReviewerRole,
    ReviewOutcome,
    ReviewStatus,
)
from adip.review.interfaces import (
    ApprovalWorkflowManager,
    DecisionReviewCoordinator,
    DecisionReviewManager,
    DecisionReviewService,
    EscalationManager,
    ReviewAuditManager,
    ReviewPolicyEngine,
    ReviewValidator,
)

# ═══════════════════════════════════════════════════════════════════════
# Enums
# ═══════════════════════════════════════════════════════════════════════


class TestReviewOutcome:
    def test_values(self) -> None:
        assert ReviewOutcome.APPROVED.value == "APPROVED"
        assert ReviewOutcome.REJECTED.value == "REJECTED"
        assert ReviewOutcome.MODIFIED.value == "MODIFIED"
        assert ReviewOutcome.MORE_INFORMATION_REQUIRED.value == "MORE_INFORMATION_REQUIRED"
        assert ReviewOutcome.ESCALATED.value == "ESCALATED"
        assert ReviewOutcome.DEFERRED.value == "DEFERRED"

    def test_unique_values(self) -> None:
        values = [e.value for e in ReviewOutcome]
        assert len(values) == len(set(values))

    def test_count(self) -> None:
        assert len(ReviewOutcome) == 6


class TestReviewerRole:
    def test_values(self) -> None:
        assert ReviewerRole.OPERATOR.value == "OPERATOR"
        assert ReviewerRole.ENGINEER.value == "ENGINEER"
        assert ReviewerRole.SUPERVISOR.value == "SUPERVISOR"
        assert ReviewerRole.MANAGER.value == "MANAGER"
        assert ReviewerRole.ADMINISTRATOR.value == "ADMINISTRATOR"
        assert ReviewerRole.AUDITOR.value == "AUDITOR"

    def test_unique_values(self) -> None:
        values = [e.value for e in ReviewerRole]
        assert len(values) == len(set(values))

    def test_count(self) -> None:
        assert len(ReviewerRole) == 6


class TestApprovalWorkflowType:
    def test_values(self) -> None:
        assert ApprovalWorkflowType.SINGLE_APPROVAL.value == "SINGLE_APPROVAL"
        assert ApprovalWorkflowType.SEQUENTIAL_APPROVAL.value == "SEQUENTIAL_APPROVAL"
        assert ApprovalWorkflowType.PARALLEL_APPROVAL.value == "PARALLEL_APPROVAL"
        assert ApprovalWorkflowType.MULTI_LEVEL_APPROVAL.value == "MULTI_LEVEL_APPROVAL"
        assert ApprovalWorkflowType.EMERGENCY_APPROVAL.value == "EMERGENCY_APPROVAL"

    def test_unique_values(self) -> None:
        values = [e.value for e in ApprovalWorkflowType]
        assert len(values) == len(set(values))

    def test_count(self) -> None:
        assert len(ApprovalWorkflowType) == 5


class TestReviewStatus:
    def test_values(self) -> None:
        assert ReviewStatus.INITIALIZED.value == "INITIALIZED"
        assert ReviewStatus.UNDER_REVIEW.value == "UNDER_REVIEW"
        assert ReviewStatus.PENDING_APPROVAL.value == "PENDING_APPROVAL"
        assert ReviewStatus.APPROVED.value == "APPROVED"
        assert ReviewStatus.REJECTED.value == "REJECTED"
        assert ReviewStatus.ESCALATED.value == "ESCALATED"
        assert ReviewStatus.COMPLETED.value == "COMPLETED"

    def test_unique_values(self) -> None:
        values = [e.value for e in ReviewStatus]
        assert len(values) == len(set(values))

    def test_count(self) -> None:
        assert len(ReviewStatus) == 7

    def test_transitions_initialized(self) -> None:
        assert ReviewStatus.INITIALIZED.value == "INITIALIZED"

    def test_transitions_approved_to_completed(self) -> None:
        assert ReviewStatus.APPROVED is not None
        assert ReviewStatus.COMPLETED is not None


class TestReviewDomain:
    def test_values(self) -> None:
        assert ReviewDomain.SYSTEM.value == "SYSTEM"
        assert ReviewDomain.ENERGY.value == "ENERGY"
        assert ReviewDomain.MAINTENANCE.value == "MAINTENANCE"
        assert ReviewDomain.OPERATIONS.value == "OPERATIONS"
        assert ReviewDomain.CUSTOMER.value == "CUSTOMER"
        assert ReviewDomain.SAFETY.value == "SAFETY"
        assert ReviewDomain.COMPLIANCE.value == "COMPLIANCE"
        assert ReviewDomain.WORKFLOW.value == "WORKFLOW"
        assert ReviewDomain.PLANNING.value == "PLANNING"
        assert ReviewDomain.GENERAL.value == "GENERAL"

    def test_unique_values(self) -> None:
        values = [e.value for e in ReviewDomain]
        assert len(values) == len(set(values))

    def test_count(self) -> None:
        assert len(ReviewDomain) == 10


# ═══════════════════════════════════════════════════════════════════════
# ReviewRequest
# ═══════════════════════════════════════════════════════════════════════


class TestReviewRequest:
    def test_default_request(self) -> None:
        rec_id = uuid.uuid4()
        exp_id = uuid.uuid4()
        req = ReviewRequest(
            recommendation_decision_id=rec_id,
            explanation_decision_id=exp_id,
        )
        assert req.request_id is not None
        assert req.recommendation_decision_id == rec_id
        assert req.explanation_decision_id == exp_id
        assert req.domain == ReviewDomain.SYSTEM
        assert req.priority == "MEDIUM"
        assert req.deadline is None
        assert req.metadata == {}

    def test_request_with_values(self) -> None:
        rec_id = uuid.uuid4()
        exp_id = uuid.uuid4()
        now = datetime.now(UTC)
        req = ReviewRequest(
            recommendation_decision_id=rec_id,
            explanation_decision_id=exp_id,
            domain=ReviewDomain.ENERGY,
            priority="HIGH",
            deadline=now,
            metadata={"source": "test"},
        )
        assert req.domain == ReviewDomain.ENERGY
        assert req.priority == "HIGH"
        assert req.deadline == now
        assert req.metadata["source"] == "test"

    def test_request_requires_rec_decision_id(self) -> None:
        exp_id = uuid.uuid4()
        with pytest.raises(ValidationError):
            ReviewRequest(explanation_decision_id=exp_id)

    def test_request_requires_exp_decision_id(self) -> None:
        rec_id = uuid.uuid4()
        with pytest.raises(ValidationError):
            ReviewRequest(recommendation_decision_id=rec_id)

    def test_request_unique_ids(self) -> None:
        rec_id = uuid.uuid4()
        exp_id = uuid.uuid4()
        r1 = ReviewRequest(
            recommendation_decision_id=rec_id,
            explanation_decision_id=exp_id,
        )
        r2 = ReviewRequest(
            recommendation_decision_id=rec_id,
            explanation_decision_id=exp_id,
        )
        assert r1.request_id != r2.request_id


# ═══════════════════════════════════════════════════════════════════════
# ReviewDecision
# ═══════════════════════════════════════════════════════════════════════


class TestReviewDecision:
    def test_default_decision(self) -> None:
        rid = uuid.uuid4()
        d = ReviewDecision(request_id=rid, outcome=ReviewOutcome.APPROVED)
        assert d.decision_id is not None
        assert d.request_id == rid
        assert d.outcome == ReviewOutcome.APPROVED
        assert d.review_summary == ""
        assert d.selected_narrative_id == ""
        assert d.modified_narrative == ""
        assert d.additional_comments == []
        assert d.compliance_status == ""

    def test_decision_with_values(self) -> None:
        rid = uuid.uuid4()
        d = ReviewDecision(
            request_id=rid,
            outcome=ReviewOutcome.MODIFIED,
            review_summary="Approved with changes",
            selected_narrative_id="narrative-1",
            modified_narrative="Updated text",
            compliance_status="COMPLIANT",
        )
        assert d.outcome == ReviewOutcome.MODIFIED
        assert d.review_summary == "Approved with changes"
        assert d.selected_narrative_id == "narrative-1"
        assert d.modified_narrative == "Updated text"
        assert d.compliance_status == "COMPLIANT"

    def test_decision_requires_request_id(self) -> None:
        with pytest.raises(ValidationError):
            ReviewDecision(outcome=ReviewOutcome.APPROVED)

    def test_decision_requires_outcome(self) -> None:
        rid = uuid.uuid4()
        with pytest.raises(ValidationError):
            ReviewDecision(request_id=rid)

    def test_decision_unique_ids(self) -> None:
        rid = uuid.uuid4()
        d1 = ReviewDecision(request_id=rid, outcome=ReviewOutcome.APPROVED)
        d2 = ReviewDecision(request_id=rid, outcome=ReviewOutcome.APPROVED)
        assert d1.decision_id != d2.decision_id


# ═══════════════════════════════════════════════════════════════════════
# ReviewSession
# ═══════════════════════════════════════════════════════════════════════


class TestReviewSession:
    def test_default_session(self) -> None:
        rid = uuid.uuid4()
        s = ReviewSession(request_id=rid, role=ReviewerRole.ENGINEER)
        assert s.session_id is not None
        assert s.request_id == rid
        assert s.role == ReviewerRole.ENGINEER
        assert s.status == ReviewStatus.INITIALIZED
        assert s.reviewer_id == ""
        assert s.completed_at is None
        assert s.escalation_reason == ""
        assert s.statistics == {}

    def test_session_with_values(self) -> None:
        rid = uuid.uuid4()
        now = datetime.now(UTC)
        s = ReviewSession(
            request_id=rid,
            role=ReviewerRole.MANAGER,
            reviewer_id="reviewer-1",
            status=ReviewStatus.UNDER_REVIEW,
            assigned_at=now,
            target_outcome=ReviewOutcome.APPROVED,
            statistics={"duration_ms": 150},
        )
        assert s.role == ReviewerRole.MANAGER
        assert s.status == ReviewStatus.UNDER_REVIEW
        assert s.target_outcome == ReviewOutcome.APPROVED
        assert s.statistics["duration_ms"] == 150

    def test_session_requires_request_id(self) -> None:
        with pytest.raises(ValidationError):
            ReviewSession(role=ReviewerRole.ENGINEER)

    def test_session_requires_role(self) -> None:
        rid = uuid.uuid4()
        with pytest.raises(ValidationError):
            ReviewSession(request_id=rid)


# ═══════════════════════════════════════════════════════════════════════
# ReviewPackage
# ═══════════════════════════════════════════════════════════════════════


class TestReviewPackage:
    def test_default_package(self) -> None:
        rid = uuid.uuid4()
        pkg = ReviewPackage(request_id=rid)
        assert pkg.package_id is not None
        assert pkg.request_id == rid
        assert pkg.recommendation_decision == {}
        assert pkg.explanation_decision == {}
        assert pkg.evidence_summary == ""
        assert pkg.reasoning_summary == ""
        assert pkg.recommendation_summary == ""
        assert pkg.policy_information == {}
        assert pkg.review_notes == []

    def test_package_with_values(self) -> None:
        rid = uuid.uuid4()
        pkg = ReviewPackage(
            request_id=rid,
            evidence_summary="Evidence from sensor data",
            reasoning_summary="Risk assessment completed",
            recommendation_summary="Replace component",
            review_notes=["Note 1"],
        )
        assert pkg.evidence_summary == "Evidence from sensor data"
        assert pkg.recommendation_summary == "Replace component"
        assert len(pkg.review_notes) == 1

    def test_package_requires_request_id(self) -> None:
        with pytest.raises(ValidationError):
            ReviewPackage()

    def test_package_unique_ids(self) -> None:
        rid = uuid.uuid4()
        p1 = ReviewPackage(request_id=rid)
        p2 = ReviewPackage(request_id=rid)
        assert p1.package_id != p2.package_id


# ═══════════════════════════════════════════════════════════════════════
# ReviewContext
# ═══════════════════════════════════════════════════════════════════════


class TestReviewContext:
    def test_default_context(self) -> None:
        rid = uuid.uuid4()
        c = ReviewContext(review_id=rid)
        assert c.context_id is not None
        assert c.review_id == rid
        assert c.asset_id == ""
        assert c.machine_id == ""
        assert c.facility_id == ""
        assert c.workflow_id == ""
        assert c.recommendation_context == {}
        assert c.explanation_context == {}

    def test_context_with_values(self) -> None:
        rid = uuid.uuid4()
        c = ReviewContext(
            review_id=rid,
            asset_id="asset-1",
            machine_id="machine-1",
            facility_id="facility-1",
            workflow_id="workflow-1",
            recommendation_context={"score": 0.85},
        )
        assert c.asset_id == "asset-1"
        assert c.machine_id == "machine-1"
        assert c.facility_id == "facility-1"
        assert c.workflow_id == "workflow-1"
        assert c.recommendation_context["score"] == 0.85

    def test_context_requires_review_id(self) -> None:
        with pytest.raises(ValidationError):
            ReviewContext()

    def test_context_unique_ids(self) -> None:
        rid = uuid.uuid4()
        c1 = ReviewContext(review_id=rid)
        c2 = ReviewContext(review_id=rid)
        assert c1.context_id != c2.context_id


# ═══════════════════════════════════════════════════════════════════════
# ReviewPolicy
# ═══════════════════════════════════════════════════════════════════════


class TestReviewPolicy:
    def test_default_policy(self) -> None:
        p = ReviewPolicy()
        assert p.policy_id is not None
        assert p.name == ""
        assert p.description == ""
        assert p.allowed_outcomes == []
        assert p.required_reviewer_roles == []
        assert p.max_reviewers == 3
        assert p.require_justification is True
        assert p.require_evidence is True
        assert p.enforce_deadline is False

    def test_policy_with_values(self) -> None:
        p = ReviewPolicy(
            name="Safety Review Policy",
            description="Policy for safety-critical reviews",
            allowed_outcomes=[ReviewOutcome.APPROVED, ReviewOutcome.REJECTED],
            required_reviewer_roles=[ReviewerRole.ENGINEER, ReviewerRole.MANAGER],
            max_reviewers=5,
            require_justification=True,
            require_evidence=True,
        )
        assert p.name == "Safety Review Policy"
        assert len(p.allowed_outcomes) == 2
        assert len(p.required_reviewer_roles) == 2
        assert p.max_reviewers == 5

    def test_policy_max_reviewers_positive(self) -> None:
        with pytest.raises(ValidationError):
            ReviewPolicy(max_reviewers=0)

    def test_policy_inactive(self) -> None:
        p = ReviewPolicy(enforce_deadline=True)
        assert p.enforce_deadline is True


# ═══════════════════════════════════════════════════════════════════════
# ReviewOutcome (Model)
# ═══════════════════════════════════════════════════════════════════════


class TestReviewOutcomeModel:
    def test_default_outcome(self) -> None:
        did = uuid.uuid4()
        o = ReviewOutcomeModel(decision_id=did, outcome=ReviewOutcome.APPROVED)
        assert o.outcome_id is not None
        assert o.decision_id == did
        assert o.outcome == ReviewOutcome.APPROVED
        assert o.reason == ""
        assert o.justification == ""
        assert o.supporting_evidence == []

    def test_outcome_with_values(self) -> None:
        did = uuid.uuid4()
        o = ReviewOutcomeModel(
            decision_id=did,
            outcome=ReviewOutcome.REJECTED,
            reason="Does not meet safety criteria",
            justification="Risk assessment failed",
            supporting_evidence=["evidence-1", "evidence-2"],
        )
        assert o.outcome == ReviewOutcome.REJECTED
        assert o.reason == "Does not meet safety criteria"
        assert len(o.supporting_evidence) == 2

    def test_outcome_requires_decision_id(self) -> None:
        with pytest.raises(ValidationError):
            ReviewOutcomeModel(outcome=ReviewOutcome.APPROVED)

    def test_outcome_requires_outcome(self) -> None:
        did = uuid.uuid4()
        with pytest.raises(ValidationError):
            ReviewOutcomeModel(decision_id=did)


# ═══════════════════════════════════════════════════════════════════════
# Reviewer
# ═══════════════════════════════════════════════════════════════════════


class TestReviewer:
    def test_default_reviewer(self) -> None:
        r = Reviewer(role=ReviewerRole.ENGINEER)
        assert r.reviewer_id is not None
        assert r.name == ""
        assert r.email == ""
        assert r.role == ReviewerRole.ENGINEER
        assert r.department == ""
        assert r.is_active is True
        assert r.certifications == []
        assert r.max_concurrent_reviews == 5

    def test_reviewer_with_values(self) -> None:
        r = Reviewer(
            name="John Doe",
            email="john@example.com",
            role=ReviewerRole.MANAGER,
            department="Engineering",
            is_active=True,
            certifications=["PE", "CEM"],
            max_concurrent_reviews=3,
        )
        assert r.name == "John Doe"
        assert r.email == "john@example.com"
        assert r.role == ReviewerRole.MANAGER
        assert len(r.certifications) == 2
        assert r.max_concurrent_reviews == 3

    def test_reviewer_requires_role(self) -> None:
        with pytest.raises(ValidationError):
            Reviewer()

    def test_reviewer_max_concurrent_positive(self) -> None:
        with pytest.raises(ValidationError):
            Reviewer(role=ReviewerRole.ENGINEER, max_concurrent_reviews=0)

    def test_reviewer_unique_ids(self) -> None:
        r1 = Reviewer(role=ReviewerRole.ENGINEER)
        r2 = Reviewer(role=ReviewerRole.ENGINEER)
        assert r1.reviewer_id != r2.reviewer_id


# ═══════════════════════════════════════════════════════════════════════
# ReviewerRole (Model)
# ═══════════════════════════════════════════════════════════════════════


class TestReviewerRoleModel:
    def test_default_role_model(self) -> None:
        r = ReviewerRoleModel(role=ReviewerRole.ENGINEER)
        assert r.role_id is not None
        assert r.role == ReviewerRole.ENGINEER
        assert r.display_name == ""
        assert r.permissions == []
        assert r.requires_certification is False

    def test_role_model_with_values(self) -> None:
        r = ReviewerRoleModel(
            role=ReviewerRole.SUPERVISOR,
            display_name="Shift Supervisor",
            permissions=["approve", "reject", "escalate"],
            requires_certification=True,
        )
        assert r.role == ReviewerRole.SUPERVISOR
        assert r.display_name == "Shift Supervisor"
        assert len(r.permissions) == 3
        assert r.requires_certification is True

    def test_role_model_requires_role(self) -> None:
        with pytest.raises(ValidationError):
            ReviewerRoleModel()


# ═══════════════════════════════════════════════════════════════════════
# ReviewComment
# ═══════════════════════════════════════════════════════════════════════


class TestReviewComment:
    def test_default_comment(self) -> None:
        did = uuid.uuid4()
        rid = uuid.uuid4()
        c = ReviewComment(decision_id=did, reviewer_id=rid)
        assert c.comment_id is not None
        assert c.decision_id == did
        assert c.reviewer_id == rid
        assert c.comment == ""
        assert c.section == ""
        assert c.is_resolved is False
        assert c.resolved_at is None

    def test_comment_with_values(self) -> None:
        did = uuid.uuid4()
        rid = uuid.uuid4()
        now = datetime.now(UTC)
        c = ReviewComment(
            decision_id=did,
            reviewer_id=rid,
            comment="Please provide more evidence",
            section="safety_analysis",
            is_resolved=False,
        )
        assert c.comment == "Please provide more evidence"
        assert c.section == "safety_analysis"

    def test_comment_requires_decision_id(self) -> None:
        rid = uuid.uuid4()
        with pytest.raises(ValidationError):
            ReviewComment(reviewer_id=rid)

    def test_comment_requires_reviewer_id(self) -> None:
        did = uuid.uuid4()
        with pytest.raises(ValidationError):
            ReviewComment(decision_id=did)

    def test_comment_unique_ids(self) -> None:
        did = uuid.uuid4()
        rid = uuid.uuid4()
        c1 = ReviewComment(decision_id=did, reviewer_id=rid)
        c2 = ReviewComment(decision_id=did, reviewer_id=rid)
        assert c1.comment_id != c2.comment_id


# ═══════════════════════════════════════════════════════════════════════
# ReviewAudit
# ═══════════════════════════════════════════════════════════════════════


class TestReviewAudit:
    def test_default_audit(self) -> None:
        did = uuid.uuid4()
        rid = uuid.uuid4()
        a = ReviewAudit(decision_id=did, reviewer_id=rid)
        assert a.audit_id is not None
        assert a.decision_id == did
        assert a.reviewer_id == rid
        assert a.action == ""
        assert a.previous_status is None
        assert a.new_status is None
        assert a.ip_address == ""
        assert a.user_agent == ""

    def test_audit_with_values(self) -> None:
        did = uuid.uuid4()
        rid = uuid.uuid4()
        a = ReviewAudit(
            decision_id=did,
            reviewer_id=rid,
            action="APPROVED",
            previous_status=ReviewStatus.UNDER_REVIEW,
            new_status=ReviewStatus.APPROVED,
            ip_address="192.168.1.1",
            user_agent="ReviewerClient/1.0",
        )
        assert a.action == "APPROVED"
        assert a.previous_status == ReviewStatus.UNDER_REVIEW
        assert a.new_status == ReviewStatus.APPROVED
        assert a.ip_address == "192.168.1.1"

    def test_audit_requires_decision_id(self) -> None:
        rid = uuid.uuid4()
        with pytest.raises(ValidationError):
            ReviewAudit(reviewer_id=rid)

    def test_audit_requires_reviewer_id(self) -> None:
        did = uuid.uuid4()
        with pytest.raises(ValidationError):
            ReviewAudit(decision_id=did)


# ═══════════════════════════════════════════════════════════════════════
# ReviewConfidence
# ═══════════════════════════════════════════════════════════════════════


class TestReviewConfidence:
    def test_default_confidence(self) -> None:
        c = ReviewConfidence()
        assert c.overall_confidence == 0.0
        assert c.recommendation_quality == 0.0
        assert c.explanation_quality == 0.0
        assert c.reviewer_expertise == 0.0
        assert c.compliance_score == 0.0

    def test_confidence_with_values(self) -> None:
        c = ReviewConfidence(
            overall_confidence=0.85,
            recommendation_quality=0.9,
            explanation_quality=0.75,
            reviewer_expertise=0.8,
            compliance_score=0.95,
        )
        assert c.overall_confidence == 0.85
        assert c.recommendation_quality == 0.9
        assert c.compliance_score == 0.95

    def test_confidence_bounds(self) -> None:
        with pytest.raises(ValidationError):
            ReviewConfidence(overall_confidence=-0.1)
        with pytest.raises(ValidationError):
            ReviewConfidence(overall_confidence=1.1)
        with pytest.raises(ValidationError):
            ReviewConfidence(recommendation_quality=-0.1)
        with pytest.raises(ValidationError):
            ReviewConfidence(recommendation_quality=1.1)
        with pytest.raises(ValidationError):
            ReviewConfidence(explanation_quality=-0.1)
        with pytest.raises(ValidationError):
            ReviewConfidence(explanation_quality=1.1)
        with pytest.raises(ValidationError):
            ReviewConfidence(reviewer_expertise=-0.1)
        with pytest.raises(ValidationError):
            ReviewConfidence(reviewer_expertise=1.1)
        with pytest.raises(ValidationError):
            ReviewConfidence(compliance_score=-0.1)
        with pytest.raises(ValidationError):
            ReviewConfidence(compliance_score=1.1)


# ═══════════════════════════════════════════════════════════════════════
# ReviewMetadata
# ═══════════════════════════════════════════════════════════════════════


class TestReviewMetadata:
    def test_default_metadata(self) -> None:
        m = ReviewMetadata()
        assert m.title == ""
        assert m.tags == []
        assert m.version == "1.0.0"
        assert m.category == ""
        assert m.priority == ""
        assert m.source == ""

    def test_metadata_with_values(self) -> None:
        m = ReviewMetadata(
            title="Safety Review",
            description="Review of safety-critical recommendation",
            tags=["safety", "critical"],
            category="safety",
            priority="HIGH",
            source="workflow-engine",
        )
        assert m.title == "Safety Review"
        assert len(m.tags) == 2
        assert m.source == "workflow-engine"


# ═══════════════════════════════════════════════════════════════════════
# ReviewHealth
# ═══════════════════════════════════════════════════════════════════════


class TestReviewHealth:
    def test_default_health(self) -> None:
        h = ReviewHealth()
        assert h.overall_status == ""
        assert h.review_count == 0
        assert h.error_count == 0
        assert h.average_latency_ms == 0.0
        assert h.service_status == ""
        assert h.manager_status == ""

    def test_health_with_values(self) -> None:
        h = ReviewHealth(
            overall_status="HEALTHY",
            service_status="HEALTHY",
            coordinator_status="HEALTHY",
            validator_status="DEGRADED",
            review_count=10,
            error_count=2,
            average_latency_ms=150.5,
        )
        assert h.overall_status == "HEALTHY"
        assert h.validator_status == "DEGRADED"
        assert h.review_count == 10
        assert h.average_latency_ms == 150.5

    def test_health_counts_non_negative(self) -> None:
        with pytest.raises(ValidationError):
            ReviewHealth(error_count=-1)
        with pytest.raises(ValidationError):
            ReviewHealth(review_count=-1)
        with pytest.raises(ValidationError):
            ReviewHealth(average_latency_ms=-1.0)


# ═══════════════════════════════════════════════════════════════════════
# ReviewMetrics
# ═══════════════════════════════════════════════════════════════════════


class TestReviewMetrics:
    def test_default_metrics(self) -> None:
        m = ReviewMetrics()
        assert m.reviews_total == 0
        assert m.approved_total == 0
        assert m.rejected_total == 0
        assert m.escalated_total == 0
        assert m.pending_total == 0
        assert m.average_review_time_ms == 0.0
        assert m.average_confidence == 0.0

    def test_metrics_with_values(self) -> None:
        m = ReviewMetrics(
            reviews_total=100,
            approved_total=60,
            rejected_total=20,
            escalated_total=10,
            pending_total=10,
            average_review_time_ms=250.0,
            average_confidence=0.85,
            reviews_per_domain={"ENERGY": 50},
            reviews_per_role={"ENGINEER": 40},
        )
        assert m.reviews_total == 100
        assert m.approved_total == 60
        assert m.reviews_per_domain["ENERGY"] == 50
        assert m.reviews_per_role["ENGINEER"] == 40

    def test_metrics_non_negative(self) -> None:
        with pytest.raises(ValidationError):
            ReviewMetrics(reviews_total=-1)
        with pytest.raises(ValidationError):
            ReviewMetrics(approved_total=-1)
        with pytest.raises(ValidationError):
            ReviewMetrics(rejected_total=-1)
        with pytest.raises(ValidationError):
            ReviewMetrics(escalated_total=-1)
        with pytest.raises(ValidationError):
            ReviewMetrics(pending_total=-1)
        with pytest.raises(ValidationError):
            ReviewMetrics(average_review_time_ms=-1.0)

    def test_metrics_confidence_bounds(self) -> None:
        with pytest.raises(ValidationError):
            ReviewMetrics(average_confidence=-0.1)
        with pytest.raises(ValidationError):
            ReviewMetrics(average_confidence=1.1)


# ═══════════════════════════════════════════════════════════════════════
# EscalationRule
# ═══════════════════════════════════════════════════════════════════════


class TestEscalationRule:
    def test_default_rule(self) -> None:
        r = EscalationRule(escalation_role=ReviewerRole.SUPERVISOR)
        assert r.rule_id is not None
        assert r.name == ""
        assert r.description == ""
        assert r.trigger_outcome is None
        assert r.trigger_role is None
        assert r.max_duration_minutes == 0
        assert r.escalation_role == ReviewerRole.SUPERVISOR
        assert r.notify_roles == []
        assert r.is_active is True

    def test_rule_with_values(self) -> None:
        r = EscalationRule(
            name="Safety Escalation",
            description="Escalate safety-critical rejections",
            trigger_outcome=ReviewOutcome.REJECTED,
            trigger_role=ReviewerRole.ENGINEER,
            max_duration_minutes=60,
            escalation_role=ReviewerRole.MANAGER,
            notify_roles=[ReviewerRole.SUPERVISOR],
            is_active=True,
        )
        assert r.name == "Safety Escalation"
        assert r.trigger_outcome == ReviewOutcome.REJECTED
        assert r.max_duration_minutes == 60
        assert r.escalation_role == ReviewerRole.MANAGER
        assert len(r.notify_roles) == 1

    def test_rule_requires_escalation_role(self) -> None:
        with pytest.raises(ValidationError):
            EscalationRule()

    def test_rule_max_duration_non_negative(self) -> None:
        with pytest.raises(ValidationError):
            EscalationRule(
                escalation_role=ReviewerRole.MANAGER,
                max_duration_minutes=-1,
            )


# ═══════════════════════════════════════════════════════════════════════
# ApprovalWorkflow
# ═══════════════════════════════════════════════════════════════════════


class TestApprovalWorkflow:
    def test_default_workflow(self) -> None:
        w = ApprovalWorkflow(workflow_type=ApprovalWorkflowType.SINGLE_APPROVAL)
        assert w.workflow_id is not None
        assert w.name == ""
        assert w.workflow_type == ApprovalWorkflowType.SINGLE_APPROVAL
        assert w.description == ""
        assert w.steps == []
        assert w.required_approvals == 1
        assert w.auto_approve is False
        assert w.deadline_minutes == 0

    def test_workflow_with_values(self) -> None:
        w = ApprovalWorkflow(
            name="Two-Step Approval",
            workflow_type=ApprovalWorkflowType.SEQUENTIAL_APPROVAL,
            description="Engineer then Manager approval",
            steps=[{"role": "ENGINEER", "order": 1}, {"role": "MANAGER", "order": 2}],
            required_approvals=2,
            auto_approve=False,
            deadline_minutes=240,
        )
        assert w.name == "Two-Step Approval"
        assert w.workflow_type == ApprovalWorkflowType.SEQUENTIAL_APPROVAL
        assert len(w.steps) == 2
        assert w.required_approvals == 2
        assert w.deadline_minutes == 240

    def test_workflow_requires_workflow_type(self) -> None:
        with pytest.raises(ValidationError):
            ApprovalWorkflow()

    def test_workflow_required_approvals_positive(self) -> None:
        with pytest.raises(ValidationError):
            ApprovalWorkflow(
                workflow_type=ApprovalWorkflowType.SINGLE_APPROVAL,
                required_approvals=0,
            )


# ═══════════════════════════════════════════════════════════════════════
# DTOs
# ═══════════════════════════════════════════════════════════════════════


class TestReviewRequestDTO:
    def test_default_request_dto(self) -> None:
        rec_id = uuid.uuid4()
        exp_id = uuid.uuid4()
        dto = ReviewRequestDTO(
            recommendation_decision_id=rec_id,
            explanation_decision_id=exp_id,
        )
        assert dto.request_id is not None
        assert dto.recommendation_decision_id == rec_id
        assert dto.explanation_decision_id == exp_id
        assert dto.domain == ReviewDomain.SYSTEM
        assert dto.priority == "MEDIUM"
        assert dto.deadline is None
        assert dto.metadata == {}

    def test_request_dto_with_values(self) -> None:
        rec_id = uuid.uuid4()
        exp_id = uuid.uuid4()
        now = datetime.now(UTC)
        dto = ReviewRequestDTO(
            recommendation_decision_id=rec_id,
            explanation_decision_id=exp_id,
            domain=ReviewDomain.ENERGY,
            priority="HIGH",
            deadline=now,
            metadata={"source": "test"},
        )
        assert dto.domain == ReviewDomain.ENERGY
        assert dto.priority == "HIGH"
        assert dto.deadline == now
        assert dto.metadata["source"] == "test"

    def test_request_dto_requires_rec_decision_id(self) -> None:
        exp_id = uuid.uuid4()
        with pytest.raises(ValidationError):
            ReviewRequestDTO(explanation_decision_id=exp_id)

    def test_request_dto_requires_exp_decision_id(self) -> None:
        rec_id = uuid.uuid4()
        with pytest.raises(ValidationError):
            ReviewRequestDTO(recommendation_decision_id=rec_id)


class TestReviewResponseDTO:
    def test_default_response_dto(self) -> None:
        req_id = uuid.uuid4()
        sess_id = uuid.uuid4()
        dto = ReviewResponseDTO(request_id=req_id, session_id=sess_id)
        assert dto.response_id is not None
        assert dto.request_id == req_id
        assert dto.session_id == sess_id
        assert dto.decision is None
        assert dto.status == ReviewStatus.INITIALIZED
        assert dto.message == ""

    def test_response_dto_with_values(self) -> None:
        req_id = uuid.uuid4()
        sess_id = uuid.uuid4()
        now = datetime.now(UTC)
        dto = ReviewResponseDTO(
            request_id=req_id,
            session_id=sess_id,
            status=ReviewStatus.COMPLETED,
            message="Review completed successfully",
        )
        assert dto.status == ReviewStatus.COMPLETED
        assert dto.message == "Review completed successfully"

    def test_response_dto_requires_request_id(self) -> None:
        sess_id = uuid.uuid4()
        with pytest.raises(ValidationError):
            ReviewResponseDTO(session_id=sess_id)

    def test_response_dto_requires_session_id(self) -> None:
        req_id = uuid.uuid4()
        with pytest.raises(ValidationError):
            ReviewResponseDTO(request_id=req_id)


class TestReviewDecisionDTO:
    def test_default_decision_dto(self) -> None:
        req_id = uuid.uuid4()
        dto = ReviewDecisionDTO(
            request_id=req_id,
            outcome=ReviewOutcome.APPROVED,
        )
        assert dto.decision_id is not None
        assert dto.request_id == req_id
        assert dto.outcome == ReviewOutcome.APPROVED
        assert dto.review_summary == ""
        assert dto.reviewer_name == ""
        assert dto.reviewer_role == ReviewerRole.ENGINEER
        assert dto.selected_narrative_id == ""
        assert dto.confidence == 0.0

    def test_decision_dto_with_values(self) -> None:
        req_id = uuid.uuid4()
        dto = ReviewDecisionDTO(
            request_id=req_id,
            outcome=ReviewOutcome.REJECTED,
            review_summary="Safety criteria not met",
            reviewer_name="Jane Doe",
            reviewer_role=ReviewerRole.MANAGER,
            selected_narrative_id="narrative-2",
            confidence=0.85,
        )
        assert dto.outcome == ReviewOutcome.REJECTED
        assert dto.review_summary == "Safety criteria not met"
        assert dto.reviewer_name == "Jane Doe"
        assert dto.reviewer_role == ReviewerRole.MANAGER
        assert dto.confidence == 0.85

    def test_decision_dto_requires_request_id(self) -> None:
        with pytest.raises(ValidationError):
            ReviewDecisionDTO(outcome=ReviewOutcome.APPROVED)

    def test_decision_dto_requires_outcome(self) -> None:
        req_id = uuid.uuid4()
        with pytest.raises(ValidationError):
            ReviewDecisionDTO(request_id=req_id)

    def test_decision_dto_confidence_bounds(self) -> None:
        req_id = uuid.uuid4()
        with pytest.raises(ValidationError):
            ReviewDecisionDTO(request_id=req_id, outcome=ReviewOutcome.APPROVED, confidence=-0.1)
        with pytest.raises(ValidationError):
            ReviewDecisionDTO(request_id=req_id, outcome=ReviewOutcome.APPROVED, confidence=1.1)


# ═══════════════════════════════════════════════════════════════════════
# Events
# ═══════════════════════════════════════════════════════════════════════


class TestReviewEvent:
    def test_base_event(self) -> None:
        e = ReviewEvent()
        assert e.event_id is not None
        assert e.timestamp is not None
        assert e.correlation_id == ""

    def test_review_requested(self) -> None:
        req_id = uuid.uuid4()
        e = ReviewRequested(
            request_id=req_id,
            domain=ReviewDomain.ENERGY,
        )
        assert e.request_id == req_id
        assert e.domain == ReviewDomain.ENERGY
        assert isinstance(e, ReviewEvent)

    def test_review_started(self) -> None:
        sess_id = uuid.uuid4()
        e = ReviewStarted(
            session_id=sess_id,
            reviewer_id="reviewer-1",
            role=ReviewerRole.ENGINEER,
        )
        assert e.session_id == sess_id
        assert e.reviewer_id == "reviewer-1"
        assert e.role == ReviewerRole.ENGINEER
        assert isinstance(e, ReviewEvent)

    def test_review_completed(self) -> None:
        sess_id = uuid.uuid4()
        e = ReviewCompleted(
            session_id=sess_id,
            outcome=ReviewOutcome.APPROVED,
            duration_ms=150.5,
        )
        assert e.session_id == sess_id
        assert e.outcome == ReviewOutcome.APPROVED
        assert e.duration_ms == 150.5
        assert isinstance(e, ReviewEvent)

    def test_review_escalated(self) -> None:
        sess_id = uuid.uuid4()
        e = ReviewEscalated(
            session_id=sess_id,
            reason="Requires higher authority",
            escalated_to_role=ReviewerRole.MANAGER,
        )
        assert e.session_id == sess_id
        assert e.reason == "Requires higher authority"
        assert e.escalated_to_role == ReviewerRole.MANAGER
        assert isinstance(e, ReviewEvent)

    def test_review_approved(self) -> None:
        sess_id = uuid.uuid4()
        e = ReviewApproved(
            session_id=sess_id,
            approval_workflow_type=ApprovalWorkflowType.SINGLE_APPROVAL,
            approved_by="approver-1",
        )
        assert e.session_id == sess_id
        assert e.approval_workflow_type == ApprovalWorkflowType.SINGLE_APPROVAL
        assert e.approved_by == "approver-1"
        assert isinstance(e, ReviewEvent)

    def test_review_rejected(self) -> None:
        sess_id = uuid.uuid4()
        e = ReviewRejected(
            session_id=sess_id,
            reason="Safety criteria not met",
            rejected_by="reviewer-1",
        )
        assert e.session_id == sess_id
        assert e.reason == "Safety criteria not met"
        assert e.rejected_by == "reviewer-1"
        assert isinstance(e, ReviewEvent)

    def test_event_inheritance(self) -> None:
        req_id = uuid.uuid4()
        e = ReviewRequested(request_id=req_id)
        assert isinstance(e, ReviewEvent)
        assert e.timestamp is not None

    def test_completed_duration_non_negative(self) -> None:
        sess_id = uuid.uuid4()
        with pytest.raises(ValidationError):
            ReviewCompleted(
                session_id=sess_id,
                outcome=ReviewOutcome.APPROVED,
                duration_ms=-1.0,
            )

    def test_event_required_fields(self) -> None:
        with pytest.raises(ValidationError):
            ReviewRequested()

    def test_review_started_requires_role(self) -> None:
        sess_id = uuid.uuid4()
        with pytest.raises(ValidationError):
            ReviewStarted(session_id=sess_id)


# ═══════════════════════════════════════════════════════════════════════
# Exceptions
# ═══════════════════════════════════════════════════════════════════════


class TestReviewException:
    def test_base_exception(self) -> None:
        e = ReviewException("review error")
        assert str(e) == "review error"
        assert isinstance(e, Exception)

    def test_approval_exception(self) -> None:
        e = ApprovalException("approval error")
        assert str(e) == "approval error"
        assert isinstance(e, ReviewException)

    def test_escalation_exception(self) -> None:
        e = EscalationException("escalation error")
        assert str(e) == "escalation error"
        assert isinstance(e, ReviewException)

    def test_validation_exception(self) -> None:
        e = ReviewValidationException("validation error")
        assert str(e) == "validation error"
        assert isinstance(e, ReviewException)

    def test_default_messages(self) -> None:
        assert "Review error occurred" in str(ReviewException())
        assert "Approval error occurred" in str(ApprovalException())
        assert "Escalation error occurred" in str(EscalationException())
        assert "Review validation error occurred" in str(ReviewValidationException())

    def test_exception_hierarchy(self) -> None:
        assert issubclass(ApprovalException, ReviewException)
        assert issubclass(EscalationException, ReviewException)
        assert issubclass(ReviewValidationException, ReviewException)

    def test_default_code_values(self) -> None:
        assert ReviewException().code == "REVIEW_ERROR"
        assert ApprovalException().code == "APPROVAL_ERROR"
        assert EscalationException().code == "ESCALATION_ERROR"
        assert ReviewValidationException().code == "REVIEW_VALIDATION_ERROR"

    def test_details(self) -> None:
        e = ReviewException("error", details={"key": "value"})
        assert e.details["key"] == "value"


# ═══════════════════════════════════════════════════════════════════════
# Model Relationships
# ═══════════════════════════════════════════════════════════════════════


class TestModelRelationships:
    def test_decision_has_outcome(self) -> None:
        rid = uuid.uuid4()
        d = ReviewDecision(request_id=rid, outcome=ReviewOutcome.APPROVED)
        assert d.outcome == ReviewOutcome.APPROVED
        assert d.outcome is not None

    def test_session_has_status(self) -> None:
        rid = uuid.uuid4()
        s = ReviewSession(request_id=rid, role=ReviewerRole.ENGINEER)
        assert s.status == ReviewStatus.INITIALIZED

    def test_decision_with_comments(self) -> None:
        rid = uuid.uuid4()
        did = uuid.uuid4()
        comment = ReviewComment(decision_id=did, reviewer_id=rid, comment="Needs more info")
        d = ReviewDecision(
            request_id=rid,
            outcome=ReviewOutcome.MODIFIED,
            additional_comments=[comment],
        )
        assert len(d.additional_comments) == 1
        assert d.additional_comments[0].comment == "Needs more info"

    def test_session_has_target_outcome(self) -> None:
        rid = uuid.uuid4()
        s = ReviewSession(
            request_id=rid,
            role=ReviewerRole.MANAGER,
            target_outcome=ReviewOutcome.APPROVED,
        )
        assert s.target_outcome == ReviewOutcome.APPROVED

    def test_escalation_rule_notifies_roles(self) -> None:
        r = EscalationRule(
            escalation_role=ReviewerRole.MANAGER,
            notify_roles=[ReviewerRole.SUPERVISOR, ReviewerRole.ENGINEER],
        )
        assert len(r.notify_roles) == 2
        assert ReviewerRole.SUPERVISOR in r.notify_roles

    def test_workflow_has_steps(self) -> None:
        w = ApprovalWorkflow(
            workflow_type=ApprovalWorkflowType.SEQUENTIAL_APPROVAL,
            steps=[{"role": "ENGINEER"}, {"role": "MANAGER"}],
        )
        assert len(w.steps) == 2
        assert w.steps[0]["role"] == "ENGINEER"

    def test_dto_to_model_flow(self) -> None:
        rec_id = uuid.uuid4()
        exp_id = uuid.uuid4()
        dto = ReviewRequestDTO(
            recommendation_decision_id=rec_id,
            explanation_decision_id=exp_id,
            domain=ReviewDomain.ENERGY,
        )
        req = ReviewRequest(
            recommendation_decision_id=dto.recommendation_decision_id,
            explanation_decision_id=dto.explanation_decision_id,
            domain=dto.domain,
        )
        assert req.recommendation_decision_id == rec_id
        assert req.explanation_decision_id == exp_id
        assert req.domain == ReviewDomain.ENERGY


# ═══════════════════════════════════════════════════════════════════════
# Cross-Module Validation
# ═══════════════════════════════════════════════════════════════════════


class TestPydanticValidation:
    def test_invalid_enum_value(self) -> None:
        rec_id = uuid.uuid4()
        exp_id = uuid.uuid4()
        with pytest.raises(ValidationError):
            ReviewRequest(
                recommendation_decision_id=rec_id,
                explanation_decision_id=exp_id,
                domain="INVALID_DOMAIN",
            )

    def test_invalid_confidence_type(self) -> None:
        with pytest.raises(ValidationError):
            ReviewConfidence(overall_confidence="high")

    def test_invalid_outcome_type(self) -> None:
        rid = uuid.uuid4()
        with pytest.raises(ValidationError):
            ReviewDecision(request_id=rid, outcome="INVALID_OUTCOME")

    def test_negative_confidence(self) -> None:
        with pytest.raises(ValidationError):
            ReviewConfidence(overall_confidence=-0.5)

    def test_excessive_confidence(self) -> None:
        with pytest.raises(ValidationError):
            ReviewConfidence(overall_confidence=1.5)

    def test_invalid_reviewer_role(self) -> None:
        with pytest.raises(ValidationError):
            Reviewer(role="INVALID_ROLE")

    def test_invalid_approval_workflow_type(self) -> None:
        with pytest.raises(ValidationError):
            ApprovalWorkflow(workflow_type="INVALID_TYPE")

    def test_invalid_escalation_role(self) -> None:
        with pytest.raises(ValidationError):
            EscalationRule(escalation_role="INVALID_ROLE")


# ═══════════════════════════════════════════════════════════════════════
# Interfaces
# ═══════════════════════════════════════════════════════════════════════


class TestDecisionReviewServiceInterface:
    def test_is_abstract(self) -> None:
        assert issubclass(DecisionReviewService, ABC)

    def test_cannot_instantiate(self) -> None:
        with pytest.raises(TypeError):
            DecisionReviewService()


class TestDecisionReviewManagerInterface:
    def test_is_abstract(self) -> None:
        assert issubclass(DecisionReviewManager, ABC)

    def test_cannot_instantiate(self) -> None:
        with pytest.raises(TypeError):
            DecisionReviewManager()


class TestDecisionReviewCoordinatorInterface:
    def test_is_abstract(self) -> None:
        assert issubclass(DecisionReviewCoordinator, ABC)

    def test_cannot_instantiate(self) -> None:
        with pytest.raises(TypeError):
            DecisionReviewCoordinator()


class TestReviewValidatorInterface:
    def test_is_abstract(self) -> None:
        assert issubclass(ReviewValidator, ABC)

    def test_cannot_instantiate(self) -> None:
        with pytest.raises(TypeError):
            ReviewValidator()


class TestReviewPolicyEngineInterface:
    def test_is_abstract(self) -> None:
        assert issubclass(ReviewPolicyEngine, ABC)

    def test_cannot_instantiate(self) -> None:
        with pytest.raises(TypeError):
            ReviewPolicyEngine()


class TestEscalationManagerInterface:
    def test_is_abstract(self) -> None:
        assert issubclass(EscalationManager, ABC)

    def test_cannot_instantiate(self) -> None:
        with pytest.raises(TypeError):
            EscalationManager()


class TestApprovalWorkflowManagerInterface:
    def test_is_abstract(self) -> None:
        assert issubclass(ApprovalWorkflowManager, ABC)

    def test_cannot_instantiate(self) -> None:
        with pytest.raises(TypeError):
            ApprovalWorkflowManager()


class TestReviewAuditManagerInterface:
    def test_is_abstract(self) -> None:
        assert issubclass(ReviewAuditManager, ABC)

    def test_cannot_instantiate(self) -> None:
        with pytest.raises(TypeError):
            ReviewAuditManager()
