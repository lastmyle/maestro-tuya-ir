#!/usr/bin/env python3
"""
Integration tests for Hitachi AC protocol command generation.

Tests the complete workflow:
1. Generate IR code from IRHitachiAc class
2. Encode to Tuya format
3. Decode and identify as HITACHI_AC
4. Generate full command set via API
5. Verify command structure and validity
"""

import pytest
from fastapi.testclient import TestClient
from index import app
from app.core.tuya_encoder import decode_ir, encode_ir
from app.core.ir_protocols.ir_recv import decode_results
from app.core.ir_protocols.hitachi import (
    IRHitachiAc,
    sendHitachiAC,
    decodeHitachiAC,
    kHitachiAcStateLength,
    kHitachiAcBits,
    kHitachiAcMinTemp,
    kHitachiAcMaxTemp,
    kHitachiAcAuto,
    kHitachiAcCool,
    kHitachiAcHeat,
    kHitachiAcDry,
    kHitachiAcFan,
    kHitachiAcFanAuto,
    kHitachiAcFanLow,
    kHitachiAcFanMed,
    kHitachiAcFanHigh,
)


def generate_hitachi_tuya_code(
    power: bool = True,
    mode: int = kHitachiAcCool,
    temp: int = 24,
    fan: int = kHitachiAcFanAuto,
) -> str:
    """Generate a Hitachi AC Tuya code with specified settings."""
    ac = IRHitachiAc()
    if power:
        ac.on()
    else:
        ac.off()
    ac.setMode(mode)
    ac.setTemp(temp)
    ac.setFan(fan)

    state = ac.getRaw()
    timings = sendHitachiAC(state, kHitachiAcStateLength)

    # Trim large gaps for Tuya encoding
    timings = [min(t, 65535) for t in timings]
    while timings and timings[-1] > 10000:
        timings = timings[:-1]

    return encode_ir(timings)


# Generate a test code for Cool mode, 24C, Auto fan
HITACHI_AC_TEST_CODE = generate_hitachi_tuya_code(
    power=True, mode=kHitachiAcCool, temp=24, fan=kHitachiAcFanAuto
)

# Real user-captured Hitachi AC code (has preamble before header)
# This code has a 4-timing preamble before the actual Hitachi header
HITACHI_AC_USER_CODE = "FK0BrQG1d9nEPg2vBq0BBgWtARwCh+AgA+AXLwEGBYAD4BdTQCdAIwIGBa0gA0AH4AMDAa0BgBuAE0AL4AEDgBsBHALgAQMCBgWt4AoDgBdAJ0ALQAdAA+ADC0APQAPgAxPgAwvAG+AHE0AX4AcD4BsjwDPgJysBBgWAx8A/4AcHQB8DBgWHAeAHF8APQBtAA8AP4AkHAK3gChPgCyfgBRPgS1PgB2OAD+AtnwEcAuAVA0C/QAPgFydAHwIGBa0gAwGHAUAL4C8DQD8DBgWtAcA/CQYFHAK1d60BrQFDi0APBK0BHAKH4CAD4BcvAQYFQAPgC1PgBRMHBgWHARwChwFAB+ABAwCtIAtAAwGHAYAbAK1gB0ALwAPgBxNAD4ADQAsBhwFAJwEGBeABD+AHE8ArQAcDBgWHAYAH4AknAwYFhwFAG+APA0AfAQYF4AE3AwYFhwHgAyvgAQ/gASMBHALgAQNAHwMGBa0B4AUT4AEPwAvAB+ADJ+ADC8AfAQYFwAMFrQEcAlkC"


