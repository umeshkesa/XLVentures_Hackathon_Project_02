"""APIManager — lightweight facade over APICoordinator.

Phase 3.5: exposes compliance, diagnostics, governance, performance, endpoint health,
and manifest report methods.
"""

from __future__ import annotations

from typing import Any

import structlog

from adip.api.rest.orchestration.coordinator import APICoordinator
from adip.api.rest.orchestration.models import ApiDecision, ApiSession

logger = structlog.get_logger(__name__)


class APIManager:
    """Lightweight facade over the APICoordinator.

    Provides a simplified interface for API request processing
    while delegating all orchestration to the coordinator.
    """

    def __init__(self, coordinator: APICoordinator | None = None) -> None:
        self._coordinator = coordinator or APICoordinator()

    @property
    def coordinator(self) -> APICoordinator:
        return self._coordinator

    def process_request(
        self,
        domain: str,
        operation: str,
        request_data: dict[str, Any] | None = None,
        method: str = "GET",
    ) -> ApiDecision:
        return self._coordinator.process_request(
            domain=domain,
            operation=operation,
            request_data=request_data,
            method=method,
        )

    def create_session(self, route: str = "", method: str = "GET") -> ApiSession:
        return self._coordinator.session_manager.create_session(route=route, method=method)

    def get_health(self) -> dict[str, Any]:
        return self._coordinator.get_health()

    def get_quality(self) -> dict[str, Any]:
        return self._coordinator.get_quality()

    def get_readiness(self) -> dict[str, Any]:
        return self._coordinator.get_readiness()

    def get_metrics(self) -> dict[str, Any]:
        return self._coordinator.get_metrics()

    # Phase 3.5
    def get_compliance_report(self) -> dict[str, Any]:
        return self._coordinator.get_compliance_report()

    def get_diagnostics(self) -> dict[str, Any]:
        return self._coordinator.get_diagnostics()

    def get_governance_report(self) -> dict[str, Any]:
        return self._coordinator.get_governance_report()

    def get_performance_summary(self) -> dict[str, Any]:
        return self._coordinator.get_performance_summary()

    def get_endpoint_health_summary(self) -> dict[str, Any]:
        return self._coordinator.get_endpoint_health_summary()

    def get_manifest(self) -> dict[str, Any]:
        return self._coordinator.get_manifest()
