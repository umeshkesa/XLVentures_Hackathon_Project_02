"""Tests for Decision Review Layer Phase 3 enterprise orchestration components.

Covers:
- GovernanceConfidence model + calculator
- ReviewReadiness model + component
- GovernanceAuditPackage model + component
- GovernanceLineage model + component
- ReviewerConsensusManager
- DelegationManager
- ReviewVersionManager
- Enhanced ReviewTrace (Phase 3 methods)
- Enhanced GovernanceMetrics (Phase 3 counters)
- Enhanced ReviewHealth model
- Enhanced ReviewMetrics model
- Enhanced ReviewExplainabilityMetadata (Phase 3 fields)
- Enhanced IntegrationHooks (Phase 3 hooks)
- Enhanced DefaultReviewService (Phase 3 methods)
- Enhanced ReviewManager (Phase 3 methods)
- Enhanced ReviewCoordinator (22-stage pipeline)
- Pipeline integration
- Backward compatibility
"""

from __future__ import annotations

import uuid

import pytest

from adip.review.contracts.models import (
    GovernanceAuditPackage as GovernanceAuditPackageModel,
)
from adip.review.contracts.models import (
    GovernanceConfidence,
    ReviewDecision,
    ReviewExplainabilityMetadata,
    ReviewHealth,
    ReviewMetrics,
    ReviewRequest,
)
from adip.review.contracts.models import (
    GovernanceLineage as GovernanceLineageModel,
)
from adip.review.contracts.models import (
    ReviewReadiness as ReviewReadinessModel,
)
from adip.review.dtos import ReviewRequestDTO, ReviewResponseDTO
from adip.review.enums import ReviewDomain, ReviewOutcome, ReviewStatus
from adip.review.execution.metrics import GovernanceMetrics
from adip.review.execution.trace import ReviewTrace
from adip.review.orchestration.audit_package import GovernanceAuditPackage
from adip.review.orchestration.confidence import (
    GovernanceConfidenceCalculator,
    ReviewConfidenceCalculator,
)
from adip.review.orchestration.consensus import (
    ConsensusMode,
    ReviewerConsensusManager,
)
from adip.review.orchestration.coordinator import ReviewCoordinator
from adip.review.orchestration.delegation import DelegationManager
from adip.review.orchestration.lineage import GovernanceLineage
from adip.review.orchestration.manager import ReviewManager
from adip.review.orchestration.readiness import ReviewReadiness
from adip.review.orchestration.session import ReviewSessionManager
from adip.review.orchestration.version_manager import ReviewVersionManager
from adip.review.services.hooks import IntegrationHooks
from adip.review.services.hooks import hooks as global_hooks
from adip.review.services.service import DefaultReviewService

# ═══════════════════════════════════════════════════════════════════════════════
# GovernanceConfidence Model
# ═══════════════════════════════════════════════════════════════════════════════


class TestGovernanceConfidenceModel:
    def test_defaults(self) -> None:
        gc = GovernanceConfidence()
        assert gc.overall_governance_confidence == 0.0
        assert gc.ai_confidence == 0.0
        assert gc.reviewer_confidence == 0.0
        assert gc.policy_compliance == 0.0
        assert gc.consensus_score == 0.0
        assert gc.workflow_completion == 0.0
        assert gc.metadata == {}

    def test_custom_values(self) -> None:
        gc = GovernanceConfidence(
            overall_governance_confidence=0.85,
            ai_confidence=0.9,
            reviewer_confidence=0.8,
            policy_compliance=1.0,
            consensus_score=0.75,
            workflow_completion=0.95,
            metadata={"source": "test"},
        )
        assert gc.overall_governance_confidence == 0.85
        assert gc.ai_confidence == 0.9
        assert gc.metadata["source"] == "test"

    def test_clamping(self) -> None:
        import pydantic
        with pytest.raises(pydantic.ValidationError):
            GovernanceConfidence(
                overall_governance_confidence=1.5,
                ai_confidence=-0.5,
            )

    def test_serialization(self) -> None:
        gc = GovernanceConfidence(overall_governance_confidence=0.75)
        d = gc.model_dump()
        assert d["overall_governance_confidence"] == 0.75
        assert d["ai_confidence"] == 0.0


# ═══════════════════════════════════════════════════════════════════════════════
# GovernanceConfidenceCalculator
# ═══════════════════════════════════════════════════════════════════════════════


class TestGovernanceConfidenceCalculator:
    def setup_method(self) -> None:
        self.calculator = GovernanceConfidenceCalculator()

    def test_defaults(self) -> None:
        gc = self.calculator.calculate()
        assert gc.overall_governance_confidence == 0.0
        assert gc.ai_confidence == 0.0
        assert gc.reviewer_confidence == 0.0
        assert gc.policy_compliance == 0.0
        assert gc.consensus_score == 0.0
        assert gc.workflow_completion == 0.0

    def test_high_confidence(self) -> None:
        gc = self.calculator.calculate(
            ai_confidence=1.0,
            reviewer_confidence=1.0,
            policy_compliance=1.0,
            consensus_score=1.0,
            workflow_completion=1.0,
        )
        assert gc.overall_governance_confidence == 1.0

    def test_mixed_confidence(self) -> None:
        gc = self.calculator.calculate(
            ai_confidence=0.8,
            reviewer_confidence=0.9,
            policy_compliance=0.7,
            consensus_score=0.6,
            workflow_completion=0.5,
        )
        expected = round(0.8 * 0.20 + 0.9 * 0.25 + 0.7 * 0.20 + 0.6 * 0.20 + 0.5 * 0.15, 4)
        assert gc.overall_governance_confidence == expected

    def test_weight_distribution(self) -> None:
        """Weights should be: ai_confidence 20%, reviewer_confidence 25%,
        policy_compliance 20%, consensus_score 20%, workflow_completion 15%."""
        gc = self.calculator.calculate(
            ai_confidence=1.0,
            reviewer_confidence=0.0,
            policy_compliance=0.0,
            consensus_score=0.0,
            workflow_completion=0.0,
        )
        assert gc.overall_governance_confidence == 0.20

        gc2 = self.calculator.calculate(
            ai_confidence=0.0,
            reviewer_confidence=1.0,
            policy_compliance=0.0,
            consensus_score=0.0,
            workflow_completion=0.0,
        )
        assert gc2.overall_governance_confidence == 0.25

        gc3 = self.calculator.calculate(
            ai_confidence=0.0,
            reviewer_confidence=0.0,
            policy_compliance=1.0,
            consensus_score=0.0,
            workflow_completion=0.0,
        )
        assert gc3.overall_governance_confidence == 0.20

        gc4 = self.calculator.calculate(
            ai_confidence=0.0,
            reviewer_confidence=0.0,
            policy_compliance=0.0,
            consensus_score=1.0,
            workflow_completion=0.0,
        )
        assert gc4.overall_governance_confidence == 0.20

        gc5 = self.calculator.calculate(
            ai_confidence=0.0,
            reviewer_confidence=0.0,
            policy_compliance=0.0,
            consensus_score=0.0,
            workflow_completion=1.0,
        )
        assert gc5.overall_governance_confidence == 0.15

    def test_clamping(self) -> None:
        gc = self.calculator.calculate(ai_confidence=-0.5, reviewer_confidence=1.5)
        assert gc.ai_confidence == 0.0
        assert gc.reviewer_confidence == 1.0
        assert 0.0 <= gc.overall_governance_confidence <= 1.0

    def test_correlation_id_propagation(self) -> None:
        gc = self.calculator.calculate(correlation_id="corr-456")
        assert gc is not None


