#!/usr/bin/env python3
"""
Extract protocol timing constants from IRremoteESP8266.

This script generates a Python module with protocol timing constants
extracted from IRremoteESP8266 v2.8.6, eliminating the need for C++ bindings.
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_FILE = PROJECT_ROOT / "app" / "core" / "protocol_timings.py"

# Protocol timing patterns extracted from IRremoteESP8266 v2.8.6 source
# Format: (protocol_name, manufacturer_list, header_mark_us, header_space_us,
#          bit_mark_us, one_space_us, zero_space_us, frequency_khz)
KNOWN_TIMINGS = [
    # Fujitsu (from ir_Fujitsu.cpp timing analysis)
    ("FUJITSU_AC", ["Fujitsu", "Fujitsu General", "OGeneral"],
     3300, 1600, 420, 1200, 400, 38),

    # Daikin (from ir_Daikin.cpp)
    ("DAIKIN", ["Daikin"],
     3650, 1623, 428, 1280, 428, 38),
    ("DAIKIN2", ["Daikin"],
     3500, 1728, 460, 1270, 420, 38),

    # Mitsubishi (from ir_Mitsubishi.cpp)
    ("MITSUBISHI_AC", ["Mitsubishi", "Mitsubishi Electric"],
     3400, 1750, 450, 1300, 420, 38),
    ("MITSUBISHI_HEAVY_152", ["Mitsubishi Heavy Industries"],
     3200, 1600, 400, 1200, 400, 38),

    # Gree (from ir_Gree.cpp)
    ("GREE", ["Gree", "Cooper & Hunter", "RusClimate", "Soleus Air"],
     9000, 4500, 620, 1600, 540, 38),

    # LG (from ir_LG.cpp)
    ("LG", ["LG", "General Electric"],
     8000, 4000, 600, 1600, 550, 38),

    # Samsung (from ir_Samsung.cpp)
    ("SAMSUNG_AC", ["Samsung"],
     690, 17844, 690, 1614, 492, 38),

    # Panasonic (from ir_Panasonic.cpp)
    ("PANASONIC_AC", ["Panasonic"],
     3500, 1750, 435, 1300, 435, 38),

    # Hitachi (from ir_Hitachi.cpp)
    ("HITACHI_AC", ["Hitachi"],
     3400, 1700, 400, 1250, 400, 38),
    ("HITACHI_AC1", ["Hitachi"],
     3300, 1700, 400, 1200, 400, 38),

    # Toshiba (from ir_Toshiba.cpp)
    ("TOSHIBA_AC", ["Toshiba", "Carrier"],
     4400, 4300, 543, 1623, 543, 38),

    # Sharp (from ir_Sharp.cpp)
    ("SHARP_AC", ["Sharp"],
     3800, 1900, 470, 1400, 470, 38),

    # Haier (from ir_Haier.cpp)
    ("HAIER_AC", ["Haier", "Daichi"],
     3000, 3000, 520, 1650, 650, 38),

    # Midea (from ir_Midea.cpp)
    ("MIDEA", ["Midea", "Comfee", "Electrolux", "Keystone", "Trotec"],
     4420, 4420, 560, 1680, 560, 38),

    # Coolix (from ir_Coolix.cpp)
    ("COOLIX", ["Midea", "Tokio", "Airwell", "Beko", "Bosch"],
     4480, 4480, 560, 1680, 560, 38),

    # Carrier (from ir_Carrier.cpp)
    ("CARRIER_AC", ["Carrier"],
     8960, 4480, 560, 1680, 560, 38),

    # Electra (from ir_Electra.cpp)
    ("ELECTRA_AC", ["Electra", "AEG", "AUX", "Frigidaire"],
     9000, 4500, 630, 1650, 530, 38),

    # Whirlpool (from ir_Whirlpool.cpp)
    ("WHIRLPOOL_AC", ["Whirlpool"],
     8950, 4484, 597, 1649, 547, 38),

    # Kelvinator (from ir_Kelvinator.cpp)
    ("KELVINATOR", ["Kelvinator"],
     9000, 4500, 630, 1650, 530, 38),

    # Argo (from ir_Argo.cpp)
    ("ARGO", ["Argo", "Airwell"],
     6400, 3300, 400, 900, 400, 38),

    # Teco (from ir_Teco.cpp)
    ("TECO", ["Teco"],
     9000, 4440, 620, 1650, 620, 38),

    # Tcl (from ir_Tcl.cpp)
    ("TCL112AC", ["TCL", "Clima"],
     3000, 1650, 500, 1050, 500, 38),

    # Neoclima (from ir_Neoclima.cpp)
    ("NEOCLIMA", ["Neoclima", "Airwell"],
     6112, 3000, 537, 1391, 537, 38),

    # Vestel (from ir_Vestel.cpp)
    ("VESTEL_AC", ["Vestel"],
     9000, 4500, 563, 1688, 563, 38),

    # Truma (from ir_Truma.cpp)
    ("TRUMA", ["Truma"],
     6000, 3000, 500, 1500, 500, 38),

    # Goodweather (from ir_Goodweather.cpp)
    ("GOODWEATHER", ["Goodweather"],
     6820, 2679, 404, 1181, 404, 38),

    # Bosch (from ir_Bosch.cpp)
    ("BOSCH144", ["Bosch"],
     4500, 4400, 550, 1600, 550, 38),

    # York (from ir_York.cpp)
    ("YORK", ["York"],
     7940, 3990, 530, 1560, 530, 38),

    # Airwell (from ir_Airwell.cpp)
    ("AIRWELL", ["Airwell"],
     3100, 1590, 430, 1200, 430, 38),

    # Delonghi (from ir_Delonghi.cpp)
    ("DELONGHI_AC", ["Delonghi"],
     8950, 4500, 550, 1650, 550, 38),

    # Corona (from ir_Corona.cpp)
    ("CORONA_AC", ["Corona"],
     3550, 1700, 435, 1250, 435, 38),
]


def generate_python_module() -> str:
    """Generate the protocol_timings.py Python module content."""

    module = '''"""
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
'''

    for timing in KNOWN_TIMINGS:
        name, mfrs, hm, hs, bm, os, zs, freq = timing

        # Format manufacturers list
        mfr_list = ", ".join(f'"{m}"' for m in mfrs)

        module += f"""    # {name} - {", ".join(mfrs)}
    ProtocolTiming(
        name="{name}",
        manufacturers=[{mfr_list}],
        header_mark={hm},
        header_space={hs},
        bit_mark={bm},
        one_space={os},
        zero_space={zs},
        frequency_khz={freq},
        tolerance=300,
    ),

"""

    module += """]


def get_all_manufacturers() -> List[str]:
    \"""Get sorted list of all unique manufacturers.\"""
    manufacturers = set()
    for proto in PROTOCOL_TIMINGS:
        manufacturers.update(proto.manufacturers)
    return sorted(manufacturers)


def get_protocols_by_manufacturer(manufacturer: str) -> List[str]:
    \"""Get all protocol names for a given manufacturer.\"""
    mfr_lower = manufacturer.lower()
    result = []
    for proto in PROTOCOL_TIMINGS:
        if any(m.lower() == mfr_lower for m in proto.manufacturers):
            result.append(proto.name)
    return result


def identify_protocol(
    timings: List[int], tolerance_multiplier: float = 1.5
) -> Optional[Dict[str, Any]]:
    \"""
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
    \"""
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

    return {
        "protocol": best_match.name,
        "manufacturer": best_match.manufacturers,
        "confidence": round(best_score, 2),
        "timing_match": {
            "header_mark": header_mark,
            "header_space": header_space,
            "expected_mark": best_match.header_mark,
            "expected_space": best_match.header_space,
        },
    }
"""

    return module


def main():
    """Generate the protocol timings Python module."""
    print("=" * 60)
    print("Generating Protocol Timing Constants (Pure Python)")
    print("=" * 60)
    print(f"Source: IRremoteESP8266 v2.8.6")
    print(f"Output: {OUTPUT_FILE}")
    print()

    # Generate Python module content
    content = generate_python_module()

    # Ensure output directory exists
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Write to file
    OUTPUT_FILE.write_text(content)

    print(f"✅ Generated pure Python protocol timing module")
    print(f"   Protocols: {len(KNOWN_TIMINGS)}")
    print(f"   Output: {OUTPUT_FILE}")
    print(f"   No C++ compilation required!")
    print()

    # List all protocols
    print("Protocols included:")
    for timing in KNOWN_TIMINGS:
        name, mfrs, *_ = timing
        print(f"  - {name:25s} {', '.join(mfrs)}")

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
