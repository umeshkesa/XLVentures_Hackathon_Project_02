"""Tests for REST API Layer Phase 3.5 — Enterprise Refinement & Interface Freeze.

Covers:
  - APIQualityManager enhancements
  - APIComplianceManager
  - APIDiagnostics
  - APIPerformanceProfile
  - APIExportPackage
  - APIPipelineVersion
  - RequestReplayPackage
  - EndpointHealth
  - APIGovernance
  - APIManifest
  - DocumentationMetadata
  - ApiDecision enhancements
  - Enhanced trace & metrics
  - Backward compatibility
"""

from __future__ import annotations

import pytest

from adip.api.rest.enums import (
    ComplianceStatus,
    HealthStatus,
    ReadinessStatus,
)
from adip.api.rest.metrics import APIMetricsCollector
from adip.api.rest.orchestration.compliance_manager import APIComplianceManager
from adip.api.rest.orchestration.diagnostics import APIDiagnostics
from adip.api.rest.orchestration.documentation_metadata import DocumentationMetadata
from adip.api.rest.orchestration.endpoint_health import EndpointHealth
from adip.api.rest.orchestration.export_package import APIExportPackage
from adip.api.rest.orchestration.governance import APIGovernance
from adip.api.rest.orchestration.manifest import APIManifest
from adip.api.rest.orchestration.models import ApiDecision, ApiSession
from adip.api.rest.orchestration.performance_profile import APIPerformanceProfile
from adip.api.rest.orchestration.pipeline_version import APIPipelineVersion
from adip.api.rest.orchestration.quality import APIQualityManager
from adip.api.rest.orchestration.readiness import APIReadiness
from adip.api.rest.orchestration.replay_package import RequestReplayStore
from adip.api.rest.orchestration.snapshot import APISnapshot, Snapshot
from adip.api.rest.trace import APITraceManager

# ========================================================================
# ApiDecision enhancements
# ========================================================================

class TestApiDecisionPhase35:
    def test_decision_has_new_fields(self) -> None:
        d = ApiDecision()
        assert hasattr(d, "http_status")
        assert hasattr(d, "quality_score")
        assert hasattr(d, "compliance_status")
        assert hasattr(d, "diagnostics")
        assert hasattr(d, "performance_profile")
        assert hasattr(d, "endpoint_health")
        assert hasattr(d, "governance_result")
        assert hasattr(d, "replay_package")
        assert hasattr(d, "export_package")
        assert hasattr(d, "pipeline_version")
        assert hasattr(d, "manifest")
        assert hasattr(d, "documentation_metadata")
        assert hasattr(d, "readiness_status")
        assert hasattr(d, "timestamp")

    def test_decision_default_values(self) -> None:
        d = ApiDecision()
        assert d.http_status == 200
        assert d.quality_score == 1.0
        assert d.compliance_status == ComplianceStatus.PENDING
        assert d.diagnostics == {}
        assert d.performance_profile == {}
        assert d.endpoint_health == HealthStatus.HEALTHY
        assert d.governance_result == {}
        assert d.replay_package == {}
        assert d.export_package == {}
        assert d.pipeline_version is None
        assert d.manifest == {}
        assert d.documentation_metadata == {}
        assert d.readiness_status == ReadinessStatus.NOT_READY

    def test_decision_custom_values(self) -> None:
        d = ApiDecision(
            http_status=201,
            quality_score=0.85,
            compliance_status=ComplianceStatus.COMPLIANT,
            endpoint_health=HealthStatus.DEGRADED,
            readiness_status=ReadinessStatus.READY,
            pipeline_version="v1.2.3",
            diagnostics={"router_failures": 1},
        )
        assert d.http_status == 201
        assert d.quality_score == 0.85
        assert d.compliance_status == ComplianceStatus.COMPLIANT
        assert d.endpoint_health == HealthStatus.DEGRADED
        assert d.readiness_status == ReadinessStatus.READY
        assert d.pipeline_version == "v1.2.3"
        assert d.diagnostics == {"router_failures": 1}

    def test_decision_backward_compatible(self) -> None:
        d = ApiDecision(success=True, status_code=200, response={"data": "ok"})
        assert d.success is True
        assert d.status_code == 200
        assert d.response == {"data": "ok"}
        assert d.validation_passed is True

    def test_decision_http_status_aliases_status_code(self) -> None:
        d = ApiDecision(status_code=404, http_status=404)
        assert d.http_status == 404
        assert d.status_code == 404


# ========================================================================
# APIQualityManager enhancements
# ========================================================================

