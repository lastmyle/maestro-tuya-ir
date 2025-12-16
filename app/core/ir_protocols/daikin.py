# Copyright 2016 sillyfrog
# Copyright 2017 sillyfrog, crankyoldgit
# Copyright 2018-2022 crankyoldgit
# Copyright 2019 pasna (IRDaikin160 class / Daikin176 class)
# Python translation: Direct conversion from C++ with NO optimizations

## @file
## @brief Support for Daikin A/C protocols.
## Direct translation from IRremoteESP8266 ir_Daikin.cpp and ir_Daikin.h
## @see Daikin http://harizanov.com/2012/02/control-daikin-air-conditioner-over-the-internet/
## @see Daikin https://github.com/mharizanov/Daikin-AC-remote-control-over-the-Internet/tree/master/IRremote
## @see Daikin http://rdlab.cdmt.vn/project-2013/daikin-ir-protocol
## @see Daikin https://github.com/blafois/Daikin-IR-Reverse
## @see Daikin128 https://github.com/crankyoldgit/IRremoteESP8266/issues/827
## @see Daikin152 https://github.com/crankyoldgit/IRremoteESP8266/issues/873
## @see Daikin160 https://github.com/crankyoldgit/IRremoteESP8266/issues/731
## @see Daikin2 https://github.com/crankyoldgit/IRremoteESP8266/issues/582
## @see Daikin216 https://github.com/crankyoldgit/IRremoteESP8266/issues/689
## @see Daikin64 https://github.com/crankyoldgit/IRremoteESP8266/issues/1064
## @see Daikin200 https://github.com/crankyoldgit/IRremoteESP8266/issues/1802
## @see Daikin312 https://github.com/crankyoldgit/IRremoteESP8266/issues/1829

from typing import List, Optional

# =============================================================================
# STATE LENGTH CONSTANTS (from IRremoteESP8266.h)
# =============================================================================
kDaikinStateLength = 35
kDaikinBits = kDaikinStateLength * 8
kDaikinStateLengthShort = kDaikinStateLength - 8  # 27
kDaikinBitsShort = kDaikinStateLengthShort * 8
kDaikin2StateLength = 39
kDaikin2Bits = kDaikin2StateLength * 8
kDaikin160StateLength = 20
kDaikin160Bits = kDaikin160StateLength * 8
kDaikin128StateLength = 16
kDaikin128Bits = kDaikin128StateLength * 8
kDaikin152StateLength = 19
kDaikin152Bits = kDaikin152StateLength * 8
kDaikin176StateLength = 22
kDaikin176Bits = kDaikin176StateLength * 8
kDaikin200StateLength = 25
kDaikin200Bits = kDaikin200StateLength * 8
kDaikin216StateLength = 27
kDaikin216Bits = kDaikin216StateLength * 8
kDaikin312StateLength = 39
kDaikin312Bits = kDaikin312StateLength * 8
kDaikin64Bits = 64

# =============================================================================
# DAIKIN (Original 280-bit) CONSTANTS
# =============================================================================
kDaikinAuto = 0b000  # temp 25
kDaikinDry = 0b010  # temp 0xc0 = 96 degrees c
kDaikinCool = 0b011
kDaikinHeat = 0b100  # temp 23
kDaikinFan = 0b110  # temp not shown, but 25
kDaikinMinTemp = 10  # Celsius
kDaikinMaxTemp = 32  # Celsius
kDaikinFanMin = 1
kDaikinFanMed = 3
kDaikinFanMax = 5
kDaikinFanAuto = 0b1010  # 10 / 0xA
kDaikinFanQuiet = 0b1011  # 11 / 0xB
kDaikinSwingOn = 0b1111
kDaikinSwingOff = 0b0000
kDaikinHeaderLength = 5
kDaikinSections = 3
kDaikinSection1Length = 8
kDaikinSection2Length = 8
kDaikinSection3Length = kDaikinStateLength - kDaikinSection1Length - kDaikinSection2Length
kDaikinByteChecksum1 = 7
kDaikinByteChecksum2 = 15
kDaikinUnusedTime = 0x600
kDaikinBeepQuiet = 1
kDaikinBeepLoud = 2
kDaikinBeepOff = 3
kDaikinLightBright = 1
kDaikinLightDim = 2
kDaikinLightOff = 3
kDaikinCurBit = kDaikinStateLength
kDaikinCurIndex = kDaikinStateLength + 1
kDaikinTolerance = 35
kDaikinMarkExcess = 50  # Typical kMarkExcess value
kDaikinHdrMark = 3650  # kDaikinBitMark * 8
kDaikinHdrSpace = 1623  # kDaikinBitMark * 4
kDaikinBitMark = 428
kDaikinZeroSpace = 428
kDaikinOneSpace = 1280
kDaikinGap = 29000
# Note bits in each octet swapped so can be sent as a single value
kDaikinFirstHeader64 = 0b1101011100000000000000001100010100000000001001111101101000010001

# =============================================================================
# DAIKIN2 (312-bit) CONSTANTS
# =============================================================================
kDaikin2Freq = 36700  # Modulation Frequency in Hz.
kDaikin2LeaderMark = 10024
kDaikin2LeaderSpace = 25180
kDaikin2Gap = kDaikin2LeaderMark + kDaikin2LeaderSpace
kDaikin2HdrMark = 3500
kDaikin2HdrSpace = 1728
kDaikin2BitMark = 460
kDaikin2OneSpace = 1270
kDaikin2ZeroSpace = 420
kDaikin2Sections = 2
kDaikin2Section1Length = 20
kDaikin2Section2Length = 19
kDaikin2Tolerance = 5  # Extra percentage tolerance

kDaikin2SwingVHighest = 0x1
kDaikin2SwingVHigh = 0x2
kDaikin2SwingVUpperMiddle = 0x3
kDaikin2SwingVLowerMiddle = 0x4
kDaikin2SwingVLow = 0x5
kDaikin2SwingVLowest = 0x6
kDaikin2SwingVBreeze = 0xC
kDaikin2SwingVCirculate = 0xD
kDaikin2SwingVOff = 0xE
kDaikin2SwingVAuto = 0xF  # A.k.a "Swing"
kDaikin2SwingVSwing = kDaikin2SwingVAuto

kDaikin2SwingHWide = 0xA3
kDaikin2SwingHLeftMax = 0xA8
kDaikin2SwingHLeft = 0xA9
kDaikin2SwingHMiddle = 0xAA
kDaikin2SwingHRight = 0xAB
kDaikin2SwingHRightMax = 0xAC
kDaikin2SwingHAuto = 0xBE  # A.k.a "Swing"
kDaikin2SwingHOff = 0xBF
kDaikin2SwingHSwing = kDaikin2SwingHAuto

kDaikin2HumidityOff = 0x00
kDaikin2HumidityHeatLow = 0x28  # Humidify (Heat) only (40%?)
kDaikin2HumidityHeatMedium = 0x2D  # Humidify (Heat) only (45%?)
kDaikin2HumidityHeatHigh = 0x32  # Humidify (Heat) only (50%?)
kDaikin2HumidityDryLow = 0x32  # Dry only (50%?)
kDaikin2HumidityDryMedium = 0x37  # Dry only (55%?)
kDaikin2HumidityDryHigh = 0x3C  # Dry only (60%?)
kDaikin2HumidityAuto = 0xFF

kDaikin2MinCoolTemp = 18  # Min temp (in C) when in Cool mode.

# =============================================================================
# DAIKIN216 (216-bit) CONSTANTS
# =============================================================================
kDaikin216Freq = 38000  # Modulation Frequency in Hz.
kDaikin216HdrMark = 3440
kDaikin216HdrSpace = 1750
kDaikin216BitMark = 420
kDaikin216OneSpace = 1300
kDaikin216ZeroSpace = 450
kDaikin216Gap = 29650
kDaikin216Sections = 2
kDaikin216Section1Length = 8
kDaikin216Section2Length = kDaikin216StateLength - kDaikin216Section1Length
kDaikin216SwingOn = 0b1111
kDaikin216SwingOff = 0b0000

# =============================================================================
# DAIKIN160 (160-bit) CONSTANTS
# =============================================================================
kDaikin160Freq = 38000  # Modulation Frequency in Hz.
kDaikin160HdrMark = 5000
kDaikin160HdrSpace = 2145
kDaikin160BitMark = 342
kDaikin160OneSpace = 1786
kDaikin160ZeroSpace = 700
kDaikin160Gap = 29650
kDaikin160Sections = 2
kDaikin160Section1Length = 7
kDaikin160Section2Length = kDaikin160StateLength - kDaikin160Section1Length
kDaikin160SwingVLowest = 0x1
kDaikin160SwingVLow = 0x2
kDaikin160SwingVMiddle = 0x3
kDaikin160SwingVHigh = 0x4
kDaikin160SwingVHighest = 0x5
kDaikin160SwingVAuto = 0xF

# =============================================================================
# DAIKIN176 (176-bit) CONSTANTS
# =============================================================================
kDaikin176Freq = 38000  # Modulation Frequency in Hz.
kDaikin176HdrMark = 5070
kDaikin176HdrSpace = 2140
kDaikin176BitMark = 370
kDaikin176OneSpace = 1780
kDaikin176ZeroSpace = 710
kDaikin176Gap = 29410
kDaikin176Sections = 2
kDaikin176Section1Length = 7
kDaikin176Section2Length = kDaikin176StateLength - kDaikin176Section1Length
kDaikin176Fan = 0b000  # 0
kDaikin176Heat = 0b001  # 1
kDaikin176Cool = 0b010  # 2
kDaikin176Auto = 0b011  # 3
kDaikin176Dry = 0b111  # 7
kDaikin176ModeButton = 0b00000100
kDaikin176DryFanTemp = 17  # Dry/Fan mode is always 17 Celsius.
kDaikin176FanMax = 3
kDaikin176SwingHAuto = 0x5
kDaikin176SwingHOff = 0x6

