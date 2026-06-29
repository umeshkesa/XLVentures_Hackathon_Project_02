"""APIReadiness — determines API readiness based on version, routers, adapters, validation.

Phase 3.5: added compliance, governance, endpoint_health, pipeline_version checks,
and readiness report generation.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import structlog

from adip.api.rest.enums import ApiVersion

logger = structlog.get_logger(__name__)


class ReadinessCheck:
    """Result of a single readiness check."""

    def __init__(self, name: str, ready: bool = True, message: str = "") -> None:
        self.name = name
        self.ready = ready
        self.message = message


class APIReadiness:
    """Assesses API readiness across all dimensions."""

    def __init__(self) -> None:
        self._checks: dict[str, ReadinessCheck] = {}

    def register_check(self, name: str, ready: bool = True, message: str = "") -> None:
        self._checks[name] = ReadinessCheck(name, ready, message)

    def update_check(self, name: str, ready: bool, message: str = "") -> None:
        if name in self._checks:
            self._checks[name].ready = ready
            if message:
                self._checks[name].message = message

    def is_ready(self) -> bool:
        return all(c.ready for c in self._checks.values()) if self._checks else False

    def check_version(self, version: str) -> ReadinessCheck:
        try:
            valid = ApiVersion(version) in {ApiVersion.V1}
            check = ReadinessCheck("api_version", valid, "" if valid else f"Unsupported version: {version}")
            self._checks["api_version"] = check
            return check
        except ValueError:
            check = ReadinessCheck("api_version", False, f"Invalid version: {version}")
            self._checks["api_version"] = check
            return check

    def check_routers(self, router_count: int) -> ReadinessCheck:
        ready = router_count > 0
        check = ReadinessCheck("routers", ready, f"{router_count} routers registered" if ready else "No routers registered")
        self._checks["routers"] = check
        return check

    def check_adapters(self, adapter_count: int) -> ReadinessCheck:
        ready = adapter_count > 0
        check = ReadinessCheck("adapters", ready, f"{adapter_count} adapters ready" if ready else "No adapters ready")
        self._checks["adapters"] = check
        return check

    def check_validation(self, passed: bool) -> ReadinessCheck:
        check = ReadinessCheck("validation", passed, "Validation pipeline ready" if passed else "Validation pipeline not ready")
        self._checks["validation"] = check
        return check

    # Phase 3.5
    def check_compliance(self, is_compliant: bool) -> ReadinessCheck:
        check = ReadinessCheck("compliance", is_compliant, "Compliance checks passed" if is_compliant else "Compliance checks failed")
        self._checks["compliance"] = check
        return check

    def check_governance(self, is_compliant: bool) -> ReadinessCheck:
        check = ReadinessCheck("governance", is_compliant, "Governance checks passed" if is_compliant else "Governance checks failed")
        self._checks["governance"] = check
        return check

    def check_endpoint_health(self, healthy_count: int, total: int) -> ReadinessCheck:
        ready = total > 0 and healthy_count == total
        check = ReadinessCheck("endpoint_health", ready, f"{healthy_count}/{total} endpoints healthy" if ready else f"{healthy_count}/{total} endpoints healthy — some degraded")
        self._checks["endpoint_health"] = check
        return check

    def check_pipeline_version(self, version: str | None) -> ReadinessCheck:
        ready = version is not None
        check = ReadinessCheck("pipeline_version", ready, f"Pipeline version: {version}" if ready else "No pipeline version set")
        self._checks["pipeline_version"] = check
        return check

    def get_readiness_report(self) -> dict[str, Any]:
        return {
            "ready": self.is_ready(),
            "generated_at": datetime.now(UTC).isoformat(),
            "checks": {
                name: {"ready": check.ready, "message": check.message}
                for name, check in self._checks.items()
            },
            "check_count": len(self._checks),
            "passed_checks": sum(1 for c in self._checks.values() if c.ready),
            "failed_checks": sum(1 for c in self._checks.values() if not c.ready),
        }

    def reset(self) -> None:
        self._checks.clear()