class TestAPIQualityManagerPhase35:
    def test_evaluate_request_completeness(self) -> None:
        qm = APIQualityManager()
        qs = qm.evaluate_request_completeness(has_body=True, has_headers=True, has_query=True)
        assert qs.score == 1.0
        assert qs.dimension == "request_completeness"

    def test_evaluate_request_completeness_partial(self) -> None:
        qm = APIQualityManager()
        qs = qm.evaluate_request_completeness(has_body=True, has_headers=False, has_query=False)
        assert qs.score == pytest.approx(1 / 3)
        assert qs.dimension == "request_completeness"

    def test_evaluate_request_completeness_none(self) -> None:
        qm = APIQualityManager()
        qs = qm.evaluate_request_completeness(has_body=False, has_headers=False, has_query=False)
        assert qs.score == 0.0

    def test_evaluate_performance(self) -> None:
        qm = APIQualityManager()
        qs = qm.evaluate_performance(p95_latency_ms=100, error_rate=0.0)
        assert qs.score > 0.9
        assert qs.dimension == "performance"

    def test_evaluate_performance_high_latency(self) -> None:
        qm = APIQualityManager()
        qs = qm.evaluate_performance(p95_latency_ms=5000, error_rate=0.5)
        assert qs.score < 0.5
        assert qs.dimension == "performance"

    def test_quality_report_includes_new_dimensions(self) -> None:
        qm = APIQualityManager()
        qm.evaluate_request_completeness(True, True, True)
        qm.evaluate_performance(100, 0.0)
        report = qm.get_quality_report()
        assert "request_completeness" in report["dimensions"]
        assert "performance" in report["dimensions"]
        assert report["dimension_count"] >= 2

    def test_backward_compatible_dimensions(self) -> None:
        qm = APIQualityManager()
        qm.evaluate_validation_quality(True)
        qm.evaluate_response_completeness(True)
        qm.evaluate_processing_time(50)
        report = qm.get_quality_report()
        assert "validation" in report["dimensions"]
        assert "response_completeness" in report["dimensions"]
        assert "processing_time" in report["dimensions"]


# ========================================================================
# APIComplianceManager
# ========================================================================

class TestAPIComplianceManager:
    def test_validate_rest_standards_valid(self) -> None:
        cm = APIComplianceManager()
        result = cm.validate_rest_standards("GET", "/api/v1/plans", 200)
        assert result.is_compliant

    def test_validate_rest_standards_invalid_method(self) -> None:
        cm = APIComplianceManager()
        result = cm.validate_rest_standards("INVALID", "/test", 200)
        assert not result.is_compliant
        assert any("Invalid HTTP method" in e for e in result.errors)

    def test_validate_rest_standards_path_no_slash(self) -> None:
        cm = APIComplianceManager()
        result = cm.validate_rest_standards("GET", "api/plans", 200)
        assert not result.is_compliant
        assert any("Path must start with" in e for e in result.errors)

    def test_validate_naming_conventions_kebab(self) -> None:
        cm = APIComplianceManager()
        result = cm.validate_naming_conventions("/api/v1/energy/assets", ["asset_id", "asset_name"])
        assert result.is_compliant

    def test_validate_naming_conventions_bad_path(self) -> None:
        cm = APIComplianceManager()
        result = cm.validate_naming_conventions("/SomePath/NotKebab", ["BadField!"])
        assert not result.is_compliant

    def test_validate_http_semantics_get_ok(self) -> None:
        cm = APIComplianceManager()
        result = cm.validate_http_semantics("GET", 200)
        assert result.is_compliant

    def test_validate_http_semantics_get_404(self) -> None:
        cm = APIComplianceManager()
        result = cm.validate_http_semantics("GET", 404)
        assert result.is_compliant  # 404 is valid for GET

    def test_validate_http_semantics_post_404(self) -> None:
        cm = APIComplianceManager()
        result = cm.validate_http_semantics("POST", 404)
        assert not result.is_compliant

    def test_validate_version_rules_v1(self) -> None:
        cm = APIComplianceManager()
        result = cm.validate_version_rules("v1")
        assert result.is_compliant

    def test_validate_version_rules_invalid(self) -> None:
        cm = APIComplianceManager()
        result = cm.validate_version_rules("v99")
        assert not result.is_compliant

    def test_validate_openapi_compliance(self) -> None:
        cm = APIComplianceManager()
        result = cm.validate_openapi_compliance({"openapi": "3.1.0", "paths": {}})
        assert result.is_compliant

    def test_validate_openapi_compliance_missing(self) -> None:
        cm = APIComplianceManager()
        result = cm.validate_openapi_compliance(None)
        assert not result.is_compliant

    def test_compliance_report(self) -> None:
        cm = APIComplianceManager()
        cm.validate_rest_standards("GET", "/test", 200)
        cm.validate_naming_conventions("/test", [])
        report = cm.get_compliance_report()
        assert report["overall_compliant"]
        assert report["check_count"] >= 2

    def test_reset(self) -> None:
        cm = APIComplianceManager()
        cm.validate_rest_standards("BAD", "/test", 200)
        cm.reset()
        report = cm.get_compliance_report()
        assert report["check_count"] == 0


