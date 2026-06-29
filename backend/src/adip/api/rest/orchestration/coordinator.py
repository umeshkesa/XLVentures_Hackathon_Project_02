"""APICoordinator — orchestrates the full API request pipeline.

Phase 3.5: extended pipeline with quality, compliance, diagnostics, governance,
performance profiling, pipeline version, endpoint health, manifest, replay,
export, documentation metadata, and readiness report stages.
"""

from __future__ import annotations

import time
from typing import Any

import structlog

from adip.api.rest.adapters.base import BaseServiceAdapter
from adip.api.rest.adapters.router_registry import get_adapter
from adip.api.rest.contract_validator import APIContractValidator
from adip.api.rest.exception_mapper import ExceptionMapper
from adip.api.rest.metrics import APIMetricsCollector
from adip.api.rest.models.base import ApiResponse
from adip.api.rest.orchestration.audit_package import APIAuditPackage
from adip.api.rest.orchestration.compliance import APIContractCompliance
from adip.api.rest.orchestration.compliance_manager import APIComplianceManager
from adip.api.rest.orchestration.diagnostics import APIDiagnostics
from adip.api.rest.orchestration.documentation_metadata import DocumentationMetadata
from adip.api.rest.orchestration.endpoint_health import EndpointHealth
from adip.api.rest.orchestration.export_package import APIExportPackage
from adip.api.rest.orchestration.governance import APIGovernance
from adip.api.rest.orchestration.health import APIHealthManager
from adip.api.rest.orchestration.hooks import IntegrationHooks
from adip.api.rest.orchestration.hooks import hooks as global_hooks
from adip.api.rest.orchestration.lineage import APILineage
from adip.api.rest.orchestration.manifest import APIManifest
from adip.api.rest.orchestration.models import ApiDecision, APISecurityContext
from adip.api.rest.orchestration.performance_profile import APIPerformanceProfile
from adip.api.rest.orchestration.pipeline_version import APIPipelineVersion
from adip.api.rest.orchestration.quality import APIQualityManager
from adip.api.rest.orchestration.readiness import APIReadiness
from adip.api.rest.orchestration.replay_package import RequestReplayStore
from adip.api.rest.orchestration.session import ApiSessionManager
from adip.api.rest.orchestration.snapshot import APISnapshot
from adip.api.rest.orchestration.version_manager import ApiVersionManager
from adip.api.rest.transformer import ResponseTransformer
from adip.api.rest.validation.pipeline import (
    ValidationPipeline,
    create_default_pipeline,
)

logger = structlog.get_logger(__name__)


