# Copyright 2022 benjy3gg
# Copyright 2022 David Conran (crankyoldgit)
# Python translation: Direct conversion from C++ with NO optimizations

## @file
## @brief Support for Clima-Butler protocol
## Direct translation from IRremoteESP8266 ir_ClimaButler.cpp
## @see https://github.com/crankyoldgit/IRremoteESP8266/issues/1812

from typing import List

# Supports:
#   Brand: Clima-Butler,  Model: AR-715 remote
#   Brand: Clima-Butler,  Model: RCS-SD43UWI A/C

# Constants - Timing values (from ir_ClimaButler.cpp lines 16-22)
kClimaButlerBitMark = 511  # uSeconds
kClimaButlerHdrMark = kClimaButlerBitMark
kClimaButlerHdrSpace = 3492  # uSeconds
kClimaButlerOneSpace = 1540  # uSeconds
kClimaButlerZeroSpace = 548  # uSeconds
kClimaButlerGap = 100000  # kDefaultMessageGap  # uSeconds (A guess.)
kClimaButlerFreq = 38000  # Hz. (Guess.)

# State length constants (from IRremoteESP8266.h)
kClimaButlerBits = 52


## Send a ClimaButler formatted message.
## Status: STABLE / Confirmed working.
## @param[in] data containing the IR command.
## @param[in] nbits Nr. of bits to send. usually kClimaButlerBits
## @param[in] repeat Nr. of times the message is to be repeated.
## Direct translation from IRremoteESP8266 IRsend::sendClimaButler (ir_ClimaButler.cpp lines 24-44)
def sendClimaButler(data: int, nbits: int = kClimaButlerBits, repeat: int = 0) -> List[int]:
    """
    Send a ClimaButler formatted message.
    EXACT translation from IRremoteESP8266 IRsend::sendClimaButler

    Returns timing array instead of transmitting via hardware.
    """
    # Import here to avoid circular import
    from app.core.ir_protocols.ir_send import sendGeneric

    kDutyDefault = 50

    all_timings = []

    for r in range(repeat + 1):
        # Header + Data
        block_timings = sendGeneric(
            headermark=kClimaButlerHdrMark,
            headerspace=kClimaButlerHdrSpace,
            onemark=kClimaButlerBitMark,
            onespace=kClimaButlerOneSpace,
            zeromark=kClimaButlerBitMark,
            zerospace=kClimaButlerZeroSpace,
            footermark=kClimaButlerBitMark,
            gap=kClimaButlerHdrSpace,
            data=data,
            nbits=nbits,
            frequency=kClimaButlerFreq,
            MSBfirst=True,
            repeat=0,
            dutycycle=kDutyDefault,
        )
        all_timings.extend(block_timings)
        # Footer
        all_timings.append(kClimaButlerBitMark)
        all_timings.append(kClimaButlerGap)

    return all_timings


## Decode the supplied ClimaButler message.
## Status: STABLE / Confirmed working.
## @param[in,out] results Ptr to the data to decode & where to store the decode
## @param[in] offset The starting index to use when attempting to decode the
##   raw data. Typically/Defaults to kStartOffset.
## @param[in] nbits The number of data bits to expect.
## @param[in] strict Flag indicating if we should perform strict matching.
## @return A boolean. True if it can decode it, false if it can't.
## Direct translation from IRremoteESP8266 IRrecv::decodeClimaButler (ir_ClimaButler.cpp lines 47-86)
def decodeClimaButler(
    results, offset: int = 1, nbits: int = kClimaButlerBits, strict: bool = True
) -> bool:
    """
    Decode a ClimaButler IR message.
    EXACT translation from IRremoteESP8266 IRrecv::decodeClimaButler

    This is the ACTUAL C++ decoder function, not a wrapper.
    """
    # Import here to avoid circular imports
    from app.core.ir_protocols.ir_recv import (
        kHeader,
        kFooter,
        kMarkExcess,
        _matchGeneric,
        matchMark,
        matchAtLeast,
    )

    if results.rawlen < 2 * nbits + kHeader + 2 * kFooter - offset:
        return False  # Too short a message to match.
    if strict and nbits != kClimaButlerBits:
        return False

    # Header + Data
    used = _matchGeneric(
        data_ptr=results.rawbuf[offset:],
        result_bits_ptr=results.value,
        result_bytes_ptr=None,
        use_bits=True,
        remaining=results.rawlen - offset,
        nbits=nbits,
        hdrmark=kClimaButlerHdrMark,
        hdrspace=kClimaButlerHdrSpace,
        onemark=kClimaButlerBitMark,
        onespace=kClimaButlerOneSpace,
        zeromark=kClimaButlerBitMark,
        zerospace=kClimaButlerZeroSpace,
        footermark=kClimaButlerBitMark,
        footerspace=kClimaButlerHdrSpace,
        atleast=False,
        tolerance=25,
        excess=kMarkExcess,
        MSBfirst=True,
    )
    if not used:
        return False  # Didn't matched.
    offset += used
    # Footer
    if not matchMark(results.rawbuf[offset], kClimaButlerBitMark):
        offset += 1
        return False
    offset += 1
    if results.rawlen <= offset and not matchAtLeast(results.rawbuf[offset], kClimaButlerGap):
        return False

    # Success
    # results.decode_type = CLIMABUTLER  # Would set protocol type in C++
    results.bits = nbits
    results.command = 0
    results.address = 0
    return True
