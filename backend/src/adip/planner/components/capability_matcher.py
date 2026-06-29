"""Deterministic CapabilityMatcher implementation."""

from __future__ import annotations

from adip.planner.contracts.models import CapabilityMatch, PlanningContext
from adip.planner.enums import ConfidenceLevelEnum
from adip.planner.interfaces.pipeline import CapabilityMatcher


class DeterministicCapabilityMatcher(CapabilityMatcher):
    """Placeholder capability matcher using keyword scoring.

    Scores each capability based on simple substring matches against
    the task description.  Swappable for an embedding-based matcher.
    """

    _CAPABILITY_KEYWORDS: dict[str, list[str]] = {
        "data_search": ["search", "find", "lookup", "retrieve"],
        "computation": ["compute", "calculate", "math", "number"],
        "analytics": ["analyze", "analyse", "report", "statistics"],
        "summarization": ["summarise", "summarize", "condense"],
        "translation": ["translate", "convert", "language"],
    }

    async def match_capabilities(
        self, task_description: str, context: PlanningContext
    ) -> list[CapabilityMatch]:
        """Match capabilities to a task description via keyword scoring."""
        description_lower = task_description.lower()
        matches: list[CapabilityMatch] = []

        for cap in context.available_capabilities:
            keywords = self._CAPABILITY_KEYWORDS.get(cap, [])
            if not keywords:
                continue
            matches_count = sum(
                1 for kw in keywords if kw in description_lower
            )
            if matches_count > 0:
                score = min(matches_count / len(keywords), 1.0)
                if score >= 0.5:
                    confidence = ConfidenceLevelEnum.HIGH
                elif score >= 0.25:
                    confidence = ConfidenceLevelEnum.MEDIUM
                else:
                    confidence = ConfidenceLevelEnum.LOW
                matches.append(
                    CapabilityMatch(
                        capability_id=cap,
                        score=round(score, 4),
                        confidence=confidence,
                        match_details={"matched_keywords": matches_count},
                    )
                )

        matches.sort(key=lambda m: m.score, reverse=True)
        return matches
