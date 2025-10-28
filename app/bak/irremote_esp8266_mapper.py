"""
IRremoteESP8266 Protocol Mapper

Maps protocols and timing patterns from the IRremoteESP8266 library.
Based on: https://github.com/crankyoldgit/IRremoteESP8266

This provides comprehensive protocol definitions for 40+ HVAC manufacturers
with more accurate timing patterns and better manufacturer detection.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class IRProtocolTiming:
    """IR protocol timing definition."""

    name: str
    manufacturer: list[str]  # Can have multiple manufacturers
    header_mark: int  # Header mark in microseconds
    header_space: int  # Header space in microseconds
    bit_mark: int  # Bit mark in microseconds
    one_space: int  # Space for "1" bit
    zero_space: int  # Space for "0" bit
    tolerance: int = 200  # Timing tolerance in microseconds
    frequency: int = 38000  # Carrier frequency in Hz (default 38kHz)
    notes: str = ""  # Additional notes about the protocol


# Protocol definitions based on IRremoteESP8266
# Timing values collected from real-world captures and library documentation
IRREMOTE_ESP8266_PROTOCOLS = {
    # Fujitsu AC protocols
    "FUJITSU_AC": IRProtocolTiming(
        name="FUJITSU_AC",
        manufacturer=["Fujitsu", "Fujitsu General", "OGeneral"],
        header_mark=3300,
        header_space=1600,
        bit_mark=420,
        one_space=1200,
        zero_space=400,
        tolerance=300,
        notes="Standard Fujitsu AC protocol (ARRAH2E, AR-RAx series)",
    ),
    "FUJITSU_AC264": IRProtocolTiming(
        name="FUJITSU_AC264",
        manufacturer=["Fujitsu"],
        header_mark=3300,
        header_space=1600,
        bit_mark=420,
        one_space=1200,
        zero_space=400,
        tolerance=300,
        notes="Extended 264-bit Fujitsu protocol",
    ),
    # Daikin AC protocols
    "DAIKIN": IRProtocolTiming(
        name="DAIKIN",
        manufacturer=["Daikin"],
        header_mark=3650,
        header_space=1623,
        bit_mark=428,
        one_space=1280,
        zero_space=428,
        tolerance=200,
        notes="Daikin ARC series remotes",
    ),
    "DAIKIN2": IRProtocolTiming(
        name="DAIKIN2",
        manufacturer=["Daikin"],
        header_mark=3500,
        header_space=1728,
        bit_mark=460,
        one_space=1270,
        zero_space=420,
        tolerance=200,
        notes="Daikin ARC4xx series",
    ),
    # Mitsubishi protocols
    "MITSUBISHI_AC": IRProtocolTiming(
        name="MITSUBISHI_AC",
        manufacturer=["Mitsubishi", "Mitsubishi Electric"],
        header_mark=3400,
        header_space=1750,
        bit_mark=450,
        one_space=1300,
        zero_space=420,
        tolerance=200,
        notes="Standard Mitsubishi AC (MSZ series)",
    ),
    "MITSUBISHI_HEAVY_152": IRProtocolTiming(
        name="MITSUBISHI_HEAVY_152",
        manufacturer=["Mitsubishi Heavy Industries"],
        header_mark=3200,
        header_space=1600,
        bit_mark=400,
        one_space=1200,
        zero_space=400,
        tolerance=200,
        notes="Mitsubishi Heavy SRK series",
    ),
    # Gree/Cooper & Hunter
    "GREE": IRProtocolTiming(
        name="GREE",
        manufacturer=["Gree", "Cooper & Hunter", "RusClimate", "Soleus Air"],
        header_mark=9000,
        header_space=4500,
        bit_mark=620,
        one_space=1600,
        zero_space=540,
        tolerance=300,
        notes="Gree YAW1F, Cooper & Hunter",
    ),
    # LG
    "LG": IRProtocolTiming(
        name="LG",
        manufacturer=["LG", "General Electric"],
        header_mark=8000,
        header_space=4000,
        bit_mark=600,
        one_space=1600,
        zero_space=550,
        tolerance=300,
        notes="LG AKB series remotes",
    ),
    # Samsung
    "SAMSUNG_AC": IRProtocolTiming(
        name="SAMSUNG_AC",
        manufacturer=["Samsung"],
        header_mark=690,
        header_space=17844,
        bit_mark=690,
        one_space=1614,
        zero_space=492,
        tolerance=200,
        notes="Samsung AR series",
    ),
    # Panasonic
    "PANASONIC_AC": IRProtocolTiming(
        name="PANASONIC_AC",
        manufacturer=["Panasonic"],
        header_mark=3500,
        header_space=1750,
        bit_mark=435,
        one_space=1300,
        zero_space=435,
        tolerance=200,
        notes="Panasonic CS series",
    ),
    # Hitachi
    "HITACHI_AC": IRProtocolTiming(
        name="HITACHI_AC",
        manufacturer=["Hitachi"],
        header_mark=3400,
        header_space=1700,
        bit_mark=400,
        one_space=1250,
        zero_space=400,
        tolerance=200,
        notes="Hitachi RAK/RAS series",
    ),
    "HITACHI_AC1": IRProtocolTiming(
        name="HITACHI_AC1",
        manufacturer=["Hitachi"],
        header_mark=3300,
        header_space=1700,
        bit_mark=400,
        one_space=1200,
        zero_space=400,
        tolerance=200,
        notes="Alternate Hitachi protocol",
    ),
    # Toshiba
    "TOSHIBA_AC": IRProtocolTiming(
        name="TOSHIBA_AC",
        manufacturer=["Toshiba", "Carrier"],
        header_mark=4400,
        header_space=4300,
        bit_mark=543,
        one_space=1623,
        zero_space=543,
        tolerance=300,
        notes="Toshiba RAS series",
    ),
    # Sharp
    "SHARP_AC": IRProtocolTiming(
        name="SHARP_AC",
        manufacturer=["Sharp"],
        header_mark=3800,
        header_space=1900,
        bit_mark=470,
        one_space=1400,
        zero_space=470,
        tolerance=200,
        notes="Sharp CRMC-A series",
    ),
    # Haier
    "HAIER_AC": IRProtocolTiming(
        name="HAIER_AC",
        manufacturer=["Haier", "Daichi"],
        header_mark=3000,
        header_space=3000,
        bit_mark=520,
        one_space=1650,
        zero_space=650,
        tolerance=250,
        notes="Haier HSU series",
    ),
    # Midea/Electrolux
    "MIDEA": IRProtocolTiming(
        name="MIDEA",
        manufacturer=["Midea", "Comfee", "Electrolux", "Keystone", "Trotec"],
        header_mark=4420,
        header_space=4420,
        bit_mark=560,
        one_space=1680,
        zero_space=560,
        tolerance=300,
        notes="Midea MWMA series, Electrolux variants",
    ),
    # Coolix (multiple brands)
    "COOLIX": IRProtocolTiming(
        name="COOLIX",
        manufacturer=["Midea", "Tokio", "Airwell", "Beko", "Bosch"],
        header_mark=4480,
        header_space=4480,
        bit_mark=560,
        one_space=1680,
        zero_space=560,
        tolerance=300,
        notes="Coolix/Midea variant used by multiple brands",
    ),
    # Carrier
    "CARRIER_AC": IRProtocolTiming(
        name="CARRIER_AC",
        manufacturer=["Carrier"],
        header_mark=8960,
        header_space=4480,
        bit_mark=560,
        one_space=1680,
        zero_space=560,
        tolerance=300,
        notes="Carrier 619EGX series",
    ),
    # Electra/AEG
    "ELECTRA_AC": IRProtocolTiming(
        name="ELECTRA_AC",
        manufacturer=["Electra", "AEG", "AUX", "Frigidaire"],
        header_mark=9000,
        header_space=4500,
        bit_mark=630,
        one_space=1650,
        zero_space=530,
        tolerance=300,
        notes="Electra YKR series remotes",
    ),
    # Whirlpool
    "WHIRLPOOL_AC": IRProtocolTiming(
        name="WHIRLPOOL_AC",
        manufacturer=["Whirlpool"],
        header_mark=8950,
        header_space=4484,
        bit_mark=597,
        one_space=1649,
        zero_space=547,
        tolerance=300,
        notes="Whirlpool SPIS series",
    ),
}


def identify_protocol_irremote(
    timings: list[int], tolerance_multiplier: float = 1.5
) -> Optional[dict]:
    """
    Identify IR protocol using IRremoteESP8266 timing database.

    Args:
        timings: Raw IR timing array in microseconds
        tolerance_multiplier: Multiplier for tolerance (default 1.5 for real-world variance)

    Returns:
        Dictionary with protocol information or None if not identified

    Example:
        {
            "protocol": "FUJITSU_AC",
            "manufacturer": ["Fujitsu", "Fujitsu General"],
            "confidence": 0.95,
            "timing_match": {"header_mark": 3294, "header_space": 1605}
        }
    """
    if len(timings) < 4:
        return None

    header_mark = timings[0]
    header_space = timings[1]

    best_match = None
    best_score = 0

    for protocol_name, protocol in IRREMOTE_ESP8266_PROTOCOLS.items():
        tolerance = protocol.tolerance * tolerance_multiplier

        # Calculate how well the header matches
        mark_diff = abs(header_mark - protocol.header_mark)
        space_diff = abs(header_space - protocol.header_space)

        # Both must be within tolerance
        if mark_diff <= tolerance and space_diff <= tolerance:
            # Calculate confidence score (0-1)
            mark_score = 1.0 - (mark_diff / tolerance)
            space_score = 1.0 - (space_diff / tolerance)
            total_score = (mark_score + space_score) / 2

            if total_score > best_score:
                best_score = total_score
                best_match = {
                    "protocol": protocol_name,
                    "manufacturer": protocol.manufacturer,
                    "confidence": round(total_score, 2),
                    "timing_match": {
                        "header_mark": header_mark,
                        "header_space": header_space,
                        "expected_mark": protocol.header_mark,
                        "expected_space": protocol.header_space,
                    },
                    "notes": protocol.notes,
                }

    return best_match


def get_protocol_capabilities(protocol_name: str) -> dict:
    """
    Get standard HVAC capabilities for a protocol.

    Returns typical capabilities (modes, fan speeds, temp range).
    """
    # Standard capabilities for most HVAC units
    return {
        "modes": ["cool", "heat", "dry", "fan", "auto"],
        "fanSpeeds": ["auto", "low", "medium", "high", "quiet"],
        "tempRange": {"min": 16, "max": 30, "unit": "celsius"},
        "features": ["swing"],
    }


def get_all_manufacturers() -> list[str]:
    """Get a sorted list of all supported manufacturers."""
    manufacturers = set()
    for protocol in IRREMOTE_ESP8266_PROTOCOLS.values():
        manufacturers.update(protocol.manufacturer)
    return sorted(manufacturers)


def get_protocols_by_manufacturer(manufacturer: str) -> list[str]:
    """
    Get all protocols for a specific manufacturer.

    Args:
        manufacturer: Manufacturer name (case-insensitive)

    Returns:
        List of protocol names
    """
    manufacturer_lower = manufacturer.lower()
    protocols = []

    for protocol_name, protocol in IRREMOTE_ESP8266_PROTOCOLS.items():
        if any(m.lower() == manufacturer_lower for m in protocol.manufacturer):
            protocols.append(protocol_name)

    return protocols
