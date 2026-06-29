"""Exception definitions for the Explainability Engine.

Defines all exception types used across explanation operations
for consistent error handling and reporting.
"""

from __future__ import annotations


class ExplainabilityException(Exception):
    """Base exception for all explainability errors.

    All explainability-specific exceptions inherit from this class
    for consistent error handling.
    """

    def __init__(
        self,
        message: str = "An explainability error occurred",
        error_code: str = "",
    ) -> None:
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class NarrativeException(ExplainabilityException):
    """Exception raised for narrative-related errors.

    Raised when narrative generation, formatting, or
    audience targeting fails.
    """

    def __init__(
        self,
        message: str = "A narrative error occurred",
        narrative_id: str = "",
    ) -> None:
        self.narrative_id = narrative_id
        super().__init__(message)


class CitationException(ExplainabilityException):
    """Exception raised for citation-related errors.

    Raised when citation creation, validation, or
    source linking fails.
    """

    def __init__(
        self,
        message: str = "A citation error occurred",
        citation_id: str = "",
    ) -> None:
        self.citation_id = citation_id
        super().__init__(message)


class TraceException(ExplainabilityException):
    """Exception raised for trace-related errors.

    Raised when trace recording, stage management, or
    correlation tracking fails.
    """

    def __init__(
        self,
        message: str = "A trace error occurred",
        trace_id: str = "",
    ) -> None:
        self.trace_id = trace_id
        super().__init__(message)
