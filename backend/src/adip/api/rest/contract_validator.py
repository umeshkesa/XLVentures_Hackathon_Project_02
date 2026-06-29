"""API Contract Validator — validates request/response models and API version conformance."""

from __future__ import annotations

from typing import Any

import structlog
from pydantic import BaseModel, ValidationError

from adip.api.rest.enums import ApiVersion

logger = structlog.get_logger(__name__)


class ContractValidationResult:
    """Result of a contract validation."""

    def __init__(self) -> None:
        self.is_valid: bool = True
        self.errors: list[dict[str, Any]] = []

    def add_error(self, field: str, message: str) -> None:
        self.is_valid = False
        self.errors.append({"field": field, "message": message})


class APIContractValidator:
    """Validates API contracts including request/response models and API versions.

    Ensures that:
    - Request bodies conform to their Pydantic models
    - Response bodies conform to their Pydantic models
    - API versions are supported
    """

    SUPPORTED_VERSIONS = {ApiVersion.V1}

    def validate_request_model(self, model: type[BaseModel], data: dict[str, Any]) -> ContractValidationResult:
        result = ContractValidationResult()
        try:
            model(**data)
        except ValidationError as exc:
            for err in exc.errors():
                field = ".".join(str(loc) for loc in err.get("loc", []))
                result.add_error(
                    field=field or "body",
                    message=err.get("msg", "Validation error"),
                )
            logger.warning("contract.validation.request_failed", errors=result.errors)
        return result

    def validate_response_model(self, model: type[BaseModel], data: dict[str, Any]) -> ContractValidationResult:
        result = ContractValidationResult()
        try:
            model(**data)
        except ValidationError as exc:
            for err in exc.errors():
                field = ".".join(str(loc) for loc in err.get("loc", []))
                result.add_error(
                    field=field or "response",
                    message=err.get("msg", "Response validation error"),
                )
            logger.warning("contract.validation.response_failed", errors=result.errors)
        return result

    def validate_api_version(self, version: str) -> ContractValidationResult:
        result = ContractValidationResult()
        try:
            api_version = ApiVersion(version)
        except ValueError:
            result.add_error("api_version", f"Unsupported API version: {version}")
            return result

        if api_version not in self.SUPPORTED_VERSIONS:
            result.add_error(
                "api_version",
                f"API version '{version}' is not supported. Supported: {[v.value for v in self.SUPPORTED_VERSIONS]}",
            )
        return result
