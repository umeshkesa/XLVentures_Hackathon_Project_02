"""ReviewerConsensusManager — manages reviewer consensus.

Supports Majority, Unanimous, Weighted, and Conflict consensus
modes for multi-reviewer governance. Deterministic placeholder.
"""

from __future__ import annotations

import uuid
from enum import StrEnum

import structlog

log = structlog.get_logger(__name__)


class ConsensusMode(StrEnum):
    MAJORITY = "MAJORITY"
    UNANIMOUS = "UNANIMOUS"
    WEIGHTED = "WEIGHTED"
    CONFLICT = "CONFLICT"


class ConsensusResult:
    """Result of a consensus evaluation."""

    def __init__(
        self,
        consensus_mode: ConsensusMode,
        agreement: float,
        votes_for: int,
        votes_against: int,
        votes_total: int,
        outcome: str,
        details: str = "",
    ) -> None:
        self.consensus_id = str(uuid.uuid4())
        self.consensus_mode = consensus_mode
        self.agreement = agreement
        self.votes_for = votes_for
        self.votes_against = votes_against
        self.votes_total = votes_total
        self.outcome = outcome
        self.details = details


class ReviewerConsensusManager:
    """Manages reviewer consensus evaluation.

    Supports four consensus modes:
    - MAJORITY: simple majority (>50%) decides
    - UNANIMOUS: all reviewers must agree
    - WEIGHTED: weighted by reviewer expertise/authority
    - CONFLICT: reports disagreement without resolution

    Deterministic placeholder implementation.
    """

    def __init__(self) -> None:
        self._results: dict[str, ConsensusResult] = {}

    def evaluate_majority(
        self,
        review_id: str,
        votes_for: int,
        votes_against: int,
        correlation_id: str = "",
    ) -> ConsensusResult:
        """Evaluate using majority consensus.

        Majority requires >50% of votes in favour.

        Args:
            review_id: The review identifier.
            votes_for: Number of votes in favour.
            votes_against: Number of votes against.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            ConsensusResult with majority outcome.
        """
        total = votes_for + votes_against
        agreement = round(votes_for / total, 4) if total > 0 else 0.0
        outcome = "APPROVED" if agreement > 0.5 else "REJECTED"
        result = ConsensusResult(
            consensus_mode=ConsensusMode.MAJORITY,
            agreement=agreement,
            votes_for=votes_for,
            votes_against=votes_against,
            votes_total=total,
            outcome=outcome,
            details=f"Majority consensus: {votes_for}/{total} in favour ({agreement:.1%})",
        )
        self._results[review_id] = result
        log.info(
            "consensus.majority",
            review_id=review_id,
            agreement=agreement,
            outcome=outcome,
            correlation_id=correlation_id,
        )
        return result

    def evaluate_unanimous(
        self,
        review_id: str,
        votes_for: int,
        votes_against: int,
        correlation_id: str = "",
    ) -> ConsensusResult:
        """Evaluate using unanimous consensus.

        Unanimous requires all votes in favour.

        Args:
            review_id: The review identifier.
            votes_for: Number of votes in favour.
            votes_against: Number of votes against.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            ConsensusResult with unanimous outcome.
        """
        total = votes_for + votes_against
        agreement = 1.0 if votes_against == 0 and total > 0 else 0.0
        outcome = "APPROVED" if agreement == 1.0 else "REJECTED"
        result = ConsensusResult(
            consensus_mode=ConsensusMode.UNANIMOUS,
            agreement=agreement,
            votes_for=votes_for,
            votes_against=votes_against,
            votes_total=total,
            outcome=outcome,
            details=(
                "Unanimous approval"
                if outcome == "APPROVED"
                else f"Not unanimous: {votes_against} vote(s) against"
            ),
        )
        self._results[review_id] = result
        log.info(
            "consensus.unanimous",
            review_id=review_id,
            agreement=agreement,
            outcome=outcome,
            correlation_id=correlation_id,
        )
        return result

    def evaluate_weighted(
        self,
        review_id: str,
        votes_for: list[float],
        votes_against: list[float],
        correlation_id: str = "",
    ) -> ConsensusResult:
        """Evaluate using weighted consensus.

        Each vote carries a weight (e.g., expertise score).
        The sum of for-weights vs against-weights decides.

        Args:
            review_id: The review identifier.
            votes_for: List of weights for votes in favour.
            votes_against: List of weights for votes against.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            ConsensusResult with weighted outcome.
        """
        weight_for = sum(votes_for)
        weight_against = sum(votes_against)
        total_weight = weight_for + weight_against
        agreement = round(weight_for / total_weight, 4) if total_weight > 0 else 0.0
        outcome = "APPROVED" if agreement > 0.5 else "REJECTED"
        result = ConsensusResult(
            consensus_mode=ConsensusMode.WEIGHTED,
            agreement=agreement,
            votes_for=len(votes_for),
            votes_against=len(votes_against),
            votes_total=len(votes_for) + len(votes_against),
            outcome=outcome,
            details=(
                f"Weighted consensus: for_weight={weight_for:.2f}, "
                f"against_weight={weight_against:.2f}, agreement={agreement:.1%}"
            ),
        )
        self._results[review_id] = result
        log.info(
            "consensus.weighted",
            review_id=review_id,
            agreement=agreement,
            outcome=outcome,
            correlation_id=correlation_id,
        )
        return result

    def evaluate_conflict(
        self,
        review_id: str,
        votes_for: int,
        votes_against: int,
        correlation_id: str = "",
    ) -> ConsensusResult:
        """Evaluate as conflict (ties or unresolvable disagreement).

        Args:
            review_id: The review identifier.
            votes_for: Number of votes in favour.
            votes_against: Number of votes against.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            ConsensusResult with CONFLICT outcome.
        """
        total = votes_for + votes_against
        agreement = round(votes_for / total, 4) if total > 0 else 0.0
        result = ConsensusResult(
            consensus_mode=ConsensusMode.CONFLICT,
            agreement=agreement,
            votes_for=votes_for,
            votes_against=votes_against,
            votes_total=total,
            outcome="CONFLICT",
            details=f"Conflict detected: {votes_for} for, {votes_against} against",
        )
        self._results[review_id] = result
        log.info(
            "consensus.conflict",
            review_id=review_id,
            agreement=agreement,
            correlation_id=correlation_id,
        )
        return result

    def get_result(self, review_id: str) -> ConsensusResult | None:
        """Get the consensus result for a review.

        Args:
            review_id: The review identifier.

        Returns:
            ConsensusResult if found, None otherwise.
        """
        return self._results.get(review_id)

    def clear(self) -> None:
        """Clear all consensus results."""
        self._results.clear()
