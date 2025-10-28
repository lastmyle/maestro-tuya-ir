# IR Protocol Support

This project now includes Python implementations of IR protocols translated from the IRremoteESP8266 C++ library. This allows you to work with structured AC state objects instead of raw timing data.

## Overview

The IR protocol system provides:

1. **Protocol Decoders**: Convert raw IR timings into structured state objects
2. **Protocol Encoders**: Convert structured state objects back into raw IR timings
3. **Tuya Integration**: Seamless integration with Tuya IR blaster encoding/decoding

## Current Protocol Support

### Fujitsu AC (`FujitsuAC`)

Full support for Fujitsu AC units with the following models:
- ARRAH2E (default)
- ARDB1
- ARREB1E
- ARJW2
- ARRY4
- ARREW4E

**State Properties:**
- `power`: On/Off
- `mode`: Auto, Cool, Dry, Fan, Heat
- `temp_celsius`: Temperature in Celsius (16-30°C)
- `fan`: Auto, High, Medium, Low, Quiet
- `swing`: Off, Vertical, Horizontal, Both
- `clean`: Clean mode
- `filter`: Filter indicator
- `outside_quiet`: Outdoor quiet mode
- `timer_type`: Timer configuration
- `on_timer`: On timer in minutes
- `off_timer`: Off timer in minutes

## Usage

### Decoding a Tuya Code to State

```python
from app.core.tuya_encoder import decode_ir
from app.core.ir_protocols import FujitsuAC
from app.core.ir_protocols.constants import FujitsuModel

# Initialize protocol handler
protocol = FujitsuAC(model=FujitsuModel.ARRAH2E)

# Decode Tuya code to timings
tuya_code = "BvQMFwbeAb4gARFdAb4BlQTeAV0B3gGVBL4BXQFAAwHeAUADAZUEQANAD0ADAd4BQAMBlQRAA+ABD0ATAV0BQA/AA0APwAPAE0AHBd4BlQTeAUAHAL4gAQFdAUADAd4B4AMDAZUEQBNAAwHeAYADAb4B4AkTQBsBvgFAAwGVBEALAd4BQAcBlQSADwuVBN4BlQS+AZUE3gE="
timings = decode_ir(tuya_code)

# Decode timings to state
state = protocol.decode_timings(timings)

# Access state properties
print(state)  # Fujitsu AC (ARRAH2E): Power: On, Mode: Cool, Temp: 24.0°C, Fan: High, Swing: Both
print(f"Temperature: {state.temp_celsius}°C")
print(f"Mode: {state.mode}")
print(f"Fan: {state.fan}")
```

### Creating and Encoding a Custom State

```python
from app.core.tuya_encoder import encode_ir
from app.core.ir_protocols import FujitsuAC
from app.core.ir_protocols.fujitsu import FujitsuACState
from app.core.ir_protocols.constants import (
    FujitsuModel,
    FUJITSU_AC_MODE_COOL,
    FUJITSU_AC_FAN_AUTO,
    FUJITSU_AC_SWING_OFF,
    FUJITSU_AC_CMD_TURN_ON
)

# Create a custom state
state = FujitsuACState(
    power=True,
    mode=FUJITSU_AC_MODE_COOL,
    temp_celsius=22.0,
    fan=FUJITSU_AC_FAN_AUTO,
    swing=FUJITSU_AC_SWING_OFF,
    cmd=FUJITSU_AC_CMD_TURN_ON,
    model=FujitsuModel.ARRAH2E
)

# Encode to timings
protocol = FujitsuAC(model=FujitsuModel.ARRAH2E)
timings = protocol.encode_timings(state)

# Encode to Tuya code
tuya_code = encode_ir(timings)
print(f"Tuya code: {tuya_code}")
# Send this code to your Tuya IR blaster!
```

### Modifying an Existing Code

```python
from app.core.tuya_encoder import decode_ir, encode_ir
from app.core.ir_protocols import FujitsuAC

protocol = FujitsuAC()

# Decode existing code
original_code = "BvQMFwbeAb4gARFdAb4BlQTeAV0B3gGVBL4BXQFAAwHeAUADAZUEQANAD0ADAd4BQAMBlQRAA+ABD0ATAV0BQA/AA0APwAPAE0AHBd4BlQTeAUAHAL4gAQFdAUADAd4B4AMDAZUEQBNAAwHeAYADAb4B4AkTQBsBvgFAAwGVBEALAd4BQAcBlQSADwuVBN4BlQS+AZUE3gE="
timings = decode_ir(original_code)
state = protocol.decode_timings(timings)

# Modify state
state.temp_celsius = 20.0
state.fan = FUJITSU_AC_FAN_LOW

# Re-encode
new_timings = protocol.encode_timings(state)
new_code = encode_ir(new_timings)
print(f"Modified code: {new_code}")
```

## Centralized Test Codes

All known-good IR codes are now centralized in `app/core/ir_protocols/test_codes.py`:

```python
from app.core.ir_protocols.test_codes import (
    FUJITSU_KNOWN_GOOD_CODES,
    get_test_codes,
    add_test_code,
    list_protocols,
    list_test_codes,
)

# Get test codes for a protocol
fujitsu_codes = get_test_codes("fujitsu")

# List available protocols
protocols = list_protocols()  # ['fujitsu', ...]

# Add new test codes
add_test_code("fujitsu", "HEAT_25C", "base64_encoded_code...")

# List test codes for a protocol
codes = list_test_codes("fujitsu")  # ['OFF', '24C_High', ...]
```

### Adding Test Codes

When you capture a new IR code from a device, add it to `test_codes.py`:

