# Copyright 2009 Ken Shirriff
# Copyright 2017 David Conran
# Python translation: Direct conversion from C++ with NO optimizations

## @file
## @brief Nikai
## @see https://github.com/crankyoldgit/IRremoteESP8266/issues/309
## Direct translation from IRremoteESP8266 ir_Nikai.cpp

# Supports:
#   Brand: Nikai,  Model: Unknown LCD TV

from typing import List

# Constants (from ir_Nikai.cpp lines 17-29)
kNikaiTick = 500
kNikaiHdrMarkTicks = 8
kNikaiHdrMark = kNikaiHdrMarkTicks * kNikaiTick
kNikaiHdrSpaceTicks = 8
kNikaiHdrSpace = kNikaiHdrSpaceTicks * kNikaiTick
kNikaiBitMarkTicks = 1
kNikaiBitMark = kNikaiBitMarkTicks * kNikaiTick
kNikaiOneSpaceTicks = 2
kNikaiOneSpace = kNikaiOneSpaceTicks * kNikaiTick
kNikaiZeroSpaceTicks = 4
kNikaiZeroSpace = kNikaiZeroSpaceTicks * kNikaiTick
kNikaiMinGapTicks = 17
kNikaiMinGap = kNikaiMinGapTicks * kNikaiTick

# Constants from IRremoteESP8266.h line 1341
kNikaiBits = 24


## Send a Nikai formatted message.
## Status: STABLE / Working.
## @param[in] data The message to be sent.
## @param[in] nbits The number of bits of message to be sent.
## @param[in] repeat The number of times the command is to be repeated.
## Direct translation from IRremoteESP8266 IRsend::sendNikai (ir_Nikai.cpp lines 37-41)
def sendNikai(data: int, nbits: int, repeat: int = 0) -> List[int]:
    """
    Send a Nikai formatted message.
    EXACT translation from IRremoteESP8266 IRsend::sendNikai

    Returns timing array instead of transmitting via hardware.
    """
    # Import here to avoid circular import
    from app.core.ir_protocols.ir_send import sendGenericUint64

    # Direct translation from ir_Nikai.cpp lines 38-40
    return sendGenericUint64(
        headermark=kNikaiHdrMark,
        headerspace=kNikaiHdrSpace,
        onemark=kNikaiBitMark,
        onespace=kNikaiOneSpace,
        zeromark=kNikaiBitMark,
        zerospace=kNikaiZeroSpace,
        footermark=kNikaiBitMark,
        gap=kNikaiMinGap,
        data=data,
        nbits=nbits,
        frequency=38,
        MSBfirst=True,
        repeat=repeat,
        dutycycle=33,
    )


## Decode the supplied Nikai message.
## Status: STABLE / Working.
## @param[in,out] results Ptr to the data to decode & where to store the result
## @param[in] offset The starting index to use when attempting to decode the
##   raw data. Typically/Defaults to kStartOffset.
## @param[in] nbits The number of data bits to expect.
## @param[in] strict Flag indicating if we should perform strict matching.
## Direct translation from IRremoteESP8266 IRrecv::decodeNikai (ir_Nikai.cpp lines 52-73)
def decodeNikai(results, offset: int = 1, nbits: int = kNikaiBits, strict: bool = True) -> bool:
    """
    Decode a Nikai IR message.
    EXACT translation from IRremoteESP8266 IRrecv::decodeNikai

    This is the ACTUAL C++ decoder function, not a wrapper.
    """
    # Import here to avoid circular imports
    from app.core.ir_protocols.ir_recv import matchGeneric

    # Direct translation from ir_Nikai.cpp lines 54-55
    if strict and nbits != kNikaiBits:
        return False  # We expect Nikai to be a certain sized message.

    data = [0]  # uint64_t data = 0;

    # Match Header + Data + Footer (ir_Nikai.cpp lines 60-65)
    if not matchGeneric(
        data_ptr=results.rawbuf[offset:],
        result_ptr=data,
        remaining=results.rawlen - offset,
        nbits=nbits,
        hdrmark=kNikaiHdrMark,
        hdrspace=kNikaiHdrSpace,
        onemark=kNikaiBitMark,
        onespace=kNikaiOneSpace,
        zeromark=kNikaiBitMark,
        zerospace=kNikaiZeroSpace,
        footermark=kNikaiBitMark,
        footerspace=kNikaiMinGap,
        atleast=True,
        tolerance=25,
    ):
        return False

    # Success (ir_Nikai.cpp lines 66-72)
    results.bits = nbits
    results.value = data[0]
    # results.decode_type = NIKAI  # Would set protocol type in C++
    results.command = 0
    results.address = 0
    return True
