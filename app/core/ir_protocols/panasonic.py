# Copyright 2015 Kristian Lauszus
# Copyright 2017, 2018 David Conran
# Python translation: Direct conversion from C++ with NO optimizations

## @file
## @brief Support for Panasonic protocols.
## Panasonic protocol originally added by Kristian Lauszus
## (Thanks to zenwheel and other people at the original blog post)
## @see Panasonic https://github.com/z3t0/Arduino-IRremote
## @see http://www.remotecentral.com/cgi-bin/mboard/rc-pronto/thread.cgi?2615
## @see Panasonic A/C support heavily influenced by https://github.com/ToniA/ESPEasy/blob/HeatpumpIR/lib/HeatpumpIR/PanasonicHeatpumpIR.cpp
## Panasonic A/C Clock & Timer support:
##   Reverse Engineering by MikkelTb
##   Code by crankyoldgit
## Direct translation from IRremoteESP8266 ir_Panasonic.cpp and ir_Panasonic.h

from typing import List, Optional
import copy

# Supports:
#   Brand: Panasonic,  Model: TV (PANASONIC)
#   Brand: Panasonic,  Model: NKE series A/C (PANASONIC_AC NKE/2)
#   Brand: Panasonic,  Model: DKE series A/C (PANASONIC_AC DKE/3)
#   Brand: Panasonic,  Model: DKW series A/C (PANASONIC_AC DKE/3)
#   Brand: Panasonic,  Model: PKR series A/C (PANASONIC_AC DKE/3)
#   Brand: Panasonic,  Model: JKE series A/C (PANASONIC_AC JKE/4)
#   Brand: Panasonic,  Model: CKP series A/C (PANASONIC_AC CKP/5)
#   Brand: Panasonic,  Model: RKR series A/C (PANASONIC_AC RKR/6)
#   Brand: Panasonic,  Model: CS-ME10CKPG A/C (PANASONIC_AC CKP/5)
#   Brand: Panasonic,  Model: CS-ME12CKPG A/C (PANASONIC_AC CKP/5)
#   Brand: Panasonic,  Model: CS-ME14CKPG A/C (PANASONIC_AC CKP/5)
#   Brand: Panasonic,  Model: CS-E7PKR A/C (PANASONIC_AC DKE/2)
#   Brand: Panasonic,  Model: CS-Z9RKR A/C (PANASONIC_AC RKR/6)
#   Brand: Panasonic,  Model: CS-Z24RKR A/C (PANASONIC_AC RKR/6)
#   Brand: Panasonic,  Model: CS-YW9MKD A/C (PANASONIC_AC JKE/4)
#   Brand: Panasonic,  Model: CS-E12QKEW A/C (PANASONIC_AC DKE/3)
#   Brand: Panasonic,  Model: A75C2311 remote (PANASONIC_AC CKP/5)
#   Brand: Panasonic,  Model: A75C2616-1 remote (PANASONIC_AC DKE/3)
#   Brand: Panasonic,  Model: A75C3704 remote (PANASONIC_AC DKE/3)
#   Brand: Panasonic,  Model: PN1122V remote (PANASONIC_AC DKE/3)
#   Brand: Panasonic,  Model: A75C3747 remote (PANASONIC_AC JKE/4)
#   Brand: Panasonic,  Model: CS-E9CKP series A/C (PANASONIC_AC32)
#   Brand: Panasonic,  Model: A75C2295 remote (PANASONIC_AC32)
#   Brand: Panasonic,  Model: A75C4762 remote (PANASONIC_AC RKR/6)

# Constants - Timing values
# EXACT translation from IRremoteESP8266 ir_Panasonic.cpp lines 27-46
kPanasonicFreq = 36700
kPanasonicHdrMark = 3456  # uSeconds
kPanasonicHdrSpace = 1728  # uSeconds
kPanasonicBitMark = 432  # uSeconds
kPanasonicOneSpace = 1296  # uSeconds
kPanasonicZeroSpace = 432  # uSeconds
kPanasonicMinCommandLength = 163296  # uSeconds
kPanasonicEndGap = 5000  # uSeconds. See #245
kPanasonicMinGap = 74736  # uSeconds

kPanasonicAcSectionGap = 10000  # uSeconds
kPanasonicAcSection1Length = 8
kPanasonicAcMessageGap = 19000  # kDefaultMessageGap - Just a guess

kPanasonicAc32HdrMark = 3543  # uSeconds
kPanasonicAc32BitMark = 920  # uSeconds
kPanasonicAc32HdrSpace = 3450  # uSeconds
kPanasonicAc32OneSpace = 2575  # uSeconds
kPanasonicAc32ZeroSpace = 828  # uSeconds
kPanasonicAc32SectionGap = 13946  # uSeconds
kPanasonicAc32Sections = 2
kPanasonicAc32BlocksPerSection = 2

# State length constants
# EXACT translation from IRremoteESP8266 IRremoteESP8266.h
kPanasonicAcStateLength = 27
kPanasonicAcBits = kPanasonicAcStateLength * 8  # 216 bits
kPanasonicAcShortBits = 152  # Bits
kPanasonicAc32Bits = 32

kPanasonicBits = 48
kPanasonic40Bits = 40

kPanasonicAcExcess = 0
# Much higher than usual. See issue #540.
kPanasonicAcTolerance = 40

# Mode constants
# EXACT translation from IRremoteESP8266 ir_Panasonic.h lines 53-57
kPanasonicAcAuto = 0  # 0b000
kPanasonicAcDry = 2  # 0b010
kPanasonicAcCool = 3  # 0b011
kPanasonicAcHeat = 4  # 0b100
kPanasonicAcFan = 6  # 0b110

# Fan speed constants
# EXACT translation from IRremoteESP8266 ir_Panasonic.h lines 58-64
kPanasonicAcFanMin = 0
kPanasonicAcFanLow = 1
kPanasonicAcFanMed = 2
kPanasonicAcFanHigh = 3
kPanasonicAcFanMax = 4
kPanasonicAcFanAuto = 7
kPanasonicAcFanDelta = 3

# Temperature constants
# EXACT translation from IRremoteESP8266 ir_Panasonic.h lines 65-70
kPanasonicAcPowerOffset = 0
kPanasonicAcTempOffset = 1  # Bits
kPanasonicAcTempSize = 5  # Bits
kPanasonicAcMinTemp = 16  # Celsius
kPanasonicAcMaxTemp = 30  # Celsius
kPanasonicAcFanModeTemp = 27  # Celsius

# Feature constants
# EXACT translation from IRremoteESP8266 ir_Panasonic.h lines 71-75
kPanasonicAcQuietOffset = 0
kPanasonicAcPowerfulOffset = 5  # 0b100000
# CKP & RKR models have Powerful and Quiet bits swapped.
kPanasonicAcQuietCkpOffset = kPanasonicAcPowerfulOffset
kPanasonicAcPowerfulCkpOffset = kPanasonicAcQuietOffset

# Vertical swing constants
# EXACT translation from IRremoteESP8266 ir_Panasonic.h lines 76-81
kPanasonicAcSwingVHighest = 0x1  # 0b0001
kPanasonicAcSwingVHigh = 0x2  # 0b0010
kPanasonicAcSwingVMiddle = 0x3  # 0b0011
kPanasonicAcSwingVLow = 0x4  # 0b0100
kPanasonicAcSwingVLowest = 0x5  # 0b0101
kPanasonicAcSwingVAuto = 0xF  # 0b1111

# Horizontal swing constants
# EXACT translation from IRremoteESP8266 ir_Panasonic.h lines 83-88
kPanasonicAcSwingHMiddle = 0x6  # 0b0110
kPanasonicAcSwingHFullLeft = 0x9  # 0b1001
kPanasonicAcSwingHLeft = 0xA  # 0b1010
kPanasonicAcSwingHRight = 0xB  # 0b1011
kPanasonicAcSwingHFullRight = 0xC  # 0b1100
kPanasonicAcSwingHAuto = 0xD  # 0b1101

