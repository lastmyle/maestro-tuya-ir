"""
Tests for the /api/manufacturers endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from index import app


client = TestClient(app)


class TestManufacturersEndpoint:
    """Tests for GET /api/manufacturers"""

    def test_list_manufacturers_returns_list(self):
        """GET /api/manufacturers should return a list of manufacturers"""
        response = client.get("/api/manufacturers")
        assert response.status_code == 200
        data = response.json()
        assert "manufacturers" in data
        assert isinstance(data["manufacturers"], list)

    def test_list_manufacturers_not_empty(self):
        """Should return at least some manufacturers with known codes"""
        response = client.get("/api/manufacturers")
        data = response.json()
        assert len(data["manufacturers"]) > 0

    def test_list_manufacturers_includes_known_brands(self):
        """Should include manufacturers we have known good codes for"""
        response = client.get("/api/manufacturers")
        data = response.json()
        manufacturers = data["manufacturers"]

        # We know we have codes for at least Fujitsu, Mitsubishi, Panasonic
        # (based on test_codes.py)
        known_brands = ["Fujitsu", "Mitsubishi", "Panasonic"]
        for brand in known_brands:
            assert brand in manufacturers, f"Expected {brand} in manufacturers list"

    def test_manufacturers_are_sorted(self):
        """Manufacturers should be returned in alphabetical order"""
        response = client.get("/api/manufacturers")
        data = response.json()
        manufacturers = data["manufacturers"]
        assert manufacturers == sorted(manufacturers)


class TestGenerateFromManufacturerEndpoint:
    """Tests for POST /api/generate-from-manufacturer"""

    def test_generate_fujitsu_commands(self):
        """Should generate commands for Fujitsu"""
        response = client.post(
            "/api/generate-from-manufacturer",
            json={"manufacturer": "Fujitsu"}
        )
        assert response.status_code == 200
        data = response.json()

        assert data["protocol"] == "FUJITSU_AC"
        assert data["manufacturer"] == "Fujitsu"
        assert "commands" in data
        assert len(data["commands"]) > 0

    def test_generate_mitsubishi_commands(self):
        """Should generate commands for Mitsubishi"""
        response = client.post(
            "/api/generate-from-manufacturer",
            json={"manufacturer": "Mitsubishi"}
        )
        assert response.status_code == 200
        data = response.json()

        assert "MITSUBISHI" in data["protocol"]
        assert data["manufacturer"] == "Mitsubishi"
        assert len(data["commands"]) > 0

    def test_generate_panasonic_commands(self):
        """Should generate commands for Panasonic"""
        response = client.post(
            "/api/generate-from-manufacturer",
            json={"manufacturer": "Panasonic"}
        )
        assert response.status_code == 200
        data = response.json()

        assert "PANASONIC" in data["protocol"]
        assert len(data["commands"]) > 0

    def test_case_insensitive_manufacturer(self):
        """Manufacturer name should be case-insensitive"""
        response1 = client.post(
            "/api/generate-from-manufacturer",
            json={"manufacturer": "fujitsu"}
        )
        response2 = client.post(
            "/api/generate-from-manufacturer",
            json={"manufacturer": "FUJITSU"}
        )
        response3 = client.post(
            "/api/generate-from-manufacturer",
            json={"manufacturer": "Fujitsu"}
        )

        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response3.status_code == 200

    def test_unknown_manufacturer_returns_404(self):
        """Unknown manufacturer should return 404"""
        response = client.post(
            "/api/generate-from-manufacturer",
            json={"manufacturer": "NonExistentBrand"}
        )
        assert response.status_code == 404
        assert "No known codes" in response.json()["detail"]

    def test_generated_commands_have_required_fields(self):
        """Each command should have name, description, and tuya_code"""
        response = client.post(
            "/api/generate-from-manufacturer",
            json={"manufacturer": "Fujitsu"}
        )
        data = response.json()

        for cmd in data["commands"]:
            assert "name" in cmd
            assert "description" in cmd
            assert "tuya_code" in cmd
            assert len(cmd["tuya_code"]) > 0

    def test_response_includes_temperature_range(self):
        """Response should include min/max temperature"""
        response = client.post(
            "/api/generate-from-manufacturer",
            json={"manufacturer": "Fujitsu"}
        )
        data = response.json()

        assert "min_temperature" in data
        assert "max_temperature" in data
        assert data["min_temperature"] < data["max_temperature"]

    def test_response_includes_modes_and_fans(self):
        """Response should include operation_modes and fan_modes"""
        response = client.post(
            "/api/generate-from-manufacturer",
            json={"manufacturer": "Fujitsu"}
        )
        data = response.json()

        assert "operation_modes" in data
        assert "fan_modes" in data
        assert len(data["operation_modes"]) > 0
        assert len(data["fan_modes"]) > 0

    def test_includes_power_commands(self):
        """Should include power_on and power_off commands"""
        response = client.post(
            "/api/generate-from-manufacturer",
            json={"manufacturer": "Fujitsu"}
        )
        data = response.json()

        command_names = [cmd["name"] for cmd in data["commands"]]
        assert "power_on" in command_names
        assert "power_off" in command_names