class APICoordinator:
    """Orchestrates the full API request pipeline.

    Coordinates: validation, routing, adapters, transformer, exception mapper,
    middleware, metrics, composition, contract validator, version manager,
    health manager, quality manager, compliance manager, diagnostics,
    governance, performance profile, pipeline version, endpoint health,
    manifest, replay, export, documentation metadata, audit, lineage,
    readiness, snapshots, hooks.
    """

    def __init__(
        self,
        session_manager: ApiSessionManager | None = None,
        version_manager: ApiVersionManager | None = None,
        health_manager: APIHealthManager | None = None,
        audit_package: APIAuditPackage | None = None,
        lineage: APILineage | None = None,
        snapshot: APISnapshot | None = None,
        readiness: APIReadiness | None = None,
        quality_manager: APIQualityManager | None = None,
        compliance: APIContractCompliance | None = None,
        contract_validator: APIContractValidator | None = None,
        exception_mapper: ExceptionMapper | None = None,
        metrics_collector: APIMetricsCollector | None = None,
        transformer: ResponseTransformer | None = None,
        validation_pipeline: ValidationPipeline | None = None,
        hooks: IntegrationHooks | None = None,
        # Phase 3.5
        compliance_manager: APIComplianceManager | None = None,
        diagnostics: APIDiagnostics | None = None,
        governance: APIGovernance | None = None,
        performance_profile: APIPerformanceProfile | None = None,
        pipeline_version: APIPipelineVersion | None = None,
        endpoint_health: EndpointHealth | None = None,
        manifest: APIManifest | None = None,
        replay_store: RequestReplayStore | None = None,
        export_package: APIExportPackage | None = None,
        doc_metadata: DocumentationMetadata | None = None,
    ) -> None:
        self.session_manager = session_manager or ApiSessionManager()
        self.version_manager = version_manager or ApiVersionManager()
        self.health_manager = health_manager or APIHealthManager()
        self.audit_package = audit_package or APIAuditPackage()
        self.lineage = lineage or APILineage()
        self.snapshot = snapshot or APISnapshot()
        self.readiness = readiness or APIReadiness()
        self.quality_manager = quality_manager or APIQualityManager()
        self.compliance = compliance or APIContractCompliance()
        self.contract_validator = contract_validator or APIContractValidator()
        self.exception_mapper = exception_mapper or ExceptionMapper()
        self.metrics_collector = metrics_collector or APIMetricsCollector()
        self.transformer = transformer or ResponseTransformer()
        self.validation_pipeline = validation_pipeline or create_default_pipeline()
        self.hooks = hooks or global_hooks
        # Phase 3.5
        self.compliance_manager = compliance_manager or APIComplianceManager()
        self.diagnostics = diagnostics or APIDiagnostics()
        self.governance = governance or APIGovernance()
        self.performance_profile = performance_profile or APIPerformanceProfile()
        self.pipeline_version = pipeline_version or APIPipelineVersion()
        self.endpoint_health = endpoint_health or EndpointHealth()
        self.manifest = manifest or APIManifest()
        self.replay_store = replay_store or RequestReplayStore()
        self.export_package = export_package or APIExportPackage()
        self.doc_metadata = doc_metadata or DocumentationMetadata()

    def process_request(
        self,
        domain: str,
        operation: str,
        request_data: dict[str, Any] | None = None,
        method: str = "GET",
        security_context: APISecurityContext | None = None,
    ) -> ApiDecision:
        start_time = time.monotonic()
        trace_id = self.lineage.start_trace()
        decision = ApiDecision(api_version=self.version_manager.get_active_version())

        try:
            self.hooks.execute("pre_request", domain=domain, operation=operation)

            adapter = get_adapter(domain)
            if adapter is None:
                raise ValueError(f"No adapter found for domain: {domain}")

            self.lineage.record_adapter(trace_id, domain, operation)
            result = self._call_adapter(adapter, operation, request_data)

            self.lineage.record_response(trace_id, 200)
            decision.success = True
            decision.status_code = 200
            decision.http_status = 200
            decision.response = self._extract_response_data(result)
            decision.validation_passed = True

            self.hooks.execute("post_request", decision=decision)

            self._record_metrics(domain, operation, 200, start_time)

        except Exception as exc:
            status_code, response = self.exception_mapper.map(exc)
            decision.success = False
            decision.status_code = status_code
            decision.http_status = status_code
            decision.response = response.model_dump(mode="json") if hasattr(response, "model_dump") else {"error": str(exc)}
            decision.validation_passed = False
            self.hooks.execute("on_error", exception=exc, decision=decision)
            self._record_metrics(domain, operation, status_code, start_time)

        decision.processing_time_ms = (time.monotonic() - start_time) * 1000
        decision.pipeline_version = self.pipeline_version.get_active_version()

        # Phase 3.5 pipeline stages
        self._evaluate_quality(decision)
        self._run_compliance(decision, domain, operation, method)
        self._run_governance(decision)
        self._run_diagnostics(decision, domain, operation)
        self._run_performance_profile(decision, domain, operation)
        self._run_endpoint_health(decision, domain)
        self._run_manifest(decision, domain, operation, method)
        self._create_replay_package(decision, request_data, method)
        self._create_export_package(decision)
        self._create_documentation_metadata(decision)
        self._create_audit_package(decision, request_data)
        self._create_snapshot(decision, request_data)
        self._update_readiness(decision)

        return decision

    def get_adapter(self, domain: str) -> BaseServiceAdapter | None:
        return get_adapter(domain)

    def get_health(self) -> dict[str, Any]:
        return self.health_manager.get_health()

    def get_quality(self) -> dict[str, Any]:
        return self.quality_manager.get_quality_report()

    def get_readiness(self) -> dict[str, Any]:
        return self.readiness.get_readiness_report()

    def get_metrics(self) -> dict[str, Any]:
        return self.metrics_collector.get_metrics_snapshot()

    def get_compliance_report(self) -> dict[str, Any]:
        return self.compliance_manager.get_compliance_report()

    def get_diagnostics(self) -> dict[str, Any]:
        return self.diagnostics.get_diagnostics()

    def get_governance_report(self) -> dict[str, Any]:
        return self.governance.get_governance_report()

    def get_performance_summary(self) -> dict[str, Any]:
        return self.performance_profile.get_summary()

    def get_endpoint_health_summary(self) -> dict[str, Any]:
        return self.endpoint_health.get_summary()

    def get_manifest(self) -> dict[str, Any]:
        return self.manifest.build()

    def _call_adapter(self, adapter: BaseServiceAdapter, operation: str, request_data: dict[str, Any] | None = None) -> ApiResponse:
        return adapter.handle_operation(operation, request_data)

    def _extract_response_data(self, response: ApiResponse) -> dict[str, Any]:
        if hasattr(response, "model_dump"):
            return response.model_dump(mode="json")
        if isinstance(response, dict):
            return response
        return {"data": str(response)}

    def _record_metrics(self, domain: str, operation: str, status_code: int, start_time: float) -> None:
        latency = (time.monotonic() - start_time) * 1000
        self.metrics_collector.record_call(f"{domain}:{operation}", method="PROCESS", status_code=status_code, latency_ms=latency)

    # --- Phase 3.5 pipeline helpers ---

    def _evaluate_quality(self, decision: ApiDecision) -> None:
        try:
            self.quality_manager.evaluate_validation_quality(decision.validation_passed)
            self.quality_manager.evaluate_response_completeness(decision.success, not decision.validation_passed)
            self.quality_manager.evaluate_processing_time(decision.processing_time_ms)
            self.quality_manager.evaluate_request_completeness(has_body=bool(decision.response))
            decision.quality_score = self.quality_manager.get_overall_quality()
        except Exception as exc:
            logger.warning("quality.evaluation_failed", error=str(exc))

    def _run_compliance(self, decision: ApiDecision, domain: str, operation: str, method: str) -> None:
        try:
            self.compliance_manager.validate_rest_standards(method, f"/{domain}/{operation}", decision.status_code)
            self.compliance_manager.validate_http_semantics(method, decision.status_code)
            self.compliance_manager.validate_version_rules(decision.api_version)
            report = self.compliance_manager.get_compliance_report()
            decision.compliance_status = (
                "compliant" if report["overall_compliant"] else "non_compliant"
            )
            self.lineage.record_stage("placeholder_trace", "compliance", report)
            for name, check in report["checks"].items():
                self.metrics_collector.record_compliance(name, check["compliant"])
        except Exception as exc:
            logger.warning("compliance.evaluation_failed", error=str(exc))

    def _run_governance(self, decision: ApiDecision) -> None:
        try:
            self.governance.validate_version_policy(decision.api_version, [decision.api_version])
            report = self.governance.get_governance_report()
            decision.governance_result = report
            for name, result in report["policies"].items():
                self.metrics_collector.record_governance(name, result["is_compliant"])
        except Exception as exc:
            logger.warning("governance.evaluation_failed", error=str(exc))

    def _run_diagnostics(self, decision: ApiDecision, domain: str, operation: str) -> None:
        try:
            if not decision.validation_passed:
                self.diagnostics.record_validation_error("pipeline", "Validation failed during request processing")
                self.metrics_collector.record_diagnostics("validation")
            if not decision.success:
                self.diagnostics.record_adapter_failure(domain, operation, f"Adapter returned error status {decision.status_code}")
                self.metrics_collector.record_diagnostics("adapter")
            decision.diagnostics = self.diagnostics.get_diagnostics()
        except Exception as exc:
            logger.warning("diagnostics.collection_failed", error=str(exc))

    def _run_performance_profile(self, decision: ApiDecision, domain: str, operation: str) -> None:
        try:
            route_key = f"{domain}:{operation}"
            is_error = not decision.success
            self.performance_profile.record(route_key, decision.processing_time_ms, is_error)
            self.metrics_collector.record_performance(decision.processing_time_ms)
            summary = self.performance_profile.get_summary()
            decision.performance_profile = {
                "latency_ms": decision.processing_time_ms,
                "error_rate": summary.get("overall_error_rate", 0.0),
                "p95_ms": summary.get("overall_p95_ms", 0.0),
                "p99_ms": summary.get("overall_p99_ms", 0.0),
            }
        except Exception as exc:
            logger.warning("performance_profile.recording_failed", error=str(exc))

    def _run_endpoint_health(self, decision: ApiDecision, domain: str) -> None:
        try:
            if decision.success:
                self.endpoint_health.report_success(domain, EndpointHealth.TYPE_ADAPTER)
            else:
                self.endpoint_health.report_failure(domain, EndpointHealth.TYPE_ADAPTER, {"status_code": decision.status_code})
            summary = self.endpoint_health.get_summary()
            decision.endpoint_health = summary.get("overall_status", "healthy")
        except Exception as exc:
            logger.warning("endpoint_health.recording_failed", error=str(exc))

    def _run_manifest(self, decision: ApiDecision, domain: str, operation: str, method: str) -> None:
        try:
            self.manifest.add_route(method, f"/{domain}/{operation}", f"{domain}.{operation}")
            self.manifest.add_adapter(domain, [operation])
            decision.manifest = self.manifest.build()
        except Exception as exc:
            logger.warning("manifest.building_failed", error=str(exc))

    def _create_replay_package(self, decision: ApiDecision, request_data: dict[str, Any] | None, method: str) -> None:
        try:
            pkg = self.replay_store.create_package(
                method=method,
                path=f"/{decision.api_version}/request",
                body=request_data,
                timing_ms=decision.processing_time_ms,
                status_code=decision.status_code,
            )
            decision.replay_package = pkg.to_dict()
        except Exception as exc:
            logger.warning("replay_package.creation_failed", error=str(exc))

    def _create_export_package(self, decision: ApiDecision) -> None:
        try:
            pkg = self.export_package.create_package(
                route_manifest=[{"method": "GET", "path": "/placeholder"}],
                version_manifest=[{"version": decision.api_version, "status": "active"}],
            )
            decision.export_package = pkg.to_dict()
        except Exception as exc:
            logger.warning("export_package.creation_failed", error=str(exc))

    def _create_documentation_metadata(self, decision: ApiDecision) -> None:
        try:
            self.doc_metadata.set_swagger_metadata(version=decision.api_version)
            self.doc_metadata.set_redoc_metadata(version=decision.api_version)
            decision.documentation_metadata = self.doc_metadata.to_dict()
        except Exception as exc:
            logger.warning("documentation_metadata.creation_failed", error=str(exc))

    def _create_audit_package(self, decision: ApiDecision, request_data: dict[str, Any] | None) -> None:
        try:
            self.audit_package.create_package(
                request_data=request_data or {},
                response_data=decision.response,
                metadata={"decision_id": str(decision.decision_id), "api_version": decision.api_version},
                trace_data={"processing_time_ms": decision.processing_time_ms, "status_code": decision.status_code},
            )
        except Exception as exc:
            logger.warning("audit_package.creation_failed", error=str(exc))

    def _create_snapshot(self, decision: ApiDecision, request_data: dict[str, Any] | None) -> None:
        try:
            self.snapshot.create_snapshot(
                request=request_data or {},
                response=decision.response,
                metadata={"decision_id": str(decision.decision_id), "status_code": decision.status_code},
                decision_id=str(decision.decision_id),
            )
        except Exception as exc:
            logger.warning("snapshot.creation_failed", error=str(exc))

    def _update_readiness(self, decision: ApiDecision) -> None:
        try:
            self.readiness.check_version(decision.api_version)
            self.readiness.check_validation(decision.validation_passed)
            self.readiness.check_compliance(decision.compliance_status == "compliant")
            decision.readiness_status = "ready" if self.readiness.is_ready() else "not_ready"
        except Exception as exc:
            logger.warning("readiness.update_failed", error=str(exc))
