"""EXACT translation of IRsend::send() and IRrecv::decode() from IRremoteESP8266

This module provides top-level dispatchers for encoding and decoding IR protocols.

Source files:
- IRsend::send() from IRremoteESP8266/src/IRsend.cpp line 1160
- IRrecv::decode() from IRremoteESP8266/src/IRrecv.cpp line 554
"""

from enum import IntEnum
from typing import List, Optional
from app.core.ir_protocols.ir_recv import decode_results


# EXACT translation from IRremoteESP8266.h line 1018
class decode_type_t(IntEnum):
    """Protocol type enumeration - EXACT translation from C++"""

    UNKNOWN = -1
    UNUSED = 0
    RC5 = 1
    RC6 = 2
    NEC = 3
    SONY = 4
    PANASONIC = 5
    JVC = 6
    SAMSUNG = 7
    WHYNTER = 8
    AIWA_RC_T501 = 9
    LG = 10
    SANYO = 11
    MITSUBISHI = 12
    DISH = 13
    SHARP = 14
    COOLIX = 15
    DAIKIN = 16
    DENON = 17
    KELVINATOR = 18
    SHERWOOD = 19
    MITSUBISHI_AC = 20
    RCMM = 21
    SANYO_LC7461 = 22
    RC5X = 23
    GREE = 24
    PRONTO = 25
    NEC_LIKE = 26
    ARGO = 27
    TROTEC = 28
    NIKAI = 29
    RAW = 30
    GLOBALCACHE = 31
    TOSHIBA_AC = 32
    FUJITSU_AC = 33
    MIDEA = 34
    MAGIQUEST = 35
    LASERTAG = 36
    CARRIER_AC = 37
    HAIER_AC = 38
    MITSUBISHI2 = 39
    HITACHI_AC = 40
    HITACHI_AC1 = 41
    HITACHI_AC2 = 42
    GICABLE = 43
    HAIER_AC_YRW02 = 44
    WHIRLPOOL_AC = 45
    SAMSUNG_AC = 46
    LUTRON = 47
    ELECTRA_AC = 48
    PANASONIC_AC = 49
    PIONEER = 50
    LG2 = 51
    MWM = 52
    DAIKIN2 = 53
    VESTEL_AC = 54
    TECO = 55
    SAMSUNG36 = 56
    TCL112AC = 57
    LEGOPF = 58
    MITSUBISHI_HEAVY_88 = 59
    MITSUBISHI_HEAVY_152 = 60
    DAIKIN216 = 61
    SHARP_AC = 62
    GOODWEATHER = 63
    INAX = 64
    DAIKIN160 = 65
    NEOCLIMA = 66
    DAIKIN176 = 67
    DAIKIN128 = 68
    AMCOR = 69
    DAIKIN152 = 70
    MITSUBISHI136 = 71
    MITSUBISHI112 = 72
    HITACHI_AC424 = 73
    SONY_38K = 74
    EPSON = 75
    SYMPHONY = 76
    HITACHI_AC3 = 77
    DAIKIN64 = 78
    AIRWELL = 79
    DELONGHI_AC = 80
    DOSHISHA = 81
    MULTIBRACKETS = 82
    CARRIER_AC40 = 83
    CARRIER_AC64 = 84
    HITACHI_AC344 = 85
    CORONA_AC = 86
    MIDEA24 = 87
    ZEPEAL = 88
    SANYO_AC = 89
    VOLTAS = 90
    METZ = 91
    TRANSCOLD = 92
    TECHNIBEL_AC = 93
    MIRAGE = 94
    ELITESCREENS = 95
    PANASONIC_AC32 = 96
    MILESTAG2 = 97
    ECOCLIM = 98
    XMP = 99
    TRUMA = 100
    HAIER_AC176 = 101
    TEKNOPOINT = 102
    KELON = 103
    TROTEC_3550 = 104
    SANYO_AC88 = 105
    BOSE = 106
    ARRIS = 107
    RHOSS = 108
    AIRTON = 109
    COOLIX48 = 110
    HITACHI_AC264 = 111
    KELON168 = 112
    HITACHI_AC296 = 113
    DAIKIN200 = 114
    HAIER_AC160 = 115
    CARRIER_AC128 = 116
    TOTO = 117
    CLIMABUTLER = 118
    TCL96AC = 119
    BOSCH144 = 120
    SANYO_AC152 = 121
    DAIKIN312 = 122
    GORENJE = 123
    WOWWEE = 124
    CARRIER_AC84 = 125
    YORK = 126
    BLUESTARHEAVY = 127


