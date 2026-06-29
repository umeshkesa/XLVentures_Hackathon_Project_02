"""Abstract interfaces for the Evidence Fusion Engine.

Defines the contract for all evidence pipeline components following
Clean Architecture and Dependency Injection principles.

     ┌─────────────────────────────────────────────────────┐
     │                  EvidenceService                     │
     │               (ONLY public API)                      │
     ├─────────────────────────────────────────────────────┤
     │                  EvidenceManager                     │
     │              (internal facade)                       │
     ├─────────────────────────────────────────────────────┤
     │                EvidenceCoordinator                   │
     │           (pipeline orchestrator)                    │
     ├──────────┬──────────┬──────────┬────────────────────┤
     │Collector │Validator │Normalizer│Correlator │Scorer   │
     ├──────────┴──────────┴──────────┴────────────────────┤
     │           EvidenceGraphBuilder                       │
     │           EvidencePackageBuilder                     │
     └─────────────────────────────────────────────────────┘

All interfaces are abstract and async. Implementations must be
deterministic placeholders until fusion algorithms are added.
"""

from __future__ import annotations

import abc
from typing import Any

from adip.evidence.contracts.events import EvidenceEvent
from adip.evidence.contracts.models import (
    Evidence,
    EvidenceDecision,
    EvidenceGraph,
    EvidenceHealth,
    EvidenceMetrics,
    EvidencePackage,
    EvidenceQuality,
)
from adip.evidence.enums import EvidenceDomain, EvidenceStatus, EvidenceType

# ═══════════════════════════════════════════════════════════════════════════════
# EvidenceCollector
# ═══════════════════════════════════════════════════════════════════════════════


class EvidenceCollector(abc.ABC):
    """Collects evidence from source systems.

    Responsible for fetching evidence from platform services
    (Knowledge Manager, Memory Manager, Rule Manager, etc.)
    and external sources, returning raw Evidence items.

    This interface is frozen as of Phase 1.
    """

    @abc.abstractmethod
    async def collect(
        self,
        evidence_type: EvidenceType,
        domain: EvidenceDomain,
        source_id: str = "",
        correlation_id: str = "",
    ) -> Evidence:
        """Collect evidence from the specified source."""
        ...

    @abc.abstractmethod
    async def collect_batch(
        self,
        evidence_types: list[EvidenceType],
        domain: EvidenceDomain,
        correlation_id: str = "",
    ) -> list[Evidence]:
        """Collect evidence from multiple source types."""
        ...


# ═══════════════════════════════════════════════════════════════════════════════
# EvidenceValidator
# ═══════════════════════════════════════════════════════════════════════════════


class EvidenceValidator(abc.ABC):
    """Validates evidence against defined criteria.

    Checks evidence metadata, source, provenance, quality,
    domain, and status to ensure data integrity before
    proceeding through the pipeline.
    """

    @abc.abstractmethod
    async def validate(self, evidence: Evidence) -> list[str]:
        """Validate evidence and return a list of violation messages.

        Returns an empty list if validation passes.
        """
        ...

    @abc.abstractmethod
    async def validate_batch(self, evidence_list: list[Evidence]) -> list[list[str]]:
        """Validate multiple evidence items and return violations per item."""
        ...


# ═══════════════════════════════════════════════════════════════════════════════
# EvidenceNormalizer
# ═══════════════════════════════════════════════════════════════════════════════


class EvidenceNormalizer(abc.ABC):
    """Normalizes evidence into a standard format.

    Transforms evidence from various source formats into a
    consistent, standardised representation for downstream
    correlation and fusion.
    """

    @abc.abstractmethod
    async def normalize(self, evidence: Evidence) -> Evidence:
        """Normalize a single evidence item."""
        ...

    @abc.abstractmethod
    async def normalize_batch(self, evidence_list: list[Evidence]) -> list[Evidence]:
        """Normalize multiple evidence items."""
        ...


# ═══════════════════════════════════════════════════════════════════════════════
# EvidenceCorrelator
# ═══════════════════════════════════════════════════════════════════════════════


class EvidenceCorrelator(abc.ABC):
    """Correlates evidence items to find relationships.

    Analyzes evidence items to identify relationships,
    patterns, and dependencies between them. Produces
    correlation scores and linked evidence groups.
    """

    @abc.abstractmethod
    async def correlate(
        self,
        evidence: Evidence,
        evidence_pool: list[Evidence],
    ) -> list[Evidence]:
        """Correlate a single evidence item against a pool of evidence.

        Returns the list of correlated evidence items.
        """
        ...

    @abc.abstractmethod
    async def correlate_batch(
        self,
        evidence_list: list[Evidence],
    ) -> list[list[Evidence]]:
        """Correlate multiple evidence items with each other.

        Returns correlation groups.
        """
        ...


# ═══════════════════════════════════════════════════════════════════════════════
# EvidenceScorer
# ═══════════════════════════════════════════════════════════════════════════════


class EvidenceScorer(abc.ABC):
    """Scores and rates evidence quality and relevance.

    Assigns quality scores to evidence based on freshness,
    completeness, consistency, and reliability dimensions.
    """

    @abc.abstractmethod
    async def score(self, evidence: Evidence) -> EvidenceQuality:
        """Score a single evidence item and return its quality assessment."""
        ...

    @abc.abstractmethod
    async def score_batch(self, evidence_list: list[Evidence]) -> list[EvidenceQuality]:
        """Score multiple evidence items."""
        ...


# ═══════════════════════════════════════════════════════════════════════════════
# EvidenceGraphBuilder
# ═══════════════════════════════════════════════════════════════════════════════


