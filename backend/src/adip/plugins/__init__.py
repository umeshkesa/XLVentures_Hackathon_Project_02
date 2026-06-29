"""Plugin Manager — dynamic extension platform for the ADIP framework.

The Plugin Manager enables ADIP to dynamically discover, validate,
install, load, manage, and expose plugins. Plugins extend the
platform without requiring modifications to the core architecture.
PluginService is the ONLY public API for external modules.

Architecture:
    PluginService  →  PluginManager  →  PluginCoordinator
    (public API)      (lightweight)      (sub-component orchestration)
                                              ├── PluginDiscoverer
                                              ├── PluginValidator
                                              ├── DependencyResolver
                                              ├── PluginDependencyGraph
                                              ├── PluginCompatibilityManager
                                              ├── PluginLoader
                                              ├── PluginInitializer
                                              ├── PluginSandboxManager
                                              ├── PluginResourceManager
                                              ├── PluginLifecycleManager
                                              ├── CapabilityRegistration
                                              ├── PluginCache
                                              ├── PluginPolicyEngine
                                              ├── PluginTrace
                                              ├── PluginMetricsCollector
                                              ├── PluginHealthChecker
                                              └── VersionManager

Domain boundaries follow the ADIP pattern with component-level
interfaces and dependency injection throughout.

Phases:
    Phase 1 — Architecture, Contracts & Models (enums, models, events, DTOs, interfaces)
    Phase 2 — Plugin Processing & Lifecycle Pipeline (execution components)
    Phase 3 — Enterprise Orchestration (coordinator, manager, service)
"""

from __future__ import annotations

from adip.plugins.contracts.events import (
    EventVersion,
    PluginActivated,
    PluginDiscovered,
    PluginEvent,
    PluginInstalled,
    PluginLoaded,
    PluginRemoved,
    PluginSuspended,
    PluginUnloaded,
    PluginValidated,
    SandboxCreated,
    SandboxDestroyed,
)
from adip.plugins.contracts.exceptions import (
    PluginDependencyException,
    PluginException,
    PluginLoadException,
    PluginValidationException,
    SandboxException,
)
from adip.plugins.contracts.models import (
    Plugin,
    PluginCapability,
    PluginConfiguration,
    PluginDecision,
    PluginDependency,
    PluginHealth,
    PluginManifest,
    PluginMetadata,
    PluginMetrics,
    PluginNamespace,
    PluginPolicy,
    PluginSandbox,
    PluginSession,
)
from adip.plugins.dtos import (
    PluginDiscoveryDTO,
    PluginInstallDTO,
    PluginRequestDTO,
    PluginResponseDTO,
    PluginSandboxDTO,
)
from adip.plugins.enums import (
    PluginDomain,
    PluginLifecycleStatus,
    PluginType,
)
from adip.plugins.execution.cache import PluginCache
from adip.plugins.execution.capability_registration import CapabilityRegistration
from adip.plugins.execution.compatibility_manager import PluginCompatibilityManager
from adip.plugins.execution.dependency_graph import PluginDependencyGraph
from adip.plugins.execution.dependency_resolver import DependencyResolver
from adip.plugins.execution.discoverer import PluginDiscoverer
from adip.plugins.execution.initializer import PluginInitializer
from adip.plugins.execution.lifecycle_manager import PluginLifecycleManager
from adip.plugins.execution.loader import PluginLoader
from adip.plugins.execution.metrics import PluginMetricsCollector
from adip.plugins.execution.models import (
    CapabilityRecord,
    CompatibilityResult,
    DependencyGraph,
    DependencyNode,
    DiscoveryResult,
    InitializationResult,
    LifecycleHistoryEntry,
    LoaderResult,
    ResourceUsage,
    TraceRecord,
)
from adip.plugins.execution.policy import PluginPolicyEngine
from adip.plugins.execution.resource_manager import PluginResourceManager
from adip.plugins.execution.sandbox_manager import PluginSandboxManager
from adip.plugins.execution.trace import PluginTrace
from adip.plugins.execution.validator import PluginValidator
from adip.plugins.interfaces import (
    CapabilityDiscoverer as AbstractCapabilityDiscoverer,
)
from adip.plugins.interfaces import (
    DependencyResolver as AbstractDependencyResolver,
)
from adip.plugins.interfaces import (
    LifecycleManager as AbstractLifecycleManager,
)
from adip.plugins.interfaces import (
    PluginCoordinator as AbstractPluginCoordinator,
)
from adip.plugins.interfaces import (
    PluginHealthChecker as AbstractPluginHealthChecker,
)
from adip.plugins.interfaces import (
    PluginLoader as AbstractPluginLoader,
)
from adip.plugins.interfaces import (
    PluginManager as AbstractPluginManager,
)
from adip.plugins.interfaces import (
    PluginService as AbstractPluginService,
)
from adip.plugins.interfaces import (
    PluginValidator as AbstractPluginValidator,
)
from adip.plugins.interfaces import (
    SandboxManager as AbstractSandboxManager,
)
from adip.plugins.interfaces import (
    VersionManager as AbstractVersionManager,
)
from adip.plugins.orchestration.confidence import PluginConfidenceCalculator
from adip.plugins.orchestration.coordinator import PluginCoordinator
from adip.plugins.orchestration.manager import PluginManager as OrchestrationPluginManager
from adip.plugins.orchestration.session import PluginSessionManager
from adip.plugins.services.hooks import IntegrationHooks
from adip.plugins.services.hooks import hooks as global_hooks
from adip.plugins.services.service import AuthResult, PluginService

