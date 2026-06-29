"""APIService — the ONLY public API for the REST API Layer.

External modules MUST go through APIService to interact with the API layer.
Phase 3.5: exposes compliance, diagnostics, governance, performance, endpoint health,
and manifest reports.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import structlog

from adip.api.rest.models.base import ApiResponse
from adip.api.rest.orchestration.coordinator import APICoordinator
from adip.api.rest.orchestration.hooks import IntegrationHooks
from adip.api.rest.orchestration.hooks import hooks as global_hooks
from adip.api.rest.orchestration.manager import APIManager
from adip.api.rest.orchestration.models import ApiSession
from adip.api.rest.transformer import ResponseTransformer

logger = structlog.get_logger(__name__)


class APIService:
    """The ONLY public API for the REST API Layer."""

    def __init__(
        self,
        manager: APIManager | None = None,
        transformer: ResponseTransformer | None = None,
        hooks: IntegrationHooks | None = None,
        auth_callback: Callable[..., Any] | None = None,
        audit_callback: Callable[..., Any] | None = None,
    ) -> None:
        self._manager = manager or APIManager()
        self._transformer = transformer or ResponseTransformer()
        self._hooks = hooks or global_hooks
        self._auth_callback = auth_callback
        self._audit_callback = audit_callback

    @property
    def manager(self) -> APIManager:
        return self._manager

    @property
    def coordinator(self) -> APICoordinator:
        return self._manager.coordinator

    def process_request(
        self,
        domain: str,
        operation: str,
        request_data: dict[str, Any] | None = None,
        method: str = "GET",
    ) -> ApiResponse:
        logger.info(
            "api_service.process_request",
            domain=domain,
            operation=operation,
            method=method,
        )

        decision = self._manager.process_request(
            domain=domain,
            operation=operation,
            request_data=request_data,
            method=method,
        )

        if decision.success:
            return self._transformer.success(
                data=decision.response,
                processing_time_ms=decision.processing_time_ms,
            )
        return self._transformer.error(
            message=decision.response.get("message", "Request failed"),
            processing_time_ms=decision.processing_time_ms,
        )

    def create_session(self, route: str = "", method: str = "GET") -> ApiSession:
        return self._manager.create_session(route=route, method=method)

    def get_health(self) -> dict[str, Any]:
        return self._manager.get_health()

    def get_quality(self) -> dict[str, Any]:
        return self._manager.get_quality()

    def get_readiness(self) -> dict[str, Any]:
        return self._manager.get_readiness()

    def get_metrics(self) -> dict[str, Any]:
        return self._manager.get_metrics()

    # Phase 3.5
    def get_compliance_report(self) -> dict[str, Any]:
        return self._manager.get_compliance_report()

    def get_diagnostics(self) -> dict[str, Any]:
        return self._manager.get_diagnostics()

    def get_governance_report(self) -> dict[str, Any]:
        return self._manager.get_governance_report()

    def get_performance_summary(self) -> dict[str, Any]:
        return self._manager.get_performance_summary()

    def get_endpoint_health_summary(self) -> dict[str, Any]:
        return self._manager.get_endpoint_health_summary()

    def get_manifest(self) -> dict[str, Any]:
        return self._manager.get_manifest()
