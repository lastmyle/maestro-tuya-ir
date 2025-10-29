# Copyright 2022 Mateusz Bronk (mbronk)
# Python translation: Direct conversion from C++ with NO optimizations

## @file
## @brief Support for the Gorenje cooker hood IR protocols.
## Direct translation from IRremoteESP8266 ir_Gorenje.cpp and IRremoteESP8266.h
## @see https://techfresh.pl/wp-content/uploads/2017/08/Gorenje-DKF-2600-MWT.pdf
## @see https://github.com/crankyoldgit/IRremoteESP8266/issues/1887

# Supports:
#   Brand: Gorenje,  Model: DKF 2600 MWT Cooker Hood

from typing import List

# Constants - From ir_Gorenje.cpp lines 14-21
kGorenjeMinGap = 100000  # 0.1s
kGorenjeHdrMark = 0
kGorenjeHdrSpace = 0
kGorenjeBitMark = 1300
kGorenjeOneSpace = 5700
kGorenjeZeroSpace = 1700
kGorenjeFreq = 38000  # Hz
kGorenjeTolerance = 7  # %

# Constants - From IRremoteESP8266.h line 1258
kGorenjeBits = 8


## Send a Gorenje Cooker Hood formatted message.
## Status: STABLE / Known working.
## @param[in] data containing the IR command to be sent.
## @param[in] nbits Nr. of bits of the message to send. usually kGorenjeBits
## @param[in] repeat Nr. of times the message is to be repeated.
## Direct translation from IRremoteESP8266 IRsend::sendGorenje (ir_Gorenje.cpp lines 23-36)
def sendGorenje(data: int, nbits: int = kGorenjeBits, repeat: int = 0) -> List[int]:
    """
    Send a Gorenje Cooker Hood formatted message.
    EXACT translation from IRremoteESP8266 IRsend::sendGorenje

    Returns timing array instead of transmitting via hardware.
    """
    # Import here to avoid circular import
    from app.core.ir_protocols.ir_send import sendGenericUint64

    # Lines 31-35
    return sendGenericUint64(
        headermark=kGorenjeHdrMark,
        headerspace=kGorenjeHdrSpace,
        onemark=kGorenjeBitMark,
        onespace=kGorenjeOneSpace,
        zeromark=kGorenjeBitMark,
        zerospace=kGorenjeZeroSpace,
        footermark=kGorenjeBitMark,
        data=data,
        nbits=nbits,
        MSBfirst=True,
    )


## Decode the supplied Gorenje Cooker Hood message.
## Status: STABLE / Known working.
## @param[in,out] results Ptr to the data to decode & where to store the
##   decoded result
## @param[in] offset The starting index to use when attempting to decode the
##   raw data. Typically/Defaults to kStartOffset.
## @param[in] nbits The number of data bits to expect.
## @param[in] strict Flag indicating if we should perform strict matching.
## @param[in] _tolerance The tolerance percentage for matching (default kGorenjeTolerance)
## @return A boolean. True if it can decode it, false if it can't.
## Direct translation from IRremoteESP8266 IRrecv::decodeGorenje (ir_Gorenje.cpp lines 39-71)
def decodeGorenje(
    results,
    offset: int = 1,
    nbits: int = kGorenjeBits,
    strict: bool = True,
    _tolerance: int = kGorenjeTolerance,
) -> bool:
    """
    Decode the supplied Gorenje Cooker Hood message.
    EXACT translation from IRremoteESP8266 IRrecv::decodeGorenje

    This is the ACTUAL C++ decoder function, not a wrapper.
    """
    # Import here to avoid circular imports
    from app.core.ir_protocols.ir_recv import matchGeneric

    # Lines 51-52
    if strict and nbits != kGorenjeBits:
        return False  # We expect Gorenje to be a certain sized message.

    # Line 54
    data = [0]  # Will hold result

    # Lines 55-61
    if not matchGeneric(
        data_ptr=results.rawbuf[offset:],
        result_ptr=data,
        remaining=results.rawlen - offset,
        nbits=nbits,
        hdrmark=kGorenjeHdrMark,
        hdrspace=kGorenjeHdrSpace,
        onemark=kGorenjeBitMark,
        onespace=kGorenjeOneSpace,
        zeromark=kGorenjeBitMark,
        zerospace=kGorenjeZeroSpace,
        footermark=kGorenjeBitMark,
        footerspace=kGorenjeMinGap,
        atleast=True,
        tolerance=_tolerance,
    ):
        return False

    # Matched!
    # Lines 64-68
    results.bits = nbits
    results.value = data[0]
    results.decode_type = "GORENJE"  # decode_type_t::GORENJE
    results.command = 0
    results.address = 0
    return True
