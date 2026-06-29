"""Phase 3 tests for the Action Engine (Enterprise Orchestration).

Tests all orchestration components, coordinator, manager,
hooks, and the public API service.
"""

from __future__ import annotations

import uuid

from adip.execution.contracts.models import (
    ExecutionConfidence,
    ExecutionDecision,
    ExecutionExplainabilityMetadata,
    ExecutionManifest,
    ExecutionRequest,
)
from adip.execution.dtos import ExecutionRequestDTO
from adip.execution.orchestration.adapter_registry import ExecutionAdapterRegistry
from adip.execution.orchestration.confidence import ExecutionConfidenceCalculator
from adip.execution.orchestration.context import ExecutionContextManager
from adip.execution.orchestration.coordinator import ExecutionCoordinatorImpl
from adip.execution.orchestration.health import ExecutionHealthManager
from adip.execution.orchestration.lineage import ExecutionLineage
from adip.execution.orchestration.manager import ExecutionManagerImpl
from adip.execution.orchestration.manifest import ExecutionManifestBuilder
from adip.execution.orchestration.quality import ExecutionQualityManager
from adip.execution.orchestration.readiness import ExecutionReadinessManager
from adip.execution.orchestration.review import ExecutionReview
from adip.execution.orchestration.session import ExecutionSessionManager
from adip.execution.orchestration.snapshot import ExecutionSnapshot
from adip.execution.orchestration.version_manager import ExecutionVersionManager
from adip.execution.services.hooks import IntegrationHooks
from adip.execution.services.service import DefaultExecutionService

# ═════════════════════════════════════════════════════════════════════════════
# ExecutionSessionManager
# ═════════════════════════════════════════════════════════════════════════════


class TestExecutionSessionManager:
    def test_create_session(self) -> None:
        mgr = ExecutionSessionManager()
        session = mgr.create_session(
            request_id=str(uuid.uuid4()),
            package_id=str(uuid.uuid4()),
            execution_mode="LIVE",
            priority="MEDIUM",
        )
        assert session.state.value == "PENDING"
        assert session.execution_mode.value == "LIVE"
        assert session.priority.value == "MEDIUM"

    def test_update_status_valid_transition(self) -> None:
        mgr = ExecutionSessionManager()
        session = mgr.create_session(request_id=str(uuid.uuid4()))
        assert mgr.update_status(str(session.session_id), "RUNNING") is True
        assert mgr.get_session(str(session.session_id)).state.value == "RUNNING"

    def test_update_status_invalid_transition(self) -> None:
        mgr = ExecutionSessionManager()
        session = mgr.create_session(request_id=str(uuid.uuid4()))
        # PENDING -> COMPLETED is a valid transition
        assert mgr.update_status(str(session.session_id), "RUNNING") is True
        assert mgr.update_status(str(session.session_id), "COMPLETED") is True

    def test_update_session_fields(self) -> None:
        mgr = ExecutionSessionManager()
        session = mgr.create_session(request_id=str(uuid.uuid4()))
        sid = str(session.session_id)
        assert mgr.update_session(sid, task_count=5, tasks_completed=3) is True
        s = mgr.get_session(sid)
        assert s.task_count == 5
        assert s.tasks_completed == 3

    def test_get_active_sessions(self) -> None:
        mgr = ExecutionSessionManager()
        s1 = mgr.create_session(request_id=str(uuid.uuid4()))
        s2 = mgr.create_session(request_id=str(uuid.uuid4()))
        mgr.update_status(str(s1.session_id), "COMPLETED")
        active = mgr.get_active_sessions()
        assert len(active) == 1
        assert active[0].session_id == s2.session_id

    def test_count_by_state(self) -> None:
        mgr = ExecutionSessionManager()
        s1 = mgr.create_session(request_id=str(uuid.uuid4()))
        mgr.create_session(request_id=str(uuid.uuid4()))
        mgr.update_status(str(s1.session_id), "COMPLETED")
        counts = mgr.count_by_state()
        assert counts.get("COMPLETED", 0) == 1
        assert counts.get("PENDING", 0) == 1