# EXACT translation from IRsend.cpp line 1160
def send(
    protocol_type: decode_type_t, state: List[int], nbytes: int, repeat: int = 0
) -> Optional[List[int]]:
    """
    EXACT translation of IRsend::send() from IRsend.cpp

    Top-level dispatcher that routes to protocol-specific send functions.

    Args:
        protocol_type: Protocol identifier from decode_type_t enum
        state: Byte array containing the IR command state
        nbytes: Number of bytes in state array
        repeat: Number of times to repeat the message

    Returns:
        List of IR timing values (microseconds), or None if protocol not supported

    Source: IRremoteESP8266/src/IRsend.cpp line 1160
    """
    # Fujitsu AC
    if protocol_type == decode_type_t.FUJITSU_AC:
        from app.core.ir_protocols.fujitsu import sendFujitsuAC

        return sendFujitsuAC(state, nbytes, repeat)

    # Gree
    elif protocol_type == decode_type_t.GREE:
        from app.core.ir_protocols.gree import sendGree

        return sendGree(state, nbytes, repeat)

    # Daikin variants (10 total)
    elif protocol_type == decode_type_t.DAIKIN:
        from app.core.ir_protocols.daikin import sendDaikin

        return sendDaikin(state, nbytes, repeat)
    elif protocol_type == decode_type_t.DAIKIN2:
        from app.core.ir_protocols.daikin import sendDaikin2

        return sendDaikin2(state, nbytes, repeat)
    elif protocol_type == decode_type_t.DAIKIN216:
        from app.core.ir_protocols.daikin import sendDaikin216

        return sendDaikin216(state, nbytes, repeat)
    elif protocol_type == decode_type_t.DAIKIN160:
        from app.core.ir_protocols.daikin import sendDaikin160

        return sendDaikin160(state, nbytes, repeat)
    elif protocol_type == decode_type_t.DAIKIN176:
        from app.core.ir_protocols.daikin import sendDaikin176

        return sendDaikin176(state, nbytes, repeat)
    elif protocol_type == decode_type_t.DAIKIN128:
        from app.core.ir_protocols.daikin import sendDaikin128

        return sendDaikin128(state, nbytes, repeat)
    elif protocol_type == decode_type_t.DAIKIN152:
        from app.core.ir_protocols.daikin import sendDaikin152

        return sendDaikin152(state, nbytes, repeat)
    elif protocol_type == decode_type_t.DAIKIN64:
        from app.core.ir_protocols.daikin import sendDaikin64

        # Daikin64 takes a 64-bit integer, not byte array
        if nbytes >= 8:
            data64 = int.from_bytes(state[:8], byteorder="little")
            return sendDaikin64(data64, repeat)
        return None
    elif protocol_type == decode_type_t.DAIKIN200:
        from app.core.ir_protocols.daikin import sendDaikin200

        return sendDaikin200(state, nbytes, repeat)
    elif protocol_type == decode_type_t.DAIKIN312:
        from app.core.ir_protocols.daikin import sendDaikin312

        return sendDaikin312(state, nbytes, repeat)

    # Mitsubishi variants (5 total)
    elif protocol_type == decode_type_t.MITSUBISHI_AC:
        from app.core.ir_protocols.mitsubishi import sendMitsubishiAC

        return sendMitsubishiAC(state, nbytes, repeat)
    elif protocol_type == decode_type_t.MITSUBISHI136:
        from app.core.ir_protocols.mitsubishi import sendMitsubishi136

        return sendMitsubishi136(state, nbytes, repeat)
    elif protocol_type == decode_type_t.MITSUBISHI112:
        from app.core.ir_protocols.mitsubishi import sendMitsubishi112

        return sendMitsubishi112(state, nbytes, repeat)
    elif protocol_type == decode_type_t.MITSUBISHI_HEAVY_88:
        from app.core.ir_protocols.mitsubishi import sendMitsubishiHeavy88

        return sendMitsubishiHeavy88(state, nbytes, repeat)
    elif protocol_type == decode_type_t.MITSUBISHI_HEAVY_152:
        from app.core.ir_protocols.mitsubishi import sendMitsubishiHeavy152

        return sendMitsubishiHeavy152(state, nbytes, repeat)

    # Hitachi variants (7 send functions for 8 variants)
    elif protocol_type == decode_type_t.HITACHI_AC:
        from app.core.ir_protocols.hitachi import sendHitachiAC

        return sendHitachiAC(state, nbytes, repeat)
    elif protocol_type == decode_type_t.HITACHI_AC1:
        from app.core.ir_protocols.hitachi import sendHitachiAC1

        return sendHitachiAC1(state, nbytes, repeat)
    elif protocol_type == decode_type_t.HITACHI_AC424:
        from app.core.ir_protocols.hitachi import sendHitachiAc424

        return sendHitachiAc424(state, nbytes, repeat)
    elif protocol_type == decode_type_t.HITACHI_AC2:
        # HITACHI_AC2 is an alias for HITACHI_AC424
        from app.core.ir_protocols.hitachi import sendHitachiAc424

        return sendHitachiAc424(state, nbytes, repeat)
    elif protocol_type == decode_type_t.HITACHI_AC344:
        from app.core.ir_protocols.hitachi import sendHitachiAc344

        return sendHitachiAc344(state, nbytes, repeat)
    elif protocol_type == decode_type_t.HITACHI_AC264:
        from app.core.ir_protocols.hitachi import sendHitachiAc264

        return sendHitachiAc264(state, nbytes, repeat)
    elif protocol_type == decode_type_t.HITACHI_AC296:
        from app.core.ir_protocols.hitachi import sendHitachiAc296

        return sendHitachiAc296(state, nbytes, repeat)
    elif protocol_type == decode_type_t.HITACHI_AC3:
        from app.core.ir_protocols.hitachi import sendHitachiAc3

        return sendHitachiAc3(state, nbytes, repeat)

    # Panasonic variants (3 total)
    elif protocol_type == decode_type_t.PANASONIC:
        from app.core.ir_protocols.panasonic import sendPanasonic64

        # Panasonic TV protocol uses 64-bit encoding
        if nbytes >= 6:
            # Extract manufacturer (2 bytes), device (1 byte), subdevice (1 byte), function (1 byte)
            manufacturer = (state[1] << 8) | state[0]
            data = (
                (state[4] << 24)
                | (state[3] << 16)
                | (state[2] << 8)
                | (state[5] if nbytes > 5 else 0)
            )
            return sendPanasonic64(manufacturer, data, repeat)
        return None
    elif protocol_type == decode_type_t.PANASONIC_AC:
        from app.core.ir_protocols.panasonic import sendPanasonicAC

        return sendPanasonicAC(state, nbytes, repeat)
    elif protocol_type == decode_type_t.PANASONIC_AC32:
        from app.core.ir_protocols.panasonic import sendPanasonicAC32

        return sendPanasonicAC32(state, nbytes, repeat)

    # Samsung variants (3 total)
    elif protocol_type == decode_type_t.SAMSUNG:
        from app.core.ir_protocols.samsung import sendSAMSUNG

        # Samsung TV protocol uses 32-bit encoding
        if nbytes >= 4:
            data = (state[3] << 24) | (state[2] << 16) | (state[1] << 8) | state[0]
            return sendSAMSUNG(data, 32, repeat)
        return None
    elif protocol_type == decode_type_t.SAMSUNG36:
        from app.core.ir_protocols.samsung import sendSamsung36

        # Samsung36 uses special encoding with 2 values
        if nbytes >= 5:
            address = (state[1] << 8) | state[0]
            command = (state[4] << 16) | (state[3] << 8) | state[2]
            return sendSamsung36(address, command, repeat)
        return None
    elif protocol_type == decode_type_t.SAMSUNG_AC:
        from app.core.ir_protocols.samsung import sendSamsungAC

        return sendSamsungAC(state, nbytes, repeat)

    # LG variants (2 total)
    elif protocol_type == decode_type_t.LG:
        from app.core.ir_protocols.lg import sendLG

        # LG uses 28 or 32-bit encoding
        if nbytes >= 4:
            data = (state[3] << 24) | (state[2] << 16) | (state[1] << 8) | state[0]
            bits = 28 if nbytes == 4 else 32
            return sendLG(data, bits, repeat)
        return None
    elif protocol_type == decode_type_t.LG2:
        from app.core.ir_protocols.lg import sendLG2

        # LG2 uses 28-bit encoding
        if nbytes >= 4:
            data = (state[3] << 24) | (state[2] << 16) | (state[1] << 8) | state[0]
            return sendLG2(data, 28, repeat)
        return None

    # Carrier variants (5 total)
    elif protocol_type == decode_type_t.CARRIER_AC:
        from app.core.ir_protocols.carrier import sendCarrierAC

        # Carrier AC uses 32-bit encoding
        if nbytes >= 4:
            data = (state[3] << 24) | (state[2] << 16) | (state[1] << 8) | state[0]
            return sendCarrierAC(data, repeat)
        return None
    elif protocol_type == decode_type_t.CARRIER_AC40:
        from app.core.ir_protocols.carrier import sendCarrierAC40

        # Carrier AC40 uses 40-bit encoding
        if nbytes >= 5:
            data = (
                (state[4] << 32) | (state[3] << 24) | (state[2] << 16) | (state[1] << 8) | state[0]
            )
            return sendCarrierAC40(data, repeat)
        return None
    elif protocol_type == decode_type_t.CARRIER_AC64:
        from app.core.ir_protocols.carrier import sendCarrierAC64

        return sendCarrierAC64(state, nbytes, repeat)
    elif protocol_type == decode_type_t.CARRIER_AC84:
        from app.core.ir_protocols.carrier import sendCarrierAC84

        return sendCarrierAC84(state, nbytes, repeat)
    elif protocol_type == decode_type_t.CARRIER_AC128:
        from app.core.ir_protocols.carrier import sendCarrierAC128

        return sendCarrierAC128(state, nbytes, repeat)

    # Protocol not supported
    return None


