"""Error models for the REST API Layer."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from adip.api.rest.enums import ErrorType


class ValidationError(BaseModel):
    type: ErrorType = Field(default=ErrorType.VALIDATION_ERROR)
    code: str = Field(default="validation_error")
    message: str = Field(default="The request payload contains invalid data.")
    details: dict[str, Any] | None = Field(default=None)
    errors: list[dict[str, Any]] | None = Field(default=None)


class AuthenticationError(BaseModel):
    type: ErrorType = Field(default=ErrorType.AUTHENTICATION_ERROR)
    code: str = Field(default="authentication_error")
    message: str = Field(default="Authentication is required.")
    details: dict[str, Any] | None = Field(default=None)


class AuthorizationError(BaseModel):
    type: ErrorType = Field(default=ErrorType.AUTHORIZATION_ERROR)
    code: str = Field(default="authorization_error")
    message: str = Field(default="You do not have permission to perform this action.")
    details: dict[str, Any] | None = Field(default=None)


class BusinessError(BaseModel):
    type: ErrorType = Field(default=ErrorType.BUSINESS_ERROR)
    code: str = Field(default="business_error")
    message: str = Field(default="A business rule was violated.")
    details: dict[str, Any] | None = Field(default=None)


class PlatformError(BaseModel):
    type: ErrorType = Field(default=ErrorType.PLATFORM_ERROR)
    code: str = Field(default="platform_error")
    message: str = Field(default="An internal platform error occurred.")
    details: dict[str, Any] | None = Field(default=None)


class IntegrationError(BaseModel):
    type: ErrorType = Field(default=ErrorType.INTEGRATION_ERROR)
    code: str = Field(default="integration_error")
    message: str = Field(default="An external integration failed.")
    details: dict[str, Any] | None = Field(default=None)