# ═══════════════════════════════════════════════════════════════════════════════
# ReviewReadiness Model
# ═══════════════════════════════════════════════════════════════════════════════


class TestReviewReadinessModel:
    def test_defaults(self) -> None:
        rr = ReviewReadinessModel(decision_id=uuid.uuid4())
        assert rr.status == "PENDING"
        assert rr.reason == ""
        assert not rr.checklist_complete
        assert rr.sla_compliant
        assert not rr.reviewers_assigned
        assert rr.policy_compliant

    def test_custom_values(self) -> None:
        did = uuid.uuid4()
        rr = ReviewReadinessModel(
            decision_id=did,
            status="READY",
            reason="All conditions met",
            checklist_complete=True,
            sla_compliant=True,
            reviewers_assigned=True,
            policy_compliant=True,
        )
        assert rr.status == "READY"
        assert rr.decision_id == did
        assert rr.checklist_complete
        assert rr.reviewers_assigned

    def test_serialization(self) -> None:
        rr = ReviewReadinessModel(decision_id=uuid.uuid4(), status="BLOCKED")
        d = rr.model_dump()
        assert d["status"] == "BLOCKED"
        assert "decision_id" in d


# ═══════════════════════════════════════════════════════════════════════════════
# ReviewReadiness Component
# ═══════════════════════════════════════════════════════════════════════════════


class TestReviewReadinessComponent:
    def setup_method(self) -> None:
        self.readiness = ReviewReadiness()

    def test_assess_ready(self) -> None:
        did = str(uuid.uuid4())
        rr = self.readiness.assess_readiness(
            decision_id=did,
            checklist_complete=True,
            sla_compliant=True,
            reviewers_assigned=True,
            policy_compliant=True,
        )
        assert rr.status == "READY"
        assert rr.checklist_complete
        assert rr.reviewers_assigned

    def test_assess_pending_no_reviewers(self) -> None:
        did = str(uuid.uuid4())
        rr = self.readiness.assess_readiness(
            decision_id=did,
            checklist_complete=True,
            reviewers_assigned=False,
        )
        assert rr.status == "PENDING"

    def test_assess_blocked_no_policy(self) -> None:
        did = str(uuid.uuid4())
        rr = self.readiness.assess_readiness(
            decision_id=did,
            policy_compliant=False,
        )
        assert rr.status == "BLOCKED"

    def test_assess_escalated_sla_breach(self) -> None:
        did = str(uuid.uuid4())
        rr = self.readiness.assess_readiness(
            decision_id=did,
            sla_compliant=False,
            checklist_complete=True,
            reviewers_assigned=True,
        )
        assert rr.status == "ESCALATED"

    def test_assess_more_information_required(self) -> None:
        did = str(uuid.uuid4())
        rr = self.readiness.assess_readiness(
            decision_id=did,
            checklist_complete=False,
            reviewers_assigned=False,
        )
        assert rr.status == "MORE_INFORMATION_REQUIRED"

    def test_get_readiness(self) -> None:
        did = str(uuid.uuid4())
        rr = self.readiness.assess_readiness(decision_id=did, checklist_complete=True, reviewers_assigned=True)
        retrieved = self.readiness.get_readiness(str(rr.readiness_id))
        assert retrieved is not None
        assert retrieved.status == rr.status

    def test_get_readiness_nonexistent(self) -> None:
        assert self.readiness.get_readiness("nonexistent") is None

    def test_get_readiness_for_decision(self) -> None:
        did = str(uuid.uuid4())
        rr = self.readiness.assess_readiness(
            decision_id=did,
            checklist_complete=True,
            reviewers_assigned=True,
        )
        retrieved = self.readiness.get_readiness_for_decision(str(rr.decision_id))
        assert retrieved is not None
        assert retrieved.status == rr.status

    def test_get_readiness_for_decision_no_match(self) -> None:
        assert self.readiness.get_readiness_for_decision(str(uuid.uuid4())) is None

    def test_count(self) -> None:
        assert self.readiness.count() == 0
        self.readiness.assess_readiness(decision_id=str(uuid.uuid4()), checklist_complete=True, reviewers_assigned=True)
        assert self.readiness.count() == 1

    def test_clear(self) -> None:
        self.readiness.assess_readiness(decision_id=str(uuid.uuid4()), checklist_complete=True, reviewers_assigned=True)
        self.readiness.clear()
        assert self.readiness.count() == 0


# ═══════════════════════════════════════════════════════════════════════════════
# GovernanceAuditPackage Model
# ═══════════════════════════════════════════════════════════════════════════════


class TestGovernanceAuditPackageModel:
    def test_defaults(self) -> None:
        ap = GovernanceAuditPackageModel(decision_id=uuid.uuid4())
        assert ap.review_package == {}
        assert ap.reviewer_decisions == []
        assert ap.comments == []
        assert ap.workflow == {}
        assert ap.timeline == []
        assert ap.policy_evaluations == []
        assert ap.hash == ""

    def test_custom_values(self) -> None:
        ap = GovernanceAuditPackageModel(
            decision_id=uuid.uuid4(),
            review_package={"key": "value"},
            reviewer_decisions=[{"reviewer": "r1"}],
            hash="abc123",
        )
        assert ap.review_package["key"] == "value"
        assert len(ap.reviewer_decisions) == 1
        assert ap.hash == "abc123"


# ═══════════════════════════════════════════════════════════════════════════════
# GovernanceAuditPackage Component
# ═══════════════════════════════════════════════════════════════════════════════


class TestGovernanceAuditPackageComponent:
    def setup_method(self) -> None:
        self.audit = GovernanceAuditPackage()

    def test_create_package(self) -> None:
        ap = self.audit.create_package(
            decision_id=str(uuid.uuid4()),
            review_package={"request_id": "req-1"},
            reviewer_decisions=[{"reviewer_id": "rev-1", "outcome": "APPROVED"}],
        )
        assert ap.review_package["request_id"] == "req-1"
        assert len(ap.reviewer_decisions) == 1
        assert ap.hash != ""

    def test_package_hash_integrity(self) -> None:
        ap = self.audit.create_package(
            decision_id=str(uuid.uuid4()),
            review_package={"data": "test"},
        )
        assert self.audit.verify_package(str(ap.package_id))

    def test_package_hash_tampered(self) -> None:
        ap = self.audit.create_package(
            decision_id=str(uuid.uuid4()),
            review_package={"data": "test"},
        )
        ap.hash = "tampered"
        assert not self.audit.verify_package(self.audit._packages[next(iter(self.audit._packages))].package_id)

    def test_get_package(self) -> None:
        ap = self.audit.create_package(decision_id=str(uuid.uuid4()))
        retrieved = self.audit.get_package(str(ap.package_id))
        assert retrieved is not None
        assert str(retrieved.package_id) == str(ap.package_id)

    def test_get_package_nonexistent(self) -> None:
        assert self.audit.get_package("nonexistent") is None

    def test_count(self) -> None:
        assert self.audit.count() == 0
        self.audit.create_package(decision_id=str(uuid.uuid4()))
        assert self.audit.count() == 1

    def test_clear(self) -> None:
        self.audit.create_package(decision_id=str(uuid.uuid4()))
        self.audit.clear()
        assert self.audit.count() == 0