# ========================================================================
# APIDiagnostics
# ========================================================================

class TestAPIDiagnostics:
    def test_record_router_failure(self) -> None:
        d = APIDiagnostics()
        entry = d.record_router_failure("/test", "GET", "Route not found")
        assert entry.category == "router"

    def test_record_middleware_failure(self) -> None:
        d = APIDiagnostics()
        entry = d.record_middleware_failure("CorrelationMiddleware", "Timeout")
        assert entry.category == "middleware"

    def test_record_validation_error(self) -> None:
        d = APIDiagnostics()
        entry = d.record_validation_error("BodyValidator", "Missing field")
        assert entry.category == "validation"

    def test_record_adapter_failure(self) -> None:
        d = APIDiagnostics()
        entry = d.record_adapter_failure("PlannerAdapter", "create_plan", "Failed")
        assert entry.category == "adapter"

    def test_record_contract_violation(self) -> None:
        d = APIDiagnostics()
        entry = d.record_contract_violation("OpenAPI", "Missing path")
        assert entry.category == "contract"

    def test_get_diagnostics_summary(self) -> None:
        d = APIDiagnostics()
        d.record_router_failure("/a", "GET", "fail")
        d.record_adapter_failure("X", "op", "fail")
        result = d.get_diagnostics()
        assert result["total_entries"] == 2
        assert result["router_failures"] == 1
        assert result["adapter_failures"] == 1
        assert "by_category" in result

    def test_clear(self) -> None:
        d = APIDiagnostics()
        d.record_router_failure("/t", "GET", "err")
        d.clear()
        assert d.count() == 0

    def test_diagnostic_entry_has_id_and_timestamp(self) -> None:
        d = APIDiagnostics()
        entry = d.record_validation_error("V", "err")
        entry_dict = entry.to_dict()
        assert "diagnostic_id" in entry_dict
        assert "timestamp" in entry_dict
        assert entry_dict["category"] == "validation"


# ========================================================================
# APIPerformanceProfile
# ========================================================================

class TestAPIPerformanceProfile:
    def test_record_and_summary(self) -> None:
        pp = APIPerformanceProfile()
        pp.record("route:test", 100.0)
        pp.record("route:test", 200.0)
        pp.record("route:test", 300.0, is_error=True)
        summary = pp.get_summary()
        assert summary["total_routes"] == 1
        assert summary["total_requests"] == 3

    def test_error_rate(self) -> None:
        pp = APIPerformanceProfile()
        pp.record("r1", 100.0)
        pp.record("r1", 100.0, is_error=True)
        profile = pp.get_profile("r1")
        assert profile is not None
        assert profile.error_rate == 0.5

    def test_percentiles(self) -> None:
        pp = APIPerformanceProfile()
        for i in range(1, 101):
            pp.record("r1", float(i))
        profile = pp.get_profile("r1")
        assert profile is not None
        assert profile.get_percentile(0.5) == pytest.approx(50.5, rel=0.1)
        assert profile.get_percentile(0.95) == pytest.approx(95.5, rel=0.1)

    def test_throughput(self) -> None:
        pp = APIPerformanceProfile()
        pp.record("r1", 10.0)
        pp.record("r1", 20.0)
        profile = pp.get_profile("r1")
        assert profile is not None
        assert profile.throughput >= 0

    def test_get_all_profiles(self) -> None:
        pp = APIPerformanceProfile()
        pp.record("r1", 10.0)
        pp.record("r2", 20.0)
        profiles = pp.get_all_profiles()
        assert len(profiles) == 2

    def test_reset(self) -> None:
        pp = APIPerformanceProfile()
        pp.record("r1", 10.0)
        pp.reset()
        assert pp.get_summary()["total_routes"] == 0


# ========================================================================
# APIExportPackage
# ========================================================================

