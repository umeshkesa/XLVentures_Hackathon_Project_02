"""Energy Domain Phase 2 — Asset Intelligence & Domain Services.

Deterministic placeholder execution components for the energy
domain: asset graph, lifecycle, sensor validation, health,
alarm correlation, maintenance scheduling, topology, event
timeline, equipment classification, unit conversion, trace,
and metrics.
"""

from adip.energy.execution.alarm_correlation import AlarmCorrelationEngine
from adip.energy.execution.asset_graph import AssetGraph
from adip.energy.execution.equipment_classification import EquipmentClassification
from adip.energy.execution.event_timeline import EnergyEventTimeline
from adip.energy.execution.health_score import HealthScoreCalculator
from adip.energy.execution.lifecycle_manager import AssetLifecycleManager
from adip.energy.execution.maintenance_scheduler import MaintenanceScheduler
from adip.energy.execution.metrics import DomainMetrics
from adip.energy.execution.models import (
    AssetEdge,
    AssetGraphModel,
    AssetLifecycleState,
    AssetNode,
    ClassificationResult,
    ConversionRequest,
    ConversionResult,
    CorrelationGroup,
    DomainMetricsSnapshot,
    DomainTraceRecord,
    HealthScoreResult,
    LifecycleTransition,
    MaintenanceSchedule,
    TimelineEntry,
    TopologyResult,
    ValidationResult,
)
from adip.energy.execution.sensor_validation import SensorValidationPipeline
from adip.energy.execution.topology import TopologyService
from adip.energy.execution.trace import DomainTrace
from adip.energy.execution.unit_conversion import UnitConversionService

__all__ = [
    # Components
    "AssetGraph",
    "AssetLifecycleManager",
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
    # Models
    "AssetLifecycleState",
    "AssetNode",
    "AssetEdge",
    "AssetGraphModel",
    "LifecycleTransition",
    "ValidationResult",
    "HealthScoreResult",
    "CorrelationGroup",
    "MaintenanceSchedule",
    "TopologyResult",
    "TimelineEntry",
    "DomainTraceRecord",
    "DomainMetricsSnapshot",
    "ClassificationResult",
    "ConversionRequest",
    "ConversionResult",
]