# ═════════════════════════════════════════════════════════════════════════════
# ExecutionConfidenceCalculator
# ═════════════════════════════════════════════════════════════════════════════


class TestExecutionConfidenceCalculator:
    def test_calculate_default(self) -> None:
        calc = ExecutionConfidenceCalculator()
        conf = calc.calculate()
        assert conf.overall_confidence == 0.0
        assert conf.resource_confidence == 0.0

    def test_calculate_high_confidence(self) -> None:
        calc = ExecutionConfidenceCalculator()
        conf = calc.calculate(
            resource_confidence=1.0,
            schedule_confidence=1.0,
            risk_confidence=1.0,
            quality_confidence=1.0,
            readiness_confidence=1.0,
            retry_confidence=1.0,
            compensation_confidence=1.0,
        )
        assert conf.overall_confidence == 1.0

    def test_calculate_clamps_values(self) -> None:
        calc = ExecutionConfidenceCalculator()
        conf = calc.calculate(
            resource_confidence=-0.5,
            schedule_confidence=1.5,
        )
        assert conf.resource_confidence == 0.0
        assert conf.schedule_confidence == 1.0

    def test_get_history(self) -> None:
        calc = ExecutionConfidenceCalculator()
        calc.calculate(resource_confidence=0.5)
        calc.calculate(resource_confidence=0.8)
        assert len(calc.get_history()) == 2


# ═════════════════════════════════════════════════════════════════════════════
# ExecutionReadinessManager
# ═════════════════════════════════════════════════════════════════════════════


class TestExecutionReadinessManager:
    def test_assess_ready(self) -> None:
        mgr = ExecutionReadinessManager()
        assessment = mgr.assess(
            session_id=str(uuid.uuid4()),
            resources_available=True,
            dependencies_satisfied=True,
            schedule_feasible=True,
            policy_compliant=True,
            risk_accepted=True,
        )
        assert assessment.status == "READY"
        assert assessment.score == 1.0

    def test_assess_blocked(self) -> None:
        mgr = ExecutionReadinessManager()
        assessment = mgr.assess(
            session_id=str(uuid.uuid4()),
            resources_available=True,
            dependencies_satisfied=False,
        )
        assert assessment.status == "BLOCKED"
        assert assessment.score < 1.0

    def test_get_all_assessments(self) -> None:
        mgr = ExecutionReadinessManager()
        mgr.assess(session_id=str(uuid.uuid4()))
        mgr.assess(session_id=str(uuid.uuid4()))
        assert len(mgr.get_all_assessments()) == 2


# ═════════════════════════════════════════════════════════════════════════════
# ExecutionReview
# ═════════════════════════════════════════════════════════════════════════════


class TestExecutionReview:
    def test_review_pass(self) -> None:
        review = ExecutionReview()
        result = review.review(
            session_id=str(uuid.uuid4()),
            task_count=5,
            has_dependencies=True,
            has_resources=True,
            has_schedule=True,
            has_compensation=True,
        )
        assert result.passed is True
        assert result.overall_score > 0.5

    def test_review_fail_no_tasks(self) -> None:
        review = ExecutionReview()
        result = review.review(session_id=str(uuid.uuid4()), task_count=0)
        assert result.passed is False

    def test_get_all_reviews(self) -> None:
        review = ExecutionReview()
        review.review(session_id=str(uuid.uuid4()), task_count=3)
        review.review(session_id=str(uuid.uuid4()), task_count=5)
        assert len(review.get_all_reviews()) == 2


# ═════════════════════════════════════════════════════════════════════════════
# ExecutionVersionManager
# ═════════════════════════════════════════════════════════════════════════════


