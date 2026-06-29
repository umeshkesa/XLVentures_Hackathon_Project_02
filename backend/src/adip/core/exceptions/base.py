"""Application exception hierarchy.

Every domain-level exception inherits from ``BaseApplicationException``,
which carries an HTTP status code, a machine-readable error code, a human-readable
message, and optional detail metadata.  The FastAPI exception handlers in
:mod:`adip.core.exceptions.handlers` render these fields into a consistent JSON
error envelope.
"""

from typing import Any


class BaseApplicationException(Exception):
    """Base for all ADIP application exceptions."""

    status_code: int = 500
    code: str = "internal_error"
    message: str = "An unexpected error occurred."
    details: dict[str, Any] | None = None

    def __init__(
        self,
        message: str | None = None,
        *,
        code: str | None = None,
        status_code: int | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        if message is not None:
            self.message = message
        if code is not None:
            self.code = code
        if status_code is not None:
            self.status_code = status_code
        self.details = details
        super().__init__(self.message)


class ValidationException(BaseApplicationException):
    status_code = 422
    code = "validation_error"
    message = "The request payload contains invalid data."


class AuthenticationException(BaseApplicationException):
    status_code = 401
    code = "authentication_error"
    message = "Authentication is required."


class AuthorizationException(BaseApplicationException):
    status_code = 403
    code = "authorization_error"
    message = "You do not have permission to perform this action."


class ResourceNotFoundException(BaseApplicationException):
    status_code = 404
    code = "resource_not_found"
    message = "The requested resource could not be found."


class PlannerException(BaseApplicationException):
    status_code = 500
    code = "planner_error"
    message = "An error occurred in the planning subsystem."


class WorkflowException(BaseApplicationException):
    status_code = 500
    code = "workflow_error"
    message = "An error occurred in the workflow subsystem."


class KnowledgeException(BaseApplicationException):
    status_code = 500
    code = "knowledge_error"
    message = "An error occurred in the knowledge subsystem."


class DatabaseException(BaseApplicationException):
    status_code = 500
    code = "database_error"
    message = "A database operation failed."
