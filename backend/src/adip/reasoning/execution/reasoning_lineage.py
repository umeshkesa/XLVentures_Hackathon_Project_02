"""ReasoningLineage — traces the lineage of a reasoning operation.

Captures the complete chain from evidence through hypotheses,
inferences, alternatives, to the final decision.
Deterministic placeholder implementation.
"""

from __future__ import annotations

from typing import Any

import structlog

from adip.reasoning.execution.models import ReasoningLineageModel

log = structlog.get_logger(__name__)


class ReasoningLineage:
    """Traces the lineage of a reasoning operation.

    Deterministic placeholder that records evidence, hypotheses,
    inferences, alternatives, and the final decision to build
    a complete lineage model.
    """

    def __init__(self) -> None:
        self._evidence: list[dict[str, Any]] = []
        self._hypotheses: list[dict[str, Any]] = []
        self._inferences: list[dict[str, Any]] = []
        self._alternatives: list[dict[str, Any]] = []
        self._final_decision: dict[str, Any] | None = None

    def add_evidence(
        self,
        evidence_id: str,
        description: str = "",
    ) -> None:
        """Add an evidence item to the lineage.

        Args:
            evidence_id: The evidence identifier.
            description: Optional description of the evidence.
        """
        self._evidence.append({"evidence_id": evidence_id, "description": description})
        log.info("reasoning_lineage.add_evidence", evidence_id=evidence_id)

    def add_hypothesis(
        self,
        hypothesis_id: str,
        description: str = "",
        confidence: float = 0.0,
    ) -> None:
        """Add a hypothesis to the lineage.

        Args:
            hypothesis_id: The hypothesis identifier.
            description: Optional description of the hypothesis.
            confidence: Confidence score for the hypothesis (0.0–1.0).
        """
        self._hypotheses.append({
            "hypothesis_id": hypothesis_id,
            "description": description,
            "confidence": confidence,
        })
        log.info("reasoning_lineage.add_hypothesis", hypothesis_id=hypothesis_id)

    def add_inference(
        self,
        inference_id: str,
        premise: str = "",
        conclusion: str = "",
    ) -> None:
        """Add an inference to the lineage.

        Args:
            inference_id: The inference identifier.
            premise: The premise of the inference.
            conclusion: The conclusion of the inference.
        """
        self._inferences.append({
            "inference_id": inference_id,
            "premise": premise,
            "conclusion": conclusion,
        })
        log.info("reasoning_lineage.add_inference", inference_id=inference_id)

    def add_alternative(
        self,
        alternative_id: str,
        description: str = "",
        score: float = 0.0,
    ) -> None:
        """Add an alternative to the lineage.

        Args:
            alternative_id: The alternative identifier.
            description: Optional description of the alternative.
            score: Evaluation score for the alternative (0.0–1.0).
        """
        self._alternatives.append({
            "alternative_id": alternative_id,
            "description": description,
            "score": score,
        })
        log.info("reasoning_lineage.add_alternative", alternative_id=alternative_id)

    def set_final_decision(
        self,
        decision_id: str,
        conclusion: str = "",
        confidence: float = 0.0,
    ) -> None:
        """Set the final decision in the lineage.

        Args:
            decision_id: The decision identifier.
            conclusion: The conclusion reached.
            confidence: Confidence in the decision (0.0–1.0).
        """
        self._final_decision = {
            "decision_id": decision_id,
            "conclusion": conclusion,
            "confidence": confidence,
        }
        log.info("reasoning_lineage.set_final_decision", decision_id=decision_id)

    def build_lineage(self) -> ReasoningLineageModel:
        """Assemble all data into a ReasoningLineageModel.

        Returns:
            A ReasoningLineageModel with the complete lineage.
        """
        model = ReasoningLineageModel(
            evidence=self._evidence,
            hypotheses=self._hypotheses,
            inferences=self._inferences,
            alternatives=self._alternatives,
            final_decision=self._final_decision,
        )
        log.info(
            "reasoning_lineage.build",
            lineage_id=model.lineage_id,
            evidence_count=len(self._evidence),
            hypothesis_count=len(self._hypotheses),
            inference_count=len(self._inferences),
        )
        return model

    def clear(self) -> None:
        """Clear all lineage data."""
        self._evidence.clear()
        self._hypotheses.clear()
        self._inferences.clear()
        self._alternatives.clear()
        self._final_decision = None

    def count(self, entity_type: str | None = None) -> int:
        """Get the count of lineage entries, optionally filtered by type.

        Args:
            entity_type: Optional entity type to filter by
                (evidence, hypothesis, inference, alternative, decision).

        Returns:
            Count of matching entries.
        """
        type_map = {
            "evidence": len(self._evidence),
            "hypothesis": len(self._hypotheses),
            "inference": len(self._inferences),
            "alternative": len(self._alternatives),
            "decision": 1 if self._final_decision else 0,
        }
        if entity_type:
            return type_map.get(entity_type, 0)
        return sum(type_map.values())
