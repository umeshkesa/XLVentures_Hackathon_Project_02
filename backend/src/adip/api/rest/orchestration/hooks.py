"""Integration hooks for the REST API Layer.

Provides extension points for:
- Authentication Module
- Authorization Module
- Frontend
- API Gateway
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


class IntegrationHooks:
    """Manages integration hooks for the REST API Layer.

    Each hook type supports multiple registered callbacks that are
    executed in registration order. Exceptions are caught and logged
    to prevent hook failures from affecting the main request flow.
    """

    def __init__(self) -> None:
        self._hooks: dict[str, list[Callable[..., Any]]] = {
            "pre_request": [],
            "post_request": [],
            "pre_validation": [],
            "post_validation": [],
            "pre_routing": [],
            "post_routing": [],
            "pre_adapter": [],
            "post_adapter": [],
            "pre_response": [],
            "post_response": [],
            "on_error": [],
        }

    def register(self, hook_type: str, callback: Callable[..., Any]) -> None:
        if hook_type in self._hooks:
            self._hooks[hook_type].append(callback)
            logger.debug("hook.registered", hook_type=hook_type, callback=callback.__name__)
        else:
            logger.warning("hook.unknown_type", hook_type=hook_type)

    def execute(self, hook_type: str, *args: Any, **kwargs: Any) -> list[Any]:
        results: list[Any] = []
        if hook_type not in self._hooks:
            return results
        for callback in self._hooks[hook_type]:
            try:
                result = callback(*args, **kwargs)
                results.append(result)
            except Exception as exc:
                logger.error("hook.failed", hook_type=hook_type, callback=callback.__name__, error=str(exc))
        return results

    def list_hooks(self) -> dict[str, list[str]]:
        return {k: [c.__name__ for c in v] for k, v in self._hooks.items()}

    def clear(self) -> None:
        for key in self._hooks:
            self._hooks[key].clear()


hooks = IntegrationHooks()
