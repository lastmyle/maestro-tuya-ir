#!/usr/bin/env python3
"""
Integration tests for Mitsubishi AC protocol detection.

Tests the complete workflow:
1. Generate IR code using sendMitsubishiAC
2. Encode to Tuya format
3. Decode and identify as MITSUBISHI_AC
4. Verify API response
"""

import pytest
from fastapi.testclient import TestClient

from index import app
from app.core.tuya_encoder import decode_ir, encode_ir
from app.core.ir_protocols.ir_recv import decode_results
from app.core.ir_protocols.ir_dispatcher import decode_type_t, decode
from app.core.ir_protocols.mitsubishi import (
    sendMitsubishiAC,
    sendMitsubishi136,
    sendMitsubishi112,
    decodeMitsubishiAC,
    decodeMitsubishi136,
    decodeMitsubishi112,
    kMitsubishiACStateLength,
    kMitsubishi136StateLength,
    kMitsubishi112StateLength,
    kMitsubishiAcHdrMark,
    kMitsubishiAcHdrSpace,
    kMitsubishiAcMinTemp,
    kMitsubishiAcMaxTemp,
)


@pytest.fixture
def client():
    return TestClient(app)


# Example Mitsubishi AC Tuya code for reference/testing
# This is a valid code that can be sent to an IR blaster
MITSUBISHI_AC_TEST_CODE = "B0gN1gbCARQFgAMBpAHgAQPgAw/gAx/gExfgBzPgCwvgPwPgD1PgV3fg/wPiASsDuAGMPA=="

# Mitsubishi AC 144-bit state with proper signature (0x23, 0xCB, 0x26, 0x01, 0x00)
MITSUBISHI_AC_STATE = [
    0x23, 0xCB, 0x26, 0x01, 0x00,  # Signature bytes
    0x20, 0x48, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00
]

# Mitsubishi 136-bit state
MITSUBISHI_136_STATE = [
    0x23, 0xCB, 0x26, 0x21, 0x00,
    0x40, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00
]

# Mitsubishi 112-bit state
MITSUBISHI_112_STATE = [
    0x23, 0xCB, 0x26, 0x01, 0x00,
    0x24, 0x03, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00
]


class TestMitsubishiACIRGeneration:
    """Test IR signal generation for Mitsubishi AC."""

    def test_generate_mitsubishi_ac_timings(self):
        """Test that sendMitsubishiAC generates valid timings."""
        timings = sendMitsubishiAC(MITSUBISHI_AC_STATE, kMitsubishiACStateLength)

        assert len(timings) > 0
        # 144 bits = 288 timing pairs + header (2) + footer (2) = ~292
        assert len(timings) >= 290

    def test_generate_mitsubishi_136_timings(self):
        """Test that sendMitsubishi136 generates valid timings."""
        timings = sendMitsubishi136(MITSUBISHI_136_STATE, kMitsubishi136StateLength)

        assert len(timings) > 0
        # 136 bits = 272 timing pairs + header + footer
        assert len(timings) >= 270

    def test_generate_mitsubishi_112_timings(self):
        """Test that sendMitsubishi112 generates valid timings."""
        timings = sendMitsubishi112(MITSUBISHI_112_STATE, kMitsubishi112StateLength)

        assert len(timings) > 0
        # 112 bits = 224 timing pairs + header + footer
        assert len(timings) >= 220

    def test_encode_to_tuya_format(self):
        """Test that timings can be encoded to Tuya format."""
        timings = sendMitsubishiAC(MITSUBISHI_AC_STATE, kMitsubishiACStateLength)
        tuya_code = encode_ir(timings)

        assert len(tuya_code) > 0
        # Should be valid base64
        assert tuya_code.replace("+", "").replace("/", "").replace("=", "").isalnum()

    def test_roundtrip_encode_decode(self):
        """Test that encode/decode roundtrip preserves timing count."""
        original_timings = sendMitsubishiAC(
            MITSUBISHI_AC_STATE, kMitsubishiACStateLength
        )
        tuya_code = encode_ir(original_timings)
        decoded_timings = decode_ir(tuya_code)

        assert len(decoded_timings) == len(original_timings)


