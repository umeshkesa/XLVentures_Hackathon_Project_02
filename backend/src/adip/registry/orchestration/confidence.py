"""RegistryConfidenceCalculator — deterministic confidence heuristics.

Calculates RegistryConfidence for registry decisions based on
seven dimensions: metadata completeness, validation quality,
version correctness, namespace validity, policy compliance,
dependency integrity, and search result quality.

Phase 3.5 adds the search_result_quality dimension.

Placeholder implementation using simple deterministic heuristics.
No machine learning or probabilistic models are used.
"""

from __future__ import annotations

import structlog

from adip.registry.contracts.models import (
    RegistryConfidence,
    RegistryEntry,
    RegistryExplainabilityMetadata,
)

log = structlog.get_logger(__name__)


class RegistryConfidenceCalculator:
    """Calculates deterministic confidence scores for registry decisions.

    Each dimension is scored 0.0–1.0 based on simple heuristics:
    - Metadata Completeness: ratio of present metadata fields
    - Validation Quality: 1.0 if no validation violations, 0.5 if any, 0.0 if critical
    - Version Correctness: 1.0 if semver-like, 0.5 if not
    - Namespace Validity: 1.0 if namespace is non-empty, 0.0 if empty
    - Policy Compliance: 1.0 if no policy violations, 0.5 if any, 0.0 if critical
    - Dependency Integrity: 1.0 if dependencies resolved, 0.5 if unresolved
    - Search Result Quality: 1.0 if results exist, 0.5 if no results, 0.0 if error
    Overall confidence is the average of all seven dimensions.
    """

    def calculate(
        self,
        entry: RegistryEntry | None = None,
        validation_violations: list[str] | None = None,
        policy_violations: list[str] | None = None,
        dependencies_resolved: bool = True,
        search_result_count: int | None = None,
        explainability: RegistryExplainabilityMetadata | None = None,
    ) -> RegistryConfidence:
        """Calculate a confidence assessment for a registry decision.

        Args:
            entry: The registry entry being evaluated (optional).
            validation_violations: List of validation violations (empty = passed).
            policy_violations: List of policy violations (empty = passed).
            dependencies_resolved: Whether all dependencies are resolved.
            search_result_count: Number of search results (None = not a search).
            explainability: Optional explainability metadata to enrich.

        Returns:
            A RegistryConfidence with scores for all seven dimensions.
        """
        log.info("registry_confidence.calculate")

        metadata_completeness = self._calculate_metadata_completeness(entry)
        validation_quality = self._calculate_validation_quality(validation_violations)
        version_correctness = self._calculate_version_correctness(entry)
        namespace_validity = self._calculate_namespace_validity(entry)
        policy_compliance = self._calculate_policy_compliance(policy_violations)
        dependency_integrity = self._calculate_dependency_integrity(dependencies_resolved)
        search_result_quality = self._calculate_search_result_quality(search_result_count)

        scores = [
            metadata_completeness,
            validation_quality,
            version_correctness,
            namespace_validity,
            policy_compliance,
            dependency_integrity,
            search_result_quality,
        ]
        overall_confidence = sum(scores) / len(scores) if scores else 0.0

        return RegistryConfidence(
            overall_confidence=round(overall_confidence, 4),
            metadata_completeness=metadata_completeness,
            validation_quality=validation_quality,
            version_correctness=version_correctness,
            namespace_validity=namespace_validity,
            policy_compliance=policy_compliance,
            dependency_integrity=dependency_integrity,
            search_result_quality=search_result_quality,
        )

    def _calculate_metadata_completeness(self, entry: RegistryEntry | None) -> float:
        """Score based on how many optional metadata fields are populated."""
        if entry is None:
            return 0.0
        fields = [
            bool(entry.name),
            bool(entry.version),
            bool(entry.owner_id),
            bool(entry.namespace),
            bool(entry.tags),
            bool(entry.metadata),
        ]
        filled = sum(1 for f in fields if f)
        return round(filled / len(fields), 4) if fields else 0.0

    def _calculate_validation_quality(self, violations: list[str] | None) -> float:
        """Score based on validation results."""
        if violations is None:
            return 1.0
        if not violations:
            return 1.0
        critical_keywords = ["invalid", "required", "forbidden", "not allowed"]
        has_critical = any(
            any(kw in v.lower() for kw in critical_keywords)
            for v in violations
        )
        if has_critical:
            return 0.0
        return 0.5

    def _calculate_version_correctness(self, entry: RegistryEntry | None) -> float:
        """Score based on whether the version looks valid (semver-like)."""
        if entry is None or not entry.version:
            return 0.0
        import re
        if re.match(r"^\d+\.\d+\.\d+", entry.version):
            return 1.0
        return 0.5

    def _calculate_namespace_validity(self, entry: RegistryEntry | None) -> float:
        """Score based on namespace validity."""
        if entry is None:
            return 0.0
        if not entry.namespace:
            return 0.0
        import re
        if re.match(r"^[a-zA-Z0-9_-]+$", entry.namespace):
            return 1.0
        return 0.5

    def _calculate_policy_compliance(self, violations: list[str] | None) -> float:
        """Score based on policy compliance."""
        if violations is None:
            return 1.0
        if not violations:
            return 1.0
        critical_keywords = ["not allowed", "forbidden", "blocked", "denied"]
        has_critical = any(
            any(kw in v.lower() for kw in critical_keywords)
            for v in violations
        )
        if has_critical:
            return 0.0
        return 0.5

    def _calculate_dependency_integrity(self, resolved: bool) -> float:
        """Score based on dependency resolution status."""
        return 1.0 if resolved else 0.5

    def _calculate_search_result_quality(self, result_count: int | None) -> float:
        """Score based on search result count.

        Returns:
            1.0 if results exist (count > 0),
            0.5 if no results (count == 0),
            1.0 if result_count is None (not a search operation, neutral).
        """
        if result_count is None:
            return 1.0
        if result_count > 0:
            return 1.0
        return 0.5
