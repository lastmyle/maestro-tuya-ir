# Quick Reference: Known Good Test Codes

## Fujitsu OFF Command (7 bytes)
```
Code: BvQMFwbeAb4gARFdAb4BlQTeAV0B3gGVBL4BXQFAAwHeAUADAZUEQANAD0ADAd4BQAMBlQRAA+ABD0ATAV0BQA/AA0APwAPAE0AHBd4BlQTeAUAHAL4gAQFdAUADAd4B4AMDAZUEQBNAAwHeAYADAb4B4AkTQBsBvgFAAwGVBEALAd4BQAcBlQSADwuVBN4BlQS+AZUE3gE=
Timings: 115
Bytes: 14 63 00 10 10 02 fd
```

## Fujitsu 24C High (16 bytes)
```
Code: B94MQgaoAXQBgAMDrwSoAUABQAfAE0ABQA9AA8ATQAdAD0ADQAtAAUAHQAPgAwFAD8AD4AMBQDfAAUAf4AMBQA/gAx9AAcATQBfgDwNAAcAnQAcFdAHkAXQBQAcAqOAAAUALQAPAQ0ALQAMBrwTgBStAE8ADwBtAAQOvBKgBwBcBdAGAM8ABAXQB4A0DQAHgCRuAOwF0AeABA0ABQA8BqAFAG0ADAagBQAPAAUAL4AcD4AMBwBvAAcCrQAFAC0ADQAHgAwcHdAGoAagBqAE=
Timings: 259
Bytes: 14 63 00 10 10 fe 09 30 81 04 00 00 00 00 20 2b
```

## Test Usage

```python
from app.core.ir_protocols.test_codes import FUJITSU_KNOWN_GOOD_CODES

off_code = FUJITSU_KNOWN_GOOD_CODES['OFF']
high_code = FUJITSU_KNOWN_GOOD_CODES['24C_High']
```

## Files

- **Test codes**: `app/core/ir_protocols/test_codes.py`
- **Test script**: `test_exact_translation.py`
- **Encoder**: `app/core/ir_protocols/ir_send.py`
- **Decoder**: `app/core/ir_protocols/ir_recv.py`
