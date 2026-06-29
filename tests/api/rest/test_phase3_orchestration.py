"""Tests for REST API Layer Phase 3 — Enterprise Orchestration."""

from __future__ import annotations

from typing import Any

import pytest

from adip.api.rest.adapters.planner import PlannerAdapter
from adip.api.rest.adapters.router_registry import clear_registry, register_adapter
from adip.api.rest.orchestration.audit_package import APIAuditPackage
from adip.api.rest.orchestration.compliance import APIContractCompliance
from adip.api.rest.orchestration.coordinator import APICoordinator
from adip.api.rest.orchestration.health import APIHealthManager
from adip.api.rest.orchestration.hooks import IntegrationHooks
from adip.api.rest.orchestration.lineage import APILineage
from adip.api.rest.orchestration.manager import APIManager
from adip.api.rest.orchestration.models import (
    ApiDecision,
    APIFeatureFlag,
    APIFeatureFlags,
    APISecurityContext,
    ApiSession,
)
from adip.api.rest.orchestration.quality import APIQualityManager
from adip.api.rest.orchestration.readiness import APIReadiness
from adip.api.rest.orchestration.session import ApiSessionManager
from adip.api.rest.orchestration.snapshot import APISnapshot
from adip.api.rest.orchestration.version_manager import ApiVersionManager
from adip.api.rest.services.service import APIService

# =============================================================================
# ApiSession & ApiSessionManager Tests
# =============================================================================

class TestApiSessionModel:
    def test_default_creation(self) -> None:
        session = ApiSession()
        assert session.status.value == "pending"
        assert session.method == "GET"
        assert session.api_version == "v1"

    def test_custom_values(self) -> None:
        session = ApiSession(
            route="/api/v1/test",
            method="POST",
            api_version="v2",
        )
        assert session.route == "/api/v1/test"
        assert session.method == "POST"
        assert session.api_version == "v2"


class TestApiSessionManager:
    @pytest.fixture
    def manager(self) -> ApiSessionManager:
        return ApiSessionManager()

    def test_create_session(self, manager: ApiSessionManager) -> None:
        session = manager.create_session(route="/test", method="GET", correlation_id="cid-123")
        assert session.route == "/test"
        assert session.method == "GET"
        assert session.correlation_id == "cid-123"

    def test_get_session(self, manager: ApiSessionManager) -> None:
        created = manager.create_session()
        retrieved = manager.get_session(str(created.session_id))
        assert retrieved is not None
        assert str(retrieved.session_id) == str(created.session_id)

    def test_complete_session(self, manager: ApiSessionManager) -> None:
        session = manager.create_session()
        assert manager.complete_session(str(session.session_id)) is True
        assert manager.get_session(str(session.session_id)).status.value == "completed"

    def test_fail_session(self, manager: ApiSessionManager) -> None:
        session = manager.create_session()
        assert manager.fail_session(str(session.session_id)) is True
        assert manager.get_session(str(session.session_id)).status.value == "failed"

    def test_complete_nonexistent_session(self, manager: ApiSessionManager) -> None:
        assert manager.complete_session("nonexistent") is False

    def test_list_sessions(self, manager: ApiSessionManager) -> None:
        manager.create_session(route="/a")
        manager.create_session(route="/b")
        assert len(manager.list_sessions()) == 2

    def test_get_active_sessions(self, manager: ApiSessionManager) -> None:
        s1 = manager.create_session()
        s2 = manager.create_session()
        manager.complete_session(str(s1.session_id))
        active = manager.get_active_sessions()
        assert len(active) == 1
        assert active[0].session_id == s2.session_id

    def test_count(self, manager: ApiSessionManager) -> None:
        manager.create_session()
        manager.create_session()
        assert manager.count() == 2

    def test_clear(self, manager: ApiSessionManager) -> None:
        manager.create_session()
        manager.clear()
        assert manager.count() == 0


# =============================================================================
# ApiDecision Tests
# =============================================================================

