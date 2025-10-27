"""
IR Protocol timing constants extracted from IRremoteESP8266 v2.8.6

Auto-generated from IRremoteESP8266 source code.
DO NOT EDIT - Run scripts/generate_protocol_timings.py to regenerate

All timing values are in microseconds (μs).
"""

from typing import List, Dict, Any, Optional


class ProtocolTiming:
    """IR Protocol timing definition."""

    def __init__(
        self,
        name: str,
        manufacturers: List[str],
        header_mark: int,
        header_space: int,
        bit_mark: int,
        one_space: int,
        zero_space: int,
        frequency_khz: int = 38,
        tolerance: int = 300,
    ):
        self.name = name
        self.manufacturers = manufacturers
        self.header_mark = header_mark
        self.header_space = header_space
        self.bit_mark = bit_mark
        self.one_space = one_space
        self.zero_space = zero_space
        self.frequency_khz = frequency_khz
        self.tolerance = tolerance

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "manufacturers": self.manufacturers,
            "header_mark": self.header_mark,
            "header_space": self.header_space,
            "bit_mark": self.bit_mark,
            "one_space": self.one_space,
            "zero_space": self.zero_space,
            "frequency_khz": self.frequency_khz,
            "tolerance": self.tolerance,
        }


# Protocol timing database extracted from IRremoteESP8266 v2.8.6
PROTOCOL_TIMINGS: List[ProtocolTiming] = [
    # FUJITSU_AC - Fujitsu, Fujitsu General, OGeneral
    ProtocolTiming(
        name="FUJITSU_AC",
        manufacturers=["Fujitsu", "Fujitsu General", "OGeneral"],
        header_mark=3300,
        header_space=1600,
        bit_mark=420,
        one_space=1200,
        zero_space=400,
        frequency_khz=38,
        tolerance=300,
    ),

    # DAIKIN - Daikin
    ProtocolTiming(
        name="DAIKIN",
        manufacturers=["Daikin"],
        header_mark=3650,
        header_space=1623,
        bit_mark=428,
        one_space=1280,
        zero_space=428,
        frequency_khz=38,
        tolerance=300,
    ),

    # DAIKIN2 - Daikin
    ProtocolTiming(
        name="DAIKIN2",
        manufacturers=["Daikin"],
        header_mark=3500,
        header_space=1728,
        bit_mark=460,
        one_space=1270,
        zero_space=420,
        frequency_khz=38,
        tolerance=300,
    ),

    # MITSUBISHI_AC - Mitsubishi, Mitsubishi Electric
    ProtocolTiming(
        name="MITSUBISHI_AC",
        manufacturers=["Mitsubishi", "Mitsubishi Electric"],
        header_mark=3400,
        header_space=1750,
        bit_mark=450,
        one_space=1300,
        zero_space=420,
        frequency_khz=38,
        tolerance=300,
    ),

    # MITSUBISHI_HEAVY_152 - Mitsubishi Heavy Industries
    ProtocolTiming(
        name="MITSUBISHI_HEAVY_152",
        manufacturers=["Mitsubishi Heavy Industries"],
        header_mark=3200,
        header_space=1600,
        bit_mark=400,
        one_space=1200,
        zero_space=400,
        frequency_khz=38,
        tolerance=300,
    ),

    # GREE - Gree, Cooper & Hunter, RusClimate, Soleus Air
    ProtocolTiming(
        name="GREE",
        manufacturers=["Gree", "Cooper & Hunter", "RusClimate", "Soleus Air"],
        header_mark=9000,
        header_space=4500,
        bit_mark=620,
        one_space=1600,
        zero_space=540,
        frequency_khz=38,
        tolerance=300,
    ),

    # LG - LG, General Electric
    ProtocolTiming(
        name="LG",
        manufacturers=["LG", "General Electric"],
        header_mark=8000,
        header_space=4000,
        bit_mark=600,
        one_space=1600,
        zero_space=550,
        frequency_khz=38,
        tolerance=300,
    ),

    # SAMSUNG_AC - Samsung
    ProtocolTiming(
        name="SAMSUNG_AC",
        manufacturers=["Samsung"],
        header_mark=690,
        header_space=17844,
        bit_mark=690,
        one_space=1614,
        zero_space=492,
        frequency_khz=38,
        tolerance=300,
    ),

    # PANASONIC_AC - Panasonic
    ProtocolTiming(
        name="PANASONIC_AC",
        manufacturers=["Panasonic"],
        header_mark=3500,
        header_space=1750,
        bit_mark=435,
        one_space=1300,
        zero_space=435,
        frequency_khz=38,
        tolerance=300,
    ),

    # HITACHI_AC - Hitachi
    ProtocolTiming(
        name="HITACHI_AC",
        manufacturers=["Hitachi"],
        header_mark=3400,
        header_space=1700,
        bit_mark=400,
        one_space=1250,
        zero_space=400,
        frequency_khz=38,
        tolerance=300,
    ),

    # HITACHI_AC1 - Hitachi
    ProtocolTiming(
        name="HITACHI_AC1",
        manufacturers=["Hitachi"],
        header_mark=3300,
        header_space=1700,
        bit_mark=400,
        one_space=1200,
        zero_space=400,
        frequency_khz=38,
        tolerance=300,
    ),

    # TOSHIBA_AC - Toshiba, Carrier
    ProtocolTiming(
        name="TOSHIBA_AC",
        manufacturers=["Toshiba", "Carrier"],
        header_mark=4400,
        header_space=4300,
        bit_mark=543,
        one_space=1623,
        zero_space=543,
        frequency_khz=38,
        tolerance=300,
    ),

    # SHARP_AC - Sharp
    ProtocolTiming(
        name="SHARP_AC",
        manufacturers=["Sharp"],
        header_mark=3800,
        header_space=1900,
        bit_mark=470,
        one_space=1400,
        zero_space=470,
        frequency_khz=38,
        tolerance=300,
    ),

    # HAIER_AC - Haier, Daichi
    ProtocolTiming(
        name="HAIER_AC",
        manufacturers=["Haier", "Daichi"],
        header_mark=3000,
        header_space=3000,
        bit_mark=520,
        one_space=1650,
        zero_space=650,
        frequency_khz=38,
        tolerance=300,
    ),

    # MIDEA - Midea, Comfee, Electrolux, Keystone, Trotec
    ProtocolTiming(
        name="MIDEA",
        manufacturers=["Midea", "Comfee", "Electrolux", "Keystone", "Trotec"],
        header_mark=4420,
        header_space=4420,
        bit_mark=560,
        one_space=1680,
        zero_space=560,
        frequency_khz=38,
        tolerance=300,
    ),

    # COOLIX - Midea, Tokio, Airwell, Beko, Bosch
    ProtocolTiming(
        name="COOLIX",
        manufacturers=["Midea", "Tokio", "Airwell", "Beko", "Bosch"],
        header_mark=4480,
        header_space=4480,
        bit_mark=560,
        one_space=1680,
        zero_space=560,
        frequency_khz=38,
        tolerance=300,
    ),

    # CARRIER_AC - Carrier
    ProtocolTiming(
        name="CARRIER_AC",
        manufacturers=["Carrier"],
        header_mark=8960,
        header_space=4480,
        bit_mark=560,
        one_space=1680,
        zero_space=560,
        frequency_khz=38,
        tolerance=300,
    ),

    # ELECTRA_AC - Electra, AEG, AUX, Frigidaire
    ProtocolTiming(
        name="ELECTRA_AC",
        manufacturers=["Electra", "AEG", "AUX", "Frigidaire"],
        header_mark=9000,
        header_space=4500,
        bit_mark=630,
        one_space=1650,
        zero_space=530,
        frequency_khz=38,
        tolerance=300,
    ),

    # WHIRLPOOL_AC - Whirlpool
    ProtocolTiming(
        name="WHIRLPOOL_AC",
        manufacturers=["Whirlpool"],
        header_mark=8950,
        header_space=4484,
        bit_mark=597,
        one_space=1649,
        zero_space=547,
        frequency_khz=38,
        tolerance=300,
    ),

    # KELVINATOR - Kelvinator
    ProtocolTiming(
        name="KELVINATOR",
        manufacturers=["Kelvinator"],
        header_mark=9000,
        header_space=4500,
        bit_mark=630,
        one_space=1650,
        zero_space=530,
        frequency_khz=38,
        tolerance=300,
    ),

    # ARGO - Argo, Airwell
    ProtocolTiming(
        name="ARGO",
        manufacturers=["Argo", "Airwell"],
        header_mark=6400,
        header_space=3300,
        bit_mark=400,
        one_space=900,
        zero_space=400,
        frequency_khz=38,
        tolerance=300,
    ),

    # TECO - Teco
    ProtocolTiming(
        name="TECO",
        manufacturers=["Teco"],
        header_mark=9000,
        header_space=4440,
        bit_mark=620,
        one_space=1650,
        zero_space=620,
        frequency_khz=38,
        tolerance=300,
    ),

    # TCL112AC - TCL, Clima
    ProtocolTiming(
        name="TCL112AC",
        manufacturers=["TCL", "Clima"],
        header_mark=3000,
        header_space=1650,
        bit_mark=500,
        one_space=1050,
        zero_space=500,
        frequency_khz=38,
        tolerance=300,
    ),

    # NEOCLIMA - Neoclima, Airwell
    ProtocolTiming(
        name="NEOCLIMA",
        manufacturers=["Neoclima", "Airwell"],
        header_mark=6112,
        header_space=3000,
        bit_mark=537,
        one_space=1391,
        zero_space=537,
        frequency_khz=38,
        tolerance=300,
    ),

    # VESTEL_AC - Vestel
    ProtocolTiming(
        name="VESTEL_AC",
        manufacturers=["Vestel"],
        header_mark=9000,
        header_space=4500,
        bit_mark=563,
        one_space=1688,
        zero_space=563,
        frequency_khz=38,
        tolerance=300,
    ),

    # TRUMA - Truma
    ProtocolTiming(
        name="TRUMA",
        manufacturers=["Truma"],
        header_mark=6000,
        header_space=3000,
        bit_mark=500,
        one_space=1500,
        zero_space=500,
        frequency_khz=38,
        tolerance=300,
    ),

    # GOODWEATHER - Goodweather
    ProtocolTiming(
        name="GOODWEATHER",
        manufacturers=["Goodweather"],
        header_mark=6820,
        header_space=2679,
        bit_mark=404,
        one_space=1181,
        zero_space=404,
        frequency_khz=38,
        tolerance=300,
    ),

    # BOSCH144 - Bosch
    ProtocolTiming(
        name="BOSCH144",
        manufacturers=["Bosch"],
        header_mark=4500,
        header_space=4400,
        bit_mark=550,
        one_space=1600,
        zero_space=550,
        frequency_khz=38,
        tolerance=300,
    ),

    # YORK - York
    ProtocolTiming(
        name="YORK",
        manufacturers=["York"],
        header_mark=7940,
        header_space=3990,
        bit_mark=530,
        one_space=1560,
        zero_space=530,
        frequency_khz=38,
        tolerance=300,
    ),

    # AIRWELL - Airwell
    ProtocolTiming(
        name="AIRWELL",
        manufacturers=["Airwell"],
        header_mark=3100,
        header_space=1590,
        bit_mark=430,
        one_space=1200,
        zero_space=430,
        frequency_khz=38,
        tolerance=300,
    ),

    # DELONGHI_AC - Delonghi
    ProtocolTiming(
        name="DELONGHI_AC",
        manufacturers=["Delonghi"],
        header_mark=8950,
        header_space=4500,
        bit_mark=550,
        one_space=1650,
        zero_space=550,
        frequency_khz=38,
        tolerance=300,
    ),

    # CORONA_AC - Corona
    ProtocolTiming(
        name="CORONA_AC",
        manufacturers=["Corona"],
        header_mark=3550,
        header_space=1700,
        bit_mark=435,
        one_space=1250,
        zero_space=435,
        frequency_khz=38,
        tolerance=300,
    ),

]


