"""
Tests for Tuya IR format conversion.
"""

import pytest

from app.core.tuya import decode_tuya_ir, encode_tuya_ir, validate_tuya_code


def test_tuya_encode_decode_round_trip():
    """Test that encode->decode returns original timings."""
    original_timings = [9000, 4500, 600, 540, 600, 1600, 600, 540]
    tuya_code = encode_tuya_ir(original_timings)
    decoded_timings = decode_tuya_ir(tuya_code)

    assert decoded_timings == original_timings


def test_tuya_encode_empty_timings():
    """Test encoding empty timing array."""
    timings = []
    tuya_code = encode_tuya_ir(timings)

    # Empty should still be encodable
    assert isinstance(tuya_code, str)


def test_tuya_decode_invalid_base64():
    """Test that invalid Base64 raises ValueError."""
    with pytest.raises(ValueError):
        decode_tuya_ir("Not valid Base64!!!")


def test_tuya_encode_invalid_timing():
    """Test that out-of-range timing raises ValueError."""
    # Timing values must fit in 16-bit unsigned int (0-65535)
    with pytest.raises(ValueError):
        encode_tuya_ir([70000])  # Too large

    with pytest.raises(ValueError):
        encode_tuya_ir([-100])  # Negative


def test_validate_tuya_code_valid():
    """Test validation of a valid Tuya code."""
    timings = [9000, 4500, 600, 540]
    tuya_code = encode_tuya_ir(timings)

    assert validate_tuya_code(tuya_code) is True


def test_validate_tuya_code_invalid():
    """Test validation of an invalid Tuya code."""
    assert validate_tuya_code("Invalid!@#$") is False


def test_tuya_encode_realistic_hvac_timings():
    """Test encoding realistic HVAC timing pattern."""
    # Typical Fujitsu header + some data bits
    timings = [9000, 4500] + [600, 540] * 50  # Header + 50 zero bits
    tuya_code = encode_tuya_ir(timings)
    decoded = decode_tuya_ir(tuya_code)

    assert decoded == timings
