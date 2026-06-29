"""Tests that all Evidence Fusion Engine exports are importable."""

from __future__ import annotations

import adip.evidence as evidence


class TestAllExports:
    def test_all_exports_importable(self) -> None:
        """Verify every name in __all__ is accessible from the module."""
        for name in evidence.__all__:
            assert hasattr(evidence, name), f"{name} not found in evidence module"


class TestAllNamesMatch:
    def test_all_members_in_all(self) -> None:
        """Verify that all public names in the evidence module match __all__."""
        expected = {
            # Enums
            "EvidenceDomain",
            "EvidenceType",
            "EvidenceStatus",
            "EvidenceClassification",
            "EvidencePriority",
            "RelationshipType",
            "BundleType",
            "ConsensusLevel",
            "FusionPolicyType",
            # Models
            "Evidence",
            "EvidenceSource",
            "EvidenceMetadata",
            "EvidenceProvenance",
            "EvidenceQuality",
            "EvidenceNode",
            "EvidenceEdge",
            "EvidenceGraph",
            "EvidencePackage",
            "EvidenceHealth",
            "EvidenceMetrics",
            "EvidenceSession",
            "EvidenceDecision",
            "EvidenceLineage",
            "EvidenceSnapshot",
            # Events
            "EvidenceEvent",
            "EvidenceCollected",
            "EvidenceValidated",
            "EvidenceNormalized",
            "EvidenceCorrelated",
            "EvidenceFused",
            "EvidencePackaged",
            # Exceptions
            "EvidenceException",
            "EvidenceValidationException",
            "EvidenceCorrelationException",
            "EvidenceFusionException",
            # DTOs
            "EvidenceRequestDTO",
            "EvidenceResponseDTO",
            "EvidencePackageDTO",
            # Interfaces
            "EvidenceService",
            "EvidenceManager",
            "EvidenceCoordinator",
            "EvidenceCollector",
            "EvidenceValidator",
            "EvidenceNormalizer",
            "EvidenceCorrelator",
            "EvidenceScorer",
            "EvidenceGraphBuilder",
            "EvidencePackageBuilder",
            # Phase 2 execution models
            "CorrelationResult",
            "ConflictReport",
            "CorrelationScore",
            "EvidenceBundle",
            "FreshnessThreshold",
            "SourceReliability",
            "Timeline",
            "TimelineEntry",
            "TraceRecord",
            "TrustScore",
            "TraceStage",
            # Phase 3 enhanced models
            "EvidenceConfidence",
            "EvidenceContext",
            "EvidenceExplainabilityMetadata",
            # Phase 3.5 execution components
            "EvidenceWeightManager",
            "EvidenceConsensusManager",
            # Phase 3 orchestration
            "EvidenceSessionManager",
            "EvidenceConfidenceCalculator",
            # Phase 3 services
            "IntegrationHooks",
            "AuthResult",
            "hooks",
        }
        actual = set(evidence.__all__)
        assert actual == expected, f"Missing: {expected - actual}, Extra: {actual - expected}"
