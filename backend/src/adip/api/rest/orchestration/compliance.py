"""APIContractCompliance — validates request/response schemas and version compatibility."""

from __future__ import annotations

from typing import Any

import structlog
from pydantic import BaseModel, ValidationError

from adip.api.rest.enums import ApiVersion

logger = structlog.get_logger(__name__)


class ComplianceResult:
    """Result of a compliance check."""

    def __init__(self, is_compliant: bool = True, errors: list[str] | None = None) -> None:
        self.is_compliant = is_compliant
        self.errors = errors or []


class APIContractCompliance:
    """Validates OpenAPI, request schema, response schema, and version compatibility."""

    SUPPORTED_VERSIONS = {ApiVersion.V1}

    def validate_openapi(self, openapi_schema: dict[str, Any] | None) -> ComplianceResult:
        if openapi_schema is None:
            return ComplianceResult(False, ["OpenAPI schema is missing"])
        if "openapi" not in openapi_schema:
            return ComplianceResult(False, ["OpenAPI version field missing"])
        if "paths" not in openapi_schema:
            return ComplianceResult(False, ["OpenAPI paths missing"])
        return ComplianceResult(True)

    def validate_request_schema(self, model: type[BaseModel], data: dict[str, Any]) -> ComplianceResult:
        errors: list[str] = []
        try:
            model(**data)
        except ValidationError as exc:
            for err in exc.errors():
                field = ".".join(str(loc) for loc in err.get("loc", []))
                errors.append(f"{field}: {err.get('msg', 'Validation error')}")
        return ComplianceResult(len(errors) == 0, errors)

    def validate_response_schema(self, model: type[BaseModel], data: dict[str, Any]) -> ComplianceResult:
        errors: list[str] = []
        try:
            model(**data)
        except ValidationError as exc:
            for err in exc.errors():
                field = ".".join(str(loc) for loc in err.get("loc", []))
                errors.append(f"{field}: {err.get('msg', 'Response error')}")
        return ComplianceResult(len(errors) == 0, errors)

    def validate_version_compatibility(self, version: str) -> ComplianceResult:
        try:
            api_version = ApiVersion(version)
        except ValueError:
            return ComplianceResult(False, [f"Invalid API version: {version}"])
        if api_version not in self.SUPPORTED_VERSIONS:
            return ComplianceResult(False, [f"Unsupported API version: {version}. Supported: {[v.value for v in self.SUPPORTED_VERSIONS]}"])
        return ComplianceResult(True)
