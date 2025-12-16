#!/usr/bin/env python3
"""
Integration tests for Daikin216 protocol command generation.

Tests the complete workflow:
1. Decode Tuya IR code
2. Identify as DAIKIN216
3. Generate full command set (807 commands)
4. Verify command structure and validity
"""

import pytest
from fastapi.testclient import TestClient
from index import app
from app.core.tuya_encoder import decode_ir, encode_ir
from app.core.ir_protocols.daikin import (
    IRDaikin216,
    sendDaikin216,
    kDaikin216StateLength,
    kDaikinMinTemp,
    kDaikinMaxTemp,
    kDaikinAuto,
    kDaikinCool,
    kDaikinHeat,
    kDaikinDry,
    kDaikinFan,
    kDaikinFanAuto,
    kDaikinFanQuiet,
    kDaikinFanMin,
    kDaikinFanMax,
)

client = TestClient(app)

# Real Daikin216 code captured from user's device
DAIKIN216_TEST_CODE = "C3AN1gakARQFpAHCAeABA+AHD+ADE0AH4AcL4AMD4BND4ANL4Asz4FMD4BNnAdJzgQfgW4fg/wPg6wMB0nM="


def test_daikin216_class_basic_operations():
    """Test IRDaikin216 class basic setters and getters."""
    ac = IRDaikin216()

    # Test power
    ac.on()
    assert ac.getPower() == True
    ac.off()
    assert ac.getPower() == False

    # Test temperature
    ac.setTemp(24)
    assert ac.getTemp() == 24

    ac.setTemp(10)  # Min
    assert ac.getTemp() == 10

    ac.setTemp(32)  # Max
    assert ac.getTemp() == 32

    ac.setTemp(5)  # Below min, should clamp to 10
    assert ac.getTemp() == 10

    ac.setTemp(40)  # Above max, should clamp to 32
    assert ac.getTemp() == 32

    # Test modes
    ac.setMode(kDaikinCool)
    assert ac.getMode() == kDaikinCool

    ac.setMode(kDaikinHeat)
    assert ac.getMode() == kDaikinHeat

    ac.setMode(kDaikinAuto)
    assert ac.getMode() == kDaikinAuto

    # Test fan speeds
    ac.setFan(kDaikinFanAuto)
    assert ac.getFan() == kDaikinFanAuto

    ac.setFan(kDaikinFanQuiet)
    assert ac.getFan() == kDaikinFanQuiet

    ac.setFan(kDaikinFanMin)  # Fan 1
    assert ac.getFan() == 2 + kDaikinFanMin  # Encoded as 2+fan

    ac.setFan(kDaikinFanMax)  # Fan 5
    assert ac.getFan() == 2 + kDaikinFanMax  # Encoded as 2+fan

    # Test swing
    ac.setSwingVertical(True)
    assert ac.getSwingVertical() == True

    ac.setSwingVertical(False)
    assert ac.getSwingVertical() == False

    ac.setSwingHorizontal(True)
    assert ac.getSwingHorizontal() == True

    ac.setSwingHorizontal(False)
    assert ac.getSwingHorizontal() == False

    # Test powerful mode
    ac.setPowerful(True)
    assert ac.getPowerful() == True

    ac.setPowerful(False)
    assert ac.getPowerful() == False


def test_daikin216_class_state_bytes():
    """Test IRDaikin216 generates valid state bytes."""
    ac = IRDaikin216()

    # Set a specific state
    ac.on()
    ac.setTemp(24)
    ac.setMode(kDaikinCool)
    ac.setFan(kDaikinFanAuto)

    state = ac.getRaw()

    # Verify state length
    assert len(state) == kDaikin216StateLength  # 27 bytes

    # Verify magic bytes
    assert state[0] == 0x11
    assert state[1] == 0xDA
    assert state[2] == 0x27
    assert state[3] == 0xF0
    assert state[8] == 0x11
    assert state[9] == 0xDA
    assert state[10] == 0x27
    assert state[23] == 0xC0

    # Verify checksums are set (non-zero after calculation)
    assert state[7] != 0  # Sum1
    assert state[26] != 0  # Sum2

    # Verify power bit (byte 13, bit 0)
    assert (state[13] & 0b00000001) == 1

    # Verify mode (byte 13, bits 2-4)
    mode = (state[13] >> 2) & 0b111
    assert mode == kDaikinCool

    # Verify temperature (byte 14, bits 1-6)
    temp = (state[14] >> 1) & 0b111111
    assert temp == 24