class TestAPIExportPackage:
    def test_create_package(self) -> None:
        ep = APIExportPackage()
        pkg = ep.create_package(
            openapi_metadata={"version": "3.1.0"},
            route_manifest=[{"method": "GET", "path": "/test"}],
        )
        assert pkg.openapi_metadata == {"version": "3.1.0"}
        assert pkg.route_manifest == [{"method": "GET", "path": "/test"}]

    def test_get_package(self) -> None:
        ep = APIExportPackage()
        pkg = ep.create_package()
        retrieved = ep.get_package(str(pkg.package_id))
        assert retrieved is not None

    def test_get_package_nonexistent(self) -> None:
        ep = APIExportPackage()
        assert ep.get_package("nonexistent") is None

    def test_list_packages(self) -> None:
        ep = APIExportPackage()
        ep.create_package()
        ep.create_package()
        assert len(ep.list_packages()) == 2

    def test_export_as_markdown(self) -> None:
        ep = APIExportPackage()
        pkg = ep.create_package(
            route_manifest=[{"method": "GET", "path": "/test", "description": "A test"}],
        )
        md = ep.export_as(str(pkg.package_id), fmt="markdown")
        assert "# API Export Package" in md
        assert "GET /test" in md

    def test_export_as_json(self) -> None:
        ep = APIExportPackage()
        pkg = ep.create_package()
        js = ep.export_as(str(pkg.package_id), fmt="json")
        assert '"package_id"' in js

    def test_count(self) -> None:
        ep = APIExportPackage()
        assert ep.count() == 0
        ep.create_package()
        assert ep.count() == 1

    def test_clear(self) -> None:
        ep = APIExportPackage()
        ep.create_package()
        ep.clear()
        assert ep.count() == 0


# ========================================================================
# APIPipelineVersion
# ========================================================================

class TestAPIPipelineVersion:
    def test_create_version(self) -> None:
        pv = APIPipelineVersion()
        record = pv.create_version("1.0.0", "Initial")
        assert record.version == "1.0.0"
        assert record.is_active is True

    def test_active_version(self) -> None:
        pv = APIPipelineVersion()
        pv.create_version("1.0.0")
        assert pv.get_active_version() == "1.0.0"

    def test_set_active_version(self) -> None:
        pv = APIPipelineVersion()
        pv.create_version("1.0.0")
        pv.create_version("2.0.0")
        pv.set_active_version("2.0.0")
        assert pv.get_active_version() == "2.0.0"
        v1 = pv.get_version("1.0.0")
        assert v1 is not None and v1.is_active is False
        v2 = pv.get_version("2.0.0")
        assert v2 is not None and v2.is_active is True

    def test_set_active_version_nonexistent(self) -> None:
        pv = APIPipelineVersion()
        pv.create_version("1.0.0")
        assert pv.set_active_version("nonexistent") is False

    def test_get_history(self) -> None:
        pv = APIPipelineVersion()
        pv.create_version("1.0.0")
        pv.create_version("2.0.0")
        history = pv.get_history()
        assert len(history) == 2

    def test_get_version(self) -> None:
        pv = APIPipelineVersion()
        pv.create_version("1.0.0")
        record = pv.get_version("1.0.0")
        assert record is not None
        assert record.version == "1.0.0"

    def test_clear(self) -> None:
        pv = APIPipelineVersion()
        pv.create_version("1.0.0")
        pv.clear()
        assert pv.count() == 0


# ========================================================================
# RequestReplayPackage
# ========================================================================

class TestRequestReplayStore:
    def test_create_package(self) -> None:
        rs = RequestReplayStore()
        pkg = rs.create_package(
            method="POST",
            path="/api/v1/plans",
            headers={"authorization": "Bearer secret", "x-custom": "value"},
            body={"name": "test"},
            timing_ms=50.0,
            status_code=201,
        )
        assert pkg.method == "POST"
        assert pkg.path == "/api/v1/plans"
        assert pkg.timing_ms == 50.0
        assert pkg.status_code == 201

    def test_sanitizes_auth_headers(self) -> None:
        rs = RequestReplayStore()
        pkg = rs.create_package(
            method="GET",
            path="/test",
            headers={"authorization": "Bearer secret", "x-api-key": "key123", "safe-header": "ok"},
        )
        assert "authorization" not in pkg.headers
        assert "x-api-key" not in pkg.headers
        assert pkg.headers.get("safe-header") == "ok"

    def test_get_package(self) -> None:
        rs = RequestReplayStore()
        pkg = rs.create_package(method="GET", path="/test")
        retrieved = rs.get_package(str(pkg.replay_id))
        assert retrieved is not None
        assert retrieved.path == "/test"

    def test_get_package_nonexistent(self) -> None:
        rs = RequestReplayStore()
        assert rs.get_package("nonexistent") is None

    def test_list_packages(self) -> None:
        rs = RequestReplayStore()
        rs.create_package(method="GET", path="/a")
        rs.create_package(method="POST", path="/b")
        assert len(rs.list_packages()) == 2

    def test_count(self) -> None:
        rs = RequestReplayStore()
        assert rs.count() == 0
        rs.create_package(method="GET", path="/t")
        assert rs.count() == 1

    def test_clear(self) -> None:
        rs = RequestReplayStore()
        rs.create_package(method="GET", path="/t")
        rs.clear()
        assert rs.count() == 0

    def test_to_dict_includes_all_fields(self) -> None:
        rs = RequestReplayStore()
        pkg = rs.create_package(method="PUT", path="/x", status_code=200, timing_ms=10)
        d = pkg.to_dict()
        assert d["method"] == "PUT"
        assert d["path"] == "/x"
        assert d["status_code"] == 200
        assert d["timing_ms"] == 10
        assert "replay_id" in d
        assert "created_at" in d


