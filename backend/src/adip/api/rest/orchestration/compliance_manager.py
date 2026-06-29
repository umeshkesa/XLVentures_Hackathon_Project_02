"""APIComplianceManager — validates REST standards, OpenAPI compliance, version rules, naming conventions, HTTP semantics.

Phase 3.5 compliance refinement.
"""

from __future__ import annotations

import re
from typing import Any

import structlog

from adip.api.rest.enums import ApiVersion, ComplianceStatus
from adip.api.rest.orchestration.compliance import APIContractCompliance

logger = structlog.get_logger(__name__)


class StandardsResult:
    """Result of a standards compliance check."""

    def __init__(self, is_compliant: bool = True, errors: list[str] | None = None) -> None:
        self.is_compliant = is_compliant
        self.errors = errors or []
        self.status = ComplianceStatus.COMPLIANT if is_compliant else ComplianceStatus.NON_COMPLIANT


class APIComplianceManager:
    """Validates API compliance across REST standards, OpenAPI, version rules, naming conventions, and HTTP semantics.

    Compliance dimensions:
    - REST Standards: HTTP methods, resource naming, status codes
    - OpenAPI Compliance: schema presence, path definitions
    - Version Rules: supported versions, compatibility
    - Naming Conventions: kebab-case paths, snake_case fields
    - HTTP Semantics: method-appropriate status codes, idempotency
    """

    REST_METHODS = frozenset({"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"})
    SAFE_METHODS = frozenset({"GET", "HEAD", "OPTIONS"})
    IDEMPOTENT_METHODS = frozenset({"GET", "HEAD", "PUT", "DELETE", "OPTIONS"})

    def __init__(self, contract_compliance: APIContractCompliance | None = None) -> None:
        self._contract_compliance = contract_compliance or APIContractCompliance()
        self._results: dict[str, StandardsResult] = {}

    def validate_rest_standards(self, method: str, path: str, status_code: int) -> StandardsResult:
        errors: list[str] = []
        if method.upper() not in self.REST_METHODS:
            errors.append(f"Invalid HTTP method: {method}")
        if not path.startswith("/"):
            errors.append(f"Path must start with '/': {path}")
        if method.upper() in self.SAFE_METHODS and status_code >= 400:
            errors.append(f"Safe method {method} returned error status {status_code}")
        result = StandardsResult(len(errors) == 0, errors)
        self._results["rest_standards"] = result
        return result

    def validate_naming_conventions(self, path: str, fields: list[str] | None = None) -> StandardsResult:
        errors: list[str] = []
        segments = [s for s in path.split("/") if s]
        path_kebab_pattern = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*(\{[a-z_]+\})?$")
        for segment in segments:
            if "{" in segment and "}" in segment:
                continue
            if not path_kebab_pattern.match(segment):
                errors.append(f"Path segment not kebab-case: '{segment}' in '{path}'")
        if fields:
            field_snake_pattern = re.compile(r"^[a-z][a-z0-9_]*$")
            for field in fields:
                if not field_snake_pattern.match(field):
                    errors.append(f"Field not snake_case: '{field}'")
        result = StandardsResult(len(errors) == 0, errors)
        self._results["naming_conventions"] = result
        return result

    def validate_http_semantics(self, method: str, status_code: int) -> StandardsResult:
        errors: list[str] = []
        if method.upper() in self.IDEMPOTENT_METHODS and status_code == 409:
            errors.append(f"Idempotent method {method} should not return 409 Conflict")
        if method.upper() == "GET" and status_code not in (200, 304, 400, 401, 403, 404, 500):
            errors.append(f"GET returned unexpected status: {status_code}")
        if method.upper() == "POST" and status_code == 404:
            errors.append("POST should not return 404; use 201 or 400 instead")
        result = StandardsResult(len(errors) == 0, errors)
        self._results["http_semantics"] = result
        return result

    def validate_version_rules(self, version: str) -> StandardsResult:
        try:
            api_version = ApiVersion(version)
            supported = api_version in {ApiVersion.V1, ApiVersion.V2}
            errors: list[str] = []
            if not supported:
                errors.append(f"Unsupported API version: {version}")
            result = StandardsResult(supported, errors)
            self._results["version_rules"] = result
            return result
        except ValueError:
            result = StandardsResult(False, [f"Invalid API version value: {version}"])
            self._results["version_rules"] = result
            return result

    def validate_openapi_compliance(self, openapi_schema: dict[str, Any] | None) -> StandardsResult:
        contract_result = self._contract_compliance.validate_openapi(openapi_schema)
        result = StandardsResult(contract_result.is_compliant, contract_result.errors)
        self._results["openapi_compliance"] = result
        return result

    def get_compliance_report(self) -> dict[str, Any]:
        return {
            "overall_compliant": all(r.is_compliant for r in self._results.values()) if self._results else True,
            "checks": {
                name: {"compliant": r.is_compliant, "errors": r.errors, "status": r.status.value}
                for name, r in self._results.items()
            },
            "check_count": len(self._results),
            "failed_checks": sum(1 for r in self._results.values() if not r.is_compliant),
        }

    def reset(self) -> None:
        self._results.clear()