def test_daikin216_generate_and_encode():
    """Test generating IR timings and encoding to Tuya format."""
    ac = IRDaikin216()

    # Set a state
    ac.on()
    ac.setTemp(22)
    ac.setMode(kDaikinCool)
    ac.setFan(kDaikinFanMin + 1)  # Fan 2

    # Get raw state
    state = ac.getRaw()

    # Generate IR timings
    timings = sendDaikin216(state, len(state))

    # Verify timings generated
    assert len(timings) > 0
    assert all(isinstance(t, int) for t in timings)
    assert all(t > 0 for t in timings)

    # Encode to Tuya format
    tuya_code = encode_ir(timings)

    # Verify Tuya code generated
    assert isinstance(tuya_code, str)
    assert len(tuya_code) > 0

    # Verify it can be decoded back
    decoded_timings = decode_ir(tuya_code)
    assert len(decoded_timings) > 0


def test_daikin216_api_identify():
    """Test /api/identify endpoint with Daikin216 code."""
    response = client.post(
        "/api/identify",
        json={"tuya_code": DAIKIN216_TEST_CODE}
    )

    assert response.status_code == 200
    data = response.json()

    # Verify protocol detection
    assert data["manufacturer"] == "Daikin"
    assert data["protocol"] == "DAIKIN216"

    # Verify temperature range
    assert data["min_temperature"] == kDaikinMinTemp  # 10
    assert data["max_temperature"] == kDaikinMaxTemp  # 32

    # Verify modes
    assert "auto" in data["operation_modes"]
    assert "cool" in data["operation_modes"]
    assert "heat" in data["operation_modes"]
    assert "dry" in data["operation_modes"]
    assert "fan" in data["operation_modes"]

    # Verify fan modes
    assert "auto" in data["fan_modes"]
    assert "quiet" in data["fan_modes"]
    assert "1" in data["fan_modes"]
    assert "2" in data["fan_modes"]
    assert "3" in data["fan_modes"]
    assert "4" in data["fan_modes"]
    assert "5" in data["fan_modes"]


def test_daikin216_api_full_command_generation():
    """Test complete command set generation via API."""
    response = client.post(
        "/api/identify",
        json={"tuya_code": DAIKIN216_TEST_CODE}
    )

    assert response.status_code == 200
    data = response.json()

    # Verify commands generated
    commands = data["commands"]
    assert isinstance(commands, list)

    # Expected: 23 temps × 5 modes × 7 fans + 2 power = 807 commands
    expected_command_count = (
        (kDaikinMaxTemp - kDaikinMinTemp + 1) *  # 23 temperatures (10-32)
        5 *  # 5 modes (auto, cool, heat, dry, fan)
        7    # 7 fan speeds (auto, quiet, 1-5)
        + 2  # 2 power commands (on, off)
    )
    assert len(commands) == expected_command_count  # 807

    # Verify command structure
    first_cmd = commands[0]
    assert "name" in first_cmd
    assert "description" in first_cmd
    assert "tuya_code" in first_cmd

    # Verify tuya_code is valid
    assert isinstance(first_cmd["tuya_code"], str)
    assert len(first_cmd["tuya_code"]) > 0

    # Test decoding a generated command
    tuya_code = first_cmd["tuya_code"]
    timings = decode_ir(tuya_code)
    assert len(timings) > 0


