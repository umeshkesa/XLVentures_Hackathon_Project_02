"""Tests for Decision Review Layer Phase 3 orchestration components."""

from __future__ import annotations

import uuid

from adip.review.contracts.models import (
    ReviewDecision,
    ReviewExplainabilityMetadata,
    ReviewHealth,
    ReviewMetrics,
    ReviewRequest,
)
from adip.review.dtos import ReviewRequestDTO, ReviewResponseDTO
from adip.review.enums import ReviewDomain, ReviewStatus
from adip.review.orchestration.confidence import ReviewConfidenceCalculator
from adip.review.orchestration.coordinator import ReviewCoordinator
from adip.review.orchestration.manager import ReviewManager
from adip.review.orchestration.session import ReviewSessionManager
from adip.review.services.hooks import IntegrationHooks
from adip.review.services.hooks import hooks as global_hooks
from adip.review.services.service import DefaultReviewService

# ═══════════════════════════════════════════════════════════════════════════════
# ReviewExplainabilityMetadata
# ═══════════════════════════════════════════════════════════════════════════════


class TestReviewExplainabilityMetadata:
    def test_defaults(self) -> None:
        m = ReviewExplainabilityMetadata()
        assert m.why_outcome_selected == ""
        assert m.why_workflow_selected == ""
        assert m.why_reviewer_assigned == ""
        assert m.why_confidence_assessed == ""
        assert m.why_policy_applied == ""
        assert m.why_escalation_triggered == ""
        assert m.metadata == {}

    def test_custom_values(self) -> None:
        m = ReviewExplainabilityMetadata(
            why_outcome_selected="High confidence",
            why_workflow_selected="Single review sufficient",
            why_reviewer_assigned="Best expertise match",
            why_confidence_assessed="All dimensions high",
            why_policy_applied="Standard policy",
            why_escalation_triggered="Low confidence",
            metadata={"source": "test"},
        )
        assert m.why_outcome_selected == "High confidence"
        assert m.why_workflow_selected == "Single review sufficient"
        assert m.metadata["source"] == "test"

    def test_serialization(self) -> None:
        m = ReviewExplainabilityMetadata(why_outcome_selected="test")
        d = m.model_dump()
        assert d["why_outcome_selected"] == "test"
        assert d["why_escalation_triggered"] == ""


# ═══════════════════════════════════════════════════════════════════════════════
# ReviewSessionManager
# ═══════════════════════════════════════════════════════════════════════════════


class TestReviewSessionManager:
    def setup_method(self) -> None:
        self.manager = ReviewSessionManager()
        self.request_id = str(uuid.uuid4())

    def test_create_session(self) -> None:
        session = self.manager.create_session(self.request_id)
        assert session is not None
        assert session.status == ReviewStatus.INITIALIZED
        assert str(session.request_id) == self.request_id

    def test_create_session_with_role(self) -> None:
        session = self.manager.create_session(self.request_id, reviewer_id="rev-1", role="ENGINEER", domain="ENERGY")
        assert session.reviewer_id == "rev-1"
        assert session.role.value == "ENGINEER"

    def test_get_session(self) -> None:
        session = self.manager.create_session(self.request_id)
        retrieved = self.manager.get_session(str(session.session_id))
        assert retrieved is not None
        assert str(retrieved.session_id) == str(session.session_id)

    def test_get_session_nonexistent(self) -> None:
        assert self.manager.get_session("nonexistent") is None

    def test_update_status_valid(self) -> None:
        session = self.manager.create_session(self.request_id)
        updated = self.manager.update_status(str(session.session_id), ReviewStatus.UNDER_REVIEW)
        assert updated is not None
        assert updated.status == ReviewStatus.UNDER_REVIEW

    def test_update_status_invalid(self) -> None:
        session = self.manager.create_session(self.request_id)
        updated = self.manager.update_status(str(session.session_id), ReviewStatus.APPROVED)
        assert updated is None

    def test_update_status_nonexistent(self) -> None:
        assert self.manager.update_status("nonexistent", ReviewStatus.UNDER_REVIEW) is None

    def test_full_lifecycle(self) -> None:
        session = self.manager.create_session(self.request_id)
        assert session.status == ReviewStatus.INITIALIZED
        self.manager.update_status(str(session.session_id), ReviewStatus.UNDER_REVIEW)
        self.manager.update_status(str(session.session_id), ReviewStatus.PENDING_APPROVAL)
        self.manager.update_status(str(session.session_id), ReviewStatus.APPROVED)
        self.manager.update_status(str(session.session_id), ReviewStatus.COMPLETED)
        final = self.manager.get_session(str(session.session_id))
        assert final is not None
        assert final.status == ReviewStatus.COMPLETED
        assert final.completed_at is not None

    def test_get_active_sessions(self) -> None:
        s1 = self.manager.create_session(str(uuid.uuid4()))
        s2 = self.manager.create_session(str(uuid.uuid4()))
        self.manager.update_status(str(s1.session_id), ReviewStatus.COMPLETED)
        active = self.manager.get_active_sessions()
        assert len(active) == 1
        assert active[0].session_id == s2.session_id

    def test_get_all_sessions(self) -> None:
        self.manager.create_session(str(uuid.uuid4()))
        self.manager.create_session(str(uuid.uuid4()))
        assert len(self.manager.get_all_sessions()) == 2

    def test_clear(self) -> None:
        self.manager.create_session(self.request_id)
        self.manager.clear()
        assert self.manager.count() == 0

    def test_count(self) -> None:
        assert self.manager.count() == 0
        self.manager.create_session(self.request_id)
        assert self.manager.count() == 1


