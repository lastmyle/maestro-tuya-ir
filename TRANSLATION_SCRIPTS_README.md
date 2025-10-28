# IRremoteESP8266 Translation Structure

## Overview

This document describes the EXACT 1:1 translations from IRremoteESP8266 C++ library to Python with NO optimizations applied. The Python file structure matches the C++ namespace structure.

## File Structure

### C++ Source → Python Translation

```
IRremoteESP8266/src/                          maestro-tuya-ir/app/core/ir_protocols/
├── IRsend.cpp              →                 ├── ir_send.py
│   ├── sendData()                            │   ├── sendData()
│   └── sendGeneric()                         │   └── sendGeneric()
├── IRrecv.cpp              →                 ├── ir_recv.py
│   ├── matchMark()                           │   ├── matchMark()
│   ├── matchSpace()                          │   ├── matchSpace()
│   ├── matchData()                           │   ├── matchData()
│   ├── matchBytes()                          │   ├── matchBytes()
│   └── _matchGeneric()                       │   └── matchGeneric()
└── ir_Fujitsu.cpp          →                 └── fujitsu.py
    ├── IRFujitsuAC class                         ├── IRFujitsuAC class
    ├── Constants                                 ├── Constants
    └── Protocol logic                            └── Protocol logic
```

## Files Created

### `ir_send.py` (IRsend.cpp translations)
- `sendData()` - Lines 248-279
- `sendGeneric()` - Lines 248-272
- `bytes_to_timings()` - Fujitsu wrapper

### `ir_recv.py` (IRrecv.cpp translations)
- `matchMark()` / `matchSpace()` - Tolerance matching
- `matchData()` - Lines 1457-1499
- `matchBytes()` - Lines 1518-1538
- `matchGeneric()` - Lines 1570-1645
- `timings_to_bytes()` - Fujitsu wrapper

### `fujitsu.py` (ir_Fujitsu.cpp translation)
- Complete IRFujitsuAC class (36KB)
- All protocol constants
- Checksum calculation

## Usage

Encoding:
```python
from app.core.ir_protocols.ir_send import bytes_to_timings
from app.core.tuya_encoder import encode_ir

bytes_array = [0x14, 0x63, 0x00, 0x10, 0x10, 0x02, 0xfd]
timings = bytes_to_timings(bytes_array)
tuya_code = encode_ir(timings)
```

Decoding:
```python
from app.core.ir_protocols.ir_recv import timings_to_bytes
from app.core.tuya_encoder import decode_ir

timings = decode_ir(tuya_code)
bytes_array = timings_to_bytes(timings)
```

## Test Results

Both OFF (7 bytes) and 24C_High (16 bytes) pass round-trip tests:
```
✓ ALL TESTS PASSED - EXACT translations work correctly!
```

Run tests: `python test_exact_translation.py`
