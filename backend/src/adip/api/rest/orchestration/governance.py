"""APIGovernance — validates deprecation policy, endpoint ownership, version policy, and contract stability.

Phase 3.5 governance for production readiness.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID, uuid4

import structlog

from adip.api.rest.enums import ComplianceStatus

logger = structlog.get_logger(__name__)


class GovernanceResult:
    """Result of a governance validation check."""

    def __init__(self, policy: str, is_compliant: bool = True, errors: list[str] | None = None) -> None:
        self.governance_id: UUID = uuid4()
        self.policy: str = policy
        self.is_compliant: bool = is_compliant
        self.errors: list[str] = errors or []
        self.timestamp: datetime = datetime.now(UTC)
        self.status: ComplianceStatus = ComplianceStatus.COMPLIANT if is_compliant else ComplianceStatus.NON_COMPLIANT

    def to_dict(self) -> dict[str, Any]:
        return {
            "governance_id": str(self.governance_id),
            "policy": self.policy,
            "is_compliant": self.is_compliant,
            "errors": self.errors,
            "timestamp": self.timestamp.isoformat(),
            "status": self.status.value,
        }


class APIGovernance:
    """Validates API governance policies.

    Policies:
    - Deprecation Policy: endpoints must have sunset dates when deprecated
    - Endpoint Ownership: endpoints must have an owner
    - Version Policy: non-current versions must have migration guidance
    - Contract Stability: stable endpoints must not have breaking changes
    """

    def __init__(self) -> None:
        self._results: dict[str, GovernanceResult] = {}
        self._deprecated_endpoints: dict[str, datetime] = {}

    def mark_deprecated(self, path: str, sunset_days: int = 90) -> None:
        self._deprecated_endpoints[path] = datetime.now(UTC) + timedelta(days=sunset_days)
        logger.info("governance.endpoint_deprecated", path=path, sunset_days=sunset_days)

    def validate_deprecation_policy(self, paths: list[str]) -> GovernanceResult:
        errors: list[str] = []
        for path in paths:
            if path in self._deprecated_endpoints:
                sunset = self._deprecated_endpoints[path]
                if datetime.now(UTC) > sunset:
                    errors.append(f"Endpoint {path} is past its sunset date ({sunset.isoformat()})")
        result = GovernanceResult("deprecation_policy", len(errors) == 0, errors)
        self._results["deprecation_policy"] = result
        return result

    def validate_endpoint_ownership(self, endpoint_owners: dict[str, str]) -> GovernanceResult:
        errors: list[str] = []
        for endpoint, owner in endpoint_owners.items():
            if not owner or not owner.strip():
                errors.append(f"Endpoint {endpoint} has no owner assigned")
        result = GovernanceResult("endpoint_ownership", len(errors) == 0, errors)
        self._results["endpoint_ownership"] = result
        return result

    def validate_version_policy(self, active_version: str, all_versions: list[str]) -> GovernanceResult:
        errors: list[str] = []
        for version in all_versions:
            if version != active_version:
                errors.append(f"Version {version} is not active; migration guidance recommended")
        result = GovernanceResult("version_policy", True, errors if errors else None)
        self._results["version_policy"] = result
        return result

    def validate_contract_stability(self, contract_changes: dict[str, list[str]]) -> GovernanceResult:
        errors: list[str] = []
        for contract, changes in contract_changes.items():
            if changes:
                errors.append(f"Contract {contract} has breaking changes: {', '.join(changes)}")
        result = GovernanceResult("contract_stability", len(errors) == 0, errors)
        self._results["contract_stability"] = result
        return result

    def get_governance_report(self) -> dict[str, Any]:
        return {
            "overall_compliant": all(r.is_compliant for r in self._results.values()) if self._results else True,
            "policies": {
                name: result.to_dict()
                for name, result in self._results.items()
            },
            "deprecated_endpoints_count": len(self._deprecated_endpoints),
            "policy_count": len(self._results),
        }

    def reset(self) -> None:
        self._results.clear()
        self._deprecated_endpoints.clear()