# =============================================================================
# DAIKIN128 (128-bit) CONSTANTS
# =============================================================================
kDaikin128Freq = 38000  # Modulation Frequency in Hz.
kDaikin128LeaderMark = 9800
kDaikin128LeaderSpace = 9800
kDaikin128HdrMark = 4600
kDaikin128HdrSpace = 2500
kDaikin128BitMark = 350
kDaikin128OneSpace = 954
kDaikin128ZeroSpace = 382
kDaikin128Gap = 20300
kDaikin128FooterMark = kDaikin128HdrMark
kDaikin128Sections = 2
kDaikin128SectionLength = 8
kDaikin128Dry = 0b00000001
kDaikin128Cool = 0b00000010
kDaikin128Fan = 0b00000100
kDaikin128Heat = 0b00001000
kDaikin128Auto = 0b00001010
kDaikin128FanAuto = 0b0001
kDaikin128FanHigh = 0b0010
kDaikin128FanMed = 0b0100
kDaikin128FanLow = 0b1000
kDaikin128FanPowerful = 0b0011
kDaikin128FanQuiet = 0b1001
kDaikin128MinTemp = 16  # C
kDaikin128MaxTemp = 30  # C
kDaikin128BitWall = 0b00001000
kDaikin128BitCeiling = 0b00000001

# =============================================================================
# DAIKIN152 (152-bit) CONSTANTS
# =============================================================================
kDaikin152Freq = 38000  # Modulation Frequency in Hz.
kDaikin152LeaderBits = 5
kDaikin152HdrMark = 3492
kDaikin152HdrSpace = 1718
kDaikin152BitMark = 433
kDaikin152OneSpace = 1529
kDaikin152ZeroSpace = kDaikin152BitMark
kDaikin152Gap = 25182
kDaikin152DryTemp = kDaikin2MinCoolTemp  # Celsius
kDaikin152FanTemp = 0x60  # 96 Celsius

# =============================================================================
# DAIKIN64 (64-bit) CONSTANTS
# =============================================================================
kDaikin64HdrMark = kDaikin128HdrMark
kDaikin64BitMark = kDaikin128BitMark
kDaikin64HdrSpace = kDaikin128HdrSpace
kDaikin64OneSpace = kDaikin128OneSpace
kDaikin64ZeroSpace = kDaikin128ZeroSpace
kDaikin64LdrMark = kDaikin128LeaderMark
kDaikin64Gap = kDaikin128Gap
kDaikin64LdrSpace = kDaikin128LeaderSpace
kDaikin64Freq = kDaikin128Freq  # Hz.
kDaikin64Overhead = 9
kDaikin64ToleranceDelta = 5  # +5%

kDaikin64KnownGoodState = 0x7C16161607204216
kDaikin64Dry = 0b0001
kDaikin64Cool = 0b0010
kDaikin64Fan = 0b0100
kDaikin64Heat = 0b1000
kDaikin64FanAuto = 0b0001
kDaikin64FanLow = 0b1000
kDaikin64FanMed = 0b0100
kDaikin64FanHigh = 0b0010
kDaikin64FanQuiet = 0b1001
kDaikin64FanTurbo = 0b0011
kDaikin64MinTemp = 16  # Celsius
kDaikin64MaxTemp = 30  # Celsius
kDaikin64ChecksumOffset = 60
kDaikin64ChecksumSize = 4  # Mask 0b1111 << 59

# =============================================================================
# DAIKIN200 (200-bit) CONSTANTS
# =============================================================================
kDaikin200Freq = 38000  # Modulation Frequency in Hz.
kDaikin200HdrMark = 4920
kDaikin200HdrSpace = 2230
kDaikin200BitMark = 290
kDaikin200OneSpace = 1850
kDaikin200ZeroSpace = 780
kDaikin200Gap = 29400
kDaikin200Sections = 2
kDaikin200Section1Length = 7
kDaikin200Section2Length = kDaikin200StateLength - kDaikin200Section1Length

# =============================================================================
# DAIKIN312 (312-bit) CONSTANTS
# =============================================================================
kDaikin312HdrMark = 3518
kDaikin312HdrSpace = 1688
kDaikin312BitMark = 453
kDaikin312ZeroSpace = 414
kDaikin312OneSpace = 1275
kDaikin312HdrGap = 25100
kDaikin312SectionGap = 35512
kDaikin312Sections = 2
kDaikin312Section1Length = 20
kDaikin312Section2Length = kDaikin312StateLength - kDaikin312Section1Length


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


## Sum bytes in a state array
## EXACT translation from IRremoteESP8266 sumBytes utility
def sumBytes(start: List[int], length: int, init: int = 0) -> int:
    """
    Sum bytes in a state array.
    EXACT translation from IRremoteESP8266 irutils::sumBytes
    """
    checksum = init
    for i in range(length):
        checksum += start[i]
    return checksum & 0xFF


## Calculate nibble checksum
## EXACT translation from IRremoteESP8266 sumNibbles utility
def sumNibbles(start: List[int], length: int, init: int = 0) -> int:
    """
    Sum nibbles (4-bit values) in a state array.
    EXACT translation from IRremoteESP8266 irutils::sumNibbles
    """
    checksum = init
    for i in range(length):
        checksum += (start[i] >> 4) + (start[i] & 0x0F)
    return checksum & 0xFF


## Set a bit in a byte array
## EXACT translation from IRremoteESP8266 setBit utility
def setBit(data: List[int], position: int, on: bool = True) -> None:
    """
    Set a bit in a byte array.
    EXACT translation from IRremoteESP8266 irutils::setBit
    """
    byte_pos = position // 8
    bit_pos = position % 8
    if on:
        data[byte_pos] |= 1 << bit_pos
    else:
        data[byte_pos] &= ~(1 << bit_pos)


## Set multiple bits in a byte array
## EXACT translation from IRremoteESP8266 setBits utility
def setBits(data: List[int], position: int, length: int, value: int) -> None:
    """
    Set multiple bits in a byte array.
    EXACT translation from IRremoteESP8266 irutils::setBits
    """
    for i in range(length):
        setBit(data, position + i, (value >> i) & 1)


# =============================================================================
# SEND FUNCTIONS
# =============================================================================


## Send a Daikin 280-bit A/C formatted message.
## Status: STABLE
## Direct translation from IRremoteESP8266 IRsend::sendDaikin (ir_Daikin.cpp lines 66-105)
def sendDaikin(data: List[int], nbytes: int, repeat: int = 0) -> List[int]:
    """
    Send a Daikin 280-bit A/C formatted message.
    EXACT translation from IRremoteESP8266 IRsend::sendDaikin

    Returns timing array instead of transmitting via hardware.
    """
    if nbytes < kDaikinStateLengthShort:
        return []  # Not enough bytes to send a proper message.

    # Import here to avoid circular import
    from app.core.ir_protocols.ir_send import sendGeneric

    all_timings = []

    for r in range(repeat + 1):
        offset = 0
        # Send the header, 0b00000
        header_timings = sendGeneric(
            headermark=0,
            headerspace=0,  # No header for the header
            onemark=kDaikinBitMark,
            onespace=kDaikinOneSpace,
            zeromark=kDaikinBitMark,
            zerospace=kDaikinZeroSpace,
            footermark=kDaikinBitMark,
            gap=kDaikinZeroSpace + kDaikinGap,
            data_value=0b00000,
            nbits=kDaikinHeaderLength,
            MSBfirst=False,
        )
        all_timings.extend(header_timings)

        # Data #1
        if nbytes < kDaikinStateLength:  # Are we using the legacy size?
            # Do this as a constant to save RAM and keep in flash memory
            data1_timings = sendGeneric(
                headermark=kDaikinHdrMark,
                headerspace=kDaikinHdrSpace,
                onemark=kDaikinBitMark,
                onespace=kDaikinOneSpace,
                zeromark=kDaikinBitMark,
                zerospace=kDaikinZeroSpace,
                footermark=kDaikinBitMark,
                gap=kDaikinZeroSpace + kDaikinGap,
                data_value=kDaikinFirstHeader64,
                nbits=64,
                MSBfirst=False,
            )
            all_timings.extend(data1_timings)
        else:  # We are using the newer/more correct size.
            data1_timings = sendGeneric(
                headermark=kDaikinHdrMark,
                headerspace=kDaikinHdrSpace,
                onemark=kDaikinBitMark,
                onespace=kDaikinOneSpace,
                zeromark=kDaikinBitMark,
                zerospace=kDaikinZeroSpace,
                footermark=kDaikinBitMark,
                gap=kDaikinZeroSpace + kDaikinGap,
                dataptr=data,
                nbytes=kDaikinSection1Length,
                MSBfirst=False,
            )
            all_timings.extend(data1_timings)
            offset += kDaikinSection1Length

        # Data #2
        data2_timings = sendGeneric(
            headermark=kDaikinHdrMark,
            headerspace=kDaikinHdrSpace,
            onemark=kDaikinBitMark,
            onespace=kDaikinOneSpace,
            zeromark=kDaikinBitMark,
            zerospace=kDaikinZeroSpace,
            footermark=kDaikinBitMark,
            gap=kDaikinZeroSpace + kDaikinGap,
            dataptr=data[offset:],
            nbytes=kDaikinSection2Length,
            MSBfirst=False,
        )
        all_timings.extend(data2_timings)
        offset += kDaikinSection2Length

        # Data #3
        data3_timings = sendGeneric(
            headermark=kDaikinHdrMark,
            headerspace=kDaikinHdrSpace,
            onemark=kDaikinBitMark,
            onespace=kDaikinOneSpace,
            zeromark=kDaikinBitMark,
            zerospace=kDaikinZeroSpace,
            footermark=kDaikinBitMark,
            gap=kDaikinZeroSpace + kDaikinGap,
            dataptr=data[offset:],
            nbytes=nbytes - offset,
            MSBfirst=False,
        )
        all_timings.extend(data3_timings)

    return all_timings


