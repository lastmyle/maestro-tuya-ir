#!/usr/bin/env python3
"""
End-to-end tests for Daikin protocol detection and command generation.

Tests the complete workflow using real user-captured IR codes.
"""

import pytest
from fastapi.testclient import TestClient
from index import app
from app.core.tuya_encoder import decode_ir
from app.core.ir_protocols import decode, decode_results, decode_type_t


# Real Daikin IR code from user
DAIKIN_USER_CODE = "AacBQAEC4QGn4AQBC61iiQ3jBqcBHgWnAeADAUAPQCtAA8ABQBNAAUAHQANAAUAH4AcDwDNAF0ABQA9AA8AB4AsLwCvAB0AjQANAD0ADQAFAD0ABQAfgCxNAF8AB4AcLQC/AA0ABQB/AD0AHAamL4QUHQB9AAUAbQAFAD0ADQAHAE0AHQANAF0AH4AcDQBdAA0AXQAdAAUAHQAPAAcALQAdAA0ABQC9AAUAPQANAAcATQAHAE0ABwAtAB0ADQAFAB0ADQAHgCzdAG0AXQAdAA0ALQANAC+F3B0ABBFQCIwGnoAFAk0ABQAdAA0ABQAdAA0ABQAdAuwGnAUAJgAFACUADQBdAB0ABQAtAA8APQAHAC0AHQAPAAcALQAdAA8ABQD9AAcAH4AMbQAHAD0AHQAPAAcALQAdAA0ABQAdAR0ADQAFAD0ADwAHgCwtAK0AD4AsbQBNAA0ABQAdAA8AB4AsLQEdAAcAHQCNAA0APQANAAUAPQAFAB0ADwAHgBwtAL+ALE0AX4AMDC6cBpwHhAacBpwGnAQ=="


class TestDaikinDecoder:
    """Test Daikin protocol decoder."""

    def test_decode_daikin_user_code(self):
        """Test decoding a real Daikin IR code from user."""
        timings = decode_ir(DAIKIN_USER_CODE)

        # Should have timings
        assert len(timings) > 0

        results = decode_results()
        results.rawbuf = timings
        results.rawlen = len(timings)

        success = decode(results)

        assert success, "Daikin code should decode successfully"
        assert results.decode_type == decode_type_t.DAIKIN
        assert results.bits == 280  # Daikin is 35 bytes = 280 bits

    def test_daikin_state_bytes(self):
        """Test that decoded state bytes are valid."""
        timings = decode_ir(DAIKIN_USER_CODE)

        results = decode_results()
        results.rawbuf = timings
        results.rawlen = len(timings)

        decode(results)

        # State should be 35 bytes
        state = results.state[:35]

        # Check known Daikin header bytes
        # Section 1 starts with signature bytes
        assert state[0] == 0x11  # Daikin signature
        assert state[1] == 0xDA  # Daikin signature
        assert state[2] == 0x27  # Daikin signature


class TestDaikinAPIEndpoint:
    """E2E tests for /api/identify endpoint with Daikin."""

    @pytest.fixture
    def client(self):
        """Create FastAPI test client."""
        return TestClient(app)

    def test_api_identify_daikin(self, client):
        """Test /api/identify correctly identifies Daikin code."""
        response = client.post(
            "/api/identify",
            json={"tuya_code": DAIKIN_USER_CODE}
        )

        assert response.status_code == 200
        data = response.json()

        # Verify protocol detection
        assert data["protocol"] == "DAIKIN"
        assert data["manufacturer"] == "Daikin"

    def test_api_generates_commands(self, client):
        """Test API generates commands for Daikin."""
        response = client.post(
            "/api/identify",
            json={"tuya_code": DAIKIN_USER_CODE}
        )

        assert response.status_code == 200
        data = response.json()

        # Should generate commands
        commands = data["commands"]
        assert isinstance(commands, list)
        assert len(commands) > 0

    def test_api_command_structure(self, client):
        """Test each command has required fields."""
        response = client.post(
            "/api/identify",
            json={"tuya_code": DAIKIN_USER_CODE}
        )

        assert response.status_code == 200
        data = response.json()

        for cmd in data["commands"]:
            assert "name" in cmd
            assert "description" in cmd
            assert "tuya_code" in cmd
            assert isinstance(cmd["tuya_code"], str)
            assert len(cmd["tuya_code"]) > 0

    def test_api_has_power_commands(self, client):
        """Test API generates power on/off commands."""
        response = client.post(
            "/api/identify",
            json={"tuya_code": DAIKIN_USER_CODE}
        )

        assert response.status_code == 200
        data = response.json()

        command_names = [cmd["name"] for cmd in data["commands"]]
        assert "power_on" in command_names
        assert "power_off" in command_names

    def test_api_generates_full_command_matrix(self, client):
        """Test API generates full command matrix with temp/mode/fan combinations."""
        response = client.post(
            "/api/identify",
            json={"tuya_code": DAIKIN_USER_CODE}
        )

        assert response.status_code == 200
        data = response.json()

        # Daikin has:
        # - Temps: 10-32°C = 23 values
        # - Modes: auto, cool, heat, dry, fan = 5 modes
        # - Fans: auto, quiet, 1, 2, 3, 4, 5 = 7 speeds
        # Total: 23 * 5 * 7 = 805 + 2 power commands = 807
        commands = data["commands"]
        assert len(commands) > 100, f"Expected full command matrix, got {len(commands)} commands"

        # Verify we have different temperature commands
        temp_commands = [c for c in commands if c["name"].startswith("2")]  # e.g., "22_cool_auto"
        assert len(temp_commands) > 20, "Should have commands for multiple temperatures"

        # Verify we have different mode commands
        cool_commands = [c for c in commands if "_cool_" in c["name"]]
        heat_commands = [c for c in commands if "_heat_" in c["name"]]
        assert len(cool_commands) > 10, "Should have multiple cool commands"
        assert len(heat_commands) > 10, "Should have multiple heat commands"

    def test_api_generated_codes_are_valid_tuya(self, client):
        """Test generated Tuya codes can be decoded back to timings."""
        response = client.post(
            "/api/identify",
            json={"tuya_code": DAIKIN_USER_CODE}
        )

        assert response.status_code == 200
        data = response.json()

        # Test first 5 commands can be decoded
        for cmd in data["commands"][:5]:
            timings = decode_ir(cmd["tuya_code"])
            assert len(timings) > 0, f"Failed to decode {cmd['name']}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