# Checksum and timer constants
# EXACT translation from IRremoteESP8266 ir_Panasonic.h lines 89-95
kPanasonicAcChecksumInit = 0xF4
kPanasonicAcOnTimerOffset = 1
kPanasonicAcOffTimerOffset = 2
kPanasonicAcTimeSize = 11  # Bits
kPanasonicAcTimeOverflowSize = 3  # Bits
kPanasonicAcTimeMax = 23 * 60 + 59  # Mins since midnight
kPanasonicAcTimeSpecial = 0x600

# Ion filter constants
# EXACT translation from IRremoteESP8266 ir_Panasonic.h lines 97-98
kPanasonicAcIonFilterByte = 22  # Byte
kPanasonicAcIonFilterOffset = 0  # Bit

# Known good state
# EXACT translation from IRremoteESP8266 ir_Panasonic.h lines 100-103
kPanasonicKnownGoodState = [
    0x02,
    0x20,
    0xE0,
    0x04,
    0x00,
    0x00,
    0x00,
    0x06,
    0x02,
    0x20,
    0xE0,
    0x04,
    0x00,
    0x00,
    0x2E,
    0x80,
    0x62,
    0x09,
    0x00,
    0x0E,
    0xE0,
    0x00,
    0x00,
    0x81,
    0x00,
    0x00,
    0x00,
]

# Panasonic AC32 mode constants
# EXACT translation from IRremoteESP8266 ir_Panasonic.h lines 209-213
kPanasonicAc32Fan = 1  # 0b001
kPanasonicAc32Cool = 2  # 0b010
kPanasonicAc32Dry = 3  # 0b011
kPanasonicAc32Heat = 4  # 0b100
kPanasonicAc32Auto = 6  # 0b110

# Panasonic AC32 fan constants
# EXACT translation from IRremoteESP8266 ir_Panasonic.h lines 215-220
kPanasonicAc32FanMin = 2
kPanasonicAc32FanLow = 3
kPanasonicAc32FanMed = 4
kPanasonicAc32FanHigh = 5
kPanasonicAc32FanMax = 6
kPanasonicAc32FanAuto = 0xF

# Panasonic AC32 swing constants
# EXACT translation from IRremoteESP8266 ir_Panasonic.h lines 221-222
kPanasonicAc32SwingVAuto = 0x7  # 0b111
kPanasonicAc32KnownGood = 0x0AF136FC  # Cool, Auto, 16C

# Model enums
# EXACT translation from IRremoteESP8266 IRremoteESP8266.h
kPanasonicUnknown = 0
kPanasonicDke = 1
kPanasonicJke = 2
kPanasonicNke = 3
kPanasonicLke = 4
kPanasonicCkp = 5
kPanasonicRkr = 6

# Bit manipulation constants
kHighNibble = 4
kLowNibble = 0
kModeBitsSize = 3
kNibbleSize = 4


def GETBIT8(byte: int, bit: int) -> int:
    """Get a bit from a byte"""
    return (byte >> bit) & 0x01


def GETBITS8(byte: int, offset: int, size: int) -> int:
    """Get multiple bits from a byte"""
    mask = (1 << size) - 1
    return (byte >> offset) & mask


def GETBITS64(value: int, offset: int, size: int) -> int:
    """Get multiple bits from a 64-bit value"""
    mask = (1 << size) - 1
    return (value >> offset) & mask


def setBit(byte_ptr: List[int], bit: int, on: bool) -> None:
    """Set a bit in a byte array element"""
    if on:
        byte_ptr[0] |= 1 << bit
    else:
        byte_ptr[0] &= ~(1 << bit)


def setBits(byte_ptr: List[int], offset: int, nbits: int, data: int) -> None:
    """Set multiple bits in a byte array element"""
    mask = ((1 << nbits) - 1) << offset
    byte_ptr[0] = (byte_ptr[0] & ~mask) | ((data << offset) & mask)


def sumBytes(state: List[int], length: int, init: int = 0) -> int:
    """Sum bytes for checksum calculation"""
    # EXACT translation from IRremoteESP8266 IRutils.cpp sumBytes
    checksum = init
    for i in range(length):
        checksum += state[i]
    return checksum & 0xFF


## Send a Panasonic formatted message.
## Status: STABLE / Should be working.
## @param[in] data The message to be sent.
## @param[in] nbits The number of bits of message to be sent.
## @param[in] repeat The number of times the command is to be repeated.
## @note This protocol is a modified version of Kaseikyo.
## @note Use this method if you want to send the results of `decodePanasonic`.
## EXACT translation from IRremoteESP8266 ir_Panasonic.cpp lines 72-78
def sendPanasonic64(data: int, nbits: int = kPanasonicBits, repeat: int = 0) -> List[int]:
    """
    Send a Panasonic 64-bit formatted message.
    EXACT translation from IRremoteESP8266 IRsend::sendPanasonic64

    Returns timing array instead of transmitting via hardware.
    """
    from app.core.ir_protocols.ir_send import sendGeneric

    return sendGeneric(
        headermark=kPanasonicHdrMark,
        headerspace=kPanasonicHdrSpace,
        onemark=kPanasonicBitMark,
        onespace=kPanasonicOneSpace,
        zeromark=kPanasonicBitMark,
        zerospace=kPanasonicZeroSpace,
        footermark=kPanasonicBitMark,
        mesgtime=kPanasonicMinCommandLength,
        data_uint64=data,
        nbits=nbits,
        MSBfirst=True,
    )


## Send a Panasonic formatted message.
## Status: STABLE, but DEPRECATED
## @deprecated This is only for legacy use only, please use `sendPanasonic64()`
##   instead.
## @param[in] address The 16-bit manufacturer code.
## @param[in] data The 32-bit data portion of the message to be sent.
## @param[in] nbits The number of bits of message to be sent.
## @param[in] repeat The number of times the command is to be repeated.
## @note This protocol is a modified version of Kaseikyo.
## EXACT translation from IRremoteESP8266 ir_Panasonic.cpp lines 89-93
def sendPanasonic(
    address: int, data: int, nbits: int = kPanasonicBits, repeat: int = 0
) -> List[int]:
    """
    Send a Panasonic formatted message (legacy).
    EXACT translation from IRremoteESP8266 IRsend::sendPanasonic
    """
    combined = (address << 32) | data
    return sendPanasonic64(combined, nbits, repeat)


## Calculate the raw Panasonic data based on device, subdevice, & function.
## Status: STABLE / Should be working.
## @param[in] manufacturer A 16-bit manufacturer code. e.g. 0x4004 is Panasonic
## @param[in] device An 8-bit code.
## @param[in] subdevice An 8-bit code.
## @param[in] function An 8-bit code.
## @return A value suitable for use with `sendPanasonic64()`.
## @note Panasonic 48-bit protocol is a modified version of Kaseikyo.
## @see http://www.remotecentral.com/cgi-bin/mboard/rc-pronto/thread.cgi?2615
## EXACT translation from IRremoteESP8266 ir_Panasonic.cpp lines 104-113
def encodePanasonic(manufacturer: int, device: int, subdevice: int, function: int) -> int:
    """
    Encode Panasonic parameters into a 64-bit value.
    EXACT translation from IRremoteESP8266 IRsend::encodePanasonic
    """
    checksum = device ^ subdevice ^ function
    return (manufacturer << 32) | (device << 24) | (subdevice << 16) | (function << 8) | checksum


