"""EvidenceManager — lightweight internal facade for evidence operations.

Delegates all operations to EvidenceCoordinator. Contains no business
logic — only delegation and structured logging.
"""

from __future__ import annotations

import structlog

from adip.evidence.contracts.models import (
    Evidence,
    EvidenceDecision,
    EvidenceHealth,
    EvidenceMetrics,
    EvidencePackage,
)
from adip.evidence.enums import EvidenceDomain, EvidenceType
from adip.evidence.orchestration.coordinator import EvidenceCoordinator

log = structlog.get_logger(__name__)


class EvidenceManager:
    """Lightweight internal facade over EvidenceCoordinator.

    All evidence processing, lookup, health, and metrics operations
    delegate directly to the coordinator. No business logic lives here.
    """

    def __init__(self, coordinator: EvidenceCoordinator | None = None) -> None:
        self._coordinator = coordinator or EvidenceCoordinator()

    # ── Collect & Process ───────────────────────────────────────────

    def collect_evidence(
        self,
        evidence_type: EvidenceType = EvidenceType.KNOWLEDGE,
        domain: EvidenceDomain = EvidenceDomain.SYSTEM,
        source_id: str = "",
        correlation_id: str = "",
    ) -> EvidenceDecision:
        """Collect evidence and run the full processing pipeline."""
        log.info(
            "evidence_manager.collect_evidence",
            evidence_type=evidence_type.value,
            domain=domain.value,
            source_id=source_id,
        )
        return self.coordinator.collect_and_process(
            evidence_type=evidence_type,
            domain=domain,
            source_id=source_id,
            correlation_id=correlation_id,
        )

    def process_existing(
        self,
        evidence_list: list[Evidence],
        correlation_id: str = "",
    ) -> EvidenceDecision:
        """Process existing evidence through the pipeline."""
        log.info(
            "evidence_manager.process_existing",
            count=len(evidence_list),
        )
        return self.coordinator.process_existing(
            evidence_list,
            correlation_id=correlation_id,
        )

    # ── Read / Lookup ───────────────────────────────────────────────

    def get_evidence(
        self,
        evidence_id: str,
        correlation_id: str = "",
    ) -> Evidence | None:
        """Retrieve an evidence item by its ID."""
        log.info("evidence_manager.get_evidence", evidence_id=evidence_id)
        return self.coordinator.get_evidence(evidence_id, correlation_id=correlation_id)

    def get_package(
        self,
        package_id: str,
        correlation_id: str = "",
    ) -> EvidencePackage | None:
        """Retrieve an evidence package by ID."""
        log.info("evidence_manager.get_package", package_id=package_id)
        return self.coordinator.get_package(package_id)

    # ── Health & Metrics ────────────────────────────────────────────

    def get_health(self) -> EvidenceHealth:
        """Return the current health status."""
        log.info("evidence_manager.get_health")
        return self.coordinator.health()

    def get_metrics(self) -> EvidenceMetrics:
        """Return aggregated metrics."""
        log.info("evidence_manager.get_metrics")
        return self.coordinator.metrics()

    # ── Sub-component access ────────────────────────────────────────

    @property
    def coordinator(self) -> EvidenceCoordinator:
        return self._coordinator

    @coordinator.setter
    def coordinator(self, value: EvidenceCoordinator) -> None:
        self._coordinator = value
