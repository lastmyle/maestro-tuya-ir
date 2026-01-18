#!/usr/bin/env python3
"""
Integration tests for Haier AC176 protocol command generation.

Tests the complete workflow:
1. Decode Tuya IR code
2. Identify as HAIER_AC176
3. Generate full command set
4. Verify command structure and validity
5. E2E API tests via FastAPI TestClient
"""

import pytest
from fastapi.testclient import TestClient
from index import app
from app.core.tuya_encoder import decode_ir, encode_ir
from app.core.ir_protocols.ir_recv import decode_results
from app.core.ir_protocols.haier import (
    IRHaierAC176,
    sendHaierAC176,
    decodeHaierAC176,
    kHaierAC176StateLength,
    kHaierAC176Bits,
    kHaierAcYrw02MinTempC,
    kHaierAcYrw02MaxTempC,
    kHaierAcYrw02Auto,
    kHaierAcYrw02Cool,
    kHaierAcYrw02Heat,
    kHaierAcYrw02Dry,
    kHaierAcYrw02Fan,
    kHaierAcYrw02FanAuto,
    kHaierAcYrw02FanLow,
    kHaierAcYrw02FanMed,
    kHaierAcYrw02FanHigh,
    kHaierAcYrw02SwingVAuto,
    kHaierAcYrw02SwingVOff,
)

# Real Haier AC176 code captured from user's device
# This is a power-off command for Cool mode, 22°C, Auto fan
HAIER_AC176_USER_CODE = "AdoLQAEHRRE3AnMGNwJAAcAHQAFAC0ADwAFAC0ADwAFAC0ADwAFAC0ADQAHAB0AB4AML4BcB4AMr4AsL4AMT4CsB4Dc/4GMBwKvgCwdAE8ADQAFAC0ABQAdAA0ABQAfAA+C3AUDHQAFAB0ADQAELcwY3AnMGNwJzBjcC"