class TestExecutionVersionManager:
    def test_create_version(self) -> None:
        mgr = ExecutionVersionManager()
        ver = mgr.create_version(package_id="pkg-1")
        assert ver.version_number == 1
        assert ver.is_active is True

    def test_multiple_versions(self) -> None:
        mgr = ExecutionVersionManager()
        mgr.create_version(package_id="pkg-1")
        mgr.create_version(package_id="pkg-1")
        versions = mgr.get_versions("pkg-1")
        assert len(versions) == 2
        assert mgr.get_active_version("pkg-1").version_number == 2

    def test_compare_versions(self) -> None:
        mgr = ExecutionVersionManager()
        v1 = mgr.create_version(package_id="pkg-1", description="First")
        v2 = mgr.create_version(package_id="pkg-1", description="Second")
        comparison = mgr.compare_versions("pkg-1", 1, 2)
        assert comparison["version_a_exists"] is True
        assert comparison["version_b_exists"] is True

    def test_get_all_version_count(self) -> None:
        mgr = ExecutionVersionManager()
        mgr.create_version(package_id="pkg-1")
        mgr.create_version(package_id="pkg-1")
        mgr.create_version(package_id="pkg-2")
        assert mgr.get_all_version_count() == 3


# ═════════════════════════════════════════════════════════════════════════════
# ExecutionLineage
# ═════════════════════════════════════════════════════════════════════════════


class TestExecutionLineage:
    def test_record_lineage(self) -> None:
        lineage = ExecutionLineage()
        record = lineage.record(request_id=str(uuid.uuid4()), stage="test", summary="Test entry")
        assert record.stage == "test"
        assert record.summary == "Test entry"

    def test_get_lineage_for_request(self) -> None:
        lineage = ExecutionLineage()
        rid = str(uuid.uuid4())
        lineage.record(request_id=rid, stage="s1")
        lineage.record(request_id=rid, stage="s2")
        lineage.record(request_id=str(uuid.uuid4()), stage="s3")
        records = lineage.get_lineage_for_request(rid)
        assert len(records) == 2


# ═════════════════════════════════════════════════════════════════════════════
# ExecutionSnapshot
# ═════════════════════════════════════════════════════════════════════════════


class TestExecutionSnapshot:
    def test_create_snapshot(self) -> None:
        snap = ExecutionSnapshot()
        record = snap.create_snapshot(
            session_id=str(uuid.uuid4()),
            request_id=str(uuid.uuid4()),
            task_count=5,
            readiness_score=0.8,
        )
        assert record.task_count == 5
        assert record.readiness_score == 0.8

    def test_get_snapshots_for_session(self) -> None:
        snap = ExecutionSnapshot()
        sid = str(uuid.uuid4())
        snap.create_snapshot(session_id=sid)
        snap.create_snapshot(session_id=sid)
        assert len(snap.get_snapshots_for_session(sid)) == 2


# ═════════════════════════════════════════════════════════════════════════════
# ExecutionHealthManager
# ═════════════════════════════════════════════════════════════════════════════


class TestExecutionHealthManager:
    def test_get_healthy(self) -> None:
        health = ExecutionHealthManager()
        h = health.get_health()
        assert h.overall_status == "HEALTHY"

    def test_get_degraded(self) -> None:
        health = ExecutionHealthManager()
        health.record_error()
        h = health.get_health()
        assert h.overall_status == "DEGRADED"

    def test_reset(self) -> None:
        health = ExecutionHealthManager()
        health.record_error()
        health.reset()
        assert health.get_health().overall_status == "HEALTHY"


# ═════════════════════════════════════════════════════════════════════════════
# ExecutionQualityManager
# ═════════════════════════════════════════════════════════════════════════════


class TestExecutionQualityManager:
    def test_assess_high_quality(self) -> None:
        mgr = ExecutionQualityManager()
        assessment = mgr.assess(
            session_id=str(uuid.uuid4()),
            task_count=10,
            tasks_completed=10,
            tasks_failed=0,
            has_audit=True,
            has_telemetry=True,
            has_compensation=True,
        )
        assert assessment.overall_quality > 0.5

    def test_assess_low_quality(self) -> None:
        mgr = ExecutionQualityManager()
        assessment = mgr.assess(
            session_id=str(uuid.uuid4()),
            task_count=0,
        )
        assert assessment.overall_quality < 0.5

    def test_get_all_assessments(self) -> None:
        mgr = ExecutionQualityManager()
        mgr.assess(session_id=str(uuid.uuid4()), task_count=5)
        mgr.assess(session_id=str(uuid.uuid4()), task_count=3)
        assert len(mgr.get_all_assessments()) == 2


