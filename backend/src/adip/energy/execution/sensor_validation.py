"""SensorValidationPipeline — validates sensor readings.

Performs deterministic validation for missing values, invalid
ranges, duplicate readings, timestamp validation, and unit
normalisation.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import structlog

from adip.energy.execution.models import ValidationResult

log = structlog.get_logger(__name__)

_MAX_TIMESTAMP_DRIFT_SECONDS = 3600
_DEFAULT_SENSOR_RANGES: dict[str, tuple[float, float]] = {
    "TEMPERATURE": (-50.0, 200.0),
    "VOLTAGE": (0.0, 1000.0),
    "CURRENT": (0.0, 5000.0),
    "POWER": (0.0, 10000.0),
    "FREQUENCY": (45.0, 65.0),
    "HUMIDITY": (0.0, 100.0),
    "PRESSURE": (0.0, 10000.0),
    "OIL_LEVEL": (0.0, 100.0),
    "VIBRATION": (0.0, 100.0),
}

_UNIT_NORMALIZATION: dict[str, str] = {
    "celsius": "°C",
    "c": "°C",
    "fahrenheit": "°F",
    "f": "°F",
    "kelvin": "K",
    "k": "K",
    "volt": "V",
    "volts": "V",
    "v": "V",
    "kilovolt": "kV",
    "kv": "kV",
    "amp": "A",
    "amps": "A",
    "ampere": "A",
    "a": "A",
    "milliamp": "mA",
    "ma": "mA",
    "watt": "W",
    "watts": "W",
    "w": "W",
    "kilowatt": "kW",
    "kw": "kW",
    "megawatt": "MW",
    "mw": "MW",
    "hertz": "Hz",
    "hz": "Hz",
    "percent": "%",
    "pct": "%",
}


class SensorValidationPipeline:
    """Validates sensor readings for quality and consistency."""

    def validate(
        self,
        sensor_type: str,
        value: float,
        unit: str = "",
        timestamp: datetime | None = None,
        recent_readings: list[float] | None = None,
        correlation_id: str = "",
    ) -> ValidationResult:
        """Validate a sensor reading.

        Args:
            sensor_type: Type of sensor (e.g. TEMPERATURE, VOLTAGE).
            value: The measured value.
            unit: Measurement unit.
            timestamp: When the reading was taken.
            recent_readings: Recent readings for duplicate detection.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            ValidationResult with any issues found.
        """
        issues: list[str] = []
        normalized_value = value
        normalized_unit = unit

        normalized_unit = self._normalize_unit(unit)

        if self._is_missing(value):
            issues.append("Missing value (zero or NaN)")

        range_issues = self._validate_range(sensor_type, value)
        issues.extend(range_issues)

        if recent_readings:
            dup_issues = self._check_duplicates(value, recent_readings)
            issues.extend(dup_issues)

        time_issues = self._validate_timestamp(timestamp)
        issues.extend(time_issues)

        is_valid = len(issues) == 0

        result = ValidationResult(
            is_valid=is_valid,
            issues=issues,
            normalized_value=normalized_value,
            normalized_unit=normalized_unit,
        )
        log.info(
            "energy.sensor_validation.result",
            sensor_type=sensor_type,
            value=value,
            is_valid=is_valid,
            issues_count=len(issues),
            correlation_id=correlation_id,
        )
        return result

    def _is_missing(self, value: float) -> bool:
        """Check if a value is effectively missing."""
        import math
        return value == 0.0 or math.isnan(value) or math.isinf(value)

    def _validate_range(
        self,
        sensor_type: str,
        value: float,
    ) -> list[str]:
        """Validate a value is within the expected range for the sensor type."""
        issues: list[str] = []
        sensor_key = sensor_type.upper()
        if sensor_key in _DEFAULT_SENSOR_RANGES:
            min_val, max_val = _DEFAULT_SENSOR_RANGES[sensor_key]
            if value < min_val:
                issues.append(
                    f"Value {value} below minimum range {min_val} for {sensor_type}"
                )
            if value > max_val:
                issues.append(
                    f"Value {value} above maximum range {max_val} for {sensor_type}"
                )
        return issues

    def _check_duplicates(
        self,
        value: float,
        recent_readings: list[float],
    ) -> list[str]:
        """Check for duplicate readings within tolerance."""
        issues: list[str] = []
        for prev in recent_readings:
            if abs(value - prev) < 0.001:
                issues.append(f"Duplicate reading detected (value={value})")
                break
        return issues

    def _validate_timestamp(
        self,
        timestamp: datetime | None,
    ) -> list[str]:
        """Validate a timestamp is not in the future or too far in the past."""
        issues: list[str] = []
        if timestamp is None:
            return issues

        now = datetime.now(UTC)
        if timestamp > now + timedelta(seconds=_MAX_TIMESTAMP_DRIFT_SECONDS):
            issues.append(f"Timestamp {timestamp} is too far in the future")
        if timestamp < now - timedelta(seconds=_MAX_TIMESTAMP_DRIFT_SECONDS * 24):
            issues.append(f"Timestamp {timestamp} is too far in the past")
        return issues

    def _normalize_unit(self, unit: str) -> str:
        """Normalize a unit string to a standard form."""
        if not unit:
            return unit
        lower = unit.lower().strip()
        return _UNIT_NORMALIZATION.get(lower, unit)

    def get_default_range(self, sensor_type: str) -> tuple[float, float]:
        """Get the default valid range for a sensor type.

        Args:
            sensor_type: The sensor type string.

        Returns:
            Tuple of (min_value, max_value).
        """
        sensor_key = sensor_type.upper()
        return _DEFAULT_SENSOR_RANGES.get(sensor_key, (float("-inf"), float("inf")))
