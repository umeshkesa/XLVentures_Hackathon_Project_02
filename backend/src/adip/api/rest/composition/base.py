"""Base composition service — abstract foundation for aggregation services."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


class BaseCompositionService(ABC):
    """Abstract base for API composition services.

    Composition services aggregate data from multiple domain adapters
    to serve cross-domain endpoints (dashboard, overviews, etc.).
    They contain NO business logic — only orchestration of adapter calls.
    """

    def __init__(self) -> None:
        self._name: str = self.__class__.__name__
        logger.debug("composition.initialized", name=self._name)

    @abstractmethod
    def get_name(self) -> str:
        """Return the composition service name."""

    def _aggregate(self, sources: dict[str, Any]) -> dict[str, Any]:
        """Merge data from multiple sources into a single response."""
        result: dict[str, Any] = {}
        for source_name, source_data in sources.items():
            if isinstance(source_data, dict) or source_data is not None:
                result[source_name] = source_data
        return result