# ═════════════════════════════════════════════════════════════════════════════
# ExecutionManifestBuilder
# ═════════════════════════════════════════════════════════════════════════════


class TestExecutionManifestBuilder:
    def test_build_manifest(self) -> None:
        builder = ExecutionManifestBuilder()
        manifest = builder.build(
            package_id=str(uuid.uuid4()),
            required_adapters=["mqtt", "http"],
            requires_compensation=True,
        )
        assert manifest.required_adapters == ["mqtt", "http"]
        assert manifest.compensation_required is True

    def test_get_manifest_not_found(self) -> None:
        builder = ExecutionManifestBuilder()
        assert builder.get_manifest("nonexistent") is None


# ═════════════════════════════════════════════════════════════════════════════
# ExecutionAdapterRegistry
# ═════════════════════════════════════════════════════════════════════════════


class TestExecutionAdapterRegistry:
    def test_register_adapter(self) -> None:
        registry = ExecutionAdapterRegistry()
        assert registry.register_adapter("mqtt", capabilities=["publish", "subscribe"]) is True
        assert registry.has_adapter("mqtt") is True

    def test_register_duplicate(self) -> None:
        registry = ExecutionAdapterRegistry()
        registry.register_adapter("mqtt")
        assert registry.register_adapter("mqtt") is False

    def test_unregister_adapter(self) -> None:
        registry = ExecutionAdapterRegistry()
        registry.register_adapter("mqtt")
        assert registry.unregister_adapter("mqtt") is True
        assert registry.has_adapter("mqtt") is False

    def test_get_capabilities(self) -> None:
        registry = ExecutionAdapterRegistry()
        registry.register_adapter("http", capabilities=["get", "post"])
        assert registry.get_capabilities_for("http") == ["get", "post"]
        assert registry.get_capabilities_for("unknown") == []

    def test_count(self) -> None:
        registry = ExecutionAdapterRegistry()
        registry.register_adapter("mqtt")
        registry.register_adapter("http")
        assert registry.count() == 2


# ═════════════════════════════════════════════════════════════════════════════
# ExecutionContextManager
# ═════════════════════════════════════════════════════════════════════════════


class TestExecutionContextManager:
    def test_build_context(self) -> None:
        mgr = ExecutionContextManager()
        request = ExecutionRequest(
            action_decision_id=uuid.uuid4(),
            domain="ENERGY",
            target="turbine-01",
            metadata={"asset_id": "asset-01", "facility_id": "fac-01"},
        )
        context = mgr.build(request)
        assert context.asset_id == "asset-01"
        assert context.facility_id == "fac-01"
        assert context.domain == "ENERGY"

    def test_get_context(self) -> None:
        mgr = ExecutionContextManager()
        request = ExecutionRequest(action_decision_id=uuid.uuid4())
        context = mgr.build(request)
        assert mgr.get_context(str(context.context_id)) is not None
        assert mgr.get_context("nonexistent") is None


# ═════════════════════════════════════════════════════════════════════════════
# ExecutionCoordinatorImpl
# ═════════════════════════════════════════════════════════════════════════════