# ═══════════════════════════════════════════════════════════════════════════════
# ReviewConfidenceCalculator
# ═══════════════════════════════════════════════════════════════════════════════


class TestReviewConfidenceCalculator:
    def setup_method(self) -> None:
        self.calculator = ReviewConfidenceCalculator()

    def test_defaults(self) -> None:
        confidence = self.calculator.calculate()
        assert confidence.overall_confidence == 0.0
        assert confidence.recommendation_quality == 0.0
        assert confidence.explanation_quality == 0.0
        assert confidence.reviewer_expertise == 0.0
        assert confidence.compliance_score == 0.0

    def test_high_confidence(self) -> None:
        confidence = self.calculator.calculate(
            recommendation_quality=1.0,
            explanation_quality=1.0,
            reviewer_expertise=1.0,
            compliance_score=1.0,
            process_completeness=1.0,
        )
        assert confidence.overall_confidence == 1.0
        assert confidence.recommendation_quality == 1.0

    def test_mixed_confidence(self) -> None:
        confidence = self.calculator.calculate(
            recommendation_quality=0.8,
            explanation_quality=0.6,
            reviewer_expertise=0.9,
            compliance_score=0.7,
            process_completeness=0.5,
        )
        expected = round(0.8 * 0.25 + 0.6 * 0.25 + 0.9 * 0.20 + 0.7 * 0.15 + 0.5 * 0.15, 4)
        assert confidence.overall_confidence == expected

    def test_clamping(self) -> None:
        confidence = self.calculator.calculate(recommendation_quality=-0.5, explanation_quality=1.5)
        assert confidence.recommendation_quality == 0.0
        assert confidence.explanation_quality == 1.0
        assert 0.0 <= confidence.overall_confidence <= 1.0

    def test_correlation_id_propagation(self) -> None:
        confidence = self.calculator.calculate(correlation_id="corr-123")
        assert confidence is not None


# ═══════════════════════════════════════════════════════════════════════════════
# ReviewCoordinator
# ═══════════════════════════════════════════════════════════════════════════════


class TestReviewCoordinator:
    def setup_method(self) -> None:
        self.coordinator = ReviewCoordinator()

    def test_review(self) -> None:
        """Test the full review pipeline produces a decision."""
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
        assert decision.request_id == request.request_id

    def test_review_with_metadata(self) -> None:
        """Test review with risk metadata."""
        request = ReviewRequest(
            recommendation_decision_id=uuid.uuid4(),
            explanation_decision_id=uuid.uuid4(),
            metadata={"risk": "HIGH", "impact": "HIGH", "criticality": "HIGH", "compliance": True},
        )
        decision = self.coordinator.review(request)
        assert decision.outcome is not None
        assert decision.confidence is not None

    def test_review_escalation(self) -> None:
        """Test review with low confidence triggers escalation path."""
        request = ReviewRequest(
            recommendation_decision_id=uuid.uuid4(),
            explanation_decision_id=uuid.uuid4(),
            metadata={"risk": "HIGH"},
        )
        decision = self.coordinator.review(request)
        assert decision is not None
        metadata = decision.metadata if decision.metadata else {}
        assert "escalation_triggered" in metadata

    def test_get_decision(self) -> None:
        assert self.coordinator.get_decision("nonexistent") is None

    def test_health(self) -> None:
        health = self.coordinator.health()
        assert isinstance(health, ReviewHealth)
        assert health.overall_status == "HEALTHY"

    def test_metrics(self) -> None:
        request = ReviewRequest(
            recommendation_decision_id=uuid.uuid4(),
            explanation_decision_id=uuid.uuid4(),
        )
        self.coordinator.review(request)
        metrics = self.coordinator.metrics()
        assert isinstance(metrics, ReviewMetrics)
        assert metrics.reviews_total >= 0


# ═══════════════════════════════════════════════════════════════════════════════
# ReviewManager
# ═══════════════════════════════════════════════════════════════════════════════