# ========================================================================
# EndpointHealth
# ========================================================================

class TestEndpointHealth:
    def test_register(self) -> None:
        eh = EndpointHealth()
        entry = eh.register("planner", EndpointHealth.TYPE_ADAPTER)
        assert entry.name == "planner"
        assert entry.component_type == "adapter"

    def test_report_success(self) -> None:
        eh = EndpointHealth()
        eh.report_success("planner", EndpointHealth.TYPE_ADAPTER)
        entries = eh.get_health(EndpointHealth.TYPE_ADAPTER)
        assert len(entries) == 1
        assert entries[0]["status"] == "healthy"

    def test_report_failure_degraded(self) -> None:
        eh = EndpointHealth()
        eh.report_failure("planner", EndpointHealth.TYPE_ADAPTER, {"err": "first"})
        eh.report_failure("planner", EndpointHealth.TYPE_ADAPTER, {"err": "second"})
        entries = eh.get_health(EndpointHealth.TYPE_ADAPTER)
        assert entries[0]["status"] == "degraded"

    def test_report_failure_unhealthy(self) -> None:
        eh = EndpointHealth()
        for _ in range(5):
            eh.report_failure("bad", EndpointHealth.TYPE_ADAPTER)
        entries = eh.get_health(EndpointHealth.TYPE_ADAPTER)
        bad = [e for e in entries if e["name"] == "bad"]
        assert bad[0]["status"] == "unhealthy"

    def test_get_health_by_type(self) -> None:
        eh = EndpointHealth()
        eh.register("r1", EndpointHealth.TYPE_ROUTER)
        eh.register("a1", EndpointHealth.TYPE_ADAPTER)
        routers = eh.get_health(EndpointHealth.TYPE_ROUTER)
        assert len(routers) == 1
        assert routers[0]["component_type"] == "router"

    def test_get_summary(self) -> None:
        eh = EndpointHealth()
        eh.report_success("r1", EndpointHealth.TYPE_ROUTER)
        eh.report_success("a1", EndpointHealth.TYPE_ADAPTER)
        summary = eh.get_summary()
        assert summary["total"] == 2
        assert summary["healthy_count"] == 2
        assert "by_type" in summary

    def test_clear(self) -> None:
        eh = EndpointHealth()
        eh.report_success("r1", EndpointHealth.TYPE_ROUTER)
        eh.clear()
        assert eh.get_summary()["total"] == 0


# ========================================================================
# APIGovernance
# ========================================================================

class TestAPIGovernance:
    def test_validate_deprecation_policy(self) -> None:
        g = APIGovernance()
        result = g.validate_deprecation_policy(["/old"])
        assert result.is_compliant
        assert result.policy == "deprecation_policy"

    def test_deprecated_endpoint_past_sunset(self) -> None:
        g = APIGovernance()
        g.mark_deprecated("/old", sunset_days=-1)
        result = g.validate_deprecation_policy(["/old"])
        assert not result.is_compliant

    def test_validate_endpoint_ownership(self) -> None:
        g = APIGovernance()
        result = g.validate_endpoint_ownership({"/test": "alice"})
        assert result.is_compliant

    def test_validate_endpoint_ownership_missing(self) -> None:
        g = APIGovernance()
        result = g.validate_endpoint_ownership({"/test": ""})
        assert not result.is_compliant

    def test_validate_version_policy(self) -> None:
        g = APIGovernance()
        result = g.validate_version_policy("v1", ["v1", "v2"])
        assert result.is_compliant

    def test_validate_contract_stability(self) -> None:
        g = APIGovernance()
        result = g.validate_contract_stability({"User": []})
        assert result.is_compliant

    def test_validate_contract_stability_breaking(self) -> None:
        g = APIGovernance()
        result = g.validate_contract_stability({"User": ["removed field email"]})
        assert not result.is_compliant

    def test_governance_report(self) -> None:
        g = APIGovernance()
        g.validate_endpoint_ownership({"/test": "bob"})
        g.validate_deprecation_policy([])
        report = g.get_governance_report()
        assert report["policy_count"] == 2

    def test_reset(self) -> None:
        g = APIGovernance()
        g.validate_deprecation_policy(["/bad"])
        g.reset()
        assert g.get_governance_report()["policy_count"] == 0