class TestApiDecision:
    def test_default_creation(self) -> None:
        decision = ApiDecision()
        assert decision.success is True
        assert decision.status_code == 200
        assert decision.validation_passed is True


# =============================================================================
# APISecurityContext Tests
# =============================================================================

class TestAPISecurityContext:
    def test_default_context(self) -> None:
        ctx = APISecurityContext()
        assert ctx.is_authenticated() is False
        assert ctx.roles == []

    def test_authenticated(self) -> None:
        ctx = APISecurityContext(user_id="user-1", roles=["admin"], permissions=["read", "write"])
        assert ctx.is_authenticated() is True
        assert ctx.has_role("admin") is True
        assert ctx.has_role("user") is False
        assert ctx.has_permission("read") is True
        assert ctx.has_permission("delete") is False


# =============================================================================
# APIFeatureFlags Tests
# =============================================================================

class TestAPIFeatureFlags:
    @pytest.fixture
    def flags(self) -> APIFeatureFlags:
        return APIFeatureFlags(flags=[
            APIFeatureFlag(name="beta-api", enabled=True),
            APIFeatureFlag(name="experimental", enabled=False),
        ])

    def test_is_enabled(self, flags: APIFeatureFlags) -> None:
        assert flags.is_enabled("beta-api") is True
        assert flags.is_enabled("experimental") is False
        assert flags.is_enabled("nonexistent") is False

    def test_enable(self, flags: APIFeatureFlags) -> None:
        flags.enable("experimental")
        assert flags.is_enabled("experimental") is True

    def test_disable(self, flags: APIFeatureFlags) -> None:
        flags.disable("beta-api")
        assert flags.is_enabled("beta-api") is False

    def test_list_enabled(self, flags: APIFeatureFlags) -> None:
        enabled = flags.list_enabled()
        assert "beta-api" in enabled
        assert "experimental" not in enabled

    def test_enable_new_flag(self, flags: APIFeatureFlags) -> None:
        flags.enable("new-feature")
        assert flags.is_enabled("new-feature") is True


# =============================================================================
# ApiVersionManager Tests
# =============================================================================

class TestApiVersionManager:
    @pytest.fixture
    def manager(self) -> ApiVersionManager:
        return ApiVersionManager()

    def test_get_active_version(self, manager: ApiVersionManager) -> None:
        assert manager.get_active_version() == "v1"

    def test_set_active_version(self, manager: ApiVersionManager) -> None:
        manager.set_active_version("v2")
        assert manager.get_active_version() == "v2"

    def test_is_supported(self, manager: ApiVersionManager) -> None:
        assert manager.is_supported("v1") is True
        assert manager.is_supported("v3") is False

    def test_check_compatibility(self, manager: ApiVersionManager) -> None:
        assert manager.check_compatibility("v1") is True
        assert manager.check_compatibility("v2") is False

    def test_get_history(self, manager: ApiVersionManager) -> None:
        history = manager.get_history()
        assert len(history) >= 1
        assert history[0]["version"] == "v1"

    def test_register_version(self, manager: ApiVersionManager) -> None:
        manager.register_version("v2", "Version 2 preview")
        history = manager.get_history()
        assert len(history) == 2
        assert history[1]["version"] == "v2"


# =============================================================================
# APIHealthManager Tests
# =============================================================================

class TestAPIHealthManager:
    @pytest.fixture
    def manager(self) -> APIHealthManager:
        return APIHealthManager()

    def test_register_component(self, manager: APIHealthManager) -> None:
        manager.register_component("routers", "healthy")
        health = manager.get_health()
        assert health["overall_status"] == "healthy"
        assert "routers" in health["components"]

    def test_update_status(self, manager: APIHealthManager) -> None:
        manager.register_component("routers", "healthy")
        manager.update_status("routers", "degraded", {"error": "timeout"})
        comp = manager.get_component_health("routers")
        assert comp["status"] == "degraded"

    def test_is_healthy(self, manager: APIHealthManager) -> None:
        manager.register_component("a", "healthy")
        manager.register_component("b", "healthy")
        assert manager.is_healthy() is True
        manager.update_status("b", "unhealthy")
        assert manager.is_healthy() is False

    def test_count_unhealthy(self, manager: APIHealthManager) -> None:
        manager.register_component("a", "healthy")
        manager.register_component("b", "unhealthy")
        assert manager.count_unhealthy() == 1

    def test_get_component_health_nonexistent(self, manager: APIHealthManager) -> None:
        assert manager.get_component_health("nonexistent") is None


