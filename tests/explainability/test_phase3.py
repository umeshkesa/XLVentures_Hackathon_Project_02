"""Comprehensive tests for the Explainability Engine Phase 3 (Enterprise Orchestration).

Tests all Phase 3 orchestration components:
  1. ExplanationSessionManager
  2. ExplanationConfidenceCalculator
  3. ExplainabilityCoordinatorImpl
  4. ExplainabilityManagerImpl
  5. IntegrationHooks
  6. DefaultExplainabilityService
  7. Enhanced Contract Models
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from unittest.mock import MagicMock

from adip.explainability.contracts.models import (
    ExplanationCitation,
    ExplanationConfidence,
    ExplanationContext,
    ExplanationDecision,
    ExplanationHealth,
    ExplanationMetrics,
    ExplanationPackage,
    ExplanationRequest,
    ExplanationResult,
    ExplanationSession,
)
from adip.explainability.dtos import (
    ExplanationRequestDTO,
)
from adip.explainability.enums import (
    CitationType,
    ExplanationDomain,
    ExplanationLayer,
    ExplanationStatus,
)
from adip.explainability.execution.models import QualityScore
from adip.explainability.orchestration.confidence import ExplanationConfidenceCalculator
from adip.explainability.orchestration.coordinator import (
    ExplainabilityCoordinatorImpl,
)
from adip.explainability.orchestration.manager import ExplainabilityManagerImpl
from adip.explainability.orchestration.session import ExplanationSessionManager
from adip.explainability.services.hooks import IntegrationHooks
from adip.explainability.services.hooks import hooks as global_hooks
from adip.explainability.services.service import DefaultExplainabilityService

# =============================================================================
# 1. ExplanationSessionManager
# =============================================================================


class TestExplanationSessionManager:
    def test_create_session(self) -> None:
        sm = ExplanationSessionManager()
        context = ExplanationContext()
        session = sm.create_session(context, correlation_id="test-cid")
        assert isinstance(session, ExplanationSession)
        assert session.status == ExplanationStatus.INITIALIZED
        assert session.metadata.get("correlation_id") == "test-cid"
        assert session.metadata.get("context_id") == str(context.context_id)

    def test_create_session_sets_context_id(self) -> None:
        sm = ExplanationSessionManager()
        context = ExplanationContext()
        session = sm.create_session(context)
        assert session.request_id == context.context_id

    def test_get_session(self) -> None:
        sm = ExplanationSessionManager()
        context = ExplanationContext()
        session = sm.create_session(context)
        retrieved = sm.get_session(str(session.session_id))
        assert retrieved is session

    def test_get_session_not_found(self) -> None:
        sm = ExplanationSessionManager()
        assert sm.get_session("nonexistent") is None

    def test_update_status_initialized_to_collecting(self) -> None:
        sm = ExplanationSessionManager()
        context = ExplanationContext()
        session = sm.create_session(context)
        updated = sm.update_status(str(session.session_id), ExplanationStatus.COLLECTING)
        assert updated is not None
        assert updated.status == ExplanationStatus.COLLECTING

    def test_update_status_collecting_to_building(self) -> None:
        sm = ExplanationSessionManager()
        context = ExplanationContext()
        session = sm.create_session(context)
        sm.update_status(str(session.session_id), ExplanationStatus.COLLECTING)
        updated = sm.update_status(str(session.session_id), ExplanationStatus.BUILDING)
        assert updated is not None
        assert updated.status == ExplanationStatus.BUILDING

    def test_update_status_building_to_validated(self) -> None:
        sm = ExplanationSessionManager()
        context = ExplanationContext()
        session = sm.create_session(context)
        sm.update_status(str(session.session_id), ExplanationStatus.COLLECTING)
        sm.update_status(str(session.session_id), ExplanationStatus.BUILDING)
        updated = sm.update_status(str(session.session_id), ExplanationStatus.VALIDATED)
        assert updated is not None
        assert updated.status == ExplanationStatus.VALIDATED

    def test_update_status_validated_to_completed(self) -> None:
        sm = ExplanationSessionManager()
        context = ExplanationContext()
        session = sm.create_session(context)
        sm.update_status(str(session.session_id), ExplanationStatus.COLLECTING)
        sm.update_status(str(session.session_id), ExplanationStatus.BUILDING)
        sm.update_status(str(session.session_id), ExplanationStatus.VALIDATED)
        updated = sm.update_status(str(session.session_id), ExplanationStatus.COMPLETED)
        assert updated is not None
        assert updated.status == ExplanationStatus.COMPLETED

    def test_update_status_rejects_invalid_transition(self) -> None:
        sm = ExplanationSessionManager()
        context = ExplanationContext()
        session = sm.create_session(context)
        # INITIALIZED -> COMPLETED directly is invalid
        updated = sm.update_status(str(session.session_id), ExplanationStatus.COMPLETED)
        assert updated is None

    def test_update_status_allows_failed_from_any_state(self) -> None:
        sm = ExplanationSessionManager()
        context = ExplanationContext()
        session = sm.create_session(context)
        updated = sm.update_status(str(session.session_id), ExplanationStatus.FAILED)
        assert updated is not None
        assert updated.status == ExplanationStatus.FAILED

    def test_update_status_not_found(self) -> None:
        sm = ExplanationSessionManager()
        assert sm.update_status("nonexistent", ExplanationStatus.COMPLETED) is None

    def test_update_status_sets_completed_at_on_completed(self) -> None:
        sm = ExplanationSessionManager()
        context = ExplanationContext()
        session = sm.create_session(context)
        sm.update_status(str(session.session_id), ExplanationStatus.COLLECTING)
        sm.update_status(str(session.session_id), ExplanationStatus.BUILDING)
        sm.update_status(str(session.session_id), ExplanationStatus.VALIDATED)
        updated = sm.update_status(str(session.session_id), ExplanationStatus.COMPLETED)
        assert updated is not None
        assert updated.completed_at is not None

    def test_update_status_sets_completed_at_on_failed(self) -> None:
        sm = ExplanationSessionManager()
        context = ExplanationContext()
        session = sm.create_session(context)
        updated = sm.update_status(str(session.session_id), ExplanationStatus.FAILED)
        assert updated is not None
        assert updated.completed_at is not None

    def test_add_narrative(self) -> None:
        sm = ExplanationSessionManager()
        context = ExplanationContext()
        session = sm.create_session(context)
        narrative_id = str(uuid.uuid4())
        updated = sm.add_narrative(str(session.session_id), narrative_id)
        assert updated is not None
        assert updated.statistics.get("narrative_count") == 1

    def test_add_narrative_not_found(self) -> None:
        sm = ExplanationSessionManager()
        assert sm.add_narrative("nonexistent", str(uuid.uuid4())) is None

    def test_add_citation(self) -> None:
        sm = ExplanationSessionManager()
        context = ExplanationContext()
        session = sm.create_session(context)
        citation_id = str(uuid.uuid4())
        updated = sm.add_citation(str(session.session_id), citation_id)
        assert updated is not None
        assert updated.statistics.get("citation_count") == 1

    def test_add_citation_not_found(self) -> None:
        sm = ExplanationSessionManager()
        assert sm.add_citation("nonexistent", str(uuid.uuid4())) is None

    def test_add_multiple_narratives_and_citations(self) -> None:
        sm = ExplanationSessionManager()
        context = ExplanationContext()
        session = sm.create_session(context)
        for i in range(3):
            sm.add_narrative(str(session.session_id), str(uuid.uuid4()))
        for i in range(2):
            sm.add_citation(str(session.session_id), str(uuid.uuid4()))
        retrieved = sm.get_session(str(session.session_id))
        assert retrieved is not None
        assert retrieved.statistics.get("narrative_count") == 3
        assert retrieved.statistics.get("citation_count") == 2

    def test_get_active_sessions(self) -> None:
        sm = ExplanationSessionManager()
        context = ExplanationContext()
        s1 = sm.create_session(context)
        sm.create_session(ExplanationContext())
        # Complete one session
        sm.update_status(str(s1.session_id), ExplanationStatus.COLLECTING)
        sm.update_status(str(s1.session_id), ExplanationStatus.BUILDING)
        sm.update_status(str(s1.session_id), ExplanationStatus.VALIDATED)
        sm.update_status(str(s1.session_id), ExplanationStatus.COMPLETED)
        active = sm.get_active_sessions()
        assert len(active) == 1
        assert active[0].status == ExplanationStatus.INITIALIZED

    def test_get_active_sessions_excludes_failed(self) -> None:
        sm = ExplanationSessionManager()
        context = ExplanationContext()
        s1 = sm.create_session(context)
        sm.update_status(str(s1.session_id), ExplanationStatus.FAILED)
        s2 = sm.create_session(ExplanationContext())
        active = sm.get_active_sessions()
        assert len(active) == 1
        assert active[0].session_id == s2.session_id

    def test_get_all_sessions(self) -> None:
        sm = ExplanationSessionManager()
        assert len(sm.get_all_sessions()) == 0
        sm.create_session(ExplanationContext())
        sm.create_session(ExplanationContext())
        assert len(sm.get_all_sessions()) == 2

    def test_clear(self) -> None:
        sm = ExplanationSessionManager()
        sm.create_session(ExplanationContext())
        sm.clear()
        assert sm.count() == 0

    def test_count(self) -> None:
        sm = ExplanationSessionManager()
        assert sm.count() == 0
        sm.create_session(ExplanationContext())
        assert sm.count() == 1
        sm.create_session(ExplanationContext())
        assert sm.count() == 2


# =============================================================================
# 2. ExplanationConfidenceCalculator
# =============================================================================


class TestExplanationConfidenceCalculator:
    def _make_package(self, citation_count: int = 0) -> ExplanationPackage:
        rid = uuid.uuid4()
        package = ExplanationPackage(result_id=rid)
        for i in range(citation_count):
            package.evidence_citations.append(
                ExplanationCitation(
                    narrative_id=uuid.uuid4(),
                    citation_type=CitationType.EVIDENCE,
                )
            )
        return package

    def test_calculate_returns_confidence(self) -> None:
        cc = ExplanationConfidenceCalculator()
        package = self._make_package()
        quality = QualityScore()
        c = cc.calculate(package, quality)
        assert isinstance(c, ExplanationConfidence)

    def test_calculate_default_values(self) -> None:
        cc = ExplanationConfidenceCalculator()
        package = self._make_package(citation_count=0)
        quality = QualityScore(
            completeness=0.0,
            citation_coverage=0.0,
        )
        c = cc.calculate(package, quality)
        # citation_coverage = quality.citation_coverage = 0.0
        # trace_completeness = quality.trace_coverage = 0.0
        # narrative_completeness = quality.completeness = 0.0
        # evidence_coverage = quality.completeness * 0.9 = 0.0
        # consistency = quality.consistency = 0.0
        # overall = 0.0*0.20 + 0.0*0.20 + 0.0*0.20 + 0.0*0.20 + 0.0*0.20 = 0.0
        assert c.overall_confidence == 0.0
        assert c.narrative_quality == 0.0
        assert c.citation_accuracy == 0.0
        assert c.completeness == 0.0
        assert c.audience_coverage == 0.0

    def test_calculate_full_coverage(self) -> None:
        cc = ExplanationConfidenceCalculator()
        package = self._make_package(citation_count=5)
        quality = QualityScore(
            completeness=1.0,
            citation_coverage=1.0,
        )
        c = cc.calculate(package, quality)
        # citation_coverage = 1.0
        # trace_completeness = 0.0 (default)
        # narrative_completeness = 1.0
        # evidence_coverage = 1.0 * 0.9 = 0.9
        # consistency = 0.0 (default)
        # overall = 1.0*0.20 + 0.0*0.20 + 1.0*0.20 + 0.9*0.20 + 0.0*0.20 = 0.20+0.0+0.20+0.18+0.0 = 0.58
        assert c.overall_confidence == 0.58
        assert c.narrative_quality == 1.0
        assert c.citation_accuracy == 1.0
        assert c.completeness == 0.0

    def test_calculate_many_citations(self) -> None:
        cc = ExplanationConfidenceCalculator()
        package = self._make_package(citation_count=10)
        quality = QualityScore(
            completeness=0.5,
            citation_coverage=0.5,
        )
        c = cc.calculate(package, quality)
        # citation_coverage = 0.5
        # trace_completeness = 0.0 (default)
        # narrative_completeness = 0.5
        # evidence_coverage = 0.5 * 0.9 = 0.45
        # consistency = 0.0 (default)
        # overall = 0.5*0.20 + 0.0*0.20 + 0.5*0.20 + 0.45*0.20 + 0.0*0.20 = 0.10+0.0+0.10+0.09+0.0 = 0.29
        assert c.overall_confidence == 0.29

    def test_calculate_clamps_values(self) -> None:
        cc = ExplanationConfidenceCalculator()
        package = self._make_package(citation_count=10)
        quality = QualityScore(
            completeness=1.0,
            citation_coverage=0.0,
        )
        c = cc.calculate(package, quality)
        # citation_coverage = 0.0
        # trace_completeness = 0.0 (default)
        # narrative_completeness = 1.0
        # evidence_coverage = 1.0 * 0.9 = 0.9
        # consistency = 0.0 (default)
        # overall = 0.0*0.20 + 0.0*0.20 + 1.0*0.20 + 0.9*0.20 + 0.0*0.20 = 0.0+0.0+0.20+0.18+0.0 = 0.38
        assert c.overall_confidence == 0.38

    def test_calculate_with_correlation_id(self) -> None:
        cc = ExplanationConfidenceCalculator()
        package = self._make_package(citation_count=3)
        quality = QualityScore(completeness=0.6, citation_coverage=0.4)
        c = cc.calculate(package, quality, correlation_id="my-cid")
        assert isinstance(c, ExplanationConfidence)
        # citation_coverage=0.4, trace_completeness=0.0, narrative_completeness=0.6, evidence_coverage=0.54, consistency=0.0
        expected = round(0.4*0.20 + 0.0*0.20 + 0.6*0.20 + 0.54*0.20 + 0.0*0.20, 4)
        assert c.overall_confidence == expected

    def test_calculate_zero_citations(self) -> None:
        cc = ExplanationConfidenceCalculator()
        package = self._make_package(citation_count=0)
        quality = QualityScore(completeness=0.8, citation_coverage=0.8)
        c = cc.calculate(package, quality)
        # citation_accuracy = quality.citation_coverage = 0.8 (no longer citation-count based)
        # citation_coverage=0.8, trace_completeness=0.0, narrative_completeness=0.8, evidence_coverage=0.72, consistency=0.0
        # overall = 0.8*0.20 + 0.0*0.20 + 0.8*0.20 + 0.72*0.20 + 0.0*0.20 = 0.16+0.0+0.16+0.144+0.0 = 0.464
        assert c.citation_accuracy == 0.8
        assert c.overall_confidence == 0.464

    def test_calculate_mixed_values(self) -> None:
        cc = ExplanationConfidenceCalculator()
        package = self._make_package(citation_count=2)
        quality = QualityScore(completeness=0.7, citation_coverage=0.6)
        c = cc.calculate(package, quality)
        # citation_coverage=0.6, trace_completeness=0.0, narrative_completeness=0.7, evidence_coverage=0.63, consistency=0.0
        # overall = 0.6*0.20 + 0.0*0.20 + 0.7*0.20 + 0.63*0.20 + 0.0*0.20 = 0.12+0.0+0.14+0.126+0.0 = 0.386
        assert c.overall_confidence == 0.386


# =============================================================================
# 3. ExplainabilityCoordinatorImpl
# =============================================================================


class TestExplainabilityCoordinatorImpl:
    def test_explain_returns_result(self) -> None:
        coord = ExplainabilityCoordinatorImpl()
        request = ExplanationRequest()
        result = coord.explain(request)
        assert isinstance(result, ExplanationResult)

    def test_explain_creates_session(self) -> None:
        coord = ExplainabilityCoordinatorImpl()
        request = ExplanationRequest()
        result = coord.explain(request)
        assert result.request_id == request.request_id
        assert result.status in (ExplanationStatus.COMPLETED, ExplanationStatus.FAILED)

    def test_explain_includes_narratives(self) -> None:
        coord = ExplainabilityCoordinatorImpl()
        request = ExplanationRequest(target_audiences=[ExplanationLayer.ENGINEER, ExplanationLayer.EXECUTIVE])
        result = coord.explain(request)
        assert len(result.narratives) == 2
        assert result.narratives[0].audience in (ExplanationLayer.ENGINEER, ExplanationLayer.EXECUTIVE)
        assert result.narratives[1].audience in (ExplanationLayer.ENGINEER, ExplanationLayer.EXECUTIVE)

    def test_explain_includes_citations(self) -> None:
        coord = ExplainabilityCoordinatorImpl()
        request = ExplanationRequest(
            target_audiences=[ExplanationLayer.ENGINEER],
        )
        result = coord.explain(request)
        assert len(result.citations) > 0
        assert result.citations[0].citation_type in (
            CitationType.EVIDENCE,
            CitationType.REASONING,
            CitationType.RECOMMENDATION,
        )

    def test_explain_includes_package(self) -> None:
        coord = ExplainabilityCoordinatorImpl()
        request = ExplanationRequest()
        result = coord.explain(request)
        assert result.package is not None
        assert isinstance(result.package, ExplanationPackage)

    def test_explain_includes_confidence(self) -> None:
        coord = ExplainabilityCoordinatorImpl()
        request = ExplanationRequest()
        result = coord.explain(request)
        assert result.confidence is not None
        assert isinstance(result.confidence, ExplanationConfidence)

    def test_explain_includes_decision(self) -> None:
        coord = ExplainabilityCoordinatorImpl()
        request = ExplanationRequest()
        result = coord.explain(request)
        assert len(result.decisions) == 1
        assert isinstance(result.decisions[0], ExplanationDecision)

    def test_explain_with_correlation_id(self) -> None:
        coord = ExplainabilityCoordinatorImpl()
        request = ExplanationRequest()
        result = coord.explain(request, correlation_id="my-cid")
        assert isinstance(result, ExplanationResult)

    def test_explain_with_single_audience(self) -> None:
        coord = ExplainabilityCoordinatorImpl()
        request = ExplanationRequest(target_audiences=[ExplanationLayer.EXECUTIVE])
        result = coord.explain(request)
        assert len(result.narratives) == 1

    def test_explain_with_multiple_audiences(self) -> None:
        coord = ExplainabilityCoordinatorImpl()
        audiences = [
            ExplanationLayer.EXECUTIVE,
            ExplanationLayer.MANAGER,
            ExplanationLayer.ENGINEER,
            ExplanationLayer.OPERATOR,
        ]
        request = ExplanationRequest(target_audiences=audiences)
        result = coord.explain(request)
        assert len(result.narratives) == 4

    def test_get_result_returns_none(self) -> None:
        coord = ExplainabilityCoordinatorImpl()
        assert coord.get_result("nonexistent") is None

    def test_get_result_after_explain(self) -> None:
        coord = ExplainabilityCoordinatorImpl()
        request = ExplanationRequest()
        result = coord.explain(request)
        # Coordinator's get_result always returns None
        assert coord.get_result(str(result.result_id)) is None

    def test_health(self) -> None:
        coord = ExplainabilityCoordinatorImpl()
        health = coord.health()
        assert isinstance(health, ExplanationHealth)
        assert health.overall_status == "HEALTHY"
        assert health.coordinator_status == "HEALTHY"
        assert health.narrative_builder_status == "HEALTHY"
        assert health.citation_builder_status == "HEALTHY"
        assert health.audience_formatter_status == "HEALTHY"
        assert health.validator_status == "HEALTHY"

    def test_metrics(self) -> None:
        coord = ExplainabilityCoordinatorImpl()
        metrics = coord.metrics()
        assert isinstance(metrics, ExplanationMetrics)
        assert metrics.explanations_total >= 0

    def test_metrics_after_explain(self) -> None:
        coord = ExplainabilityCoordinatorImpl()
        request = ExplanationRequest()
        coord.explain(request)
        metrics = coord.metrics()
        assert metrics.explanations_total >= 1
        assert metrics.narratives_total >= 1
        assert metrics.citations_total >= 1

    def test_explain_uses_injected_components(self) -> None:
        from adip.explainability.execution.citation_manager import CitationManager
        from adip.explainability.execution.narrative_builder import NarrativeBuilder

        nb = NarrativeBuilder()
        cm = CitationManager()
        coord = ExplainabilityCoordinatorImpl(
            narrative_builder=nb,
            citation_manager=cm,
        )
        request = ExplanationRequest()
        result = coord.explain(request)
        assert isinstance(result, ExplanationResult)

    def test_explain_completes_with_default_audience(self) -> None:
        coord = ExplainabilityCoordinatorImpl()
        request = ExplanationRequest()  # no target_audiences specified
        result = coord.explain(request)
        assert result.status == ExplanationStatus.COMPLETED
        assert len(result.narratives) == 1

    def test_explain_with_metadata_policy_type(self) -> None:
        coord = ExplainabilityCoordinatorImpl()
        request = ExplanationRequest(
            target_audiences=[ExplanationLayer.EXECUTIVE],
            metadata={"policy_type": "SUMMARY"},
        )
        result = coord.explain(request)
        assert result.status == ExplanationStatus.COMPLETED


# =============================================================================
# 4. ExplainabilityManagerImpl
# =============================================================================


class TestExplainabilityManagerImpl:
    def test_execute_explanation_returns_result(self) -> None:
        mgr = ExplainabilityManagerImpl()
        request = ExplanationRequest()
        result = mgr.execute_explanation(request)
        assert isinstance(result, ExplanationResult)
        assert result.status != ExplanationStatus.INITIALIZED

    def test_get_result(self) -> None:
        mgr = ExplainabilityManagerImpl()
        request = ExplanationRequest()
        result = mgr.execute_explanation(request)
        retrieved = mgr.get_result(str(result.result_id))
        assert retrieved is not None
        assert str(retrieved.result_id) == str(result.result_id)

    def test_get_result_not_found(self) -> None:
        mgr = ExplainabilityManagerImpl()
        assert mgr.get_result("nonexistent") is None

    def test_get_health(self) -> None:
        mgr = ExplainabilityManagerImpl()
        health = mgr.get_health()
        assert isinstance(health, ExplanationHealth)
        assert health.overall_status == "HEALTHY"

    def test_get_metrics(self) -> None:
        mgr = ExplainabilityManagerImpl()
        metrics = mgr.get_metrics()
        assert isinstance(metrics, ExplanationMetrics)

    def test_get_metrics_after_execution(self) -> None:
        mgr = ExplainabilityManagerImpl()
        mgr.execute_explanation(ExplanationRequest())
        metrics = mgr.get_metrics()
        assert metrics.explanations_total >= 1

    def test_multiple_executions(self) -> None:
        mgr = ExplainabilityManagerImpl()
        r1 = mgr.execute_explanation(ExplanationRequest())
        r2 = mgr.execute_explanation(ExplanationRequest())
        assert str(r1.result_id) != str(r2.result_id)
        assert mgr.get_result(str(r1.result_id)) is not None
        assert mgr.get_result(str(r2.result_id)) is not None

    def test_execute_with_correlation_id(self) -> None:
        mgr = ExplainabilityManagerImpl()
        result = mgr.execute_explanation(ExplanationRequest(), correlation_id="my-cid")
        assert isinstance(result, ExplanationResult)

    def test_default_coordinator_created(self) -> None:
        mgr = ExplainabilityManagerImpl()
        assert mgr._coordinator is not None

    def test_injected_coordinator(self) -> None:
        from adip.explainability.orchestration.coordinator import ExplainabilityCoordinatorImpl
        coord = ExplainabilityCoordinatorImpl()
        mgr = ExplainabilityManagerImpl(coordinator=coord)
        assert mgr._coordinator is coord


# =============================================================================
# 5. IntegrationHooks
# =============================================================================


class TestIntegrationHooks:
    def test_register_and_run_pre_explain(self) -> None:
        h = IntegrationHooks()
        calls: list[str] = []

        def hook(**kwargs: object) -> None:
            calls.append("hook1")

        h.register_pre_explain(hook)
        h.run_pre_explain()
        assert calls == ["hook1"]

    def test_register_and_run_post_explain(self) -> None:
        h = IntegrationHooks()
        calls: list[str] = []

        def hook(**kwargs: object) -> None:
            calls.append("hook1")

        h.register_post_explain(hook)
        h.run_post_explain()
        assert calls == ["hook1"]

    def test_register_and_run_on_error(self) -> None:
        h = IntegrationHooks()
        calls: list[str] = []

        def hook(**kwargs: object) -> None:
            calls.append("on_error")

        h.register_on_error(hook)
        h.run_on_error()
        assert calls == ["on_error"]

    def test_register_and_run_session_created(self) -> None:
        h = IntegrationHooks()
        calls: list[str] = []

        def hook(**kwargs: object) -> None:
            calls.append("session_created")

        h.register_session_created(hook)
        h.run_session_created()
        assert calls == ["session_created"]

    def test_register_and_run_session_completed(self) -> None:
        h = IntegrationHooks()
        calls: list[str] = []

        def hook(**kwargs: object) -> None:
            calls.append("session_completed")

        h.register_session_completed(hook)
        h.run_session_completed()
        assert calls == ["session_completed"]

    def test_exception_isolation_pre_explain(self) -> None:
        h = IntegrationHooks()
        calls: list[str] = []

        def failing_hook(**kwargs: object) -> None:
            raise ValueError("Hook failed")

        def working_hook(**kwargs: object) -> None:
            calls.append("working")

        h.register_pre_explain(failing_hook)
        h.register_pre_explain(working_hook)
        h.run_pre_explain()
        assert calls == ["working"]

    def test_exception_isolation_on_error(self) -> None:
        h = IntegrationHooks()
        calls: list[str] = []

        def failing_hook(**kwargs: object) -> None:
            raise RuntimeError("fail")

        def working_hook(**kwargs: object) -> None:
            calls.append("working")

        h.register_on_error(failing_hook)
        h.register_on_error(working_hook)
        h.run_on_error()
        assert calls == ["working"]

    def test_exception_isolation_session_created(self) -> None:
        h = IntegrationHooks()
        calls: list[str] = []

        def fail(**kwargs: object) -> None:
            raise ValueError("fail")

        def ok(**kwargs: object) -> None:
            calls.append("ok")

        h.register_session_created(fail)
        h.register_session_created(ok)
        h.run_session_created()
        assert calls == ["ok"]

    def test_exception_isolation_session_completed(self) -> None:
        h = IntegrationHooks()
        calls: list[str] = []

        def fail(**kwargs: object) -> None:
            raise ValueError("fail")

        def ok(**kwargs: object) -> None:
            calls.append("ok")

        h.register_session_completed(fail)
        h.register_session_completed(ok)
        h.run_session_completed()
        assert calls == ["ok"]

    def test_multiple_hooks_all_run(self) -> None:
        h = IntegrationHooks()
        calls: list[int] = []

        def h1(**kwargs: object) -> None:
            calls.append(1)

        def h2(**kwargs: object) -> None:
            calls.append(2)

        def h3(**kwargs: object) -> None:
            calls.append(3)

        h.register_pre_explain(h1)
        h.register_pre_explain(h2)
        h.register_pre_explain(h3)
        h.run_pre_explain()
        assert calls == [1, 2, 3]

    def test_hooks_pass_kwargs(self) -> None:
        h = IntegrationHooks()
        received: dict[str, object] = {}

        def hook(**kwargs: object) -> None:
            received.update(kwargs)

        h.register_pre_explain(hook)
        h.run_pre_explain(request_id="req-1", user_id="user-1")
        assert received.get("request_id") == "req-1"
        assert received.get("user_id") == "user-1"

    def test_on_error_hooks_pass_kwargs(self) -> None:
        h = IntegrationHooks()
        received: dict[str, object] = {}

        def hook(**kwargs: object) -> None:
            received.update(kwargs)

        h.register_on_error(hook)
        h.run_on_error(error="test error", user_id="user-1")
        assert received.get("error") == "test error"
        assert received.get("user_id") == "user-1"

    def test_global_hooks_singleton(self) -> None:
        assert isinstance(global_hooks, IntegrationHooks)

    def test_all_exceptions_isolated(self) -> None:
        h = IntegrationHooks()
        calls: list[int] = []

        def fail1(**kwargs: object) -> None:
            raise RuntimeError("fail1")

        def ok1(**kwargs: object) -> None:
            calls.append(1)

        def fail2(**kwargs: object) -> None:
            raise ValueError("fail2")

        def ok2(**kwargs: object) -> None:
            calls.append(2)

        h.register_pre_explain(fail1)
        h.register_pre_explain(ok1)
        h.register_pre_explain(fail2)
        h.register_pre_explain(ok2)
        h.run_pre_explain()
        assert calls == [1, 2]


# =============================================================================
# 6. DefaultExplainabilityService
# =============================================================================


class TestDefaultExplainabilityService:
    def test_explain_returns_response(self) -> None:
        svc = DefaultExplainabilityService()
        dto = ExplanationRequestDTO(reasoning_result_id=str(uuid.uuid4()))
        response = svc.explain(dto)
        assert response is not None
        assert response.status is not None
        assert response.status != ""

    def test_explain_with_auth_fail(self) -> None:
        def auth_fail(user_id: str, action: str) -> bool:
            return False

        svc = DefaultExplainabilityService(auth_callback=auth_fail)
        dto = ExplanationRequestDTO(reasoning_result_id=str(uuid.uuid4()))
        response = svc.explain(dto, user_id="user-1")
        assert response is None

    def test_explain_with_auth_pass(self) -> None:
        def auth_pass(user_id: str, action: str) -> bool:
            return True

        svc = DefaultExplainabilityService(auth_callback=auth_pass)
        dto = ExplanationRequestDTO(reasoning_result_id=str(uuid.uuid4()))
        response = svc.explain(dto, user_id="user-1")
        assert response is not None

    def test_explain_calls_pre_and_post_hooks(self) -> None:
        pre_calls: list[str] = []
        post_calls: list[str] = []

        def pre_hook(**kwargs: object) -> None:
            pre_calls.append("pre")

        def post_hook(**kwargs: object) -> None:
            post_calls.append("post")

        hooks = IntegrationHooks()
        hooks.register_pre_explain(pre_hook)
        hooks.register_post_explain(post_hook)

        svc = DefaultExplainabilityService(hooks=hooks)
        dto = ExplanationRequestDTO(reasoning_result_id=str(uuid.uuid4()))
        svc.explain(dto)
        assert pre_calls == ["pre"]
        assert post_calls == ["post"]

    def test_explain_calls_audit_callback(self) -> None:
        audit_log: list[str] = []

        def audit(action: str, user: str, resource: str, details: dict) -> None:
            audit_log.append(f"{action}:{user}")

        svc = DefaultExplainabilityService(audit_callback=audit)
        dto = ExplanationRequestDTO(reasoning_result_id=str(uuid.uuid4()))
        svc.explain(dto, user_id="user-1")
        assert len(audit_log) >= 1
        assert "explain:user-1" in audit_log

    def test_explain_handles_error_and_fires_on_error(self) -> None:
        error_log: list[dict] = []

        def on_error(**kwargs: object) -> None:
            error_log.append(kwargs)

        hooks = IntegrationHooks()
        hooks.register_on_error(on_error)

        failing_manager = MagicMock()
        failing_manager.execute_explanation.side_effect = ValueError("Something went wrong")

        svc = DefaultExplainabilityService(
            manager=failing_manager,
            hooks=hooks,
        )
        dto = ExplanationRequestDTO(reasoning_result_id=str(uuid.uuid4()))
        response = svc.explain(dto)
        assert response is None
        assert len(error_log) >= 1
        assert "error" in error_log[0]
        assert isinstance(error_log[0]["error"], ValueError)

    def test_get_result(self) -> None:
        svc = DefaultExplainabilityService()
        dto = ExplanationRequestDTO(reasoning_result_id=str(uuid.uuid4()))
        svc.explain(dto)
        result = svc.get_result("nonexistent")
        assert result is None

    def test_get_result_after_explain(self) -> None:
        svc = DefaultExplainabilityService()
        dto = ExplanationRequestDTO(reasoning_result_id=str(uuid.uuid4()))
        response = svc.explain(dto)
        assert response is not None
        result = svc.get_result(str(response.result_id))
        assert result is not None
        assert isinstance(result, ExplanationResult)

    def test_get_result_with_auth_fail(self) -> None:
        def auth_fail(user_id: str, action: str) -> bool:
            return False

        svc = DefaultExplainabilityService(auth_callback=auth_fail)
        assert svc.get_result("test", user_id="user-1") is None

    def test_get_result_with_auth_pass(self) -> None:
        def auth_pass(user_id: str, action: str) -> bool:
            return True

        svc = DefaultExplainabilityService(auth_callback=auth_pass)
        dto = ExplanationRequestDTO(reasoning_result_id=str(uuid.uuid4()))
        svc.explain(dto)
        result = svc.get_result("nonexistent", user_id="user-1")
        assert result is None  # doesn't exist, but auth passes

    def test_get_package_returns_none(self) -> None:
        svc = DefaultExplainabilityService()
        assert svc.get_package("any-package-id") is None

    def test_get_health(self) -> None:
        svc = DefaultExplainabilityService()
        health = svc.get_health()
        assert isinstance(health, ExplanationHealth)

    def test_get_metrics(self) -> None:
        svc = DefaultExplainabilityService()
        metrics = svc.get_metrics()
        assert isinstance(metrics, ExplanationMetrics)

    def test_explain_with_correlation_id(self) -> None:
        svc = DefaultExplainabilityService()
        dto = ExplanationRequestDTO(reasoning_result_id=str(uuid.uuid4()))
        response = svc.explain(dto, correlation_id="test-cid")
        assert response is not None

    def test_explain_response_fields(self) -> None:
        svc = DefaultExplainabilityService()
        dto = ExplanationRequestDTO(reasoning_result_id=str(uuid.uuid4()))
        response = svc.explain(dto)
        assert response is not None
        assert response.result_id is not None
        assert response.request_id is not None
        assert response.status == "COMPLETED"
        assert response.narratives_count >= 1
        assert response.citations_count >= 1
        assert response.confidence > 0.0

    def test_explain_with_target_audiences(self) -> None:
        svc = DefaultExplainabilityService()
        dto = ExplanationRequestDTO(
            reasoning_result_id=str(uuid.uuid4()),
            target_audiences=["EXECUTIVE", "ENGINEER"],
            domain="ENERGY",
        )
        response = svc.explain(dto)
        assert response is not None
        assert response.narratives_count == 2

    def test_explain_with_empty_user_id_skips_auth(self) -> None:
        called = False

        def auth(user_id: str, action: str) -> bool:
            nonlocal called
            called = True
            return True

        svc = DefaultExplainabilityService(auth_callback=auth)
        dto = ExplanationRequestDTO(reasoning_result_id=str(uuid.uuid4()))
        response = svc.explain(dto)  # no user_id -> auth skipped
        assert response is not None
        assert not called

    def test_service_logs_and_returns_none_on_error(self) -> None:
        error_log: list[dict] = []

        def on_error(**kwargs: object) -> None:
            error_log.append(kwargs)

        hooks = IntegrationHooks()
        hooks.register_on_error(on_error)

        failing_mgr = MagicMock()
        failing_mgr.execute_explanation.side_effect = RuntimeError("Unexpected failure")

        svc = DefaultExplainabilityService(
            manager=failing_mgr,
            hooks=hooks,
            audit_callback=lambda a, u, r, d: None,
        )
        dto = ExplanationRequestDTO(reasoning_result_id=str(uuid.uuid4()))
        response = svc.explain(dto, user_id="user-1")
        assert response is None
        assert len(error_log) >= 1


# =============================================================================
# 7. Enhanced Contract Models
# =============================================================================


class TestSessionNewFields:
    def test_session_defaults(self) -> None:
        rid = uuid.uuid4()
        s = ExplanationSession(request_id=rid)
        assert s.domain == ExplanationDomain.SYSTEM
        assert s.target_layers == []
        assert s.status == ExplanationStatus.INITIALIZED
        assert s.completed_at is None
        assert s.statistics == {}

    def test_session_with_values(self) -> None:
        rid = uuid.uuid4()
        now = datetime.now(UTC)
        layers = [ExplanationLayer.EXECUTIVE]
        s = ExplanationSession(
            request_id=rid,
            domain=ExplanationDomain.ENERGY,
            target_layers=layers,
            status=ExplanationStatus.COMPLETED,
            completed_at=now,
            statistics={"narrative_count": 3},
        )
        assert s.domain == ExplanationDomain.ENERGY
        assert len(s.target_layers) == 1
        assert s.status == ExplanationStatus.COMPLETED
        assert s.completed_at == now
        assert s.statistics["narrative_count"] == 3


class TestDecisionNewFields:
    def test_decision_defaults(self) -> None:
        rid = uuid.uuid4()
        d = ExplanationDecision(result_id=rid)
        assert d.conclusion == ""
        assert d.reasoning_summary == ""
        assert d.recommendation_summary == ""
        assert d.selected_narratives == []
        assert d.rejected_narratives == []
        assert d.confidence == 0.0
        assert d.audience == ExplanationLayer.ENGINEER

    def test_decision_with_values(self) -> None:
        rid = uuid.uuid4()
        d = ExplanationDecision(
            result_id=rid,
            conclusion="Schedule maintenance",
            reasoning_summary="Evidence supports action",
            recommendation_summary="Repair within 7 days",
            selected_narratives=["n-1"],
            rejected_narratives=["n-2"],
            confidence=0.85,
            audience=ExplanationLayer.EXECUTIVE,
        )
        assert d.conclusion == "Schedule maintenance"
        assert d.reasoning_summary == "Evidence supports action"
        assert d.confidence == 0.85
        assert d.audience == ExplanationLayer.EXECUTIVE


class TestHealthNewFields:
    def test_health_defaults(self) -> None:
        h = ExplanationHealth()
        assert h.overall_status == ""
        assert h.coordinator_status == ""
        assert h.narrative_builder_status == ""
        assert h.citation_builder_status == ""
        assert h.audience_formatter_status == ""
        assert h.validator_status == ""
        assert h.explanation_count == 0
        assert h.error_count == 0

    def test_health_healthy(self) -> None:
        h = ExplanationHealth(
            overall_status="HEALTHY",
            coordinator_status="HEALTHY",
            narrative_builder_status="HEALTHY",
            citation_builder_status="HEALTHY",
            audience_formatter_status="HEALTHY",
            validator_status="HEALTHY",
        )
        assert h.overall_status == "HEALTHY"


class TestMetricsNewFields:
    def test_metrics_defaults(self) -> None:
        m = ExplanationMetrics()
        assert m.explanations_total == 0
        assert m.narratives_total == 0
        assert m.citations_total == 0
        assert m.packages_total == 0
        assert m.validated_total == 0
        assert m.failed_total == 0
        assert m.explanations_per_domain == {}
        assert m.explanations_per_layer == {}
        assert m.average_confidence == 0.0
        assert m.average_completeness == 0.0

    def test_metrics_with_values(self) -> None:
        m = ExplanationMetrics(
            explanations_total=10,
            narratives_total=25,
            citations_total=50,
            packages_total=9,
            validated_total=8,
            failed_total=1,
            explanations_per_domain={"ENERGY": 5, "SAFETY": 5},
            explanations_per_layer={"ENGINEER": 6, "EXECUTIVE": 4},
            average_confidence=0.78,
            average_completeness=0.82,
        )
        assert m.explanations_total == 10
        assert m.narratives_total == 25
        assert m.packages_total == 9
        assert m.explanations_per_domain["ENERGY"] == 5
        assert m.average_confidence == 0.78


class TestConfidenceNewFields:
    def test_confidence_defaults(self) -> None:
        c = ExplanationConfidence()
        assert c.overall_confidence == 0.0
        assert c.narrative_quality == 0.0
        assert c.citation_accuracy == 0.0
        assert c.completeness == 0.0
        assert c.audience_coverage == 0.0

    def test_confidence_with_values(self) -> None:
        c = ExplanationConfidence(
            overall_confidence=0.85,
            narrative_quality=0.9,
            citation_accuracy=0.75,
            completeness=0.8,
            audience_coverage=0.7,
        )
        assert c.overall_confidence == 0.85
        assert c.narrative_quality == 0.9
        assert c.citation_accuracy == 0.75
        assert c.completeness == 0.8
        assert c.audience_coverage == 0.7
