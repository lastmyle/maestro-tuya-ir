"""
Tests for protocol detection and identification.
"""

import pytest

from app.core.protocols import (
    get_protocol_by_name,
    get_supported_manufacturers,
    identify_protocol,
)


def test_identify_fujitsu():
    """Test identifying Fujitsu protocol from header timings."""
    # Fujitsu header: 9000, 4500
    timings = [9000, 4500, 600, 540, 600, 1600]
    result = identify_protocol(timings)

    assert result["manufacturer"] == "Fujitsu"
    assert result["protocol"] == "fujitsu_ac"
    assert result["confidence"] > 0.8


def test_identify_daikin():
    """Test identifying Daikin protocol."""
    # Daikin header: 3500, 1728
    timings = [3500, 1728, 428, 1280, 428, 428]
    result = identify_protocol(timings)

    assert result["manufacturer"] == "Daikin"
    assert result["protocol"] == "daikin_ac"


def test_identify_with_manufacturer_hint():
    """Test protocol identification with manufacturer hint."""
    timings = [9000, 4500, 600, 540]
    result = identify_protocol(timings, manufacturer_hint="Fujitsu")

    assert result["manufacturer"] == "Fujitsu"
    assert result["confidence"] > 0.9  # Higher confidence with hint


def test_identify_insufficient_timings():
    """Test that insufficient timings raise ValueError."""
    with pytest.raises(ValueError, match="Insufficient timing data"):
        identify_protocol([9000])  # Only one timing


def test_identify_unknown_protocol():
    """Test that unknown protocol raises ValueError."""
    # Very unusual timings that don't match any protocol
    timings = [1234, 5678, 9012, 3456]
    with pytest.raises(ValueError, match="Could not identify protocol"):
        identify_protocol(timings)


def test_get_protocol_by_name():
    """Test retrieving protocol definition by name."""
    protocol = get_protocol_by_name("fujitsu_ac")

    assert protocol is not None
    assert protocol.manufacturer == "Fujitsu"
    assert protocol.name == "fujitsu_ac"


def test_get_protocol_by_name_invalid():
    """Test that invalid protocol name returns None."""
    protocol = get_protocol_by_name("nonexistent_ac")

    assert protocol is None


def test_get_supported_manufacturers():
    """Test getting list of supported manufacturers."""
    manufacturers = get_supported_manufacturers()

    assert isinstance(manufacturers, list)
    assert "Fujitsu" in manufacturers
    assert "Daikin" in manufacturers
    assert "Mitsubishi" in manufacturers
    assert len(manufacturers) >= 5  # At least 5 manufacturers


def test_protocol_capabilities():
    """Test that protocol definitions include capabilities."""
    result = identify_protocol([9000, 4500, 600, 540])

    assert "capabilities" in result
    caps = result["capabilities"]
    assert "modes" in caps
    assert "fanSpeeds" in caps
    assert "tempRange" in caps
    assert "features" in caps
