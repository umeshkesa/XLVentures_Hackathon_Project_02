"""Memory Manager orchestration layer — Phase 3 enterprise orchestration.

MemoryService is the ONLY public API.

Architecture:
    MemoryService → MemoryManager → MemoryCoordinator → (Phase 2 components)
"""

from adip.memory.enums import MemoryDomain
from adip.memory.orchestration.coordinator import MemoryCoordinator
from adip.memory.orchestration.health import MemoryHealth
from adip.memory.orchestration.hooks import IntegrationHooks
from adip.memory.orchestration.metrics_aggregator import MetricsAggregator
from adip.memory.orchestration.pipeline import MemoryOperationPipeline
from adip.memory.orchestration.session import MemorySession
from adip.memory.orchestration.tracing import AggregatedTracing
from adip.memory.orchestration.transaction import MemoryTransaction

__all__ = [
    "AggregatedTracing",
    "IntegrationHooks",
    "MemoryCoordinator",
    "MemoryDomain",
    "MemoryHealth",
    "MemoryOperationPipeline",
    "MemorySession",
    "MemoryTransaction",
    "MetricsAggregator",
]