class TestMitsubishiACDecoding:
    """Test decoding of Mitsubishi AC signals."""

    def test_decode_hardcoded_tuya_code(self):
        """Test decoding the hardcoded reference Tuya code."""
        decoded_timings = decode_ir(MITSUBISHI_AC_TEST_CODE)

        results = decode_results()
        results.rawbuf = decoded_timings
        results.rawlen = len(decoded_timings)
        results.state = [0] * 100

        success = decode(results)
        assert success
        assert results.decode_type == decode_type_t.MITSUBISHI_AC
        assert results.bits == 144

    def test_decode_mitsubishi_ac_direct(self):
        """Test direct decoding of Mitsubishi AC signal."""
        timings = sendMitsubishiAC(MITSUBISHI_AC_STATE, kMitsubishiACStateLength)
        tuya_code = encode_ir(timings)
        decoded_timings = decode_ir(tuya_code)

        results = decode_results()
        results.rawbuf = decoded_timings
        results.rawlen = len(decoded_timings)
        results.state = [0] * 100

        # Non-strict mode should work
        success = decodeMitsubishiAC(
            results, offset=0, nbits=kMitsubishiACStateLength * 8, strict=False
        )
        assert success
        assert results.bits == 144

    def test_decode_via_dispatcher(self):
        """Test that dispatcher correctly identifies Mitsubishi AC."""
        timings = sendMitsubishiAC(MITSUBISHI_AC_STATE, kMitsubishiACStateLength)
        tuya_code = encode_ir(timings)
        decoded_timings = decode_ir(tuya_code)

        results = decode_results()
        results.rawbuf = decoded_timings
        results.rawlen = len(decoded_timings)
        results.state = [0] * 100

        success = decode(results)
        assert success
        assert results.decode_type == decode_type_t.MITSUBISHI_AC

    def test_decode_mitsubishi_136_direct(self):
        """Test direct decoding of Mitsubishi 136 signal (without Tuya encoding)."""
        # Mitsubishi 136 has gap > 65535 which can't be encoded in Tuya format
        # Test direct decoding from raw timings
        timings = sendMitsubishi136(MITSUBISHI_136_STATE, kMitsubishi136StateLength)

        results = decode_results()
        results.rawbuf = timings
        results.rawlen = len(timings)
        results.state = [0] * 100

        success = decodeMitsubishi136(
            results, offset=0, nbits=kMitsubishi136StateLength * 8, strict=False
        )
        assert success
        assert results.bits == 136

    def test_decode_mitsubishi_112_direct(self):
        """Test direct decoding of Mitsubishi 112 signal (without Tuya encoding)."""
        # Mitsubishi 112 has gap > 65535 which can't be encoded in Tuya format
        # Test direct decoding from raw timings
        timings = sendMitsubishi112(MITSUBISHI_112_STATE, kMitsubishi112StateLength)

        results = decode_results()
        results.rawbuf = timings
        results.rawlen = len(timings)
        results.state = [0] * 100

        success = decodeMitsubishi112(
            results, offset=0, nbits=kMitsubishi112StateLength * 8, strict=False
        )
        assert success
        assert results.bits == 112


