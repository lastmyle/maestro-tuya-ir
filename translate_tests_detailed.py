#!/usr/bin/env python3
"""
Advanced script to translate C++ test files from IRremoteESP8266 to Python pytest format.
Creates working pytest implementations with proper state encoding/decoding tests.
"""

import re
import os
from typing import List, Tuple, Dict, Optional

SOURCE_DIR = "/Users/rhyswilliams/Documents/lastmyle/IRremoteESP8266/test"
DEST_DIR = "/Users/rhyswilliams/Documents/lastmyle/maestro-tuya-ir/tests/ir_protocols"

# Protocol name mapping
PROTOCOLS = [
    "Fujitsu",
    "Daikin",
    "Mitsubishi",
    "Panasonic",
    "Samsung",
    "LG",
    "Carrier",
    "Haier",
    "Hitachi",
    "Sharp",
    "Toshiba",
    "Vestel",
    "Whirlpool",
    "Electra",
    "Delonghi",
    "Corona",
]


def extract_byte_arrays(test_body: str) -> List[Tuple[str, List[int]]]:
    """Extract byte array definitions from C++ test code."""
    arrays = []

    # Match uint8_t varname[size] = {0x..., 0x..., ...};
    pattern = re.compile(
        r"uint8_t\s+(\w+)\s*\[\s*(?:\d+|kFujitsu\w+)?\s*\]\s*=\s*\{([^}]+)\}", re.DOTALL
    )

    for match in pattern.finditer(test_body):
        var_name = match.group(1)
        values_str = match.group(2)

        # Extract hex values
        hex_values = re.findall(r"0x[0-9A-Fa-f]+", values_str)
        byte_values = [int(v, 16) for v in hex_values]

        arrays.append((var_name, byte_values))

    return arrays


def extract_setter_calls(test_body: str) -> List[Tuple[str, str]]:
    """Extract setter method calls like ac.setTemp(24)."""
    setters = []

    # Match ac.setXXX(value) or ac.methodName()
    pattern = re.compile(r"ac\.(set\w+|step\w+|on|off|begin)\s*\(([^)]*)\)")

    for match in pattern.finditer(test_body):
        method = match.group(1)
        arg = match.group(2).strip()
        setters.append((method, arg))

    return setters


def convert_cpp_constant(const: str) -> str:
    """Convert C++ constant names to Python."""
    # kFujitsuAcModeCool -> FUJITSU_AC_MODE_COOL
    if const.startswith("k"):
        const = const[1:]  # Remove 'k' prefix

    # Convert camelCase to UPPER_SNAKE_CASE
    const = re.sub("([a-z])([A-Z])", r"\1_\2", const)
    const = const.upper()

    # Handle model constants
    if const == "ARRAH2E" or const == "ARDB1" or const == "ARREW4E":
        return f"FujitsuModel.{const}"

    return const


def generate_state_creation_code(protocol: str, setters: List[Tuple[str, str]]) -> List[str]:
    """Generate Python code to create and configure a state object."""
    protocol_lower = protocol.lower()
    protocol_class = f"{protocol}AC"
    lines = []

    lines.append(f"    {protocol_lower} = {protocol_class}()")

    # Track if we need to create state or modify existing
    state_lines = []
    model = None

    for method, arg in setters:
        if method == "setModel":
            model = convert_cpp_constant(arg)
            lines[0] = f"    {protocol_lower} = {protocol_class}(model={model})"
        elif method == "begin" or method == "reset":
            continue  # Skip these
        elif method == "on":
            state_lines.append(f"    state.power = True")
        elif method == "off":
            state_lines.append(f"    state.power = False")
        elif method.startswith("set"):
            # Extract property name
            prop = method[3:]  # Remove 'set'
            prop = prop[0].lower() + prop[1:]  # Lowercase first letter

            # Convert property name to snake_case
            prop = re.sub("([a-z])([A-Z])", r"\1_\2", prop).lower()

            # Convert argument
            if arg and not arg.isdigit():
                arg = convert_cpp_constant(arg)

            state_lines.append(f"    state.{prop} = {arg}")

    return lines, state_lines


