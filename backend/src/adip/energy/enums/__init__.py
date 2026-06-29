"""Enumerations for the Energy Domain Package.

Defines all enum types for energy domain models, contracts,
and interfaces.
"""

from __future__ import annotations

from enum import StrEnum


class AssetType(StrEnum):
    """Type of energy asset.

    Values:
    - TRANSFORMER: Electrical transformer
    - SUBSTATION: Electrical substation
    - BREAKER: Circuit breaker
    - FEEDER: Power feeder line
    - GENERATOR: Power generator
    - BATTERY: Battery energy storage
    - SOLAR_PANEL: Solar photovoltaic panel
    - WIND_TURBINE: Wind turbine generator
    - METER: Energy meter
    - SENSOR: Measurement sensor
    """

    TRANSFORMER = "TRANSFORMER"
    SUBSTATION = "SUBSTATION"
    BREAKER = "BREAKER"
    FEEDER = "FEEDER"
    GENERATOR = "GENERATOR"
    BATTERY = "BATTERY"
    SOLAR_PANEL = "SOLAR_PANEL"
    WIND_TURBINE = "WIND_TURBINE"
    METER = "METER"
    SENSOR = "SENSOR"


class SensorType(StrEnum):
    """Type of measurement sensor.

    Values:
    - TEMPERATURE: Temperature sensor
    - VOLTAGE: Voltage measurement
    - CURRENT: Current measurement
    - POWER: Power measurement
    - FREQUENCY: Frequency measurement
    - HUMIDITY: Humidity sensor
    - PRESSURE: Pressure sensor
    - OIL_LEVEL: Oil level sensor
    - VIBRATION: Vibration sensor
    """

    TEMPERATURE = "TEMPERATURE"
    VOLTAGE = "VOLTAGE"
    CURRENT = "CURRENT"
    POWER = "POWER"
    FREQUENCY = "FREQUENCY"
    HUMIDITY = "HUMIDITY"
    PRESSURE = "PRESSURE"
    OIL_LEVEL = "OIL_LEVEL"
    VIBRATION = "VIBRATION"


class HealthState(StrEnum):
    """Health state of an energy asset.

    Values:
    - NORMAL: Asset operating normally
    - WARNING: Asset showing signs of degradation
    - CRITICAL: Asset requires immediate attention
    - OFFLINE: Asset is offline or disconnected
    - MAINTENANCE: Asset is under maintenance
    """

    NORMAL = "NORMAL"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    OFFLINE = "OFFLINE"
    MAINTENANCE = "MAINTENANCE"


class MaintenanceType(StrEnum):
    """Type of maintenance activity.

    Values:
    - PREVENTIVE: Scheduled preventive maintenance
    - PREDICTIVE: Condition-based predictive maintenance
    - CORRECTIVE: Reactive corrective maintenance
    - EMERGENCY: Emergency unscheduled maintenance
    """

    PREVENTIVE = "PREVENTIVE"
    PREDICTIVE = "PREDICTIVE"
    CORRECTIVE = "CORRECTIVE"
    EMERGENCY = "EMERGENCY"


class AlarmSeverity(StrEnum):
    """Severity level of an alarm.

    Values:
    - CRITICAL: Critical — immediate action required
    - MAJOR: Major — significant impact
    - MINOR: Minor — limited impact
    - WARNING: Warning — potential issue
    - INFO: Informational notification
    """

    CRITICAL = "CRITICAL"
    MAJOR = "MAJOR"
    MINOR = "MINOR"
    WARNING = "WARNING"
    INFO = "INFO"


class EnergyDomain(StrEnum):
    """Utility domain for energy operations.

    Values:
    - ELECTRICITY: Electrical power domain
    - GAS: Natural gas domain
    - WATER: Water utility domain
    - STEAM: Steam / thermal domain
    - RENEWABLES: Renewable energy domain
    """

    ELECTRICITY = "ELECTRICITY"
    GAS = "GAS"
    WATER = "WATER"
    STEAM = "STEAM"
    RENEWABLES = "RENEWABLES"


class AssetStatus(StrEnum):
    """Operational status of an energy asset.

    Values:
    - ACTIVE: Asset is active and operational
    - INACTIVE: Asset is inactive but installed
    - DECOMMISSIONED: Asset has been decommissioned
    - PLANNED: Asset is planned but not yet installed
    - CONSTRUCTION: Asset is under construction
    """

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    DECOMMISSIONED = "DECOMMISSIONED"
    PLANNED = "PLANNED"
    CONSTRUCTION = "CONSTRUCTION"


class AlarmStatus(StrEnum):
    """Status of an alarm.

    Values:
    - ACTIVE: Alarm is currently active
    - ACKNOWLEDGED: Alarm has been acknowledged
    - RESOLVED: Alarm has been resolved
    - CLEARED: Alarm condition has cleared
    - ESCALATED: Alarm has been escalated
    """

    ACTIVE = "ACTIVE"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    RESOLVED = "RESOLVED"
    CLEARED = "CLEARED"
    ESCALATED = "ESCALATED"


class IncidentPriority(StrEnum):
    """Priority level for an incident.

    Values:
    - CRITICAL: Critical priority
    - HIGH: High priority
    - MEDIUM: Medium priority
    - LOW: Low priority
    """

    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class WorkOrderStatus(StrEnum):
    """Status of a work order.

    Values:
    - OPEN: Work order has been created
    - ASSIGNED: Work order has been assigned
    - IN_PROGRESS: Work is in progress
    - COMPLETED: Work has been completed
    - CANCELLED: Work order has been cancelled
    """

    OPEN = "OPEN"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
