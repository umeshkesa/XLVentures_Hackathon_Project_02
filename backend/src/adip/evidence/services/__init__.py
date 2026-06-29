"""Evidence Phase 3 — Services layer.

Provides the ONLY public API (EvidenceService) and integration
hooks for the Evidence Fusion Engine.
"""

from __future__ import annotations

from adip.evidence.services.hooks import IntegrationHooks, hooks
from adip.evidence.services.service import AuthResult, EvidenceService

__all__ = [
    "IntegrationHooks",
    "hooks",
    "AuthResult",
    "EvidenceService",
]