## Decode the supplied Panasonic message.
## Status: STABLE / Should be working.
## @param[in,out] results Ptr to the data to decode & where to store the result
## @param[in] offset The starting index to use when attempting to decode the
##   raw data. Typically/Defaults to kStartOffset.
## @param[in] nbits The number of data bits to expect.
## @param[in] manufacturer A 16-bit manufacturer code. e.g. 0x4004 is Panasonic
## @param[in] strict Flag indicating if we should perform strict matching.
## @return True if it can decode it, false if it can't.
## @warning Results to be used with `sendPanasonic64()`, not `sendPanasonic()`.
## @note Panasonic 48-bit protocol is a modified version of Kaseikyo.
## @see http://www.remotecentral.com/cgi-bin/mboard/rc-pronto/thread.cgi?2615
## @see http://www.hifi-remote.com/wiki/index.php?title=Panasonic
## EXACT translation from IRremoteESP8266 ir_Panasonic.cpp lines 131-174
def decodePanasonic(
    results,
    offset: int = 1,
    nbits: int = kPanasonicBits,
    strict: bool = True,
    manufacturer: int = 0x4004,
) -> bool:
    """
    Decode a Panasonic IR message.
    EXACT translation from IRremoteESP8266 IRrecv::decodePanasonic
    """
    from app.core.ir_protocols.ir_recv import _matchGeneric

    if strict:  # Compliance checks
        if nbits not in [kPanasonic40Bits, kPanasonicBits]:
            return False  # Request is out of spec.

    data = 0

    # Match Header + Data + Footer
    used = _matchGeneric(
        data_ptr=results.rawbuf[offset:],
        result_bits_ptr=None,
        result_bytes_ptr=None,
        use_bits=True,
        remaining=results.rawlen - offset,
        nbits=nbits,
        hdrmark=kPanasonicHdrMark,
        hdrspace=kPanasonicHdrSpace,
        onemark=kPanasonicBitMark,
        onespace=kPanasonicOneSpace,
        zeromark=kPanasonicBitMark,
        zerospace=kPanasonicZeroSpace,
        footermark=kPanasonicBitMark,
        footerspace=kPanasonicEndGap,
        atleast=True,
        tolerance=25,
        excess=0,
        MSBfirst=True,
    )
    if used == 0:
        return False

    # Extract data from result - matchGeneric stores in results.value
    data = results.value

    # Compliance
    address = data >> 32
    command = data & 0xFFFFFFFF
    if strict:
        if address != manufacturer:  # Verify the Manufacturer code.
            return False
        # Verify the checksum.
        checksumOrig = data & 0xFF
        checksumCalc = ((data >> 16) & 0xFF) ^ ((data >> 8) & 0xFF)
        if nbits != kPanasonic40Bits:
            checksumCalc ^= (data >> 24) & 0xFF
        if checksumOrig != checksumCalc:
            return False

    # Success
    results.value = data
    results.address = address
    results.command = command
    results.bits = nbits
    return True


## Send a Panasonic A/C message.
## Status: STABLE / Work with real device(s).
## @param[in] data The message to be sent.
## @param[in] nbytes The number of bytes of message to be sent.
## @param[in] repeat The number of times the command is to be repeated.
## EXACT translation from IRremoteESP8266 ir_Panasonic.cpp lines 183-200
def sendPanasonicAC(
    data: List[int], nbytes: int = kPanasonicAcStateLength, repeat: int = 0
) -> List[int]:
    """
    Send a Panasonic A/C formatted message.
    EXACT translation from IRremoteESP8266 IRsend::sendPanasonicAC

    Returns timing array instead of transmitting via hardware.
    """
    if nbytes < kPanasonicAcSection1Length:
        return []

    from app.core.ir_protocols.ir_send import sendGeneric

    all_timings = []

    for r in range(repeat + 1):
        # First section. (8 bytes)
        section1_timings = sendGeneric(
            headermark=kPanasonicHdrMark,
            headerspace=kPanasonicHdrSpace,
            onemark=kPanasonicBitMark,
            onespace=kPanasonicOneSpace,
            zeromark=kPanasonicBitMark,
            zerospace=kPanasonicZeroSpace,
            footermark=kPanasonicBitMark,
            gap=kPanasonicAcSectionGap,  # 10,000µs gap before section 2
            dataptr=data,
            nbytes=kPanasonicAcSection1Length,
            MSBfirst=False,
            repeat=0,  # Don't use repeat inside sendGeneric, handle it here
        )
        all_timings.extend(section1_timings)

        # Second section. (The rest of the data bytes)
        section2_timings = sendGeneric(
            headermark=kPanasonicHdrMark,
            headerspace=kPanasonicHdrSpace,
            onemark=kPanasonicBitMark,
            onespace=kPanasonicOneSpace,
            zeromark=kPanasonicBitMark,
            zerospace=kPanasonicZeroSpace,
            footermark=kPanasonicBitMark,
            gap=0,  # No gap after final section
            dataptr=data[kPanasonicAcSection1Length:],
            nbytes=nbytes - kPanasonicAcSection1Length,
            MSBfirst=False,
            repeat=0,
        )
        all_timings.extend(section2_timings)

        # Add inter-message gap only between repeated messages
        if r < repeat:
            all_timings.append(kPanasonicAcMessageGap)

    return all_timings


