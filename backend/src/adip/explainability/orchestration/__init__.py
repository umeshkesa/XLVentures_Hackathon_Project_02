"""Explainability Engine Phase 3.5 — Orchestration layer.

Provides session management, confidence calculation, review,
version management, readiness assessment, lineage tracking,
snapshot capture, justification, compliance, audit packaging,
export profiles, coordinator, and manager components that
orchestrate the full explanation pipeline by delegating to
Phase 2 execution components.
"""

from __future__ import annotations

from adip.explainability.orchestration.audit_package import ExplanationAuditPackage
from adip.explainability.orchestration.compliance import ExplanationCompliance
from adip.explainability.orchestration.confidence import ExplanationConfidenceCalculator
from adip.explainability.orchestration.coordinator import ExplainabilityCoordinatorImpl
from adip.explainability.orchestration.export_profiles import ExplanationExportProfiles
from adip.explainability.orchestration.justification import ExplanationJustification
from adip.explainability.orchestration.lineage import ExplanationLineage
from adip.explainability.orchestration.manager import ExplainabilityManagerImpl
from adip.explainability.orchestration.readiness import ExplanationReadiness
from adip.explainability.orchestration.review import ExplanationReview
from adip.explainability.orchestration.session import ExplanationSessionManager
from adip.explainability.orchestration.snapshot import ExplanationSnapshot
from adip.explainability.orchestration.version_manager import ExplanationVersionManager

__all__ = [
    "ExplanationAuditPackage",
    "ExplanationCompliance",
    "ExplanationConfidenceCalculator",
    "ExplanationExportProfiles",
    "ExplanationJustification",
    "ExplanationLineage",
    "ExplanationReadiness",
    "ExplanationReview",
    "ExplanationSessionManager",
    "ExplanationSnapshot",
    "ExplanationVersionManager",
    "ExplainabilityCoordinatorImpl",
    "ExplainabilityManagerImpl",
]
