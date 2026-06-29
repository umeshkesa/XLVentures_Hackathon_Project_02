"""Knowledge Manager orchestration layer.

KnowledgeCoordinator and KnowledgeManager implementations.
"""

from __future__ import annotations

from adip.knowledge.orchestration.coordinator import KnowledgeCoordinator
from adip.knowledge.orchestration.manager import KnowledgeManager

__all__ = [
    "KnowledgeCoordinator",
    "KnowledgeManager",
]