# =============================================================================
# APIAuditPackage Tests
# =============================================================================

class TestAPIAuditPackage:
    @pytest.fixture
    def manager(self) -> APIAuditPackage:
        return APIAuditPackage()

    def test_create_package(self, manager: APIAuditPackage) -> None:
        pkg = manager.create_package(
            request_data={"action": "test"},
            response_data={"result": "ok"},
            headers={"x-request-id": "123"},
        )
        assert pkg.request_data["action"] == "test"
        assert pkg.response_data["result"] == "ok"
        assert pkg.hash != ""

    def test_get_package(self, manager: APIAuditPackage) -> None:
        pkg = manager.create_package()
        retrieved = manager.get_package(str(pkg.audit_id))
        assert retrieved is not None

    def test_verify_package(self, manager: APIAuditPackage) -> None:
        pkg = manager.create_package(request_data={"key": "value"})
        assert manager.verify_package(str(pkg.audit_id)) is True
        assert manager.verify_package("nonexistent") is False

    def test_list_packages(self, manager: APIAuditPackage) -> None:
        manager.create_package()
        manager.create_package()
        assert len(manager.list_packages()) == 2

    def test_count(self, manager: APIAuditPackage) -> None:
        manager.create_package()
        assert manager.count() == 1

    def test_clear(self, manager: APIAuditPackage) -> None:
        manager.create_package()
        manager.clear()
        assert manager.count() == 0


# =============================================================================
# APILineage Tests
# =============================================================================

class TestAPILineage:
    @pytest.fixture
    def lineage(self) -> APILineage:
        return APILineage()

    def test_start_trace(self, lineage: APILineage) -> None:
        tid = lineage.start_trace()
        assert tid is not None

    def test_record_stage(self, lineage: APILineage) -> None:
        tid = lineage.start_trace()
        lineage.record_stage(tid, "test_stage", {"key": "value"})
        entries = lineage.get_lineage(tid)
        assert len(entries) == 2  # request + test_stage

    def test_record_middleware(self, lineage: APILineage) -> None:
        tid = lineage.start_trace()
        lineage.record_middleware(tid, "CorrelationMiddleware", "passed")
        entries = lineage.get_lineage(tid)
        assert any(e["stage"] == "middleware" for e in entries)

    def test_record_router(self, lineage: APILineage) -> None:
        tid = lineage.start_trace()
        lineage.record_router(tid, "/test", "GET")
        assert len(lineage.get_lineage(tid)) == 2

    def test_record_adapter(self, lineage: APILineage) -> None:
        tid = lineage.start_trace()
        lineage.record_adapter(tid, "PlannerAdapter", "create_plan")
        assert len(lineage.get_lineage(tid)) == 2

    def test_record_service(self, lineage: APILineage) -> None:
        tid = lineage.start_trace()
        lineage.record_service(tid, "PlannerService", "called")
        assert len(lineage.get_lineage(tid)) == 2

    def test_record_response(self, lineage: APILineage) -> None:
        tid = lineage.start_trace()
        lineage.record_response(tid, 200)
        entries = lineage.get_lineage(tid)
        assert entries[-1]["data"]["status_code"] == 200

    def test_get_lineage_nonexistent(self, lineage: APILineage) -> None:
        assert lineage.get_lineage("nonexistent") is None

    def test_list_traces(self, lineage: APILineage) -> None:
        lineage.start_trace("trace-1")
        lineage.start_trace("trace-2")
        assert "trace-1" in lineage.list_traces()
        assert "trace-2" in lineage.list_traces()

    def test_clear(self, lineage: APILineage) -> None:
        lineage.start_trace()
        lineage.clear()
        assert len(lineage.list_traces()) == 0

    def test_record_stage_creates_trace(self, lineage: APILineage) -> None:
        lineage.record_stage("auto-trace", "test")
        assert lineage.get_lineage("auto-trace") is not None


