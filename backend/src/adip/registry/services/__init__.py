"""Registry Framework Phase 3 service layer.

Provides the ONLY public API for registry operations (RegistryService)
and the integration hooks system (IntegrationHooks).
"""

from __future__ import annotations

from adip.registry.services.hooks import IntegrationHooks
from adip.registry.services.service import RegistryService

__all__ = [
    "IntegrationHooks",
    "RegistryService",
]