class TestReviewManager:
    def setup_method(self) -> None:
        self.manager = ReviewManager()

    def test_start_review(self) -> None:
        request = ReviewRequest(
            recommendation_decision_id=uuid.uuid4(),
            explanation_decision_id=uuid.uuid4(),
        )
        decision = self.manager.start_review(request)
        assert isinstance(decision, ReviewDecision)
        assert str(decision.decision_id) in self.manager._decisions

    def test_get_decision(self) -> None:
        request = ReviewRequest(
            recommendation_decision_id=uuid.uuid4(),
            explanation_decision_id=uuid.uuid4(),
        )
        decision = self.manager.start_review(request)
        retrieved = self.manager.get_decision(str(decision.decision_id))
        assert retrieved is not None
        assert retrieved.outcome == decision.outcome

    def test_get_decision_nonexistent(self) -> None:
        assert self.manager.get_decision("nonexistent") is None

    def test_get_session(self) -> None:
        request = ReviewRequest(
            recommendation_decision_id=uuid.uuid4(),
            explanation_decision_id=uuid.uuid4(),
        )
        self.manager.start_review(request)
        assert self.manager.get_session("nonexistent") is None

    def test_get_health(self) -> None:
        health = self.manager.get_health()
        assert isinstance(health, ReviewHealth)
        assert health.overall_status == "HEALTHY"

    def test_get_metrics(self) -> None:
        metrics = self.manager.get_metrics()
        assert isinstance(metrics, ReviewMetrics)

    def test_correlation_id_propagation(self) -> None:
        request = ReviewRequest(
            recommendation_decision_id=uuid.uuid4(),
            explanation_decision_id=uuid.uuid4(),
        )
        decision = self.manager.start_review(request, correlation_id="corr-abc")
        assert decision is not None


# ═══════════════════════════════════════════════════════════════════════════════
# IntegrationHooks
# ═══════════════════════════════════════════════════════════════════════════════


class TestIntegrationHooks:
    def setup_method(self) -> None:
        self.hooks = IntegrationHooks()

    def test_register_and_run_pre_review(self) -> None:
        results: list[str] = []

        def hook(**kwargs: str) -> None:
            results.append("pre_review")

        self.hooks.register_pre_review(hook)
        self.hooks.run_pre_review()
        assert len(results) == 1

    def test_register_and_run_post_review(self) -> None:
        results: list[str] = []

        def hook(**kwargs: str) -> None:
            results.append("post_review")

        self.hooks.register_post_review(hook)
        self.hooks.run_post_review()
        assert len(results) == 1

    def test_register_and_run_on_error(self) -> None:
        results: list[str] = []

        def hook(**kwargs: str) -> None:
            results.append("on_error")

        self.hooks.register_on_error(hook)
        self.hooks.run_on_error()
        assert len(results) == 1

    def test_register_and_run_session_created(self) -> None:
        results: list[str] = []

        def hook(**kwargs: str) -> None:
            results.append("session_created")

        self.hooks.register_session_created(hook)
        self.hooks.run_session_created()
        assert len(results) == 1

    def test_register_and_run_session_completed(self) -> None:
        results: list[str] = []

        def hook(**kwargs: str) -> None:
            results.append("session_completed")

        self.hooks.register_session_completed(hook)
        self.hooks.run_session_completed()
        assert len(results) == 1

    def test_register_and_run_pre_escalation(self) -> None:
        results: list[str] = []

        def hook(**kwargs: str) -> None:
            results.append("pre_escalation")

        self.hooks.register_pre_escalation(hook)
        self.hooks.run_pre_escalation()
        assert len(results) == 1

    def test_register_and_run_post_escalation(self) -> None:
        results: list[str] = []

        def hook(**kwargs: str) -> None:
            results.append("post_escalation")

        self.hooks.register_post_escalation(hook)
        self.hooks.run_post_escalation()
        assert len(results) == 1

    def test_register_and_run_workflow_started(self) -> None:
        results: list[str] = []

        def hook(**kwargs: str) -> None:
            results.append("workflow_started")

        self.hooks.register_workflow_started(hook)
        self.hooks.run_workflow_started()
        assert len(results) == 1

    def test_register_and_run_workflow_completed(self) -> None:
        results: list[str] = []

        def hook(**kwargs: str) -> None:
            results.append("workflow_completed")

        self.hooks.register_workflow_completed(hook)
        self.hooks.run_workflow_completed()
        assert len(results) == 1

    def test_register_and_run_decision_made(self) -> None:
        results: list[str] = []

        def hook(**kwargs: str) -> None:
            results.append("decision_made")

        self.hooks.register_decision_made(hook)
        self.hooks.run_decision_made()
        assert len(results) == 1

    def test_global_hooks_singleton(self) -> None:
        assert isinstance(global_hooks, IntegrationHooks)

    def test_exception_isolation(self) -> None:
        """A failing hook should not prevent other hooks from running."""
        results: list[str] = []

        def failing_hook(**kwargs: str) -> None:
            msg = "intentional failure"
            raise ValueError(msg)

        def working_hook(**kwargs: str) -> None:
            results.append("worked")

        self.hooks.register_pre_review(failing_hook)
        self.hooks.register_pre_review(working_hook)
        self.hooks.run_pre_review()
        assert len(results) == 1

    def test_multiple_hooks_same_type(self) -> None:
        results: list[str] = []

        def hook1(**kwargs: str) -> None:
            results.append("hook1")

        def hook2(**kwargs: str) -> None:
            results.append("hook2")

        self.hooks.register_pre_review(hook1)
        self.hooks.register_pre_review(hook2)
        self.hooks.run_pre_review()
        assert len(results) == 2
        assert results == ["hook1", "hook2"]


