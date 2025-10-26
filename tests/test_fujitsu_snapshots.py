"""
Snapshot tests for Fujitsu HVAC commands.

These tests capture the full API responses including all generated IR codes
so you can manually test them with your IR blaster.

To update snapshots after changes: pytest --snapshot-update
"""

import pytest
from fastapi.testclient import TestClient

from index import app

client = TestClient(app)


@pytest.fixture
def real_fujitsu_code():
    """Real Fujitsu HVAC IR code captured from Tuya device."""
    return (
        "Ed4MRQYFAkQBxAGIAcQBwATEAYAHQBMAiKABA8QBwASAA0ALQAMGRAHEAcAEiCADA8QBiAGA"
        "A0ATgAvAAUAPQAFAB4ADAsQBiGABQDfAL8AHAIhgAQDEIAEBiAHgAR8BiAFAD0ABQBMBwARA"
        "B0ADQAtAA0ALQAMBxAHARwjABIgBiAHEAYhgAUAH4AcDAYgBQCNAAwGIAYAbQAsCxAGIoAEB"
        "xAFAS0ADQAsDwATEAcALQA8AiKABwAlABwHEAYAhQAECxAGIYAFAB+ADA4ABQBGAAQDEIAEB"
        "RAFBZ0AHAsQBiCABgAUBiAGAB0AFAcQBgBsCxAGIYAHAB0ABAcQB4BMbQLcAiKABAcAE4AU"
        "DQAELwATEAYgBxAGIAYgB"
    )


def test_fujitsu_identify_snapshot(snapshot, real_fujitsu_code):
    """
    Snapshot test for Fujitsu identification response.

    This captures the manufacturer, protocol, and capabilities.
    """
    response = client.post(
        "/api/identify",
        json={"tuyaCode": real_fujitsu_code},
    )

    assert response.status_code == 200
    data = response.json()

    # Snapshot the full response
    assert data == snapshot


def test_fujitsu_decode_snapshot(snapshot, real_fujitsu_code):
    """
    Snapshot test for decoding Fujitsu IR code.

    This captures the raw timings and decoded state.
    """
    response = client.post(
        "/api/decode",
        json={"tuyaCode": real_fujitsu_code},
    )

    assert response.status_code == 200
    data = response.json()

    # Snapshot the full response
    assert data == snapshot


def test_fujitsu_generate_cool_auto_snapshot(snapshot, real_fujitsu_code):
    """
    Snapshot test for generating Fujitsu Cool mode commands with Auto fan.

    This captures ALL Cool/Auto commands for temperatures 18-30°C.
    You can manually test these codes with your IR blaster!
    """
    # First identify to get protocol
    identify_response = client.post(
        "/api/identify",
        json={"tuyaCode": real_fujitsu_code},
    )
    identify_data = identify_response.json()

    # Generate Cool mode, Auto fan, all temperatures
    response = client.post(
        "/api/generate",
        json={
            "manufacturer": identify_data["manufacturer"],
            "protocol": identify_data["protocol"],
            "filter": {
                "modes": ["cool"],
                "tempRange": [18, 30],
                "fanSpeeds": ["auto"],
            },
        },
    )

    assert response.status_code == 200
    data = response.json()

    # Snapshot the full response with all IR codes
    assert data == snapshot


def test_fujitsu_generate_common_temps_snapshot(snapshot, real_fujitsu_code):
    """
    Snapshot test for common temperature settings (22-26°C).

    This generates commands for the most commonly used temperature range
    across multiple modes and fan speeds.

    Test these commands with your IR blaster:
    - Cool 24°C Auto
    - Cool 24°C High
    - Heat 22°C Auto
    - etc.
    """
    # First identify to get protocol
    identify_response = client.post(
        "/api/identify",
        json={"tuyaCode": real_fujitsu_code},
    )
    identify_data = identify_response.json()

    # Generate common temperature range with multiple modes/fans
    response = client.post(
        "/api/generate",
        json={
            "manufacturer": identify_data["manufacturer"],
            "protocol": identify_data["protocol"],
            "filter": {
                "modes": ["cool", "heat"],
                "tempRange": [22, 26],
                "fanSpeeds": ["auto", "low", "high"],
            },
        },
    )

    assert response.status_code == 200
    data = response.json()

    # Snapshot the full response
    assert data == snapshot


def test_fujitsu_generate_all_modes_24c_snapshot(snapshot, real_fujitsu_code):
    """
    Snapshot test for all modes at 24°C with auto fan.

    This is perfect for testing different modes with your IR blaster:
    - Cool 24°C Auto
    - Heat 24°C Auto
    - Dry 24°C Auto
    - Fan 24°C Auto
    - Auto 24°C Auto
    - Off
    """
    # First identify to get protocol
    identify_response = client.post(
        "/api/identify",
        json={"tuyaCode": real_fujitsu_code},
    )
    identify_data = identify_response.json()

    # Generate all modes at 24°C
    response = client.post(
        "/api/generate",
        json={
            "manufacturer": identify_data["manufacturer"],
            "protocol": identify_data["protocol"],
            "filter": {
                "modes": ["cool", "heat", "dry", "fan", "auto"],
                "tempRange": [24, 24],
                "fanSpeeds": ["auto"],
            },
        },
    )

    assert response.status_code == 200
    data = response.json()

    # Snapshot the full response
    assert data == snapshot


