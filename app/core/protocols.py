"""
HVAC IR protocol detection and identification.

Identifies manufacturer and protocol from IR timing patterns.
"""

from typing import Optional


class ProtocolDefinition:
    """Definition of an HVAC IR protocol."""

    def __init__(
        self,
        name: str,
        manufacturer: str,
        header: tuple[int, int],
        tolerance: int = 200,
        capabilities: Optional[dict] = None,
    ):
        self.name = name
        self.manufacturer = manufacturer
        self.header = header  # (mark, space) in microseconds
        self.tolerance = tolerance
        self.capabilities = capabilities or self._default_capabilities()

    def _default_capabilities(self) -> dict:
        """Default HVAC capabilities."""
        return {
            "modes": ["cool", "heat", "dry", "fan", "auto"],
            "fanSpeeds": ["low", "medium", "high", "auto"],
            "tempRange": {"min": 16, "max": 30, "unit": "celsius"},
            "features": ["swing"],
        }

    def matches(self, timings: list[int]) -> bool:
        """
        Check if timing pattern matches this protocol.

        Args:
            timings: Raw IR timing array

        Returns:
            True if timings match this protocol
        """
        if len(timings) < 2:
            return False

        # Check header timing
        mark, space = self.header
        return (
            abs(timings[0] - mark) <= self.tolerance
            and abs(timings[1] - space) <= self.tolerance
        )


# Protocol definitions for supported manufacturers
PROTOCOLS = {
    "fujitsu_ac": ProtocolDefinition(
        name="fujitsu_ac",
        manufacturer="Fujitsu",
        header=(9000, 4500),
        tolerance=300,
        capabilities={
            "modes": ["cool", "heat", "dry", "fan", "auto"],
            "fanSpeeds": ["low", "medium", "high", "auto", "quiet"],
            "tempRange": {"min": 16, "max": 30, "unit": "celsius"},
            "features": ["swing", "quiet", "powerful"],
        },
    ),
    "fujitsu_ac_alt": ProtocolDefinition(
        name="fujitsu_ac_alt",
        manufacturer="Fujitsu",
        header=(3300, 1600),
        tolerance=300,
        capabilities={
            "modes": ["cool", "heat", "dry", "fan", "auto"],
            "fanSpeeds": ["low", "medium", "high", "auto", "quiet"],
            "tempRange": {"min": 16, "max": 30, "unit": "celsius"},
            "features": ["swing", "quiet", "powerful"],
        },
    ),
    "daikin_ac": ProtocolDefinition(
        name="daikin_ac",
        manufacturer="Daikin",
        header=(3500, 1728),
        tolerance=200,
        capabilities={
            "modes": ["cool", "heat", "dry", "fan", "auto"],
            "fanSpeeds": ["low", "medium", "high", "auto", "quiet"],
            "tempRange": {"min": 18, "max": 30, "unit": "celsius"},
            "features": ["swing", "quiet", "powerful", "econo"],
        },
    ),
    "mitsubishi_ac": ProtocolDefinition(
        name="mitsubishi_ac",
        manufacturer="Mitsubishi",
        header=(3400, 1750),
        tolerance=200,
        capabilities={
            "modes": ["cool", "heat", "dry", "fan", "auto"],
            "fanSpeeds": ["low", "medium", "high", "auto", "quiet"],
            "tempRange": {"min": 16, "max": 31, "unit": "celsius"},
            "features": ["swing", "quiet"],
        },
    ),
    "gree_ac": ProtocolDefinition(
        name="gree_ac",
        manufacturer="Gree",
        header=(9000, 4500),
        tolerance=300,
        capabilities={
            "modes": ["cool", "heat", "dry", "fan", "auto"],
            "fanSpeeds": ["low", "medium", "high", "auto"],
            "tempRange": {"min": 16, "max": 30, "unit": "celsius"},
            "features": ["swing", "turbo", "light"],
        },
    ),
    "carrier_ac": ProtocolDefinition(
        name="carrier_ac",
        manufacturer="Carrier",
        header=(8960, 4480),
        tolerance=300,
        capabilities={
            "modes": ["cool", "heat", "dry", "fan", "auto"],
            "fanSpeeds": ["low", "medium", "high", "auto"],
            "tempRange": {"min": 17, "max": 30, "unit": "celsius"},
            "features": ["swing"],
        },
    ),
    "hisense_ac": ProtocolDefinition(
        name="hisense_ac",
        manufacturer="Hisense",
        header=(9000, 4500),
        tolerance=300,
    ),
    "hitachi_ac": ProtocolDefinition(
        name="hitachi_ac",
        manufacturer="Hitachi",
        header=(3400, 1700),
        tolerance=200,
    ),
    "hyundai_ac": ProtocolDefinition(
        name="hyundai_ac",
        manufacturer="Hyundai",
        header=(8800, 4400),
        tolerance=300,
    ),
}