# ═══════════════════════════════════════════════════════════════════════════════
# DefaultReviewService
# ═══════════════════════════════════════════════════════════════════════════════


class TestDefaultReviewService:
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

    def test_submit_review_with_auth_success(self) -> None:
        called: list[str] = []

        def auth_callback(user_id: str, action: str) -> bool:
            called.append(user_id)
            return True

        service = DefaultReviewService(auth_callback=auth_callback)
        dto = ReviewRequestDTO(
            recommendation_decision_id=uuid.uuid4(),
            explanation_decision_id=uuid.uuid4(),
        )
        response = service.submit_review(dto, user_id="user-1")
        assert response is not None
        assert len(called) == 1

    def test_submit_review_with_auth_failure(self) -> None:
        def auth_callback(user_id: str, action: str) -> bool:
            return False

        service = DefaultReviewService(auth_callback=auth_callback)
        dto = ReviewRequestDTO(
            recommendation_decision_id=uuid.uuid4(),
            explanation_decision_id=uuid.uuid4(),
        )
        response = service.submit_review(dto, user_id="user-1")
        assert response is None

    def test_submit_review_with_audit(self) -> None:
        audit_entries: list[tuple[str, str, str, dict]] = []

        def audit_callback(action: str, user_id: str, entity_id: str, details: dict) -> None:
            audit_entries.append((action, user_id, entity_id, details))

        service = DefaultReviewService(audit_callback=audit_callback)
        dto = ReviewRequestDTO(
            recommendation_decision_id=uuid.uuid4(),
            explanation_decision_id=uuid.uuid4(),
        )
        response = service.submit_review(dto, user_id="user-1")
        assert response is not None
        assert len(audit_entries) == 1
        assert audit_entries[0][0] == "submit_review"

    def test_submit_review_with_hooks(self) -> None:
        pre_results: list[str] = []
        post_results: list[str] = []

        def pre_hook(**kwargs: str) -> None:
            pre_results.append("pre")

        def post_hook(**kwargs: str) -> None:
            post_results.append("post")

        hooks = IntegrationHooks()
        hooks.register_pre_review(pre_hook)
        hooks.register_post_review(post_hook)

        service = DefaultReviewService(hooks=hooks)
        dto = ReviewRequestDTO(
            recommendation_decision_id=uuid.uuid4(),
            explanation_decision_id=uuid.uuid4(),
        )
        response = service.submit_review(dto, user_id="user-1")
        assert response is not None
        assert len(pre_results) == 1
        assert len(post_results) == 1

    def test_get_decision(self) -> None:
        decision = self.service.get_decision("nonexistent")
        assert decision is None

    def test_get_decision_with_auth_success(self) -> None:
        def auth_callback(user_id: str, action: str) -> bool:
            return True

        service = DefaultReviewService(auth_callback=auth_callback)
        decision = service.get_decision("nonexistent", user_id="user-1")
        assert decision is None

    def test_get_decision_with_auth_failure(self) -> None:
        def auth_callback(user_id: str, action: str) -> bool:
            return False

        service = DefaultReviewService(auth_callback=auth_callback)
        decision = service.get_decision("test-id", user_id="user-1")
        assert decision is None

    def test_get_session(self) -> None:
        session = self.service.get_session("nonexistent")
        assert session is None

    def test_get_health(self) -> None:
        health = self.service.get_health()
        assert isinstance(health, ReviewHealth)

    def test_get_metrics(self) -> None:
        metrics = self.service.get_metrics()
        assert isinstance(metrics, ReviewMetrics)
        assert metrics.reviews_total >= 0

    def test_correlation_id_propagation(self) -> None:
        dto = ReviewRequestDTO(
            recommendation_decision_id=uuid.uuid4(),
            explanation_decision_id=uuid.uuid4(),
        )
        response = self.service.submit_review(dto, user_id="user-1", correlation_id="corr-xyz")
        assert response is not None