## Send a Daikin2 312-bit A/C formatted message.
## Direct translation from IRremoteESP8266 IRsend::sendDaikin2 (ir_Daikin.cpp lines 671-698)
def sendDaikin2(data: List[int], nbytes: int, repeat: int = 0) -> List[int]:
    """
    Send a Daikin2 312-bit A/C formatted message.
    EXACT translation from IRremoteESP8266 IRsend::sendDaikin2

    Returns timing array instead of transmitting via hardware.
    """
    if nbytes < kDaikin2StateLength:
        return []

    from app.core.ir_protocols.ir_send import sendGeneric

    all_timings = []

    for r in range(repeat + 1):
        # Leader
        all_timings.append(kDaikin2LeaderMark)
        all_timings.append(kDaikin2LeaderSpace)

        # Section #1
        section1_timings = sendGeneric(
            headermark=kDaikin2HdrMark,
            headerspace=kDaikin2HdrSpace,
            onemark=kDaikin2BitMark,
            onespace=kDaikin2OneSpace,
            zeromark=kDaikin2BitMark,
            zerospace=kDaikin2ZeroSpace,
            footermark=kDaikin2BitMark,
            gap=kDaikin2Gap,
            dataptr=data,
            nbytes=kDaikin2Section1Length,
            MSBfirst=False,
        )
        all_timings.extend(section1_timings)

        # Section #2
        section2_timings = sendGeneric(
            headermark=kDaikin2HdrMark,
            headerspace=kDaikin2HdrSpace,
            onemark=kDaikin2BitMark,
            onespace=kDaikin2OneSpace,
            zeromark=kDaikin2BitMark,
            zerospace=kDaikin2ZeroSpace,
            footermark=kDaikin2BitMark,
            gap=kDaikin2Gap,
            dataptr=data[kDaikin2Section1Length:],
            nbytes=kDaikin2Section2Length,
            MSBfirst=False,
        )
        all_timings.extend(section2_timings)

    return all_timings


## Send a Daikin216 216-bit A/C formatted message.
## Direct translation from IRremoteESP8266 IRsend::sendDaikin216 (ir_Daikin.cpp lines 1396-1420)
def sendDaikin216(data: List[int], nbytes: int, repeat: int = 0) -> List[int]:
    """
    Send a Daikin216 216-bit A/C formatted message.
    EXACT translation from IRremoteESP8266 IRsend::sendDaikin216

    Returns timing array instead of transmitting via hardware.
    """
    if nbytes < kDaikin216StateLength:
        return []

    from app.core.ir_protocols.ir_send import sendGeneric

    all_timings = []

    for r in range(repeat + 1):
        # Section #1
        section1_timings = sendGeneric(
            headermark=kDaikin216HdrMark,
            headerspace=kDaikin216HdrSpace,
            onemark=kDaikin216BitMark,
            onespace=kDaikin216OneSpace,
            zeromark=kDaikin216BitMark,
            zerospace=kDaikin216ZeroSpace,
            footermark=kDaikin216BitMark,
            gap=kDaikin216Gap,
            dataptr=data,
            nbytes=kDaikin216Section1Length,
            MSBfirst=False,
        )
        all_timings.extend(section1_timings)

        # Section #2
        section2_timings = sendGeneric(
            headermark=kDaikin216HdrMark,
            headerspace=kDaikin216HdrSpace,
            onemark=kDaikin216BitMark,
            onespace=kDaikin216OneSpace,
            zeromark=kDaikin216BitMark,
            zerospace=kDaikin216ZeroSpace,
            footermark=kDaikin216BitMark,
            gap=kDaikin216Gap,
            dataptr=data[kDaikin216Section1Length:],
            nbytes=kDaikin216Section2Length,
            MSBfirst=False,
        )
        all_timings.extend(section2_timings)

    return all_timings


## Send a Daikin160 160-bit A/C formatted message.
## Direct translation from IRremoteESP8266 IRsend::sendDaikin160 (ir_Daikin.cpp lines 1733-1757)
def sendDaikin160(data: List[int], nbytes: int, repeat: int = 0) -> List[int]:
    """
    Send a Daikin160 160-bit A/C formatted message.
    EXACT translation from IRremoteESP8266 IRsend::sendDaikin160

    Returns timing array instead of transmitting via hardware.
    """
    if nbytes < kDaikin160StateLength:
        return []

    from app.core.ir_protocols.ir_send import sendGeneric

    all_timings = []

    for r in range(repeat + 1):
        # Section #1
        section1_timings = sendGeneric(
            headermark=kDaikin160HdrMark,
            headerspace=kDaikin160HdrSpace,
            onemark=kDaikin160BitMark,
            onespace=kDaikin160OneSpace,
            zeromark=kDaikin160BitMark,
            zerospace=kDaikin160ZeroSpace,
            footermark=kDaikin160BitMark,
            gap=kDaikin160Gap,
            dataptr=data,
            nbytes=kDaikin160Section1Length,
            MSBfirst=False,
        )
        all_timings.extend(section1_timings)

        # Section #2
        section2_timings = sendGeneric(
            headermark=kDaikin160HdrMark,
            headerspace=kDaikin160HdrSpace,
            onemark=kDaikin160BitMark,
            onespace=kDaikin160OneSpace,
            zeromark=kDaikin160BitMark,
            zerospace=kDaikin160ZeroSpace,
            footermark=kDaikin160BitMark,
            gap=kDaikin160Gap,
            dataptr=data[kDaikin160Section1Length:],
            nbytes=kDaikin160Section2Length,
            MSBfirst=False,
        )
        all_timings.extend(section2_timings)

    return all_timings


## Send a Daikin176 176-bit A/C formatted message.
## Direct translation from IRremoteESP8266 IRsend::sendDaikin176 (ir_Daikin.cpp lines 2087-2111)
def sendDaikin176(data: List[int], nbytes: int, repeat: int = 0) -> List[int]:
    """
    Send a Daikin176 176-bit A/C formatted message.
    EXACT translation from IRremoteESP8266 IRsend::sendDaikin176

    Returns timing array instead of transmitting via hardware.
    """
    if nbytes < kDaikin176StateLength:
        return []

    from app.core.ir_protocols.ir_send import sendGeneric

    all_timings = []

    for r in range(repeat + 1):
        # Section #1
        section1_timings = sendGeneric(
            headermark=kDaikin176HdrMark,
            headerspace=kDaikin176HdrSpace,
            onemark=kDaikin176BitMark,
            onespace=kDaikin176OneSpace,
            zeromark=kDaikin176BitMark,
            zerospace=kDaikin176ZeroSpace,
            footermark=kDaikin176BitMark,
            gap=kDaikin176Gap,
            dataptr=data,
            nbytes=kDaikin176Section1Length,
            MSBfirst=False,
        )
        all_timings.extend(section1_timings)

        # Section #2
        section2_timings = sendGeneric(
            headermark=kDaikin176HdrMark,
            headerspace=kDaikin176HdrSpace,
            onemark=kDaikin176BitMark,
            onespace=kDaikin176OneSpace,
            zeromark=kDaikin176BitMark,
            zerospace=kDaikin176ZeroSpace,
            footermark=kDaikin176BitMark,
            gap=kDaikin176Gap,
            dataptr=data[kDaikin176Section1Length:],
            nbytes=kDaikin176Section2Length,
            MSBfirst=False,
        )
        all_timings.extend(section2_timings)

    return all_timings


## Send a Daikin128 128-bit A/C formatted message.
## Direct translation from IRremoteESP8266 IRsend::sendDaikin128 (ir_Daikin.cpp lines 2481-2511)
def sendDaikin128(data: List[int], nbytes: int, repeat: int = 0) -> List[int]:
    """
    Send a Daikin128 128-bit A/C formatted message.
    EXACT translation from IRremoteESP8266 IRsend::sendDaikin128

    Returns timing array instead of transmitting via hardware.
    """
    if nbytes < kDaikin128StateLength:
        return []

    from app.core.ir_protocols.ir_send import sendGeneric

    all_timings = []

    for r in range(repeat + 1):
        # Leader
        all_timings.append(kDaikin128LeaderMark)
        all_timings.append(kDaikin128LeaderSpace)

        # Section #1 (Header + Data)
        section1_timings = sendGeneric(
            headermark=kDaikin128HdrMark,
            headerspace=kDaikin128HdrSpace,
            onemark=kDaikin128BitMark,
            onespace=kDaikin128OneSpace,
            zeromark=kDaikin128BitMark,
            zerospace=kDaikin128ZeroSpace,
            footermark=kDaikin128FooterMark,
            gap=kDaikin128Gap,
            dataptr=data,
            nbytes=kDaikin128SectionLength,
            MSBfirst=False,
        )
        all_timings.extend(section1_timings)

        # Section #2 (Header + Data + Footer)
        section2_timings = sendGeneric(
            headermark=kDaikin128HdrMark,
            headerspace=kDaikin128HdrSpace,
            onemark=kDaikin128BitMark,
            onespace=kDaikin128OneSpace,
            zeromark=kDaikin128BitMark,
            zerospace=kDaikin128ZeroSpace,
            footermark=kDaikin128BitMark,
            gap=kDaikin128Gap,
            dataptr=data[kDaikin128SectionLength:],
            nbytes=kDaikin128SectionLength,
            MSBfirst=False,
        )
        all_timings.extend(section2_timings)

    return all_timings


