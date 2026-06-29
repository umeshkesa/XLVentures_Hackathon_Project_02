"""Exceptions for the Evidence Fusion Engine.

Defines the exception hierarchy for evidence-related errors
including validation, correlation, and fusion failures.
"""

from __future__ import annotations


class EvidenceException(Exception):
    """Base exception for all evidence-related errors."""

    def __init__(self, message: str = "Evidence error") -> None:
        self.message = message
        super().__init__(self.message)


class EvidenceValidationException(EvidenceException):
    """Raised when evidence validation fails."""

    def __init__(self, message: str = "Evidence validation error") -> None:
        super().__init__(message)


class EvidenceCorrelationException(EvidenceException):
    """Raised when evidence correlation fails."""

    def __init__(
        self,
        evidence_id: str = "",
        correlated_evidence_id: str = "",
        message: str = "",
    ) -> None:
        self.evidence_id = evidence_id
        self.correlated_evidence_id = correlated_evidence_id
        if not message:
            details = []
            if evidence_id:
                details.append(f"evidence: {evidence_id}")
            if correlated_evidence_id:
                details.append(f"correlated with: {correlated_evidence_id}")
            message = (
                f"Evidence correlation failed ({'; '.join(details)})"
                if details
                else "Evidence correlation failed"
            )
        super().__init__(message)


class EvidenceFusionException(EvidenceException):
    """Raised when evidence fusion fails."""

    def __init__(
        self,
        evidence_ids: list[str] | None = None,
        message: str = "",
    ) -> None:
        self.evidence_ids = evidence_ids or []
        if not message:
            if self.evidence_ids:
                message = f"Evidence fusion failed for {len(self.evidence_ids)} evidence items"
            else:
                message = "Evidence fusion failed"
        super().__init__(message)