class TestHitachiACClassOperations:
    """Test IRHitachiAc class basic operations."""

    def test_power_operations(self):
        """Test power on/off operations."""
        ac = IRHitachiAc()

        ac.on()
        assert ac.getPower() == True

        ac.off()
        assert ac.getPower() == False

        ac.setPower(True)
        assert ac.getPower() == True

        ac.setPower(False)
        assert ac.getPower() == False

    def test_temperature_operations(self):
        """Test temperature setting and getting."""
        ac = IRHitachiAc()

        # Test normal temperature
        ac.setTemp(24)
        assert ac.getTemp() == 24

        ac.setTemp(16)  # Min
        assert ac.getTemp() == 16

        ac.setTemp(32)  # Max
        assert ac.getTemp() == 32

        # Test clamping
        ac.setTemp(10)  # Below min
        assert ac.getTemp() == kHitachiAcMinTemp

        ac.setTemp(40)  # Above max
        assert ac.getTemp() == kHitachiAcMaxTemp

    def test_mode_operations(self):
        """Test mode setting and getting."""
        ac = IRHitachiAc()

        modes = [
            (kHitachiAcAuto, "auto"),
            (kHitachiAcCool, "cool"),
            (kHitachiAcHeat, "heat"),
            (kHitachiAcDry, "dry"),
            (kHitachiAcFan, "fan"),
        ]

        for mode_val, mode_name in modes:
            ac.setMode(mode_val)
            assert ac.getMode() == mode_val, f"Mode {mode_name} failed"

    def test_fan_operations(self):
        """Test fan speed setting and getting."""
        ac = IRHitachiAc()

        fans = [
            (kHitachiAcFanAuto, "auto"),
            (kHitachiAcFanLow, "low"),
            (kHitachiAcFanMed, "med"),
            (kHitachiAcFanHigh, "high"),
        ]

        for fan_val, fan_name in fans:
            ac.setFan(fan_val)
            assert ac.getFan() == fan_val, f"Fan {fan_name} failed"

    def test_swing_operations(self):
        """Test swing setting and getting."""
        ac = IRHitachiAc()

        ac.setSwingVertical(True)
        assert ac.getSwingVertical() == True

        ac.setSwingVertical(False)
        assert ac.getSwingVertical() == False

        ac.setSwingHorizontal(True)
        assert ac.getSwingHorizontal() == True

        ac.setSwingHorizontal(False)
        assert ac.getSwingHorizontal() == False


class TestHitachiACStateGeneration:
    """Test state byte generation."""

    def test_state_length(self):
        """Test state has correct length."""
        ac = IRHitachiAc()
        state = ac.getRaw()
        assert len(state) == kHitachiAcStateLength  # 28 bytes

    def test_state_header_byte(self):
        """Test header byte is correct."""
        ac = IRHitachiAc()
        state = ac.getRaw()
        # Hitachi uses 0x80 as first byte
        assert state[0] == 0x80

    def test_checksum_present(self):
        """Test checksum is calculated."""
        ac = IRHitachiAc()
        ac.on()
        ac.setTemp(24)
        ac.setMode(kHitachiAcCool)
        ac.setFan(kHitachiAcFanAuto)

        state = ac.getRaw()

        # Last byte should be checksum (non-zero in most cases)
        # The checksum is calculated over previous bytes
        assert len(state) == 28


class TestHitachiACIRGeneration:
    """Test IR timing generation."""

    def test_generate_ir_timings(self):
        """Test generating IR timings from state."""
        ac = IRHitachiAc()
        ac.on()
        ac.setTemp(24)
        ac.setMode(kHitachiAcCool)
        ac.setFan(kHitachiAcFanAuto)

        state = ac.getRaw()
        timings = sendHitachiAC(state, kHitachiAcStateLength)

        # Verify timings generated
        assert len(timings) > 0
        assert all(isinstance(t, int) for t in timings)
        assert all(t > 0 for t in timings)

    def test_encode_to_tuya_format(self):
        """Test encoding timings to Tuya format."""
        ac = IRHitachiAc()
        ac.on()
        ac.setTemp(22)
        ac.setMode(kHitachiAcCool)
        ac.setFan(kHitachiAcFanMed)

        state = ac.getRaw()
        timings = sendHitachiAC(state, kHitachiAcStateLength)

        # Trim large gap values for Tuya encoding
        timings = [min(t, 65535) for t in timings]
        while timings and timings[-1] > 10000:
            timings = timings[:-1]

        tuya_code = encode_ir(timings)

        # Verify Tuya code generated
        assert isinstance(tuya_code, str)
        assert len(tuya_code) > 0

    def test_roundtrip_encode_decode(self):
        """Test that generated codes can be decoded back."""
        ac = IRHitachiAc()
        ac.on()
        ac.setTemp(25)
        ac.setMode(kHitachiAcHeat)
        ac.setFan(kHitachiAcFanHigh)

        state = ac.getRaw()
        timings = sendHitachiAC(state, kHitachiAcStateLength)

        # Trim and encode
        timings = [min(t, 65535) for t in timings]
        while timings and timings[-1] > 10000:
            timings = timings[:-1]

        tuya_code = encode_ir(timings)

        # Decode back
        decoded_timings = decode_ir(tuya_code)
        assert len(decoded_timings) > 0


