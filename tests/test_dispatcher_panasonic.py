"""
Test Panasonic protocol detection via dispatcher

This test ensures that Panasonic IR codes are correctly identified
by the dispatcher and not misidentified as other protocols (e.g., CARRIER_AC84).
"""

from app.core.tuya_encoder import decode_ir
from app.core.ir_protocols.ir_recv import decode_results
from app.core.ir_protocols.ir_dispatcher import decode, decode_type_t


# Real Panasonic AC code captured from actual device
PANASONIC_TEST_CODE = "DYYNvAbdAa4B3QExBd0BQAeAA4ABQA3gAQHADUAHAd0B4AEvQAEB3QGAA8ABAd0BQB/AA0APQAMIMQWuAa4B3QGuYAFAB0ADQAFAB8ADAa4BQAmAAUAJwANAAeABCwDdIAFABYADQAHgCwvgARMCMQXdYAMAruAAAUALQAMDrgFnKOEDBwGuAeABAUAfQAPgDQFAGeAFL8ABQBmAAUAfgAPAEwrdATEFrgGuAd0BruAAAUALQAPAAUALwAMBrgFACUABATEFgAkBMQVAA0ALgAMDMQWuAYABgAtADwkxBd0BrgHdATEFQAUAriABQAVAA+AHAUATAd0BQCcBrgFABwLdAa7gAAEB3QFADwMxBa4BQAEEMQXdAa4gAUAFAzEFrgFABwGuAUAFQAMBrgGABeABAUAPwAMBrgFACQGuAUA3wANAEcADwAFAD8ABQAvAK0AHQAFAE+ADAUAPwAPgAwHgCxPAQ0ABwB/AB0AbwAvgAwHAE0AHQAFAB+ADA+ADAUBDQANAH0AHQAMLrgGuATEFrgExBa4B"


def test_dispatcher_detects_panasonic():
    """Test that dispatcher correctly identifies Panasonic code"""
    signal = decode_ir(PANASONIC_TEST_CODE)
    results = decode_results()
    results.rawbuf = signal
    results.rawlen = len(signal)

    # Decode via dispatcher
    success = decode(results, max_skip=0)

    # Verify detection
    assert success, "Dispatcher should successfully decode Panasonic code"
    detected_protocol = decode_type_t(results.decode_type).name

    print(f"\n=== Panasonic Detection Test ===")
    print(f"Code length: {len(PANASONIC_TEST_CODE)} characters")
    print(f"Timings: {len(signal)}")
    print(f"Detected protocol: {detected_protocol}")
    print(f"Bits decoded: {results.bits}")
    print(f"State (first 10 bytes): {results.state[:10]}")

    assert detected_protocol == "PANASONIC_AC", f"Expected PANASONIC_AC but got {detected_protocol}"
    assert results.bits == 216, f"Expected 216 bits but got {results.bits}"


def test_panasonic_header_timings():
    """Test that Panasonic code has expected header timings"""
    signal = decode_ir(PANASONIC_TEST_CODE)

    # Expected Panasonic AC header: [3456, 1728] (with tolerance)
    # Actual captured: [3462, 1724]
    header_mark = signal[0]
    header_space = signal[1]

    print(f"\n=== Panasonic Header Analysis ===")
    print(f"Header mark: {header_mark} (expected ~3456)")
    print(f"Header space: {header_space} (expected ~1728)")

    # Allow 5% tolerance
    assert 3280 <= header_mark <= 3630, f"Header mark {header_mark} outside expected range"
    assert 1640 <= header_space <= 1815, f"Header space {header_space} outside expected range"


def test_panasonic_not_carrier():
    """Ensure Panasonic code is NOT misidentified as Carrier"""
    signal = decode_ir(PANASONIC_TEST_CODE)
    results = decode_results()
    results.rawbuf = signal
    results.rawlen = len(signal)

    success = decode(results, max_skip=0)
    detected_protocol = decode_type_t(results.decode_type).name if success else "NONE"

    print(f"\n=== Carrier False Positive Test ===")
    print(f"Detected as: {detected_protocol}")

    # Should NOT be detected as any Carrier variant
    assert "CARRIER" not in detected_protocol, \
        f"Panasonic code should not be detected as Carrier (got {detected_protocol})"

    # Should be Panasonic
    assert detected_protocol == "PANASONIC_AC", \
        f"Expected PANASONIC_AC but got {detected_protocol}"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v", "-s"])