# EXACT translation from IRrecv.cpp line 554
def decode(results: decode_results, max_skip: int = 0, noise_floor: int = 0) -> bool:
    """
    EXACT translation of IRrecv::decode() from IRrecv.cpp

    Top-level dispatcher that tries all protocols sequentially until one matches.

    This function attempts to decode an IR signal by trying each protocol decoder
    in sequence. The order matters - some protocols must be tried before others
    to avoid false positives (see comments in C++ source).

    Args:
        results: decode_results object with rawbuf containing IR timings
        max_skip: Maximum number of leading timing pairs to skip
        noise_floor: Noise threshold (not implemented in Python version yet)

    Returns:
        True if any protocol successfully decoded the signal, False otherwise

    Source: IRremoteESP8266/src/IRrecv.cpp line 554

    Note: In C++, this function tries 100+ protocols. Currently we only have
    Fujitsu and Gree imported, so we only try those. More will be added as
    we import the protocol drivers.
    """
    # Reset any previously partially processed results
    results.decode_type = decode_type_t.UNKNOWN
    results.bits = 0
    results.value = 0
    results.address = 0
    results.command = 0
    results.repeat = False

    # Keep looking for protocols until we've run out of entries to skip or we
    # find a valid protocol message.
    # NOTE: C++ uses kStartOffset=1 for hardware captures with leading noise.
    # But Tuya codes are clean timing arrays, so we start at 0.
    kStartOffset = 0

    for offset in range(kStartOffset, (max_skip * 2) + kStartOffset + 1, 2):
        # The C++ version tries protocols in a specific order to avoid false positives
        # Order is CRITICAL - some protocols must be tried before others

        # Fujitsu A/C needs to precede Panasonic and Denon as it has a short
        # message which looks exactly the same as a Panasonic/Denon message.
        # DECODE_FUJITSU_AC
        from app.core.ir_protocols.ir_recv import decodeFujitsuAC, kFujitsuAcBits

        if decodeFujitsuAC(results, offset, kFujitsuAcBits, strict=False):
            results.decode_type = decode_type_t.FUJITSU_AC
            return True

        # DECODE_CARRIER_AC (all variants)
        from app.core.ir_protocols.carrier import (
            decodeCarrierAC,
            decodeCarrierAC40,
            decodeCarrierAC64,
            decodeCarrierAC84,
            decodeCarrierAC128,
        )

        if decodeCarrierAC128(results, offset):
            results.decode_type = decode_type_t.CARRIER_AC128
            return True
        if decodeCarrierAC84(results, offset):
            results.decode_type = decode_type_t.CARRIER_AC84
            return True
        if decodeCarrierAC64(results, offset):
            results.decode_type = decode_type_t.CARRIER_AC64
            return True
        if decodeCarrierAC40(results, offset):
            results.decode_type = decode_type_t.CARRIER_AC40
            return True
        if decodeCarrierAC(results, offset):
            results.decode_type = decode_type_t.CARRIER_AC
            return True

        # DECODE_HITACHI_AC (all variants - order matters!)
        from app.core.ir_protocols.hitachi import (
            decodeHitachiAC,
            decodeHitachiAc424,
            decodeHitachiAc296,
            decodeHitachiAc3,
        )

        # HitachiAC424 must come before HitachiAC (it's more specific)
        if decodeHitachiAc424(results, offset):
            results.decode_type = decode_type_t.HITACHI_AC424
            return True
        if decodeHitachiAc296(results, offset):
            results.decode_type = decode_type_t.HITACHI_AC296
            return True
        if decodeHitachiAc3(results, offset):
            results.decode_type = decode_type_t.HITACHI_AC3
            return True
        # HitachiAC decoder handles AC, AC1, AC264, AC344 (multi-format)
        if decodeHitachiAC(results, offset):
            # decode_type is set by the decoder based on bits detected
            # Could be HITACHI_AC, HITACHI_AC1, HITACHI_AC264, or HITACHI_AC344
            return True

        # DECODE_SAMSUNG_AC
        from app.core.ir_protocols.samsung import decodeSamsungAC, decodeSamsung36, decodeSAMSUNG

        if decodeSamsungAC(results, offset):
            results.decode_type = decode_type_t.SAMSUNG_AC
            return True
        if decodeSamsung36(results, offset):
            results.decode_type = decode_type_t.SAMSUNG36
            return True
        if decodeSAMSUNG(results, offset):
            results.decode_type = decode_type_t.SAMSUNG
            return True

        # DECODE_DAIKIN (all variants - order matters!)
        from app.core.ir_protocols.daikin import (
            decodeDaikin312,
            decodeDaikin200,
            decodeDaikin216,
            decodeDaikin176,
            decodeDaikin160,
            decodeDaikin152,
            decodeDaikin128,
            decodeDaikin64,
            decodeDaikin2,
            decodeDaikin,
        )

        if decodeDaikin312(results, offset):
            results.decode_type = decode_type_t.DAIKIN312
            return True
        if decodeDaikin200(results, offset):
            results.decode_type = decode_type_t.DAIKIN200
            return True
        if decodeDaikin216(results, offset):
            results.decode_type = decode_type_t.DAIKIN216
            return True
        if decodeDaikin176(results, offset):
            results.decode_type = decode_type_t.DAIKIN176
            return True
        if decodeDaikin160(results, offset):
            results.decode_type = decode_type_t.DAIKIN160
            return True
        if decodeDaikin152(results, offset):
            results.decode_type = decode_type_t.DAIKIN152
            return True
        if decodeDaikin128(results, offset):
            results.decode_type = decode_type_t.DAIKIN128
            return True
        if decodeDaikin64(results, offset):
            results.decode_type = decode_type_t.DAIKIN64
            return True
        if decodeDaikin2(results, offset):
            results.decode_type = decode_type_t.DAIKIN2
            return True
        if decodeDaikin(results, offset):
            results.decode_type = decode_type_t.DAIKIN
            return True

        # DECODE_PANASONIC_AC (must come before PANASONIC to avoid conflicts)
        from app.core.ir_protocols.panasonic import (
            decodePanasonicAC,
            decodePanasonicAC32,
            decodePanasonic,
        )

        if decodePanasonicAC(results, offset, strict=False):
            results.decode_type = decode_type_t.PANASONIC_AC
            return True
        if decodePanasonicAC32(results, offset, strict=False):
            results.decode_type = decode_type_t.PANASONIC_AC32
            return True
        if decodePanasonic(results, offset, strict=False):
            results.decode_type = decode_type_t.PANASONIC
            return True

        # DECODE_LG (handles both LG and LG2)
        from app.core.ir_protocols.lg import decodeLG

        if decodeLG(results, offset):
            # decodeLG sets decode_type to either LG or LG2
            return True

        # DECODE_MITSUBISHI (all variants)
        from app.core.ir_protocols.mitsubishi import (
            decodeMitsubishiHeavy,
            decodeMitsubishiAC,
            decodeMitsubishi136,
            decodeMitsubishi112,
        )

        # MitsubishiHeavy handles both 88 and 152-bit variants
        if decodeMitsubishiHeavy(results, offset):
            # decode_type is set by decoder (MITSUBISHI_HEAVY_88 or MITSUBISHI_HEAVY_152)
            return True
        if decodeMitsubishiAC(results, offset):
            results.decode_type = decode_type_t.MITSUBISHI_AC
            return True
        if decodeMitsubishi136(results, offset):
            results.decode_type = decode_type_t.MITSUBISHI136
            return True
        # Mitsubishi112 also handles TCL112AC (sets decode_type appropriately)
        if decodeMitsubishi112(results, offset):
            # decode_type is set by decoder (MITSUBISHI112 or TCL112AC)
            return True

        # Gree based-devices use a similar code to Kelvinator ones, to avoid false
        # matches this needs to happen after decodeKelvinator() (not yet imported).
        # DECODE_GREE
        from app.core.ir_protocols.gree import decodeGree

        if decodeGree(results, offset):
            results.decode_type = decode_type_t.GREE
            return True

        # More protocols will be added here as we import them
        # Current count: 36 variants from 9 manufacturers

    # Nothing matched
    return False