```python
# In test_codes.py
FUJITSU_KNOWN_GOOD_CODES = {
    "OFF": "BvQMFwbeAb4...",
    "24C_High": "EfcMNAbRAY...",
    "HEAT_25C": "your_new_code_here...",  # Add new code
}
```

## Running Tests

```bash
# Run IR protocol tests
uv run pytest tests/test_ir_protocol_roundtrip.py -v

# Run with verbose output to see generated codes
uv run pytest tests/test_ir_protocol_roundtrip.py::test_fujitsu_decode_from_tuya -v -s

# Run Tuya encoder roundtrip tests
uv run pytest tests/test_tuya_encoder_roundtrip.py -v
```

## Test Results

The test suite validates:
1. **Decode → State → Encode → Tuya Roundtrip**: Successfully decodes Tuya codes, extracts state, and generates new Tuya codes
2. **Manual State Creation**: Creates custom states and encodes them to Tuya codes
3. **Roundtrip Validation**: Ensures encoded codes can be decoded back to identical states

Example test output:
```
============================================================
Testing: OFF
============================================================

[1] Decoded 115 timing values from Tuya code
[2] ✓ Decoded to Fujitsu state:
    Fujitsu AC (ARRAH2E): Power: On, Mode: Cool, Temp: 24.0°C, Fan: High, Swing: Both
[3] ✓ Encoded state to 115 timing values
[4] ✓ Encoded timings to Tuya code

New Tuya code (for manual testing):
B/wMJgbAAYYBgAMBngTgBQfgAxfgGxPgHwPgFzfgCx/gEzPgA6/gB6tAow==
```

## Architecture

```
┌─────────────────┐
│   Tuya Code     │  Base64 encoded, compressed
└────────┬────────┘
         │ decode_ir()
         ▼
┌─────────────────┐
│  Raw Timings    │  List of microsecond durations
└────────┬────────┘
         │ protocol.decode_timings()
         ▼
┌─────────────────┐
│  State Object   │  Structured data (temp, mode, fan, etc)
│  (FujitsuACState)│
└────────┬────────┘
         │ protocol.encode_timings()
         ▼
┌─────────────────┐
│  Raw Timings    │  List of microsecond durations
└────────┬────────┘
         │ encode_ir()
         ▼
┌─────────────────┐
│   Tuya Code     │  Base64 encoded, compressed
└─────────────────┘
```

## File Structure

```
app/core/ir_protocols/
├── __init__.py          # Package exports
├── constants.py         # Protocol constants and enums
├── utils.py            # Utility functions for timing encoding/decoding
├── test_codes.py       # Centralized known-good test codes
├── fujitsu.py          # Fujitsu AC protocol implementation
└── test_codes_example.py  # Example of using test codes

tests/
├── test_ir_protocol_roundtrip.py  # Roundtrip tests
└── test_tuya_encoder_roundtrip.py # Tuya encoder tests
```

## Constants Reference

### Fujitsu AC Modes
- `FUJITSU_AC_MODE_AUTO` = 0x0
- `FUJITSU_AC_MODE_COOL` = 0x1
- `FUJITSU_AC_MODE_DRY` = 0x2
- `FUJITSU_AC_MODE_FAN` = 0x3
- `FUJITSU_AC_MODE_HEAT` = 0x4

### Fujitsu AC Fan Speeds
- `FUJITSU_AC_FAN_AUTO` = 0x0
- `FUJITSU_AC_FAN_HIGH` = 0x1
- `FUJITSU_AC_FAN_MED` = 0x2
- `FUJITSU_AC_FAN_LOW` = 0x3
- `FUJITSU_AC_FAN_QUIET` = 0x4

### Fujitsu AC Swing Modes
- `FUJITSU_AC_SWING_OFF` = 0x0
- `FUJITSU_AC_SWING_VERT` = 0x1
- `FUJITSU_AC_SWING_HORIZ` = 0x2
- `FUJITSU_AC_SWING_BOTH` = 0x3

### Fujitsu AC Commands
- `FUJITSU_AC_CMD_STAY_ON` = 0x00
- `FUJITSU_AC_CMD_TURN_ON` = 0x01
- `FUJITSU_AC_CMD_TURN_OFF` = 0x02
- `FUJITSU_AC_CMD_ECONO` = 0x09
- `FUJITSU_AC_CMD_POWERFUL` = 0x39
- `FUJITSU_AC_CMD_STEP_VERT` = 0x6C
- `FUJITSU_AC_CMD_TOGGLE_SWING_VERT` = 0x6D
- `FUJITSU_AC_CMD_STEP_HORIZ` = 0x79
- `FUJITSU_AC_CMD_TOGGLE_SWING_HORIZ` = 0x7A

## Adding More Protocols

To add support for additional AC protocols:

1. Study the IRremoteESP8266 source for the protocol (e.g., `ir_Daikin.cpp`)
2. Create a new Python file in `app/core/ir_protocols/` (e.g., `daikin.py`)
3. Add constants to `constants.py`
4. Implement the protocol class following the `FujitsuAC` pattern:
   - `decode_timings(timings: List[int]) -> StateObject`
   - `encode_timings(state: StateObject) -> List[int]`
5. Add tests to `tests/test_ir_protocol_roundtrip.py`
6. Export the new protocol in `__init__.py`

## Source

The IR protocol implementations are translated from the excellent [IRremoteESP8266](https://github.com/crankyoldgit/IRremoteESP8266) library.

## Next Steps

Potential future enhancements:
- Add more AC protocols (Daikin, Mitsubishi, LG, etc.)
- Add TV/Receiver protocols
- Add protocol auto-detection
- Add validation and error handling for invalid states
- Add temperature unit conversion helpers
