"""
Tuya IR format conversion utilities.

Handles encoding and decoding between Tuya Base64 format and raw IR timings.
"""

import base64
import struct
import io
from app.core.fastlz import fastlz_decompress, fastlz_compress


def decode_tuya_ir(tuya_code: str) -> list[int]:
    """
    Convert Tuya Base64 IR code to raw timing array.

    Process:
    1. Base64 decode
    2. FastLZ decompress
    3. Unpack 16-bit little-endian integers to microsecond timings

    Args:
        tuya_code: Base64 encoded Tuya IR code

    Returns:
        List of microsecond timings [9000, 4500, 600, ...]

    Raises:
        ValueError: If the code is invalid or cannot be decoded
    """
    try:
        # 1. Base64 decode
        compressed = base64.b64decode(tuya_code)

        # 2. FastLZ decompress
        raw_bytes = fastlz_decompress(compressed)

        # 3. Unpack 16-bit little-endian integers
        timings = []
        for i in range(0, len(raw_bytes), 2):
            if i + 1 < len(raw_bytes):
                timing = struct.unpack("<H", raw_bytes[i : i + 2])[0]
                timings.append(timing)

        return timings

    except Exception as e:
        raise ValueError(f"Failed to decode Tuya IR code: {str(e)}") from e


def encode_tuya_ir(timings: list[int]) -> str:
    """
    Convert raw timing array to Tuya Base64 IR code.

    Process:
    1. Pack as 16-bit little-endian integers
    2. FastLZ compress
    3. Base64 encode

    Args:
        timings: List of microsecond timings

    Returns:
        Base64 encoded Tuya IR code

    Raises:
        ValueError: If the timings are invalid
    """
    try:
        # 1. Pack as 16-bit little-endian integers
        raw_bytes = b""
        for timing in timings:
            if timing < 0 or timing > 65535:
                raise ValueError(f"Timing value {timing} out of range (0-65535)")
            raw_bytes += struct.pack("<H", timing)

        # 2. FastLZ compress
        compressed = fastlz_compress(raw_bytes)

        # 3. Base64 encode
        tuya_code = base64.b64encode(compressed).decode("ascii")

        return tuya_code

    except Exception as e:
        raise ValueError(f"Failed to encode Tuya IR code: {str(e)}") from e


def validate_tuya_code(tuya_code: str) -> bool:
    """
    Validate if a string is a valid Tuya IR code.

    Args:
        tuya_code: String to validate

    Returns:
        True if valid, False otherwise
    """
    try:
        decode_tuya_ir(tuya_code)
        return True
    except Exception:
        return False