def test_fujitsu_generate_fan_speeds_24c_cool_snapshot(snapshot, real_fujitsu_code):
    """
    Snapshot test for all fan speeds in Cool mode at 24°C.

    Test these with your IR blaster to verify fan speed control:
    - Cool 24°C Auto
    - Cool 24°C Low
    - Cool 24°C Medium
    - Cool 24°C High
    - Cool 24°C Quiet
    """
    # First identify to get protocol
    identify_response = client.post(
        "/api/identify",
        json={"tuyaCode": real_fujitsu_code},
    )
    identify_data = identify_response.json()

    # Generate all fan speeds at Cool 24°C
    response = client.post(
        "/api/generate",
        json={
            "manufacturer": identify_data["manufacturer"],
            "protocol": identify_data["protocol"],
            "filter": {
                "modes": ["cool"],
                "tempRange": [24, 24],
                "fanSpeeds": ["auto", "low", "medium", "high", "quiet"],
            },
        },
    )

    assert response.status_code == 200
    data = response.json()

    # Snapshot the full response
    assert data == snapshot


def test_fujitsu_roundtrip_validation(snapshot, real_fujitsu_code):
    """
    Validates the entire pipeline works by comparing input/output.

    This test:
    1. Sends the original Fujitsu code to identify
    2. Generates ALL commands for the same protocol
    3. Compares original vs generated (NOTE: exact match not expected!)
    4. Verifies generated commands can be decoded
    5. Snapshots everything for manual validation

    IMPORTANT: The original code likely WON'T match generated codes exactly because:
    - Original was captured from real device (may have timing variations)
    - Generator creates idealized IR patterns from protocol specs
    - Both decode to same manufacturer/protocol - that's what matters!

    This proves the service identifies protocols correctly even if exact
    codes differ - which is expected and correct behavior!
    """
    # Step 1: Identify original code
    identify_response = client.post(
        "/api/identify",
        json={"tuyaCode": real_fujitsu_code},
    )
    identify_data = identify_response.json()

    # Step 2: Decode original to see what it contains
    decode_original = client.post(
        "/api/decode",
        json={"tuyaCode": real_fujitsu_code},
    )
    decode_original_data = decode_original.json()

    # Step 3: Generate ALL commands for the same protocol (full range)
    generate_response = client.post(
        "/api/generate",
        json={
            "manufacturer": identify_data["manufacturer"],
            "protocol": identify_data["protocol"],
            # No filter - generate everything to compare
        },
    )
    generate_data = generate_response.json()

    # Step 4: Check if original code appears in generated codes
    # (This will likely be False - see docstring for why that's OK)
    all_generated_codes = []
    commands = generate_data["commands"]
    for mode, mode_data in commands.items():
        if mode == "off":
            all_generated_codes.append(mode_data)
        elif isinstance(mode_data, dict):
            for fan, temps in mode_data.items():
                for temp, code in temps.items():
                    all_generated_codes.append(code)

    original_in_generated = real_fujitsu_code in all_generated_codes

    # Step 5: Pick a generated command and verify it can be decoded
    sample_code = generate_data["commands"]["cool"]["auto"]["24"]
    decode_response = client.post(
        "/api/decode",
        json={"tuyaCode": sample_code},
    )
    decode_data = decode_response.json()

    # Create validation snapshot
    validation_result = {
        "original_code": real_fujitsu_code,
        "original_code_timings_count": len(decode_original_data["timings"]),
        "identified_manufacturer": identify_data["manufacturer"],
        "identified_protocol": identify_data["protocol"],
        "total_generated_commands": len(all_generated_codes),
        "original_code_matches_generated": original_in_generated,
        "sample_generated_code_cool_24_auto": sample_code,
        "sample_generated_timings_count": len(decode_data["timings"]),
        "sample_decoded_protocol": decode_data["protocol"],
        "workflow_validation": {
            "original_identifies_correctly": identify_data["manufacturer"] == "Fujitsu",
            "generated_decodes_correctly": decode_data["protocol"]["manufacturer"] == "Fujitsu",
            "both_same_protocol": (
                identify_data["protocol"] == decode_data["protocol"]["name"]
            ),
        },
    }

    # Snapshot for manual validation
    assert validation_result == snapshot

    # Assert that workflow works even if codes don't match exactly
    assert identify_data["manufacturer"] == "Fujitsu", "Should identify manufacturer"
    assert (
        decode_data["protocol"]["manufacturer"] == "Fujitsu"
    ), "Generated codes should decode to same manufacturer"
