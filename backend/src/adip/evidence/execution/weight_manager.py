"""EvidenceWeightManager — deterministic weight calculation.

Calculates and manages weights for evidence items based on
quality, trust, freshness, and correlation dimensions.
Placeholder implementation using simple heuristics.
"""

from __future__ import annotations

import structlog

log = structlog.get_logger(__name__)


class EvidenceWeightManager:
    """Manages weight calculation, normalization, and aggregation.

    Deterministic placeholder that assigns weights to evidence
    based on quality, trust, freshness, and correlation scores.
    """

    def calculate_weight(
        self,
        quality_score: float | None = None,
        trust_score: float | None = None,
        freshness_score: float | None = None,
        correlation_score: float | None = None,
    ) -> float:
        """Calculate a weight for evidence based on input dimensions.

        Weight is the average of all provided dimension scores.
        Unprovided dimensions default to 0.5.

        Args:
            quality_score: Quality score (0.0–1.0), optional.
            trust_score: Trust score (0.0–1.0), optional.
            freshness_score: Freshness score (0.0–1.0), optional.
            correlation_score: Correlation score (0.0–1.0), optional.

        Returns:
            Calculated weight (0.0–1.0).
        """
        scores = [
            quality_score if quality_score is not None else 0.5,
            trust_score if trust_score is not None else 0.5,
            freshness_score if freshness_score is not None else 0.5,
            correlation_score if correlation_score is not None else 0.5,
        ]
        return round(sum(scores) / len(scores), 4) if scores else 0.0

    def normalize_weights(
        self,
        weights: dict[str, float],
    ) -> dict[str, float]:
        """Normalize a dict of weights so they sum to 1.0.

        Args:
            weights: Map of evidence_id to raw weight (0.0–1.0).

        Returns:
            Normalized weights summing to 1.0.
        """
        total = sum(weights.values())
        if total == 0.0:
            return {k: 0.0 for k in weights}
        return {k: round(v / total, 4) for k, v in weights.items()}

    def aggregate_weights(
        self,
        weight_groups: list[dict[str, float]],
    ) -> dict[str, float]:
        """Aggregate multiple weight groups by averaging.

        Args:
            weight_groups: List of weight dicts to aggregate.

        Returns:
            Aggregated weights (average across groups).
        """
        if not weight_groups:
            return {}
        all_keys: set[str] = set()
        for group in weight_groups:
            all_keys.update(group.keys())
        result: dict[str, list[float]] = {k: [] for k in all_keys}
        for group in weight_groups:
            for k in all_keys:
                result[k].append(group.get(k, 0.0))
        return {
            k: round(sum(v) / len(v), 4) for k, v in result.items()
        }

    def get_weight_explainability(
        self,
        quality_score: float | None = None,
        trust_score: float | None = None,
        freshness_score: float | None = None,
        correlation_score: float | None = None,
    ) -> list[str]:
        """Generate explainability strings for weight assignment.

        Args:
            quality_score: Quality score (0.0–1.0), optional.
            trust_score: Trust score (0.0–1.0), optional.
            freshness_score: Freshness score (0.0–1.0), optional.
            correlation_score: Correlation score (0.0–1.0), optional.

        Returns:
            List of human-readable reasons for the weight.
        """
        reasons: list[str] = []
        if quality_score is not None:
            reasons.append(f"Quality contribution: {quality_score:.2f}")
        if trust_score is not None:
            reasons.append(f"Trust contribution: {trust_score:.2f}")
        if freshness_score is not None:
            reasons.append(f"Freshness contribution: {freshness_score:.2f}")
        if correlation_score is not None:
            reasons.append(f"Correlation contribution: {correlation_score:.2f}")
        return reasons or ["Default weight applied (no dimensions provided)"]
