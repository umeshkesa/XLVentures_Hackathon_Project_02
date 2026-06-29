"""Exception definitions for the Reasoning Engine.

Defines all exception types used across reasoning operations
for consistent error handling and reporting.
"""

from __future__ import annotations


class ReasoningException(Exception):
    """Base exception for all reasoning errors.

    All reasoning-specific exceptions inherit from this class
    for consistent error handling.
    """

    def __init__(self, message: str = "A reasoning error occurred") -> None:
        self.message = message
        super().__init__(self.message)


class HypothesisException(ReasoningException):
    """Exception raised for hypothesis-related errors.

    Raised when hypothesis generation, validation, or
    management operations fail.
    """

    def __init__(self, message: str = "A hypothesis error occurred") -> None:
        super().__init__(message)


class InferenceException(ReasoningException):
    """Exception raised for inference-related errors.

    Raised when inference operations, chain construction,
    or evaluation fails.
    """

    def __init__(self, message: str = "An inference error occurred") -> None:
        super().__init__(message)


class ContradictionException(ReasoningException):
    """Exception raised for contradiction-related errors.

    Raised when contradiction detection, resolution, or
    management operations fail.
    """

    def __init__(self, message: str = "A contradiction error occurred") -> None:
        super().__init__(message)