class TestHaierAC176Decoding:
    """Test decoding of user's Haier AC176 IR code."""

    def test_decode_user_code_to_timings(self):
        """Test decoding Tuya code to raw IR timings."""
        timings = decode_ir(HAIER_AC176_USER_CODE)

        # Verify we got timing values
        assert len(timings) > 0
        assert len(timings) == 357  # Expected for AC176

        # Verify header pattern (Haier uses ~3000µs mark, ~3000µs space, ~3000µs mark, ~4300µs space)
        assert 2800 < timings[0] < 3200  # ~3000µs
        assert 2800 < timings[1] < 3200  # ~3000µs
        assert 2800 < timings[2] < 3200  # ~3000µs
        assert 4200 < timings[3] < 4600  # ~4400µs

    def test_decode_user_code_as_haier_ac176(self):
        """Test decoding timings as HAIER_AC176 protocol."""
        timings = decode_ir(HAIER_AC176_USER_CODE)

        results = decode_results()
        results.rawbuf = timings
        results.rawlen = len(timings)

        # Should decode as HAIER_AC176
        assert decodeHaierAC176(results, offset=0, nbits=kHaierAC176Bits, strict=False)
        assert results.bits == 176

        # Verify state bytes
        state = results.state[: results.bits // 8]
        assert len(state) == 22  # AC176 has 22 bytes

        # Verify known bytes from the user's capture
        assert state[0] == 0xA6  # Model byte
        assert state[14] == 0xB7  # Prefix byte

    def test_decode_user_code_settings(self):
        """Test decoding user's code reveals correct AC settings."""
        timings = decode_ir(HAIER_AC176_USER_CODE)

        results = decode_results()
        results.rawbuf = timings
        results.rawlen = len(timings)

        decodeHaierAC176(results, offset=0, nbits=kHaierAC176Bits, strict=False)

        # Load state into AC class for interpretation
        ac = IRHaierAC176()
        ac.setRaw(results.state[: results.bits // 8])

        # Verify decoded settings match user's captured command
        assert ac.getPower() == False  # Power OFF
        assert ac.getMode() == kHaierAcYrw02Cool  # Cool mode
        assert ac.getTemp() == 22  # 22°C
        assert ac.getFan() == kHaierAcYrw02FanAuto  # Auto fan


class TestHaierAC176ClassOperations:
    """Test IRHaierAC176 class basic operations."""

    def test_power_operations(self):
        """Test power on/off operations."""
        ac = IRHaierAC176()

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
        ac = IRHaierAC176()

        # Test normal temperature
        ac.setTemp(24)
        assert ac.getTemp() == 24

        ac.setTemp(16)  # Min
        assert ac.getTemp() == 16

        ac.setTemp(30)  # Max
        assert ac.getTemp() == 30

        # Test clamping
        ac.setTemp(10)  # Below min
        assert ac.getTemp() == kHaierAcYrw02MinTempC

        ac.setTemp(40)  # Above max
        assert ac.getTemp() == kHaierAcYrw02MaxTempC

    def test_mode_operations(self):
        """Test mode setting and getting."""
        ac = IRHaierAC176()

        modes = [
            (kHaierAcYrw02Auto, "auto"),
            (kHaierAcYrw02Cool, "cool"),
            (kHaierAcYrw02Heat, "heat"),
            (kHaierAcYrw02Dry, "dry"),
            (kHaierAcYrw02Fan, "fan"),
        ]

        for mode_val, mode_name in modes:
            ac.setMode(mode_val)
            assert ac.getMode() == mode_val, f"Mode {mode_name} failed"

    def test_fan_operations(self):
        """Test fan speed setting and getting."""
        ac = IRHaierAC176()

        fans = [
            (kHaierAcYrw02FanAuto, "auto"),
            (kHaierAcYrw02FanLow, "low"),
            (kHaierAcYrw02FanMed, "med"),
            (kHaierAcYrw02FanHigh, "high"),
        ]

        for fan_val, fan_name in fans:
            ac.setFan(fan_val)
            assert ac.getFan() == fan_val, f"Fan {fan_name} failed"

    def test_swing_operations(self):
        """Test swing setting and getting."""
        ac = IRHaierAC176()

        ac.setSwingV(kHaierAcYrw02SwingVAuto)
        assert ac.getSwingV() == kHaierAcYrw02SwingVAuto

        ac.setSwingV(kHaierAcYrw02SwingVOff)
        assert ac.getSwingV() == kHaierAcYrw02SwingVOff

    def test_sleep_operations(self):
        """Test sleep mode setting and getting."""
        ac = IRHaierAC176()

        ac.setSleep(True)
        assert ac.getSleep() == True

        ac.setSleep(False)
        assert ac.getSleep() == False

    def test_turbo_operations(self):
        """Test turbo mode setting and getting."""
        ac = IRHaierAC176()

        # Turbo only works in cool/heat modes
        ac.setMode(kHaierAcYrw02Cool)
        ac.setTurbo(True)
        assert ac.getTurbo() == True

        ac.setTurbo(False)
        assert ac.getTurbo() == False

    def test_health_operations(self):
        """Test health mode setting and getting."""
        ac = IRHaierAC176()

        ac.setHealth(True)
        assert ac.getHealth() == True

        ac.setHealth(False)
        assert ac.getHealth() == False


class TestHaierAC176StateGeneration:
    """Test state byte generation."""

    def test_state_length(self):
        """Test state has correct length."""
        ac = IRHaierAC176()
        state = ac.getRaw()
        assert len(state) == kHaierAC176StateLength  # 22 bytes

    def test_state_model_byte(self):
        """Test model byte is correct."""
        ac = IRHaierAC176()
        state = ac.getRaw()
        assert state[0] == 0xA6  # Model A

    def test_state_prefix_byte(self):
        """Test prefix byte is correct."""
        ac = IRHaierAC176()
        state = ac.getRaw()
        assert state[14] == 0xB7  # AC176 prefix

    def test_checksum_calculation(self):
        """Test checksum is calculated correctly."""
        ac = IRHaierAC176()

        # Set various states and verify checksum is set
        ac.on()
        ac.setTemp(24)
        ac.setMode(kHaierAcYrw02Cool)
        ac.setFan(kHaierAcYrw02FanAuto)

        state = ac.getRaw()

        # Checksum bytes should be non-zero
        assert state[13] != 0  # First checksum
        assert state[21] != 0  # Second checksum


class TestHaierAC176IRGeneration:
    """Test IR timing generation."""

    def test_generate_ir_timings(self):
        """Test generating IR timings from state."""
        ac = IRHaierAC176()
        ac.on()
        ac.setTemp(24)
        ac.setMode(kHaierAcYrw02Cool)
        ac.setFan(kHaierAcYrw02FanAuto)

        state = ac.getRaw()
        timings = sendHaierAC176(state, kHaierAC176StateLength)

        # Verify timings generated
        assert len(timings) > 0
        assert all(isinstance(t, int) for t in timings)
        assert all(t > 0 for t in timings)

    def test_encode_to_tuya_format(self):
        """Test encoding timings to Tuya format."""
        ac = IRHaierAC176()
        ac.on()
        ac.setTemp(22)
        ac.setMode(kHaierAcYrw02Cool)
        ac.setFan(kHaierAcYrw02FanMed)

        state = ac.getRaw()
        timings = sendHaierAC176(state, kHaierAC176StateLength)

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
        ac = IRHaierAC176()
        ac.on()
        ac.setTemp(25)
        ac.setMode(kHaierAcYrw02Heat)
        ac.setFan(kHaierAcYrw02FanHigh)

        state = ac.getRaw()
        timings = sendHaierAC176(state, kHaierAC176StateLength)

        # Trim and encode
        timings = [min(t, 65535) for t in timings]
        while timings and timings[-1] > 10000:
            timings = timings[:-1]

        tuya_code = encode_ir(timings)

        # Decode back
        decoded_timings = decode_ir(tuya_code)
        assert len(decoded_timings) > 0


class TestHaierAC176FullCommandGeneration:
    """Test full command set generation."""

    @staticmethod
    def trim_timings(timings):
        """Remove trailing gaps and cap values at 65535."""
        while timings and timings[-1] > 10000:
            timings = timings[:-1]
        return [min(t, 65535) for t in timings]

    def test_generate_power_off_command(self):
        """Test generating power off command."""
        ac = IRHaierAC176()
        ac.off()

        state = ac.getRaw()
        timings = self.trim_timings(sendHaierAC176(state, kHaierAC176StateLength))
        tuya_code = encode_ir(timings)

        assert isinstance(tuya_code, str)
        assert len(tuya_code) > 0

    def test_generate_all_temperature_commands(self):
        """Test generating commands for all temperatures."""
        for temp in range(kHaierAcYrw02MinTempC, kHaierAcYrw02MaxTempC + 1):
            ac = IRHaierAC176()
            ac.on()
            ac.setTemp(temp)
            ac.setMode(kHaierAcYrw02Cool)
            ac.setFan(kHaierAcYrw02FanAuto)

            state = ac.getRaw()
            timings = self.trim_timings(sendHaierAC176(state, kHaierAC176StateLength))
            tuya_code = encode_ir(timings)

            assert isinstance(tuya_code, str), f"Failed at temp {temp}"
            assert len(tuya_code) > 0, f"Empty code at temp {temp}"

    def test_generate_all_mode_commands(self):
        """Test generating commands for all modes."""
        modes = [
            kHaierAcYrw02Auto,
            kHaierAcYrw02Cool,
            kHaierAcYrw02Heat,
            kHaierAcYrw02Dry,
            kHaierAcYrw02Fan,
        ]

        for mode in modes:
            ac = IRHaierAC176()
            ac.on()
            ac.setTemp(24)
            ac.setMode(mode)
            ac.setFan(kHaierAcYrw02FanAuto)

            state = ac.getRaw()
            timings = self.trim_timings(sendHaierAC176(state, kHaierAC176StateLength))
            tuya_code = encode_ir(timings)

            assert isinstance(tuya_code, str), f"Failed at mode {mode}"
            assert len(tuya_code) > 0, f"Empty code at mode {mode}"

    def test_generate_all_fan_commands(self):
        """Test generating commands for all fan speeds."""
        fans = [
            kHaierAcYrw02FanAuto,
            kHaierAcYrw02FanLow,
            kHaierAcYrw02FanMed,
            kHaierAcYrw02FanHigh,
        ]

        for fan in fans:
            ac = IRHaierAC176()
            ac.on()
            ac.setTemp(24)
            ac.setMode(kHaierAcYrw02Cool)
            ac.setFan(fan)

            state = ac.getRaw()
            timings = self.trim_timings(sendHaierAC176(state, kHaierAC176StateLength))
            tuya_code = encode_ir(timings)

            assert isinstance(tuya_code, str), f"Failed at fan {fan}"
            assert len(tuya_code) > 0, f"Empty code at fan {fan}"

    def test_generate_full_command_set(self):
        """Test generating complete command set (245 commands)."""
        commands = []

        modes = [
            (kHaierAcYrw02Auto, "auto"),
            (kHaierAcYrw02Cool, "cool"),
            (kHaierAcYrw02Heat, "heat"),
            (kHaierAcYrw02Dry, "dry"),
            (kHaierAcYrw02Fan, "fan"),
        ]

        fans = [
            (kHaierAcYrw02FanAuto, "auto"),
            (kHaierAcYrw02FanLow, "low"),
            (kHaierAcYrw02FanMed, "med"),
            (kHaierAcYrw02FanHigh, "high"),
        ]

        # Power off command
        ac = IRHaierAC176()
        ac.off()
        state = ac.getRaw()
        timings = self.trim_timings(sendHaierAC176(state, kHaierAC176StateLength))
        commands.append({"name": "off", "code": encode_ir(timings)})

        # Generate all mode/temp/fan combinations
        for mode_val, mode_name in modes:
            if mode_name == "fan":
                # Fan mode doesn't use temperature
                for fan_val, fan_name in fans:
                    ac = IRHaierAC176()
                    ac.on()
                    ac.setMode(mode_val)
                    ac.setTemp(24)
                    ac.setFan(fan_val)
                    ac.setSwingV(kHaierAcYrw02SwingVAuto)

                    state = ac.getRaw()
                    timings = self.trim_timings(sendHaierAC176(state, kHaierAC176StateLength))
                    commands.append({
                        "name": f"{mode_name}_{fan_name}",
                        "code": encode_ir(timings)
                    })
            else:
                # Other modes use temperature
                for temp in range(kHaierAcYrw02MinTempC, kHaierAcYrw02MaxTempC + 1):
                    for fan_val, fan_name in fans:
                        ac = IRHaierAC176()
                        ac.on()
                        ac.setMode(mode_val)
                        ac.setTemp(temp)
                        ac.setFan(fan_val)
                        ac.setSwingV(kHaierAcYrw02SwingVAuto)

                        state = ac.getRaw()
                        timings = self.trim_timings(sendHaierAC176(state, kHaierAC176StateLength))
                        commands.append({
                            "name": f"{mode_name}_{temp}c_{fan_name}",
                            "code": encode_ir(timings)
                        })

        # Expected: 1 off + 4 fan modes + (15 temps × 4 modes × 4 fans) = 245
        expected_count = 1 + 4 + (15 * 4 * 4)
        assert len(commands) == expected_count, f"Expected {expected_count}, got {len(commands)}"

        # Verify all commands have valid Tuya codes
        for cmd in commands:
            assert "name" in cmd
            assert "code" in cmd
            assert isinstance(cmd["code"], str)
            assert len(cmd["code"]) > 0

    def test_generated_codes_are_unique(self):
        """Test that generated Tuya codes are unique."""
        codes = set()

        modes = [
            (kHaierAcYrw02Auto, "auto"),
            (kHaierAcYrw02Cool, "cool"),
            (kHaierAcYrw02Heat, "heat"),
            (kHaierAcYrw02Dry, "dry"),
        ]

        fans = [
            (kHaierAcYrw02FanAuto, "auto"),
            (kHaierAcYrw02FanLow, "low"),
            (kHaierAcYrw02FanMed, "med"),
            (kHaierAcYrw02FanHigh, "high"),
        ]

        for mode_val, mode_name in modes:
            for temp in range(kHaierAcYrw02MinTempC, kHaierAcYrw02MaxTempC + 1):
                for fan_val, fan_name in fans:
                    ac = IRHaierAC176()
                    ac.on()
                    ac.setMode(mode_val)
                    ac.setTemp(temp)
                    ac.setFan(fan_val)

                    state = ac.getRaw()
                    timings = self.trim_timings(sendHaierAC176(state, kHaierAC176StateLength))
                    code = encode_ir(timings)
                    codes.add(code)

        # All codes should be unique
        expected_unique = 4 * 15 * 4  # 4 modes × 15 temps × 4 fans = 240
        assert len(codes) == expected_unique, f"Expected {expected_unique} unique codes, got {len(codes)}"


class TestHaierAC176CommandOutput:
    """Test command output format."""

    @staticmethod
    def trim_timings(timings):
        """Remove trailing gaps and cap values at 65535."""
        while timings and timings[-1] > 10000:
            timings = timings[:-1]
        return [min(t, 65535) for t in timings]

    def test_output_sample_commands(self):
        """Output sample commands for manual testing."""
        samples = []

        # Power off
        ac = IRHaierAC176()
        ac.off()
        state = ac.getRaw()
        timings = self.trim_timings(sendHaierAC176(state, kHaierAC176StateLength))
        samples.append(("off", encode_ir(timings)))

        # Cool 22°C Auto fan
        ac = IRHaierAC176()
        ac.on()
        ac.setMode(kHaierAcYrw02Cool)
        ac.setTemp(22)
        ac.setFan(kHaierAcYrw02FanAuto)
        state = ac.getRaw()
        timings = self.trim_timings(sendHaierAC176(state, kHaierAC176StateLength))
        samples.append(("cool_22c_auto", encode_ir(timings)))

        # Heat 24°C High fan
        ac = IRHaierAC176()
        ac.on()
        ac.setMode(kHaierAcYrw02Heat)
        ac.setTemp(24)
        ac.setFan(kHaierAcYrw02FanHigh)
        state = ac.getRaw()
        timings = self.trim_timings(sendHaierAC176(state, kHaierAC176StateLength))
        samples.append(("heat_24c_high", encode_ir(timings)))

        # Auto 25°C Med fan
        ac = IRHaierAC176()
        ac.on()
        ac.setMode(kHaierAcYrw02Auto)
        ac.setTemp(25)
        ac.setFan(kHaierAcYrw02FanMed)
        state = ac.getRaw()
        timings = self.trim_timings(sendHaierAC176(state, kHaierAC176StateLength))
        samples.append(("auto_25c_med", encode_ir(timings)))

        # Print for manual testing
        print("\n=== Sample Haier AC176 Commands ===")
        for name, code in samples:
            print(f"\n{name}:")
            print(f"  {code}")

        # Verify all samples generated
        assert len(samples) == 4


class TestHaierAC176APIEndpoint:
    """E2E tests for /api/identify endpoint with Haier AC176."""

    @pytest.fixture
    def client(self):
        """Create FastAPI test client."""
        return TestClient(app)

    def test_api_identify_haier_ac176(self, client):
        """Test /api/identify correctly identifies Haier AC176 code."""
        response = client.post(
            "/api/identify",
            json={"tuya_code": HAIER_AC176_USER_CODE}
        )

        assert response.status_code == 200
        data = response.json()

        # Verify protocol detection
        assert data["protocol"] == "HAIER_AC176"
        assert data["manufacturer"] == "Haier"

    def test_api_returns_correct_temperature_range(self, client):
        """Test API returns correct temperature range for Haier AC176."""
        response = client.post(
            "/api/identify",
            json={"tuya_code": HAIER_AC176_USER_CODE}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["min_temperature"] == kHaierAcYrw02MinTempC  # 16
        assert data["max_temperature"] == kHaierAcYrw02MaxTempC  # 30

    def test_api_returns_all_operation_modes(self, client):
        """Test API returns all operation modes."""
        response = client.post(
            "/api/identify",
            json={"tuya_code": HAIER_AC176_USER_CODE}
        )

        assert response.status_code == 200
        data = response.json()

        expected_modes = ["auto", "cool", "heat", "dry", "fan"]
        assert set(data["operation_modes"]) == set(expected_modes)

    def test_api_returns_all_fan_modes(self, client):
        """Test API returns all fan modes."""
        response = client.post(
            "/api/identify",
            json={"tuya_code": HAIER_AC176_USER_CODE}
        )

        assert response.status_code == 200
        data = response.json()

        expected_fans = ["auto", "low", "med", "high"]
        assert set(data["fan_modes"]) == set(expected_fans)

    def test_api_generates_commands(self, client):
        """Test API generates commands for Haier AC176."""
        response = client.post(
            "/api/identify",
            json={"tuya_code": HAIER_AC176_USER_CODE}
        )

        assert response.status_code == 200
        data = response.json()

        # Should generate commands
        commands = data["commands"]
        assert isinstance(commands, list)
        assert len(commands) > 0

        # Expected: 15 temps × 5 modes × 4 fans + 2 power = 302 commands
        expected_count = (15 * 5 * 4) + 2
        assert len(commands) == expected_count, f"Expected {expected_count}, got {len(commands)}"

    def test_api_command_structure(self, client):
        """Test each command has required fields."""
        response = client.post(
            "/api/identify",
            json={"tuya_code": HAIER_AC176_USER_CODE}
        )

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
        response = client.post(
            "/api/identify",
            json={"tuya_code": HAIER_AC176_USER_CODE}
        )

        assert response.status_code == 200
        data = response.json()

        # Test first 10 commands can be decoded
        for cmd in data["commands"][:10]:
            timings = decode_ir(cmd["tuya_code"])
            assert len(timings) > 0, f"Failed to decode {cmd['name']}"

    def test_api_has_power_commands(self, client):
        """Test API generates power on/off commands."""
        response = client.post(
            "/api/identify",
            json={"tuya_code": HAIER_AC176_USER_CODE}
        )

        assert response.status_code == 200
        data = response.json()

        command_names = [cmd["name"] for cmd in data["commands"]]
        assert "power_on" in command_names
        assert "power_off" in command_names

    def test_api_has_expected_temp_mode_fan_commands(self, client):
        """Test API generates specific temperature/mode/fan combinations."""
        response = client.post(
            "/api/identify",
            json={"tuya_code": HAIER_AC176_USER_CODE}
        )

        assert response.status_code == 200
        data = response.json()

        command_names = [cmd["name"] for cmd in data["commands"]]

        # Check for specific commands
        assert "22_cool_auto" in command_names
        assert "24_heat_high" in command_names
        assert "16_auto_low" in command_names
        assert "30_dry_med" in command_names


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