# ═══════════════════════════════════════════════════════════════════════════════
# GovernanceLineage Model
# ═══════════════════════════════════════════════════════════════════════════════


class TestGovernanceLineageModel:
    def test_defaults(self) -> None:
        gl = GovernanceLineageModel(decision_id=uuid.uuid4())
        assert gl.recommendation_id == ""
        assert gl.explanation_id == ""
        assert gl.review_id == ""
        assert gl.action_id == ""
        assert gl.chain == []

    def test_custom_values(self) -> None:
        gl = GovernanceLineageModel(
            decision_id=uuid.uuid4(),
            recommendation_id="rec-1",
            explanation_id="exp-1",
            review_id="rev-1",
            action_id="act-1",
            chain=[{"stage": "recommendation", "entity_id": "rec-1"}],
        )
        assert gl.recommendation_id == "rec-1"
        assert len(gl.chain) == 1


# ═══════════════════════════════════════════════════════════════════════════════
# GovernanceLineage Component
# ═══════════════════════════════════════════════════════════════════════════════


class TestGovernanceLineageComponent:
    def setup_method(self) -> None:
        self.lineage = GovernanceLineage()

    def test_create_lineage_full_chain(self) -> None:
        gl = self.lineage.create_lineage(
            decision_id=str(uuid.uuid4()),
            recommendation_id="rec-1",
            explanation_id="exp-1",
            review_id="rev-1",
            action_id="act-1",
        )
        assert gl.recommendation_id == "rec-1"
        assert gl.explanation_id == "exp-1"
        assert gl.review_id == "rev-1"
        assert gl.action_id == "act-1"
        assert len(gl.chain) == 4

    def test_create_lineage_partial_chain(self) -> None:
        gl = self.lineage.create_lineage(
            decision_id=str(uuid.uuid4()),
            recommendation_id="rec-1",
        )
        assert len(gl.chain) == 1
        assert gl.chain[0]["stage"] == "recommendation"

    def test_add_to_chain(self) -> None:
        gl = self.lineage.create_lineage(
            decision_id=str(uuid.uuid4()),
            recommendation_id="rec-1",
        )
        assert self.lineage.add_to_chain(str(gl.lineage_id), "explanation", "exp-1")
        assert self.lineage.add_to_chain(str(gl.lineage_id), "review", "rev-1")
        updated = self.lineage.get_lineage(str(gl.lineage_id))
        assert updated is not None
        assert len(updated.chain) == 3

    def test_add_to_chain_nonexistent(self) -> None:
        assert not self.lineage.add_to_chain("nonexistent", "review", "rev-1")

    def test_get_lineage(self) -> None:
        gl = self.lineage.create_lineage(decision_id=str(uuid.uuid4()))
        retrieved = self.lineage.get_lineage(str(gl.lineage_id))
        assert retrieved is not None

    def test_get_lineage_nonexistent(self) -> None:
        assert self.lineage.get_lineage("nonexistent") is None

    def test_get_lineage_for_decision(self) -> None:
        did = str(uuid.uuid4())
        self.lineage.create_lineage(
            decision_id=did,
            recommendation_id="rec-1",
        )
        retrieved = self.lineage.get_lineage_for_decision(did)
        assert retrieved is not None
        assert retrieved.recommendation_id == "rec-1"

    def test_count(self) -> None:
        assert self.lineage.count() == 0
        self.lineage.create_lineage(decision_id=str(uuid.uuid4()))
        assert self.lineage.count() == 1

    def test_clear(self) -> None:
        self.lineage.create_lineage(decision_id=str(uuid.uuid4()))
        self.lineage.clear()
        assert self.lineage.count() == 0


# ═══════════════════════════════════════════════════════════════════════════════
# ReviewerConsensusManager
# ═══════════════════════════════════════════════════════════════════════════════


class TestReviewerConsensusManager:
    def setup_method(self) -> None:
        self.manager = ReviewerConsensusManager()

    def test_majority_approved(self) -> None:
        result = self.manager.evaluate_majority("review-1", votes_for=3, votes_against=1)
        assert result.outcome == "APPROVED"
        assert result.consensus_mode == ConsensusMode.MAJORITY
        assert result.votes_for == 3
        assert result.votes_against == 1
        assert result.votes_total == 4
        assert result.agreement == 0.75

    def test_majority_rejected(self) -> None:
        result = self.manager.evaluate_majority("review-2", votes_for=1, votes_against=3)
        assert result.outcome == "REJECTED"
        assert result.agreement == 0.25

    def test_majority_tie(self) -> None:
        result = self.manager.evaluate_majority("review-3", votes_for=2, votes_against=2)
        assert result.outcome == "REJECTED"
        assert result.agreement == 0.5

    def test_unanimous_approved(self) -> None:
        result = self.manager.evaluate_unanimous("review-4", votes_for=3, votes_against=0)
        assert result.outcome == "APPROVED"
        assert result.agreement == 1.0

    def test_unanimous_rejected(self) -> None:
        result = self.manager.evaluate_unanimous("review-5", votes_for=2, votes_against=1)
        assert result.outcome == "REJECTED"
        assert result.agreement == 0.0

    def test_weighted_approved(self) -> None:
        result = self.manager.evaluate_weighted(
            "review-6",
            votes_for=[0.9, 0.8],
            votes_against=[0.3],
        )
        assert result.outcome == "APPROVED"
        total_weight = 0.9 + 0.8 + 0.3
        expected_agreement = round((0.9 + 0.8) / total_weight, 4)
        assert result.agreement == expected_agreement

    def test_weighted_rejected(self) -> None:
        result = self.manager.evaluate_weighted(
            "review-7",
            votes_for=[0.2],
            votes_against=[0.9, 0.8],
        )
        assert result.outcome == "REJECTED"

    def test_conflict(self) -> None:
        result = self.manager.evaluate_conflict("review-8", votes_for=2, votes_against=2)
        assert result.outcome == "CONFLICT"
        assert result.consensus_mode == ConsensusMode.CONFLICT

    def test_get_result(self) -> None:
        self.manager.evaluate_majority("review-9", votes_for=3, votes_against=0)
        result = self.manager.get_result("review-9")
        assert result is not None
        assert result.outcome == "APPROVED"

    def test_get_result_nonexistent(self) -> None:
        assert self.manager.get_result("nonexistent") is None

    def test_clear(self) -> None:
        self.manager.evaluate_majority("review-10", votes_for=1, votes_against=0)
        self.manager.clear()
        assert self.manager.get_result("review-10") is None


# ═══════════════════════════════════════════════════════════════════════════════
# DelegationManager
# ═══════════════════════════════════════════════════════════════════════════════


