"""EquipmentClassification — classifies energy equipment.

Deterministic placeholder that maps AssetType values to
equipment classification categories: Generation, Transmission,
Distribution, Consumption, or Storage.
"""

from __future__ import annotations

import uuid

import structlog

from adip.energy.enums import AssetType
from adip.energy.execution.models import ClassificationResult

log = structlog.get_logger(__name__)

_CLASSIFICATION_MAP: dict[AssetType, tuple[str, str]] = {
    AssetType.GENERATOR: ("generation", "Power Generation"),
    AssetType.SOLAR_PANEL: ("generation", "Solar Generation"),
    AssetType.WIND_TURBINE: ("generation", "Wind Generation"),
    AssetType.BATTERY: ("storage", "Battery Storage"),
    AssetType.TRANSFORMER: ("transmission", "Step-up/Step-down Transformer"),
    AssetType.SUBSTATION: ("transmission", "Electrical Substation"),
    AssetType.BREAKER: ("distribution", "Circuit Breaker"),
    AssetType.FEEDER: ("distribution", "Power Feeder"),
    AssetType.METER: ("consumption", "Energy Meter"),
    AssetType.SENSOR: ("consumption", "Measurement Sensor"),
}


class EquipmentClassification:
    """Classifies energy assets into equipment categories."""

    def classify(
        self,
        asset_id: str,
        asset_type: str,
        correlation_id: str = "",
    ) -> ClassificationResult:
        """Classify an asset by its type.

        Args:
            asset_id: The asset identifier.
            asset_type: The asset type string.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            ClassificationResult with classification and category.
        """
        atype = self._parse_asset_type(asset_type)
        classification, category = _CLASSIFICATION_MAP.get(
            atype,
            ("consumption", "Unknown"),
        )

        result = ClassificationResult(
            asset_id=self._parse_uuid(asset_id),
            asset_type=atype,
            classification=classification,
            category=category,
        )
        log.info(
            "energy.classification.result",
            asset_id=asset_id,
            asset_type=atype.value,
            classification=classification,
            correlation_id=correlation_id,
        )
        return result

    def get_classification_for_type(
        self,
        asset_type: str,
    ) -> str:
        """Get the equipment classification for an asset type.

        Args:
            asset_type: The asset type string.

        Returns:
            Classification string (generation, transmission, distribution,
            consumption, or storage).
        """
        atype = self._parse_asset_type(asset_type)
        classification, _ = _CLASSIFICATION_MAP.get(
            atype,
            ("consumption",),
        )
        return classification

    def get_all_classifications(self) -> dict[str, list[str]]:
        """Get all equipment classifications with their asset types.

        Returns:
            Dict mapping classification to list of asset type names.
        """
        result: dict[str, list[str]] = {}
        for atype, (classification, _) in _CLASSIFICATION_MAP.items():
            if classification not in result:
                result[classification] = []
            result[classification].append(atype.value)
        return result

    def _parse_asset_type(self, type_str: str) -> AssetType:
        """Parse a string into AssetType."""
        for at in AssetType:
            if at.value == type_str or at.name == type_str:
                return at
        return AssetType.SENSOR

    @staticmethod
    def _parse_uuid(value: str | uuid.UUID) -> uuid.UUID:
        if isinstance(value, uuid.UUID):
            return value
        try:
            return uuid.UUID(value)
        except ValueError:
            return uuid.uuid5(uuid.NAMESPACE_DNS, value)
