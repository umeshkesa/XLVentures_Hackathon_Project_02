"""DefaultPlatformReadinessChecker — generates platform readiness reports."""

from __future__ import annotations

import structlog

from adip.platform.contracts.models import (
    PlatformHealth,
    PlatformReadinessReport,
    PlatformValidationResult,
)
from adip.platform.interfaces import PlatformReadinessChecker, ServiceRegistry

logger = structlog.get_logger(__name__)


class DefaultPlatformReadinessChecker(PlatformReadinessChecker):
    """Generates readiness reports based on validation and health state."""

    def __init__(self, platform_version: str = "1.0.0", build_metadata: dict[str, str] | None = None) -> None:
        self._platform_version = platform_version
        self._build_metadata = build_metadata or {
            "framework": "ADIP Platform Integration",
            "python": "3.12",
            "architecture": "Clean Architecture + SOLID",
        }
        logger.debug("readiness_checker.initialized")

    def check_readiness(
        self,
        registry: ServiceRegistry,
        validation: PlatformValidationResult,
        health: PlatformHealth,
    ) -> PlatformReadinessReport:
        bootstrap_status = "passed" if validation.bootstrap_valid else "failed"
        health_status = health.overall_status.value
        compatibility_status = "passed" if validation.contracts_valid else "failed"
        overall_ready = validation.platform_valid and health.overall_status.value == "healthy"

        messages: list[str] = []
        if bootstrap_status == "passed":
            messages.append("Bootstrap validation passed")
        else:
            messages.append("Bootstrap validation failed")

        if health_status == "healthy":
            messages.append(f"Health: {health.healthy_count}/{health.total_modules} modules healthy")
        else:
            messages.append(f"Health degraded: {health.healthy_count}/{health.total_modules} modules healthy")

        if compatibility_status == "passed":
            messages.append("Cross-module contracts validated")
        else:
            messages.append("Cross-module contract violations detected")

        logger.info(
            "readiness_report.generated",
            overall_ready=overall_ready,
            bootstrap=bootstrap_status,
            health=health_status,
            compatibility=compatibility_status,
        )

        return PlatformReadinessReport(
            bootstrap_status=bootstrap_status,
            health_status=health_status,
            compatibility_status=compatibility_status,
            version=self._platform_version,
            build_metadata=dict(self._build_metadata),
            overall_ready=overall_ready,
            messages=messages,
        )