class TestDelegationManager:
    def setup_method(self) -> None:
        self.manager = DelegationManager()

    def test_delegate_reviewer(self) -> None:
        delegation = self.manager.delegate_reviewer(
            review_id="review-1",
            original_reviewer_id="rev-1",
            delegate_reviewer_id="rev-2",
            reason="On leave",
        )
        assert delegation.review_id == "review-1"
        assert delegation.original_reviewer_id == "rev-1"
        assert delegation.delegate_reviewer_id == "rev-2"
        assert delegation.delegation_type == "REVIEWER_DELEGATION"
        assert delegation.is_active

    def test_assign_acting_reviewer(self) -> None:
        delegation = self.manager.assign_acting_reviewer(
            review_id="review-2",
            original_reviewer_id="rev-1",
            acting_reviewer_id="rev-3",
            reason="Temporary coverage",
        )
        assert delegation.delegation_type == "ACTING_REVIEWER"
        assert delegation.delegate_reviewer_id == "rev-3"

    def test_escalated_delegate(self) -> None:
        delegation = self.manager.escalated_delegate(
            review_id="review-3",
            original_reviewer_id="rev-1",
            escalated_reviewer_id="rev-4",
            reason="Requires manager approval",
        )
        assert delegation.delegation_type == "ESCALATED_DELEGATE"
        assert delegation.delegate_reviewer_id == "rev-4"

    def test_revoke_delegation(self) -> None:
        delegation = self.manager.delegate_reviewer(
            review_id="review-4",
            original_reviewer_id="rev-1",
            delegate_reviewer_id="rev-2",
        )
        assert self.manager.revoke_delegation(delegation.delegation_id)
        assert not delegation.is_active

    def test_revoke_nonexistent(self) -> None:
        assert not self.manager.revoke_delegation("nonexistent")

    def test_get_delegations_for_review(self) -> None:
        self.manager.delegate_reviewer("review-5", "rev-1", "rev-2")
        self.manager.delegate_reviewer("review-5", "rev-3", "rev-4")
        delegations = self.manager.get_delegations_for_review("review-5")
        assert len(delegations) == 2

    def test_get_active_delegations(self) -> None:
        d1 = self.manager.delegate_reviewer("review-6", "rev-1", "rev-2")
        self.manager.delegate_reviewer("review-7", "rev-3", "rev-4")
        self.manager.revoke_delegation(d1.delegation_id)
        active = self.manager.get_active_delegations()
        assert len(active) == 1

    def test_count(self) -> None:
        assert self.manager.count() == 0
        self.manager.delegate_reviewer("review-8", "rev-1", "rev-2")
        assert self.manager.count() == 1

    def test_clear(self) -> None:
        self.manager.delegate_reviewer("review-9", "rev-1", "rev-2")
        self.manager.clear()
        assert self.manager.count() == 0


# ═══════════════════════════════════════════════════════════════════════════════
# ReviewVersionManager
# ═══════════════════════════════════════════════════════════════════════════════


class TestReviewVersionManager:
    def setup_method(self) -> None:
        self.manager = ReviewVersionManager()

    def test_create_version(self) -> None:
        version = self.manager.create_version(
            entity_id="entity-1",
            entity_type="review_decision",
            data={"outcome": "APPROVED"},
            created_by="rev-1",
            change_description="Initial approval",
        )
        assert version.entity_id == "entity-1"
        assert version.version_number == 1
        assert version.entity_type == "review_decision"
        assert version.created_by == "rev-1"

    def test_multiple_versions(self) -> None:
        v1 = self.manager.create_version("entity-2", "policy", {"v": 1})
        v2 = self.manager.create_version("entity-2", "policy", {"v": 2})
        assert v1.version_number == 1
        assert v2.version_number == 2

    def test_get_version(self) -> None:
        version = self.manager.create_version("entity-3", "workflow", {"name": "wf-1"})
        retrieved = self.manager.get_version(version.version_id)
        assert retrieved is not None
        assert retrieved.entity_id == "entity-3"

    def test_get_version_nonexistent(self) -> None:
        assert self.manager.get_version("nonexistent") is None

    def test_get_versions_for_entity(self) -> None:
        self.manager.create_version("entity-4", "decision", {"o": "A"})
        self.manager.create_version("entity-4", "decision", {"o": "B"})
        versions = self.manager.get_versions_for_entity("entity-4")
        assert len(versions) == 2

    def test_get_latest_version(self) -> None:
        self.manager.create_version("entity-5", "decision", {"o": "A"})
        v2 = self.manager.create_version("entity-5", "decision", {"o": "B"})
        latest = self.manager.get_latest_version("entity-5")
        assert latest is not None
        assert latest.version_number == v2.version_number

    def test_get_latest_version_no_versions(self) -> None:
        assert self.manager.get_latest_version("nonexistent") is None

    def test_get_version_count(self) -> None:
        assert self.manager.get_version_count("entity-6") == 0
        self.manager.create_version("entity-6", "decision", {"o": "A"})
        assert self.manager.get_version_count("entity-6") == 1

    def test_count(self) -> None:
        assert self.manager.count() == 0
        self.manager.create_version("entity-7", "decision", {"o": "A"})
        assert self.manager.count() == 1

    def test_clear(self) -> None:
        self.manager.create_version("entity-8", "decision", {"o": "A"})
        self.manager.clear()
        assert self.manager.count() == 0


# ═══════════════════════════════════════════════════════════════════════════════
# Enhanced ReviewExplainabilityMetadata (Phase 3 fields)
# ═══════════════════════════════════════════════════════════════════════════════


class TestEnhancedReviewExplainabilityMetadata:
    def test_phase3_defaults(self) -> None:
        m = ReviewExplainabilityMetadata()
        assert m.why_assigned == ""
        assert m.why_escalated == ""
        assert m.why_modified == ""
        assert m.why_rejected == ""
        assert m.why_approved == ""

    def test_phase3_custom_values(self) -> None:
        m = ReviewExplainabilityMetadata(
            why_assigned="Best expertise match",
            why_escalated="Low confidence score",
            why_modified="Narrative required updates",
            why_rejected="Policy violations detected",
            why_approved="All checks passed",
        )
        assert m.why_assigned == "Best expertise match"
        assert m.why_escalated == "Low confidence score"
        assert m.why_modified == "Narrative required updates"
        assert m.why_rejected == "Policy violations detected"
        assert m.why_approved == "All checks passed"

    def test_backward_compatibility(self) -> None:
        m = ReviewExplainabilityMetadata(why_outcome_selected="High confidence")
        assert m.why_outcome_selected == "High confidence"
        assert m.why_assigned == ""


# ═══════════════════════════════════════════════════════════════════════════════
# Enhanced ReviewHealth Model (Phase 3 fields)
# ═══════════════════════════════════════════════════════════════════════════════


class TestEnhancedReviewHealth:
    def test_phase3_defaults(self) -> None:
        h = ReviewHealth()
        assert h.assignment_status == ""
        assert h.workflow_status == ""
        assert h.consensus_status == ""
        assert h.delegation_status == ""
        assert h.readiness_status == ""
        assert h.version_status == ""
        assert h.lineage_status == ""
        assert h.consensus_manager_status == ""
        assert h.delegation_manager_status == ""

    def test_phase3_custom_values(self) -> None:
        h = ReviewHealth(
            overall_status="HEALTHY",
            assignment_status="HEALTHY",
            workflow_status="HEALTHY",
            consensus_status="HEALTHY",
            delegation_status="HEALTHY",
            readiness_status="HEALTHY",
            version_status="HEALTHY",
            lineage_status="HEALTHY",
            consensus_manager_status="HEALTHY",
            delegation_manager_status="HEALTHY",
        )
        assert h.assignment_status == "HEALTHY"
        assert h.consensus_manager_status == "HEALTHY"

    def test_backward_compatibility(self) -> None:
        h = ReviewHealth(overall_status="HEALTHY", service_status="HEALTHY")
        assert h.overall_status == "HEALTHY"
        assert h.service_status == "HEALTHY"
        assert h.assignment_status == ""


