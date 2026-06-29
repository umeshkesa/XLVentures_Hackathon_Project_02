"""PluginConfidenceCalculator — computes confidence and quality scores.

Produces PluginConfidence from manifest quality, dependency completeness,
compatibility score, sandbox readiness, lifecycle validity, and
configuration quality. Placeholder implementation using deterministic
heuristics.
"""

from __future__ import annotations

import structlog

from adip.plugins.contracts.models import Plugin, PluginConfidence

log = structlog.get_logger(__name__)


class PluginConfidenceCalculator:
    """Computes confidence metrics for plugin lifecycle decisions."""

    def calculate(self, plugin: Plugin) -> PluginConfidence:
        """Calculate confidence metrics for a plugin.

        Uses deterministic placeholder heuristics:
        - manifest_quality: based on manifest presence and field completeness
        - dependency_completeness: based on dependency resolution status
        - compatibility_score: based on version presence
        - sandbox_readiness: based on namespace and status
        - lifecycle_validity: based on lifecycle status appropriateness
        - configuration_quality: based on plugin metadata completeness
        - overall: weighted average of all sub-scores
        """
        log.info("plugin_confidence.calculate", plugin=plugin.name)

        manifest_quality = self._calculate_manifest_quality(plugin)
        dependency_completeness = self._calculate_dependency_completeness(plugin)
        compatibility_score = self._calculate_compatibility_score(plugin)
        sandbox_readiness = self._calculate_sandbox_readiness(plugin)
        lifecycle_validity = self._calculate_lifecycle_validity(plugin)
        configuration_quality = self._calculate_configuration_quality(plugin)

        signature_status = self._calculate_signature_status(plugin)

        overall = (
            manifest_quality * 0.18
            + dependency_completeness * 0.18
            + compatibility_score * 0.14
            + sandbox_readiness * 0.14
            + lifecycle_validity * 0.14
            + configuration_quality * 0.12
            + (1.0 if signature_status == "verified" else 0.5 if signature_status == "unverified" else 0.0) * 0.10
        )

        confidence = PluginConfidence(
            overall_confidence=round(overall, 4),
            manifest_quality=round(manifest_quality, 4),
            dependency_completeness=round(dependency_completeness, 4),
            compatibility_score=round(compatibility_score, 4),
            sandbox_readiness=round(sandbox_readiness, 4),
            lifecycle_validity=round(lifecycle_validity, 4),
            configuration_quality=round(configuration_quality, 4),
            signature_status=signature_status,
        )

        log.info(
            "plugin_confidence.calculated",
            plugin=plugin.name,
            overall=confidence.overall_confidence,
        )
        return confidence

    def _calculate_manifest_quality(self, plugin: Plugin) -> float:
        """Score manifest quality based on field completeness."""
        if not plugin.manifest:
            return 0.0

        score = 0.0
        if plugin.manifest.plugin_name.strip():
            score += 0.2
        if plugin.manifest.plugin_version.strip():
            score += 0.2
        if plugin.manifest.plugin_type is not None:
            score += 0.2
        if plugin.manifest.capabilities:
            score += 0.2
        if plugin.manifest.dependencies:
            score += 0.1
        score += 0.1  # base score
        return min(1.0, score)

    def _calculate_dependency_completeness(self, plugin: Plugin) -> float:
        """Score dependency completeness."""
        if not plugin.manifest or not plugin.manifest.dependencies:
            return 1.0  # no deps = fully complete
        resolved = sum(1 for d in plugin.manifest.dependencies if d.status == "satisfied")
        return resolved / len(plugin.manifest.dependencies)

    def _calculate_compatibility_score(self, plugin: Plugin) -> float:
        """Score compatibility based on version presence."""
        if not plugin.version.strip():
            return 0.0
        return 1.0

    def _calculate_sandbox_readiness(self, plugin: Plugin) -> float:
        """Score sandbox readiness."""
        score = 0.0
        if plugin.namespace.strip():
            score += 0.5
        if plugin.status in (
            plugin.status.__class__.LOADED,
            plugin.status.__class__.INITIALIZED,
            plugin.status.__class__.ACTIVE,
        ):
            score += 0.5
        return score

    def _calculate_lifecycle_validity(self, plugin: Plugin) -> float:
        """Score lifecycle validity based on status progression."""
        higher_statuses = {
            "VALIDATED": 0.2,
            "INSTALLED": 0.3,
            "LOADED": 0.5,
            "INITIALIZED": 0.7,
            "ACTIVE": 1.0,
        }
        return higher_statuses.get(plugin.status.value, 0.1)

    def _calculate_configuration_quality(self, plugin: Plugin) -> float:
        """Score configuration quality."""
        score = 0.3
        if plugin.tags:
            score += 0.2
        if plugin.owner_id:
            score += 0.2
        if plugin.metadata and plugin.metadata.load_count > 0:
            score += 0.3
        return min(1.0, score)

    def _calculate_signature_status(self, plugin: Plugin) -> str:
        """Determine signature status for a plugin.

        Placeholder — always returns 'unknown' as no real
        signature verification is implemented.
        """
        return "unknown"