# ========================================================================
# APIManifest
# ========================================================================

class TestAPIManifest:
    def test_add_route(self) -> None:
        m = APIManifest()
        m.add_route("GET", "/test", "Test endpoint", ["testing"])
        manifest = m.build()
        assert manifest["route_count"] == 1
        assert manifest["routes"][0]["method"] == "GET"
        assert manifest["routes"][0]["path"] == "/test"

    def test_add_middleware(self) -> None:
        m = APIManifest()
        m.add_middleware("CorrelationMiddleware", enabled=True, priority=1)
        manifest = m.build()
        assert manifest["middleware_count"] == 1

    def test_add_adapter(self) -> None:
        m = APIManifest()
        m.add_adapter("planner", ["create_plan", "get_plan"])
        manifest = m.build()
        assert manifest["adapter_count"] == 1
        assert manifest["adapters"][0]["domain"] == "planner"

    def test_add_contract(self) -> None:
        m = APIManifest()
        m.add_contract("ApiResponse", "1.0.0", ["success", "data"])
        manifest = m.build()
        assert manifest["contract_count"] == 1

    def test_add_version(self) -> None:
        m = APIManifest()
        m.add_version("v1", "active", "Initial version")
        manifest = m.build()
        assert manifest["version_count"] == 1

    def test_build_has_metadata(self) -> None:
        m = APIManifest()
        manifest = m.build()
        assert "manifest_id" in manifest
        assert "created_at" in manifest

    def test_reset(self) -> None:
        m = APIManifest()
        m.add_route("GET", "/test")
        m.reset()
        assert m.build()["route_count"] == 0


# ========================================================================
# DocumentationMetadata
# ========================================================================

class TestDocumentationMetadata:
    def test_set_swagger_metadata(self) -> None:
        dm = DocumentationMetadata()
        dm.set_swagger_metadata(title="My API", version="2.0.0")
        d = dm.to_dict()
        assert d["swagger"]["title"] == "My API"
        assert d["swagger"]["version"] == "2.0.0"

    def test_set_redoc_metadata(self) -> None:
        dm = DocumentationMetadata()
        dm.set_redoc_metadata(title="Redoc API")
        d = dm.to_dict()
        assert d["redoc"]["title"] == "Redoc API"

    def test_set_openapi_metadata(self) -> None:
        dm = DocumentationMetadata()
        dm.set_openapi_metadata(spec_version="3.1.0", info={"title": "ADIP"})
        d = dm.to_dict()
        assert d["openapi"]["spec_version"] == "3.1.0"

    def test_add_route(self) -> None:
        dm = DocumentationMetadata()
        dm.add_route("GET", "/test", "A test", ["testing"])
        d = dm.to_dict()
        assert d["route_count"] == 1
        assert d["route_inventory"][0]["method"] == "GET"

    def test_add_service(self) -> None:
        dm = DocumentationMetadata()
        dm.add_service("PlannerService", "planner", ["create_plan"], "Planning service")
        d = dm.to_dict()
        assert d["service_count"] == 1

    def test_to_dict_structure(self) -> None:
        dm = DocumentationMetadata()
        d = dm.to_dict()
        assert "metadata_id" in d
        assert "created_at" in d
        assert "swagger" in d
        assert "redoc" in d
        assert "openapi" in d
        assert "route_inventory" in d
        assert "service_inventory" in d

    def test_reset(self) -> None:
        dm = DocumentationMetadata()
        dm.add_route("GET", "/test")
        dm.reset()
        assert dm.to_dict()["route_count"] == 0


# ========================================================================
# Enhanced Trace (diagnostics stage)
# ========================================================================