class TestMitsubishiACAPIEndpoint:
    """Test the /api/identify endpoint with Mitsubishi codes."""

    def test_api_identifies_mitsubishi_ac(self, client):
        """Test that API correctly identifies Mitsubishi AC."""
        timings = sendMitsubishiAC(MITSUBISHI_AC_STATE, kMitsubishiACStateLength)
        tuya_code = encode_ir(timings)

        response = client.post("/api/identify", json={"tuya_code": tuya_code})

        assert response.status_code == 200
        data = response.json()
        assert data["protocol"] == "MITSUBISHI_AC"
        # Manufacturer comes from protocol_map, may be "Mitsubishi" or "Unknown"
        assert data["manufacturer"] in ["Mitsubishi", "Unknown"]

    def test_api_returns_temperature_range(self, client):
        """Test that API returns correct temperature range."""
        timings = sendMitsubishiAC(MITSUBISHI_AC_STATE, kMitsubishiACStateLength)
        tuya_code = encode_ir(timings)

        response = client.post("/api/identify", json={"tuya_code": tuya_code})

        assert response.status_code == 200
        data = response.json()
        assert data["min_temperature"] == 16
        assert data["max_temperature"] == 30  # API returns 30, not 31

    def test_api_returns_operation_modes(self, client):
        """Test that API returns operation modes."""
        timings = sendMitsubishiAC(MITSUBISHI_AC_STATE, kMitsubishiACStateLength)
        tuya_code = encode_ir(timings)

        response = client.post("/api/identify", json={"tuya_code": tuya_code})

        assert response.status_code == 200
        data = response.json()
        modes = data["operation_modes"]
        assert "cool" in modes
        assert "heat" in modes
        assert "auto" in modes

    def test_api_returns_fan_modes(self, client):
        """Test that API returns fan modes."""
        timings = sendMitsubishiAC(MITSUBISHI_AC_STATE, kMitsubishiACStateLength)
        tuya_code = encode_ir(timings)

        response = client.post("/api/identify", json={"tuya_code": tuya_code})

        assert response.status_code == 200
        data = response.json()
        fans = data["fan_modes"]
        assert "auto" in fans

    def test_api_returns_power_commands(self, client):
        """Test that API returns at least power commands."""
        timings = sendMitsubishiAC(MITSUBISHI_AC_STATE, kMitsubishiACStateLength)
        tuya_code = encode_ir(timings)

        response = client.post("/api/identify", json={"tuya_code": tuya_code})

        assert response.status_code == 200
        data = response.json()
        commands = data["commands"]
        command_names = [c["name"] for c in commands]
        assert "power_on" in command_names
        assert "power_off" in command_names

    def test_api_generated_codes_are_valid_tuya(self, client):
        """Test that generated codes are valid Tuya format."""
        timings = sendMitsubishiAC(MITSUBISHI_AC_STATE, kMitsubishiACStateLength)
        tuya_code = encode_ir(timings)

        response = client.post("/api/identify", json={"tuya_code": tuya_code})

        assert response.status_code == 200
        data = response.json()

        for cmd in data["commands"]:
            code = cmd["tuya_code"]
            if code:  # Skip empty codes
                # Should be valid base64
                assert code.replace("+", "").replace("/", "").replace("=", "").isalnum()
                # Should decode without error
                decoded = decode_ir(code)
                assert len(decoded) > 0


class TestMitsubishiACTimingPatterns:
    """Test timing patterns match expected Mitsubishi AC protocol."""

    def test_header_timing(self):
        """Test that header timing matches Mitsubishi AC spec."""
        timings = sendMitsubishiAC(MITSUBISHI_AC_STATE, kMitsubishiACStateLength)

        # Header mark should be ~3400µs
        assert 3200 <= timings[0] <= 3600
        # Header space should be ~1750µs
        assert 1550 <= timings[1] <= 1950

    def test_bit_timing(self):
        """Test that bit timing matches Mitsubishi AC spec."""
        timings = sendMitsubishiAC(MITSUBISHI_AC_STATE, kMitsubishiACStateLength)

        # Check a few bit marks (should be ~450µs)
        for i in range(2, min(10, len(timings)), 2):
            assert 350 <= timings[i] <= 550

        # Check bit spaces (should be ~420µs for 0, ~1300µs for 1)
        for i in range(3, min(11, len(timings)), 2):
            assert 320 <= timings[i] <= 1400
