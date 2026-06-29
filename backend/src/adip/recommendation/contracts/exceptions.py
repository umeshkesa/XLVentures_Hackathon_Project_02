"""Exception definitions for the Recommendation Engine.

Defines all exception types used across recommendation operations
for consistent error handling and reporting.
"""

from __future__ import annotations


class RecommendationException(Exception):
    """Base exception for all recommendation errors.

    All recommendation-specific exceptions inherit from this class
    for consistent error handling.
    """

    def __init__(self, message: str = "A recommendation error occurred") -> None:
        self.message = message
        super().__init__(self.message)


class RecommendationValidationException(RecommendationException):
    """Exception raised for recommendation validation errors.

    Raised when recommendation generation, ranking, or
    package validation fails.
    """

    def __init__(self, message: str = "A recommendation validation error occurred") -> None:
        super().__init__(message)


class RecommendationRankingException(RecommendationException):
    """Exception raised for recommendation ranking errors.

    Raised when ranking operations, priority assignment,
    or comparison fails.
    """

    def __init__(self, message: str = "A recommendation ranking error occurred") -> None:
        super().__init__(message)


class RecommendationPolicyException(RecommendationException):
    """Exception raised for recommendation policy errors.

    Raised when policy checks, constraint validation, or
    approval workflows fail.
    """

    def __init__(self, message: str = "A recommendation policy error occurred") -> None:
        super().__init__(message)
