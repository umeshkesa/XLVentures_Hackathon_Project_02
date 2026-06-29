"""API Exception Mapper — maps domain exceptions to HTTP error responses."""

from __future__ import annotations

from typing import Any

import structlog

from adip.api.rest.enums import ErrorType
from adip.api.rest.models.base import ApiError, ApiResponse

logger = structlog.get_logger(__name__)


class ExceptionMapper:
    """Maps application exceptions to standardised API error responses.

    Conversion table:
        ValidationException   → 400 / validation_error
        AuthenticationException → 401 / authentication_error
        AuthorizationException  → 403 / authorization_error
        BusinessException       → 422 / business_error
        NotFoundException       → 404 / not_found
        ConflictException       → 409 / conflict
        PlatformException       → 500 / platform_error
        IntegrationException    → 502 / integration_error
        Exception (fallback)    → 500 / internal_error
    """

    STATUS_MAP: dict[str, int] = {
        "validation_error": 400,
        "authentication_error": 401,
        "authorization_error": 403,
        "business_error": 422,
        "not_found": 404,
        "conflict": 409,
        "platform_error": 500,
        "integration_error": 502,
        "internal_error": 500,
    }

    def __init__(self) -> None:
        self._custom_handlers: dict[str, Any] = {}

    def register_handler(self, exception_type: str, handler: Any) -> None:
        self._custom_handlers[exception_type] = handler

    def map(self, exception: Exception) -> tuple[int, ApiResponse]:
        status_code = self._resolve_status_code(exception)
        error_type = self._resolve_error_type(status_code)
        message = self._resolve_message(exception)

        api_error = ApiError(
            code=error_type.value,
            message=message,
            details=getattr(exception, "details", None),
        )
        response = ApiResponse(
            success=False,
            data=None,
            errors=[api_error],
        )

        logger.warning(
            "exception_mapped",
            exception_type=type(exception).__name__,
            status_code=status_code,
            error_code=error_type.value,
        )
        return status_code, response

    def _resolve_status_code(self, exception: Exception) -> int:
        exc_name = type(exception).__name__
        exc_lower = exc_name.lower()
        msg_lower = str(exception).lower()
        if "validation" in exc_lower:
            return 400
        if "authentication" in exc_lower or "auth" in exc_lower and "unauthorized" in msg_lower:
            return 401
        if "authorization" in exc_lower or "auth" in exc_lower and "forbidden" in msg_lower:
            return 403
        if "business" in exc_lower:
            return 422
        if "notfound" in exc_lower or "not found" in msg_lower:
            return 404
        if "conflict" in exc_lower:
            return 409
        if "integration" in exc_lower:
            return 502
        return 500

    def _resolve_error_type(self, status_code: int) -> ErrorType:
        mapping = {
            400: ErrorType.VALIDATION_ERROR,
            401: ErrorType.AUTHENTICATION_ERROR,
            403: ErrorType.AUTHORIZATION_ERROR,
            404: ErrorType.NOT_FOUND,
            409: ErrorType.CONFLICT,
            422: ErrorType.BUSINESS_ERROR,
            500: ErrorType.PLATFORM_ERROR,
            502: ErrorType.INTEGRATION_ERROR,
        }
        return mapping.get(status_code, ErrorType.PLATFORM_ERROR)

    def _resolve_message(self, exception: Exception) -> str:
        return str(exception) or "An unexpected error occurred."
