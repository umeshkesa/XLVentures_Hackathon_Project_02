"""DecisionJustification — builds justifications for decisions.

Assembles supporting evidence, rules, constraints, assumptions,
risks, and alternatives into a structured justification model.
Deterministic placeholder implementation.
"""

from __future__ import annotations

from typing import Any

import structlog

from adip.reasoning.execution.models import (
    DecisionJustificationModel,
    ReasoningAlternative,
    RiskAssessment,
)

log = structlog.get_logger(__name__)


class DecisionJustification:
    """Builds justifications for decisions.

    Deterministic placeholder that collects evidence, rules,
    constraints, assumptions, risks, and alternatives to
    produce a structured justification model.
    """

    def __init__(self) -> None:
        self._evidence: list[dict[str, Any]] = []
        self._rules: list[dict[str, Any]] = []
        self._constraints: list[dict[str, Any]] = []
        self._assumptions: list[dict[str, Any]] = []
        self._risks: list[dict[str, Any]] = []
        self._alternatives: list[dict[str, Any]] = []
        self._selected: dict[str, Any] | None = None

    def add_supporting_evidence(
        self,
        evidence_ids: list[str],
        descriptions: list[str] | None = None,
    ) -> None:
        """Add supporting evidence items.

        Args:
            evidence_ids: List of evidence IDs.
            descriptions: Optional list of descriptions, one per evidence ID.
        """
        for i, eid in enumerate(evidence_ids):
            desc = descriptions[i] if descriptions and i < len(descriptions) else ""
            self._evidence.append({"evidence_id": eid, "description": desc})
        log.info("decision_justification.add_evidence", count=len(evidence_ids))

    def add_rule_used(
        self,
        rule_id: str,
        rule_description: str,
    ) -> None:
        """Add a rule used in the decision.

        Args:
            rule_id: The rule identifier.
            rule_description: Description of the rule.
        """
        self._rules.append({"rule_id": rule_id, "description": rule_description})
        log.info("decision_justification.add_rule", rule_id=rule_id)

    def add_constraint_used(
        self,
        constraint_id: str,
        constraint_description: str,
    ) -> None:
        """Add a constraint used in the decision.

        Args:
            constraint_id: The constraint identifier.
            constraint_description: Description of the constraint.
        """
        self._constraints.append(
            {"constraint_id": constraint_id, "description": constraint_description}
        )
        log.info("decision_justification.add_constraint", constraint_id=constraint_id)

    def add_assumption_used(
        self,
        assumption_id: str,
        assumption_description: str,
    ) -> None:
        """Add an assumption used in the decision.

        Args:
            assumption_id: The assumption identifier.
            assumption_description: Description of the assumption.
        """
        self._assumptions.append(
            {"assumption_id": assumption_id, "description": assumption_description}
        )
        log.info("decision_justification.add_assumption", assumption_id=assumption_id)

    def add_risk_assessed(
        self,
        risk: RiskAssessment,
    ) -> None:
        """Add a risk assessment.

        Args:
            risk: The RiskAssessment to add.
        """
        self._risks.append({
            "risk_id": risk.risk_id,
            "risk_type": risk.risk_type,
            "score": risk.score,
            "level": risk.level,
            "description": risk.description,
        })
        log.info("decision_justification.add_risk", risk_id=risk.risk_id)

    def add_alternative(
        self,
        alternative: ReasoningAlternative,
        was_selected: bool = False,
    ) -> None:
        """Add a decision alternative.

        Args:
            alternative: The ReasoningAlternative to add.
            was_selected: Whether this alternative was selected.
        """
        alt_data = {
            "alternative_id": str(alternative.alternative_id),
            "description": alternative.decision_description,
            "confidence": alternative.confidence,
            "status": str(alternative.status),
            "score": alternative.score,
        }
        self._alternatives.append(alt_data)
        if was_selected:
            self._selected = alt_data
        log.info("decision_justification.add_alternative", alt_id=str(alternative.alternative_id))

    def build_justification(self) -> DecisionJustificationModel:
        """Assemble all data into a DecisionJustificationModel.

        Returns:
            A DecisionJustificationModel with all collected data.
        """
        model = DecisionJustificationModel(
            supporting_evidence=self._evidence,
            rules_used=self._rules,
            constraints_used=self._constraints,
            assumptions_used=self._assumptions,
            risks_assessed=self._risks,
            alternatives=self._alternatives,
            selected_alternative=self._selected,
        )
        log.info(
            "decision_justification.build",
            justification_id=model.justification_id,
            evidence_count=len(self._evidence),
            rules_count=len(self._rules),
        )
        return model

    def clear(self) -> None:
        """Clear all collected justification data."""
        self._evidence.clear()
        self._rules.clear()
        self._constraints.clear()
        self._assumptions.clear()
        self._risks.clear()
        self._alternatives.clear()
        self._selected = None

    def count(self) -> int:
        """Get the total number of justification items.

        Returns:
            Total count of all items collected.
        """
        return (
            len(self._evidence)
            + len(self._rules)
            + len(self._constraints)
            + len(self._assumptions)
            + len(self._risks)
            + len(self._alternatives)
        )