## Send a Daikin152 152-bit A/C formatted message.
## Direct translation from IRremoteESP8266 IRsend::sendDaikin152 (ir_Daikin.cpp lines 2985-3011)
def sendDaikin152(data: List[int], nbytes: int, repeat: int = 0) -> List[int]:
    """
    Send a Daikin152 152-bit A/C formatted message.
    EXACT translation from IRremoteESP8266 IRsend::sendDaikin152

    Returns timing array instead of transmitting via hardware.
    """
    if nbytes < kDaikin152StateLength:
        return []

    from app.core.ir_protocols.ir_send import sendGeneric

    all_timings = []

    for r in range(repeat + 1):
        # Send the data with special leader
        # Leader bits (5 bits of 0)
        timings = sendGeneric(
            headermark=kDaikin152HdrMark,
            headerspace=kDaikin152HdrSpace,
            onemark=kDaikin152BitMark,
            onespace=kDaikin152OneSpace,
            zeromark=kDaikin152BitMark,
            zerospace=kDaikin152ZeroSpace,
            footermark=0,
            gap=0,
            data_value=0,
            nbits=kDaikin152LeaderBits,
            MSBfirst=False,
        )
        all_timings.extend(timings)

        # Main data
        timings = sendGeneric(
            headermark=0,
            headerspace=0,
            onemark=kDaikin152BitMark,
            onespace=kDaikin152OneSpace,
            zeromark=kDaikin152BitMark,
            zerospace=kDaikin152ZeroSpace,
            footermark=kDaikin152BitMark,
            gap=kDaikin152Gap,
            dataptr=data,
            nbytes=nbytes,
            MSBfirst=False,
        )
        all_timings.extend(timings)

    return all_timings


## Send a Daikin64 64-bit A/C formatted message.
## Direct translation from IRremoteESP8266 IRsend::sendDaikin64 (ir_Daikin.cpp lines 3342-3372)
def sendDaikin64(data: int, nbits: int = kDaikin64Bits, repeat: int = 0) -> List[int]:
    """
    Send a Daikin64 64-bit A/C formatted message.
    EXACT translation from IRremoteESP8266 IRsend::sendDaikin64

    Note: This takes a 64-bit integer, not a byte array.
    Returns timing array instead of transmitting via hardware.
    """
    if nbits != kDaikin64Bits:
        return []

    from app.core.ir_protocols.ir_send import sendGeneric

    all_timings = []

    for r in range(repeat + 1):
        # Leader
        all_timings.append(kDaikin64LdrMark)
        all_timings.append(kDaikin64LdrSpace)

        # Data
        timings = sendGeneric(
            headermark=kDaikin64HdrMark,
            headerspace=kDaikin64HdrSpace,
            onemark=kDaikin64BitMark,
            onespace=kDaikin64OneSpace,
            zeromark=kDaikin64BitMark,
            zerospace=kDaikin64ZeroSpace,
            footermark=kDaikin64BitMark,
            gap=kDaikin64Gap,
            data_value=data,
            nbits=nbits,
            MSBfirst=False,
        )
        all_timings.extend(timings)

    return all_timings


## Send a Daikin200 200-bit A/C formatted message.
## Direct translation from IRremoteESP8266 IRsend::sendDaikin200 (ir_Daikin.cpp lines 3748-3779)
def sendDaikin200(data: List[int], nbytes: int, repeat: int = 0) -> List[int]:
    """
    Send a Daikin200 200-bit A/C formatted message.
    EXACT translation from IRremoteESP8266 IRsend::sendDaikin200

    Returns timing array instead of transmitting via hardware.
    """
    if nbytes < kDaikin200StateLength:
        return []

    from app.core.ir_protocols.ir_send import sendGeneric

    all_timings = []

    for r in range(repeat + 1):
        # Section #1
        section1_timings = sendGeneric(
            headermark=kDaikin200HdrMark,
            headerspace=kDaikin200HdrSpace,
            onemark=kDaikin200BitMark,
            onespace=kDaikin200OneSpace,
            zeromark=kDaikin200BitMark,
            zerospace=kDaikin200ZeroSpace,
            footermark=kDaikin200BitMark,
            gap=kDaikin200Gap,
            dataptr=data,
            nbytes=kDaikin200Section1Length,
            MSBfirst=False,
        )
        all_timings.extend(section1_timings)

        # Section #2
        section2_timings = sendGeneric(
            headermark=kDaikin200HdrMark,
            headerspace=kDaikin200HdrSpace,
            onemark=kDaikin200BitMark,
            onespace=kDaikin200OneSpace,
            zeromark=kDaikin200BitMark,
            zerospace=kDaikin200ZeroSpace,
            footermark=kDaikin200BitMark,
            gap=kDaikin200Gap,
            dataptr=data[kDaikin200Section1Length:],
            nbytes=kDaikin200Section2Length,
            MSBfirst=False,
        )
        all_timings.extend(section2_timings)

    return all_timings


## Send a Daikin312 312-bit A/C formatted message.
## Direct translation from IRremoteESP8266 IRsend::sendDaikin312 (ir_Daikin.cpp lines 3833-3871)
def sendDaikin312(data: List[int], nbytes: int, repeat: int = 0) -> List[int]:
    """
    Send a Daikin312 312-bit A/C formatted message.
    EXACT translation from IRremoteESP8266 IRsend::sendDaikin312

    Returns timing array instead of transmitting via hardware.
    """
    if nbytes < kDaikin312StateLength:
        return []

    from app.core.ir_protocols.ir_send import sendGeneric

    all_timings = []

    for r in range(repeat + 1):
        # Section #1
        section1_timings = sendGeneric(
            headermark=kDaikin312HdrMark,
            headerspace=kDaikin312HdrSpace,
            onemark=kDaikin312BitMark,
            onespace=kDaikin312OneSpace,
            zeromark=kDaikin312BitMark,
            zerospace=kDaikin312ZeroSpace,
            footermark=kDaikin312BitMark,
            gap=kDaikin312HdrGap,
            dataptr=data,
            nbytes=kDaikin312Section1Length,
            MSBfirst=False,
        )
        all_timings.extend(section1_timings)

        # Section #2
        section2_timings = sendGeneric(
            headermark=kDaikin312HdrMark,
            headerspace=kDaikin312HdrSpace,
            onemark=kDaikin312BitMark,
            onespace=kDaikin312OneSpace,
            zeromark=kDaikin312BitMark,
            zerospace=kDaikin312ZeroSpace,
            footermark=kDaikin312BitMark,
            gap=kDaikin312SectionGap,
            dataptr=data[kDaikin312Section1Length:],
            nbytes=kDaikin312Section2Length,
            MSBfirst=False,
        )
        all_timings.extend(section2_timings)

    return all_timings


# =============================================================================
# DECODE FUNCTIONS
# =============================================================================


## Decode a Daikin 280-bit A/C message.
## Direct translation from IRremoteESP8266 IRrecv::decodeDaikin (ir_Daikin.cpp lines 601-668)
def decodeDaikin(results, offset: int = 1, nbits: int = kDaikinBits, strict: bool = True) -> bool:
    """
    Decode a Daikin 280-bit A/C message.
    EXACT translation from IRremoteESP8266 IRrecv::decodeDaikin
    """
    from app.core.ir_protocols.ir_recv import kHeader, kFooter, kMarkExcess, _matchGeneric

    if nbits % 8 != 0:
        return False  # Not a byte multiple

    # Calculate expected length
    nbytes = nbits // 8
    if nbytes < kDaikinStateLengthShort:
        return False

    # Compliance
    if strict:
        if nbits != kDaikinBits and nbits != kDaikinBitsShort:
            return False

    # Header (5 bits, 0b00000)
    used = _matchGeneric(
        data_ptr=results.rawbuf[offset:],
        result_bits_ptr=None,
        result_bytes_ptr=None,
        use_bits=False,
        remaining=results.rawlen - offset,
        nbits=kDaikinHeaderLength,
        hdrmark=0,
        hdrspace=0,
        onemark=kDaikinBitMark,
        onespace=kDaikinOneSpace,
        zeromark=kDaikinBitMark,
        zerospace=kDaikinZeroSpace,
        footermark=kDaikinBitMark,
        footerspace=kDaikinZeroSpace + kDaikinGap,
        atleast=False,
        tolerance=kDaikinTolerance,
        excess=kDaikinMarkExcess,
        MSBfirst=False,
    )
    if used == 0:
        return False
    offset += used

    # Data #1
    if nbytes == kDaikinStateLengthShort:
        # Legacy size - skip the first header
        offset_increment = 2 * 64 + (kHeader + kFooter)
        if offset + offset_increment > results.rawlen:
            return False
        offset += offset_increment
    else:
        # Newer size - decode section 1
        used = _matchGeneric(
            data_ptr=results.rawbuf[offset:],
            result_bits_ptr=None,
            result_bytes_ptr=results.state,
            use_bits=False,
            remaining=results.rawlen - offset,
            nbits=kDaikinSection1Length * 8,
            hdrmark=kDaikinHdrMark,
            hdrspace=kDaikinHdrSpace,
            onemark=kDaikinBitMark,
            onespace=kDaikinOneSpace,
            zeromark=kDaikinBitMark,
            zerospace=kDaikinZeroSpace,
            footermark=kDaikinBitMark,
            footerspace=kDaikinZeroSpace + kDaikinGap,
            atleast=False,
            tolerance=kDaikinTolerance,
            excess=kDaikinMarkExcess,
            MSBfirst=False,
        )
        if used == 0:
            return False
        offset += used

    # Data #2
    data_offset = 0 if nbytes == kDaikinStateLengthShort else kDaikinSection1Length
    used = _matchGeneric(
        data_ptr=results.rawbuf[offset:],
        result_bits_ptr=None,
        result_bytes_ptr=results.state[data_offset:],
        use_bits=False,
        remaining=results.rawlen - offset,
        nbits=kDaikinSection2Length * 8,
        hdrmark=kDaikinHdrMark,
        hdrspace=kDaikinHdrSpace,
        onemark=kDaikinBitMark,
        onespace=kDaikinOneSpace,
        zeromark=kDaikinBitMark,
        zerospace=kDaikinZeroSpace,
        footermark=kDaikinBitMark,
        footerspace=kDaikinZeroSpace + kDaikinGap,
        atleast=False,
        tolerance=kDaikinTolerance,
        excess=kDaikinMarkExcess,
        MSBfirst=False,
    )
    if used == 0:
        return False
    offset += used

    # Data #3
    data_offset += kDaikinSection2Length
    used = _matchGeneric(
        data_ptr=results.rawbuf[offset:],
        result_bits_ptr=None,
        result_bytes_ptr=results.state[data_offset:],
        use_bits=False,
        remaining=results.rawlen - offset,
        nbits=(nbytes - data_offset) * 8,
        hdrmark=kDaikinHdrMark,
        hdrspace=kDaikinHdrSpace,
        onemark=kDaikinBitMark,
        onespace=kDaikinOneSpace,
        zeromark=kDaikinBitMark,
        zerospace=kDaikinZeroSpace,
        footermark=kDaikinBitMark,
        footerspace=kDaikinZeroSpace + kDaikinGap,
        atleast=True,
        tolerance=kDaikinTolerance,
        excess=kDaikinMarkExcess,
        MSBfirst=False,
    )
    if used == 0:
        return False

    # Compliance
    if strict and not validChecksumDaikin(results.state, nbytes):
        return False

    # Success
    results.bits = nbits
    return True


