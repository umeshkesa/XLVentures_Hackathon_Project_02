"""Evidence priority assignment.

Assigns priority to evidence based on its type and characteristics.
"""

from __future__ import annotations

from adip.evidence.contracts.models import Evidence
from adip.evidence.enums import EvidencePriority, EvidenceType


class EvidencePriorityAssigner:
    """Assigns priority levels to evidence.

    Deterministic placeholder that maps evidence types to priority levels.
    """

    TYPE_PRIORITY_MAP: dict[EvidenceType, EvidencePriority] = {
        EvidenceType.SENSOR: EvidencePriority.HIGH,
        EvidenceType.MEMORY: EvidencePriority.MEDIUM,
        EvidenceType.KNOWLEDGE: EvidencePriority.HIGH,
        EvidenceType.RULE: EvidencePriority.MEDIUM,
        EvidenceType.PLANNER: EvidencePriority.CRITICAL,
        EvidenceType.REPORT: EvidencePriority.LOW,
        EvidenceType.WORKFLOW: EvidencePriority.MEDIUM,
        EvidenceType.INCIDENT: EvidencePriority.CRITICAL,
        EvidenceType.MAINTENANCE: EvidencePriority.LOW,
        EvidenceType.CUSTOMER: EvidencePriority.MEDIUM,
        EvidenceType.CRM: EvidencePriority.LOW,
        EvidenceType.EMAIL: EvidencePriority.INFORMATIONAL,
    }

    def assign_priority(self, evidence: Evidence) -> EvidencePriority:
        """Assign priority to evidence based on its type.

        Args:
            evidence: The evidence to assign priority to.

        Returns:
            The assigned priority level.
        """
        return self.TYPE_PRIORITY_MAP.get(evidence.evidence_type, EvidencePriority.MEDIUM)
