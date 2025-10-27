"""
Tests for HVAC code generator.
"""

import pytest

from app.core.generator import HVACCodeGenerator, generate_command
from app.core.tuya import decode_tuya_ir


def test_generator_initialization():
    """Test creating a generator for a protocol."""
    generator = HVACCodeGenerator("fujitsu_ac")

    assert generator.protocol == "fujitsu_ac"
    assert generator.protocol_def is not None


def test_generator_invalid_protocol():
    """Test that invalid protocol raises ValueError."""
    with pytest.raises(ValueError, match="Unsupported protocol"):
        HVACCodeGenerator("nonexistent_ac")


def test_generate_single_command():
    """Test generating a single HVAC command."""
    generator = HVACCodeGenerator("fujitsu_ac")
    code = generator.generate_code(power="on", mode="cool", temperature=24, fan="auto")

    # Should return a Base64 string
    assert isinstance(code, str)
    assert len(code) > 0

    # Should be decodable
    timings = decode_tuya_ir(code)
    assert len(timings) > 0


def test_generate_command_function():
    """Test convenience function for generating commands."""
    code = generate_command("fujitsu_ac", mode="heat", temperature=22, fan="low")

    assert isinstance(code, str)
    assert len(code) > 0


def test_generate_invalid_mode():
    """Test that invalid mode raises ValueError."""
    generator = HVACCodeGenerator("fujitsu_ac")

    with pytest.raises(ValueError, match="Invalid mode"):
        generator.generate_code(mode="invalid_mode")


def test_generate_invalid_temperature():
    """Test that out-of-range temperature raises ValueError."""
    generator = HVACCodeGenerator("fujitsu_ac")

    # Too low
    with pytest.raises(ValueError, match="Temperature .* out of range"):
        generator.generate_code(temperature=10)

    # Too high
    with pytest.raises(ValueError, match="Temperature .* out of range"):
        generator.generate_code(temperature=40)


def test_generate_invalid_fan():
    """Test that invalid fan speed raises ValueError."""
    generator = HVACCodeGenerator("fujitsu_ac")

    with pytest.raises(ValueError, match="Invalid fan speed"):
        generator.generate_code(fan="turbo")  # Not supported for Fujitsu


def test_generate_all_commands():
    """Test generating complete command set."""
    generator = HVACCodeGenerator("fujitsu_ac")
    commands = generator.generate_all_commands(
        modes=["cool", "heat"], temp_range=(20, 22), fan_speeds=["auto", "low"]
    )

    # Should have off command
    assert "off" in commands

    # Should have cool and heat modes
    assert "cool" in commands
    assert "heat" in commands

    # Each mode should have fan speeds
    assert "auto" in commands["cool"]
    assert "low" in commands["cool"]

    # Each fan speed should have temperatures
    assert "20" in commands["cool"]["auto"]
    assert "21" in commands["cool"]["auto"]
    assert "22" in commands["cool"]["auto"]


def test_generate_all_commands_defaults():
    """Test generating commands with default filters."""
    generator = HVACCodeGenerator("fujitsu_ac")
    commands = generator.generate_all_commands()

    # Should generate a substantial number of commands
    assert "off" in commands
    assert len(commands) > 1


def test_different_manufacturers():
    """Test generating commands for different manufacturers."""
    for protocol in ["fujitsu_ac", "daikin", "mitsubishi_ac"]:  # Use actual protocol names
        generator = HVACCodeGenerator(protocol)
        code = generator.generate_code(mode="cool", temperature=24)

        assert isinstance(code, str)
        assert len(code) > 0
