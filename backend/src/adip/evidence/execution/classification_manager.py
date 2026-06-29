"""Evidence classification manager.

Classifies evidence based on its type and contents.
"""

from __future__ import annotations

from adip.evidence.contracts.models import Evidence
from adip.evidence.enums import EvidenceClassification, EvidenceType


class EvidenceClassificationManager:
    """Classifies evidence into predefined categories.

    Deterministic placeholder that maps evidence types to
    classifications.
    """

    TYPE_CLASSIFICATION_MAP: dict[EvidenceType, EvidenceClassification] = {
        EvidenceType.SENSOR: EvidenceClassification.REAL_TIME,
        EvidenceType.MEMORY: EvidenceClassification.HISTORICAL,
        EvidenceType.KNOWLEDGE: EvidenceClassification.PRIMARY,
        EvidenceType.RULE: EvidenceClassification.DERIVED,
        EvidenceType.PLANNER: EvidenceClassification.PREDICTIVE,
        EvidenceType.REPORT: EvidenceClassification.SECONDARY,
        EvidenceType.WORKFLOW: EvidenceClassification.SECONDARY,
        EvidenceType.INCIDENT: EvidenceClassification.SECONDARY,
        EvidenceType.MAINTENANCE: EvidenceClassification.HISTORICAL,
        EvidenceType.CUSTOMER: EvidenceClassification.SECONDARY,
        EvidenceType.CRM: EvidenceClassification.SECONDARY,
        EvidenceType.EMAIL: EvidenceClassification.SECONDARY,
    }

    def classify(self, evidence: Evidence) -> EvidenceClassification:
        """Classify evidence based on its type.

        Args:
            evidence: The evidence to classify.

        Returns:
            The determined classification.
        """
        return self.TYPE_CLASSIFICATION_MAP.get(
            evidence.evidence_type, EvidenceClassification.SECONDARY,
        )