class EvidenceGraphBuilder(abc.ABC):
    """Builds evidence relationship graphs.

    Creates graph structures from evidence items and their
    relationships, enabling structural analysis of evidence
    connections.
    """

    @abc.abstractmethod
    async def build_graph(
        self,
        evidence_list: list[Evidence],
        relationships: list[tuple[str, str, str]] | None = None,
    ) -> EvidenceGraph:
        """Build a graph from evidence items and optional relationships.

        Args:
            evidence_list: The evidence items to include in the graph.
            relationships: Optional list of (source_id, target_id, relationship_type) tuples.

        Returns:
            An EvidenceGraph containing nodes and edges.
        """
        ...

    @abc.abstractmethod
    async def add_to_graph(
        self,
        graph: EvidenceGraph,
        evidence: Evidence,
        relationships: list[tuple[str, str, str]] | None = None,
    ) -> EvidenceGraph:
        """Add evidence to an existing graph with relationships."""
        ...


# ═══════════════════════════════════════════════════════════════════════════════
# EvidencePackageBuilder
# ═══════════════════════════════════════════════════════════════════════════════


class EvidencePackageBuilder(abc.ABC):
    """Builds unified evidence packages for the Reasoning Engine.

    Aggregates processed evidence into packages with fused
    content, relationship graphs, and confidence scores.
    """

    @abc.abstractmethod
    async def build_package(
        self,
        evidence_list: list[Evidence],
        graph: EvidenceGraph | None = None,
        correlation_id: str = "",
    ) -> EvidencePackage:
        """Build an evidence package from processed evidence items."""
        ...

    @abc.abstractmethod
    async def add_to_package(
        self,
        package: EvidencePackage,
        evidence: Evidence,
    ) -> EvidencePackage:
        """Add evidence to an existing package."""
        ...


# ═══════════════════════════════════════════════════════════════════════════════
# EvidenceCoordinator
# ═══════════════════════════════════════════════════════════════════════════════


class EvidenceCoordinator(abc.ABC):
    """Orchestrates the full evidence processing pipeline.

    Coordinates collection, validation, normalization, correlation,
    scoring, graph building, and packaging in the correct order.
    Contains orchestration only — no business logic.
    """

    @abc.abstractmethod
    async def collect_and_process(
        self,
        evidence_type: EvidenceType,
        domain: EvidenceDomain,
        source_id: str = "",
        correlation_id: str = "",
    ) -> EvidencePackage:
        """Collect evidence and run the full processing pipeline."""
        ...

    @abc.abstractmethod
    async def process_existing(
        self,
        evidence_list: list[Evidence],
        correlation_id: str = "",
    ) -> EvidencePackage:
        """Process existing evidence through the pipeline."""
        ...

    @abc.abstractmethod
    async def health(self) -> EvidenceHealth:
        """Return current health status of the pipeline."""
        ...

    @abc.abstractmethod
    async def metrics(self) -> EvidenceMetrics:
        """Return current pipeline metrics."""
        ...


# ═══════════════════════════════════════════════════════════════════════════════
# EvidenceManager
# ═══════════════════════════════════════════════════════════════════════════════


class EvidenceManager(abc.ABC):
    """Internal facade over the EvidenceCoordinator.

    Provides simplified access to evidence operations without
    exposing the coordinator's orchestration complexity.
    """

    @abc.abstractmethod
    async def collect_evidence(
        self,
        evidence_type: EvidenceType,
        domain: EvidenceDomain,
        source_id: str = "",
        correlation_id: str = "",
    ) -> Evidence:
        """Collect a single piece of evidence."""
        ...

    @abc.abstractmethod
    async def get_evidence(self, evidence_id: str) -> Evidence | None:
        """Retrieve evidence by ID."""
        ...

    @abc.abstractmethod
    async def get_package(self, package_id: str) -> EvidencePackage | None:
        """Retrieve an evidence package by ID."""
        ...

    @abc.abstractmethod
    async def health(self) -> EvidenceHealth:
        """Return current health status."""
        ...

    @abc.abstractmethod
    async def metrics(self) -> EvidenceMetrics:
        """Return current metrics."""
        ...


# ═══════════════════════════════════════════════════════════════════════════════
# EvidenceService
# ═══════════════════════════════════════════════════════════════════════════════


class EvidenceService(abc.ABC):
    """ONLY public API for the Evidence Fusion Engine.

    All external modules (Reasoning Engine, Planner, Workflow Engine,
    etc.) MUST go through this interface. Wraps evidence operations
    with authentication, auditing, correlation IDs, and integration hooks.
    """

    @abc.abstractmethod
    async def collect_evidence(
        self,
        evidence_type: EvidenceType,
        domain: EvidenceDomain,
        source_id: str = "",
        correlation_id: str = "",
    ) -> Evidence:
        """Collect evidence from a source.

        Validates access, runs pre/post hooks, and returns the evidence.
        """
        ...

    @abc.abstractmethod
    async def get_evidence(self, evidence_id: str, correlation_id: str = "") -> Evidence | None:
        """Retrieve evidence by ID."""
        ...

    @abc.abstractmethod
    async def get_package(self, package_id: str, correlation_id: str = "") -> EvidencePackage | None:
        """Retrieve an evidence package by ID."""
        ...

    @abc.abstractmethod
    async def health(self, correlation_id: str = "") -> EvidenceHealth:
        """Return current health status of the evidence engine."""
        ...

    @abc.abstractmethod
    async def metrics(self, correlation_id: str = "") -> EvidenceMetrics:
        """Return current metrics of the evidence engine."""
        ...
