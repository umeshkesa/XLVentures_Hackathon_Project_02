"""IntegrationHooks — extension points for the Decision Review Layer.

Provides hook points for external integrations to observe
review operations. All hooks are exception-isolated
(one hook failure does not affect others).

Phase 3 adds hooks for Action Manager and Action Engine.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import structlog

log = structlog.get_logger(__name__)

HookCallback = Callable[..., Any]


class IntegrationHooks:
    """Extension hooks for the Decision Review Layer.

    Provides pre/post hooks for review, session, error,
    workflow, escalation, decision, governance, audit,
    lineage, readiness, delegation, version, and action
    operations. All hooks execute with exception isolation.
    """

    def __init__(self) -> None:
        self._pre_review: list[HookCallback] = []
        self._post_review: list[HookCallback] = []
        self._on_error: list[HookCallback] = []
        self._session_created: list[HookCallback] = []
        self._session_completed: list[HookCallback] = []
        self._pre_escalation: list[HookCallback] = []
        self._post_escalation: list[HookCallback] = []
        self._workflow_started: list[HookCallback] = []
        self._workflow_completed: list[HookCallback] = []
        self._decision_made: list[HookCallback] = []
        # Phase 3 hooks
        self._pre_action: list[HookCallback] = []
        self._post_action: list[HookCallback] = []
        self._governance_confidence_calculated: list[HookCallback] = []
        self._consensus_evaluated: list[HookCallback] = []
        self._delegation_performed: list[HookCallback] = []
        self._version_created: list[HookCallback] = []
        self._readiness_assessed: list[HookCallback] = []
        self._audit_package_created: list[HookCallback] = []
        self._lineage_created: list[HookCallback] = []

    def register_pre_review(self, callback: HookCallback) -> None:
        """Register a hook to run before review."""
        self._pre_review.append(callback)

    def register_post_review(self, callback: HookCallback) -> None:
        """Register a hook to run after review."""
        self._post_review.append(callback)

    def register_on_error(self, callback: HookCallback) -> None:
        """Register a hook to run on error."""
        self._on_error.append(callback)

    def register_session_created(self, callback: HookCallback) -> None:
        """Register a hook to run when a session is created."""
        self._session_created.append(callback)

    def register_session_completed(self, callback: HookCallback) -> None:
        """Register a hook to run when a session is completed."""
        self._session_completed.append(callback)

    def register_pre_escalation(self, callback: HookCallback) -> None:
        """Register a hook to run before escalation."""
        self._pre_escalation.append(callback)

    def register_post_escalation(self, callback: HookCallback) -> None:
        """Register a hook to run after escalation."""
        self._post_escalation.append(callback)

    def register_workflow_started(self, callback: HookCallback) -> None:
        """Register a hook to run when a workflow starts."""
        self._workflow_started.append(callback)

    def register_workflow_completed(self, callback: HookCallback) -> None:
        """Register a hook to run when a workflow completes."""
        self._workflow_completed.append(callback)

    def register_decision_made(self, callback: HookCallback) -> None:
        """Register a hook to run when a decision is made."""
        self._decision_made.append(callback)

    def register_pre_action(self, callback: HookCallback) -> None:
        """Register a hook to run before action execution.

        For Action Manager integration.
        """
        self._pre_action.append(callback)

    def register_post_action(self, callback: HookCallback) -> None:
        """Register a hook to run after action execution.

        For Action Engine integration.
        """
        self._post_action.append(callback)

    def register_governance_confidence_calculated(self, callback: HookCallback) -> None:
        """Register a hook for governance confidence calculation."""
        self._governance_confidence_calculated.append(callback)

    def register_consensus_evaluated(self, callback: HookCallback) -> None:
        """Register a hook for consensus evaluation."""
        self._consensus_evaluated.append(callback)

    def register_delegation_performed(self, callback: HookCallback) -> None:
        """Register a hook for delegation operations."""
        self._delegation_performed.append(callback)

    def register_version_created(self, callback: HookCallback) -> None:
        """Register a hook for version creation."""
        self._version_created.append(callback)

    def register_readiness_assessed(self, callback: HookCallback) -> None:
        """Register a hook for readiness assessment."""
        self._readiness_assessed.append(callback)

    def register_audit_package_created(self, callback: HookCallback) -> None:
        """Register a hook for audit package creation."""
        self._audit_package_created.append(callback)

    def register_lineage_created(self, callback: HookCallback) -> None:
        """Register a hook for lineage creation."""
        self._lineage_created.append(callback)

    def _run_hooks(self, hooks: list[HookCallback], *args: Any, **kwargs: Any) -> None:
        for hook in hooks:
            try:
                hook(*args, **kwargs)
            except Exception as e:
                log.warning("hook.failed", hook=str(hook), error=str(e))

    def run_pre_review(self, **kwargs: Any) -> None:
        """Run all pre-review hooks."""
        self._run_hooks(self._pre_review, **kwargs)

    def run_post_review(self, **kwargs: Any) -> None:
        """Run all post-review hooks."""
        self._run_hooks(self._post_review, **kwargs)

    def run_on_error(self, **kwargs: Any) -> None:
        """Run all error hooks."""
        self._run_hooks(self._on_error, **kwargs)

    def run_session_created(self, **kwargs: Any) -> None:
        """Run all session-created hooks."""
        self._run_hooks(self._session_created, **kwargs)

    def run_session_completed(self, **kwargs: Any) -> None:
        """Run all session-completed hooks."""
        self._run_hooks(self._session_completed, **kwargs)

    def run_pre_escalation(self, **kwargs: Any) -> None:
        """Run all pre-escalation hooks."""
        self._run_hooks(self._pre_escalation, **kwargs)

    def run_post_escalation(self, **kwargs: Any) -> None:
        """Run all post-escalation hooks."""
        self._run_hooks(self._post_escalation, **kwargs)

    def run_workflow_started(self, **kwargs: Any) -> None:
        """Run all workflow-started hooks."""
        self._run_hooks(self._workflow_started, **kwargs)

    def run_workflow_completed(self, **kwargs: Any) -> None:
        """Run all workflow-completed hooks."""
        self._run_hooks(self._workflow_completed, **kwargs)

    def run_decision_made(self, **kwargs: Any) -> None:
        """Run all decision-made hooks."""
        self._run_hooks(self._decision_made, **kwargs)

    def run_pre_action(self, **kwargs: Any) -> None:
        """Run all pre-action hooks.

        For Action Manager integration.
        """
        self._run_hooks(self._pre_action, **kwargs)

    def run_post_action(self, **kwargs: Any) -> None:
        """Run all post-action hooks.

        For Action Engine integration.
        """
        self._run_hooks(self._post_action, **kwargs)

    def run_governance_confidence_calculated(self, **kwargs: Any) -> None:
        """Run all governance-confidence hooks."""
        self._run_hooks(self._governance_confidence_calculated, **kwargs)

    def run_consensus_evaluated(self, **kwargs: Any) -> None:
        """Run all consensus-evaluated hooks."""
        self._run_hooks(self._consensus_evaluated, **kwargs)

    def run_delegation_performed(self, **kwargs: Any) -> None:
        """Run all delegation-performed hooks."""
        self._run_hooks(self._delegation_performed, **kwargs)

    def run_version_created(self, **kwargs: Any) -> None:
        """Run all version-created hooks."""
        self._run_hooks(self._version_created, **kwargs)

    def run_readiness_assessed(self, **kwargs: Any) -> None:
        """Run all readiness-assessed hooks."""
        self._run_hooks(self._readiness_assessed, **kwargs)

    def run_audit_package_created(self, **kwargs: Any) -> None:
        """Run all audit-package-created hooks."""
        self._run_hooks(self._audit_package_created, **kwargs)

    def run_lineage_created(self, **kwargs: Any) -> None:
        """Run all lineage-created hooks."""
        self._run_hooks(self._lineage_created, **kwargs)


# Global singleton hooks instance
hooks = IntegrationHooks()
