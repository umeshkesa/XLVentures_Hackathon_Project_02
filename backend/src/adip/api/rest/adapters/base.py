"""Base service adapter — abstract foundation for all domain adapters."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import structlog

from adip.api.rest.models.base import ApiResponse

logger = structlog.get_logger(__name__)


class BaseServiceAdapter(ABC):
    """Abstract base for all service adapters.

    Each adapter wraps one domain service and exposes its operations
    as deterministic placeholder methods returning ``ApiResponse``.
    Adapters contain NO business logic — they only translate between
    HTTP request/response formats and service interfaces.
    """

    def __init__(self) -> None:
        self._domain: str = self.__class__.__name__.replace("Adapter", "").lower()
        logger.debug("adapter.initialized", domain=self._domain)

    @abstractmethod
    def get_domain(self) -> str:
        """Return the domain name this adapter serves."""

    def _success_response(self, data: Any = None, **kwargs: Any) -> ApiResponse:
        return ApiResponse(success=True, data=data, **kwargs)

    def _error_response(
        self,
        code: str = "internal_error",
        message: str = "An error occurred.",
        **kwargs: Any,
    ) -> ApiResponse:
        from adip.api.rest.models.base import ApiError

        return ApiResponse(
            success=False,
            data=None,
            errors=[ApiError(code=code, message=message, details=kwargs.get("details"))],
        )

    def handle_operation(self, operation: str, params: dict[str, Any] | None = None) -> ApiResponse:
        """Route an operation to the appropriate adapter method.

        Deterministic placeholder — returns a success response with the
        operation name echoed back.
        """
        logger.info("adapter.operation", domain=self._domain, operation=operation)
        return self._success_response(
            data={
                "domain": self._domain,
                "operation": operation,
                "params": params or {},
                "status": "accepted",
            }
        )
