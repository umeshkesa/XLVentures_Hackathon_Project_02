"""Exception definitions for the Energy Domain Package.

Defines all exception types used across energy domain
operations for consistent error handling and reporting.
"""

from __future__ import annotations

from typing import Any


class EnergyDomainException(Exception):
    """Base exception for all energy domain errors.

    All energy-specific exceptions inherit from this class
    for consistent error handling.
    """

    def __init__(
        self,
        message: str = "Energy domain error occurred",
        code: str = "ENERGY_DOMAIN_ERROR",
        details: dict[str, Any] | None = None,
    ) -> None:
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)


class AssetException(EnergyDomainException):
    """Exception raised for asset-related errors.

    Raised when an asset operation fails, such as registration,
    update, hierarchy, or retrieval errors.
    """

    def __init__(
        self,
        message: str = "Asset error occurred",
        code: str = "ASSET_ERROR",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message=message, code=code, details=details)


class SensorException(EnergyDomainException):
    """Exception raised for sensor-related errors.

    Raised when a sensor operation fails, such as reading
    collection, configuration, or communication errors.
    """

    def __init__(
        self,
        message: str = "Sensor error occurred",
        code: str = "SENSOR_ERROR",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message=message, code=code, details=details)


class MaintenanceException(EnergyDomainException):
    """Exception raised for maintenance-related errors.

    Raised when a maintenance operation fails, such as
    scheduling, execution, or record-keeping errors.
    """

    def __init__(
        self,
        message: str = "Maintenance error occurred",
        code: str = "MAINTENANCE_ERROR",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message=message, code=code, details=details)


class AlarmException(EnergyDomainException):
    """Exception raised for alarm-related errors.

    Raised when an alarm operation fails, such as creation,
    acknowledgement, escalation, or resolution errors.
    """

    def __init__(
        self,
        message: str = "Alarm error occurred",
        code: str = "ALARM_ERROR",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message=message, code=code, details=details)