class TestAPITraceManagerPhase35:
    def test_record_diagnostics_stage(self) -> None:
        tm = APITraceManager()
        trace = tm.start_trace()
        tm.record_diagnostics_stage(trace.trace_id, "validation", "completed", {"errors": 0})
        trace_dict = trace.to_dict()
        assert trace_dict["trace_id"] is not None

    def test_record_compliance_stage(self) -> None:
        tm = APITraceManager()
        trace = tm.start_trace()
        tm.record_compliance_stage(trace.trace_id, "completed", {"compliant": True})
        assert len(trace.stages) >= 1

    def test_record_governance_stage(self) -> None:
        tm = APITraceManager()
        trace = tm.start_trace()
        tm.record_governance_stage(trace.trace_id, "completed", {"policy": "version"})
        assert len(trace.stages) >= 1

    def test_complete_trace(self) -> None:
        tm = APITraceManager()
        trace = tm.start_trace()
        trace.begin_stage("test")
        trace.end_stage()
        trace.complete()
        assert trace.stages[0].status == "completed"

    def test_list_traces(self) -> None:
        tm = APITraceManager()
        tm.start_trace()
        tm.start_trace()
        assert len(tm.list_traces()) == 2

    def test_clear(self) -> None:
        tm = APITraceManager()
        tm.start_trace()
        tm.clear()
        assert len(tm.list_traces()) == 0


# ========================================================================
# Enhanced Metrics (compliance, diagnostics, governance)
# ========================================================================

class TestAPIMetricsCollectorPhase35:
    def test_record_compliance(self) -> None:
        mc = APIMetricsCollector()
        mc.record_compliance("rest_standards", True)
        mc.record_compliance("version_rules", False)
        snapshot = mc.get_metrics_snapshot()
        assert "compliance_checks" in snapshot
        assert snapshot["compliance_checks"]["compliant:rest_standards"] == 1

    def test_record_diagnostics(self) -> None:
        mc = APIMetricsCollector()
        mc.record_diagnostics("validation")
        mc.record_diagnostics("adapter")
        snapshot = mc.get_metrics_snapshot()
        assert "diagnostics_by_category" in snapshot
        assert snapshot["diagnostics_by_category"]["validation"] == 1

    def test_record_governance(self) -> None:
        mc = APIMetricsCollector()
        mc.record_governance("version_policy", True)
        snapshot = mc.get_metrics_snapshot()
        assert "governance_checks" in snapshot

    def test_record_performance(self) -> None:
        mc = APIMetricsCollector()
        mc.record_performance(100.0)
        mc.record_performance(200.0)
        snapshot = mc.get_metrics_snapshot()
        assert snapshot["performance_samples"] == 2

    def test_backward_compatible_metrics(self) -> None:
        mc = APIMetricsCollector()
        mc.record_call("route", "GET", 200, 50.0)
        mc.record_call("route2", "POST", 500, 100.0)
        snapshot = mc.get_metrics_snapshot()
        assert snapshot["total_calls"] == 2
        assert snapshot["total_errors"] == 1
        assert snapshot["p50_latency_ms"] > 0
        assert snapshot["p95_latency_ms"] > 0

    def test_reset(self) -> None:
        mc = APIMetricsCollector()
        mc.record_compliance("test", True)
        mc.record_diagnostics("test")
        mc.reset()
        snapshot = mc.get_metrics_snapshot()
        assert snapshot["total_calls"] == 0
        assert len(snapshot["compliance_checks"]) == 0


# ========================================================================
# APIReadiness Phase 3.5 enhancements
# ========================================================================

class TestAPIReadinessPhase35:
    def test_check_compliance(self) -> None:
        r = APIReadiness()
        check = r.check_compliance(True)
        assert check.ready
        assert check.name == "compliance"

    def test_check_compliance_failed(self) -> None:
        r = APIReadiness()
        check = r.check_compliance(False)
        assert not check.ready

    def test_check_governance(self) -> None:
        r = APIReadiness()
        check = r.check_governance(True)
        assert check.ready

    def test_check_endpoint_health(self) -> None:
        r = APIReadiness()
        check = r.check_endpoint_health(5, 5)
        assert check.ready

    def test_check_endpoint_health_degraded(self) -> None:
        r = APIReadiness()
        check = r.check_endpoint_health(3, 5)
        assert not check.ready

    def test_check_pipeline_version(self) -> None:
        r = APIReadiness()
        check = r.check_pipeline_version("1.0.0")
        assert check.ready

    def test_check_pipeline_version_none(self) -> None:
        r = APIReadiness()
        check = r.check_pipeline_version(None)
        assert not check.ready

    def test_readiness_report_includes_generated_at(self) -> None:
        r = APIReadiness()
        r.check_version("v1")
        report = r.get_readiness_report()
        assert "generated_at" in report
        assert "passed_checks" in report
        assert "failed_checks" in report


# ========================================================================
# APISnapshot Phase 3.5 enhancements
# ========================================================================