# =============================================================================
# APISnapshot Tests
# =============================================================================

class TestAPISnapshot:
    @pytest.fixture
    def manager(self) -> APISnapshot:
        return APISnapshot()

    def test_create_snapshot(self, manager: APISnapshot) -> None:
        snap = manager.create_snapshot(
            request={"method": "GET"},
            response={"status": 200},
            headers={"x-id": "1"},
        )
        assert snap.request["method"] == "GET"
        assert snap.response["status"] == 200

    def test_get_snapshot(self, manager: APISnapshot) -> None:
        snap = manager.create_snapshot()
        retrieved = manager.get_snapshot(str(snap.snapshot_id))
        assert retrieved is not None

    def test_list_snapshots(self, manager: APISnapshot) -> None:
        manager.create_snapshot()
        manager.create_snapshot()
        assert len(manager.list_snapshots()) == 2

    def test_count(self, manager: APISnapshot) -> None:
        manager.create_snapshot()
        assert manager.count() == 1

    def test_clear(self, manager: APISnapshot) -> None:
        manager.create_snapshot()
        manager.clear()
        assert manager.count() == 0


# =============================================================================
# APIReadiness Tests
# =============================================================================

class TestAPIReadiness:
    @pytest.fixture
    def readiness(self) -> APIReadiness:
        return APIReadiness()

    def test_default_not_ready(self, readiness: APIReadiness) -> None:
        assert readiness.is_ready() is False

    def test_check_version_valid(self, readiness: APIReadiness) -> None:
        check = readiness.check_version("v1")
        assert check.ready is True

    def test_check_version_invalid(self, readiness: APIReadiness) -> None:
        check = readiness.check_version("v3")
        assert check.ready is False

    def test_check_routers(self, readiness: APIReadiness) -> None:
        check = readiness.check_routers(16)
        assert check.ready is True
        check = readiness.check_routers(0)
        assert check.ready is False

    def test_check_adapters(self, readiness: APIReadiness) -> None:
        check = readiness.check_adapters(15)
        assert check.ready is True

    def test_check_validation(self, readiness: APIReadiness) -> None:
        check = readiness.check_validation(True)
        assert check.ready is True

    def test_is_ready_all_checks(self, readiness: APIReadiness) -> None:
        readiness.check_version("v1")
        readiness.check_routers(16)
        readiness.check_adapters(15)
        readiness.check_validation(True)
        assert readiness.is_ready() is True

    def test_get_readiness_report(self, readiness: APIReadiness) -> None:
        readiness.check_version("v1")
        report = readiness.get_readiness_report()
        assert report["check_count"] == 1
        assert "api_version" in report["checks"]

    def test_register_and_update_check(self, readiness: APIReadiness) -> None:
        readiness.register_check("custom", True, "Custom check passed")
        assert readiness.is_ready() is True
        readiness.update_check("custom", False, "Custom check failed")
        assert readiness.is_ready() is False

    def test_reset(self, readiness: APIReadiness) -> None:
        readiness.check_version("v1")
        readiness.reset()
        assert readiness.is_ready() is False


# =============================================================================
# APIQualityManager Tests
# =============================================================================

