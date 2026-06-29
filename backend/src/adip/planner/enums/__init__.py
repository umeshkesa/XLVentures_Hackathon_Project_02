"""Enum classes for the planner module."""

from __future__ import annotations

from enum import Enum, auto


class PriorityEnum(Enum):
    """Defines the priority of a planning goal or task."""
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    CRITICAL = auto()


class PlanningStrategyEnum(Enum):
    """Defines the strategy to be used for planning."""
    DEFAULT = auto()
    OPTIMISTIC = auto()
    PESSIMISTIC = auto()
    GREEDY = auto()
    BEST_FIRST = auto()


class PlanningStatusEnum(Enum):
    """Represents the overall status of the planning process."""
    CREATED = auto()
    ANALYZING = auto()
    PLANNING = auto()
    VALIDATING = auto()
    OPTIMIZING = auto()
    EXECUTING = auto()
    COMPLETED = auto()
    FAILED = auto()
    CANCELLED = auto()


class TaskStatusEnum(Enum):
    """Represents the status of an individual planning task."""
    PENDING = auto()
    READY = auto()
    IN_PROGRESS = auto()
    COMPLETED = auto()
    FAILED = auto()
    CANCELLED = auto()
    SKIPPED = auto()


class ConfidenceLevelEnum(Enum):
    """Represents the confidence level of a capability match."""
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    VERY_HIGH = auto()
