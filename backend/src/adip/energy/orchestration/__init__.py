"""Energy Domain Phase 3.5 — Enterprise Orchestration & Interface Freeze.

Orchestration components for the energy domain pipeline:
session management, context, digital twin, readiness,
versioning, lineage, snapshots, health, portfolio,
topology validation, policy, quality, compliance,
diagnostics, audit, export, pipeline version,
readiness reports, coordinator, and manager.
"""

from adip.energy.orchestration.audit_package import EnergyAuditPackageGenerator
from adip.energy.orchestration.compliance_manager import EnergyComplianceManager
from adip.energy.orchestration.context_manager import AssetContextManager
from adip.energy.orchestration.coordinator import EnergyDomainCoordinator
from adip.energy.orchestration.diagnostics import EnergyDiagnostics
from adip.energy.orchestration.digital_twin import DigitalTwinManager
from adip.energy.orchestration.export_profiles import EnergyExportProfiles
from adip.energy.orchestration.health import DomainHealthManager
from adip.energy.orchestration.lineage import EnergyLineage
from adip.energy.orchestration.manager import EnergyDomainManager
from adip.energy.orchestration.models import (
    DomainPipelineVersion,
    EnergyComplianceReport,
    EnergyDecision,
    EnergyExplainabilityMetadata,
    EnergyExportProfile,
    EnergyLineageModel,
    EnergyQualityReport,
    EnergyReadiness,
    EnergyReadinessReport,
    EnergySession,
    EnergySnapshotModel,
    EnergyVersionRecord,
    PortfolioQuality,
)
from adip.energy.orchestration.models import (
    EnergyAuditPackage as EnergyAuditPackageModel,
)
from adip.energy.orchestration.models import (
    EnergyDiagnostics as EnergyDiagnosticsModel,
)
from adip.energy.orchestration.pipeline_version import DomainPipelineVersionManager
from adip.energy.orchestration.policy import DomainPolicyManager
from adip.energy.orchestration.portfolio import AssetPortfolioManager
from adip.energy.orchestration.quality_manager import EnergyQualityManager
from adip.energy.orchestration.readiness import EnergyReadinessCalculator
from adip.energy.orchestration.readiness_report import EnergyReadinessReportGenerator
from adip.energy.orchestration.session import EnergySessionManager
from adip.energy.orchestration.snapshot import EnergySnapshot
from adip.energy.orchestration.topology_validator import TopologyValidator
from adip.energy.orchestration.version_manager import EnergyVersionManager

__all__ = [
    # Models
    "EnergySession",
    "EnergyDecision",
    "EnergyExplainabilityMetadata",
    "EnergyReadiness",
    "EnergyVersionRecord",
    "EnergyLineageModel",
    "EnergySnapshotModel",
    "EnergyQualityReport",
    "EnergyComplianceReport",
    "EnergyDiagnosticsModel",
    "EnergyReadinessReport",
    "EnergyAuditPackageModel",
    "EnergyExportProfile",
    "PortfolioQuality",
    "DomainPipelineVersion",
    # Orchestration components
    "EnergySessionManager",
    "AssetContextManager",
    "DigitalTwinManager",
    "EnergyReadinessCalculator",
    "EnergyVersionManager",
    "EnergyLineage",
    "EnergySnapshot",
    "DomainHealthManager",
    "AssetPortfolioManager",
    "TopologyValidator",
    "DomainPolicyManager",
    "EnergyQualityManager",
    "EnergyComplianceManager",
    "EnergyDiagnostics",
    "EnergyAuditPackageGenerator",
    "EnergyExportProfiles",
    "DomainPipelineVersionManager",
    "EnergyReadinessReportGenerator",
    # Coordinator & Manager
    "EnergyDomainCoordinator",
    "EnergyDomainManager",
]