class TestAPISnapshotPhase35:
    def test_snapshot_has_timestamp(self) -> None:
        s = Snapshot()
        assert hasattr(s, "timestamp")
        assert s.timestamp is not None

    def test_snapshot_has_decision_id(self) -> None:
        snap = APISnapshot()
        snapshot = snap.create_snapshot(decision_id="dec-123")
        d = snapshot.to_dict()
        assert d["decision_id"] == "dec-123"
        assert d["timestamp"] is not None

    def test_snapshot_to_dict_includes_new_fields(self) -> None:
        snap = APISnapshot()
        snapshot = snap.create_snapshot(
            request={"key": "val"},
            response={"status": "ok"},
            decision_id="dec-456",
        )
        d = snapshot.to_dict()
        assert d["timestamp"] is not None
        assert d["decision_id"] == "dec-456"
        assert d["request"] == {"key": "val"}

    def test_backward_compatible_create(self) -> None:
        snap = APISnapshot()
        snapshot = snap.create_snapshot(request={"a": 1}, response={"b": 2})
        d = snapshot.to_dict()
        assert d["request"] == {"a": 1}
        assert d["response"] == {"b": 2}
        assert d["decision_id"] is None


# ========================================================================
# ApiSession backward compatibility
# ========================================================================

class TestApiSessionBackwardCompat:
    def test_session_defaults(self) -> None:
        s = ApiSession()
        assert s.session_id is not None
        assert s.method == "GET"
        assert s.api_version == "v1"

    def test_session_with_values(self) -> None:
        s = ApiSession(route="/test", method="POST", api_version="v2")
        assert s.route == "/test"
        assert s.method == "POST"
        assert s.api_version == "v2"


# ========================================================================
# Import verification
# ========================================================================

class TestPhase35Imports:
    def test_import_enums(self) -> None:
        from adip.api.rest.enums import (
            ComplianceStatus,
            ExportFormat,
            HealthStatus,
            PipelineStage,
            ReadinessStatus,
        )
        assert ComplianceStatus.COMPLIANT.value == "compliant"
        assert HealthStatus.HEALTHY.value == "healthy"
        assert ReadinessStatus.READY.value == "ready"
        assert PipelineStage.REQUEST.value == "request"
        assert ExportFormat.JSON.value == "json"

    def test_import_compliance_manager(self) -> None:
        from adip.api.rest.orchestration.compliance_manager import APIComplianceManager
        assert APIComplianceManager is not None

    def test_import_diagnostics(self) -> None:
        from adip.api.rest.orchestration.diagnostics import APIDiagnostics
        assert APIDiagnostics is not None

    def test_import_performance_profile(self) -> None:
        from adip.api.rest.orchestration.performance_profile import APIPerformanceProfile
        assert APIPerformanceProfile is not None

    def test_import_export_package(self) -> None:
        from adip.api.rest.orchestration.export_package import APIExportPackage
        assert APIExportPackage is not None

    def test_import_pipeline_version(self) -> None:
        from adip.api.rest.orchestration.pipeline_version import APIPipelineVersion
        assert APIPipelineVersion is not None

    def test_import_replay_package(self) -> None:
        from adip.api.rest.orchestration.replay_package import RequestReplayStore
        assert RequestReplayStore is not None

    def test_import_endpoint_health(self) -> None:
        from adip.api.rest.orchestration.endpoint_health import EndpointHealth
        assert EndpointHealth is not None

    def test_import_governance(self) -> None:
        from adip.api.rest.orchestration.governance import APIGovernance
        assert APIGovernance is not None

    def test_import_manifest(self) -> None:
        from adip.api.rest.orchestration.manifest import APIManifest
        assert APIManifest is not None

    def test_import_documentation_metadata(self) -> None:
        from adip.api.rest.orchestration.documentation_metadata import DocumentationMetadata
        assert DocumentationMetadata is not None

    def test_import_orchestration_package(self) -> None:
        from adip.api.rest import orchestration
        assert hasattr(orchestration, "APIComplianceManager")
        assert hasattr(orchestration, "APIDiagnostics")
        assert hasattr(orchestration, "APIPerformanceProfile")
        assert hasattr(orchestration, "APIPipelineVersion")
        assert hasattr(orchestration, "EndpointHealth")
        assert hasattr(orchestration, "APIManifest")
        assert hasattr(orchestration, "RequestReplayStore")
        assert hasattr(orchestration, "APIExportPackage")
        assert hasattr(orchestration, "DocumentationMetadata")
        assert hasattr(orchestration, "APIGovernance")
