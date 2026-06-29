"""EvidenceService — the ONLY public API for evidence operations.

Provides validation, authentication, authorisation, audit, structured
logging, metrics, correlation ID propagation, and session management.
All external ADIP modules MUST interact with the evidence platform
through this service — never through EvidenceManager or
EvidenceCoordinator directly.
"""

from __future__ import annotations

import uuid
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import structlog

from adip.evidence.contracts.models import (
    Evidence,
    EvidenceDecision,
    EvidenceHealth,
    EvidenceMetrics,
    EvidencePackage,
)
from adip.evidence.enums import EvidenceDomain, EvidenceType
from adip.evidence.orchestration.manager import EvidenceManager
from adip.evidence.services.hooks import IntegrationHooks
from adip.evidence.services.hooks import hooks as default_hooks

log = structlog.get_logger(__name__)


@dataclass
class AuthResult:
    """Result of an authentication/authorisation check."""

    authenticated: bool = True
    authorised: bool = True
    user_id: str = ""
    message: str = ""


class EvidenceService:
    """Enterprise facade for all evidence operations.

    This is the ONLY public API for evidence operations. External
    modules (Planner, Workflow Engine, Memory Manager, etc.) MUST
    go through this service.

    Responsibilities:
        • Request validation
        • Authentication (via configurable auth_callback)
        • Authorisation (via configurable auth_callback)
        • Audit (via configurable audit_callback)
        • Structured logging
        • Metrics
        • Correlation IDs
        • Session management
        • Integration hooks
        • Delegation to EvidenceManager
    """

    def __init__(
        self,
        manager: EvidenceManager | None = None,
        hooks: IntegrationHooks | None = None,
        auth_callback: Callable[[str, str], AuthResult] | None = None,
        audit_callback: Callable[[str, str, dict[str, Any]], None] | None = None,
    ) -> None:
        self.manager = manager or EvidenceManager()
        self.hooks = hooks or default_hooks
        self.auth_callback = auth_callback or self._default_auth
        self.audit_callback = audit_callback or self._default_audit

    # ─────────────────────────────────────────────────────────────────
    # Collect & Process
    # ─────────────────────────────────────────────────────────────────

    def collect_evidence(
        self,
        evidence_type: EvidenceType = EvidenceType.KNOWLEDGE,
        domain: EvidenceDomain = EvidenceDomain.SYSTEM,
        source_id: str = "",
        user_id: str = "",
        correlation_id: str = "",
    ) -> EvidenceDecision | None:
        """Collect evidence with full enterprise pipeline.

        Validates auth, invokes pre/post hooks, delegates to manager,
        records audit, and returns the decision on success.
        """
        corr_id = correlation_id or str(uuid.uuid4())
        log.info(
            "evidence_service.collect_evidence",
            evidence_type=evidence_type.value,
            domain=domain.value,
            user_id=user_id,
            correlation_id=corr_id,
        )

        # Auth
        auth = self.auth_callback(user_id, "collect")
        if not auth.authenticated or not auth.authorised:
            log.warning("evidence_service.collect_evidence.auth_failed", user_id=user_id)
            self.audit_callback("collect", f"{domain.value}/{evidence_type.value}", {
                "status": "DENIED",
                "reason": auth.message,
                "correlation_id": corr_id,
            })
            return None

        # Pre-hooks
        self.hooks.invoke_pre_collect(evidence_type=evidence_type, domain=domain, correlation_id=corr_id)

        try:
            # Delegate
            decision = self.manager.collect_evidence(
                evidence_type=evidence_type,
                domain=domain,
                source_id=source_id,
                correlation_id=corr_id,
            )

            # Audit
            self.audit_callback("collect", f"{domain.value}/{evidence_type.value}", {
                "evidence_id": str(decision.evidence_id),
                "allowed": decision.allowed,
                "reasoning": decision.reasoning,
                "correlation_id": corr_id,
            })

            # Post-hooks
            self.hooks.invoke_post_collect(evidence=decision, correlation_id=corr_id)

            return decision
        except Exception as exc:
            log.exception("evidence_service.collect_evidence.error", correlation_id=corr_id)
            self.hooks.invoke_error(operation="collect", error=exc, correlation_id=corr_id)
            self.audit_callback("collect", f"{domain.value}/{evidence_type.value}", {
                "status": "ERROR",
                "error": str(exc),
                "correlation_id": corr_id,
            })
            raise

    # ─────────────────────────────────────────────────────────────────
    # Process existing
    # ─────────────────────────────────────────────────────────────────

    def process_existing(
        self,
        evidence_list: list[Evidence],
        user_id: str = "",
        correlation_id: str = "",
    ) -> EvidenceDecision | None:
        """Process existing evidence with full enterprise pipeline."""
        corr_id = correlation_id or str(uuid.uuid4())
        log.info(
            "evidence_service.process_existing",
            count=len(evidence_list),
            user_id=user_id,
            correlation_id=corr_id,
        )

        auth = self.auth_callback(user_id, "process")
        if not auth.authenticated or not auth.authorised:
            log.warning("evidence_service.process_existing.auth_failed", user_id=user_id)
            return None

        self.hooks.invoke_pre_process(evidence_list=evidence_list, correlation_id=corr_id)

        try:
            decision = self.manager.process_existing(evidence_list, correlation_id=corr_id)
            self.audit_callback("process", f"{len(evidence_list)} items", {
                "allowed": decision.allowed,
                "reasoning": decision.reasoning,
                "correlation_id": corr_id,
            })
            self.hooks.invoke_post_process(decision=decision, correlation_id=corr_id)
            return decision
        except Exception as exc:
            self.hooks.invoke_error(operation="process", error=exc, correlation_id=corr_id)
            raise

    # ─────────────────────────────────────────────────────────────────
    # Lookup
    # ─────────────────────────────────────────────────────────────────

    def get_evidence(
        self,
        evidence_id: str,
        user_id: str = "",
        correlation_id: str = "",
    ) -> Evidence | None:
        """Retrieve an evidence item by its identifier."""
        corr_id = correlation_id or str(uuid.uuid4())
        log.info("evidence_service.get_evidence", evidence_id=evidence_id, correlation_id=corr_id)

        auth = self.auth_callback(user_id, "read")
        if not auth.authenticated or not auth.authorised:
            return None

        self.hooks.invoke_pre_lookup(evidence_id=evidence_id, correlation_id=corr_id)

        try:
            evidence = self.manager.get_evidence(evidence_id, correlation_id=corr_id)
            self.hooks.invoke_post_lookup(evidence=evidence, correlation_id=corr_id)
            self.audit_callback("read", evidence_id, {
                "found": evidence is not None,
                "correlation_id": corr_id,
            })
            return evidence
        except Exception as exc:
            self.hooks.invoke_error(operation="read", error=exc, correlation_id=corr_id)
            raise

    def get_package(
        self,
        package_id: str,
        user_id: str = "",
        correlation_id: str = "",
    ) -> EvidencePackage | None:
        """Retrieve an evidence package by its identifier."""
        corr_id = correlation_id or str(uuid.uuid4())
        log.info("evidence_service.get_package", package_id=package_id, correlation_id=corr_id)

        auth = self.auth_callback(user_id, "read")
        if not auth.authenticated or not auth.authorised:
            return None

        try:
            package = self.manager.get_package(package_id, correlation_id=corr_id)
            self.audit_callback("read_package", package_id, {
                "found": package is not None,
                "correlation_id": corr_id,
            })
            return package
        except Exception as exc:
            self.hooks.invoke_error(operation="read_package", error=exc, correlation_id=corr_id)
            raise

    # ─────────────────────────────────────────────────────────────────
    # Health & Metrics
    # ─────────────────────────────────────────────────────────────────

    def health(self, user_id: str = "", correlation_id: str = "") -> EvidenceHealth:
        """Return the current health status of the evidence engine."""
        return self.manager.get_health()

    def metrics(self, user_id: str = "", correlation_id: str = "") -> EvidenceMetrics:
        """Return aggregated evidence engine metrics."""
        return self.manager.get_metrics()

    # ── Defaults ────────────────────────────────────────────────────

    @staticmethod
    def _default_auth(user_id: str, operation: str) -> AuthResult:
        """Default auth — allows all operations."""
        return AuthResult(authenticated=True, authorised=True, user_id=user_id)

    @staticmethod
    def _default_audit(operation: str, target: str, details: dict[str, Any]) -> None:
        """Default audit — logs to structlog."""
        log.info("evidence_service.audit", operation=operation, target=target, details=details)
