"""UncertaintyManager — tracks and analyzes uncertainties in reasoning.

Manages sources of uncertainty: missing evidence, ambiguous data,
conflicting information, and unknown variables.
Deterministic placeholder implementation.
"""

from __future__ import annotations

import structlog

from adip.reasoning.execution.models import UncertaintyAnalysis

log = structlog.get_logger(__name__)


class UncertaintyManager:
    """Tracks uncertainties during reasoning.

    Deterministic placeholder that identifies and analyzes
    uncertainty sources based on missing information and
    unresolved contradictions.
    """

    def __init__(self) -> None:
        self._uncertainties: list[UncertaintyAnalysis] = []

    def identify_missing_info(
        self,
        expected_count: int = 0,
        actual_count: int = 0,
        description: str = "",
    ) -> UncertaintyAnalysis:
        """Identify uncertainty from missing information.

        Args:
            expected_count: Expected number of evidence items.
            actual_count: Actual number of evidence items.
            description: Description of the missing information.

        Returns:
            An UncertaintyAnalysis for the missing info.
        """
        gap = max(0, expected_count - actual_count)
        criticality = min(1.0, gap / max(1, expected_count))

        analysis = UncertaintyAnalysis(
            uncertainty_type="missing_information",
            description=description or f"Missing {gap} of {expected_count} expected evidence items",
            criticality=round(criticality, 4),
            source="evidence_gap",
            details={
                "expected_count": expected_count,
                "actual_count": actual_count,
                "gap": gap,
            },
        )
        self._uncertainties.append(analysis)
        log.info(
            "uncertainty_manager.missing_info",
            gap=gap,
            criticality=criticality,
        )
        return analysis

    def identify_unknown_variables(
        self,
        variable_count: int = 0,
        description: str = "",
    ) -> UncertaintyAnalysis:
        """Identify uncertainty from unknown variables.

        Args:
            variable_count: Number of unknown variables.
            description: Description of the unknowns.

        Returns:
            An UncertaintyAnalysis for the unknown variables.
        """
        criticality = min(1.0, variable_count * 0.2)

        analysis = UncertaintyAnalysis(
            uncertainty_type="unknown_variables",
            description=description or f"{variable_count} unknown variables identified",
            criticality=round(criticality, 4),
            source="variable_uncertainty",
            details={"variable_count": variable_count},
        )
        self._uncertainties.append(analysis)
        log.info(
            "uncertainty_manager.unknown_variables",
            count=variable_count,
            criticality=criticality,
        )
        return analysis

    def identify_conflicting_evidence(
        self,
        conflict_count: int = 0,
        total_evidence: int = 0,
        description: str = "",
    ) -> UncertaintyAnalysis:
        """Identify uncertainty from conflicting evidence.

        Args:
            conflict_count: Number of conflicting evidence pairs.
            total_evidence: Total number of evidence items.
            description: Description of the conflicts.

        Returns:
            An UncertaintyAnalysis for the conflicting evidence.
        """
        criticality = min(1.0, conflict_count / max(1, total_evidence))

        analysis = UncertaintyAnalysis(
            uncertainty_type="conflicting_evidence",
            description=description or f"{conflict_count} conflicting evidence pairs out of {total_evidence}",
            criticality=round(criticality, 4),
            source="evidence_conflict",
            details={
                "conflict_count": conflict_count,
                "total_evidence": total_evidence,
            },
        )
        self._uncertainties.append(analysis)
        log.info(
            "uncertainty_manager.conflicting_evidence",
            conflicts=conflict_count,
            criticality=criticality,
        )
        return analysis

    def track_all(
        self,
        evidence_count: int = 0,
        expected_evidence: int = 0,
        unknown_variables: int = 0,
        contradiction_count: int = 0,
    ) -> list[UncertaintyAnalysis]:
        """Run all uncertainty analyses.

        Args:
            evidence_count: Actual evidence count.
            expected_evidence: Expected evidence count.
            unknown_variables: Number of unknown variables.
            contradiction_count: Number of contradictions.

        Returns:
            List of UncertaintyAnalysis results.
        """
        results: list[UncertaintyAnalysis] = []
        results.append(self.identify_missing_info(
            expected_count=expected_evidence,
            actual_count=evidence_count,
        ))
        results.append(self.identify_unknown_variables(
            variable_count=unknown_variables,
        ))
        results.append(self.identify_conflicting_evidence(
            conflict_count=contradiction_count,
            total_evidence=max(1, evidence_count),
        ))
        log.info(
            "uncertainty_manager.track_all",
            count=len(results),
        )
        return results

    def get_uncertainties(self) -> list[UncertaintyAnalysis]:
        """Get all tracked uncertainties.

        Returns:
            List of all UncertaintyAnalysis records.
        """
        return list(self._uncertainties)

    def count(self) -> int:
        """Get the number of tracked uncertainties.

        Returns:
            Uncertainty count.
        """
        return len(self._uncertainties)

    def clear(self) -> None:
        """Clear all tracked uncertainties."""
        self._uncertainties.clear()
