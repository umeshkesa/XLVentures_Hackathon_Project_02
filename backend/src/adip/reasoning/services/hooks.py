"""IntegrationHooks — extension points for ADIP platform modules.

All hooks are no-op by default. Downstream modules (Memory Manager,
Planner, Workflow Engine, etc.) can attach callbacks at runtime
without modifying the Reasoning Engine.

Only hook definitions — no business logic.
"""

from __future__ import annotations

from collections.abc import Callable

import structlog

from adip.reasoning.contracts.models import (
    ReasoningDecision,
    ReasoningRequest,
    ReasoningResult,
    ReasoningSession,
)

log = structlog.get_logger(__name__)


class IntegrationHooks:
    """Extension hooks for ADIP platform module integration.

    Each hook is a list of callables. Consumers register callbacks
    via the on_* methods. The ReasoningService invokes them at the
    appropriate points in the pipeline.
    """

    def __init__(self) -> None:
        self._pre_reason_hooks: list[Callable[[ReasoningRequest], None]] = []
        self._post_reason_hooks: list[Callable[[ReasoningResult], None]] = []
        self._pre_validate_hooks: list[Callable[[ReasoningRequest], None]] = []
        self._post_validate_hooks: list[Callable[[ReasoningRequest, list[str]], None]] = []
        self._pre_hypothesis_generate_hooks: list[Callable[[ReasoningRequest], None]] = []
        self._post_hypothesis_generate_hooks: list[Callable[[ReasoningRequest, list], None]] = []
        self._pre_inference_hooks: list[Callable[[ReasoningRequest], None]] = []
        self._post_inference_hooks: list[Callable[[ReasoningRequest, list], None]] = []
        self._pre_contradiction_detect_hooks: list[Callable[[ReasoningRequest], None]] = []
        self._post_contradiction_detect_hooks: list[Callable[[ReasoningRequest, list], None]] = []
        self._pre_decision_hooks: list[Callable[[ReasoningRequest], None]] = []
        self._post_decision_hooks: list[Callable[[ReasoningRequest, ReasoningDecision], None]] = []
        self._session_started_hooks: list[Callable[[ReasoningSession], None]] = []
        self._session_completed_hooks: list[Callable[[ReasoningSession], None]] = []
        self._error_hooks: list[Callable[[str, Exception], None]] = []

    def on_pre_reason(self, callback: Callable[[ReasoningRequest], None]) -> None:
        """Register a hook called before reasoning."""
        self._pre_reason_hooks.append(callback)

    def on_post_reason(self, callback: Callable[[ReasoningResult], None]) -> None:
        """Register a hook called after reasoning."""
        self._post_reason_hooks.append(callback)

    def on_pre_validate(self, callback: Callable[[ReasoningRequest], None]) -> None:
        """Register a hook called before validation."""
        self._pre_validate_hooks.append(callback)

    def on_post_validate(self, callback: Callable[[ReasoningRequest, list[str]], None]) -> None:
        """Register a hook called after validation."""
        self._post_validate_hooks.append(callback)

    def on_pre_hypothesis_generate(self, callback: Callable[[ReasoningRequest], None]) -> None:
        """Register a hook called before hypothesis generation."""
        self._pre_hypothesis_generate_hooks.append(callback)

    def on_post_hypothesis_generate(self, callback: Callable[[ReasoningRequest, list], None]) -> None:
        """Register a hook called after hypothesis generation."""
        self._post_hypothesis_generate_hooks.append(callback)

    def on_pre_inference(self, callback: Callable[[ReasoningRequest], None]) -> None:
        """Register a hook called before inference."""
        self._pre_inference_hooks.append(callback)

    def on_post_inference(self, callback: Callable[[ReasoningRequest, list], None]) -> None:
        """Register a hook called after inference."""
        self._post_inference_hooks.append(callback)

    def on_pre_contradiction_detect(self, callback: Callable[[ReasoningRequest], None]) -> None:
        """Register a hook called before contradiction detection."""
        self._pre_contradiction_detect_hooks.append(callback)

    def on_post_contradiction_detect(self, callback: Callable[[ReasoningRequest, list], None]) -> None:
        """Register a hook called after contradiction detection."""
        self._post_contradiction_detect_hooks.append(callback)

    def on_pre_decision(self, callback: Callable[[ReasoningRequest], None]) -> None:
        """Register a hook called before decision."""
        self._pre_decision_hooks.append(callback)

    def on_post_decision(self, callback: Callable[[ReasoningRequest, ReasoningDecision], None]) -> None:
        """Register a hook called after decision."""
        self._post_decision_hooks.append(callback)

    def on_session_started(self, callback: Callable[[ReasoningSession], None]) -> None:
        """Register a hook called when a session starts."""
        self._session_started_hooks.append(callback)

    def on_session_completed(self, callback: Callable[[ReasoningSession], None]) -> None:
        """Register a hook called when a session completes."""
        self._session_completed_hooks.append(callback)

    def on_error(self, callback: Callable[[str, Exception], None]) -> None:
        """Register a hook called when an error occurs."""
        self._error_hooks.append(callback)

    def invoke_pre_reason(self, request: ReasoningRequest) -> None:
        for hook in self._pre_reason_hooks:
            try:
                hook(request)
            except Exception:
                log.exception("hooks.pre_reason.error")

    def invoke_post_reason(self, result: ReasoningResult) -> None:
        for hook in self._post_reason_hooks:
            try:
                hook(result)
            except Exception:
                log.exception("hooks.post_reason.error")

    def invoke_pre_validate(self, request: ReasoningRequest) -> None:
        for hook in self._pre_validate_hooks:
            try:
                hook(request)
            except Exception:
                log.exception("hooks.pre_validate.error")

    def invoke_post_validate(self, request: ReasoningRequest, violations: list[str]) -> None:
        for hook in self._post_validate_hooks:
            try:
                hook(request, violations)
            except Exception:
                log.exception("hooks.post_validate.error")

    def invoke_pre_hypothesis_generate(self, request: ReasoningRequest) -> None:
        for hook in self._pre_hypothesis_generate_hooks:
            try:
                hook(request)
            except Exception:
                log.exception("hooks.pre_hypothesis_generate.error")

    def invoke_post_hypothesis_generate(self, request: ReasoningRequest, hypotheses: list) -> None:
        for hook in self._post_hypothesis_generate_hooks:
            try:
                hook(request, hypotheses)
            except Exception:
                log.exception("hooks.post_hypothesis_generate.error")

    def invoke_pre_inference(self, request: ReasoningRequest) -> None:
        for hook in self._pre_inference_hooks:
            try:
                hook(request)
            except Exception:
                log.exception("hooks.pre_inference.error")

    def invoke_post_inference(self, request: ReasoningRequest, inferences: list) -> None:
        for hook in self._post_inference_hooks:
            try:
                hook(request, inferences)
            except Exception:
                log.exception("hooks.post_inference.error")

    def invoke_pre_contradiction_detect(self, request: ReasoningRequest) -> None:
        for hook in self._pre_contradiction_detect_hooks:
            try:
                hook(request)
            except Exception:
                log.exception("hooks.pre_contradiction_detect.error")

    def invoke_post_contradiction_detect(self, request: ReasoningRequest, contradictions: list) -> None:
        for hook in self._post_contradiction_detect_hooks:
            try:
                hook(request, contradictions)
            except Exception:
                log.exception("hooks.post_contradiction_detect.error")

    def invoke_pre_decision(self, request: ReasoningRequest) -> None:
        for hook in self._pre_decision_hooks:
            try:
                hook(request)
            except Exception:
                log.exception("hooks.pre_decision.error")

    def invoke_post_decision(self, request: ReasoningRequest, decision: ReasoningDecision) -> None:
        for hook in self._post_decision_hooks:
            try:
                hook(request, decision)
            except Exception:
                log.exception("hooks.post_decision.error")

    def invoke_session_started(self, session: ReasoningSession) -> None:
        for hook in self._session_started_hooks:
            try:
                hook(session)
            except Exception:
                log.exception("hooks.session_started.error")

    def invoke_session_completed(self, session: ReasoningSession) -> None:
        for hook in self._session_completed_hooks:
            try:
                hook(session)
            except Exception:
                log.exception("hooks.session_completed.error")

    def invoke_error(self, operation: str, error: Exception) -> None:
        for hook in self._error_hooks:
            try:
                hook(operation, error)
            except Exception:
                log.exception("hooks.error.error")


# Default global hooks instance
hooks: IntegrationHooks = IntegrationHooks()