## Decode a Daikin2 312-bit A/C message.
## Direct translation from IRremoteESP8266 IRrecv::decodeDaikin2 (ir_Daikin.cpp lines 1335-1393)
def decodeDaikin2(results, offset: int = 1, nbits: int = kDaikin2Bits, strict: bool = True) -> bool:
    """
    Decode a Daikin2 312-bit A/C message.
    EXACT translation from IRremoteESP8266 IRrecv::decodeDaikin2
    """
    from app.core.ir_protocols.ir_recv import (
        kHeader,
        kFooter,
        kMarkExcess,
        matchMark,
        matchSpace,
        _matchGeneric,
    )

    if nbits % 8 != 0:
        return False

    # Compliance
    if strict and nbits != kDaikin2Bits:
        return False

    # Leader
    if not matchMark(
        results.rawbuf[offset],
        kDaikin2LeaderMark,
        kDaikin2Tolerance + kDaikin2Tolerance,
        kMarkExcess,
    ):
        return False
    offset += 1
    if not matchSpace(
        results.rawbuf[offset],
        kDaikin2LeaderSpace,
        kDaikin2Tolerance + kDaikin2Tolerance,
        kMarkExcess,
    ):
        return False
    offset += 1

    # Section #1
    used = _matchGeneric(
        data_ptr=results.rawbuf[offset:],
        result_bits_ptr=None,
        result_bytes_ptr=results.state,
        use_bits=False,
        remaining=results.rawlen - offset,
        nbits=kDaikin2Section1Length * 8,
        hdrmark=kDaikin2HdrMark,
        hdrspace=kDaikin2HdrSpace,
        onemark=kDaikin2BitMark,
        onespace=kDaikin2OneSpace,
        zeromark=kDaikin2BitMark,
        zerospace=kDaikin2ZeroSpace,
        footermark=kDaikin2BitMark,
        footerspace=kDaikin2Gap,
        atleast=False,
        tolerance=kDaikin2Tolerance,
        excess=kMarkExcess,
        MSBfirst=False,
    )
    if used == 0:
        return False
    offset += used

    # Section #2
    used = _matchGeneric(
        data_ptr=results.rawbuf[offset:],
        result_bits_ptr=None,
        result_bytes_ptr=results.state[kDaikin2Section1Length:],
        use_bits=False,
        remaining=results.rawlen - offset,
        nbits=kDaikin2Section2Length * 8,
        hdrmark=kDaikin2HdrMark,
        hdrspace=kDaikin2HdrSpace,
        onemark=kDaikin2BitMark,
        onespace=kDaikin2OneSpace,
        zeromark=kDaikin2BitMark,
        zerospace=kDaikin2ZeroSpace,
        footermark=kDaikin2BitMark,
        footerspace=kDaikin2Gap,
        atleast=True,
        tolerance=kDaikin2Tolerance,
        excess=kMarkExcess,
        MSBfirst=False,
    )
    if used == 0:
        return False

    # Compliance
    if strict and not validChecksumDaikin2(results.state):
        return False

    # Success
    results.bits = nbits
    return True


## Decode a Daikin216 216-bit A/C message.
## Direct translation from IRremoteESP8266 IRrecv::decodeDaikin216 (ir_Daikin.cpp lines 1682-1730)
def decodeDaikin216(
    results, offset: int = 1, nbits: int = kDaikin216Bits, strict: bool = True
) -> bool:
    """
    Decode a Daikin216 216-bit A/C message.
    EXACT translation from IRremoteESP8266 IRrecv::decodeDaikin216
    """
    from app.core.ir_protocols.ir_recv import kMarkExcess, _matchGeneric

    if nbits % 8 != 0:
        return False

    # Compliance
    if strict and nbits != kDaikin216Bits:
        return False

    # Section #1
    used = _matchGeneric(
        data_ptr=results.rawbuf[offset:],
        result_bits_ptr=None,
        result_bytes_ptr=results.state,
        use_bits=False,
        remaining=results.rawlen - offset,
        nbits=kDaikin216Section1Length * 8,
        hdrmark=kDaikin216HdrMark,
        hdrspace=kDaikin216HdrSpace,
        onemark=kDaikin216BitMark,
        onespace=kDaikin216OneSpace,
        zeromark=kDaikin216BitMark,
        zerospace=kDaikin216ZeroSpace,
        footermark=kDaikin216BitMark,
        footerspace=kDaikin216Gap,
        atleast=False,
        tolerance=kDaikinTolerance,
        excess=kMarkExcess,
        MSBfirst=False,
    )
    if used == 0:
        return False
    offset += used

    # Section #2
    used = _matchGeneric(
        data_ptr=results.rawbuf[offset:],
        result_bits_ptr=None,
        result_bytes_ptr=results.state[kDaikin216Section1Length:],
        use_bits=False,
        remaining=results.rawlen - offset,
        nbits=kDaikin216Section2Length * 8,
        hdrmark=kDaikin216HdrMark,
        hdrspace=kDaikin216HdrSpace,
        onemark=kDaikin216BitMark,
        onespace=kDaikin216OneSpace,
        zeromark=kDaikin216BitMark,
        zerospace=kDaikin216ZeroSpace,
        footermark=kDaikin216BitMark,
        footerspace=kDaikin216Gap,
        atleast=True,
        tolerance=kDaikinTolerance,
        excess=kMarkExcess,
        MSBfirst=False,
    )
    if used == 0:
        return False

    # Compliance
    if strict and not validChecksumDaikin216(results.state):
        return False

    # Success
    results.bits = nbits
    return True


## Decode a Daikin160 160-bit A/C message.
## Direct translation from IRremoteESP8266 IRrecv::decodeDaikin160 (ir_Daikin.cpp lines 2037-2084)
def decodeDaikin160(
    results, offset: int = 1, nbits: int = kDaikin160Bits, strict: bool = True
) -> bool:
    """
    Decode a Daikin160 160-bit A/C message.
    EXACT translation from IRremoteESP8266 IRrecv::decodeDaikin160
    """
    from app.core.ir_protocols.ir_recv import kMarkExcess, _matchGeneric

    if nbits % 8 != 0:
        return False

    # Compliance
    if strict and nbits != kDaikin160Bits:
        return False

    # Section #1
    used = _matchGeneric(
        data_ptr=results.rawbuf[offset:],
        result_bits_ptr=None,
        result_bytes_ptr=results.state,
        use_bits=False,
        remaining=results.rawlen - offset,
        nbits=kDaikin160Section1Length * 8,
        hdrmark=kDaikin160HdrMark,
        hdrspace=kDaikin160HdrSpace,
        onemark=kDaikin160BitMark,
        onespace=kDaikin160OneSpace,
        zeromark=kDaikin160BitMark,
        zerospace=kDaikin160ZeroSpace,
        footermark=kDaikin160BitMark,
        footerspace=kDaikin160Gap,
        atleast=False,
        tolerance=kDaikinTolerance,
        excess=kMarkExcess,
        MSBfirst=False,
    )
    if used == 0:
        return False
    offset += used

    # Section #2
    used = _matchGeneric(
        data_ptr=results.rawbuf[offset:],
        result_bits_ptr=None,
        result_bytes_ptr=results.state[kDaikin160Section1Length:],
        use_bits=False,
        remaining=results.rawlen - offset,
        nbits=kDaikin160Section2Length * 8,
        hdrmark=kDaikin160HdrMark,
        hdrspace=kDaikin160HdrSpace,
        onemark=kDaikin160BitMark,
        onespace=kDaikin160OneSpace,
        zeromark=kDaikin160BitMark,
        zerospace=kDaikin160ZeroSpace,
        footermark=kDaikin160BitMark,
        footerspace=kDaikin160Gap,
        atleast=True,
        tolerance=kDaikinTolerance,
        excess=kMarkExcess,
        MSBfirst=False,
    )
    if used == 0:
        return False

    # Compliance
    if strict and not validChecksumDaikin160(results.state):
        return False

    # Success
    results.bits = nbits
    return True