def get_all_manufacturers() -> List[str]:
    """Get sorted list of all unique manufacturers."""
    manufacturers = set()
    for proto in PROTOCOL_TIMINGS:
        manufacturers.update(proto.manufacturers)
    return sorted(manufacturers)


def get_protocols_by_manufacturer(manufacturer: str) -> List[str]:
    """Get all protocol names for a given manufacturer."""
    mfr_lower = manufacturer.lower()
    result = []
    for proto in PROTOCOL_TIMINGS:
        if any(m.lower() == mfr_lower for m in proto.manufacturers):
            result.append(proto.name)
    return result


def identify_protocol(
    timings: List[int], tolerance_multiplier: float = 1.5
) -> Optional[Dict[str, Any]]:
    """
    Identify IR protocol from raw timing data.

    Args:
        timings: Array of timing values in microseconds [mark, space, mark, space, ...]
        tolerance_multiplier: Adjust tolerance (1.0 = default, 1.5 = more lenient)

    Returns:
        Dictionary with protocol info, or None if no match:
        {
            "protocol": str,
            "manufacturer": List[str],
            "confidence": float,
            "timing_match": {
                "header_mark": int,
                "header_space": int,
                "expected_mark": int,
                "expected_space": int,
            }
        }
    """
    if len(timings) < 4:
        return None

    header_mark = timings[0]
    header_space = timings[1]

    best_match = None
    best_score = 0.0

    for proto in PROTOCOL_TIMINGS:
        tolerance = int(proto.tolerance * tolerance_multiplier)

        mark_diff = abs(header_mark - proto.header_mark)
        space_diff = abs(header_space - proto.header_space)

        if mark_diff <= tolerance and space_diff <= tolerance:
            mark_score = 1.0 - (mark_diff / tolerance)
            space_score = 1.0 - (space_diff / tolerance)
            total_score = (mark_score + space_score) / 2.0

            if total_score > best_score:
                best_score = total_score
                best_match = proto

    if best_match is None:
        return None

    # Default HVAC capabilities
    capabilities = {
        "modes": ["cool", "heat", "dry", "fan", "auto"],
        "fanSpeeds": ["auto", "low", "medium", "high"],
        "tempRange": {"min": 16, "max": 30, "unit": "celsius"},
        "features": ["swing"],
    }

    return {
        "protocol": best_match.name,
        "manufacturer": best_match.manufacturers[0] if best_match.manufacturers else "Unknown",
        "confidence": round(best_score, 2),
        "capabilities": capabilities,
        "source": "irremote_esp8266",
        "timing_match": {
            "header_mark": header_mark,
            "header_space": header_space,
            "expected_mark": best_match.header_mark,
            "expected_space": best_match.header_space,
        },
    }


def get_protocol_by_name(protocol_name: str) -> Optional[ProtocolTiming]:
    """
    Get protocol definition by name (case-insensitive).

    Args:
        protocol_name: Protocol name (e.g., "fujitsu_ac" or "FUJITSU_AC")

    Returns:
        ProtocolTiming or None if not found
    """
    protocol_lower = protocol_name.lower().replace(" ", "_")

    for proto in PROTOCOL_TIMINGS:
        if proto.name.lower() == protocol_lower:
            return proto

    return None


def get_supported_manufacturers() -> List[str]:
    """
    Get sorted list of unique manufacturers from all protocols.

    Returns:
        Sorted list of manufacturer names
    """
    return get_all_manufacturers()


def parse_hvac_state(timings: List[int], protocol: str) -> Dict[str, Any]:
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