def identify_protocol(timings: list[int], manufacturer_hint: Optional[str] = None) -> dict:
    """
    Identify HVAC protocol from raw IR timings.

    Uses timing pattern analysis to match against known protocols.

    Args:
        timings: Raw microsecond timing array
        manufacturer_hint: Optional manufacturer name to prioritize

    Returns:
        {
            "protocol": "fujitsu_ac",
            "manufacturer": "Fujitsu",
            "confidence": 0.95,
            "capabilities": {...}
        }

    Raises:
        ValueError: If no protocol matches the timings
    """
    if not timings or len(timings) < 2:
        raise ValueError("Insufficient timing data for protocol identification")

    # If manufacturer hint provided, try that first
    if manufacturer_hint:
        for protocol_name, protocol in PROTOCOLS.items():
            if protocol.manufacturer.lower() == manufacturer_hint.lower():
                if protocol.matches(timings):
                    return {
                        "protocol": protocol.name,
                        "manufacturer": protocol.manufacturer,
                        "confidence": 0.98,
                        "capabilities": protocol.capabilities,
                    }

    # Try all protocols
    matches = []
    for protocol_name, protocol in PROTOCOLS.items():
        if protocol.matches(timings):
            # Calculate confidence based on header match quality
            mark_diff = abs(timings[0] - protocol.header[0])
            space_diff = abs(timings[1] - protocol.header[1])
            total_diff = mark_diff + space_diff
            confidence = max(0.5, 1.0 - (total_diff / (protocol.tolerance * 2)))
            matches.append((protocol, confidence))

    if not matches:
        raise ValueError(
            f"Could not identify protocol. Header: [{timings[0]}, {timings[1]}]"
        )

    # Return best match
    best_protocol, best_confidence = max(matches, key=lambda x: x[1])
    return {
        "protocol": best_protocol.name,
        "manufacturer": best_protocol.manufacturer,
        "confidence": round(best_confidence, 2),
        "capabilities": best_protocol.capabilities,
    }


def get_protocol_by_name(protocol_name: str) -> Optional[ProtocolDefinition]:
    """
    Get protocol definition by name.

    Args:
        protocol_name: Protocol name (e.g., "fujitsu_ac")

    Returns:
        ProtocolDefinition or None if not found
    """
    return PROTOCOLS.get(protocol_name)


def get_supported_manufacturers() -> list[str]:
    """
    Get list of supported manufacturer names.

    Returns:
        List of manufacturer names
    """
    return sorted(set(p.manufacturer for p in PROTOCOLS.values()))


def parse_hvac_state(timings: list[int], protocol: str) -> dict:
    """
    Parse HVAC state from IR timings.

    Note: This is a simplified implementation. Real implementation would
    decode the actual bit patterns for each protocol.

    Args:
        timings: Raw IR timing array
        protocol: Protocol name

    Returns:
        Dictionary with power, mode, temperature, fan, swing settings
    """
    # This is a placeholder - real implementation would decode bit patterns
    # For now, return default/unknown state
    return {
        "power": "unknown",
        "mode": "unknown",
        "temperature": None,
        "fan": "unknown",
        "swing": "unknown",
    }