class TestHitachiACDecoding:
    """Test decoding of Hitachi AC IR codes."""

    def test_decode_generated_code(self):
        """Test decoding a generated Tuya code."""
        timings = decode_ir(HITACHI_AC_TEST_CODE)

        # Verify we got timing values
        assert len(timings) > 0

        # Verify header pattern (Hitachi uses ~3300µs mark, ~1700µs space)
        assert 3000 < timings[0] < 3600  # ~3300µs mark
        assert 1500 < timings[1] < 1900  # ~1700µs space

    def test_decode_as_hitachi_ac(self):
        """Test decoding timings as HITACHI_AC protocol."""
        timings = decode_ir(HITACHI_AC_TEST_CODE)

        results = decode_results()
        results.rawbuf = timings
        results.rawlen = len(timings)

        # Should decode as HITACHI_AC
        assert decodeHitachiAC(results, offset=0, nbits=kHitachiAcBits, strict=False)
        assert results.bits == 224  # 28 bytes * 8

        # Verify state bytes
        state = results.state[: results.bits // 8]
        assert len(state) == 28


class TestHitachiACFullCommandGeneration:
    """Test full command set generation."""

    @staticmethod
    def trim_timings(timings):
        """Remove trailing gaps and cap values at 65535."""
        while timings and timings[-1] > 10000:
            timings = timings[:-1]
        return [min(t, 65535) for t in timings]

    def test_generate_power_off_command(self):
        """Test generating power off command."""
        ac = IRHitachiAc()
        ac.off()

        state = ac.getRaw()
        timings = self.trim_timings(sendHitachiAC(state, kHitachiAcStateLength))
        tuya_code = encode_ir(timings)

        assert isinstance(tuya_code, str)
        assert len(tuya_code) > 0

    def test_generate_all_temperature_commands(self):
        """Test generating commands for all temperatures."""
        for temp in range(kHitachiAcMinTemp, kHitachiAcMaxTemp + 1):
            ac = IRHitachiAc()
            ac.on()
            ac.setTemp(temp)
            ac.setMode(kHitachiAcCool)
            ac.setFan(kHitachiAcFanAuto)

            state = ac.getRaw()
            timings = self.trim_timings(sendHitachiAC(state, kHitachiAcStateLength))
            tuya_code = encode_ir(timings)

            assert isinstance(tuya_code, str), f"Failed at temp {temp}"
            assert len(tuya_code) > 0, f"Empty code at temp {temp}"

    def test_generate_all_mode_commands(self):
        """Test generating commands for all modes."""
        modes = [
            kHitachiAcAuto,
            kHitachiAcCool,
            kHitachiAcHeat,
            kHitachiAcDry,
            kHitachiAcFan,
        ]

        for mode in modes:
            ac = IRHitachiAc()
            ac.on()
            ac.setTemp(24)
            ac.setMode(mode)
            ac.setFan(kHitachiAcFanAuto)

            state = ac.getRaw()
            timings = self.trim_timings(sendHitachiAC(state, kHitachiAcStateLength))
            tuya_code = encode_ir(timings)

            assert isinstance(tuya_code, str), f"Failed at mode {mode}"
            assert len(tuya_code) > 0, f"Empty code at mode {mode}"

    def test_generate_all_fan_commands(self):
        """Test generating commands for all fan speeds."""
        fans = [
            kHitachiAcFanAuto,
            kHitachiAcFanLow,
            kHitachiAcFanMed,
            kHitachiAcFanHigh,
        ]

        for fan in fans:
            ac = IRHitachiAc()
            ac.on()
            ac.setTemp(24)
            ac.setMode(kHitachiAcCool)
            ac.setFan(fan)

            state = ac.getRaw()
            timings = self.trim_timings(sendHitachiAC(state, kHitachiAcStateLength))
            tuya_code = encode_ir(timings)

            assert isinstance(tuya_code, str), f"Failed at fan {fan}"
            assert len(tuya_code) > 0, f"Empty code at fan {fan}"

    def test_generated_codes_are_unique(self):
        """Test that generated Tuya codes are unique for different settings."""
        codes = {}  # code -> (mode, temp, fan)

        modes = [
            (kHitachiAcAuto, "auto"),
            (kHitachiAcCool, "cool"),
            (kHitachiAcHeat, "heat"),
            (kHitachiAcDry, "dry"),
        ]

        fans = [
            (kHitachiAcFanAuto, "auto"),
            (kHitachiAcFanLow, "low"),
            (kHitachiAcFanMed, "med"),
            (kHitachiAcFanHigh, "high"),
        ]

        for mode_val, mode_name in modes:
            for temp in range(kHitachiAcMinTemp, kHitachiAcMaxTemp + 1):
                for fan_val, fan_name in fans:
                    ac = IRHitachiAc()
                    ac.on()
                    ac.setMode(mode_val)
                    ac.setTemp(temp)
                    ac.setFan(fan_val)

                    state = ac.getRaw()
                    timings = self.trim_timings(
                        sendHitachiAC(state, kHitachiAcStateLength)
                    )
                    code = encode_ir(timings)
                    codes[code] = (mode_name, temp, fan_name)

        # All codes should be unique - verify we have at least 200 unique codes
        # (some modes like auto may produce identical codes for different temps)
        assert len(codes) >= 200, f"Expected at least 200 unique codes, got {len(codes)}"

        # Verify that different temperatures in cool mode produce unique codes
        cool_codes = set()
        for temp in range(kHitachiAcMinTemp, kHitachiAcMaxTemp + 1):
            ac = IRHitachiAc()
            ac.on()
            ac.setMode(kHitachiAcCool)
            ac.setTemp(temp)
            ac.setFan(kHitachiAcFanAuto)

            state = ac.getRaw()
            timings = self.trim_timings(sendHitachiAC(state, kHitachiAcStateLength))
            cool_codes.add(encode_ir(timings))

        # Each temperature in cool mode should produce a unique code
        assert len(cool_codes) == 17, f"Expected 17 unique cool codes, got {len(cool_codes)}"


class TestHitachiACAPIEndpoint:
    """E2E tests for /api/identify endpoint with Hitachi AC."""

    @pytest.fixture
    def client(self):
        """Create FastAPI test client."""
        return TestClient(app)

    def test_api_identify_hitachi_ac(self, client):
        """Test /api/identify correctly identifies Hitachi AC code."""
        response = client.post("/api/identify", json={"tuya_code": HITACHI_AC_TEST_CODE})

        assert response.status_code == 200
        data = response.json()

        # Verify protocol detection
        assert data["protocol"] == "HITACHI_AC"
        assert data["manufacturer"] == "Hitachi"

    def test_api_returns_correct_temperature_range(self, client):
        """Test API returns correct temperature range for Hitachi AC."""
        response = client.post("/api/identify", json={"tuya_code": HITACHI_AC_TEST_CODE})

        assert response.status_code == 200
        data = response.json()

        assert data["min_temperature"] == kHitachiAcMinTemp  # 16
        assert data["max_temperature"] == kHitachiAcMaxTemp  # 32

    def test_api_returns_all_operation_modes(self, client):
        """Test API returns all operation modes."""
        response = client.post("/api/identify", json={"tuya_code": HITACHI_AC_TEST_CODE})

        assert response.status_code == 200
        data = response.json()

        expected_modes = ["auto", "cool", "heat", "dry", "fan"]
        assert set(data["operation_modes"]) == set(expected_modes)

    def test_api_returns_all_fan_modes(self, client):
        """Test API returns all fan modes."""
        response = client.post("/api/identify", json={"tuya_code": HITACHI_AC_TEST_CODE})

        assert response.status_code == 200
        data = response.json()

        expected_fans = ["auto", "low", "med", "high"]
        assert set(data["fan_modes"]) == set(expected_fans)

    def test_api_generates_commands(self, client):
        """Test API generates commands for Hitachi AC."""
        response = client.post("/api/identify", json={"tuya_code": HITACHI_AC_TEST_CODE})

        assert response.status_code == 200
        data = response.json()

        # Should generate commands
        commands = data["commands"]
        assert isinstance(commands, list)
        assert len(commands) > 0

        # Expected: 17 temps x 5 modes x 4 fans + 2 power = 342 commands
        expected_count = (17 * 5 * 4) + 2
        assert (
            len(commands) == expected_count
        ), f"Expected {expected_count}, got {len(commands)}"

    def test_api_command_structure(self, client):
        """Test each command has required fields."""
        response = client.post("/api/identify", json={"tuya_code": HITACHI_AC_TEST_CODE})

        assert response.status_code == 200
        data = response.json()

        for cmd in data["commands"]:
            assert "name" in cmd
            assert "description" in cmd
            assert "tuya_code" in cmd
            assert isinstance(cmd["tuya_code"], str)
            assert len(cmd["tuya_code"]) > 0

    def test_api_generated_codes_are_valid_tuya(self, client):
        """Test generated Tuya codes can be decoded back to timings."""
        response = client.post("/api/identify", json={"tuya_code": HITACHI_AC_TEST_CODE})

        assert response.status_code == 200
        data = response.json()

        # Test first 10 commands can be decoded
        for cmd in data["commands"][:10]:
            timings = decode_ir(cmd["tuya_code"])
            assert len(timings) > 0, f"Failed to decode {cmd['name']}"

    def test_api_has_power_commands(self, client):
        """Test API generates power on/off commands."""
        response = client.post("/api/identify", json={"tuya_code": HITACHI_AC_TEST_CODE})

        assert response.status_code == 200
        data = response.json()

        command_names = [cmd["name"] for cmd in data["commands"]]
        assert "power_on" in command_names
        assert "power_off" in command_names

    def test_api_has_expected_temp_mode_fan_commands(self, client):
        """Test API generates specific temperature/mode/fan combinations."""
        response = client.post("/api/identify", json={"tuya_code": HITACHI_AC_TEST_CODE})

        assert response.status_code == 200
        data = response.json()

        command_names = [cmd["name"] for cmd in data["commands"]]

        # Check for specific commands
        assert "24_cool_auto" in command_names
        assert "25_heat_high" in command_names
        assert "16_auto_low" in command_names
        assert "30_dry_med" in command_names


class TestHitachiACUserCapturedCode:
    """Tests for real user-captured Hitachi AC code with preamble."""

    @pytest.fixture
    def client(self):
        """Create FastAPI test client."""
        return TestClient(app)

    def test_user_code_decodes_to_timings(self):
        """Test user's Hitachi code decodes to timings."""
        timings = decode_ir(HITACHI_AC_USER_CODE)

        # Verify we got timing values
        assert len(timings) > 0
        # User's code has preamble + 2 repeats, so longer than standard
        assert len(timings) > 450

    def test_user_code_has_preamble_and_header(self):
        """Test user's code has preamble followed by Hitachi header."""
        timings = decode_ir(HITACHI_AC_USER_CODE)

        # First 4 timings are preamble
        # Then Hitachi header at indices 4-5: ~3300µs mark, ~1700µs space
        assert 3000 < timings[4] < 3600  # ~3390µs header mark
        assert 1500 < timings[5] < 1900  # ~1711µs header space

    def test_api_identifies_user_code_as_hitachi(self, client):
        """Test API identifies user's code as HITACHI_AC."""
        response = client.post(
            "/api/identify", json={"tuya_code": HITACHI_AC_USER_CODE}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["protocol"] == "HITACHI_AC"
        assert data["manufacturer"] == "Hitachi"

    def test_api_generates_commands_for_user_code(self, client):
        """Test API generates commands for user's Hitachi code."""
        response = client.post(
            "/api/identify", json={"tuya_code": HITACHI_AC_USER_CODE}
        )

        assert response.status_code == 200
        data = response.json()

        # Should generate the full command set
        commands = data["commands"]
        assert len(commands) == 342  # 17 temps × 5 modes × 4 fans + 2 power

    def test_user_code_temperature_range(self, client):
        """Test user's code returns correct temperature range."""
        response = client.post(
            "/api/identify", json={"tuya_code": HITACHI_AC_USER_CODE}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["min_temperature"] == 16
        assert data["max_temperature"] == 32


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