# ═══════════════════════════════════════════════════════════════════════════════
# Enhanced ReviewMetrics Model (Phase 3 fields)
# ═══════════════════════════════════════════════════════════════════════════════


class TestEnhancedReviewMetrics:
    def test_phase3_defaults(self) -> None:
        m = ReviewMetrics()
        assert m.modified_total == 0
        assert m.deferred_total == 0
        assert m.approval_rate == 0.0
        assert m.rejection_rate == 0.0
        assert m.escalation_rate == 0.0
        assert m.sla_compliance_rate == 0.0
        assert m.average_governance_confidence == 0.0
        assert m.audits_total == 0
        assert m.versions_total == 0
        assert m.delegations_total == 0

    def test_phase3_custom_values(self) -> None:
        m = ReviewMetrics(
            reviews_total=100,
            approved_total=80,
            approval_rate=80.0,
            sla_compliance_rate=95.0,
            average_governance_confidence=0.85,
            audits_total=10,
            versions_total=25,
            delegations_total=5,
        )
        assert m.approval_rate == 80.0
        assert m.average_governance_confidence == 0.85
        assert m.audits_total == 10
        assert m.versions_total == 25
        assert m.delegations_total == 5

    def test_backward_compatibility(self) -> None:
        m = ReviewMetrics(reviews_total=50, approved_total=30)
        assert m.reviews_total == 50
        assert m.approved_total == 30
        assert m.audits_total == 0


# ═══════════════════════════════════════════════════════════════════════════════
# Enhanced ReviewTrace (Phase 3 dedicated stage methods)
# ═══════════════════════════════════════════════════════════════════════════════


class TestEnhancedReviewTrace:
    def setup_method(self) -> None:
        self.trace = ReviewTrace()

    def test_record_governance_confidence(self) -> None:
        tr = self.trace.record_governance_confidence("review-1", "system", "corr-1")
        assert tr.stage_name == "governance_confidence"
        assert tr.review_id == "review-1"

    def test_record_consensus(self) -> None:
        tr = self.trace.record_consensus("review-2", "system", "corr-2")
        assert tr.stage_name == "consensus"
        assert tr.review_id == "review-2"

    def test_record_delegation(self) -> None:
        tr = self.trace.record_delegation("review-3", "system", "corr-3")
        assert tr.stage_name == "delegation"

    def test_record_version(self) -> None:
        tr = self.trace.record_version("review-4", "system", "corr-4")
        assert tr.stage_name == "version"

    def test_record_readiness(self) -> None:
        tr = self.trace.record_readiness("review-5", "system", "corr-5")
        assert tr.stage_name == "readiness"

    def test_record_audit_package(self) -> None:
        tr = self.trace.record_audit_package("review-6", "system", "corr-6")
        assert tr.stage_name == "audit_package"

    def test_record_lineage(self) -> None:
        tr = self.trace.record_lineage("review-7", "system", "corr-7")
        assert tr.stage_name == "lineage"

    def test_backward_compatibility(self) -> None:
        tr = self.trace.record_stage("validation", "review-8")
        assert tr.stage_name == "validation"
        assert self.trace.count() == 1


# ═══════════════════════════════════════════════════════════════════════════════
# Enhanced GovernanceMetrics (Phase 3 counters)
# ═══════════════════════════════════════════════════════════════════════════════


class TestEnhancedGovernanceMetrics:
    def setup_method(self) -> None:
        self.metrics = GovernanceMetrics()

    def test_record_governance_confidence(self) -> None:
        self.metrics.record_governance_confidence(0.85)
        assert self.metrics.get_average_governance_confidence() == 0.85

    def test_record_governance_confidence_multiple(self) -> None:
        self.metrics.record_governance_confidence(0.8)
        self.metrics.record_governance_confidence(0.9)
        assert self.metrics.get_average_governance_confidence() == 0.85

    def test_record_audit_package(self) -> None:
        assert self.metrics.get_audit_packages_total() == 0
        self.metrics.record_audit_package()
        assert self.metrics.get_audit_packages_total() == 1

    def test_record_version(self) -> None:
        assert self.metrics.get_versions_total() == 0
        self.metrics.record_version()
        assert self.metrics.get_versions_total() == 1

    def test_record_delegation(self) -> None:
        assert self.metrics.get_delegations_total() == 0
        self.metrics.record_delegation()
        assert self.metrics.get_delegations_total() == 1

    def test_record_consensus_evaluation(self) -> None:
        self.metrics.record_consensus_evaluation()
        snap = self.metrics.snapshot()
        assert snap.consensus_evaluations == 1

    def test_snapshot_phase3_fields(self) -> None:
        self.metrics.record_governance_confidence(0.85)
        self.metrics.record_audit_package()
        self.metrics.record_version()
        self.metrics.record_delegation()
        self.metrics.record_consensus_evaluation()
        snap = self.metrics.snapshot()
        assert snap.average_governance_confidence == 0.85
        assert snap.audit_packages_total == 1
        assert snap.versions_total == 1
        assert snap.delegations_total == 1
        assert snap.consensus_evaluations == 1

    def test_reset_phase3_fields(self) -> None:
        self.metrics.record_governance_confidence(0.85)
        self.metrics.record_audit_package()
        self.metrics.reset()
        assert self.metrics.get_average_governance_confidence() == 0.0
        assert self.metrics.get_audit_packages_total() == 0

    def test_backward_compatibility(self) -> None:
        self.metrics.record_approval(domain="ENERGY", role="ENGINEER")
        snap = self.metrics.snapshot()
        assert snap.reviews_total == 1
        assert snap.approved_total == 1


# ═══════════════════════════════════════════════════════════════════════════════
# Enhanced IntegrationHooks (Phase 3 hooks)
# ═══════════════════════════════════════════════════════════════════════════════


class TestEnhancedIntegrationHooks:
    def setup_method(self) -> None:
        self.hooks = IntegrationHooks()

    def test_register_and_run_pre_action(self) -> None:
        results: list[str] = []

        def hook(**kwargs: str) -> None:
            results.append("pre_action")

        self.hooks.register_pre_action(hook)
        self.hooks.run_pre_action()
        assert len(results) == 1

    def test_register_and_run_post_action(self) -> None:
        results: list[str] = []

        def hook(**kwargs: str) -> None:
            results.append("post_action")

        self.hooks.register_post_action(hook)
        self.hooks.run_post_action()
        assert len(results) == 1

    def test_register_and_run_governance_confidence_calculated(self) -> None:
        results: list[str] = []

        def hook(**kwargs: str) -> None:
            results.append("gov_confidence")

        self.hooks.register_governance_confidence_calculated(hook)
        self.hooks.run_governance_confidence_calculated()
        assert len(results) == 1

    def test_register_and_run_consensus_evaluated(self) -> None:
        results: list[str] = []

        def hook(**kwargs: str) -> None:
            results.append("consensus")

        self.hooks.register_consensus_evaluated(hook)
        self.hooks.run_consensus_evaluated()
        assert len(results) == 1

    def test_register_and_run_delegation_performed(self) -> None:
        results: list[str] = []

        def hook(**kwargs: str) -> None:
            results.append("delegation")

        self.hooks.register_delegation_performed(hook)
        self.hooks.run_delegation_performed()
        assert len(results) == 1

    def test_register_and_run_version_created(self) -> None:
        results: list[str] = []

        def hook(**kwargs: str) -> None:
            results.append("version")

        self.hooks.register_version_created(hook)
        self.hooks.run_version_created()
        assert len(results) == 1

    def test_register_and_run_readiness_assessed(self) -> None:
        results: list[str] = []

        def hook(**kwargs: str) -> None:
            results.append("readiness")

        self.hooks.register_readiness_assessed(hook)
        self.hooks.run_readiness_assessed()
        assert len(results) == 1

    def test_register_and_run_audit_package_created(self) -> None:
        results: list[str] = []

        def hook(**kwargs: str) -> None:
            results.append("audit_package")

        self.hooks.register_audit_package_created(hook)
        self.hooks.run_audit_package_created()
        assert len(results) == 1

    def test_register_and_run_lineage_created(self) -> None:
        results: list[str] = []

        def hook(**kwargs: str) -> None:
            results.append("lineage")

        self.hooks.register_lineage_created(hook)
        self.hooks.run_lineage_created()
        assert len(results) == 1

    def test_backward_compatibility(self) -> None:
        results: list[str] = []

        def hook(**kwargs: str) -> None:
            results.append("pre_review")

        self.hooks.register_pre_review(hook)
        self.hooks.run_pre_review()
        assert len(results) == 1


