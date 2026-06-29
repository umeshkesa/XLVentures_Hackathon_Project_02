"""Energy Domain Package — Phase 3 (Enterprise Orchestration).

First business domain implementation for energy and utilities.
Provides energy-specific business models, contracts, DTOs,
events, interfaces, execution components, and orchestration.

Phase 3 adds enterprise orchestration: session management,
context, digital twin, readiness, versioning, lineage,
snapshots, health, portfolio, topology validation, policy,
coordinator, manager, service, and hooks.
"""

from adip.energy.contracts import models as energy_models
from adip.energy.dtos import (
    AlarmDTO,
    DigitalTwinDTO,
    EnergyAssetDTO,
    IncidentDTO,
    SensorDTO,
)
from adip.energy.enums import (
    AlarmSeverity,
    AlarmStatus,
    AssetStatus,
    AssetType,
    EnergyDomain,
    HealthState,
    IncidentPriority,
    MaintenanceType,
    SensorType,
    WorkOrderStatus,
)
from adip.energy.execution import (
    AlarmCorrelationEngine,
    AssetGraph,
    AssetLifecycleManager,
    AssetLifecycleState,
    DomainMetrics,
    DomainTrace,
    EnergyEventTimeline,
    EquipmentClassification,
    HealthScoreCalculator,
    MaintenanceScheduler,
    SensorValidationPipeline,
    TopologyService,
    UnitConversionService,
)
from adip.energy.interfaces import (
    AlarmRepository,
    AssetRepository,
    DigitalTwinRepository,
    EnergyDomainCoordinator,
    EnergyDomainManager,
    EnergyDomainService,
    MaintenanceRepository,
    SensorRepository,
)
from adip.energy.orchestration import (
    AssetContextManager,
    AssetPortfolioManager,
    DigitalTwinManager,
    DomainHealthManager,
    DomainPolicyManager,
    EnergyDecision,
    EnergyDomainCoordinator,
    EnergyDomainManager,
    EnergyExplainabilityMetadata,
    EnergyLineage,
    EnergyLineageModel,
    EnergyReadiness,
    EnergyReadinessCalculator,
    EnergySession,
    EnergySessionManager,
    EnergySnapshot,
    EnergySnapshotModel,
    EnergyVersionManager,
    EnergyVersionRecord,
    TopologyValidator,
)
from adip.energy.services.hooks import IntegrationHooks, hooks
from adip.energy.services.service import DefaultEnergyDomainService

__all__ = [
    # Enums
    "AssetType",
    "SensorType",
    "HealthState",
    "MaintenanceType",
    "AlarmSeverity",
    "EnergyDomain",
    "AssetStatus",
    "AlarmStatus",
    "IncidentPriority",
    "WorkOrderStatus",
    # Models
    "energy_models",
    # DTOs
    "EnergyAssetDTO",
    "SensorDTO",
    "DigitalTwinDTO",
    "AlarmDTO",
    "IncidentDTO",
    # Interfaces
    "EnergyDomainService",
    "EnergyDomainManager",
    "EnergyDomainCoordinator",
    "AssetRepository",
    "SensorRepository",
    "DigitalTwinRepository",
    "MaintenanceRepository",
    "AlarmRepository",
    # Phase 2 execution components
    "AssetGraph",
    "AssetLifecycleManager",
    "AssetLifecycleState",
    "SensorValidationPipeline",
    "HealthScoreCalculator",
    "AlarmCorrelationEngine",
    "MaintenanceScheduler",
    "TopologyService",
    "EnergyEventTimeline",
    "EquipmentClassification",
    "UnitConversionService",
    "DomainTrace",
    "DomainMetrics",
    # Phase 3 orchestration
    "EnergySession",
    "EnergyDecision",
    "EnergyExplainabilityMetadata",
    "EnergyReadiness",
    "EnergyVersionRecord",
    "EnergyLineageModel",
    "EnergySnapshotModel",
    "EnergySessionManager",
    "AssetContextManager",
    "EnergyReadinessCalculator",
    "EnergyVersionManager",
    "EnergyLineage",
    "EnergySnapshot",
    "DomainHealthManager",
    "AssetPortfolioManager",
    "TopologyValidator",
    "DomainPolicyManager",
    # Phase 3 services
    "IntegrationHooks",
    "hooks",
    "DefaultEnergyDomainService",
]
