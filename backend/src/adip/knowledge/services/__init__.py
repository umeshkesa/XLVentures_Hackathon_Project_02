"""Knowledge Manager service layer.

KnowledgeService (the ONLY public API) and IntegrationHooks.
"""

from __future__ import annotations

from adip.knowledge.services.hooks import IntegrationHooks, hooks
from adip.knowledge.services.service import AuthResult, KnowledgeService

__all__ = [
    "KnowledgeService",
    "IntegrationHooks",
    "AuthResult",
    "hooks",
]