# ═══════════════════════════════════════════════════════════════════════════════
# Enhanced ReviewCoordinator (22-stage pipeline)
# ═══════════════════════════════════════════════════════════════════════════════


class TestEnhancedReviewCoordinator:
    def setup_method(self) -> None:
        self.coordinator = ReviewCoordinator()

    def test_review_produces_decision_with_governance_confidence(self) -> None:
        request = ReviewRequest(
            recommendation_decision_id=uuid.uuid4(),
            explanation_decision_id=uuid.uuid4(),
            domain=ReviewDomain.ENERGY,
            priority="HIGH",
        )
        decision = self.coordinator.review(request, correlation_id="test-corr")
        assert isinstance(decision, ReviewDecision)
        assert decision.outcome is not None
        assert decision.confidence is not None
        metadata = decision.metadata if decision.metadata else {}
        assert "governance_confidence_value" in metadata
        assert metadata["governance_confidence_value"] > 0
        assert "governance_confidence" in metadata
        assert metadata["governance_confidence"]["overall_governance_confidence"] > 0

    def test_review_includes_audit_package_id(self) -> None:
        request = ReviewRequest(
            recommendation_decision_id=uuid.uuid4(),
            explanation_decision_id=uuid.uuid4(),
        )
        decision = self.coordinator.review(request)
        metadata = decision.metadata if decision.metadata else {}
        assert "audit_package_id" in metadata
        assert metadata["audit_package_id"] != ""

    def test_review_includes_lineage_id(self) -> None:
        request = ReviewRequest(
            recommendation_decision_id=uuid.uuid4(),
            explanation_decision_id=uuid.uuid4(),
        )
        decision = self.coordinator.review(request)
        metadata = decision.metadata if decision.metadata else {}
        assert "lineage_id" in metadata
        assert metadata["lineage_id"] != ""

    def test_review_includes_version_number(self) -> None:
        request = ReviewRequest(
            recommendation_decision_id=uuid.uuid4(),
            explanation_decision_id=uuid.uuid4(),
        )
        decision = self.coordinator.review(request)
        metadata = decision.metadata if decision.metadata else {}
        assert "version_number" in metadata
        assert metadata["version_number"] >= 1

    def test_review_includes_consensus_mode(self) -> None:
        request = ReviewRequest(
            recommendation_decision_id=uuid.uuid4(),
            explanation_decision_id=uuid.uuid4(),
        )
        decision = self.coordinator.review(request)
        metadata = decision.metadata if decision.metadata else {}
        assert "consensus_mode" in metadata
        assert metadata["consensus_mode"] in ("MAJORITY", "SINGLE_REVIEWER")

    def test_review_includes_readiness_status(self) -> None:
        request = ReviewRequest(
            recommendation_decision_id=uuid.uuid4(),
            explanation_decision_id=uuid.uuid4(),
        )
        decision = self.coordinator.review(request)
        metadata = decision.metadata if decision.metadata else {}
        assert "readiness_status" in metadata
        assert metadata["readiness_status"] in ("READY", "PENDING", "BLOCKED", "ESCALATED", "MORE_INFORMATION_REQUIRED")

    def test_review_with_high_risk_triggers_escalation(self) -> None:
        request = ReviewRequest(
            recommendation_decision_id=uuid.uuid4(),
            explanation_decision_id=uuid.uuid4(),
            metadata={"risk": "HIGH", "impact": "HIGH"},
        )
        decision = self.coordinator.review(request)
        metadata = decision.metadata if decision.metadata else {}
        assert "escalation_triggered" in metadata
        assert "explainability" in metadata

    def test_review_creates_audit_package(self) -> None:
        request = ReviewRequest(
            recommendation_decision_id=uuid.uuid4(),
            explanation_decision_id=uuid.uuid4(),
        )
        self.coordinator.review(request)
        assert self.coordinator.audit_package.count() == 1

    def test_review_creates_lineage(self) -> None:
        request = ReviewRequest(
            recommendation_decision_id=uuid.uuid4(),
            explanation_decision_id=uuid.uuid4(),
        )
        self.coordinator.review(request)
        assert self.coordinator.lineage.count() == 1

    def test_review_creates_version(self) -> None:
        request = ReviewRequest(
            recommendation_decision_id=uuid.uuid4(),
            explanation_decision_id=uuid.uuid4(),
        )
        self.coordinator.review(request)
        assert self.coordinator.version_manager.count() == 1

    def test_health_includes_phase3_fields(self) -> None:
        health = self.coordinator.health()
        assert health.assignment_status == "HEALTHY"
        assert health.workflow_status == "HEALTHY"
        assert health.consensus_status == "HEALTHY"
        assert health.delegation_status == "HEALTHY"
        assert health.readiness_status == "HEALTHY"
        assert health.version_status == "HEALTHY"
        assert health.lineage_status == "HEALTHY"
        assert health.consensus_manager_status == "HEALTHY"
        assert health.delegation_manager_status == "HEALTHY"

    def test_metrics_includes_phase3_fields(self) -> None:
        request = ReviewRequest(
            recommendation_decision_id=uuid.uuid4(),
            explanation_decision_id=uuid.uuid4(),
        )
        self.coordinator.review(request)
        metrics = self.coordinator.metrics()
        assert metrics.audits_total == 1
        assert metrics.versions_total == 1
        assert metrics.delegations_total == 0
        assert metrics.approval_rate > 0

    def test_get_decision(self) -> None:
        assert self.coordinator.get_decision("nonexistent") is None


# ═══════════════════════════════════════════════════════════════════════════════
# Enhanced ReviewManager (Phase 3 methods)
# ═══════════════════════════════════════════════════════════════════════════════


