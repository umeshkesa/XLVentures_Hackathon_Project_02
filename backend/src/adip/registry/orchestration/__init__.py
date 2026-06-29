"""Registry Framework Phase 3 orchestration layer.

Provides the enterprise orchestration components for registry
operations including the RegistryCoordinator (pipeline orchestrator),
RegistryManager (internal facade), RegistrySessionManager (session
lifecycle), and RegistryConfidenceCalculator (confidence heuristics).
"""

from __future__ import annotations

from adip.registry.orchestration.confidence import RegistryConfidenceCalculator
from adip.registry.orchestration.coordinator import RegistryCoordinator
from adip.registry.orchestration.manager import RegistryManager
from adip.registry.orchestration.session import RegistrySessionManager

__all__ = [
    "RegistryCoordinator",
    "RegistryManager",
    "RegistrySessionManager",
    "RegistryConfidenceCalculator",
]