## Class for handling detailed Panasonic A/C messages.
## EXACT translation from IRremoteESP8266 IRPanasonicAc class
class IRPanasonicAc:
    """
    Class for handling detailed Panasonic A/C messages.
    EXACT translation from IRremoteESP8266 IRPanasonicAc class
    """

    ## Class constructor
    ## @param[in] pin GPIO to be used when sending.
    ## @param[in] inverted Is the output signal to be inverted?
    ## @param[in] use_modulation Is frequency modulation to be used?
    ## EXACT translation from IRremoteESP8266 ir_Panasonic.cpp lines 207-209
    def __init__(self, pin: int = 0, inverted: bool = False, use_modulation: bool = True) -> None:
        self.remote_state = [0] * kPanasonicAcStateLength
        self._temp = 25
        self._swingh = kPanasonicAcSwingHMiddle
        self.stateReset()

    ## Reset the state of the remote to a known good state/sequence.
    ## EXACT translation from IRremoteESP8266 ir_Panasonic.cpp lines 212-216
    def stateReset(self) -> None:
        for i in range(kPanasonicAcStateLength):
            self.remote_state[i] = kPanasonicKnownGoodState[i]
        self._temp = 25  # An initial saved desired temp. Completely made up.
        self._swingh = kPanasonicAcSwingHMiddle  # A similar made up value for H Swing.

    ## Verify the checksum is valid for a given state.
    ## @param[in] state The array to verify the checksum of.
    ## @param[in] length The length of the state array.
    ## @return true, if the state has a valid checksum. Otherwise, false.
    ## EXACT translation from IRremoteESP8266 ir_Panasonic.cpp lines 225-229
    @staticmethod
    def validChecksum(state: List[int], length: int = kPanasonicAcStateLength) -> bool:
        if length < 2:
            return False  # 1 byte of data can't have a checksum.
        return state[length - 1] == sumBytes(state, length - 1, kPanasonicAcChecksumInit)

    ## Calculate the checksum for a given state.
    ## @param[in] state The value to calc the checksum of.
    ## @param[in] length The size/length of the state.
    ## @return The calculated checksum value.
    ## EXACT translation from IRremoteESP8266 ir_Panasonic.cpp lines 235-238
    @staticmethod
    def calcChecksum(state: List[int], length: int = kPanasonicAcStateLength) -> int:
        return sumBytes(state, length - 1, kPanasonicAcChecksumInit)

    ## Calculate and set the checksum values for the internal state.
    ## @param[in] length The size/length of the state.
    ## EXACT translation from IRremoteESP8266 ir_Panasonic.cpp lines 242-244
    def fixChecksum(self, length: int = kPanasonicAcStateLength) -> None:
        self.remote_state[length - 1] = self.calcChecksum(self.remote_state, length)

    ## Send the current internal state as an IR message.
    ## @param[in] repeat Nr. of times the message will be repeated.
    ## EXACT translation from IRremoteESP8266 ir_Panasonic.cpp lines 249-251
    def send(self, repeat: int = 0) -> List[int]:
        return sendPanasonicAC(self.getRaw(), kPanasonicAcStateLength, repeat)

    ## Set the model of the A/C to emulate.
    ## @param[in] model The enum of the appropriate model.
    ## EXACT translation from IRremoteESP8266 ir_Panasonic.cpp lines 256-302
    def setModel(self, model: int) -> None:
        if model not in [
            kPanasonicDke,
            kPanasonicJke,
            kPanasonicLke,
            kPanasonicNke,
            kPanasonicCkp,
            kPanasonicRkr,
        ]:
            # Only proceed if we know what to do.
            return

        # clear & set the various bits and bytes.
        self.remote_state[13] &= 0xF0
        self.remote_state[17] = 0x00
        self.remote_state[21] &= 0b11101111
        self.remote_state[23] = 0x81
        self.remote_state[25] = 0x00

        if model == kPanasonicLke:
            self.remote_state[13] |= 0x02
            self.remote_state[17] = 0x06
        elif model == kPanasonicDke:
            self.remote_state[23] = 0x01
            self.remote_state[25] = 0x06
            # Has to be done last as setSwingHorizontal has model check built-in
            self.setSwingHorizontal(self._swingh)
        elif model == kPanasonicNke:
            self.remote_state[17] = 0x06
        elif model == kPanasonicJke:
            pass
        elif model == kPanasonicCkp:
            self.remote_state[21] |= 0x10
            self.remote_state[23] = 0x01
        elif model == kPanasonicRkr:
            self.remote_state[13] |= 0x08
            self.remote_state[23] = 0x89

        # Reset the Ion filter.
        self.setIon(self.getIon())

    ## Get/Detect the model of the A/C.
    ## @return The enum of the compatible model.
    ## EXACT translation from IRremoteESP8266 ir_Panasonic.cpp lines 306-321
    def getModel(self) -> int:
        if self.remote_state[23] == 0x89:
            return kPanasonicRkr
        if self.remote_state[17] == 0x00:
            if (self.remote_state[21] & 0x10) and (self.remote_state[23] & 0x01):
                return kPanasonicCkp
            if self.remote_state[23] & 0x80:
                return kPanasonicJke
        if self.remote_state[17] == 0x06 and (self.remote_state[13] & 0x0F) == 0x02:
            return kPanasonicLke
        if self.remote_state[23] == 0x01:
            return kPanasonicDke
        if self.remote_state[17] == 0x06:
            return kPanasonicNke
        return kPanasonicUnknown  # Default

    ## Get a PTR to the internal state/code for this protocol.
    ## @return PTR to a code for this protocol based on the current internal state.
    ## EXACT translation from IRremoteESP8266 ir_Panasonic.cpp lines 325-328
    def getRaw(self) -> List[int]:
        self.fixChecksum()
        return self.remote_state

    ## Set the internal state from a valid code for this protocol.
    ## @param[in] state A valid code for this protocol.
    ## EXACT translation from IRremoteESP8266 ir_Panasonic.cpp lines 332-334
    def setRaw(self, state: List[int]) -> None:
        for i in range(min(len(state), kPanasonicAcStateLength)):
            self.remote_state[i] = state[i]

    ## Control the power state of the A/C unit.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## @warning For CKP models, the remote has no memory of the power state the A/C
    ##   unit should be in. For those models setting this on/true will toggle the
    ##   power state of the Panasonic A/C unit with the next message.
    ##     e.g. If the A/C unit is already on, setPower(true) will turn it off.
    ##       If the A/C unit is already off, setPower(true) will turn it on.
    ##       `setPower(false)` will leave the A/C power state as it was.
    ##   For all other models, setPower(true) should set the internal state to
    ##   turn it on, and setPower(false) should turn it off.
    ## EXACT translation from IRremoteESP8266 ir_Panasonic.cpp lines 346-348
    def setPower(self, on: bool) -> None:
        setBit([self.remote_state[13]], kPanasonicAcPowerOffset, on)
        self.remote_state[13] = [self.remote_state[13]][0]

    ## Get the A/C power state of the remote.
    ## @return true, the setting is on. false, the setting is off.
    ## @warning Except for CKP models, where it returns if the power state will be
    ##   toggled on the A/C unit when the next message is sent.
    ## EXACT translation from IRremoteESP8266 ir_Panasonic.cpp lines 354-356
    def getPower(self) -> bool:
        return bool(GETBIT8(self.remote_state[13], kPanasonicAcPowerOffset))

    ## Change the power setting to On.
    ## EXACT translation from IRremoteESP8266 ir_Panasonic.cpp line 359
    def on(self) -> None:
        self.setPower(True)

    ## Change the power setting to Off.
    ## EXACT translation from IRremoteESP8266 ir_Panasonic.cpp line 362
    def off(self) -> None:
        self.setPower(False)

    ## Get the operating mode setting of the A/C.
    ## @return The current operating mode setting.
    ## EXACT translation from IRremoteESP8266 ir_Panasonic.cpp lines 366-368
    def getMode(self) -> int:
        return GETBITS8(self.remote_state[13], kHighNibble, kModeBitsSize)

    ## Set the operating mode of the A/C.
    ## @param[in] desired The desired operating mode.
    ## EXACT translation from IRremoteESP8266 ir_Panasonic.cpp lines 372-391
    def setMode(self, desired: int) -> None:
        mode = kPanasonicAcAuto  # Default to Auto mode.
        if desired == kPanasonicAcFan:
            # Allegedly Fan mode has a temperature of 27.
            self.setTemp(kPanasonicAcFanModeTemp, False)
            mode = desired
        elif desired in [kPanasonicAcAuto, kPanasonicAcCool, kPanasonicAcHeat, kPanasonicAcDry]:
            mode = desired
            # Set the temp to the saved temp, just incase our previous mode was Fan.
            self.setTemp(self._temp)

        self.remote_state[13] &= 0x0F  # Clear the previous mode bits.
        setBits([self.remote_state[13]], kHighNibble, kModeBitsSize, mode)
        self.remote_state[13] = [self.remote_state[13]][0]

    ## Get the current temperature setting.
    ## @return The current setting for temp. in degrees celsius.
    ## EXACT translation from IRremoteESP8266 ir_Panasonic.cpp lines 395-398
    def getTemp(self) -> int:
        return GETBITS8(self.remote_state[14], kPanasonicAcTempOffset, kPanasonicAcTempSize)

    ## Set the temperature.
    ## @param[in] celsius The temperature in degrees celsius.
    ## @param[in] remember: A flag for the class to remember the temperature.
    ## @note Automatically safely limits the temp to the operating range supported.
    ## EXACT translation from IRremoteESP8266 ir_Panasonic.cpp lines 404-411
    def setTemp(self, celsius: int, remember: bool = True) -> None:
        temperature = max(celsius, kPanasonicAcMinTemp)
        temperature = min(temperature, kPanasonicAcMaxTemp)
        if remember:
            self._temp = temperature
        setBits([self.remote_state[14]], kPanasonicAcTempOffset, kPanasonicAcTempSize, temperature)
        self.remote_state[14] = [self.remote_state[14]][0]

    ## Get the current vertical swing setting.
    ## @return The current position it is set to.
    ## EXACT translation from IRremoteESP8266 ir_Panasonic.cpp lines 415-417
    def getSwingVertical(self) -> int:
        return GETBITS8(self.remote_state[16], kLowNibble, kNibbleSize)

    ## Control the vertical swing setting.
    ## @param[in] desired_elevation The position to set the vertical swing to.
    ## EXACT translation from IRremoteESP8266 ir_Panasonic.cpp lines 421-428
    def setSwingVertical(self, desired_elevation: int) -> None:
        elevation = desired_elevation
        if elevation != kPanasonicAcSwingVAuto:
            elevation = max(elevation, kPanasonicAcSwingVHighest)
            elevation = min(elevation, kPanasonicAcSwingVLowest)
        setBits([self.remote_state[16]], kLowNibble, kNibbleSize, elevation)
        self.remote_state[16] = [self.remote_state[16]][0]

    ## Get the current horizontal swing setting.
    ## @return The current position it is set to.
    ## EXACT translation from IRremoteESP8266 ir_Panasonic.cpp lines 432-434
    def getSwingHorizontal(self) -> int:
        return GETBITS8(self.remote_state[17], kLowNibble, kNibbleSize)

    ## Control the horizontal swing setting.
    ## @param[in] desired_direction The position to set the horizontal swing to.
    ## EXACT translation from IRremoteESP8266 ir_Panasonic.cpp lines 438-463
    def setSwingHorizontal(self, desired_direction: int) -> None:
        if desired_direction not in [
            kPanasonicAcSwingHAuto,
            kPanasonicAcSwingHMiddle,
            kPanasonicAcSwingHFullLeft,
            kPanasonicAcSwingHLeft,
            kPanasonicAcSwingHRight,
            kPanasonicAcSwingHFullRight,
        ]:
            # Ignore anything that isn't valid.
            return

        self._swingh = desired_direction  # Store the direction for later.
        direction = desired_direction
        model = self.getModel()

        if model in [kPanasonicDke, kPanasonicRkr]:
            pass
        elif model in [kPanasonicNke, kPanasonicLke]:
            direction = kPanasonicAcSwingHMiddle
        else:  # Ignore everything else.
            return

        setBits([self.remote_state[17]], kLowNibble, kNibbleSize, direction)
        self.remote_state[17] = [self.remote_state[17]][0]

    ## Set the speed of the fan.
    ## @param[in] speed The desired setting.
    ## EXACT translation from IRremoteESP8266 ir_Panasonic.cpp lines 467-480
    def setFan(self, speed: int) -> None:
        if speed in [
            kPanasonicAcFanMin,
            kPanasonicAcFanLow,
            kPanasonicAcFanMed,
            kPanasonicAcFanHigh,
            kPanasonicAcFanMax,
            kPanasonicAcFanAuto,
        ]:
            setBits([self.remote_state[16]], kHighNibble, kNibbleSize, speed + kPanasonicAcFanDelta)
            self.remote_state[16] = [self.remote_state[16]][0]
        else:
            self.setFan(kPanasonicAcFanAuto)

    ## Get the current fan speed setting.
    ## @return The current fan speed.
    ## EXACT translation from IRremoteESP8266 ir_Panasonic.cpp lines 484-487
    def getFan(self) -> int:
        return GETBITS8(self.remote_state[16], kHighNibble, kNibbleSize) - kPanasonicAcFanDelta

    ## Get the Quiet setting of the A/C.
    ## @return true, the setting is on. false, the setting is off.
    ## EXACT translation from IRremoteESP8266 ir_Panasonic.cpp lines 491-499
    def getQuiet(self) -> bool:
        model = self.getModel()
        if model in [kPanasonicRkr, kPanasonicCkp]:
            return bool(GETBIT8(self.remote_state[21], kPanasonicAcQuietCkpOffset))
        else:
            return bool(GETBIT8(self.remote_state[21], kPanasonicAcQuietOffset))

    ## Set the Quiet setting of the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## EXACT translation from IRremoteESP8266 ir_Panasonic.cpp lines 503-512
    def setQuiet(self, on: bool) -> None:
        model = self.getModel()
        if model in [kPanasonicRkr, kPanasonicCkp]:
            offset = kPanasonicAcQuietCkpOffset
        else:
            offset = kPanasonicAcQuietOffset

        if on:
            self.setPowerful(False)  # Powerful is mutually exclusive.
        setBit([self.remote_state[21]], offset, on)
        self.remote_state[21] = [self.remote_state[21]][0]

    ## Get the Powerful (Turbo) setting of the A/C.
    ## @return true, the setting is on. false, the setting is off.
    ## EXACT translation from IRremoteESP8266 ir_Panasonic.cpp lines 516-524
    def getPowerful(self) -> bool:
        model = self.getModel()
        if model in [kPanasonicRkr, kPanasonicCkp]:
            return bool(GETBIT8(self.remote_state[21], kPanasonicAcPowerfulCkpOffset))
        else:
            return bool(GETBIT8(self.remote_state[21], kPanasonicAcPowerfulOffset))

    ## Set the Powerful (Turbo) setting of the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## EXACT translation from IRremoteESP8266 ir_Panasonic.cpp lines 528-538
    def setPowerful(self, on: bool) -> None:
        model = self.getModel()
        if model in [kPanasonicRkr, kPanasonicCkp]:
            offset = kPanasonicAcPowerfulCkpOffset
        else:
            offset = kPanasonicAcPowerfulOffset

        if on:
            self.setQuiet(False)  # Quiet is mutually exclusive.
        setBit([self.remote_state[21]], offset, on)
        self.remote_state[21] = [self.remote_state[21]][0]

    ## Convert standard (military/24hr) time to nr. of minutes since midnight.
    ## @param[in] hours The hours component of the time.
    ## @param[in] mins The minutes component of the time.
    ## @return The nr of minutes since midnight.
    ## EXACT translation from IRremoteESP8266 ir_Panasonic.cpp lines 544-546
    @staticmethod
    def encodeTime(hours: int, mins: int) -> int:
        return min(hours, 23) * 60 + min(mins, 59)

    ## Get the time from a given pointer location.
    ## @param[in] ptr A pointer to a time location in a state.
    ## @return The time expressed as nr. of minutes past midnight.
    ## @note Internal use only.
    ## EXACT translation from IRremoteESP8266 ir_Panasonic.cpp lines 552-558
    @staticmethod
    def _getTime(ptr: List[int]) -> int:
        result = (
            GETBITS8(ptr[1], kLowNibble, kPanasonicAcTimeOverflowSize)
            << (kPanasonicAcTimeSize - kPanasonicAcTimeOverflowSize)
        ) + ptr[0]
        if result == kPanasonicAcTimeSpecial:
            return 0
        return result

    ## Get the current clock time value.
    ## @return The time expressed as nr. of minutes past midnight.
    ## EXACT translation from IRremoteESP8266 ir_Panasonic.cpp line 562
    def getClock(self) -> int:
        return self._getTime(self.remote_state[24:26])

    ## Set the time at a given pointer location.
    ## @param[in, out] ptr A pointer to a time location in a state.
    ## @param[in] mins_since_midnight The time as nr. of minutes past midnight.
    ## @param[in] round_down Do we round to the nearest 10 minute mark?
    ## @note Internal use only.
    ## EXACT translation from IRremoteESP8266 ir_Panasonic.cpp lines 569-579
    @staticmethod
    def _setTime(ptr: List[int], mins_since_midnight: int, round_down: bool) -> None:
        corrected = min(mins_since_midnight, kPanasonicAcTimeMax)
        if round_down:
            corrected -= corrected % 10
        if mins_since_midnight == kPanasonicAcTimeSpecial:
            corrected = kPanasonicAcTimeSpecial
        ptr[0] = corrected & 0xFF
        setBits(
            [ptr[1]],
            kLowNibble,
            kPanasonicAcTimeOverflowSize,
            corrected >> (kPanasonicAcTimeSize - kPanasonicAcTimeOverflowSize),
        )

    ## Set the current clock time value.
    ## @param[in] mins_since_midnight The time as nr. of minutes past midnight.
    ## EXACT translation from IRremoteESP8266 ir_Panasonic.cpp lines 583-585
    def setClock(self, mins_since_midnight: int) -> None:
        self._setTime(self.remote_state[24:26], mins_since_midnight, False)

    ## Get the On Timer time value.
    ## @return The time expressed as nr. of minutes past midnight.
    ## EXACT translation from IRremoteESP8266 ir_Panasonic.cpp line 589
    def getOnTimer(self) -> int:
        return self._getTime(self.remote_state[18:20])

    ## Set/Enable the On Timer.
    ## @param[in] mins_since_midnight The time as nr. of minutes past midnight.
    ## @param[in] enable Do we enable the timer or not?
    ## EXACT translation from IRremoteESP8266 ir_Panasonic.cpp lines 594-600
    def setOnTimer(self, mins_since_midnight: int, enable: bool = True) -> None:
        # Set the timer flag.
        setBit([self.remote_state[13]], kPanasonicAcOnTimerOffset, enable)
        self.remote_state[13] = [self.remote_state[13]][0]
        # Store the time.
        self._setTime(self.remote_state[18:20], mins_since_midnight, True)

    ## Cancel the On Timer.
    ## EXACT translation from IRremoteESP8266 ir_Panasonic.cpp line 603
    def cancelOnTimer(self) -> None:
        self.setOnTimer(0, False)

    ## Check if the On Timer is Enabled.
    ## @return true, the setting is on. false, the setting is off.
    ## EXACT translation from IRremoteESP8266 ir_Panasonic.cpp lines 607-609
    def isOnTimerEnabled(self) -> bool:
        return bool(GETBIT8(self.remote_state[13], kPanasonicAcOnTimerOffset))

    ## Get the Off Timer time value.
    ## @return The time expressed as nr. of minutes past midnight.
    ## EXACT translation from IRremoteESP8266 ir_Panasonic.cpp lines 613-618
    def getOffTimer(self) -> int:
        result = (GETBITS8(self.remote_state[20], 0, 7) << kNibbleSize) | GETBITS8(
            self.remote_state[19], kHighNibble, kNibbleSize
        )
        if result == kPanasonicAcTimeSpecial:
            return 0
        return result

    ## Set/Enable the Off Timer.
    ## @param[in] mins_since_midnight The time as nr. of minutes past midnight.
    ## @param[in] enable Do we enable the timer or not?
    ## EXACT translation from IRremoteESP8266 ir_Panasonic.cpp lines 623-635
    def setOffTimer(self, mins_since_midnight: int, enable: bool = True) -> None:
        # Ensure its on a 10 minute boundary and no overflow.
        corrected = min(mins_since_midnight, kPanasonicAcTimeMax)
        corrected -= corrected % 10
        if mins_since_midnight == kPanasonicAcTimeSpecial:
            corrected = kPanasonicAcTimeSpecial
        # Set the timer flag.
        setBit([self.remote_state[13]], kPanasonicAcOffTimerOffset, enable)
        self.remote_state[13] = [self.remote_state[13]][0]
        # Store the time.
        setBits([self.remote_state[19]], kHighNibble, kNibbleSize, corrected & 0x0F)
        self.remote_state[19] = [self.remote_state[19]][0]
        setBits([self.remote_state[20]], 0, 7, corrected >> kNibbleSize)
        self.remote_state[20] = [self.remote_state[20]][0]

    ## Cancel the Off Timer.
    ## EXACT translation from IRremoteESP8266 ir_Panasonic.cpp line 638
    def cancelOffTimer(self) -> None:
        self.setOffTimer(0, False)

    ## Check if the Off Timer is Enabled.
    ## @return true, the setting is on. false, the setting is off.
    ## EXACT translation from IRremoteESP8266 ir_Panasonic.cpp lines 642-644
    def isOffTimerEnabled(self) -> bool:
        return bool(GETBIT8(self.remote_state[13], kPanasonicAcOffTimerOffset))

    ## Get the Ion (filter) setting of the A/C.
    ## @return true, the setting is on. false, the setting is off.
    ## EXACT translation from IRremoteESP8266 ir_Panasonic.cpp lines 648-656
    def getIon(self) -> bool:
        if self.getModel() == kPanasonicDke:
            return bool(
                GETBIT8(self.remote_state[kPanasonicAcIonFilterByte], kPanasonicAcIonFilterOffset)
            )
        else:
            return False

    ## Set the Ion (filter) setting of the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## EXACT translation from IRremoteESP8266 ir_Panasonic.cpp lines 660-664
    def setIon(self, on: bool) -> None:
        if self.getModel() == kPanasonicDke:
            setBit([self.remote_state[kPanasonicAcIonFilterByte]], kPanasonicAcIonFilterOffset, on)
            self.remote_state[kPanasonicAcIonFilterByte] = [
                self.remote_state[kPanasonicAcIonFilterByte]
            ][0]


