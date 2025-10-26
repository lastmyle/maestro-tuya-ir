"""
Integration tests for the full Tuya IR translation pipeline.

This tests the complete workflow that a Hubitat device would use:
1. Send a captured Tuya IR code to /api/identify to detect manufacturer/protocol
2. Use /api/generate to create a complete command set for all temperatures/modes
3. Store these commands on the Hubitat device for direct IR transmission
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


def test_full_hubitat_workflow(real_fujitsu_code):
    """
    Integration test simulating complete Hubitat device workflow.

    Workflow:
    1. User trains Hubitat with one Tuya IR command (e.g., Cool 24C)
    2. Hubitat sends code to /api/identify to detect manufacturer
    3. Hubitat calls /api/generate to get complete command set
    4. Hubitat stores all commands for direct temperature control
    5. User can now set any temperature without additional training
    """
    # Step 1: Identify the device from captured IR code
    identify_response = client.post(
        "/api/identify",
        json={"tuyaCode": real_fujitsu_code},
    )

    assert identify_response.status_code == 200
    identify_data = identify_response.json()

    print("\n=== STEP 1: IDENTIFY DEVICE ===")
    print(f"Manufacturer: {identify_data['manufacturer']}")
    print(f"Protocol: {identify_data['protocol']}")
    print(f"Confidence: {identify_data.get('confidence', 'N/A')}")

    # Verify identification was successful
    assert identify_data["success"] is True
    assert identify_data["manufacturer"] == "Fujitsu"
    assert identify_data["protocol"] in ["fujitsu_ac", "FUJITSU_AC"]

    # Check capabilities
    assert "capabilities" in identify_data
    capabilities = identify_data["capabilities"]
    assert "modes" in capabilities
    assert "cool" in [m.lower() for m in capabilities["modes"]]

    # Step 2: Decode the original command to see what state it represents
    decode_response = client.post(
        "/api/decode",
        json={"tuyaCode": real_fujitsu_code},
    )

    assert decode_response.status_code == 200
    decode_data = decode_response.json()

    print("\n=== STEP 2: DECODE ORIGINAL COMMAND ===")
    print(f"Decoded state: {decode_data.get('state', 'N/A')}")
    print(f"Timing count: {len(decode_data['timings'])}")

    # Step 3: Generate complete command set for all temperatures
    generate_response = client.post(
        "/api/generate",
        json={
            "manufacturer": identify_data["manufacturer"],
            "protocol": identify_data["protocol"],
            "filter": {
                "modes": ["cool", "heat", "auto"],
                "tempRange": [18, 30],
                "fanSpeeds": ["auto", "low", "medium", "high"],
            },
        },
    )

    assert generate_response.status_code == 200
    generate_data = generate_response.json()

    print("\n=== STEP 3: GENERATE COMMAND SET ===")
    print(f"Total commands generated: {generate_data['totalCommands']}")
    print(f"Manufacturer: {generate_data['manufacturer']}")
    print(f"Protocol: {generate_data['protocol']}")

    # Verify command structure
    assert generate_data["success"] is True
    commands = generate_data["commands"]

    # Should have "off" command
    assert "off" in commands
    assert isinstance(commands["off"], str)  # Tuya IR code

    # Should have mode-specific commands
    for mode in ["cool", "heat", "auto"]:
        assert mode in commands
        mode_commands = commands[mode]

        # Each mode should have fan speed variations
        for fan in ["auto", "low", "medium", "high"]:
            assert fan in mode_commands
            fan_commands = mode_commands[fan]

            # Each fan speed should have temperature range
            for temp in range(18, 31):
                temp_key = str(temp)
                assert temp_key in fan_commands
                tuya_code = fan_commands[temp_key]
                assert isinstance(tuya_code, str)
                assert len(tuya_code) > 0

                # Verify it's valid base64-ish Tuya format
                assert tuya_code.replace("+", "").replace("/", "").replace("=", "").isalnum()

    print("\n=== STEP 4: VERIFY COMMAND STORAGE FORMAT ===")
    print("Commands ready for Hubitat storage:")

    # Example: Show how Hubitat would store these commands
    sample_commands = {
        "cool_24_auto": commands["cool"]["auto"]["24"],
        "cool_22_high": commands["cool"]["high"]["22"],
        "heat_26_low": commands["heat"]["low"]["26"],
        "off": commands["off"],
    }

    for cmd_name, tuya_code in sample_commands.items():
        print(f"  {cmd_name}: {tuya_code[:50]}... ({len(tuya_code)} chars)")

    print("\n=== STEP 5: VERIFY COMMANDS ARE DECODABLE ===")
    # Verify a sample of generated commands can be decoded back
    test_code = commands["cool"]["auto"]["24"]
    verify_response = client.post(
        "/api/decode",
        json={"tuyaCode": test_code},
    )

    assert verify_response.status_code == 200
    verify_data = verify_response.json()
    assert verify_data["success"] is True
    assert len(verify_data["timings"]) > 0

    # Check if state was parsed
    if verify_data.get("state"):
        state = verify_data["state"]
        print("\nVerified command state:")
        print(f"  Power: {state.get('power', 'N/A')}")
        print(f"  Mode: {state.get('mode', 'N/A')}")
        print(f"  Temperature: {state.get('temperature', 'N/A')}")
        print(f"  Fan: {state.get('fan', 'N/A')}")

    print("\n✅ Integration test complete!")
    print(f"Generated {generate_data['totalCommands']} commands ready for Hubitat")


def test_generate_filtered_command_set(real_fujitsu_code):
    """
    Test generating a filtered subset of commands.

    This is useful when Hubitat has limited storage and only needs
    specific temperature ranges or modes.
    """
    # First identify the device
    identify_response = client.post(
        "/api/identify",
        json={"tuyaCode": real_fujitsu_code},
    )

    assert identify_response.status_code == 200
    identify_data = identify_response.json()

    # Generate only cool mode, limited temp range, auto fan only
    generate_response = client.post(
        "/api/generate",
        json={
            "manufacturer": identify_data["manufacturer"],
            "protocol": identify_data["protocol"],
            "filter": {
                "modes": ["cool"],
                "tempRange": [22, 26],
                "fanSpeeds": ["auto"],
            },
        },
    )

    assert generate_response.status_code == 200
    generate_data = generate_response.json()

    print("\n=== FILTERED COMMAND SET ===")
    print(f"Total commands: {generate_data['totalCommands']}")

    commands = generate_data["commands"]

    # Should only have cool mode
    assert "cool" in commands
    assert "heat" not in commands or len(commands.get("heat", {})) == 0

    # Cool mode should only have auto fan
    assert "auto" in commands["cool"]
    assert "low" not in commands["cool"]

    # Should have limited temperature range (22-26)
    auto_commands = commands["cool"]["auto"]
    assert "22" in auto_commands
    assert "23" in auto_commands
    assert "24" in auto_commands
    assert "25" in auto_commands
    assert "26" in auto_commands
    assert "21" not in auto_commands
    assert "27" not in auto_commands

    print(f"Generated commands for temperatures: {sorted(auto_commands.keys())}")


def test_error_handling_invalid_protocol():
    """Test that unsupported protocols return proper error messages."""
    response = client.post(
        "/api/generate",
        json={
            "manufacturer": "UnknownBrand",
            "protocol": "fake_protocol_xyz",
        },
    )

    assert response.status_code == 422
    error_data = response.json()
    assert "detail" in error_data
    detail = error_data["detail"]
    assert detail["success"] is False
    assert detail["error"] == "UNSUPPORTED_PROTOCOL"


def test_decode_to_identify_to_generate_round_trip():
    """
    Test complete round trip: decode -> identify -> generate -> verify.

    This ensures all APIs work together coherently.
    """
    second_fujitsu_code = (
        "B9oMWAatAYIBgAMFyASCAYIBQAcBrQFAB8ADQA9AA8APQAdAD0ADQAvgIQNAAQGtAeAJN0AB"
        "Aa0BwAPgAx8CrQGCIAEBrQFAE+AJAwCC4AATAYIBQAMBggFAE0AJ4BMDQCMByARAIQKCAa0g"
        "AYAFAa0BQAdAA4AbAK1gAcALQA/gOQNAAeAJRwGtAeANFQGtAeALF+AVEwPlAYIBQCMDyASC"
        "AUAH4A8DC8gEggGtAYIBrQGCAQ=="
    )

    # 1. Decode
    decode_resp = client.post("/api/decode", json={"tuyaCode": second_fujitsu_code})
    assert decode_resp.status_code == 200
    decode_data = decode_resp.json()
    assert decode_data["success"] is True

    # 2. Identify
    identify_resp = client.post("/api/identify", json={"tuyaCode": second_fujitsu_code})
    assert identify_resp.status_code == 200
    identify_data = identify_resp.json()
    assert identify_data["success"] is True

    manufacturer = identify_data["manufacturer"]
    protocol = identify_data["protocol"]

    # 3. Generate
    generate_resp = client.post(
        "/api/generate",
        json={
            "manufacturer": manufacturer,
            "protocol": protocol,
            "filter": {"modes": ["cool"], "tempRange": [24, 24], "fanSpeeds": ["auto"]},
        },
    )
    assert generate_resp.status_code == 200
    generate_data = generate_resp.json()
    assert generate_data["success"] is True

    # 4. Verify generated command is decodable
    generated_code = generate_data["commands"]["cool"]["auto"]["24"]
    verify_resp = client.post("/api/decode", json={"tuyaCode": generated_code})
    assert verify_resp.status_code == 200
    verify_data = verify_resp.json()
    assert verify_data["success"] is True

    print(f"\n✅ Round trip successful for {manufacturer} {protocol}")
    print(f"   Original timings: {len(decode_data['timings'])}")
    print(f"   Generated timings: {len(verify_data['timings'])}")