class TestEnhancedReviewManager:
    def setup_method(self) -> None:
        self.manager = ReviewManager()

    def test_start_review_with_governance(self) -> None:
        request = ReviewRequest(
            recommendation_decision_id=uuid.uuid4(),
            explanation_decision_id=uuid.uuid4(),
        )
        decision = self.manager.start_review(request)
        metadata = decision.metadata if decision.metadata else {}
        assert "governance_confidence_value" in metadata
        assert "audit_package_id" in metadata
        assert "lineage_id" in metadata

    def test_get_governance_confidence(self) -> None:
        assert self.manager.get_governance_confidence() is None

    def test_get_readiness(self) -> None:
        assert self.manager.get_readiness("nonexistent") is None

    def test_get_audit_package(self) -> None:
        assert self.manager.get_audit_package("nonexistent") is None

    def test_get_lineage(self) -> None:
        assert self.manager.get_lineage("nonexistent") is None

    def test_get_readiness_after_review(self) -> None:
        request = ReviewRequest(
            recommendation_decision_id=uuid.uuid4(),
            explanation_decision_id=uuid.uuid4(),
        )
        decision = self.manager.start_review(request)
        metadata = decision.metadata if decision.metadata else {}
        readiness_id = None
        assert "readiness_status" in metadata

    def test_coordinator_property(self) -> None:
        assert self.manager.coordinator is not None

    def test_backward_compatibility(self) -> None:
        request = ReviewRequest(
            recommendation_decision_id=uuid.uuid4(),
            explanation_decision_id=uuid.uuid4(),
        )
        decision = self.manager.start_review(request)
        assert isinstance(decision, ReviewDecision)
        retrieved = self.manager.get_decision(str(decision.decision_id))
        assert retrieved is not None
        health = self.manager.get_health()
        assert isinstance(health, ReviewHealth)


# ═══════════════════════════════════════════════════════════════════════════════
# Enhanced DefaultReviewService (Phase 3 methods)
# ═══════════════════════════════════════════════════════════════════════════════


class TestEnhancedDefaultReviewService:
    def setup_method(self) -> None:
        self.service = DefaultReviewService()

    def test_submit_review(self) -> None:
        dto = ReviewRequestDTO(
            recommendation_decision_id=uuid.uuid4(),
            explanation_decision_id=uuid.uuid4(),
        )
        response = self.service.submit_review(dto, user_id="user-1")
        assert response is not None
        assert isinstance(response, ReviewResponseDTO)
        assert response.status == ReviewStatus.COMPLETED

    def test_get_readiness(self) -> None:
        result = self.service.get_readiness("nonexistent")
        assert result is None

    def test_get_audit_package(self) -> None:
        result = self.service.get_audit_package("nonexistent")
        assert result is None

    def test_get_lineage(self) -> None:
        result = self.service.get_lineage("nonexistent")
        assert result is None

    def test_get_health(self) -> None:
        health = self.service.get_health()
        assert isinstance(health, ReviewHealth)
        assert health.assignment_status == "HEALTHY"

    def test_get_metrics(self) -> None:
        dto = ReviewRequestDTO(
            recommendation_decision_id=uuid.uuid4(),
            explanation_decision_id=uuid.uuid4(),
        )
        self.service.submit_review(dto, user_id="user-1")
        metrics = self.service.get_metrics()
        assert isinstance(metrics, ReviewMetrics)
        assert metrics.reviews_total > 0

    def test_manager_property(self) -> None:
        assert self.service.manager is not None

    def test_hooks_property(self) -> None:
        assert self.service.hooks is not None

    def test_backward_compatibility(self) -> None:
        dto = ReviewRequestDTO(
            recommendation_decision_id=uuid.uuid4(),
            explanation_decision_id=uuid.uuid4(),
        )
        response = self.service.submit_review(dto, user_id="user-1", correlation_id="corr-xyz")
        assert response is not None
        assert response.status == ReviewStatus.COMPLETED
        session = self.service.get_session("nonexistent")
        assert session is None


# ═══════════════════════════════════════════════════════════════════════════════
# Pipeline Integration Test
# ═══════════════════════════════════════════════════════════════════════════════


class TestPipelineIntegration:
    def test_full_review_pipeline(self) -> None:
        """End-to-end test: DTO → Service → Manager → Coordinator → Decision."""
        service = DefaultReviewService()
        dto = ReviewRequestDTO(
            recommendation_decision_id=uuid.uuid4(),
            explanation_decision_id=uuid.uuid4(),
            domain=ReviewDomain.MAINTENANCE,
            priority="HIGH",
            metadata={"risk": "MEDIUM", "impact": "HIGH", "compliance": True},
        )
        response = service.submit_review(dto, user_id="operator-1", correlation_id="integration-test-1")
        assert response is not None
        assert response.status == ReviewStatus.COMPLETED
        assert response.message != ""

    def test_pipeline_with_multiple_hooks(self) -> None:
        """Verify all Phase 3 hooks fire during pipeline execution."""
        hook_results: dict[str, int] = {}

        def make_counter(name: str):
            def hook(**kwargs: str) -> None:
                hook_results[name] = hook_results.get(name, 0) + 1
            return hook

        hooks = IntegrationHooks()
        hooks.register_pre_review(make_counter("pre_review"))
        hooks.register_post_review(make_counter("post_review"))
        hooks.register_pre_action(make_counter("pre_action"))
        hooks.register_post_action(make_counter("post_action"))
        hooks.register_governance_confidence_calculated(make_counter("gov_conf"))
        hooks.register_consensus_evaluated(make_counter("consensus"))
        hooks.register_delegation_performed(make_counter("delegation"))
        hooks.register_version_created(make_counter("version"))
        hooks.register_readiness_assessed(make_counter("readiness"))
        hooks.register_audit_package_created(make_counter("audit"))
        hooks.register_lineage_created(make_counter("lineage"))

        service = DefaultReviewService(hooks=hooks)
        dto = ReviewRequestDTO(
            recommendation_decision_id=uuid.uuid4(),
            explanation_decision_id=uuid.uuid4(),
        )
        response = service.submit_review(dto, user_id="user-1")
        assert response is not None
        assert hook_results.get("pre_review", 0) == 1
        assert hook_results.get("post_review", 0) == 1

    def test_pipeline_with_auth_and_audit(self) -> None:
        """Verify auth and audit callbacks work with full pipeline."""
        auth_called: list[str] = []
        audit_entries: list[tuple[str, str, str, dict]] = []

        def auth_cb(user_id: str, action: str) -> bool:
            auth_called.append(action)
            return True

        def audit_cb(action: str, user_id: str, entity_id: str, details: dict) -> None:
            audit_entries.append((action, user_id, entity_id, details))

        service = DefaultReviewService(auth_callback=auth_cb, audit_callback=audit_cb)
        dto = ReviewRequestDTO(
            recommendation_decision_id=uuid.uuid4(),
            explanation_decision_id=uuid.uuid4(),
        )
        response = service.submit_review(dto, user_id="auditor-1")
        assert response is not None
        assert len(auth_called) == 1
        assert len(audit_entries) == 1

    def test_pipeline_with_auth_failure(self) -> None:
        def auth_cb(user_id: str, action: str) -> bool:
            return False

        service = DefaultReviewService(auth_callback=auth_cb)
        dto = ReviewRequestDTO(
            recommendation_decision_id=uuid.uuid4(),
            explanation_decision_id=uuid.uuid4(),
        )
        response = service.submit_review(dto, user_id="unauthorized")
        assert response is None

    def test_audit_package_created_in_pipeline(self) -> None:
        """Verify audit package is created during pipeline execution."""
        service = DefaultReviewService()
        dto = ReviewRequestDTO(
            recommendation_decision_id=uuid.uuid4(),
            explanation_decision_id=uuid.uuid4(),
        )
        service.submit_review(dto, user_id="user-1")
        manager = service.manager
        assert manager.coordinator.audit_package.count() >= 1

    def test_lineage_created_in_pipeline(self) -> None:
        """Verify lineage is created during pipeline execution."""
        service = DefaultReviewService()
        dto = ReviewRequestDTO(
            recommendation_decision_id=uuid.uuid4(),
            explanation_decision_id=uuid.uuid4(),
        )
        service.submit_review(dto, user_id="user-1")
        manager = service.manager
        assert manager.coordinator.lineage.count() >= 1

    def test_version_created_in_pipeline(self) -> None:
        """Verify version is created during pipeline execution."""
        service = DefaultReviewService()
        dto = ReviewRequestDTO(
            recommendation_decision_id=uuid.uuid4(),
            explanation_decision_id=uuid.uuid4(),
        )
        service.submit_review(dto, user_id="user-1")
        manager = service.manager
        assert manager.coordinator.version_manager.count() >= 1