## Decode the supplied Panasonic AC message.
## Status: STABLE / Works with real device(s).
## @param[in,out] results Ptr to the data to decode & where to store the result
## @param[in] offset The starting index to use when attempting to decode the
##   raw data. Typically/Defaults to kStartOffset.
## @param[in] nbits The number of data bits to expect.
## @param[in] strict Flag indicating if we should perform strict matching.
## @return True if it can decode it, false if it can't.
## EXACT translation from IRremoteESP8266 ir_Panasonic.cpp lines 865-913
def decodePanasonicAC(
    results, offset: int = 1, nbits: int = kPanasonicAcBits, strict: bool = True
) -> bool:
    """
    Decode a Panasonic A/C IR message.
    EXACT translation from IRremoteESP8266 IRrecv::decodePanasonicAC
    """
    from app.core.ir_protocols.ir_recv import _matchGeneric, kHeader, kFooter

    min_nr_of_messages = 1
    if strict:
        if nbits not in [kPanasonicAcBits, kPanasonicAcShortBits]:
            return False  # Not strictly a PANASONIC_AC message.

    if results.rawlen <= min_nr_of_messages * (2 * nbits + kHeader + kFooter) - 1 + offset:
        return False  # Can't possibly be a valid PANASONIC_AC message.

    # Match Header + Data #1 + Footer
    used = _matchGeneric(
        data_ptr=results.rawbuf[offset:],
        result_bits_ptr=None,
        result_bytes_ptr=results.state,
        use_bits=False,
        remaining=results.rawlen - offset,
        nbits=kPanasonicAcSection1Length * 8,
        hdrmark=kPanasonicHdrMark,
        hdrspace=kPanasonicHdrSpace,
        onemark=kPanasonicBitMark,
        onespace=kPanasonicOneSpace,
        zeromark=kPanasonicBitMark,
        zerospace=kPanasonicZeroSpace,
        footermark=kPanasonicBitMark,
        footerspace=kPanasonicAcSectionGap,
        atleast=False,
        tolerance=kPanasonicAcTolerance,
        excess=kPanasonicAcExcess,
        MSBfirst=False,
    )
    if used == 0:
        return False
    offset += used

    # Match Header + Data #2 + Footer
    if not _matchGeneric(
        data_ptr=results.rawbuf[offset:],
        result_bits_ptr=None,
        result_bytes_ptr=results.state[kPanasonicAcSection1Length:],
        use_bits=False,
        remaining=results.rawlen - offset,
        nbits=nbits - kPanasonicAcSection1Length * 8,
        hdrmark=kPanasonicHdrMark,
        hdrspace=kPanasonicHdrSpace,
        onemark=kPanasonicBitMark,
        onespace=kPanasonicOneSpace,
        zeromark=kPanasonicBitMark,
        zerospace=kPanasonicZeroSpace,
        footermark=kPanasonicBitMark,
        footerspace=kPanasonicAcMessageGap,
        atleast=True,
        tolerance=kPanasonicAcTolerance,
        excess=kPanasonicAcExcess,
        MSBfirst=False,
    ):
        return False

    # Compliance
    if strict:
        # Check the signatures of the section blocks. They start with 0x02& 0x20.
        if (
            results.state[0] != 0x02
            or results.state[1] != 0x20
            or results.state[8] != 0x02
            or results.state[9] != 0x20
        ):
            return False
        if not IRPanasonicAc.validChecksum(results.state, nbits // 8):
            return False

    # Success
    results.bits = nbits
    return True


## Send a Panasonic AC 32/16bit formatted message.
## Status: STABLE / Confirmed working.
## @param[in] data containing the IR command.
## @param[in] nbits Nr. of bits to send. Usually kPanasonicAc32Bits
## @param[in] repeat Nr. of times the message is to be repeated.
## @see https://github.com/crankyoldgit/IRremoteESP8266/issues/1307
## EXACT translation from IRremoteESP8266 ir_Panasonic.cpp lines 923-968
def sendPanasonicAC32(data: int, nbits: int = kPanasonicAc32Bits, repeat: int = 0) -> List[int]:
    """
    Send a Panasonic AC 32/16bit formatted message.
    EXACT translation from IRremoteESP8266 IRsend::sendPanasonicAC32

    Returns timing array instead of transmitting via hardware.
    """
    from app.core.ir_protocols.ir_send import sendGeneric

    # Calculate the section, block, and bit sizes based on the requested bit size
    if nbits > kPanasonicAc32Bits // 2:  # A long message
        section_bits = nbits // kPanasonicAc32Sections
        sections = kPanasonicAc32Sections
        blocks = kPanasonicAc32BlocksPerSection
    else:  # A short message
        section_bits = nbits
        sections = kPanasonicAc32Sections - 1
        blocks = kPanasonicAc32BlocksPerSection + 1

    all_timings = []

    for r in range(repeat + 1):
        for section in range(sections):
            section_data = GETBITS64(data, section_bits * (sections - section - 1), section_bits)

            # Duplicate bytes in the data.
            expanded_data = 0
            for i in range(8):  # sizeof(expanded_data) = 8 bytes
                first_byte = (section_data >> 56) & 0xFF
                for j in range(2):
                    expanded_data = (expanded_data << 8) | first_byte
                section_data = (section_data << 8) & 0xFFFFFFFFFFFFFFFF

            # Two data blocks per section (i.e. 1 + a repeat)
            block_timings = sendGeneric(
                headermark=kPanasonicAc32HdrMark,
                headerspace=kPanasonicAc32HdrSpace,
                onemark=kPanasonicAc32BitMark,
                onespace=kPanasonicAc32OneSpace,
                zeromark=kPanasonicAc32BitMark,
                zerospace=kPanasonicAc32ZeroSpace,
                footermark=0,
                data_uint64=expanded_data,
                nbits=section_bits * 2,
                MSBfirst=False,
            )
            all_timings.extend(block_timings)

            # Section Footer
            footer_timings = sendGeneric(
                headermark=kPanasonicAc32HdrMark,
                headerspace=kPanasonicAc32HdrSpace,
                onemark=0,
                onespace=0,
                zeromark=0,
                zerospace=0,
                footermark=kPanasonicAc32BitMark,
                data_uint64=0,
                nbits=0,  # No data
                MSBfirst=True,
            )
            all_timings.extend(footer_timings)

    return all_timings


## Native representation of a Panasonic 32-bit A/C message.
## EXACT translation from IRremoteESP8266 ir_Panasonic.h lines 189-207
class PanasonicAc32Protocol:
    """
    Native representation of a Panasonic 32-bit A/C message.
    EXACT translation from C++ union/struct
    """

    def __init__(self):
        self.raw = 0

    # Byte 0
    @property
    def SwingH(self) -> int:
        return (self.raw >> 3) & 0x01

    @SwingH.setter
    def SwingH(self, value: bool) -> None:
        if value:
            self.raw |= 1 << 3
        else:
            self.raw &= ~(1 << 3)

    @property
    def SwingV(self) -> int:
        return (self.raw >> 4) & 0x07

    @SwingV.setter
    def SwingV(self, value: int) -> None:
        self.raw = (self.raw & ~(0x07 << 4)) | ((value & 0x07) << 4)

    # Byte 2 (at bit offset 16)
    @property
    def Temp(self) -> int:
        return (self.raw >> 16) & 0x0F

    @Temp.setter
    def Temp(self, value: int) -> None:
        self.raw = (self.raw & ~(0x0F << 16)) | ((value & 0x0F) << 16)

    @property
    def Fan(self) -> int:
        return (self.raw >> 20) & 0x0F

    @Fan.setter
    def Fan(self, value: int) -> None:
        self.raw = (self.raw & ~(0x0F << 20)) | ((value & 0x0F) << 20)

    # Byte 3 (at bit offset 24)
    @property
    def Mode(self) -> int:
        return (self.raw >> 24) & 0x07

    @Mode.setter
    def Mode(self, value: int) -> None:
        self.raw = (self.raw & ~(0x07 << 24)) | ((value & 0x07) << 24)

    @property
    def PowerToggle(self) -> int:
        return (self.raw >> 27) & 0x01

    @PowerToggle.setter
    def PowerToggle(self, value: bool) -> None:
        if value:
            self.raw |= 1 << 27
        else:
            self.raw &= ~(1 << 27)


## Class for handling detailed Panasonic 32bit A/C messages.
## EXACT translation from IRremoteESP8266 IRPanasonicAc32 class
class IRPanasonicAc32:
    """
    Class for handling detailed Panasonic 32bit A/C messages.
    EXACT translation from IRremoteESP8266 IRPanasonicAc32 class
    """

    ## Class constructor
    ## @param[in] pin GPIO to be used when sending.
    ## @param[in] inverted Is the output signal to be inverted?
    ## @param[in] use_modulation Is frequency modulation to be used?
    ## EXACT translation from IRremoteESP8266 ir_Panasonic.cpp lines 1101-1103
    def __init__(self, pin: int = 0, inverted: bool = False, use_modulation: bool = True) -> None:
        self._ = PanasonicAc32Protocol()
        self.stateReset()

    ## Send the current internal state as IR messages.
    ## @param[in] repeat Nr. of times the message will be repeated.
    ## EXACT translation from IRremoteESP8266 ir_Panasonic.cpp lines 1108-1110
    def send(self, repeat: int = 0) -> List[int]:
        return sendPanasonicAC32(self.getRaw(), kPanasonicAc32Bits, repeat)

    ## Get a copy of the internal state/code for this protocol.
    ## @return The code for this protocol based on the current internal state.
    ## EXACT translation from IRremoteESP8266 ir_Panasonic.cpp line 1118
    def getRaw(self) -> int:
        return self._.raw

    ## Set the internal state from a valid code for this protocol.
    ## @param[in] state A valid code for this protocol.
    ## EXACT translation from IRremoteESP8266 ir_Panasonic.cpp line 1122
    def setRaw(self, state: int) -> None:
        self._.raw = state

    ## Reset the state of the remote to a known good state/sequence.
    ## EXACT translation from IRremoteESP8266 ir_Panasonic.cpp line 1125
    def stateReset(self) -> None:
        self.setRaw(kPanasonicAc32KnownGood)

    ## Set the Power Toggle setting of the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## EXACT translation from IRremoteESP8266 ir_Panasonic.cpp line 1129
    def setPowerToggle(self, on: bool) -> None:
        self._.PowerToggle = not on

    ## Get the Power Toggle setting of the A/C.
    ## @return true, the setting is on. false, the setting is off.
    ## EXACT translation from IRremoteESP8266 ir_Panasonic.cpp line 1133
    def getPowerToggle(self) -> bool:
        return not bool(self._.PowerToggle)

    ## Set the desired temperature.
    ## @param[in] degrees The temperature in degrees celsius.
    ## EXACT translation from IRremoteESP8266 ir_Panasonic.cpp lines 1137-1141
    def setTemp(self, degrees: int) -> None:
        temp = max(kPanasonicAcMinTemp, degrees)
        temp = min(kPanasonicAcMaxTemp, temp)
        self._.Temp = temp - (kPanasonicAcMinTemp - 1)

    ## Get the current desired temperature setting.
    ## @return The current setting for temp. in degrees celsius.
    ## EXACT translation from IRremoteESP8266 ir_Panasonic.cpp lines 1145-1147
    def getTemp(self) -> int:
        return self._.Temp + (kPanasonicAcMinTemp - 1)

    ## Get the operating mode setting of the A/C.
    ## @return The current operating mode setting.
    ## EXACT translation from IRremoteESP8266 ir_Panasonic.cpp line 1151
    def getMode(self) -> int:
        return self._.Mode

    ## Set the operating mode of the A/C.
    ## @param[in] mode The desired operating mode.
    ## @note If we get an unexpected mode, default to AUTO.
    ## EXACT translation from IRremoteESP8266 ir_Panasonic.cpp lines 1156-1167
    def setMode(self, mode: int) -> None:
        if mode in [
            kPanasonicAc32Auto,
            kPanasonicAc32Cool,
            kPanasonicAc32Dry,
            kPanasonicAc32Heat,
            kPanasonicAc32Fan,
        ]:
            self._.Mode = mode
        else:
            self._.Mode = kPanasonicAc32Auto

    ## Set the speed of the fan.
    ## @param[in] speed The desired setting.
    ## EXACT translation from IRremoteESP8266 ir_Panasonic.cpp lines 1197-1209
    def setFan(self, speed: int) -> None:
        if speed in [
            kPanasonicAc32FanMin,
            kPanasonicAc32FanLow,
            kPanasonicAc32FanMed,
            kPanasonicAc32FanHigh,
            kPanasonicAc32FanMax,
            kPanasonicAc32FanAuto,
        ]:
            self._.Fan = speed
        else:
            self._.Fan = kPanasonicAc32FanAuto

    ## Get the current fan speed setting.
    ## @return The current fan speed.
    ## EXACT translation from IRremoteESP8266 ir_Panasonic.cpp line 1213
    def getFan(self) -> int:
        return self._.Fan

    ## Get the current horizontal swing setting.
    ## @return The current position it is set to.
    ## EXACT translation from IRremoteESP8266 ir_Panasonic.cpp line 1245
    def getSwingHorizontal(self) -> bool:
        return bool(self._.SwingH)

    ## Control the horizontal swing setting.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## EXACT translation from IRremoteESP8266 ir_Panasonic.cpp line 1249
    def setSwingHorizontal(self, on: bool) -> None:
        self._.SwingH = on

    ## Get the current vertical swing setting.
    ## @return The current position it is set to.
    ## EXACT translation from IRremoteESP8266 ir_Panasonic.cpp line 1253
    def getSwingVertical(self) -> int:
        return self._.SwingV

    ## Control the vertical swing setting.
    ## @param[in] pos The position to set the vertical swing to.
    ## EXACT translation from IRremoteESP8266 ir_Panasonic.cpp lines 1257-1264
    def setSwingVertical(self, pos: int) -> None:
        elevation = pos
        if elevation != kPanasonicAc32SwingVAuto:
            elevation = max(elevation, kPanasonicAcSwingVHighest)
            elevation = min(elevation, kPanasonicAcSwingVLowest)
        self._.SwingV = elevation


## Decode the supplied Panasonic AC 32/16bit message.
## Status: STABLE / Confirmed working.
## @param[in,out] results Ptr to the data to decode & where to store the decode
##   result.
## @param[in] offset The starting index to use when attempting to decode the
##   raw data. Typically/Defaults to kStartOffset.
## @param[in] nbits The number of data bits to expect.
##   Typically: kPanasonicAc32Bits or kPanasonicAc32Bits/2
## @param[in] strict Flag indicating if we should perform strict matching.
## @return A boolean. True if it can decode it, false if it can't.
## @see https://github.com/crankyoldgit/IRremoteESP8266/issues/1307
## @note Protocol has two known configurations:
##   (long)
##   Two sections of identical 32 bit data block pairs. ie. (32+32)+(32+32)=128
##   or
##   (short)
##   A single section of 3 x identical 32 bit data blocks i.e. (32+32+32)=96
## Each data block also has a pair of 8 bits repeated identical bits.
## e.g. (8+8)+(8+8)=32
##
## So each long version really only has 32 unique bits, and the short version
## really only has 16 unique bits.
## EXACT translation from IRremoteESP8266 ir_Panasonic.cpp lines 994-1094
def decodePanasonicAC32(
    results, offset: int = 1, nbits: int = kPanasonicAc32Bits, strict: bool = True
) -> bool:
    """
    Decode a Panasonic AC 32/16bit IR message.
    EXACT translation from IRremoteESP8266 IRrecv::decodePanasonicAC32
    """
    from app.core.ir_protocols.ir_recv import (
        _matchGeneric,
        kHeader,
        kFooter,
        kUseDefTol,
        kMarkExcess,
    )

    if strict and (nbits != kPanasonicAc32Bits and nbits != kPanasonicAc32Bits // 2):
        return False  # Not strictly a valid bit size.

    # Determine if this is a long or a short message we are looking for.
    is_long = nbits > kPanasonicAc32Bits // 2
    if is_long:
        min_length = (
            kPanasonicAc32Sections
            * kPanasonicAc32BlocksPerSection
            * ((2 * nbits) + kHeader + kFooter)
            - 1
            + offset
        )
    else:
        min_length = (
            (kPanasonicAc32BlocksPerSection + 1) * ((4 * nbits) + kHeader) + kFooter - 1 + offset
        )

    if results.rawlen < min_length:
        return False  # Can't possibly be a valid message.

    # Calculate the parameters for the decode based on it's length.
    if is_long:
        sections = kPanasonicAc32Sections
        blocks_per_section = kPanasonicAc32BlocksPerSection
    else:
        sections = kPanasonicAc32Sections - 1
        blocks_per_section = kPanasonicAc32BlocksPerSection + 1

    bits_per_block = nbits // sections

    data = 0
    section_data = 0
    prev_section_data = 0

    # Match all the expected data blocks.
    for block in range(sections * blocks_per_section):
        prev_section_data = section_data
        used = _matchGeneric(
            data_ptr=results.rawbuf[offset:],
            result_bits_ptr=None,
            result_bytes_ptr=None,
            use_bits=True,
            remaining=results.rawlen - offset,
            nbits=bits_per_block * 2,
            hdrmark=kPanasonicAc32HdrMark,
            hdrspace=kPanasonicAc32HdrSpace,
            onemark=kPanasonicAc32BitMark,
            onespace=kPanasonicAc32OneSpace,
            zeromark=kPanasonicAc32BitMark,
            zerospace=kPanasonicAc32ZeroSpace,
            footermark=0,
            footerspace=0,  # No Footer
            atleast=False,
            tolerance=kUseDefTol,
            excess=kMarkExcess,
            MSBfirst=False,
        )
        if used == 0:
            return False

        section_data = results.value  # Get the decoded value
        offset += used

        # Is it the first block of the section?
        if block % blocks_per_section == 0:
            # The protocol repeats each byte twice, so to shrink the code we
            # remove the duplicate bytes in the collected data. We only need to do
            # this for the first block in a section.
            shrunk_data = 0
            data_copy = section_data
            for i in range(0, 8, 2):  # sizeof(data_copy) = 8 bytes
                first_byte = GETBITS64(data_copy, (8 - 1) * 8, 8)
                shrunk_data = (shrunk_data << 8) | first_byte
                # Compliance
                if strict:
                    # Every second byte must be a duplicate of the previous.
                    next_byte = GETBITS64(data_copy, (8 - 2) * 8, 8)
                    if first_byte != next_byte:
                        return False
                data_copy = (data_copy << 16) & 0xFFFFFFFFFFFFFFFF

            # Keep the data from the first of the block in the section.
            data = (data << bits_per_block) | shrunk_data
        else:  # Not the first block in a section.
            # Compliance
            if strict:
                # Compare the data from the blocks in pairs.
                if section_data != prev_section_data:
                    return False
            # Look for the section footer at the end of the blocks.
            if (block + 1) % blocks_per_section == 0:
                used = _matchGeneric(
                    data_ptr=results.rawbuf[offset:],
                    result_bits_ptr=None,
                    result_bytes_ptr=None,
                    use_bits=True,
                    remaining=results.rawlen - offset,
                    nbits=0,
                    hdrmark=kPanasonicAc32HdrMark,
                    hdrspace=kPanasonicAc32HdrSpace,
                    onemark=0,
                    onespace=0,
                    zeromark=0,
                    zerospace=0,
                    footermark=kPanasonicAc32BitMark,
                    footerspace=kPanasonicAc32SectionGap,
                    atleast=True,
                    tolerance=kUseDefTol,
                    excess=kMarkExcess,
                    MSBfirst=False,
                )
                if used == 0:
                    return False
                offset += used

    # Success
    results.value = data
    results.bits = nbits
    results.address = 0
    results.command = 0
    return True