__all__ = [
    # Enums
    "PluginType",
    "PluginLifecycleStatus",
    "PluginDomain",
    # Models
    "Plugin",
    "PluginManifest",
    "PluginMetadata",
    "PluginCapability",
    "PluginDependency",
    "PluginConfiguration",
    "PluginHealth",
    "PluginMetrics",
    "PluginSession",
    "PluginDecision",
    "PluginSandbox",
    "PluginNamespace",
    "PluginPolicy",
    # DTOs
    "PluginRequestDTO",
    "PluginResponseDTO",
    "PluginInstallDTO",
    "PluginDiscoveryDTO",
    "PluginSandboxDTO",
    # Events
    "EventVersion",
    "PluginEvent",
    "PluginDiscovered",
    "PluginValidated",
    "PluginInstalled",
    "PluginLoaded",
    "PluginActivated",
    "PluginSuspended",
    "PluginUnloaded",
    "PluginRemoved",
    "SandboxCreated",
    "SandboxDestroyed",
    # Exceptions
    "PluginException",
    "PluginValidationException",
    "PluginDependencyException",
    "PluginLoadException",
    "SandboxException",
    # Interfaces (abstract)
    "AbstractPluginService",
    "AbstractPluginManager",
    "AbstractPluginCoordinator",
    "AbstractPluginLoader",
    "AbstractPluginValidator",
    "AbstractDependencyResolver",
    "AbstractCapabilityDiscoverer",
    "AbstractLifecycleManager",
    "AbstractVersionManager",
    "AbstractSandboxManager",
    "AbstractPluginHealthChecker",
    # Execution Models (Phase 2)
    "DiscoveryResult",
    "DependencyGraph",
    "DependencyNode",
    "CompatibilityResult",
    "LoaderResult",
    "InitializationResult",
    "ResourceUsage",
    "LifecycleHistoryEntry",
    "CapabilityRecord",
    "TraceRecord",
    # Execution Components (Phase 2)
    "PluginDiscoverer",
    "PluginValidator",
    "DependencyResolver",
    "PluginDependencyGraph",
    "PluginCompatibilityManager",
    "PluginLoader",
    "PluginInitializer",
    "PluginSandboxManager",
    "PluginResourceManager",
    "PluginLifecycleManager",
    "CapabilityRegistration",
    "PluginCache",
    "PluginPolicyEngine",
    "PluginTrace",
    "PluginMetricsCollector",
    # Orchestration (Phase 3)
    "PluginCoordinator",
    "OrchestrationPluginManager",
    "PluginSessionManager",
    "PluginConfidenceCalculator",
    # Services (Phase 3)
    "IntegrationHooks",
    "global_hooks",
    "PluginService",
    "AuthResult",
]