class TestExecutionCoordinatorImpl:
    def test_execute_returns_result(self) -> None:
        coord = ExecutionCoordinatorImpl()
        request = ExecutionRequest(action_decision_id=uuid.uuid4())
        result = coord.execute(request)
        assert result.overall_success is True
        assert result.request_id == request.request_id

    def test_get_session(self) -> None:
        coord = ExecutionCoordinatorImpl()
        request = ExecutionRequest(action_decision_id=uuid.uuid4())
        result = coord.execute(request)
        session = coord.get_session(str(result.session_id))
        assert session is not None
        assert session.state.value in ("COMPLETED", "FAILED")

    def test_get_result_by_session(self) -> None:
        coord = ExecutionCoordinatorImpl()
        request = ExecutionRequest(action_decision_id=uuid.uuid4())
        result = coord.execute(request)
        retrieved = coord.get_result(str(result.session_id))
        assert retrieved is not None
        assert retrieved.overall_success == result.overall_success

    def test_cancel_session(self) -> None:
        coord = ExecutionCoordinatorImpl()
        request = ExecutionRequest(action_decision_id=uuid.uuid4())
        result = coord.execute(request)
        # Already completed, should fail to cancel
        assert coord.cancel(str(result.session_id)) is False

    def test_health(self) -> None:
        coord = ExecutionCoordinatorImpl()
        health = coord.health()
        assert health.overall_status == "HEALTHY"

    def test_metrics(self) -> None:
        coord = ExecutionCoordinatorImpl()
        request = ExecutionRequest(action_decision_id=uuid.uuid4())
        coord.execute(request)
        metrics = coord.metrics()
        assert metrics.sessions_total >= 1


# ═════════════════════════════════════════════════════════════════════════════
# ExecutionManagerImpl
# ═════════════════════════════════════════════════════════════════════════════


class TestExecutionManagerImpl:
    def test_start_execution(self) -> None:
        mgr = ExecutionManagerImpl()
        request = ExecutionRequest(action_decision_id=uuid.uuid4())
        session = mgr.start_execution(request)
        assert session.request_id == request.request_id
        assert session.state.value in ("COMPLETED", "FAILED")

    def test_get_health(self) -> None:
        mgr = ExecutionManagerImpl()
        health = mgr.get_health()
        assert health.overall_status == "HEALTHY"

    def test_get_metrics(self) -> None:
        mgr = ExecutionManagerImpl()
        request = ExecutionRequest(action_decision_id=uuid.uuid4())
        mgr.start_execution(request)
        metrics = mgr.get_metrics()
        assert metrics.sessions_total >= 1

    def test_cancel_execution(self) -> None:
        mgr = ExecutionManagerImpl()
        # Need a session first
        request = ExecutionRequest(action_decision_id=uuid.uuid4())
        session = mgr.start_execution(request)
        # Already terminal, should fail
        assert mgr.cancel_execution(str(session.session_id), "test") is False


# ═════════════════════════════════════════════════════════════════════════════
# IntegrationHooks
# ═════════════════════════════════════════════════════════════════════════════


class TestIntegrationHooks:
    def test_hooks_execute(self) -> None:
        hooks = IntegrationHooks()
        calls: list[str] = []

        hooks.register_pre_execute(lambda **kw: calls.append("pre"))
        hooks.register_post_execute(lambda **kw: calls.append("post"))

        hooks.fire_pre_execute("req-1")
        hooks.fire_post_execute("sess-1", True)

        assert "pre" in calls
        assert "post" in calls

    def test_hook_exception_isolation(self) -> None:
        hooks = IntegrationHooks()

        def failing_hook(**kw: object) -> None:
            raise ValueError("Hook failed")

        calls: list[str] = []

        def good_hook(**kw: object) -> None:
            calls.append("good")

        hooks.register_pre_execute(failing_hook)
        hooks.register_pre_execute(good_hook)

        hooks.fire_pre_execute("req-1")

        assert "good" in calls

    def test_all_hook_types(self) -> None:
        hooks = IntegrationHooks()
        calls: list[str] = []

        hooks.register_pre_execute(lambda **kw: calls.append("pre_execute"))
        hooks.register_post_execute(lambda **kw: calls.append("post_execute"))
        hooks.register_on_error(lambda **kw: calls.append("on_error"))
        hooks.register_session_created(lambda **kw: calls.append("session_created"))
        hooks.register_session_completed(lambda **kw: calls.append("session_completed"))
        hooks.register_decision_made(lambda **kw: calls.append("decision_made"))
        hooks.register_readiness_assessed(lambda **kw: calls.append("readiness_assessed"))
        hooks.register_task_completed(lambda **kw: calls.append("task_completed"))
        hooks.register_retry_performed(lambda **kw: calls.append("retry_performed"))
        hooks.register_compensation_triggered(lambda **kw: calls.append("compensation_triggered"))

        hooks.fire_pre_execute("req-1")
        hooks.fire_post_execute("sess-1", True)
        hooks.fire_on_error("sess-1", "err")
        hooks.fire_session_created("sess-1")
        hooks.fire_session_completed("sess-1", "COMPLETED")
        hooks.fire_decision_made("dec-1", True)
        hooks.fire_readiness_assessed("sess-1", "READY", 1.0)
        hooks.fire_task_completed("task-1", True)
        hooks.fire_retry_performed("task-1", 1)
        hooks.fire_compensation_triggered("sess-1", "task-1")

        assert len(calls) == 10