## Decode a Daikin176 176-bit A/C message.
## Direct translation from IRremoteESP8266 IRrecv::decodeDaikin176 (ir_Daikin.cpp lines 2429-2478)
def decodeDaikin176(
    results, offset: int = 1, nbits: int = kDaikin176Bits, strict: bool = True
) -> bool:
    """
    Decode a Daikin176 176-bit A/C message.
    EXACT translation from IRremoteESP8266 IRrecv::decodeDaikin176
    """
    from app.core.ir_protocols.ir_recv import kMarkExcess, _matchGeneric

    if nbits % 8 != 0:
        return False

    # Compliance
    if strict and nbits != kDaikin176Bits:
        return False

    # Section #1
    used = _matchGeneric(
        data_ptr=results.rawbuf[offset:],
        result_bits_ptr=None,
        result_bytes_ptr=results.state,
        use_bits=False,
        remaining=results.rawlen - offset,
        nbits=kDaikin176Section1Length * 8,
        hdrmark=kDaikin176HdrMark,
        hdrspace=kDaikin176HdrSpace,
        onemark=kDaikin176BitMark,
        onespace=kDaikin176OneSpace,
        zeromark=kDaikin176BitMark,
        zerospace=kDaikin176ZeroSpace,
        footermark=kDaikin176BitMark,
        footerspace=kDaikin176Gap,
        atleast=False,
        tolerance=kDaikinTolerance,
        excess=kMarkExcess,
        MSBfirst=False,
    )
    if used == 0:
        return False
    offset += used

    # Section #2
    used = _matchGeneric(
        data_ptr=results.rawbuf[offset:],
        result_bits_ptr=None,
        result_bytes_ptr=results.state[kDaikin176Section1Length:],
        use_bits=False,
        remaining=results.rawlen - offset,
        nbits=kDaikin176Section2Length * 8,
        hdrmark=kDaikin176HdrMark,
        hdrspace=kDaikin176HdrSpace,
        onemark=kDaikin176BitMark,
        onespace=kDaikin176OneSpace,
        zeromark=kDaikin176BitMark,
        zerospace=kDaikin176ZeroSpace,
        footermark=kDaikin176BitMark,
        footerspace=kDaikin176Gap,
        atleast=True,
        tolerance=kDaikinTolerance,
        excess=kMarkExcess,
        MSBfirst=False,
    )
    if used == 0:
        return False

    # Compliance
    if strict and not validChecksumDaikin176(results.state):
        return False

    # Success
    results.bits = nbits
    return True


## Decode a Daikin128 128-bit A/C message.
## Direct translation from IRremoteESP8266 IRrecv::decodeDaikin128 (ir_Daikin.cpp lines 2924-2982)
def decodeDaikin128(
    results, offset: int = 1, nbits: int = kDaikin128Bits, strict: bool = True
) -> bool:
    """
    Decode a Daikin128 128-bit A/C message.
    EXACT translation from IRremoteESP8266 IRrecv::decodeDaikin128
    """
    from app.core.ir_protocols.ir_recv import kMarkExcess, matchMark, matchSpace, _matchGeneric

    if nbits % 8 != 0:
        return False

    # Compliance
    if strict and nbits != kDaikin128Bits:
        return False

    # Leader
    if not matchMark(results.rawbuf[offset], kDaikin128LeaderMark, kDaikinTolerance, kMarkExcess):
        return False
    offset += 1
    if not matchSpace(results.rawbuf[offset], kDaikin128LeaderSpace, kDaikinTolerance, kMarkExcess):
        return False
    offset += 1

    # Section #1
    used = _matchGeneric(
        data_ptr=results.rawbuf[offset:],
        result_bits_ptr=None,
        result_bytes_ptr=results.state,
        use_bits=False,
        remaining=results.rawlen - offset,
        nbits=kDaikin128SectionLength * 8,
        hdrmark=kDaikin128HdrMark,
        hdrspace=kDaikin128HdrSpace,
        onemark=kDaikin128BitMark,
        onespace=kDaikin128OneSpace,
        zeromark=kDaikin128BitMark,
        zerospace=kDaikin128ZeroSpace,
        footermark=kDaikin128FooterMark,
        footerspace=kDaikin128Gap,
        atleast=False,
        tolerance=kDaikinTolerance,
        excess=kMarkExcess,
        MSBfirst=False,
    )
    if used == 0:
        return False
    offset += used

    # Section #2
    used = _matchGeneric(
        data_ptr=results.rawbuf[offset:],
        result_bits_ptr=None,
        result_bytes_ptr=results.state[kDaikin128SectionLength:],
        use_bits=False,
        remaining=results.rawlen - offset,
        nbits=kDaikin128SectionLength * 8,
        hdrmark=kDaikin128HdrMark,
        hdrspace=kDaikin128HdrSpace,
        onemark=kDaikin128BitMark,
        onespace=kDaikin128OneSpace,
        zeromark=kDaikin128BitMark,
        zerospace=kDaikin128ZeroSpace,
        footermark=kDaikin128BitMark,
        footerspace=kDaikin128Gap,
        atleast=True,
        tolerance=kDaikinTolerance,
        excess=kMarkExcess,
        MSBfirst=False,
    )
    if used == 0:
        return False

    # Compliance
    if strict and not validChecksumDaikin128(results.state):
        return False

    # Success
    results.bits = nbits
    return True


## Decode a Daikin152 152-bit A/C message.
## Direct translation from IRremoteESP8266 IRrecv::decodeDaikin152 (ir_Daikin.cpp lines 3014-3063)
def decodeDaikin152(
    results, offset: int = 1, nbits: int = kDaikin152Bits, strict: bool = True
) -> bool:
    """
    Decode a Daikin152 152-bit A/C message.
    EXACT translation from IRremoteESP8266 IRrecv::decodeDaikin152
    """
    from app.core.ir_protocols.ir_recv import kMarkExcess, _matchGeneric

    if nbits % 8 != 0:
        return False

    # Compliance
    if strict and nbits != kDaikin152Bits:
        return False

    # Leader (5 bits of 0)
    used = _matchGeneric(
        data_ptr=results.rawbuf[offset:],
        result_bits_ptr=None,
        result_bytes_ptr=None,
        use_bits=False,
        remaining=results.rawlen - offset,
        nbits=kDaikin152LeaderBits,
        hdrmark=kDaikin152HdrMark,
        hdrspace=kDaikin152HdrSpace,
        onemark=kDaikin152BitMark,
        onespace=kDaikin152OneSpace,
        zeromark=kDaikin152BitMark,
        zerospace=kDaikin152ZeroSpace,
        footermark=0,
        footerspace=0,
        atleast=False,
        tolerance=kDaikinTolerance,
        excess=kMarkExcess,
        MSBfirst=False,
    )
    if used == 0:
        return False
    offset += used

    # Data
    used = _matchGeneric(
        data_ptr=results.rawbuf[offset:],
        result_bits_ptr=None,
        result_bytes_ptr=results.state,
        use_bits=False,
        remaining=results.rawlen - offset,
        nbits=nbits - kDaikin152LeaderBits,
        hdrmark=0,
        hdrspace=0,
        onemark=kDaikin152BitMark,
        onespace=kDaikin152OneSpace,
        zeromark=kDaikin152BitMark,
        zerospace=kDaikin152ZeroSpace,
        footermark=kDaikin152BitMark,
        footerspace=kDaikin152Gap,
        atleast=True,
        tolerance=kDaikinTolerance,
        excess=kMarkExcess,
        MSBfirst=False,
    )
    if used == 0:
        return False

    # Compliance
    if strict and not validChecksumDaikin152(results.state):
        return False

    # Success
    results.bits = nbits
    return True


## Decode a Daikin64 64-bit A/C message.
## Direct translation from IRremoteESP8266 IRrecv::decodeDaikin64 (ir_Daikin.cpp lines 3375-3417)
def decodeDaikin64(
    results, offset: int = 1, nbits: int = kDaikin64Bits, strict: bool = True
) -> bool:
    """
    Decode a Daikin64 64-bit A/C message.
    EXACT translation from IRremoteESP8266 IRrecv::decodeDaikin64
    """
    from app.core.ir_protocols.ir_recv import kMarkExcess, matchMark, matchSpace, _matchGeneric

    # Compliance
    if strict and nbits != kDaikin64Bits:
        return False

    # Leader
    if not matchMark(
        results.rawbuf[offset],
        kDaikin64LdrMark,
        kDaikinTolerance + kDaikin64ToleranceDelta,
        kMarkExcess,
    ):
        return False
    offset += 1
    if not matchSpace(
        results.rawbuf[offset],
        kDaikin64LdrSpace,
        kDaikinTolerance + kDaikin64ToleranceDelta,
        kMarkExcess,
    ):
        return False
    offset += 1

    # Data
    used = _matchGeneric(
        data_ptr=results.rawbuf[offset:],
        result_bits_ptr=None,
        result_bytes_ptr=results.state,
        use_bits=False,
        remaining=results.rawlen - offset,
        nbits=nbits,
        hdrmark=kDaikin64HdrMark,
        hdrspace=kDaikin64HdrSpace,
        onemark=kDaikin64BitMark,
        onespace=kDaikin64OneSpace,
        zeromark=kDaikin64BitMark,
        zerospace=kDaikin64ZeroSpace,
        footermark=kDaikin64BitMark,
        footerspace=kDaikin64Gap,
        atleast=True,
        tolerance=kDaikinTolerance + kDaikin64ToleranceDelta,
        excess=kMarkExcess,
        MSBfirst=False,
    )
    if used == 0:
        return False

    # Convert state bytes to uint64
    data_value = 0
    for i in range(8):
        data_value |= results.state[i] << (i * 8)

    # Compliance
    if strict and not validChecksumDaikin64(data_value):
        return False

    # Success
    results.bits = nbits
    results.value = data_value  # Store as integer for Daikin64
    return True


