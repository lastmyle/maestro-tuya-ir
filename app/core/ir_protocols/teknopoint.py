# Copyright 2021 David Conran (crankyoldgit)
# Python translation: Direct conversion from C++ with NO optimizations

## @file
## @brief Support for the Teknopoint protocol
## @see https://github.com/crankyoldgit/IRremoteESP8266/issues/1486
## Direct translation from IRremoteESP8266 ir_Teknopoint.cpp

from typing import List

# Supports:
#   Brand: Teknopoint,  Model: Allegro SSA-09H A/C
#   Brand: Teknopoint,  Model: GZ-055B-E1 remote
#   Brand: Teknopoint,  Model: GZ01-BEJ0-000 remote

# Protocol timings (from ir_Teknopoint.cpp lines 15-22)
kTeknopointHdrMark = 3600
kTeknopointBitMark = 477
kTeknopointHdrSpace = 1600
kTeknopointOneSpace = 1200
kTeknopointZeroSpace = 530
kTeknopointFreq = 38000  # Hz. (Guess Only)
kTeknopointExtraTol = 10  # Extra tolerance percentage.

# State length constants (from IRremoteESP8266.h lines 1407-1408)
kTeknopointStateLength = 14
kTeknopointBits = kTeknopointStateLength * 8  # 112 bits

# Default message gap
kDefaultMessageGap = 100000


## Helper function to sum bytes
## EXACT translation from C++ sumBytes utility function
def sumBytes(data: List[int], length: int) -> int:
    """Sum up all the bytes in an array"""
    sum_val = 0
    for i in range(length):
        sum_val += data[i]
    return sum_val & 0xFF


## Send a Teknopoint formatted message.
## Status: BETA / Probably works.
## @param[in] data An array of bytes containing the IR command.
## @param[in] nbytes Nr. of bytes of data in the array.
## @param[in] repeat Nr. of times the message is to be repeated.
## Direct translation from IRremoteESP8266 IRsend::sendTeknopoint (ir_Teknopoint.cpp lines 24-39)
def sendTeknopoint(data: List[int], nbytes: int, repeat: int = 0) -> List[int]:
    """
    Send a Teknopoint formatted message.
    EXACT translation from IRremoteESP8266 IRsend::sendTeknopoint

    Returns timing array instead of transmitting via hardware.
    """
    # Import here to avoid circular import
    from app.core.ir_protocols.ir_send import sendGeneric

    return sendGeneric(
        headermark=kTeknopointHdrMark,
        headerspace=kTeknopointHdrSpace,
        onemark=kTeknopointBitMark,
        onespace=kTeknopointOneSpace,
        zeromark=kTeknopointBitMark,
        zerospace=kTeknopointZeroSpace,
        footermark=kTeknopointBitMark,
        gap=kDefaultMessageGap,
        dataptr=data,
        nbytes=nbytes,
        frequency=kTeknopointFreq,
        MSBfirst=False,
        repeat=repeat,
        dutycycle=50
    )


## Decode the supplied Teknopoint message.
## Status: Alpha / Probably works.
## @param[in,out] results Ptr to the data to decode & where to store the decode
## @param[in] offset The starting index to use when attempting to decode the raw data.
## @param[in] nbits The number of data bits to expect.
## @param[in] strict Flag indicating if we should perform strict matching.
## @return A boolean. True if it can decode it, false if it can't.
## Direct translation from IRremoteESP8266 IRrecv::decodeTeknopoint (ir_Teknopoint.cpp lines 41-76)
def decodeTeknopoint(results, offset: int = 1, nbits: int = kTeknopointBits,
                     strict: bool = True) -> bool:
    """
    Decode a Teknopoint IR message.
    EXACT translation from IRremoteESP8266 IRrecv::decodeTeknopoint

    This is the ACTUAL C++ decoder function, not a wrapper.
    """
    # Import here to avoid circular imports
    from app.core.ir_protocols.ir_recv import (
        kHeader, kFooter, kMarkExcess, _matchGeneric
    )

    if results.rawlen < 2 * nbits + kHeader + kFooter - 1 - offset:
        return False  # Too short a message to match.
    if strict and nbits != kTeknopointBits:
        return False

    if not _matchGeneric(
        data_ptr=results.rawbuf[offset:],
        result_bits_ptr=None,
        result_bytes_ptr=results.state,
        use_bits=False,
        remaining=results.rawlen - offset,
        nbits=nbits,
        hdrmark=kTeknopointHdrMark,
        hdrspace=kTeknopointHdrSpace,
        onemark=kTeknopointBitMark,
        onespace=kTeknopointOneSpace,
        zeromark=kTeknopointBitMark,
        zerospace=kTeknopointZeroSpace,
        footermark=kTeknopointBitMark,
        footerspace=kDefaultMessageGap,
        atleast=True,
        tolerance=25 + kTeknopointExtraTol,
        excess=kMarkExcess,
        MSBfirst=False
    ):
        return False

    # Compliance
    if strict:
        # Is the checksum valid?
        if sumBytes(results.state, kTeknopointStateLength - 1) != results.state[kTeknopointStateLength - 1]:
            return False

    # Success
    # results.decode_type = decode_type_t::TEKNOPOINT  # Would set protocol type in C++
    results.bits = nbits
    return True


# Looking for the IRTeknopoint/IRTeknopointAc class?
# It doesn't exist, it is instead part of the `IRTcl112Ac` class.
# i.e. use `IRTcl112Ac::setModel(tcl_ac_remote_model_t::GZ055BE1);` for
# Teknopoint A/Cs.
# (from ir_Teknopoint.cpp lines 78-81)
