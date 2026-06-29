"""Platform IntegrationHooks — extension points for platform pipeline lifecycle.

Provides 8 hook types for pre/post pipeline execution and error handling.
Hooks are exception-isolated — a failing hook does not break the pipeline.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import structlog

from adip.platform.enums import PipelineStage

logger = structlog.get_logger(__name__)

# Type alias for hook callbacks
HookCallback = Callable[[dict[str, Any]], None]


class PlatformHooks:
    """Global platform integration hooks.

    Provides extension points for monitoring, audit, and custom
    integrations. All hook execution is exception-isolated.
    """

    def __init__(self) -> None:
        self._pre_pipeline: list[HookCallback] = []
        self._post_pipeline: list[HookCallback] = []
        self._pre_stage: list[HookCallback] = []
        self._post_stage: list[HookCallback] = []
        self._on_error: list[HookCallback] = []
        self._on_health_check: list[HookCallback] = []
        self._on_metrics: list[HookCallback] = []
        self._on_manifest: list[HookCallback] = []
        logger.debug("platform_hooks.initialized")

    def register_pre_pipeline(self, callback: HookCallback) -> None:
        """Register a callback to run before pipeline execution."""
        self._pre_pipeline.append(callback)
        logger.debug("hook.registered", hook="pre_pipeline")

    def register_post_pipeline(self, callback: HookCallback) -> None:
        """Register a callback to run after pipeline execution."""
        self._post_pipeline.append(callback)
        logger.debug("hook.registered", hook="post_pipeline")

    def register_pre_stage(self, callback: HookCallback) -> None:
        """Register a callback to run before each pipeline stage."""
        self._pre_stage.append(callback)
        logger.debug("hook.registered", hook="pre_stage")

    def register_post_stage(self, callback: HookCallback) -> None:
        """Register a callback to run after each pipeline stage."""
        self._post_stage.append(callback)
        logger.debug("hook.registered", hook="post_stage")

    def register_on_error(self, callback: HookCallback) -> None:
        """Register a callback to run on pipeline errors."""
        self._on_error.append(callback)
        logger.debug("hook.registered", hook="on_error")

    def register_on_health_check(self, callback: HookCallback) -> None:
        """Register a callback to run on health check."""
        self._on_health_check.append(callback)
        logger.debug("hook.registered", hook="on_health_check")

    def register_on_metrics(self, callback: HookCallback) -> None:
        """Register a callback to run on metrics collection."""
        self._on_metrics.append(callback)
        logger.debug("hook.registered", hook="on_metrics")

    def register_on_manifest(self, callback: HookCallback) -> None:
        """Register a callback to run on manifest generation."""
        self._on_manifest.append(callback)
        logger.debug("hook.registered", hook="on_manifest")

    def fire_pre_pipeline(self, context: dict[str, Any]) -> None:
        """Fire all pre-pipeline hooks."""
        self._fire_hooks(self._pre_pipeline, "pre_pipeline", context)

    def fire_post_pipeline(self, context: dict[str, Any]) -> None:
        """Fire all post-pipeline hooks."""
        self._fire_hooks(self._post_pipeline, "post_pipeline", context)

    def fire_pre_stage(self, stage: PipelineStage, context: dict[str, Any]) -> None:
        """Fire all pre-stage hooks."""
        ctx = {**context, "stage": stage.value}
        self._fire_hooks(self._pre_stage, "pre_stage", ctx)

    def fire_post_stage(self, stage: PipelineStage, context: dict[str, Any]) -> None:
        """Fire all post-stage hooks."""
        ctx = {**context, "stage": stage.value}
        self._fire_hooks(self._post_stage, "post_stage", ctx)

    def fire_on_error(self, stage: PipelineStage, error: str, context: dict[str, Any]) -> None:
        """Fire all on-error hooks."""
        ctx = {**context, "stage": stage.value, "error": error}
        self._fire_hooks(self._on_error, "on_error", ctx)

    def fire_on_health_check(self, context: dict[str, Any]) -> None:
        """Fire all on-health-check hooks."""
        self._fire_hooks(self._on_health_check, "on_health_check", context)

    def fire_on_metrics(self, context: dict[str, Any]) -> None:
        """Fire all on-metrics hooks."""
        self._fire_hooks(self._on_metrics, "on_metrics", context)

    def fire_on_manifest(self, context: dict[str, Any]) -> None:
        """Fire all on-manifest hooks."""
        self._fire_hooks(self._on_manifest, "on_manifest", context)

    def _fire_hooks(self, hooks: list[HookCallback], hook_type: str, context: dict[str, Any]) -> None:
        """Fire a list of hooks with exception isolation.

        Each hook is wrapped in a try-except so a single failing
        hook does not prevent other hooks from executing.
        """
        for callback in hooks:
            try:
                callback(context)
            except Exception as exc:
                logger.warning(
                    "hook.failed",
                    hook_type=hook_type,
                    error=str(exc),
                )

    def clear(self) -> None:
        """Clear all registered hooks."""
        self._pre_pipeline.clear()
        self._post_pipeline.clear()
        self._pre_stage.clear()
        self._post_stage.clear()
        self._on_error.clear()
        self._on_health_check.clear()
        self._on_metrics.clear()
        self._on_manifest.clear()
        logger.debug("platform_hooks.cleared")


# Global singleton instance
hooks = PlatformHooks()
