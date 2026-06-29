"""Evidence Phase 3 — Enterprise Orchestration.

Provides the orchestration layer for the Evidence Fusion Engine:
sessions, confidence calculator, coordinator, and manager.
"""

from __future__ import annotations

from adip.evidence.orchestration.confidence import EvidenceConfidenceCalculator
from adip.evidence.orchestration.coordinator import EvidenceCoordinator
from adip.evidence.orchestration.manager import EvidenceManager
from adip.evidence.orchestration.session import EvidenceSessionManager

__all__ = [
    "EvidenceSessionManager",
    "EvidenceConfidenceCalculator",
    "EvidenceCoordinator",
    "EvidenceManager",
]
