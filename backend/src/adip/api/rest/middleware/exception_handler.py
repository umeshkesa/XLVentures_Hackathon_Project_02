"""Exception handling middleware for the REST API Layer."""

from __future__ import annotations

import structlog
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from adip.api.rest.enums import ErrorType
from adip.api.rest.models.base import ApiError, ApiMetadata, ApiResponse

logger = structlog.get_logger(__name__)


def _build_error_response(
    status_code: int,
    error_type: ErrorType,
    message: str,
    details: dict | None = None,
    request: Request | None = None,
) -> JSONResponse:
    metadata = ApiMetadata()
    api_error = ApiError(code=error_type.value, message=message, details=details)
    response = ApiResponse(
        success=False,
        data=None,
        metadata=metadata,
        errors=[api_error],
    )
    return JSONResponse(
        status_code=status_code,
        content=response.model_dump(mode="json"),
        headers={"X-Trace-ID": metadata.trace_id},
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    errors = []
    for err in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in err.get("loc", [])),
            "message": err.get("msg", "Validation error"),
            "code": err.get("type", "validation_error"),
        })
    logger.warning("validation_error", path=request.url.path, errors=errors)
    return _build_error_response(
        status_code=422,
        error_type=ErrorType.VALIDATION_ERROR,
        message="The request payload contains invalid data.",
        details={"errors": errors},
        request=request,
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    error_map = {
        401: (ErrorType.AUTHENTICATION_ERROR, "Authentication is required."),
        403: (ErrorType.AUTHORIZATION_ERROR, "You do not have permission to perform this action."),
        404: (ErrorType.NOT_FOUND, "The requested resource could not be found."),
        409: (ErrorType.CONFLICT, "The request conflicts with the current state."),
        429: (ErrorType.RATE_LIMITED, "Too many requests. Please try again later."),
    }
    error_type, message = error_map.get(
        exc.status_code,
        (ErrorType.PLATFORM_ERROR, "An unexpected error occurred."),
    )
    logger.warning(
        "http_exception",
        status_code=exc.status_code,
        path=request.url.path,
        detail=exc.detail,
    )
    return _build_error_response(
        status_code=exc.status_code,
        error_type=error_type,
        message=message,
        details={"detail": exc.detail} if exc.detail else None,
        request=request,
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("unhandled_exception", path=request.url.path, error_type=type(exc).__name__)
    return _build_error_response(
        status_code=500,
        error_type=ErrorType.INTERNAL_ERROR,
        message="An unexpected internal error occurred.",
        request=request,
    )


def register_exception_handlers(application: FastAPI) -> None:
    application.add_exception_handler(RequestValidationError, validation_exception_handler)
    application.add_exception_handler(HTTPException, http_exception_handler)
    application.add_exception_handler(Exception, unhandled_exception_handler)
