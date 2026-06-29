"""ConflictResolutionManager — deterministic conflict resolution for reviews.

Resolves conflicts between reviews or reviewers via voting,
tie-breaking, and split-decision logic for the Decision Review Layer.
"""

from __future__ import annotations

from typing import Any

import structlog

from adip.review.execution.models import ConflictResolutionResult

log = structlog.get_logger(__name__)


class ConflictResolutionManager:
    """In-memory conflict resolution manager for review operations."""

    def __init__(self) -> None:
        self._conflicts: list[ConflictResolutionResult] = []

    def resolve_conflicting_reviews(
        self,
        review_ids: list[str],
        votes_for: int,
        votes_against: int,
        conflict_type: str = "",
        correlation_id: str = "",
    ) -> ConflictResolutionResult:
        """Resolve a conflict between reviews by vote count.

        - votes_for > votes_against -> APPROVED
        - votes_against > votes_for -> REJECTED
        - equal -> tie (delegates to resolve_tie)
        """
        outcome = ""
        resolution = ""

        if votes_for > votes_against:
            outcome = "APPROVED"
            resolution = (
                f"Conflict resolved by majority vote ({votes_for} for / "
                f"{votes_against} against): APPROVED"
            )
        elif votes_against > votes_for:
            outcome = "REJECTED"
            resolution = (
                f"Conflict resolved by majority vote ({votes_against} against / "
                f"{votes_for} for): REJECTED"
            )
        else:
            tie_result = self.resolve_tie_vote(
                review_ids, tie_breaker_role="MANAGER", correlation_id=correlation_id
            )
            outcome = tie_result.outcome
            resolution = tie_result.resolution

        result = ConflictResolutionResult(
            review_ids=review_ids,
            conflict_type=conflict_type,
            votes_for=votes_for,
            votes_against=votes_against,
            tie_broken=(votes_for == votes_against),
            outcome=outcome,
            resolution=resolution,
        )
        self._conflicts.append(result)
        log.info(
            "conflict_resolver.resolve_conflicting_reviews",
            conflict_id=str(result.conflict_id),
            outcome=outcome,
            votes_for=votes_for,
            votes_against=votes_against,
            correlation_id=correlation_id,
        )
        return result

    def resolve_tie_vote(
        self,
        review_ids: list[str],
        tie_breaker_role: str = "MANAGER",
        correlation_id: str = "",
    ) -> ConflictResolutionResult:
        """Resolve a tied vote using a tie-breaker role."""
        result = ConflictResolutionResult(
            review_ids=review_ids,
            conflict_type="vote_standoff",
            votes_for=0,
            votes_against=0,
            tie_broken=True,
            tie_breaker_role=tie_breaker_role,
            outcome="TIE_BROKEN",
            resolution=f"Tie broken by {tie_breaker_role} role",
        )
        self._conflicts.append(result)
        log.info(
            "conflict_resolver.resolve_tie_vote",
            conflict_id=str(result.conflict_id),
            tie_breaker_role=tie_breaker_role,
            correlation_id=correlation_id,
        )
        return result

    def resolve_split_decision(
        self,
        decisions: list[dict[str, Any]],
        correlation_id: str = "",
    ) -> ConflictResolutionResult:
        """Resolve a split decision by picking the majority outcome.

        Each decision dict must have an 'outcome' key. The outcome
        with the highest count is selected as the result.
        """
        counts: dict[str, int] = {}
        for d in decisions:
            outcome = d.get("outcome", "")
            counts[outcome] = counts.get(outcome, 0) + 1

        majority_outcome = max(counts, key=counts.get) if counts else "UNDETERMINED"
        result = ConflictResolutionResult(
            review_ids=[d.get("review_id", "") for d in decisions],
            conflict_type="split_decision",
            votes_for=counts.get(majority_outcome, 0),
            votes_against=sum(v for k, v in counts.items() if k != majority_outcome),
            tie_broken=False,
            outcome=majority_outcome,
            resolution=(
                f"Split decision resolved: majority chose '{majority_outcome}' "
                f"({counts.get(majority_outcome, 0)} out of {len(decisions)})"
            ),
        )
        self._conflicts.append(result)
        log.info(
            "conflict_resolver.resolve_split_decision",
            conflict_id=str(result.conflict_id),
            outcome=majority_outcome,
            total_decisions=len(decisions),
            correlation_id=correlation_id,
        )
        return result

    def get_conflicts(self, review_id: str) -> list[ConflictResolutionResult]:
        """Return all conflicts involving a specific review."""
        return [c for c in self._conflicts if review_id in c.review_ids]

    def get_all_conflicts(self) -> list[ConflictResolutionResult]:
        """Return all conflict resolution results."""
        return list(self._conflicts)

    def clear(self) -> None:
        """Clear all conflict records."""
        self._conflicts.clear()
        log.info("conflict_resolver.clear")