class TestAPIQualityManager:
    @pytest.fixture
    def manager(self) -> APIQualityManager:
        return APIQualityManager()

    def test_evaluate_validation_quality_passed(self, manager: APIQualityManager) -> None:
        qs = manager.evaluate_validation_quality(True)
        assert qs.score == 1.0

    def test_evaluate_validation_quality_failed(self, manager: APIQualityManager) -> None:
        qs = manager.evaluate_validation_quality(False, total_checks=5, failed_checks=2)
        assert qs.score == 0.6

    def test_contract_compliance(self, manager: APIQualityManager) -> None:
        qs = manager.evaluate_contract_compliance(True)
        assert qs.score == 1.0
        qs = manager.evaluate_contract_compliance(False)
        assert qs.score == 0.0

    def test_response_completeness(self, manager: APIQualityManager) -> None:
        assert manager.evaluate_response_completeness(True).score == 1.0
        assert manager.evaluate_response_completeness(False).score == 0.0
        assert manager.evaluate_response_completeness(True, has_errors=True).score == 0.5

    def test_processing_time(self, manager: APIQualityManager) -> None:
        assert manager.evaluate_processing_time(0).score == 1.0
        assert manager.evaluate_processing_time(500, threshold_ms=1000).score == 0.5
        assert manager.evaluate_processing_time(2000, threshold_ms=1000).score == 0.0

    def test_overall_quality(self, manager: APIQualityManager) -> None:
        manager.evaluate_validation_quality(True)
        manager.evaluate_contract_compliance(True)
        assert manager.get_overall_quality() == 1.0

    def test_quality_report(self, manager: APIQualityManager) -> None:
        manager.evaluate_validation_quality(True)
        report = manager.get_quality_report()
        assert "overall_score" in report
        assert "dimensions" in report

    def test_reset(self, manager: APIQualityManager) -> None:
        manager.evaluate_validation_quality(True)
        manager.reset()
        assert len(manager.get_quality_report()["dimensions"]) == 0

    def test_overall_quality_no_scores(self, manager: APIQualityManager) -> None:
        assert manager.get_overall_quality() == 1.0


# =============================================================================
# APIContractCompliance Tests
# =============================================================================

class TestAPIContractCompliance:
    @pytest.fixture
    def compliance(self) -> APIContractCompliance:
        return APIContractCompliance()

    def test_validate_openapi_valid(self, compliance: APIContractCompliance) -> None:
        schema = {"openapi": "3.0.0", "paths": {"/test": {"get": {}}}}
        result = compliance.validate_openapi(schema)
        assert result.is_compliant is True

    def test_validate_openapi_missing(self, compliance: APIContractCompliance) -> None:
        result = compliance.validate_openapi(None)
        assert result.is_compliant is False
        assert "missing" in result.errors[0].lower()

    def test_validate_version_compatibility_valid(self, compliance: APIContractCompliance) -> None:
        result = compliance.validate_version_compatibility("v1")
        assert result.is_compliant is True

    def test_validate_version_compatibility_invalid(self, compliance: APIContractCompliance) -> None:
        result = compliance.validate_version_compatibility("v3")
        assert result.is_compliant is False

    def test_validate_request_schema(self, compliance: APIContractCompliance) -> None:
        from pydantic import BaseModel

        class TestModel(BaseModel):
            name: str

        result = compliance.validate_request_schema(TestModel, {"name": "test"})
        assert result.is_compliant is True

        result = compliance.validate_request_schema(TestModel, {})
        assert result.is_compliant is False


# =============================================================================
# IntegrationHooks Tests
# =============================================================================