# ═════════════════════════════════════════════════════════════════════════════
# DefaultExecutionService
# ═════════════════════════════════════════════════════════════════════════════


class TestDefaultExecutionService:
    def test_start_execution(self) -> None:
        service = DefaultExecutionService()
        dto = ExecutionRequestDTO(
            action_decision_id=uuid.uuid4(),
            domain="ENERGY",
        )
        response = service.start_execution(dto, user_id="test-user")
        assert response is not None
        assert response.state.value != "PENDING"

    def test_start_execution_auth_failure(self) -> None:
        def deny_auth(user_id: str, permission: str) -> bool:
            return False

        service = DefaultExecutionService(auth_callback=deny_auth)
        dto = ExecutionRequestDTO(action_decision_id=uuid.uuid4())
        response = service.start_execution(dto, user_id="test-user")
        assert response is None

    def test_get_session(self) -> None:
        service = DefaultExecutionService()
        dto = ExecutionRequestDTO(action_decision_id=uuid.uuid4())
        response = service.start_execution(dto)
        assert response is not None
        session = service.get_session(str(response.session_id))
        assert session is not None

    def test_get_health(self) -> None:
        service = DefaultExecutionService()
        health = service.get_health()
        assert health.overall_status == "HEALTHY"

    def test_get_metrics(self) -> None:
        service = DefaultExecutionService()
        metrics = service.get_metrics()
        assert metrics.sessions_total >= 0


# ═════════════════════════════════════════════════════════════════════════════
# Contract Model Tests (Phase 3 models)
# ═════════════════════════════════════════════════════════════════════════════


class TestExecutionDecision:
    def test_defaults(self) -> None:
        decision = ExecutionDecision(
            request_id=uuid.uuid4(),
            session_id=uuid.uuid4(),
        )
        assert decision.overall_success is False
        assert decision.state.value == "PENDING"
        assert decision.tasks_total == 0

    def test_with_confidence(self) -> None:
        confidence = ExecutionConfidence(overall_confidence=0.85)
        decision = ExecutionDecision(
            request_id=uuid.uuid4(),
            session_id=uuid.uuid4(),
            overall_success=True,
            confidence=confidence,
        )
        assert decision.confidence.overall_confidence == 0.85

    def test_with_explainability(self) -> None:
        explain = ExecutionExplainabilityMetadata(
            why_session_created="Test session",
        )
        decision = ExecutionDecision(
            request_id=uuid.uuid4(),
            session_id=uuid.uuid4(),
            explainability=explain,
        )
        assert decision.explainability.why_session_created == "Test session"


class TestExecutionConfidence:
    def test_defaults(self) -> None:
        conf = ExecutionConfidence()
        assert conf.overall_confidence == 0.0
        assert conf.resource_confidence == 0.0
        assert conf.compensation_confidence == 0.0


class TestExecutionExplainabilityMetadata:
    def test_defaults(self) -> None:
        meta = ExecutionExplainabilityMetadata()
        assert meta.why_session_created == ""
        assert meta.why_task_ordered == ""


class TestExecutionManifest:
    def test_defaults(self) -> None:
        manifest = ExecutionManifest(package_id=uuid.uuid4())
        assert manifest.required_adapters == []
        assert manifest.required_sandbox is False
        assert manifest.compensation_required is False
