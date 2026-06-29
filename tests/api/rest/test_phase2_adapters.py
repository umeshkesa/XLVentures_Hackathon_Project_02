"""Tests for REST API Phase 2 — Service Adapters, Composition, Validation, etc."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from adip.api.rest.adapters import (
    ActionEngineAdapter,
    ActionManagerAdapter,
    DecisionReviewAdapter,
    EnergyAdapter,
    EvidenceAdapter,
    ExplainabilityAdapter,
    KnowledgeAdapter,
    MemoryAdapter,
    PlannerAdapter,
    PluginsAdapter,
    ReasoningAdapter,
    RecommendationAdapter,
    RegistryAdapter,
    RulesAdapter,
    WorkflowAdapter,
)
from adip.api.rest.adapters.router_registry import (
    clear_registry,
    get_adapter,
    get_all_adapters,
    get_registered_domains,
    register_adapter,
)
from adip.api.rest.composition import (
    AIOverviewComposition,
    DashboardComposition,
    EnergyOverviewComposition,
    OperationsOverviewComposition,
    WorkflowOverviewComposition,
)
from adip.api.rest.composition.cache import DashboardCache, SummaryCache
from adip.api.rest.contract_validator import APIContractValidator
from adip.api.rest.exception_mapper import ExceptionMapper
from adip.api.rest.metrics import APIMetricsCollector
from adip.api.rest.operation_tracker import OperationTracker
from adip.api.rest.profile_manager import APIProfileManager, ProfileType
from adip.api.rest.transformer import ResponseTransformer
from adip.api.rest.validation.pipeline import (
    ApiVersionValidator,
    BodyValidator,
    HeaderValidator,
    PathParamValidator,
    QueryParamValidator,
    ValidationContext,
    create_default_pipeline,
)

# =============================================================================
# Service Adapter Tests
# =============================================================================

class TestBaseServiceAdapter:
    def test_handle_operation(self) -> None:
        adapter = PlannerAdapter()
        result = adapter.handle_operation("create_plan", {"param": "value"})
        assert result.success is True
        assert result.data["domain"] == "planner"
        assert result.data["operation"] == "create_plan"
        assert result.data["params"] == {"param": "value"}

    def test_error_response(self) -> None:
        adapter = PlannerAdapter()
        result = adapter._error_response(code="test_error", message="test message")
        assert result.success is False
        assert result.errors is not None
        assert result.errors[0].code == "test_error"


class TestPlannerAdapter:
    @pytest.fixture
    def adapter(self) -> PlannerAdapter:
        return PlannerAdapter()

    def test_get_domain(self, adapter: PlannerAdapter) -> None:
        assert adapter.get_domain() == "planner"

    def test_create_plan(self, adapter: PlannerAdapter) -> None:
        result = adapter.create_plan({"name": "test"})
        assert result.success is True
        assert result.data["plan_id"] == "plan-001"

    def test_get_plan(self, adapter: PlannerAdapter) -> None:
        result = adapter.get_plan("plan-001")
        assert result.success is True
        assert result.data["plan_id"] == "plan-001"

    def test_list_plans(self, adapter: PlannerAdapter) -> None:
        result = adapter.list_plans()
        assert result.success is True
        assert "plans" in result.data

    def test_update_plan(self, adapter: PlannerAdapter) -> None:
        result = adapter.update_plan("plan-001", {"name": "updated"})
        assert result.data["status"] == "updated"

    def test_delete_plan(self, adapter: PlannerAdapter) -> None:
        result = adapter.delete_plan("plan-001")
        assert result.data["status"] == "deleted"


class TestWorkflowAdapter:
    @pytest.fixture
    def adapter(self) -> WorkflowAdapter:
        return WorkflowAdapter()

    def test_get_domain(self, adapter: WorkflowAdapter) -> None:
        assert adapter.get_domain() == "workflow"

    def test_create_workflow(self, adapter: WorkflowAdapter) -> None:
        result = adapter.create_workflow({"name": "test"})
        assert result.data["workflow_id"] == "wf-001"

    def test_execute_workflow(self, adapter: WorkflowAdapter) -> None:
        result = adapter.execute_workflow("wf-001")
        assert result.data["execution_id"] == "exec-001"


class TestMemoryAdapter:
    @pytest.fixture
    def adapter(self) -> MemoryAdapter:
        return MemoryAdapter()

    def test_store_and_retrieve(self, adapter: MemoryAdapter) -> None:
        store_result = adapter.store("key1", {"value": "data"})
        assert store_result.data["status"] == "stored"
        retrieve_result = adapter.retrieve("key1")
        assert retrieve_result.success is True


class TestKnowledgeAdapter:
    @pytest.fixture
    def adapter(self) -> KnowledgeAdapter:
        return KnowledgeAdapter()

    def test_ingest_and_query(self, adapter: KnowledgeAdapter) -> None:
        ingest = adapter.ingest({"title": "doc1"})
        assert ingest.data["document_id"] == "doc-001"
        query = adapter.query("test query")
        assert query.data["total"] == 0


class TestRulesAdapter:
    @pytest.fixture
    def adapter(self) -> RulesAdapter:
        return RulesAdapter()

    def test_evaluate(self, adapter: RulesAdapter) -> None:
        result = adapter.evaluate("rule-001", {"value": 100})
        assert result.data["result"] == "allowed"

    def test_create_and_get(self, adapter: RulesAdapter) -> None:
        created = adapter.create_rule({"name": "test rule"})
        assert created.data["status"] == "created"
        got = adapter.get_rule(created.data["rule_id"])
        assert got.success is True


class TestPluginsAdapter:
    @pytest.fixture
    def adapter(self) -> PluginsAdapter:
        return PluginsAdapter()

    def test_install_and_uninstall(self, adapter: PluginsAdapter) -> None:
        install = adapter.install("plugin-001")
        assert install.data["status"] == "installed"
        uninstall = adapter.uninstall("plugin-001")
        assert uninstall.data["status"] == "uninstalled"


class TestRegistryAdapter:
    @pytest.fixture
    def adapter(self) -> RegistryAdapter:
        return RegistryAdapter()

    def test_register_and_search(self, adapter: RegistryAdapter) -> None:
        reg = adapter.register({"name": "service-a"})
        assert reg.data["status"] == "registered"
        search = adapter.search("service")
        assert search.success is True


class TestEvidenceAdapter:
    @pytest.fixture
    def adapter(self) -> EvidenceAdapter:
        return EvidenceAdapter()

    def test_collect_and_fuse(self, adapter: EvidenceAdapter) -> None:
        collected = adapter.collect("sensor-01")
        assert collected.data["evidence_id"] == "ev-001"
        fused = adapter.fuse(["ev-001", "ev-002"])
        assert fused.data["status"] == "fused"


class TestReasoningAdapter:
    @pytest.fixture
    def adapter(self) -> ReasoningAdapter:
        return ReasoningAdapter()

    def test_reason(self, adapter: ReasoningAdapter) -> None:
        result = adapter.reason("analyze trend", {"data": [1, 2, 3]})
        assert result.data["conclusion"] == "deterministic_result"


class TestRecommendationAdapter:
    @pytest.fixture
    def adapter(self) -> RecommendationAdapter:
        return RecommendationAdapter()

    def test_recommend(self, adapter: RecommendationAdapter) -> None:
        result = adapter.recommend("optimize", {"goal": "efficiency"})
        assert result.data["recommendation_id"] == "rec-001"


class TestExplainabilityAdapter:
    @pytest.fixture
    def adapter(self) -> ExplainabilityAdapter:
        return ExplainabilityAdapter()

    def test_explain(self, adapter: ExplainabilityAdapter) -> None:
        result = adapter.explain("decision-001")
        assert result.data["explanation_id"] == "exp-001"


class TestDecisionReviewAdapter:
    @pytest.fixture
    def adapter(self) -> DecisionReviewAdapter:
        return DecisionReviewAdapter()

    def test_create_and_approve(self, adapter: DecisionReviewAdapter) -> None:
        created = adapter.create_review("decision-001")
        assert created.data["status"] == "pending"
        approved = adapter.approve(created.data["review_id"])
        assert approved.data["status"] == "approved"

    def test_reject(self, adapter: DecisionReviewAdapter) -> None:
        rejected = adapter.reject("rev-001", "Insufficient evidence")
        assert rejected.data["status"] == "rejected"


class TestActionManagerAdapter:
    @pytest.fixture
    def adapter(self) -> ActionManagerAdapter:
        return ActionManagerAdapter()

    def test_create_and_cancel(self, adapter: ActionManagerAdapter) -> None:
        created = adapter.create_action("notification")
        assert created.data["status"] == "planned"
        cancelled = adapter.cancel_action(created.data["action_id"])
        assert cancelled.data["status"] == "cancelled"


class TestActionEngineAdapter:
    @pytest.fixture
    def adapter(self) -> ActionEngineAdapter:
        return ActionEngineAdapter()

    def test_execute(self, adapter: ActionEngineAdapter) -> None:
        result = adapter.execute("act-001")
        assert result.data["status"] == "executed"


class TestEnergyAdapter:
    @pytest.fixture
    def adapter(self) -> EnergyAdapter:
        return EnergyAdapter()

    def test_get_asset(self, adapter: EnergyAdapter) -> None:
        result = adapter.get_asset("asset-001")
        assert result.data["type"] == "solar_panel"

    def test_analyze(self, adapter: EnergyAdapter) -> None:
        result = adapter.analyze("asset-001", {"metric": "efficiency"})
        assert result.data["analysis"]["health_score"] == 0.95


# =============================================================================
# Router Registry Tests
# =============================================================================

class TestRouterRegistry:
    def teardown_method(self) -> None:
        clear_registry()

    def test_register_and_get_adapter(self) -> None:
        adapter = MemoryAdapter()
        register_adapter("memory", adapter)
        assert get_adapter("memory") is adapter
        assert "memory" in get_registered_domains()

    def test_get_all_adapters(self) -> None:
        register_adapter("planner", PlannerAdapter())
        register_adapter("energy", EnergyAdapter())
        all_adapters = get_all_adapters()
        assert "planner" in all_adapters
        assert "energy" in all_adapters

    def test_clear_registry(self) -> None:
        register_adapter("test", PlannerAdapter())
        clear_registry()
        assert get_adapter("test") is None

    def test_get_nonexistent_adapter(self) -> None:
        assert get_adapter("nonexistent") is None


# =============================================================================
# Validation Pipeline Tests
# =============================================================================

class TestValidationPipeline:
    @pytest.mark.asyncio
    async def test_default_pipeline_creation(self) -> None:
        pipeline = create_default_pipeline()
        assert len(pipeline._validators) == 5

    @pytest.mark.asyncio
    async def test_header_validator_missing(self) -> None:
        from unittest.mock import MagicMock

        request = MagicMock()
        request.headers = {}
        request.url = MagicMock()
        request.url.path = "/api/v1/test"
        request.path_params = {}
        request.query_params = {}
        context = ValidationContext(request)
        validator = HeaderValidator()
        await validator.validate(context)
        assert not context.is_valid()

    @pytest.mark.asyncio
    async def test_path_param_validator_empty(self) -> None:
        from unittest.mock import MagicMock

        request = MagicMock()
        request.headers = {"content-type": "application/json", "accept": "application/json"}
        request.path_params = {"id": ""}
        request.url = MagicMock()
        request.url.path = "/api/v1/test"
        request.query_params = {}
        context = ValidationContext(request)
        validator = PathParamValidator()
        await validator.validate(context)
        assert not context.is_valid()

    @pytest.mark.asyncio
    async def test_query_param_validator_too_long(self) -> None:
        from unittest.mock import MagicMock

        request = MagicMock()
        request.headers = {"content-type": "application/json", "accept": "application/json"}
        request.path_params = {}
        request.query_params = {"q": "x" * 2000}
        request.url = MagicMock()
        request.url.path = "/api/v1/test"
        context = ValidationContext(request)
        validator = QueryParamValidator()
        await validator.validate(context)
        assert not context.is_valid()

    @pytest.mark.asyncio
    async def test_body_validator(self) -> None:
        from unittest.mock import MagicMock

        request = MagicMock()
        request.headers = {"content-type": "application/json", "accept": "application/json"}
        request.path_params = {}
        request.query_params = {}
        request.url = MagicMock()
        request.url.path = "/api/v1/test"
        request.method = "POST"
        context = ValidationContext(request, body=None)
        validator = BodyValidator()
        await validator.validate(context)
        assert not context.is_valid()

    @pytest.mark.asyncio
    async def test_api_version_validator(self) -> None:
        from unittest.mock import MagicMock

        request = MagicMock()
        request.headers = {"content-type": "application/json", "accept": "application/json"}
        request.path_params = {}
        request.query_params = {}
        request.url = MagicMock()
        request.url.path = "/api/v3/test"
        context = ValidationContext(request)
        validator = ApiVersionValidator()
        await validator.validate(context)
        assert not context.is_valid()

    @pytest.mark.asyncio
    async def test_valid_request_passes(self) -> None:
        from unittest.mock import MagicMock

        request = MagicMock()
        request.headers = {"content-type": "application/json", "accept": "application/json"}
        request.path_params = {"id": "valid"}
        request.query_params = {"q": "short"}
        request.url = MagicMock()
        request.url.path = "/api/v1/test"
        request.method = "GET"
        context = ValidationContext(request, body={"key": "value"})
        pipeline = create_default_pipeline()
        result = await pipeline.validate(context)
        assert result.is_valid()


# =============================================================================
# Response Transformer Tests
# =============================================================================

class TestResponseTransformer:
    @pytest.fixture
    def transformer(self) -> ResponseTransformer:
        return ResponseTransformer(api_version="v1")

    def test_success_response(self, transformer: ResponseTransformer) -> None:
        response = transformer.success({"key": "value"})
        assert response.success is True
        assert response.data == {"key": "value"}
        assert response.trace_id is not None
        assert response.errors is None

    def test_error_response(self, transformer: ResponseTransformer) -> None:
        response = transformer.error(message="Test error")
        assert response.success is False
        assert response.errors is not None
        assert response.errors[0].message == "Test error"

    def test_from_service_response_dict(self, transformer: ResponseTransformer) -> None:
        result = transformer.from_service_response({"data": {"id": 1}})
        assert result.success is True
        assert result.data == {"id": 1}

    def test_from_service_response_apiresponse(self, transformer: ResponseTransformer) -> None:
        original = transformer.success("test")
        result = transformer.from_service_response(original)
        assert result is original

    def test_paginated_response(self, transformer: ResponseTransformer) -> None:
        response = transformer.paginated(items=["a", "b"], total=2, limit=10, offset=0)
        assert response.success is True
        assert response.data["pagination"]["total"] == 2
        assert len(response.data["items"]) == 2


# =============================================================================
# Exception Mapper Tests
# =============================================================================

class TestExceptionMapper:
    @pytest.fixture
    def mapper(self) -> ExceptionMapper:
        return ExceptionMapper()

    def test_map_validation_exception(self, mapper: ExceptionMapper) -> None:
        class ValidationErr(Exception):
            pass

        status, response = mapper.map(ValidationErr("invalid"))
        assert status == 400
        assert response.errors[0].code == "validation_error"

    def test_map_authentication_exception(self, mapper: ExceptionMapper) -> None:
        class AuthErr(Exception):
            pass

        status, response = mapper.map(AuthErr("unauthorized"))
        assert status == 401

    def test_map_authorization_exception(self, mapper: ExceptionMapper) -> None:
        class AuthzErr(Exception):
            pass

        status, response = mapper.map(AuthzErr("forbidden"))
        assert status == 403

    def test_map_not_found_exception(self, mapper: ExceptionMapper) -> None:
        class NotFoundErr(Exception):
            pass

        status, response = mapper.map(NotFoundErr("not found"))
        assert status == 404

    def test_map_conflict_exception(self, mapper: ExceptionMapper) -> None:
        class ConflictErr(Exception):
            pass

        status, response = mapper.map(ConflictErr("conflict"))
        assert status == 409

    def test_map_integration_exception(self, mapper: ExceptionMapper) -> None:
        class IntegrationErr(Exception):
            pass

        status, response = mapper.map(IntegrationErr("integration failed"))
        assert status == 502

    def test_map_unknown_exception(self, mapper: ExceptionMapper) -> None:
        status, response = mapper.map(Exception("something broke"))
        assert status == 500
        assert response.errors[0].code == "platform_error"

    def test_map_value_error(self, mapper: ExceptionMapper) -> None:
        status, response = mapper.map(ValueError("bad value"))
        assert status == 500
        assert response.errors[0].code == "platform_error"


# =============================================================================
# Composition Service Tests
# =============================================================================

class TestDashboardComposition:
    @pytest.fixture
    def comp(self) -> DashboardComposition:
        return DashboardComposition()

    def test_get_name(self, comp: DashboardComposition) -> None:
        assert comp.get_name() == "dashboard"

    def test_get_overview(self, comp: DashboardComposition) -> None:
        overview = comp.get_overview()
        assert "system_health" in overview
        assert "active_workflows" in overview


class TestAIOverviewComposition:
    @pytest.fixture
    def comp(self) -> AIOverviewComposition:
        return AIOverviewComposition()

    def test_get_name(self, comp: AIOverviewComposition) -> None:
        assert comp.get_name() == "ai_overview"

    def test_get_overview(self, comp: AIOverviewComposition) -> None:
        overview = comp.get_overview()
        assert "active_reasoning_sessions" in overview


class TestEnergyOverviewComposition:
    @pytest.fixture
    def comp(self) -> EnergyOverviewComposition:
        return EnergyOverviewComposition()

    def test_get_overview(self, comp: EnergyOverviewComposition) -> None:
        overview = comp.get_overview()
        assert "total_assets" in overview


class TestWorkflowOverviewComposition:
    @pytest.fixture
    def comp(self) -> WorkflowOverviewComposition:
        return WorkflowOverviewComposition()

    def test_get_overview(self, comp: WorkflowOverviewComposition) -> None:
        overview = comp.get_overview()
        assert "active_workflows" in overview


class TestOperationsOverviewComposition:
    @pytest.fixture
    def comp(self) -> OperationsOverviewComposition:
        return OperationsOverviewComposition()

    def test_get_overview(self, comp: OperationsOverviewComposition) -> None:
        overview = comp.get_overview()
        assert "pending_actions" in overview


# =============================================================================
# Composition Cache Tests
# =============================================================================

class TestDashboardCache:
    @pytest.mark.asyncio
    async def test_get_returns_none(self) -> None:
        cache = DashboardCache()
        result = await cache.get("test-key")
        assert result is None

    @pytest.mark.asyncio
    async def test_set_and_delete(self) -> None:
        cache = DashboardCache()
        await cache.set("key", "value")
        await cache.delete("key")

    @pytest.mark.asyncio
    async def test_exists_returns_false(self) -> None:
        cache = DashboardCache()
        assert await cache.exists("any-key") is False


class TestSummaryCache:
    @pytest.mark.asyncio
    async def test_get_returns_none(self) -> None:
        cache = SummaryCache()
        assert await cache.get("key") is None

    @pytest.mark.asyncio
    async def test_set(self) -> None:
        cache = SummaryCache()
        await cache.set("key", "value", ttl_seconds=60)


# =============================================================================
# Operation Tracker Tests
# =============================================================================

class TestOperationTracker:
    @pytest.fixture
    def tracker(self) -> OperationTracker:
        return OperationTracker()

    def test_create_operation(self, tracker: OperationTracker) -> None:
        op = tracker.create_operation("data_export", {"file": "data.csv"})
        assert op.operation_type == "data_export"
        assert op.status.value == "pending"

    def test_operation_lifecycle(self, tracker: OperationTracker) -> None:
        op = tracker.create_operation("process")
        op_id = str(op.operation_id)

        assert tracker.start_operation(op_id) is True
        assert tracker.get_operation(op_id).status.value == "running"

        assert tracker.complete_operation(op_id, {"result": "ok"}) is True
        assert tracker.get_operation(op_id).status.value == "completed"

    def test_operation_fail(self, tracker: OperationTracker) -> None:
        op = tracker.create_operation("fail")
        op_id = str(op.operation_id)
        tracker.start_operation(op_id)
        tracker.fail_operation(op_id, "Something went wrong")
        assert tracker.get_operation(op_id).status.value == "failed"

    def test_cancel_operation(self, tracker: OperationTracker) -> None:
        op = tracker.create_operation("cancel")
        op_id = str(op.operation_id)
        assert tracker.cancel_operation(op_id) is True
        assert tracker.get_operation(op_id).status.value == "cancelled"

    def test_count_by_status(self, tracker: OperationTracker) -> None:
        op1 = tracker.create_operation("a")
        op2 = tracker.create_operation("b")
        tracker.start_operation(str(op1.operation_id))
        tracker.complete_operation(str(op1.operation_id))
        counts = tracker.count_by_status()
        assert counts.get("completed") == 1
        assert counts.get("pending") == 1

    def test_list_operations(self, tracker: OperationTracker) -> None:
        tracker.create_operation("a")
        tracker.create_operation("b")
        assert len(tracker.list_operations()) == 2

    def test_clear(self, tracker: OperationTracker) -> None:
        tracker.create_operation("a")
        tracker.clear()
        assert len(tracker.list_operations()) == 0


# =============================================================================
# API Profile Manager Tests
# =============================================================================

class TestAPIProfileManager:
    @pytest.fixture
    def manager(self) -> APIProfileManager:
        return APIProfileManager()

    def test_default_profile(self, manager: APIProfileManager) -> None:
        profile = manager.get_profile()
        assert profile["include_metadata"] is True

    def test_summary_profile(self, manager: APIProfileManager) -> None:
        profile = manager.get_profile("summary")
        assert profile["include_metadata"] is False

    def test_debug_profile(self, manager: APIProfileManager) -> None:
        profile = manager.get_profile("debug")
        assert profile["include_debug"] is True

    def test_audit_profile(self, manager: APIProfileManager) -> None:
        profile = manager.get_profile("audit")
        assert profile["include_audit"] is True

    def test_fallback_to_default(self, manager: APIProfileManager) -> None:
        profile = manager.get_profile("nonexistent")
        assert profile["include_metadata"] is True

    def test_list_profiles(self, manager: APIProfileManager) -> None:
        profiles = manager.list_profiles()
        assert "summary" in profiles
        assert "detailed" in profiles
        assert "audit" in profiles
        assert "debug" in profiles

    def test_set_default_profile(self, manager: APIProfileManager) -> None:
        manager.set_default_profile(ProfileType.SUMMARY)
        assert manager._default_profile == ProfileType.SUMMARY


# =============================================================================
# Metrics Tests
# =============================================================================

class TestAPIMetricsCollector:
    @pytest.fixture
    def metrics(self) -> APIMetricsCollector:
        return APIMetricsCollector()

    def test_record_call(self, metrics: APIMetricsCollector) -> None:
        metrics.record_call("/api/v1/test", "GET", 200, 45.2)
        assert metrics.get_total_calls("GET:/api/v1/test") == 1
        assert metrics.get_total_calls() == 1

    def test_record_error(self, metrics: APIMetricsCollector) -> None:
        metrics.record_call("/api/v1/error", "GET", 500, 30.0)
        assert metrics.get_total_errors("GET:/api/v1/error") == 1

    def test_success_rate(self, metrics: APIMetricsCollector) -> None:
        metrics.record_call("/ok", "GET", 200, 10)
        metrics.record_call("/ok", "GET", 200, 10)
        metrics.record_call("/err", "GET", 500, 10)
        assert metrics.get_success_rate() == 2 / 3

    def test_average_latency(self, metrics: APIMetricsCollector) -> None:
        metrics.record_call("/test", "GET", 200, 10)
        metrics.record_call("/test", "GET", 200, 20)
        metrics.record_call("/test", "GET", 200, 30)
        assert metrics.get_average_latency("GET:/test") == 20.0

    def test_latency_percentile(self, metrics: APIMetricsCollector) -> None:
        for i in range(1, 101):
            metrics.record_call("/test", "GET", 200, float(i))
        p50 = metrics.get_latency_percentile(0.5, "GET:/test")
        assert 49 <= p50 <= 51

    def test_metrics_snapshot(self, metrics: APIMetricsCollector) -> None:
        metrics.record_call("/ok", "GET", 200, 10)
        metrics.record_call("/err", "GET", 500, 20)
        snapshot = metrics.get_metrics_snapshot()
        assert snapshot["total_calls"] == 2
        assert snapshot["total_errors"] == 1
        assert snapshot["routes_monitored"] == 2

    def test_reset(self, metrics: APIMetricsCollector) -> None:
        metrics.record_call("/test", "GET", 200, 10)
        metrics.reset()
        assert metrics.get_total_calls() == 0


# =============================================================================
# Contract Validator Tests
# =============================================================================

class TestAPIContractValidator:
    @pytest.fixture
    def validator(self) -> APIContractValidator:
        return APIContractValidator()

    def test_validate_api_version_v1(self, validator: APIContractValidator) -> None:
        result = validator.validate_api_version("v1")
        assert result.is_valid is True

    def test_validate_api_version_invalid(self, validator: APIContractValidator) -> None:
        result = validator.validate_api_version("v3")
        assert result.is_valid is False

    def test_validate_request_model_valid(self, validator: APIContractValidator) -> None:
        from pydantic import BaseModel

        class TestModel(BaseModel):
            name: str

        result = validator.validate_request_model(TestModel, {"name": "test"})
        assert result.is_valid is True

    def test_validate_request_model_invalid(self, validator: APIContractValidator) -> None:
        from pydantic import BaseModel

        class TestModel(BaseModel):
            name: str

        result = validator.validate_request_model(TestModel, {})
        assert result.is_valid is False
        assert len(result.errors) > 0


# =============================================================================
# Router Endpoint Tests (Phase 2)
# =============================================================================

class TestRouterEndpoints:
    """Test that Phase 1 router endpoints return 200 with adapter responses."""

    def test_create_plan_endpoint(self, client: TestClient) -> None:
        response = client.post("/api/v1/planner/plans", json={"name": "test"})
        assert response.status_code == 200

    def test_get_plan_endpoint(self, client: TestClient) -> None:
        response = client.get("/api/v1/planner/plans/plan-001")
        assert response.status_code == 200

    def test_health_endpoint(self, client: TestClient) -> None:
        response = client.get("/api/v1/health")
        assert response.status_code == 200

    def test_energy_assets_endpoint(self, client: TestClient) -> None:
        response = client.get("/api/v1/energy/assets")
        assert response.status_code == 200

    def test_rules_evaluate_endpoint(self, client: TestClient) -> None:
        response = client.post("/api/v1/rules/evaluate/rule-001", json={"value": 100})
        assert response.status_code == 200

    def test_reasoning_reason_endpoint(self, client: TestClient) -> None:
        response = client.post("/api/v1/reasoning/reason", json={"query": "analyze"})
        assert response.status_code == 200

    def test_recommendation_recommend_endpoint(self, client: TestClient) -> None:
        response = client.post("/api/v1/recommendation/recommend", json={"query": "optimize"})
        assert response.status_code == 200

    def test_explainability_explain_endpoint(self, client: TestClient) -> None:
        response = client.post("/api/v1/explainability/explain", json={"decision_id": "d-001"})
        assert response.status_code == 200

    def test_action_execute_endpoint(self, client: TestClient) -> None:
        response = client.post("/api/v1/action-engine/execute", json={"action_id": "a-001"})
        assert response.status_code == 200

    def test_action_manager_create_endpoint(self, client: TestClient) -> None:
        response = client.post("/api/v1/action-manager/actions", json={"action_type": "alert"})
        assert response.status_code == 200
