"""ReasoningMemory — stores intermediate reasoning states and results.

Provides key-value storage for reasoning context, alternatives,
risks, impacts, uncertainties, decisions, and comparisons.
Deterministic placeholder implementation.
"""

from __future__ import annotations

from typing import Any

import structlog

from adip.reasoning.execution.models import (
    DecisionComparison,
    ImpactAssessment,
    MemoryEntry,
    RiskAssessment,
    UncertaintyAnalysis,
)

log = structlog.get_logger(__name__)


class ReasoningMemory:
    """Stores and retrieves intermediate reasoning states.

    Deterministic placeholder that maintains in-memory key-value
    storage organised by reasoning ID and entry type.
    """

    def __init__(self) -> None:
        self._entries: dict[str, MemoryEntry] = {}

    def store(
        self,
        key: str,
        entry_type: str,
        data: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> MemoryEntry:
        """Store a memory entry.

        Args:
            key: Unique key for the entry.
            entry_type: Type of entry (context, alternative, risk, etc.).
            data: Data payload for the entry.
            metadata: Additional metadata.

        Returns:
            The created MemoryEntry.
        """
        entry = MemoryEntry(
            key=key,
            entry_type=entry_type,
            data=data or {},
            metadata=metadata or {},
        )
        self._entries[key] = entry
        log.info(
            "reasoning_memory.store",
            key=key,
            entry_type=entry_type,
        )
        return entry

    def store_alternatives(
        self,
        reasoning_id: str,
        alternatives: list,
    ) -> MemoryEntry:
        """Store decision alternatives in memory.

        Args:
            reasoning_id: The reasoning operation ID.
            alternatives: List of alternatives to store.

        Returns:
            The created MemoryEntry.
        """
        alt_data = [
            {
                "alternative_id": str(a.alternative_id),
                "description": a.decision_description,
                "confidence": a.confidence,
            }
            for a in alternatives
        ]
        return self.store(
            key=f"{reasoning_id}:alternatives",
            entry_type="alternatives",
            data={"alternatives": alt_data, "count": len(alternatives)},
        )

    def store_risks(
        self,
        reasoning_id: str,
        risks: dict[str, RiskAssessment],
    ) -> MemoryEntry:
        """Store risk assessments in memory.

        Args:
            reasoning_id: The reasoning operation ID.
            risks: Mapping of alternative ID to RiskAssessment.

        Returns:
            The created MemoryEntry.
        """
        risk_data = {
            alt_id: {
                "risk_id": r.risk_id,
                "risk_type": r.risk_type,
                "score": r.score,
                "level": r.level,
            }
            for alt_id, r in risks.items()
        }
        return self.store(
            key=f"{reasoning_id}:risks",
            entry_type="risks",
            data={"risks": risk_data, "count": len(risks)},
        )

    def store_impacts(
        self,
        reasoning_id: str,
        impacts: dict[str, ImpactAssessment],
    ) -> MemoryEntry:
        """Store impact assessments in memory.

        Args:
            reasoning_id: The reasoning operation ID.
            impacts: Mapping of alternative ID to ImpactAssessment.

        Returns:
            The created MemoryEntry.
        """
        impact_data = {
            alt_id: {
                "impact_id": i.impact_id,
                "impact_type": i.impact_type,
                "score": i.score,
                "quantitative_value": i.quantitative_value,
            }
            for alt_id, i in impacts.items()
        }
        return self.store(
            key=f"{reasoning_id}:impacts",
            entry_type="impacts",
            data={"impacts": impact_data, "count": len(impacts)},
        )

    def store_uncertainties(
        self,
        reasoning_id: str,
        uncertainties: list[UncertaintyAnalysis],
    ) -> MemoryEntry:
        """Store uncertainty analyses in memory.

        Args:
            reasoning_id: The reasoning operation ID.
            uncertainties: List of UncertaintyAnalysis.

        Returns:
            The created MemoryEntry.
        """
        unc_data = [
            {
                "uncertainty_id": u.uncertainty_id,
                "uncertainty_type": u.uncertainty_type,
                "criticality": u.criticality,
                "source": u.source,
            }
            for u in uncertainties
        ]
        return self.store(
            key=f"{reasoning_id}:uncertainties",
            entry_type="uncertainties",
            data={"uncertainties": unc_data, "count": len(uncertainties)},
        )

    def store_decisions(
        self,
        reasoning_id: str,
        comparisons: list[DecisionComparison],
        best: object | None = None,
    ) -> MemoryEntry:
        """Store decision comparisons in memory.

        Args:
            reasoning_id: The reasoning operation ID.
            comparisons: List of DecisionComparison.
            best: The best alternative (if any).

        Returns:
            The created MemoryEntry.
        """
        comp_data = [
            {
                "comparison_id": c.comparison_id,
                "alternative_id": c.alternative_id,
                "composite_score": c.composite_score,
            }
            for c in comparisons
        ]
        return self.store(
            key=f"{reasoning_id}:decisions",
            entry_type="decisions",
            data={
                "comparisons": comp_data,
                "count": len(comparisons),
                "best_id": str(best) if best else None,
            },
        )

    def retrieve(self, key: str) -> MemoryEntry | None:
        """Retrieve a memory entry by key.

        Args:
            key: The entry key.

        Returns:
            The MemoryEntry if found, else None.
        """
        return self._entries.get(key)

    def retrieve_by_type(self, entry_type: str) -> list[MemoryEntry]:
        """Retrieve all entries of a given type.

        Args:
            entry_type: The entry type to filter by.

        Returns:
            List of matching MemoryEntry objects.
        """
        return [e for e in self._entries.values() if e.entry_type == entry_type]

    def count(self) -> int:
        """Get the total number of stored entries.

        Returns:
            Entry count.
        """
        return len(self._entries)

    def clear(self) -> None:
        """Clear all stored memory entries."""
        self._entries.clear()