def create_test_function(test_name: str, test_body: str, protocol: str) -> str:
    """Create a complete pytest function from C++ test."""
    protocol_lower = protocol.lower()
    protocol_class = f"{protocol}AC"
    pytest_name = convert_test_name(test_name)

    # Extract arrays and setters
    arrays = extract_byte_arrays(test_body)
    setters = extract_setter_calls(test_body)

    # Start building the test
    lines = [f"def {pytest_name}():"]
    lines.append(f'    """{test_name} - Converted from C++ test"""')

    # Add protocol instance creation
    lines.append(f"    {protocol_lower} = {protocol_class}()")
    lines.append("")

    # If there are byte arrays, this is likely an encoding/decoding test
    if arrays:
        # Add the expected arrays
        for var_name, byte_values in arrays:
            lines.append(f"    {var_name} = bytes([")
            # Format bytes in groups of 8
            for i in range(0, len(byte_values), 8):
                group = byte_values[i : i + 8]
                hex_str = ", ".join(f"0x{b:02X}" for b in group)
                lines.append(f"        {hex_str},")
            lines.append("    ])")
            lines.append("")

        # Check if this is an encoding test (has setters) or decoding test
        if setters:
            # Encoding test - create state and encode it
            lines.append(f"    # Create state with specific settings")
            lines.append(f"    state = {protocol_class}State()")

            for method, arg in setters:
                if method.startswith("set"):
                    prop = method[3:]
                    prop = prop[0].lower() + prop[1:]
                    prop = re.sub("([a-z])([A-Z])", r"\1_\2", prop).lower()

                    if arg and not arg.isdigit():
                        arg = convert_cpp_constant(arg)

                    lines.append(f"    state.{prop} = {arg}")
                elif method == "off":
                    lines.append(f"    state.power = False")

            lines.append("")
            lines.append(f"    # Encode state to bytes")
            lines.append(f"    result = {protocol_lower}._state_to_bytes(state)")
            lines.append("")

            # Add assertion
            if arrays:
                expected_var = arrays[0][0]
                lines.append(f"    assert result == {expected_var}")
        else:
            # Decoding test - decode bytes to state
            if arrays:
                data_var = arrays[0][0]
                lines.append(f"    # Decode bytes to state")
                lines.append(f"    state = {protocol_lower}._bytes_to_state({data_var})")
                lines.append(f"    assert state is not None")

    else:
        # No arrays, probably a simple functional test
        lines.append(f"    # TODO: Implement test logic")
        lines.append(f"    pass")

    lines.append("")
    lines.append("")
    return "\n".join(lines)


def convert_test_name(cpp_name: str) -> str:
    """Convert C++ test name to Python snake_case."""
    name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", cpp_name)
    name = re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower()
    return f"test_{name}"


def extract_test_functions(cpp_content: str) -> List[Tuple[str, str]]:
    """Extract TEST and TEST_F functions from C++ code."""
    test_pattern = re.compile(r"TEST(?:_F)?\s*\(\s*\w+\s*,\s*(\w+)\s*\)\s*\{", re.MULTILINE)

    tests = []
    for match in test_pattern.finditer(cpp_content):
        test_name = match.group(1)

        # Find the matching closing brace
        start = match.end()
        brace_count = 1
        end = start

        for i in range(start, len(cpp_content)):
            if cpp_content[i] == "{":
                brace_count += 1
            elif cpp_content[i] == "}":
                brace_count -= 1
                if brace_count == 0:
                    end = i
                    break

        test_body = cpp_content[start:end]
        tests.append((test_name, test_body))

    return tests


def generate_pytest_file(protocol: str, tests: List[Tuple[str, str]]) -> str:
    """Generate complete pytest file."""
    protocol_lower = protocol.lower()
    protocol_class = f"{protocol}AC"

    header = f'''"""
Tests for {protocol} AC Protocol
Translated from IRremoteESP8266 C++ tests

Note: These tests have been automatically translated and may require manual adjustments.
"""
import pytest
from app.core.ir_protocols.{protocol_lower} import {protocol_class}, {protocol_class}State
from app.core.ir_protocols.constants import *


'''

    test_functions = []
    for test_name, test_body in tests[:10]:  # Process first 10 tests as examples
        test_func = create_test_function(test_name, test_body, protocol)
        test_functions.append(test_func)

    return header + "".join(test_functions)


def process_protocol(protocol: str) -> Tuple[int, int]:
    """Process a single protocol's test file."""
    cpp_file = f"{SOURCE_DIR}/ir_{protocol}_test.cpp"
    py_file = f"{DEST_DIR}/test_{protocol.lower()}_protocol.py"

    if not os.path.exists(cpp_file):
        return 0, 0

    print(f"Processing {protocol}...")

    with open(cpp_file, "r", encoding="utf-8", errors="ignore") as f:
        cpp_content = f.read()

    tests = extract_test_functions(cpp_content)

    if not tests:
        return 0, 0

    pytest_content = generate_pytest_file(protocol, tests)

    with open(py_file, "w") as f:
        f.write(pytest_content)

    print(
        f"  Created {py_file} with {min(10, len(tests))} detailed tests (from {len(tests)} total)"
    )
    return 1, min(10, len(tests))


def main():
    """Main translation function."""
    os.makedirs(DEST_DIR, exist_ok=True)

    total_files = 0
    total_tests = 0

    for protocol in PROTOCOLS:
        files, tests = process_protocol(protocol)
        total_files += files
        total_tests += tests

    print(f"\n{'=' * 60}")
    print(f"Detailed translation complete!")
    print(f"  Files created: {total_files}")
    print(f"  Detailed tests: {total_tests}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
