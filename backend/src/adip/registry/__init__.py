"""Registry Framework module.

The Registry Framework provides a reusable foundation for all ADIP
platform registries, including Capability Registry, Agent Registry,
Tool Registry, Rule Registry, Plugin Registry, and Workflow Registry.

Architecture:
    RegistryService  →  RegistryManager  →  RegistryCoordinator
                                             ├── RegistryValidator
                                             ├── RegistrySearcher
                                             ├── RegistryVersionManager
                                             ├── RegistryLifecycleManager
                                             └── RegistryHealthChecker

RegistryService is the ONLY public API for external consumers.

Phase 1: contracts, models, enums, events, exceptions, DTOs, interfaces.
Phase 2: execution pipeline (validator, searcher, version manager, etc.).
Phase 3: enterprise orchestration (coordinator, manager, service,
         session management, confidence calculator, integration hooks).
"""

from __future__ import annotations

from adip.registry.contracts.events import (
    EntryActivated,
    EntryDeprecated,
    EntryRegistered,
    EntryRemoved,
    EntryUpdated,
    EntryValidated,
    RegistryEvent,
)
from adip.registry.contracts.exceptions import (
    RegistryConflictException,
    RegistryException,
    RegistrySearchException,
    RegistryValidationException,
)
from adip.registry.contracts.models import (
    RegistryConfidence,
    RegistryDecision,
    RegistryEntry,
    RegistryExplainabilityMetadata,
    RegistryFilter,
    RegistryHealth,
    RegistryMetadata,
    RegistryMetrics,
    RegistryNamespace,
    RegistryPipelineVersion,
    RegistrySearchResult,
    RegistrySession,
    RegistryVersion,
)
from adip.registry.dtos import (
    RegistryRegistrationDTO,
    RegistryRequestDTO,
    RegistryResponseDTO,
    RegistrySearchDTO,
)
from adip.registry.enums import RegistryLifecycleStatus, RegistryScope, RegistryType
from adip.registry.interfaces import (
    BaseRegistry,
    RegistryCache,
    RegistryCoordinator,
    RegistryHealthChecker,
    RegistryLifecycleManager,
    RegistryManager,
    RegistrySearcher,
    RegistryService,
    RegistryValidator,
    RegistryVersionManager,
)
from adip.registry.orchestration import (
    RegistryConfidenceCalculator,
    RegistrySessionManager,
)
from adip.registry.orchestration import (
    RegistryCoordinator as RegistryCoordinatorImpl,
)
from adip.registry.orchestration import (
    RegistryManager as RegistryManagerImpl,
)
from adip.registry.services import (
    IntegrationHooks,
)
from adip.registry.services import (
    RegistryService as RegistryServiceImpl,
)

__all__ = [
    # Enums
    "RegistryType",
    "RegistryLifecycleStatus",
    "RegistryScope",
    # Models
    "RegistryEntry",
    "RegistryMetadata",
    "RegistryVersion",
    "RegistryHealth",
    "RegistryMetrics",
    "RegistrySession",
    "RegistryDecision",
    "RegistryConfidence",
    "RegistryExplainabilityMetadata",
    "RegistryPipelineVersion",
    "RegistrySearchResult",
    "RegistryFilter",
    "RegistryNamespace",
    # Events
    "RegistryEvent",
    "EntryRegistered",
    "EntryUpdated",
    "EntryValidated",
    "EntryActivated",
    "EntryDeprecated",
    "EntryRemoved",
    # Exceptions
    "RegistryException",
    "RegistryValidationException",
    "RegistryConflictException",
    "RegistrySearchException",
    # DTOs
    "RegistryRequestDTO",
    "RegistryResponseDTO",
    "RegistrySearchDTO",
    "RegistryRegistrationDTO",
    # Interfaces
    "BaseRegistry",
    "RegistryService",
    "RegistryManager",
    "RegistryCoordinator",
    "RegistryValidator",
    "RegistrySearcher",
    "RegistryVersionManager",
    "RegistryLifecycleManager",
    "RegistryHealthChecker",
    "RegistryCache",
    # Phase 3 Orchestration
    "RegistryCoordinatorImpl",
    "RegistryManagerImpl",
    "RegistrySessionManager",
    "RegistryConfidenceCalculator",
    "RegistryServiceImpl",
    "IntegrationHooks",
]
