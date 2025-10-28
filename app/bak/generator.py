"""
HVAC IR code generator.

Generates IR codes for various HVAC manufacturers and protocols.
Note: This is a simplified implementation. For production use with real devices,
integrate with hvac_ir library or IRremoteESP8266.
"""

from typing import Optional

from app.core.protocol_timings import get_protocol_by_name
from app.core.tuya_encoder import encode_tuya_ir

# Import Fujitsu encoders for real protocol support
from app.core.fujitsu_encoder import generate_fujitsu_command as generate_fujitsu_16byte
from app.core.fujitsu_3byte_encoder import generate_fujitsu_3byte_command

class HVACCodeGenerator:
    """Generator for HVAC IR codes."""

    # Simplified timing templates for demo purposes
    # Real implementation would use proper protocol encoders
    TIMING_TEMPLATES = {
        "fujitsu_ac": {
            "header": [9000, 4500],
            "one": [600, 1600],
            "zero": [600, 540],
            "footer": [600],
        },
        "daikin_ac": {
            "header": [3500, 1728],
            "one": [428, 1280],
            "zero": [428, 428],
            "footer": [428],
        },
        "mitsubishi_ac": {
            "header": [3400, 1750],
            "one": [450, 1300],
            "zero": [450, 420],
            "footer": [450],
        },
        "gree_ac": {
            "header": [9000, 4500],
            "one": [620, 1600],
            "zero": [620, 540],
            "footer": [620],
        },
        "carrier_ac": {
            "header": [8960, 4480],
            "one": [600, 1580],
            "zero": [600, 530],
            "footer": [600],
        },
    }

    def __init__(self, protocol: str, detected_variant: str = None):
        """
        Initialize generator for a specific protocol.

        Args:
            protocol: Protocol name (e.g., "fujitsu_ac")
            detected_variant: Optional variant identifier (e.g., "3byte" for Fujitsu)

        Raises:
            ValueError: If protocol is not supported
        """
        self.protocol = protocol
        self.detected_variant = detected_variant
        self.protocol_def = get_protocol_by_name(protocol)
        if not self.protocol_def:
            raise ValueError(f"Unsupported protocol: {protocol}")

        self.template = self.TIMING_TEMPLATES.get(protocol)
        if not self.template:
            # Use generic template based on header
            self.template = {
                "header": list(self.protocol_def.header),
                "one": [600, 1600],
                "zero": [600, 540],
                "footer": [600],
            }

    def generate_code(
        self,
        power: str = "on",
        mode: str = "cool",
        temperature: int = 24,
        fan: str = "auto",
        swing: str = "off",
    ) -> str:
        """
        Generate a single HVAC command in Tuya format.

        Args:
            power: "on" or "off"
            mode: "cool", "heat", "dry", "fan", "auto"
            temperature: Temperature in Celsius (16-30)
            fan: "low", "medium", "high", "auto"
            swing: "on" or "off"

        Returns:
            Tuya Base64 IR code

        Raises:
            ValueError: If parameters are invalid
        """
        self._validate_parameters(power, mode, temperature, fan, swing)

        # Use protocol-specific encoder if available
        if "fujitsu" in self.protocol.lower():
            # Detect which Fujitsu variant to use
            if self.detected_variant == "3byte":
                timings = generate_fujitsu_3byte_command(power, mode, temperature, fan, swing)
            else:
                # Default to 16-byte IRremoteESP8266 format
                timings = generate_fujitsu_16byte(power, mode, temperature, fan, swing)
        else:
            # Fall back to generic encoder
            timings = self._encode_command(power, mode, temperature, fan, swing)

        # Convert to Tuya format
        return encode_tuya_ir(timings)

    def generate_all_commands(
        self,
        modes: Optional[list[str]] = None,
        temp_range: Optional[tuple[int, int]] = None,
        fan_speeds: Optional[list[str]] = None,
    ) -> dict:
        """
        Generate complete command set for all combinations.

        Args:
            modes: List of modes to generate (default: all supported)
            temp_range: (min, max) temperature range (default: full range)
            fan_speeds: List of fan speeds (default: all supported)

        Returns:
            Dictionary structure:
            {
                "off": "Base64Code...",
                "cool": {
                    "auto": {
                        "16": "Base64Code...",
                        "17": "Base64Code...",
                        ...
                    },
                    "low": {...},
                    ...
                },
                "heat": {...},
                ...
            }
        """
        caps = self.protocol_def.capabilities

        # Use defaults if not specified
        if modes is None:
            modes = [m for m in caps["modes"] if m != "auto"]
        if temp_range is None:
            temp_range = (caps["tempRange"]["min"], caps["tempRange"]["max"])
        if fan_speeds is None:
            fan_speeds = caps["fanSpeeds"]

        commands = {}

        # Generate OFF command
        commands["off"] = self.generate_code(power="off", mode="cool", temperature=24)

        # Generate commands for each mode
        for mode in modes:
            commands[mode] = {}

            for fan in fan_speeds:
                commands[mode][fan] = {}

                for temp in range(temp_range[0], temp_range[1] + 1):
                    try:
                        code = self.generate_code(
                            power="on", mode=mode, temperature=temp, fan=fan, swing="off"
                        )
                        commands[mode][fan][str(temp)] = code
                    except ValueError:
                        # Skip invalid combinations
                        continue

        return commands

    def _validate_parameters(self, power: str, mode: str, temperature: int, fan: str, swing: str):
        """Validate command parameters against protocol capabilities."""
        caps = self.protocol_def.capabilities

        if power not in ["on", "off"]:
            raise ValueError(f"Invalid power: {power}")

        if mode not in caps["modes"]:
            raise ValueError(f"Invalid mode: {mode}. Supported: {caps['modes']}")

        temp_min = caps["tempRange"]["min"]
        temp_max = caps["tempRange"]["max"]
        if not (temp_min <= temperature <= temp_max):
            raise ValueError(f"Temperature {temperature} out of range ({temp_min}-{temp_max})")

        if fan not in caps["fanSpeeds"]:
            raise ValueError(f"Invalid fan speed: {fan}. Supported: {caps['fanSpeeds']}")

        if swing not in ["on", "off"]:
            raise ValueError(f"Invalid swing: {swing}")

    def _encode_command(
        self, power: str, mode: str, temperature: int, fan: str, swing: str
    ) -> list[int]:
        """
        Encode HVAC command to IR timings.

        Note: This is a simplified implementation that generates valid-looking
        timing patterns. Real implementation would properly encode the actual
        protocol bit patterns.
        """
        timings = []

        # Add header
        timings.extend(self.template["header"])

        # Create a simple bit pattern based on parameters
        # In real implementation, this would follow the actual protocol specification
        bits = self._create_bit_pattern(power, mode, temperature, fan, swing)

        # Encode bits to timings
        for bit in bits:
            if bit == "1":
                timings.extend(self.template["one"])
            else:
                timings.extend(self.template["zero"])

        # Add footer
        timings.extend(self.template["footer"])

        return timings

    def _create_bit_pattern(
        self, power: str, mode: str, temperature: int, fan: str, swing: str
    ) -> str:
        """
        Create bit pattern for command.

        This is a simplified demonstration. Real protocols have specific
        bit layouts for each parameter.
        """
        # Simplified bit encoding (not accurate to real protocols)
        power_bit = "1" if power == "on" else "0"

        mode_bits = {
            "cool": "000",
            "heat": "001",
            "dry": "010",
            "fan": "011",
            "auto": "100",
        }.get(mode, "000")

        # Encode temperature (simplified)
        temp_bits = format(temperature - 16, "05b")  # 5 bits for temp (16-31)

        fan_bits = {
            "auto": "00",
            "low": "01",
            "medium": "10",
            "high": "11",
            "quiet": "00",
        }.get(fan, "00")

        swing_bit = "1" if swing == "on" else "0"

        # Create a pattern with some repetition for a realistic length
        # Real protocols typically have 48-144 bits
        base_pattern = power_bit + mode_bits + temp_bits + fan_bits + swing_bit
        # Repeat and pad to create realistic length
        pattern = (base_pattern * 8)[:96]  # 96 bits is common for many protocols

        return pattern


def generate_command(
    protocol: str,
    power: str = "on",
    mode: str = "cool",
    temperature: int = 24,
    fan: str = "auto",
    swing: str = "off",
    sample_code: Optional[str] = None,
) -> str:
    """
    Convenience function to generate a single command.

    Args:
        protocol: Protocol name
        power: "on" or "off"
        mode: HVAC mode
        temperature: Temperature in Celsius
        fan: Fan speed
        swing: Swing setting
        sample_code: Optional sample Tuya code for variant detection (Fujitsu only)

    Returns:
        Tuya Base64 IR code
    """
    # Detect variant from sample code if provided (Fujitsu only)
    detected_variant = None
    if sample_code and "fujitsu" in protocol.lower():
        from app.core.fujitsu_variant_detector import detect_fujitsu_variant
        detected_variant = detect_fujitsu_variant(sample_code)

    generator = HVACCodeGenerator(protocol, detected_variant=detected_variant)
    return generator.generate_code(power, mode, temperature, fan, swing)
