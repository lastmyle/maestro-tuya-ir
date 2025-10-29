#!/usr/bin/env python3
"""
Integration tests for the simplified API endpoints
Tests both /api/manufacturers and /api/identify with snake_case format
"""

import pytest
from fastapi.testclient import TestClient
from index import app


client = TestClient(app)

def test_identify_endpoint_with_fujitsu_code():
    """Test POST /api/identify with a known Fujitsu code"""
    from app.core.ir_protocols.test_codes import FUJITSU_KNOWN_GOOD_CODES

    # Use a known good Fujitsu code with manufacturer hint
    tuya_code = FUJITSU_KNOWN_GOOD_CODES["24C_High"]

    response = client.post(
        "/api/identify",
        json={"tuya_code": tuya_code, "manufacturer": "fujitsu"}
    )

    assert response.status_code == 200
    data = response.json()

    # Check snake_case field names
    assert "protocol" in data
    assert "manufacturer" in data
    assert "commands" in data
    assert "min_temperature" in data
    assert "max_temperature" in data
    assert "operation_modes" in data
    assert "fan_modes" in data

    # Verify it detected Fujitsu
    assert data["manufacturer"] == "Fujitsu"
    assert data["protocol"] in ["FUJITSU_AC", "FUJITSU_AC264"]

    # Check temperature range
    assert isinstance(data["min_temperature"], int)
    assert isinstance(data["max_temperature"], int)
    assert data["min_temperature"] < data["max_temperature"]

    # Check modes are lists
    assert isinstance(data["operation_modes"], list)
    assert isinstance(data["fan_modes"], list)
    assert len(data["operation_modes"]) > 0
    assert len(data["fan_modes"]) > 0

    # Check commands structure
    assert isinstance(data["commands"], list)
    if len(data["commands"]) > 0:
        first_command = data["commands"][0]
        assert "name" in first_command
        assert "description" in first_command
        assert "tuya_code" in first_command  # snake_case!

    print(f"✓ Identified as {data['manufacturer']} with {len(data['commands'])} commands")


def test_identify_endpoint_with_manufacturer_hint():
    """Test POST /api/identify with manufacturer hint"""
    from app.core.ir_protocols.test_codes import FUJITSU_KNOWN_GOOD_CODES

    tuya_code = FUJITSU_KNOWN_GOOD_CODES["24C_High"]

    response = client.post(
        "/api/identify",
        json={
            "tuya_code": tuya_code,
            "manufacturer": "fujitsu"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["manufacturer"] == "Fujitsu"

    print(f"✓ Identified with hint: {data['manufacturer']}")


def test_identify_endpoint_invalid_code():
    """Test POST /api/identify with invalid Tuya code"""
    response = client.post(
        "/api/identify",
        json={"tuya_code": "invalid_base64_code"}
    )

    # Should return 400 for invalid code
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data

    print(f"✓ Invalid code rejected: {data['detail']}")


def test_root_redirects_to_docs():
    """Test that root URL redirects to /docs"""
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307  # Temporary redirect
    assert response.headers["location"] == "/docs"

    print("✓ Root redirects to /docs")


def test_swagger_ui_accessible():
    """Test that Swagger UI is accessible at /docs"""
    response = client.get("/docs")

    assert response.status_code == 200
    assert "swagger" in response.text.lower() or "openapi" in response.text.lower()

    print("✓ Swagger UI is accessible")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
