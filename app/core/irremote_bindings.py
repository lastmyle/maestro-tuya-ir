"""
Python interface for IRremoteESP8266 C++ bindings.

This module provides a clean Python API for the C++ protocol database,
offering improved protocol detection using the comprehensive IRremoteESP8266
timing definitions.
"""

from typing import Optional

try:
    import _irremote
except ImportError as e:
    raise ImportError(
        "C++ bindings not available. Build the extension with: "
        "python setup.py build_ext --inplace"
    ) from e


class IRProtocolDatabase:
    """
    Python interface to the IRremoteESP8266 protocol database.

    Provides protocol identification and manufacturer detection using
    timing patterns from the IRremoteESP8266 library.

    Example:
        >>> db = IRProtocolDatabase()
        >>> timings = [3294, 1605, 420, 1200, ...]
        >>> result = db.identify_protocol(timings)
        >>> print(result['manufacturer'], result['protocol'], result['confidence'])
    """

    def __init__(self):
        """Initialize the protocol database."""
        self._db = _irremote.IRProtocolDatabase()

    def identify_protocol(
        self, timings: list[int], tolerance_multiplier: float = 1.5
    ) -> Optional[dict]:
        """
        Identify IR protocol from timing array.

        Args:
            timings: List of IR timing values in microseconds (mark/space pairs)
            tolerance_multiplier: Multiplier for timing tolerance (default 1.5)

        Returns:
            Dictionary with protocol information or None if not identified:
            {
                "protocol": "FUJITSU_AC",
                "manufacturer": ["Fujitsu", "Fujitsu General"],
                "confidence": 0.98,
                "timing_match": {
                    "header_mark": 3294,
                    "header_space": 1605,
                    "expected_mark": 3300,
                    "expected_space": 1600
                },
                "notes": "Standard Fujitsu AC protocol"
            }
        """
        result = self._db.identify_protocol(timings, tolerance_multiplier)
        return result if result else None

    def get_all_manufacturers(self) -> list[str]:
        """
        Get a sorted list of all supported manufacturers.

        Returns:
            List of manufacturer names (e.g., ["Daikin", "Fujitsu", "LG", ...])
        """
        return self._db.get_all_manufacturers()

    def get_protocols_by_manufacturer(self, manufacturer: str) -> list[str]:
        """
        Get all protocols for a specific manufacturer.

        Args:
            manufacturer: Manufacturer name (case-insensitive)

        Returns:
            List of protocol names (e.g., ["FUJITSU_AC", "FUJITSU_AC264"])
        """
        return self._db.get_protocols_by_manufacturer(manufacturer)

    def get_all_protocols(self) -> list[dict]:
        """
        Get all protocol definitions.

        Returns:
            List of protocol objects with timing information
        """
        protocols = self._db.get_protocols()
        return [
            {
                "name": p.name,
                "manufacturers": p.manufacturers,
                "header_mark": p.header_mark,
                "header_space": p.header_space,
                "bit_mark": p.bit_mark,
                "one_space": p.one_space,
                "zero_space": p.zero_space,
                "tolerance": p.tolerance,
                "frequency": p.frequency,
                "notes": p.notes,
            }
            for p in protocols
        ]