def test_daikin216_command_naming():
    """Test command naming follows expected pattern."""
    response = client.post(
        "/api/identify",
        json={"tuya_code": DAIKIN216_TEST_CODE}
    )

    data = response.json()
    commands = data["commands"]

    # Find specific commands
    cmd_24_cool_auto = None
    cmd_18_heat_quiet = None
    cmd_power_on = None
    cmd_power_off = None

    for cmd in commands:
        if cmd["name"] == "24_cool_auto":
            cmd_24_cool_auto = cmd
        elif cmd["name"] == "18_heat_quiet":
            cmd_18_heat_quiet = cmd
        elif cmd["name"] == "power_on":
            cmd_power_on = cmd
        elif cmd["name"] == "power_off":
            cmd_power_off = cmd

    # Verify expected commands exist
    assert cmd_24_cool_auto is not None
    assert cmd_24_cool_auto["description"] == "24°C, Cool, Auto fan"

    assert cmd_18_heat_quiet is not None
    assert cmd_18_heat_quiet["description"] == "18°C, Heat, Quiet fan"

    assert cmd_power_on is not None
    assert cmd_power_on["description"] == "Turn power on"

    assert cmd_power_off is not None
    assert cmd_power_off["description"] == "Turn power off"


def test_daikin216_all_temps_generated():
    """Test all temperatures from 10-32°C are generated."""
    response = client.post(
        "/api/identify",
        json={"tuya_code": DAIKIN216_TEST_CODE}
    )

    data = response.json()
    commands = data["commands"]

    # Extract all temperatures from command names
    temps_found = set()
    for cmd in commands:
        name = cmd["name"]
        if "_" in name and not name.startswith("power"):
            temp_str = name.split("_")[0]
            try:
                temp = int(temp_str)
                temps_found.add(temp)
            except ValueError:
                pass

    # Verify all temps from 10-32
    expected_temps = set(range(kDaikinMinTemp, kDaikinMaxTemp + 1))
    assert temps_found == expected_temps


def test_daikin216_all_modes_generated():
    """Test all operating modes are generated."""
    response = client.post(
        "/api/identify",
        json={"tuya_code": DAIKIN216_TEST_CODE}
    )

    data = response.json()
    commands = data["commands"]

    # Extract all modes from command names
    modes_found = set()
    for cmd in commands:
        name = cmd["name"]
        if "_" in name and not name.startswith("power"):
            parts = name.split("_")
            if len(parts) >= 2:
                mode = parts[1]
                modes_found.add(mode)

    # Verify all modes
    expected_modes = {"auto", "cool", "heat", "dry", "fan"}
    assert modes_found == expected_modes


def test_daikin216_all_fans_generated():
    """Test all fan speeds are generated."""
    response = client.post(
        "/api/identify",
        json={"tuya_code": DAIKIN216_TEST_CODE}
    )

    data = response.json()
    commands = data["commands"]

    # Extract all fan speeds from command names
    fans_found = set()
    for cmd in commands:
        name = cmd["name"]
        if "_" in name and not name.startswith("power"):
            parts = name.split("_")
            if len(parts) >= 3:
                fan = parts[2]
                fans_found.add(fan)

    # Verify all fan speeds
    expected_fans = {"auto", "quiet", "1", "2", "3", "4", "5"}
    assert fans_found == expected_fans


def test_daikin216_generated_codes_are_unique():
    """Test that generated Tuya codes are unique (no duplicates)."""
    response = client.post(
        "/api/identify",
        json={"tuya_code": DAIKIN216_TEST_CODE}
    )

    data = response.json()
    commands = data["commands"]

    # Extract all Tuya codes
    tuya_codes = [cmd["tuya_code"] for cmd in commands]

    # Verify all codes are unique
    # Note: Power on/off might be the same, so we allow 1 duplicate
    unique_codes = set(tuya_codes)

    # Should have at least 806 unique codes (power on/off might be identical)
    assert len(unique_codes) >= 806


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
