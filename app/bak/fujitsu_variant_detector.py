"""
Fujitsu AC variant detector.

Detects which Fujitsu protocol variant is being used based on sample IR code.
"""

from typing import Optional
from app.core.tuya_encoder import decode_tuya_ir
from app.core.ac_decoders import bits_to_bytes, timings_to_bits_space_encoding


def detect_fujitsu_variant(tuya_code: str) -> Optional[str]:
    """
    Detect Fujitsu AC protocol variant from a sample Tuya IR code.

    Args:
        tuya_code: Tuya Base64 IR code

    Returns:
        "3byte" for 12-byte 3-byte repeating pattern variant
        "16byte" for 7/16-byte IRremoteESP8266 variant
        None if not recognizable as Fujitsu
    """
    try:
        # Decode to bytes
        timings = decode_tuya_ir(tuya_code)
        bits = timings_to_bits_space_encoding(timings, threshold=700)
        state_bytes = bits_to_bytes(bits)

        # Detect variant based on byte length
        if len(state_bytes) == 12:
            # 3-byte repeating pattern variant
            return "3byte"
        elif len(state_bytes) in [7, 16]:
            # IRremoteESP8266 variant (7 = OFF, 16 = state command)
            return "16byte"
        else:
            # Unknown Fujitsu variant
            return None

    except Exception:
        # Decoding failed
        return None