## Decode a Daikin200 200-bit A/C message.
## Direct translation from IRremoteESP8266 IRrecv::decodeDaikin200 (ir_Daikin.cpp lines 3782-3830)
def decodeDaikin200(
    results, offset: int = 1, nbits: int = kDaikin200Bits, strict: bool = True
) -> bool:
    """
    Decode a Daikin200 200-bit A/C message.
    EXACT translation from IRremoteESP8266 IRrecv::decodeDaikin200
    """
    from app.core.ir_protocols.ir_recv import kMarkExcess, _matchGeneric

    if nbits % 8 != 0:
        return False

    # Compliance
    if strict and nbits != kDaikin200Bits:
        return False

    # Section #1
    used = _matchGeneric(
        data_ptr=results.rawbuf[offset:],
        result_bits_ptr=None,
        result_bytes_ptr=results.state,
        use_bits=False,
        remaining=results.rawlen - offset,
        nbits=kDaikin200Section1Length * 8,
        hdrmark=kDaikin200HdrMark,
        hdrspace=kDaikin200HdrSpace,
        onemark=kDaikin200BitMark,
        onespace=kDaikin200OneSpace,
        zeromark=kDaikin200BitMark,
        zerospace=kDaikin200ZeroSpace,
        footermark=kDaikin200BitMark,
        footerspace=kDaikin200Gap,
        atleast=False,
        tolerance=kDaikinTolerance,
        excess=kMarkExcess,
        MSBfirst=False,
    )
    if used == 0:
        return False
    offset += used

    # Section #2
    used = _matchGeneric(
        data_ptr=results.rawbuf[offset:],
        result_bits_ptr=None,
        result_bytes_ptr=results.state[kDaikin200Section1Length:],
        use_bits=False,
        remaining=results.rawlen - offset,
        nbits=kDaikin200Section2Length * 8,
        hdrmark=kDaikin200HdrMark,
        hdrspace=kDaikin200HdrSpace,
        onemark=kDaikin200BitMark,
        onespace=kDaikin200OneSpace,
        zeromark=kDaikin200BitMark,
        zerospace=kDaikin200ZeroSpace,
        footermark=kDaikin200BitMark,
        footerspace=kDaikin200Gap,
        atleast=True,
        tolerance=kDaikinTolerance,
        excess=kMarkExcess,
        MSBfirst=False,
    )
    if used == 0:
        return False

    # Compliance
    if strict and not validChecksumDaikin200(results.state):
        return False

    # Success
    results.bits = nbits
    return True


## Decode a Daikin312 312-bit A/C message.
## Direct translation from IRremoteESP8266 IRrecv::decodeDaikin312 (ir_Daikin.cpp lines 3874-3922)
def decodeDaikin312(
    results, offset: int = 1, nbits: int = kDaikin312Bits, strict: bool = True
) -> bool:
    """
    Decode a Daikin312 312-bit A/C message.
    EXACT translation from IRremoteESP8266 IRrecv::decodeDaikin312
    """
    from app.core.ir_protocols.ir_recv import kMarkExcess, _matchGeneric

    if nbits % 8 != 0:
        return False

    # Compliance
    if strict and nbits != kDaikin312Bits:
        return False

    # Section #1
    used = _matchGeneric(
        data_ptr=results.rawbuf[offset:],
        result_bits_ptr=None,
        result_bytes_ptr=results.state,
        use_bits=False,
        remaining=results.rawlen - offset,
        nbits=kDaikin312Section1Length * 8,
        hdrmark=kDaikin312HdrMark,
        hdrspace=kDaikin312HdrSpace,
        onemark=kDaikin312BitMark,
        onespace=kDaikin312OneSpace,
        zeromark=kDaikin312BitMark,
        zerospace=kDaikin312ZeroSpace,
        footermark=kDaikin312BitMark,
        footerspace=kDaikin312HdrGap,
        atleast=False,
        tolerance=kDaikinTolerance,
        excess=kMarkExcess,
        MSBfirst=False,
    )
    if used == 0:
        return False
    offset += used

    # Section #2
    used = _matchGeneric(
        data_ptr=results.rawbuf[offset:],
        result_bits_ptr=None,
        result_bytes_ptr=results.state[kDaikin312Section1Length:],
        use_bits=False,
        remaining=results.rawlen - offset,
        nbits=kDaikin312Section2Length * 8,
        hdrmark=kDaikin312HdrMark,
        hdrspace=kDaikin312HdrSpace,
        onemark=kDaikin312BitMark,
        onespace=kDaikin312OneSpace,
        zeromark=kDaikin312BitMark,
        zerospace=kDaikin312ZeroSpace,
        footermark=kDaikin312BitMark,
        footerspace=kDaikin312SectionGap,
        atleast=True,
        tolerance=kDaikinTolerance,
        excess=kMarkExcess,
        MSBfirst=False,
    )
    if used == 0:
        return False

    # Compliance
    if strict and not validChecksumDaikin312(results.state):
        return False

    # Success
    results.bits = nbits
    return True


# =============================================================================
# CHECKSUM VALIDATION FUNCTIONS
# =============================================================================


## Verify the checksum is valid for a Daikin message.
## Direct translation from IRremoteESP8266 IRDaikinESP::validChecksum (ir_Daikin.cpp lines 131-149)
def validChecksumDaikin(state: List[int], length: int = kDaikinStateLength) -> bool:
    """
    Verify the checksum is valid for a Daikin message.
    EXACT translation from IRremoteESP8266 IRDaikinESP::validChecksum
    """
    # Data #1
    if length < kDaikinSection1Length:
        return False
    if state[kDaikinByteChecksum1] != sumBytes(state, kDaikinSection1Length - 1):
        return False

    # Data #2
    if length < kDaikinSection1Length + kDaikinSection2Length:
        return False
    if state[kDaikinByteChecksum2] != sumBytes(
        state[kDaikinSection1Length:], kDaikinSection2Length - 1
    ):
        return False

    # Data #3
    if length < kDaikinSection1Length + kDaikinSection2Length + 2:
        return False
    section3_start = kDaikinSection1Length + kDaikinSection2Length
    if state[length - 1] != sumBytes(state[section3_start:], length - section3_start - 1):
        return False

    return True


## Verify the checksum is valid for a Daikin2 message.
## Direct translation from IRremoteESP8266 IRDaikin2::validChecksum (ir_Daikin.cpp lines 729-745)
def validChecksumDaikin2(state: List[int], length: int = kDaikin2StateLength) -> bool:
    """
    Verify the checksum is valid for a Daikin2 message.
    EXACT translation from IRremoteESP8266 IRDaikin2::validChecksum
    """
    if length < kDaikin2Section1Length:
        return False
    if state[kDaikin2Section1Length - 1] != sumBytes(state, kDaikin2Section1Length - 1):
        return False

    if length < kDaikin2StateLength:
        return False
    if state[length - 1] != sumBytes(state[kDaikin2Section1Length:], kDaikin2Section2Length - 1):
        return False

    return True


## Verify the checksum is valid for a Daikin216 message.
def validChecksumDaikin216(state: List[int], length: int = kDaikin216StateLength) -> bool:
    """
    Verify the checksum is valid for a Daikin216 message.
    EXACT translation from IRremoteESP8266 IRDaikin216::validChecksum
    """
    if length < kDaikin216Section1Length:
        return False
    if state[kDaikin216Section1Length - 1] != sumBytes(state, kDaikin216Section1Length - 1):
        return False

    if length < kDaikin216StateLength:
        return False
    if state[length - 1] != sumBytes(
        state[kDaikin216Section1Length:], kDaikin216Section2Length - 1
    ):
        return False

    return True


## Verify the checksum is valid for a Daikin160 message.
def validChecksumDaikin160(state: List[int], length: int = kDaikin160StateLength) -> bool:
    """
    Verify the checksum is valid for a Daikin160 message.
    EXACT translation from IRremoteESP8266 IRDaikin160::validChecksum
    """
    if length < kDaikin160Section1Length:
        return False
    if state[kDaikin160Section1Length - 1] != sumBytes(state, kDaikin160Section1Length - 1):
        return False

    if length < kDaikin160StateLength:
        return False
    if state[length - 1] != sumBytes(
        state[kDaikin160Section1Length:], kDaikin160Section2Length - 1
    ):
        return False

    return True


## Verify the checksum is valid for a Daikin176 message.
def validChecksumDaikin176(state: List[int], length: int = kDaikin176StateLength) -> bool:
    """
    Verify the checksum is valid for a Daikin176 message.
    EXACT translation from IRremoteESP8266 IRDaikin176::validChecksum
    """
    if length < kDaikin176Section1Length:
        return False
    if state[kDaikin176Section1Length - 1] != sumBytes(state, kDaikin176Section1Length - 1):
        return False

    if length < kDaikin176StateLength:
        return False
    if state[length - 1] != sumBytes(
        state[kDaikin176Section1Length:], kDaikin176Section2Length - 1
    ):
        return False

    return True


## Verify the checksum is valid for a Daikin128 message.
def validChecksumDaikin128(state: List[int]) -> bool:
    """
    Verify the checksum is valid for a Daikin128 message.
    EXACT translation from IRremoteESP8266 IRDaikin128::validChecksum
    """
    if calcFirstChecksumDaikin128(state) != (state[7] >> 4):
        return False
    if calcSecondChecksumDaikin128(state) != (state[15] & 0xFF):
        return False
    return True


