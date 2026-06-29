"""Evidence bundling.

Groups evidence into bundles by common entities.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from adip.evidence.contracts.models import Evidence
from adip.evidence.enums import BundleType
from adip.evidence.execution.models import EvidenceBundle


class EvidenceBundleManager:
    """Manages evidence bundles.

    Deterministic placeholder for grouping evidence by common entities.
    """

    def __init__(self) -> None:
        self._bundles: dict[uuid.UUID, EvidenceBundle] = {}

    def create_bundle(
        self,
        bundle_type: BundleType,
        bundle_key: str,
        evidence_list: list[Evidence],
        title: str | None = None,
        confidence: float = 0.5,
    ) -> EvidenceBundle:
        """Create a new bundle from a list of evidence.

        Args:
            bundle_type: Type of bundle grouping.
            bundle_key: Entity ID or key to group by.
            evidence_list: List of evidence to include.
            title: Optional human-readable title.
            confidence: Confidence score for the bundle.

        Returns:
            The created EvidenceBundle.
        """
        bundle = EvidenceBundle(
            bundle_id=uuid.uuid4(),
            bundle_type=bundle_type,
            entity_id=bundle_key,
            evidence_ids=[ev.evidence_id for ev in evidence_list],
            title=title or f"{bundle_type.value} bundle for {bundle_key}",
            confidence=confidence,
            created_at=datetime.now(UTC),
            metadata={"bundle_type": bundle_type.value, "entity_count": len(evidence_list)},
        )
        self._bundles[bundle.bundle_id] = bundle
        return bundle

    def add_to_bundle(
        self,
        bundle: EvidenceBundle,
        evidence: Evidence,
    ) -> EvidenceBundle:
        """Add evidence to an existing bundle.

        Args:
            bundle: The bundle to add to.
            evidence: The evidence to add.

        Returns:
            Updated EvidenceBundle.
        """
        if evidence.evidence_id not in bundle.evidence_ids:
            bundle.evidence_ids.append(evidence.evidence_id)
        self._bundles[bundle.bundle_id] = bundle
        return bundle

    def get_bundle(self, bundle_id: uuid.UUID) -> EvidenceBundle | None:
        """Retrieve a bundle by ID.

        Args:
            bundle_id: The bundle ID to look up.

        Returns:
            The bundle if found, None otherwise.
        """
        return self._bundles.get(bundle_id)

    def list_bundles(self) -> list[EvidenceBundle]:
        """List all bundles.

        Returns:
            List of all EvidenceBundle objects.
        """
        return list(self._bundles.values())

    def remove_bundle(self, bundle_id: uuid.UUID) -> bool:
        """Remove a bundle by ID.

        Args:
            bundle_id: The bundle ID to remove.

        Returns:
            True if the bundle was removed, False if not found.
        """
        if bundle_id in self._bundles:
            del self._bundles[bundle_id]
            return True
        return False
