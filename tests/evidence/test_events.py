"""Tests for Evidence Fusion Engine events."""

from __future__ import annotations

import uuid

from adip.evidence.contracts.events import (
    EventVersion,
    EvidenceCollected,
    EvidenceCorrelated,
    EvidenceEvent,
    EvidenceFused,
    EvidenceNormalized,
    EvidencePackaged,
    EvidenceValidated,
)
from adip.evidence.enums import EvidenceDomain, EvidenceType


class TestEventVersion:
    def test_event_version_defined(self) -> None:
        assert EventVersion == "1.0.0"


class TestEvidenceEvent:
    def test_base_event_defaults(self) -> None:
        eid = uuid.uuid4()
        event = EvidenceEvent(evidence_id=eid, evidence_type=EvidenceType.KNOWLEDGE)
        assert event.domain == EvidenceDomain.SYSTEM
        assert event.correlation_id == ""
        assert event.payload == {}
        assert event.event_id is not None
        assert event.timestamp is not None

    def test_base_event_evidence_id_required(self) -> None:
        import pytest
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            EvidenceEvent()


class TestEvidenceCollected:
    def test_collected_defaults(self) -> None:
        eid = uuid.uuid4()
        event = EvidenceCollected(evidence_id=eid, evidence_type=EvidenceType.SENSOR)
        assert event.source_type == ""
        assert event.source_manager == ""
        assert event.evidence_type == EvidenceType.SENSOR

    def test_collected_with_values(self) -> None:
        eid = uuid.uuid4()
        event = EvidenceCollected(
            evidence_id=eid,
            evidence_type=EvidenceType.SENSOR,
            domain=EvidenceDomain.ENERGY,
            source_type="iot-sensor",
            source_manager="SensorCollector",
            correlation_id="corr-1",
        )
        assert event.source_type == "iot-sensor"
        assert event.source_manager == "SensorCollector"
        assert event.domain == EvidenceDomain.ENERGY


class TestEvidenceValidated:
    def test_validated_defaults(self) -> None:
        eid = uuid.uuid4()
        event = EvidenceValidated(evidence_id=eid, evidence_type=EvidenceType.KNOWLEDGE)
        assert event.validated is True
        assert event.violations == []

    def test_validated_with_violations(self) -> None:
        eid = uuid.uuid4()
        event = EvidenceValidated(
            evidence_id=eid,
            evidence_type=EvidenceType.KNOWLEDGE,
            validated=False,
            violations=["Missing metadata", "Invalid source"],
        )
        assert event.validated is False
        assert len(event.violations) == 2


class TestEvidenceNormalized:
    def test_normalized_defaults(self) -> None:
        eid = uuid.uuid4()
        event = EvidenceNormalized(evidence_id=eid, evidence_type=EvidenceType.MEMORY)
        assert event.normalizer == ""
        assert event.normalized_fields == []

    def test_normalized_with_values(self) -> None:
        eid = uuid.uuid4()
        event = EvidenceNormalized(
            evidence_id=eid,
            evidence_type=EvidenceType.MEMORY,
            normalizer="StandardNormalizer",
            normalized_fields=["payload", "metadata"],
        )
        assert event.normalizer == "StandardNormalizer"
        assert "payload" in event.normalized_fields


class TestEvidenceCorrelated:
    def test_correlated_defaults(self) -> None:
        eid = uuid.uuid4()
        event = EvidenceCorrelated(evidence_id=eid, evidence_type=EvidenceType.RULE)
        assert event.correlated_evidence_ids == []
        assert event.correlation_score == 0.0

    def test_correlated_with_values(self) -> None:
        eid = uuid.uuid4()
        cid1 = uuid.uuid4()
        cid2 = uuid.uuid4()
        event = EvidenceCorrelated(
            evidence_id=eid,
            evidence_type=EvidenceType.RULE,
            correlated_evidence_ids=[cid1, cid2],
            correlation_score=0.85,
        )
        assert len(event.correlated_evidence_ids) == 2
        assert event.correlation_score == 0.85

    def test_correlation_score_bounds(self) -> None:
        import pytest
        from pydantic import ValidationError
        eid = uuid.uuid4()
        with pytest.raises(ValidationError):
            EvidenceCorrelated(evidence_id=eid, evidence_type=EvidenceType.RULE, correlation_score=1.5)


class TestEvidenceFused:
    def test_fused_defaults(self) -> None:
        eid = uuid.uuid4()
        pid = uuid.uuid4()
        event = EvidenceFused(evidence_id=eid, evidence_type=EvidenceType.WORKFLOW, package_id=pid)
        assert event.fusion_weight == 0.0

    def test_fused_with_values(self) -> None:
        eid = uuid.uuid4()
        pid = uuid.uuid4()
        event = EvidenceFused(
            evidence_id=eid,
            evidence_type=EvidenceType.WORKFLOW,
            package_id=pid,
            fusion_weight=0.75,
        )
        assert event.fusion_weight == 0.75

    def test_package_id_required(self) -> None:
        import pytest
        from pydantic import ValidationError
        eid = uuid.uuid4()
        with pytest.raises(ValidationError):
            EvidenceFused(evidence_id=eid, evidence_type=EvidenceType.WORKFLOW)


class TestEvidencePackaged:
    def test_packaged_defaults(self) -> None:
        eid = uuid.uuid4()
        pid = uuid.uuid4()
        event = EvidencePackaged(evidence_id=eid, evidence_type=EvidenceType.REPORT, package_id=pid)
        assert event.evidence_count == 0
        assert event.package_confidence == 0.0

    def test_packaged_with_values(self) -> None:
        eid = uuid.uuid4()
        pid = uuid.uuid4()
        event = EvidencePackaged(
            evidence_id=eid,
            evidence_type=EvidenceType.REPORT,
            package_id=pid,
            evidence_count=10,
            package_confidence=0.9,
        )
        assert event.evidence_count == 10
        assert event.package_confidence == 0.9