class TestIntegrationHooks:
    @pytest.fixture
    def hooks(self) -> IntegrationHooks:
        h = IntegrationHooks()
        h.clear()
        return h

    def test_register_and_execute(self, hooks: IntegrationHooks) -> None:
        results: list[str] = []

        def pre_request_hook(domain: str, **kwargs: Any) -> None:
            results.append(f"pre:{domain}")

        hooks.register("pre_request", pre_request_hook)
        hooks.execute("pre_request", domain="test")
        assert "pre:test" in results

    def test_multiple_hooks(self, hooks: IntegrationHooks) -> None:
        def hook1(**kwargs: Any) -> int:
            return 1

        def hook2(**kwargs: Any) -> int:
            return 2

        hooks.register("post_request", hook1)
        hooks.register("post_request", hook2)
        results = hooks.execute("post_request")
        assert results == [1, 2]

    def test_hook_exception_isolation(self, hooks: IntegrationHooks) -> None:
        def failing_hook(**kwargs: Any) -> None:
            raise ValueError("Hook failed")

        def working_hook(**kwargs: Any) -> str:
            return "ok"

        hooks.register("on_error", failing_hook)
        hooks.register("on_error", working_hook)
        results = hooks.execute("on_error", exception=ValueError("test"))
        assert results == ["ok"]

    def test_unknown_hook_type(self, hooks: IntegrationHooks) -> None:
        def hook(**kwargs: Any) -> None:
            pass

        hooks.register("nonexistent", hook)
        # Should not raise, just log warning
        results = hooks.execute("nonexistent")
        assert results == []

    def test_list_hooks(self, hooks: IntegrationHooks) -> None:
        def hook(**kwargs: Any) -> None:
            pass

        hooks.register("pre_request", hook)
        listed = hooks.list_hooks()
        assert "pre_request" in listed
        assert hook.__name__ in listed["pre_request"]

    def test_clear(self, hooks: IntegrationHooks) -> None:
        def hook(**kwargs: Any) -> None:
            pass

        hooks.register("pre_request", hook)
        hooks.clear()
        assert len(hooks.list_hooks()["pre_request"]) == 0

    def test_all_hook_types_present(self, hooks: IntegrationHooks) -> None:
        expected_types = {
            "pre_request", "post_request", "pre_validation", "post_validation",
            "pre_routing", "post_routing", "pre_adapter", "post_adapter",
            "pre_response", "post_response", "on_error",
        }
        listed = hooks.list_hooks()
        assert set(listed.keys()) == expected_types


# =============================================================================
# APICoordinator Tests
# =============================================================================

class TestAPICoordinator:
    def setup_method(self) -> None:
        clear_registry()
        register_adapter("planner", PlannerAdapter())

    def test_process_request_success(self) -> None:
        coordinator = APICoordinator()
        decision = coordinator.process_request(
            domain="planner",
            operation="create_plan",
            request_data={"name": "test"},
            method="POST",
        )
        assert decision.success is True
        assert decision.status_code == 200
        assert decision.processing_time_ms >= 0

    def test_process_request_no_adapter(self) -> None:
        coordinator = APICoordinator()
        decision = coordinator.process_request(
            domain="nonexistent",
            operation="test",
        )
        assert decision.success is False
        assert decision.status_code == 500

    def test_process_request_records_metrics(self) -> None:
        coordinator = APICoordinator()
        coordinator.process_request(domain="planner", operation="create_plan")
        metrics = coordinator.get_metrics()
        assert metrics["total_calls"] >= 1

    def test_get_health(self) -> None:
        coordinator = APICoordinator()
        health = coordinator.get_health()
        assert "overall_status" in health

    def test_get_quality(self) -> None:
        coordinator = APICoordinator()
        coordinator.process_request(domain="planner", operation="create_plan")
        quality = coordinator.get_quality()
        assert "overall_score" in quality

    def test_get_readiness(self) -> None:
        coordinator = APICoordinator()
        readiness = coordinator.get_readiness()
        assert "ready" in readiness

    def test_get_metrics(self) -> None:
        coordinator = APICoordinator()
        metrics = coordinator.get_metrics()
        assert "total_calls" in metrics


# =============================================================================
# APIManager Tests
# =============================================================================

class TestAPIManager:
    def setup_method(self) -> None:
        clear_registry()
        register_adapter("planner", PlannerAdapter())

    @pytest.fixture
    def manager(self) -> APIManager:
        return APIManager()

    def test_process_request(self, manager: APIManager) -> None:
        decision = manager.process_request("planner", "create_plan", {"name": "test"}, "POST")
        assert decision.success is True

    def test_create_session(self, manager: APIManager) -> None:
        session = manager.create_session(route="/test", method="GET")
        assert session.route == "/test"

    def test_get_health(self, manager: APIManager) -> None:
        health = manager.get_health()
        assert "overall_status" in health

    def test_get_quality(self, manager: APIManager) -> None:
        quality = manager.get_quality()
        assert "overall_score" in quality

    def test_get_readiness(self, manager: APIManager) -> None:
        readiness = manager.get_readiness()
        assert "ready" in readiness

    def test_get_metrics(self, manager: APIManager) -> None:
        metrics = manager.get_metrics()
        assert "total_calls" in metrics