## Calculate first checksum for Daikin128.
def calcFirstChecksumDaikin128(state: List[int]) -> int:
    """
    Calculate first checksum for Daikin128.
    EXACT translation from IRremoteESP8266 IRDaikin128::calcFirstChecksum
    """
    return sumNibbles(state, 7, 0) & 0x0F


## Calculate second checksum for Daikin128.
def calcSecondChecksumDaikin128(state: List[int]) -> int:
    """
    Calculate second checksum for Daikin128.
    EXACT translation from IRremoteESP8266 IRDaikin128::calcSecondChecksum
    """
    return sumBytes(state[8:], 7, 0)


## Verify the checksum is valid for a Daikin152 message.
def validChecksumDaikin152(state: List[int], length: int = kDaikin152StateLength) -> bool:
    """
    Verify the checksum is valid for a Daikin152 message.
    EXACT translation from IRremoteESP8266 IRDaikin152::validChecksum
    """
    if length < kDaikin152StateLength:
        return False
    return state[length - 1] == sumBytes(state, length - 1)


## Verify the checksum is valid for a Daikin64 message.
def validChecksumDaikin64(data: int) -> bool:
    """
    Verify the checksum is valid for a Daikin64 message.
    EXACT translation from IRremoteESP8266 IRDaikin64::validChecksum
    """
    return calcChecksumDaikin64(data) == ((data >> kDaikin64ChecksumOffset) & 0x0F)


## Calculate checksum for Daikin64.
def calcChecksumDaikin64(data: int) -> int:
    """
    Calculate checksum for Daikin64.
    EXACT translation from IRremoteESP8266 IRDaikin64::calcChecksum
    """
    # Convert to bytes
    state = []
    for i in range(8):
        state.append((data >> (i * 8)) & 0xFF)

    return sumNibbles(state, 7, 0) & 0x0F


## Verify the checksum is valid for a Daikin200 message.
def validChecksumDaikin200(state: List[int], length: int = kDaikin200StateLength) -> bool:
    """
    Verify the checksum is valid for a Daikin200 message.
    EXACT translation from IRremoteESP8266 (similar to Daikin216)
    """
    if length < kDaikin200Section1Length:
        return False
    if state[kDaikin200Section1Length - 1] != sumBytes(state, kDaikin200Section1Length - 1):
        return False

    if length < kDaikin200StateLength:
        return False
    if state[length - 1] != sumBytes(
        state[kDaikin200Section1Length:], kDaikin200Section2Length - 1
    ):
        return False

    return True


## Verify the checksum is valid for a Daikin312 message.
def validChecksumDaikin312(state: List[int], length: int = kDaikin312StateLength) -> bool:
    """
    Verify the checksum is valid for a Daikin312 message.
    EXACT translation from IRremoteESP8266 (similar to Daikin2)
    """
    if length < kDaikin312Section1Length:
        return False
    if state[kDaikin312Section1Length - 1] != sumBytes(state, kDaikin312Section1Length - 1):
        return False

    if length < kDaikin312StateLength:
        return False
    if state[length - 1] != sumBytes(
        state[kDaikin312Section1Length:], kDaikin312Section2Length - 1
    ):
        return False

    return True


# =============================================================================
# IRDaikin216 CLASS - Full state manipulation for Daikin216 protocol
# =============================================================================

class IRDaikin216:
    """
    Class for handling Daikin216 216-bit A/C protocol.

    Based on IRremoteESP8266 IRDaikin216 class with exact byte structure:
    - Byte 7: Sum1 (checksum for section 1)
    - Byte 13: Power (bit 0), Mode (bits 2-4)
    - Byte 14: Temp (bits 1-6)
    - Byte 16: SwingV (bits 0-3), Fan (bits 4-7)
    - Byte 17: SwingH (bits 0-3)
    - Byte 21: Powerful (bit 0)
    - Byte 26: Sum2 (checksum for section 2)
    """

    def __init__(self):
        """Initialize with default state (all zeros + magic bytes)."""
        self.remote_state = [0x00] * kDaikin216StateLength
        self.stateReset()

    def stateReset(self):
        """Reset state to default values with magic bytes."""
        # Zero everything
        for i in range(kDaikin216StateLength):
            self.remote_state[i] = 0x00

        # Set magic bytes (from IRremoteESP8266 stateReset)
        self.remote_state[0] = 0x11
        self.remote_state[1] = 0xDA
        self.remote_state[2] = 0x27
        self.remote_state[3] = 0xF0
        # Byte 7 is Sum1 (checksum), set by checksum()
        self.remote_state[8] = 0x11
        self.remote_state[9] = 0xDA
        self.remote_state[10] = 0x27
        self.remote_state[23] = 0xC0
        # Byte 26 is Sum2 (checksum), set by checksum()

    def checksum(self):
        """Calculate and set checksums for both sections."""
        # Sum1 at byte 7: sum of bytes 0-6
        self.remote_state[7] = sumBytes(self.remote_state, kDaikin216Section1Length - 1)

        # Sum2 at byte 26: sum of bytes 8-25
        self.remote_state[26] = sumBytes(
            self.remote_state[kDaikin216Section1Length:],
            kDaikin216Section2Length - 1
        )

    def getRaw(self) -> List[int]:
        """Get the raw state bytes."""
        self.checksum()  # Ensure checksums are up to date
        return list(self.remote_state)

    def setRaw(self, new_state: List[int]):
        """Set the raw state from bytes."""
        length = min(len(new_state), kDaikin216StateLength)
        for i in range(length):
            self.remote_state[i] = new_state[i]

    # Power control
    def setPower(self, on: bool):
        """Set power state. Byte 13, bit 0."""
        if on:
            self.remote_state[13] |= 0b00000001  # Set bit 0
        else:
            self.remote_state[13] &= 0b11111110  # Clear bit 0

    def getPower(self) -> bool:
        """Get power state."""
        return (self.remote_state[13] & 0b00000001) != 0

    def on(self):
        """Turn power on."""
        self.setPower(True)

    def off(self):
        """Turn power off."""
        self.setPower(False)

    # Mode control
    def setMode(self, mode: int):
        """Set operating mode. Byte 13, bits 2-4 (3 bits)."""
        # Valid modes: Auto(0), Cool(3), Heat(4), Dry(2), Fan(6)
        if mode in [kDaikinAuto, kDaikinCool, kDaikinHeat, kDaikinDry, kDaikinFan]:
            # Clear bits 2-4, then set the mode
            self.remote_state[13] &= 0b11100011  # Clear bits 2-4
            self.remote_state[13] |= (mode & 0b111) << 2  # Set bits 2-4
        else:
            # Default to Auto
            self.setMode(kDaikinAuto)

    def getMode(self) -> int:
        """Get operating mode."""
        return (self.remote_state[13] >> 2) & 0b111

    # Temperature control
    def setTemp(self, temp: int):
        """Set temperature. Byte 14, bits 1-6 (6 bits)."""
        # Clamp to valid range
        degrees = max(temp, kDaikinMinTemp)
        degrees = min(degrees, kDaikinMaxTemp)

        # Clear bits 1-6, then set temperature
        self.remote_state[14] &= 0b10000001  # Clear bits 1-6
        self.remote_state[14] |= (degrees & 0b111111) << 1  # Set bits 1-6

    def getTemp(self) -> int:
        """Get temperature."""
        return (self.remote_state[14] >> 1) & 0b111111

    # Fan control
    def setFan(self, fan: int):
        """Set fan speed. Byte 16, bits 4-7 (4 bits)."""
        # Fan encoding: numeric speeds 1-5 are encoded as 2+fan (3-7)
        # Special values kDaikinFanQuiet (11) and kDaikinFanAuto (10) are used directly
        if fan == kDaikinFanQuiet or fan == kDaikinFanAuto:
            fanset = fan
        elif fan < kDaikinFanMin or fan > kDaikinFanMax:
            fanset = kDaikinFanAuto
        else:
            fanset = 2 + fan

        # Clear bits 4-7, then set fan
        self.remote_state[16] &= 0b00001111  # Clear bits 4-7
        self.remote_state[16] |= (fanset & 0b1111) << 4  # Set bits 4-7

    def getFan(self) -> int:
        """Get fan speed."""
        return (self.remote_state[16] >> 4) & 0b1111

    # Swing control
    def setSwingVertical(self, on: bool):
        """Set vertical swing. Byte 16, bits 0-3."""
        swing_val = kDaikin216SwingOn if on else kDaikin216SwingOff
        # Clear bits 0-3, then set swing
        self.remote_state[16] &= 0b11110000  # Clear bits 0-3
        self.remote_state[16] |= swing_val & 0b1111  # Set bits 0-3

    def getSwingVertical(self) -> bool:
        """Get vertical swing state."""
        return (self.remote_state[16] & 0b1111) == kDaikin216SwingOn

    def setSwingHorizontal(self, on: bool):
        """Set horizontal swing. Byte 17, bits 0-3."""
        swing_val = kDaikin216SwingOn if on else kDaikin216SwingOff
        # Clear bits 0-3, then set swing
        self.remote_state[17] &= 0b11110000  # Clear bits 0-3
        self.remote_state[17] |= swing_val & 0b1111  # Set bits 0-3

    def getSwingHorizontal(self) -> bool:
        """Get horizontal swing state."""
        return (self.remote_state[17] & 0b1111) == kDaikin216SwingOn

    # Powerful mode
    def setPowerful(self, on: bool):
        """Set powerful mode. Byte 21, bit 0."""
        if on:
            self.remote_state[21] |= 0b00000001  # Set bit 0
        else:
            self.remote_state[21] &= 0b11111110  # Clear bit 0

    def getPowerful(self) -> bool:
        """Get powerful mode state."""
        return (self.remote_state[21] & 0b00000001) != 0
