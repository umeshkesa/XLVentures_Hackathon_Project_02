"""UnitConversionService — provides deterministic unit conversions.

Deterministic placeholder conversions for temperature, voltage,
current, power, frequency, and pressure units.
"""

from __future__ import annotations

import structlog

from adip.energy.execution.models import ConversionRequest, ConversionResult

log = structlog.get_logger(__name__)


class UnitConversionService:
    """Provides deterministic unit conversions for energy domain."""

    def convert(
        self,
        request: ConversionRequest,
        correlation_id: str = "",
    ) -> ConversionResult:
        """Convert a value from one unit to another.

        Args:
            request: The ConversionRequest with value, from_unit, to_unit.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            ConversionResult with the converted value.

        Raises:
            ValueError: If conversion is not supported.
        """
        from_lower = request.from_unit.lower().strip()
        to_lower = request.to_unit.lower().strip()
        conv_type = request.conversion_type.lower().strip()
        value = request.value

        output_value = self._convert(value, from_lower, to_lower, conv_type)

        result = ConversionResult(
            input_value=value,
            output_value=output_value,
            from_unit=request.from_unit,
            to_unit=request.to_unit,
            conversion_type=request.conversion_type,
        )
        log.info(
            "energy.unit_conversion.complete",
            value=value,
            from_unit=request.from_unit,
            to_unit=request.to_unit,
            result=output_value,
            correlation_id=correlation_id,
        )
        return result

    def convert_temperature(
        self,
        value: float,
        from_unit: str,
        to_unit: str,
    ) -> float:
        """Convert between temperature units.

        Supports: Celsius (°C), Fahrenheit (°F), Kelvin (K).

        Args:
            value: Temperature value.
            from_unit: Source unit.
            to_unit: Target unit.

        Returns:
            Converted temperature value.
        """
        from_lower = from_unit.lower().strip()
        to_lower = to_unit.lower().strip()

        if from_lower == to_lower:
            return value

        if from_lower in ("celsius", "c", "°c"):
            if to_lower in ("fahrenheit", "f", "°f"):
                return round(value * 9.0 / 5.0 + 32.0, 4)
            if to_lower in ("kelvin", "k"):
                return round(value + 273.15, 4)

        if from_lower in ("fahrenheit", "f", "°f"):
            if to_lower in ("celsius", "c", "°c"):
                return round((value - 32.0) * 5.0 / 9.0, 4)
            if to_lower in ("kelvin", "k"):
                return round((value - 32.0) * 5.0 / 9.0 + 273.15, 4)

        if from_lower in ("kelvin", "k"):
            if to_lower in ("celsius", "c", "°c"):
                return round(value - 273.15, 4)
            if to_lower in ("fahrenheit", "f", "°f"):
                return round((value - 273.15) * 9.0 / 5.0 + 32.0, 4)

        raise ValueError(f"Unsupported temperature conversion: {from_unit} -> {to_unit}")

    def convert_voltage(
        self,
        value: float,
        from_unit: str,
        to_unit: str,
    ) -> float:
        """Convert between voltage units.

        Supports: Volt (V), Kilovolt (kV), Millivolt (mV).

        Args:
            value: Voltage value.
            from_unit: Source unit.
            to_unit: Target unit.

        Returns:
            Converted voltage value.
        """
        from_lower = from_unit.lower().strip()
        to_lower = to_unit.lower().strip()

        if from_lower == to_lower:
            return value

        ref_volts = self._to_volts(value, from_lower)
        return self._from_volts(ref_volts, to_lower)

    def convert_current(
        self,
        value: float,
        from_unit: str,
        to_unit: str,
    ) -> float:
        """Convert between current units.

        Supports: Ampere (A), Milliampere (mA), Kiloampere (kA).

        Args:
            value: Current value.
            from_unit: Source unit.
            to_unit: Target unit.

        Returns:
            Converted current value.
        """
        from_lower = from_unit.lower().strip()
        to_lower = to_unit.lower().strip()

        if from_lower == to_lower:
            return value

        ref_amps = self._to_amps(value, from_lower)
        return self._from_amps(ref_amps, to_lower)

    def convert_power(
        self,
        value: float,
        from_unit: str,
        to_unit: str,
    ) -> float:
        """Convert between power units.

        Supports: Watt (W), Kilowatt (kW), Megawatt (MW), Gigawatt (GW).

        Args:
            value: Power value.
            from_unit: Source unit.
            to_unit: Target unit.

        Returns:
            Converted power value.
        """
        from_lower = from_unit.lower().strip()
        to_lower = to_unit.lower().strip()

        if from_lower == to_lower:
            return value

        ref_watts = self._to_watts(value, from_lower)
        return self._from_watts(ref_watts, to_lower)

    def convert_frequency(
        self,
        value: float,
        from_unit: str,
        to_unit: str,
    ) -> float:
        """Convert between frequency units.

        Supports: Hertz (Hz), Kilohertz (kHz), Megahertz (MHz).

        Args:
            value: Frequency value.
            from_unit: Source unit.
            to_unit: Target unit.

        Returns:
            Converted frequency value.
        """
        from_lower = from_unit.lower().strip()
        to_lower = to_unit.lower().strip()

        if from_lower == to_lower:
            return value

        ref_hz = self._to_hertz(value, from_lower)
        return self._from_hertz(ref_hz, to_lower)

    def convert_pressure(
        self,
        value: float,
        from_unit: str,
        to_unit: str,
    ) -> float:
        """Convert between pressure units.

        Supports: Pascal (Pa), Kilopascal (kPa), Bar (bar), PSI (psi).

        Args:
            value: Pressure value.
            from_unit: Source unit.
            to_unit: Target unit.

        Returns:
            Converted pressure value.
        """
        from_lower = from_unit.lower().strip()
        to_lower = to_unit.lower().strip()

        if from_lower == to_lower:
            return value

        ref_pa = self._to_pascals(value, from_lower)
        return self._from_pascals(ref_pa, to_lower)

    def _convert(
        self,
        value: float,
        from_unit: str,
        to_unit: str,
        conv_type: str,
    ) -> float:
        """Internal dispatch to the correct conversion method."""
        if conv_type == "temperature":
            return self.convert_temperature(value, from_unit, to_unit)
        if conv_type == "voltage":
            return self.convert_voltage(value, from_unit, to_unit)
        if conv_type == "current":
            return self.convert_current(value, from_unit, to_unit)
        if conv_type == "power":
            return self.convert_power(value, from_unit, to_unit)
        if conv_type == "frequency":
            return self.convert_frequency(value, from_unit, to_unit)
        if conv_type == "pressure":
            return self.convert_pressure(value, from_unit, to_unit)
        raise ValueError(f"Unsupported conversion type: {conv_type}")

    def _to_volts(self, value: float, unit: str) -> float:
        if unit in ("v", "volt", "volts"):
            return value
        if unit in ("kv", "kilovolt", "kilovolts"):
            return value * 1000.0
        if unit in ("mv", "millivolt", "millivolts"):
            return value / 1000.0
        raise ValueError(f"Unsupported voltage unit: {unit}")

    def _from_volts(self, value: float, unit: str) -> float:
        if unit in ("v", "volt", "volts"):
            return value
        if unit in ("kv", "kilovolt", "kilovolts"):
            return value / 1000.0
        if unit in ("mv", "millivolt", "millivolts"):
            return value * 1000.0
        raise ValueError(f"Unsupported voltage unit: {unit}")

    def _to_amps(self, value: float, unit: str) -> float:
        if unit in ("a", "amp", "amps", "ampere", "amperes"):
            return value
        if unit in ("ma", "milliamp", "milliamps", "milliampere"):
            return value / 1000.0
        if unit in ("ka", "kiloamp", "kiloamps", "kiloampere"):
            return value * 1000.0
        raise ValueError(f"Unsupported current unit: {unit}")

    def _from_amps(self, value: float, unit: str) -> float:
        if unit in ("a", "amp", "amps", "ampere", "amperes"):
            return value
        if unit in ("ma", "milliamp", "milliamps", "milliampere"):
            return value * 1000.0
        if unit in ("ka", "kiloamp", "kiloamps", "kiloampere"):
            return value / 1000.0
        raise ValueError(f"Unsupported current unit: {unit}")

    def _to_watts(self, value: float, unit: str) -> float:
        if unit in ("w", "watt", "watts"):
            return value
        if unit in ("kw", "kilowatt", "kilowatts"):
            return value * 1000.0
        if unit in ("mw", "megawatt", "megawatts"):
            return value * 1_000_000.0
        if unit in ("gw", "gigawatt", "gigawatts"):
            return value * 1_000_000_000.0
        raise ValueError(f"Unsupported power unit: {unit}")

    def _from_watts(self, value: float, unit: str) -> float:
        if unit in ("w", "watt", "watts"):
            return value
        if unit in ("kw", "kilowatt", "kilowatts"):
            return value / 1000.0
        if unit in ("mw", "megawatt", "megawatts"):
            return value / 1_000_000.0
        if unit in ("gw", "gigawatt", "gigawatts"):
            return value / 1_000_000_000.0
        raise ValueError(f"Unsupported power unit: {unit}")

    def _to_hertz(self, value: float, unit: str) -> float:
        if unit in ("hz", "hertz"):
            return value
        if unit in ("khz", "kilohertz"):
            return value * 1000.0
        if unit in ("mhz", "megahertz"):
            return value * 1_000_000.0
        raise ValueError(f"Unsupported frequency unit: {unit}")

    def _from_hertz(self, value: float, unit: str) -> float:
        if unit in ("hz", "hertz"):
            return value
        if unit in ("khz", "kilohertz"):
            return value / 1000.0
        if unit in ("mhz", "megahertz"):
            return value / 1_000_000.0
        raise ValueError(f"Unsupported frequency unit: {unit}")

    def _to_pascals(self, value: float, unit: str) -> float:
        if unit in ("pa", "pascal", "pascals"):
            return value
        if unit in ("kpa", "kilopascal", "kilopascals"):
            return value * 1000.0
        if unit in ("bar", "bars"):
            return value * 100_000.0
        if unit in ("psi"):
            return value * 6894.76
        raise ValueError(f"Unsupported pressure unit: {unit}")

    def _from_pascals(self, value: float, unit: str) -> float:
        if unit in ("pa", "pascal", "pascals"):
            return value
        if unit in ("kpa", "kilopascal", "kilopascals"):
            return value / 1000.0
        if unit in ("bar", "bars"):
            return value / 100_000.0
        if unit in ("psi"):
            return value / 6894.76
        raise ValueError(f"Unsupported pressure unit: {unit}")