class HVACState:
    """
    HVAC state management matching IRremoteESP8266's stdAc::state_t.

    Represents the complete state of an HVAC unit including temperature,
    mode, fan speed, and various features.

    Example:
        >>> state = HVACState()
        >>> state.power = True
        >>> state.mode = "cool"
        >>> state.degrees = 22.0
        >>> state.fanspeed = "auto"
        >>> print(state.to_dict())
    """

    def __init__(self):
        """Initialize with default HVAC state."""
        self._state = _irremote.HVACState()

    @property
    def protocol(self) -> str:
        """Protocol name (e.g., "FUJITSU_AC")."""
        return self._state.protocol

    @protocol.setter
    def protocol(self, value: str):
        self._state.protocol = value

    @property
    def model(self) -> str:
        """Model identifier."""
        return self._state.model

    @model.setter
    def model(self, value: str):
        self._state.model = value

    @property
    def power(self) -> bool:
        """Power state (True = on, False = off)."""
        return self._state.power

    @power.setter
    def power(self, value: bool):
        self._state.power = value

    @property
    def mode(self) -> str:
        """Operating mode (cool, heat, dry, fan, auto)."""
        return self._state.mode

    @mode.setter
    def mode(self, value: str):
        self._state.mode = value

    @property
    def degrees(self) -> float:
        """Target temperature."""
        return self._state.degrees

    @degrees.setter
    def degrees(self, value: float):
        self._state.degrees = value

    @property
    def celsius(self) -> bool:
        """Temperature unit (True = Celsius, False = Fahrenheit)."""
        return self._state.celsius

    @celsius.setter
    def celsius(self, value: bool):
        self._state.celsius = value

    @property
    def fanspeed(self) -> str:
        """Fan speed (auto, low, medium, high, quiet, turbo)."""
        return self._state.fanspeed

    @fanspeed.setter
    def fanspeed(self, value: str):
        self._state.fanspeed = value

    @property
    def swingv(self) -> str:
        """Vertical swing mode."""
        return self._state.swingv

    @swingv.setter
    def swingv(self, value: str):
        self._state.swingv = value

    @property
    def swingh(self) -> str:
        """Horizontal swing mode."""
        return self._state.swingh

    @swingh.setter
    def swingh(self, value: str):
        self._state.swingh = value

    @property
    def quiet(self) -> bool:
        """Quiet mode enabled."""
        return self._state.quiet

    @quiet.setter
    def quiet(self, value: bool):
        self._state.quiet = value

    @property
    def turbo(self) -> bool:
        """Turbo mode enabled."""
        return self._state.turbo

    @turbo.setter
    def turbo(self, value: bool):
        self._state.turbo = value

    @property
    def econo(self) -> bool:
        """Economy mode enabled."""
        return self._state.econo

    @econo.setter
    def econo(self, value: bool):
        self._state.econo = value

    @property
    def light(self) -> bool:
        """Display light enabled."""
        return self._state.light

    @light.setter
    def light(self, value: bool):
        self._state.light = value

    @property
    def filter(self) -> bool:
        """Filter indicator."""
        return self._state.filter

    @filter.setter
    def filter(self, value: bool):
        self._state.filter = value

    @property
    def clean(self) -> bool:
        """Clean mode enabled."""
        return self._state.clean

    @clean.setter
    def clean(self, value: bool):
        self._state.clean = value

    @property
    def beep(self) -> bool:
        """Beep enabled."""
        return self._state.beep

    @beep.setter
    def beep(self, value: bool):
        self._state.beep = value

    @property
    def sleep(self) -> int:
        """Sleep timer in minutes (-1 = disabled)."""
        return self._state.sleep

    @sleep.setter
    def sleep(self, value: int):
        self._state.sleep = value

    def to_dict(self) -> dict:
        """
        Convert state to dictionary.

        Returns:
            Dictionary with all state properties
        """
        return self._state.to_dict()


# Convenience functions for backward compatibility
def identify_protocol_irremote(
    timings: list[int], tolerance_multiplier: float = 1.5
) -> Optional[dict]:
    """
    Identify IR protocol using IRremoteESP8266 timing database.

    This is a convenience function that creates a database instance and
    performs protocol identification.

    Args:
        timings: Raw IR timing array in microseconds
        tolerance_multiplier: Multiplier for tolerance (default 1.5)

    Returns:
        Dictionary with protocol information or None if not identified
    """
    db = IRProtocolDatabase()
    return db.identify_protocol(timings, tolerance_multiplier)


def get_all_manufacturers() -> list[str]:
    """Get a sorted list of all supported manufacturers."""
    db = IRProtocolDatabase()
    return db.get_all_manufacturers()


def get_protocols_by_manufacturer(manufacturer: str) -> list[str]:
    """Get all protocols for a specific manufacturer."""
    db = IRProtocolDatabase()
    return db.get_protocols_by_manufacturer(manufacturer)