# =============================================================================
# APIService Tests (ONLY public API)
# =============================================================================

class TestAPIService:
    def setup_method(self) -> None:
        clear_registry()
        register_adapter("planner", PlannerAdapter())

    @pytest.fixture
    def service(self) -> APIService:
        return APIService()

    def test_process_request_success(self, service: APIService) -> None:
        response = service.process_request("planner", "create_plan", {"name": "test"}, "POST")
        assert response.success is True
        assert response.data is not None
        assert response.errors is None

    def test_process_request_failure(self, service: APIService) -> None:
        response = service.process_request("nonexistent", "test")
        assert response.success is False
        assert response.errors is not None

    def test_create_session(self, service: APIService) -> None:
        session = service.create_session(route="/api/v1/test", method="GET")
        assert session.route == "/api/v1/test"

    def test_get_health(self, service: APIService) -> None:
        health = service.get_health()
        assert "overall_status" in health

    def test_get_quality(self, service: APIService) -> None:
        quality = service.get_quality()
        assert "overall_score" in quality

    def test_get_readiness(self, service: APIService) -> None:
        readiness = service.get_readiness()
        assert "ready" in readiness

    def test_get_metrics(self, service: APIService) -> None:
        metrics = service.get_metrics()
        assert "total_calls" in metrics

    def test_manager_property(self, service: APIService) -> None:
        assert service.manager is not None

    def test_coordinator_property(self, service: APIService) -> None:
        assert service.coordinator is not None

    def test_response_format(self, service: APIService) -> None:
        response = service.process_request("planner", "list_plans")
        assert hasattr(response, "success")
        assert hasattr(response, "data")
        assert hasattr(response, "metadata")
        assert hasattr(response, "errors")
        assert hasattr(response, "trace_id")
        assert hasattr(response, "timestamp")


# =============================================================================
# Full Pipeline Integration Test
# =============================================================================

class TestFullPipeline:
    """End-to-end pipeline test: APIService → APIManager → APICoordinator."""

    def setup_method(self) -> None:
        clear_registry()
        register_adapter("planner", PlannerAdapter())
        register_adapter("energy", __import__("adip.api.rest.adapters.energy", fromlist=["EnergyAdapter"]).EnergyAdapter())

    def test_full_pipeline_success(self) -> None:
        service = APIService()
        response = service.process_request("planner", "create_plan", {"name": "test"}, "POST")
        assert response.success is True
        assert response.metadata.trace_id is not None
        assert response.metadata.processing_time_ms is not None

    def test_full_pipeline_with_session(self) -> None:
        service = APIService()
        session = service.create_session(route="/api/v1/planner/plans", method="POST")
        assert session is not None
        response = service.process_request("planner", "create_plan", {"name": "test"}, "POST")
        assert response.success is True

    def test_full_pipeline_error_handling(self) -> None:
        service = APIService()
        response = service.process_request("nonexistent_domain", "operation")
        assert response.success is False
        assert response.errors is not None
        assert len(response.errors) > 0

    def test_multiple_requests(self) -> None:
        service = APIService()
        for i in range(5):
            response = service.process_request("planner", "create_plan", {"index": i})
            assert response.success is True

        metrics = service.get_metrics()
        assert metrics["total_calls"] >= 5

    def test_health_after_requests(self) -> None:
        service = APIService()
        service.process_request("planner", "create_plan")
        health = service.get_health()
        assert health["component_count"] >= 0

    def test_readiness_after_requests(self) -> None:
        service = APIService()
        service.process_request("planner", "create_plan")
        readiness = service.get_readiness()
        assert "ready" in readiness