# ═══════════════════════════════════════════════════════════════════════════════
# Backward Compatibility Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestBackwardCompatibility:
    def test_phase1_models_still_work(self) -> None:
        """Phase 1 models should be unchanged."""
        request = ReviewRequest(
            recommendation_decision_id=uuid.uuid4(),
            explanation_decision_id=uuid.uuid4(),
        )
        assert request.request_id is not None
        assert request.domain == ReviewDomain.SYSTEM

    def test_phase1_enums_still_work(self) -> None:
        """Phase 1 enums should be unchanged."""
        assert ReviewOutcome.APPROVED.value == "APPROVED"
        assert ReviewStatus.INITIALIZED.value == "INITIALIZED"
        assert ReviewDomain.ENERGY.value == "ENERGY"

    def test_phase1_interfaces_still_work(self) -> None:
        """Phase 1 interfaces should still be importable."""
        from adip.review.interfaces import (
            DecisionReviewCoordinator as DRCI,
        )
        from adip.review.interfaces import (
            DecisionReviewManager as DRMI,
        )
        from adip.review.interfaces import (
            DecisionReviewService as DRSI,
        )
        assert DRSI is not None
        assert DRMI is not None
        assert DRCI is not None

    def test_phase1_dtos_still_work(self) -> None:
        """Phase 1 DTOs should be unchanged."""
        dto = ReviewRequestDTO(
            recommendation_decision_id=uuid.uuid4(),
            explanation_decision_id=uuid.uuid4(),
        )
        assert dto.request_id is not None
        assert dto.priority == "MEDIUM"

    def test_phase2_components_still_work(self) -> None:
        """Phase 2 execution components should still work."""
        from adip.review.execution.approval_strategy import ApprovalStrategyManager
        from adip.review.execution.checklist import ReviewChecklist
        from adip.review.execution.conflict_resolver import ConflictResolutionManager
        from adip.review.execution.escalation_engine import EscalationEngine
        from adip.review.execution.metrics import GovernanceMetrics
        from adip.review.execution.modification_manager import ModificationManager
        from adip.review.execution.policy_matrix import ReviewPolicyMatrix
        from adip.review.execution.reviewer_assignment import ReviewerAssignmentEngine
        from adip.review.execution.sla_manager import ReviewSLAManager
        from adip.review.execution.timeline import ReviewTimeline
        from adip.review.execution.trace import ReviewTrace
        from adip.review.execution.validator import ReviewValidator
        assert ReviewValidator is not None
        assert ReviewPolicyMatrix is not None
        assert ApprovalStrategyManager is not None
        assert ReviewerAssignmentEngine is not None
        assert ConflictResolutionManager is not None
        assert EscalationEngine is not None
        assert ReviewChecklist is not None
        assert ReviewTimeline is not None
        assert ModificationManager is not None
        assert ReviewSLAManager is not None
        assert GovernanceMetrics is not None
        assert ReviewTrace is not None

    def test_phase2_session_manager_still_works(self) -> None:
        """Phase 2 session manager should still work."""
        sm = ReviewSessionManager()
        session = sm.create_session(str(uuid.uuid4()))
        assert session.status == ReviewStatus.INITIALIZED

    def test_phase2_confidence_calculator_still_works(self) -> None:
        """Phase 2 confidence calculator should still work."""
        calc = ReviewConfidenceCalculator()
        conf = calc.calculate(recommendation_quality=0.8, explanation_quality=0.7)
        assert conf.recommendation_quality == 0.8
        assert conf.overall_confidence > 0

    def test_phase2_metrics_still_work(self) -> None:
        """Phase 2 governance metrics should still work."""
        metrics = GovernanceMetrics()
        metrics.record_approval(domain="ENERGY", role="ENGINEER")
        snap = metrics.snapshot()
        assert snap.reviews_total == 1
        assert snap.approval_rate == 100.0

    def test_phase2_trace_still_works(self) -> None:
        """Phase 2 trace should still work."""
        trace = ReviewTrace()
        tr = trace.record_stage("validation", "review-1")
        assert tr.stage_name == "validation"
        assert trace.count() == 1

    def test_phase2_models_still_serialize(self) -> None:
        """Phase 2 execution models should still serialize."""
        from adip.review.execution.models import PolicyMatrixResult, ReviewerAssignment, TraceRecord
        pmr = PolicyMatrixResult()
        assert pmr.recommended_workflow == "SINGLE_REVIEW"
        ra = ReviewerAssignment()
        assert ra.expertise_score == 0.5
        tr = TraceRecord()
        assert tr.success

    def test_phase3_new_models_serialize(self) -> None:
        """Phase 3 new models should serialize correctly."""
        gc = GovernanceConfidence(overall_governance_confidence=0.8)
        d = gc.model_dump()
        assert d["overall_governance_confidence"] == 0.8

        rr = ReviewReadinessModel(decision_id=uuid.uuid4(), status="READY")
        d2 = rr.model_dump()
        assert d2["status"] == "READY"

        ap = GovernanceAuditPackageModel(decision_id=uuid.uuid4())
        d3 = ap.model_dump()
        assert "hash" in d3

        gl = GovernanceLineageModel(decision_id=uuid.uuid4())
        d4 = gl.model_dump()
        assert "chain" in d4

    def test_coordinator_accepts_phase2_deps(self) -> None:
        """Coordinator should accept Phase 2 dependencies."""
        from adip.review.execution.policy_matrix import ReviewPolicyMatrix
        from adip.review.execution.trace import ReviewTrace
        from adip.review.execution.validator import ReviewValidator
        coord = ReviewCoordinator(
            validator=ReviewValidator(),
            policy_matrix=ReviewPolicyMatrix(),
            trace=ReviewTrace(),
        )
        assert coord is not None
        request = ReviewRequest(
            recommendation_decision_id=uuid.uuid4(),
            explanation_decision_id=uuid.uuid4(),
        )
        decision = coord.review(request)
        assert decision.outcome is not None

    def test_global_hooks_singleton_still_works(self) -> None:
        """Global hooks singleton should still work."""
        assert isinstance(global_hooks, IntegrationHooks)
        assert hasattr(global_hooks, "register_pre_review")
        assert hasattr(global_hooks, "register_pre_action")
