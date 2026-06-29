"""Validation pipeline — validates requests before they reach service adapters."""

from __future__ import annotations

from typing import Any

import structlog
from fastapi import Request

from adip.api.rest.enums import ApiVersion

logger = structlog.get_logger(__name__)


class ValidationResult:
    """Result of a validation check."""

    def __init__(self, is_valid: bool = True, error: str | None = None, field: str | None = None) -> None:
        self.is_valid = is_valid
        self.error = error
        self.field = field


class ValidationContext:
    """Context passed through the validation pipeline."""

    def __init__(self, request: Request, body: Any = None) -> None:
        self.request = request
        self.body = body
        self.headers = dict(request.headers)
        self.path_params = dict(request.path_params)
        self.query_params = dict(request.query_params)
        self.api_version: str | None = self._detect_api_version()
        self.errors: list[ValidationResult] = []

    def _detect_api_version(self) -> str | None:
        path = self.request.url.path
        import re
        match = re.search(r"/api/(v\d+)/", path)
        if match:
            return match.group(1)
        return None

    def add_error(self, error: ValidationResult) -> None:
        self.errors.append(error)

    def is_valid(self) -> bool:
        return all(e.is_valid for e in self.errors) if self.errors else True


class ValidationPipeline:
    """Pipeline that runs multiple validators against incoming requests."""

    def __init__(self) -> None:
        self._validators: list[Any] = []

    def add_validator(self, validator: Any) -> None:
        self._validators.append(validator)

    async def validate(self, context: ValidationContext) -> ValidationContext:
        for validator in self._validators:
            if not context.is_valid():
                break
            try:
                await validator.validate(context)
            except Exception as exc:
                logger.error("validator.failed", validator=type(validator).__name__, error=str(exc))
                context.add_error(
                    ValidationResult(
                        is_valid=False,
                        error=f"Validator {type(validator).__name__} failed: {exc}",
                    )
                )
        return context


class HeaderValidator:
    """Validates required HTTP headers."""

    REQUIRED_HEADERS = {"content-type", "accept"}

    async def validate(self, context: ValidationContext) -> None:
        for header in self.REQUIRED_HEADERS:
            if header not in context.headers:
                context.add_error(
                    ValidationResult(
                        is_valid=False,
                        error=f"Missing required header: {header}",
                        field=header,
                    )
                )


class PathParamValidator:
    """Validates path parameters."""

    async def validate(self, context: ValidationContext) -> None:
        for key, value in context.path_params.items():
            if not value or (isinstance(value, str) and not value.strip()):
                context.add_error(
                    ValidationResult(
                        is_valid=False,
                        error=f"Path parameter '{key}' must not be empty",
                        field=key,
                    )
                )


class QueryParamValidator:
    """Validates query parameters."""

    MAX_QUERY_LENGTH = 1000

    async def validate(self, context: ValidationContext) -> None:
        for key, value in context.query_params.items():
            if isinstance(value, str) and len(value) > self.MAX_QUERY_LENGTH:
                context.add_error(
                    ValidationResult(
                        is_valid=False,
                        error=f"Query parameter '{key}' exceeds maximum length of {self.MAX_QUERY_LENGTH}",
                        field=key,
                    )
                )


class BodyValidator:
    """Validates request body presence and type."""

    async def validate(self, context: ValidationContext) -> None:
        method = context.request.method.upper()
        if method in ("POST", "PUT", "PATCH") and context.body is None:
            context.add_error(
                ValidationResult(
                    is_valid=False,
                    error=f"Request body is required for {method} requests",
                    field="body",
                )
            )


class ApiVersionValidator:
    """Validates API version in the request path."""

    SUPPORTED_VERSIONS = {ApiVersion.V1.value}

    async def validate(self, context: ValidationContext) -> None:
        if context.api_version and context.api_version not in self.SUPPORTED_VERSIONS:
            context.add_error(
                ValidationResult(
                    is_valid=False,
                    error=f"Unsupported API version '{context.api_version}'. Supported versions: {', '.join(self.SUPPORTED_VERSIONS)}",
                    field="api_version",
                )
            )


def create_default_pipeline() -> ValidationPipeline:
    """Create a validation pipeline with all default validators."""
    pipeline = ValidationPipeline()
    pipeline.add_validator(HeaderValidator())
    pipeline.add_validator(PathParamValidator())
    pipeline.add_validator(QueryParamValidator())
    pipeline.add_validator(BodyValidator())
    pipeline.add_validator(ApiVersionValidator())
    return pipeline
