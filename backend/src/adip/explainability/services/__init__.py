"""Explainability Engine Phase 3 — Service layer.

Provides the ONLY public API (DefaultExplainabilityService) and
IntegrationHooks for the Explainability Engine.
"""

from __future__ import annotations

from adip.explainability.services.hooks import IntegrationHooks, hooks
from adip.explainability.services.service import DefaultExplainabilityService

__all__ = [
    "IntegrationHooks",
    "hooks",
    "DefaultExplainabilityService",
]
