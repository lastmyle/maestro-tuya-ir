# Copyright 2024 Harsh Bhosale (harshbhosale01)
# Python translation: Direct conversion from C++ with NO optimizations

## @file
## @brief Support for BluestarHeavy protocol
## Direct translation from IRremoteESP8266 ir_BluestarHeavy.cpp

from typing import List

# Supports:
# Brand: Bluestar,  Model: D716LXM0535A2400313 (Remote)

# Constants - Timing values (from ir_BluestarHeavy.cpp lines 12-18)
kBluestarHeavyHdrMark = 4912
kBluestarHeavyBitMark = 465
kBluestarHeavyHdrSpace = 5058
kBluestarHeavyOneSpace = 572
kBluestarHeavyZeroSpace = 1548
kBluestarHeavyFreq = 38000
kBluestarHeavyOverhead = 3

# State length constants (from IRremoteESP8266.h)
kBluestarHeavyStateLength = 13
kBluestarHeavyBits = kBluestarHeavyStateLength * 8  # 104 bits

# Default message gap (from IRremoteESP8266.h - standard value)
kDefaultMessageGap = 100000


## Send a BluestarHeavy formatted message.
## Status: BETA / Tested.
## @param[in] data An array of bytes containing the IR command.
##                 It is assumed to be in MSB order for this code.
## e.g.
## @code
## data = [0x2A,0x00,0x20,0xD0,0x05,0xA0,0x05,0xA0,0x00,0x80,0xBA,0x02,0x23]
## @endcode
## @param[in] nbytes Nr. of bytes of data in the array.
## @param[in] repeat Nr. of times the message is to be repeated.
## Direct translation from IRremoteESP8266 IRsend::sendBluestarHeavy (ir_BluestarHeavy.cpp lines 21-40)
def sendBluestarHeavy(data: List[int], nbytes: int, repeat: int = 0) -> List[int]:
    """
    Send a BluestarHeavy formatted message.
    EXACT translation from IRremoteESP8266 IRsend::sendBluestarHeavy

    Returns timing array instead of transmitting via hardware.
    """
    # Import here to avoid circular import
    from app.core.ir_protocols.ir_send import sendGeneric

    kDutyDefault = 50

    return sendGeneric(
        headermark=kBluestarHeavyHdrMark,
        headerspace=kBluestarHeavyHdrSpace,
        onemark=kBluestarHeavyBitMark,
        onespace=kBluestarHeavyOneSpace,
        zeromark=kBluestarHeavyBitMark,
        zerospace=kBluestarHeavyZeroSpace,
        footermark=kBluestarHeavyHdrMark,
        gap=kDefaultMessageGap,
        dataptr=data,
        nbytes=nbytes,  # Bytes
        frequency=kBluestarHeavyFreq,
        MSBfirst=True,
        repeat=repeat,
        dutycycle=kDutyDefault
    )


## Decode the supplied BluestarHeavy message.
## Status: BETA / Tested.
## @param[in,out] results Ptr to the data to decode & where to store the decode
## @param[in] offset The starting index to use when attempting to decode the
##   raw data. Typically/Defaults to kStartOffset.
## @param[in] nbits The number of data bits to expect.
## @param[in] strict Flag indicating if we should perform strict matching.
## @return A boolean. True if it can decode it, false if it can't.
## Direct translation from IRremoteESP8266 IRrecv::decodeBluestarHeavy (ir_BluestarHeavy.cpp lines 43-72)
def decodeBluestarHeavy(results, offset: int = 1, nbits: int = kBluestarHeavyBits,
                        strict: bool = True) -> bool:
    """
    Decode a BluestarHeavy IR message.
    EXACT translation from IRremoteESP8266 IRrecv::decodeBluestarHeavy

    This is the ACTUAL C++ decoder function, not a wrapper.
    """
    # Import here to avoid circular imports
    from app.core.ir_protocols.ir_recv import kMarkExcess, _matchGeneric

    if strict and nbits != kBluestarHeavyBits:
        return False

    used = 0

    used = _matchGeneric(
        data_ptr=results.rawbuf[offset:],
        result_bits_ptr=None,
        result_bytes_ptr=results.state,
        use_bits=False,
        remaining=results.rawlen - offset,
        nbits=nbits,
        hdrmark=kBluestarHeavyHdrMark,
        hdrspace=kBluestarHeavyHdrSpace,
        onemark=kBluestarHeavyBitMark,
        onespace=kBluestarHeavyOneSpace,
        zeromark=kBluestarHeavyBitMark,
        zerospace=kBluestarHeavyZeroSpace,
        footermark=kBluestarHeavyHdrMark,
        footerspace=kDefaultMessageGap,
        atleast=False,
        tolerance=25,
        excess=kMarkExcess,
        MSBfirst=True
    )
    if used == 0:
        return False  # We failed to find any data.

    # Success
    # results.decode_type = BLUESTARHEAVY  # Would set protocol type in C++
    results.bits = nbits
    return True
