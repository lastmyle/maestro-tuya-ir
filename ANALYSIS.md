# Fujitsu AC Protocol Analysis - User's Working Codes

## OFF Command (7 bytes)
```
14 63 00 10 10 02 FD
```

## ON Command (Auto 20°C High Vertical) - 15.625 bytes
```
14 63 00 10 10 FE 09 30 41 00 11 40 18 16 01 [+5 bits: 00000]
```

## Byte-by-Byte Analysis

### Common Header (Bytes 0-4)
- **Byte 0**: `0x14` = Header/Signature
- **Byte 1**: `0x63` = Header/Model ID
- **Byte 2**: `0x00` = ?
- **Byte 3**: `0x10` = ?
- **Byte 4**: `0x10` = ?

### OFF Command (Bytes 5-6)
- **Byte 5**: `0x02` = OFF marker
- **Byte 6**: `0xFD` = Checksum

### ON Command (Bytes 5-15+)
- **Byte 5**: `0xFE` = ON marker (vs 0x02 for OFF)
- **Byte 6**: `0x09` = ? (vs 0x30 in my generated code)
- **Byte 7**: `0x30` = ? (was 0x41 in my code - this is temp byte!)
- **Byte 8**: `0x41` = ?
  - Binary: `01000001`
  - Bit 0 = 1 (Power ON)
  - Bits 2-7 = 16 → (16/4 + 16) = 20°C ❌ Wrong!

Wait, let me recalculate using IRremoteESP8266 formula:
- Byte 8 = 0x41 = 01000001
- Bits 2-7 = 010000 (binary) = 16 (decimal)
- Temperature = 16 / 4 + 16 = 4 + 16 = 20°C ✅

- **Byte 9**: `0x00` = Mode? (bits 0-2 = 000 = Auto)
- **Byte 10**: `0x11` = Fan/Swing?
  - Binary: `00010001`
  - Bits 0-2 = 001 = ?
  - Bits 4-5 = 01 = ?
- **Byte 11**: `0x40` = ?
- **Byte 12**: `0x18` = ?
- **Byte 13**: `0x16` = ?
- **Byte 14**: `0x01` = ?
- **Partial Byte 15**: `00000` (5 bits only)

## Comparison with IRremoteESP8266 Structure

Standard Fujitsu 16-byte command:
```
[0][1][2][3][4][5][6][7][8][9][10][11][12][13][14][15]
                          ^   ^    ^
                          |   |    |
                        Temp Mode Fan
```

But user's code has:
- Only 15 complete bytes + 5 bits
- Different structure than IRremoteESP8266

## Hypothesis

The user's Hubitat device learned a **variant** of the Fujitsu protocol that:
1. Uses different byte positions for temperature/mode/fan
2. May use 15-byte commands instead of 16-byte
3. Has a different checksum formula
4. Uses byte 5 as ON/OFF marker (0xFE=ON, 0x02=OFF)

## Next Steps

1. Need to decode the actual protocol from the working codes
2. Map which bytes control what functions
3. Generate new codes using the correct structure
4. Test on hardware
