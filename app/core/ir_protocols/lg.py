# Copyright 2015 Darryl Smith
# Copyright 2015 cheaplin
# Copyright 2017-2021 David Conran
# Python translation: Direct conversion from C++ with NO optimizations

## @file
## @brief Support for LG protocols.
## LG decode originally added by Darryl Smith (based on the JVC protocol)
## LG send originally added by https://github.com/chaeplin
## @see https://github.com/arendst/Tasmota/blob/54c2eb283a02e4287640a4595e506bc6eadbd7f2/sonoff/xdrv_05_irremote.ino#L327-438
## @see https://github.com/crankyoldgit/IRremoteESP8266/issues/1513
## Direct translation from IRremoteESP8266 ir_LG.cpp and ir_LG.h

from typing import List

# Supports:
#   Brand: LG,  Model: 6711A20083V remote (LG - LG6711A20083V)
#   Brand: LG,  Model: TS-H122ERM1 remote (LG - LG6711A20083V)
#   Brand: LG,  Model: AKB74395308 remote (LG2)
#   Brand: LG,  Model: S4-W12JA3AA A/C (LG2)
#   Brand: LG,  Model: AKB75215403 remote (LG2)
#   Brand: LG,  Model: AKB74955603 remote (LG2 - AKB74955603)
#   Brand: LG,  Model: A4UW30GFA2 A/C (LG2 - AKB74955603 & AKB73757604)
#   Brand: LG,  Model: AMNW09GSJA0 A/C (LG2 - AKB74955603)
#   Brand: LG,  Model: AMNW24GTPA1 A/C (LG2 - AKB73757604)
#   Brand: LG,  Model: AKB73757604 remote (LG2 - AKB73757604)
#   Brand: LG,  Model: AKB73315611 remote (LG2 - AKB74955603)
#   Brand: LG,  Model: MS05SQ NW0 A/C (LG2 - AKB74955603)
#   Brand: General Electric,  Model: AG1BH09AW101 A/C (LG - GE6711AR2853M)
#   Brand: General Electric,  Model: 6711AR2853M Remote (LG - GE6711AR2853M)

# Constants
# EXACT translation from IRremoteESP8266 ir_LG.cpp:30-48
# Common timings
kLgBitMark = 550  # uSeconds.
kLgOneSpace = 1600  # uSeconds.
kLgZeroSpace = 550  # uSeconds.
kLgRptSpace = 2250  # uSeconds.
kLgMinGap = 39750  # uSeconds.
kLgMinMessageLength = 108050  # uSeconds.
# LG (28 Bit)
kLgHdrMark = 8500  # uSeconds.
kLgHdrSpace = 4250  # uSeconds.
# LG (32 Bit)
kLg32HdrMark = 4500  # uSeconds.
kLg32HdrSpace = 4450  # uSeconds.
kLg32RptHdrMark = 8950  # uSeconds.
# LG2 (28 Bit)
kLg2HdrMark = 3200  # uSeconds.
kLg2HdrSpace = 9900  # uSeconds.
kLg2BitMark = 480  # uSeconds.

# EXACT translation from IRremoteESP8266 ir_LG.cpp:50-60
kLgAcAKB74955603DetectionMask = 0x0000080
kLgAcChecksumSize = 4  # Size in bits.
# Signature has the checksum removed, and another bit to match both Auto & Off.
kLgAcSwingHOffsetSize = kLgAcChecksumSize + 1
kLgAcSwingHSignature = 0x881317C >> kLgAcSwingHOffsetSize  # kLgAcSwingHOff >> kLgAcSwingHOffsetSize
kLgAcVaneSwingVBase = 0x8813200

# EXACT translation from IRremoteESP8266 ir_LG.h:53-96
kLgAcFanLowest = 0  # 0b0000
kLgAcFanLow = 1  # 0b0001
kLgAcFanMedium = 2  # 0b0010
kLgAcFanMax = 4  # 0b0100
kLgAcFanAuto = 5  # 0b0101
kLgAcFanLowAlt = 9  # 0b1001
kLgAcFanHigh = 10  # 0b1010
# Nr. of slots in the look-up table
kLgAcFanEntries = kLgAcFanHigh + 1
kLgAcTempAdjust = 15
kLgAcMinTemp = 16  # Celsius
kLgAcMaxTemp = 30  # Celsius
kLgAcCool = 0  # 0b000
kLgAcDry = 1  # 0b001
kLgAcFan = 2  # 0b010
kLgAcAuto = 3  # 0b011
kLgAcHeat = 4  # 0b100
kLgAcPowerOff = 3  # 0b11
kLgAcPowerOn = 0  # 0b00
kLgAcSignature = 0x88

kLgAcOffCommand = 0x88C0051
kLgAcLightToggle = 0x88C00A6

kLgAcSwingVToggle = 0x8810001
kLgAcSwingSignature = 0x8813
kLgAcSwingVLowest = 0x8813048
kLgAcSwingVLow = 0x8813059
kLgAcSwingVMiddle = 0x881306A
kLgAcSwingVUpperMiddle = 0x881307B
kLgAcSwingVHigh = 0x881308C
kLgAcSwingVHighest = 0x881309D
kLgAcSwingVSwing = 0x8813149
kLgAcSwingVAuto = kLgAcSwingVSwing
kLgAcSwingVOff = 0x881315A
kLgAcSwingVLowest_Short = 0x04
kLgAcSwingVLow_Short = 0x05
kLgAcSwingVMiddle_Short = 0x06
kLgAcSwingVUpperMiddle_Short = 0x07
kLgAcSwingVHigh_Short = 0x08
kLgAcSwingVHighest_Short = 0x09
kLgAcSwingVSwing_Short = 0x14
kLgAcSwingVAuto_Short = kLgAcSwingVSwing_Short
kLgAcSwingVOff_Short = 0x15

# AKB73757604 Constants
# SwingH
kLgAcSwingHAuto = 0x881316B
kLgAcSwingHOff = 0x881317C
# SwingV
kLgAcVaneSwingVHighest = 1  # 0b001
kLgAcVaneSwingVHigh = 2  # 0b010
kLgAcVaneSwingVUpperMiddle = 3  # 0b011
kLgAcVaneSwingVMiddle = 4  # 0b100
kLgAcVaneSwingVLow = 5  # 0b101
kLgAcVaneSwingVLowest = 6  # 0b110
kLgAcVaneSwingVSize = 8
kLgAcSwingVMaxVanes = 4  # Max Nr. of Vanes

# State length constants
kLgBits = 28
kLg32Bits = 32

# Model enums
LG_GE6711AR2853M = 0
LG_LG6711A20083V = 1
LG_AKB75215403 = 2
LG_AKB74955603 = 3
LG_AKB73757604 = 4


## Send an LG formatted message. (LG)
## Status: Beta / Should be working.
## @param[in] data The message to be sent.
## @param[in] nbits The number of bits of message to be sent.
##   Typically kLgBits or kLg32Bits.
## @param[in] repeat The number of times the command is to be repeated.
## @note LG has a separate message to indicate a repeat, like NEC does.
## EXACT translation from IRremoteESP8266 ir_LG.cpp:62-95
def sendLG(data: int, nbits: int = kLgBits, repeat: int = 0) -> List[int]:
    """
    Send an LG formatted message. (LG)
    EXACT translation from IRremoteESP8266 IRsend::sendLG (ir_LG.cpp:70-94)

    Returns timing array instead of transmitting via hardware.
    """
    from app.core.ir_protocols.ir_send import sendGeneric, sendGenericUint64
    from app.core.ir_protocols.samsung import sendSAMSUNG

    all_timings = []
    repeatHeaderMark = 0
    duty = 50

    if nbits >= kLg32Bits:
        # LG 32bit protocol is near identical to Samsung except for repeats.
        timings = sendSAMSUNG(data, nbits, 0)  # Send it as a single Samsung message.
        all_timings.extend(timings)
        repeatHeaderMark = kLg32RptHdrMark
        duty = 33
        repeat += 1
    else:
        # LG (28-bit) protocol.
        repeatHeaderMark = kLgHdrMark
        timings = sendGenericUint64(
            headermark=kLgHdrMark,
            headerspace=kLgHdrSpace,
            onemark=kLgBitMark,
            onespace=kLgOneSpace,
            zeromark=kLgBitMark,
            zerospace=kLgZeroSpace,
            footermark=kLgBitMark,
            data=data,
            nbits=nbits,
            MSBfirst=True,
        )
        all_timings.extend(timings)

    # Repeat
    # Protocol has a mandatory repeat-specific code sent after every command.
    if repeat:
        for _ in range(repeat):
            rep_timings = sendGenericUint64(
                headermark=repeatHeaderMark,
                headerspace=kLgRptSpace,
                onemark=0,
                onespace=0,
                zeromark=0,
                zerospace=0,  # No data is sent.
                footermark=kLgBitMark,
                data=0,
                nbits=0,  # No data.
                MSBfirst=True,
            )
            all_timings.extend(rep_timings)

    return all_timings


## Send an LG Variant-2 formatted message. (LG2)
## Status: Beta / Should be working.
## @param[in] data The message to be sent.
## @param[in] nbits The number of bits of message to be sent.
##   Typically kLgBits or kLg32Bits.
## @param[in] repeat The number of times the command is to be repeated.
## @note LG has a separate message to indicate a repeat, like NEC does.
## EXACT translation from IRremoteESP8266 ir_LG.cpp:97-124
def sendLG2(data: int, nbits: int = kLgBits, repeat: int = 0) -> List[int]:
    """
    Send an LG Variant-2 formatted message. (LG2)
    EXACT translation from IRremoteESP8266 IRsend::sendLG2 (ir_LG.cpp:104-123)

    Returns timing array instead of transmitting via hardware.
    """
    from app.core.ir_protocols.ir_send import sendGeneric, sendGenericUint64

    if nbits >= kLg32Bits:
        # Let the original routine handle it.
        return sendLG(data, nbits, repeat)  # Send it as a single Samsung message.

    all_timings = []

    # LGv2 (28-bit) protocol.
    timings = sendGenericUint64(
        headermark=kLg2HdrMark,
        headerspace=kLg2HdrSpace,
        onemark=kLg2BitMark,
        onespace=kLgOneSpace,
        zeromark=kLg2BitMark,
        zerospace=kLgZeroSpace,
        footermark=kLg2BitMark,
        data=data,
        nbits=nbits,
        MSBfirst=True,
    )
    all_timings.extend(timings)

    # TODO(crackn): Verify the details of what repeat messages look like.
    # Repeat
    # Protocol has a mandatory repeat-specific code sent after every command.
    if repeat:
        for _ in range(repeat):
            rep_timings = sendGenericUint64(
                headermark=kLg2HdrMark,
                headerspace=kLgRptSpace,
                onemark=0,
                onespace=0,
                zeromark=0,
                zerospace=0,  # No data is sent.
                footermark=kLgBitMark,
                data=0,
                nbits=0,  # No data.
                MSBfirst=True,
            )
            all_timings.extend(rep_timings)

    return all_timings


## Construct a raw 28-bit LG message code from the supplied address & command.
## Status: STABLE / Works.
## @param[in] address The address code.
## @param[in] command The command code.
## @return A raw 28-bit LG message code suitable for sendLG() etc.
## @note Sequence of bits = address + command + checksum.
## EXACT translation from IRremoteESP8266 ir_LG.cpp:126-136
def encodeLG(address: int, command: int) -> int:
    """
    Construct a raw 28-bit LG message code from the supplied address & command.
    EXACT translation from IRremoteESP8266 IRsend::encodeLG (ir_LG.cpp:132-135)
    """

    def sumNibbles(data, nibbles):
        """Sum nibbles (4-bit chunks)"""
        total = 0
        for _ in range(nibbles):
            total += data & 0xF
            data >>= 4
        return total & 0xF

    return (address << 20) | (command << kLgAcChecksumSize) | sumNibbles(command, 4)


## Decode the supplied LG message.
## Status: STABLE / Working.
## @param[in,out] results Ptr to the data to decode & where to store the result
## @param[in] offset The starting index to use when attempting to decode the
##   raw data. Typically/Defaults to kStartOffset.
## @param[in] nbits The number of data bits to expect.
##   Typically kLgBits or kLg32Bits.
## @param[in] strict Flag indicating if we should perform strict matching.
## @return True if it can decode it, false if it can't.
## @note LG protocol has a repeat code which is 4 items long.
##   Even though the protocol has 28/32 bits of data, only 24/28 bits are
##   distinct.
##   In transmission order, the 28/32 bits are constructed as follows:
##     8/12 bits of address + 16 bits of command + 4 bits of checksum.
## @note LG 32bit protocol appears near identical to the Samsung protocol.
##   They possibly differ on how they repeat and initial HDR mark.
## @see https://funembedded.wordpress.com/2014/11/08/ir-remote-control-for-lg-conditioner-using-stm32f302-mcu-on-mbed-platform/
## EXACT translation from IRremoteESP8266 ir_LG.cpp:138-224
def decodeLG(results, offset: int = 1, nbits: int = kLgBits, strict: bool = True) -> bool:
    """
    Decode the supplied LG message.
    EXACT translation from IRremoteESP8266 IRrecv::decodeLG (ir_LG.cpp:156-223)
    """
    from app.core.ir_protocols.ir_recv import _matchGeneric, matchMark, kHeader, kFooter

    def sumNibbles(data, nibbles):
        """Sum nibbles (4-bit chunks)"""
        total = 0
        for _ in range(nibbles):
            total += data & 0xF
            data >>= 4
        return total & 0xF

    if nbits >= kLg32Bits:
        if results.rawlen <= 2 * nbits + 2 * (kHeader + kFooter) - 1 + offset:
            return False  # Can't possibly be a valid LG32 message.
    else:
        if results.rawlen <= 2 * nbits + kHeader - 1 + offset:
            return False  # Can't possibly be a valid LG message.

    # Compliance
    if strict and nbits != kLgBits and nbits != kLg32Bits:
        return False  # Doesn't comply with expected LG protocol.

    # Header (Mark)
    kHdrSpace = 0
    if matchMark(results.rawbuf[offset], kLgHdrMark, 25, 50):
        kHdrSpace = kLgHdrSpace
    elif matchMark(results.rawbuf[offset], kLg2HdrMark, 25, 50):
        kHdrSpace = kLg2HdrSpace
    elif matchMark(results.rawbuf[offset], kLg32HdrMark, 25, 50):
        kHdrSpace = kLg32HdrSpace
    else:
        return False
    offset += 1

    # Set up the expected data section values.
    kBitmark = kLg2BitMark if (kHdrSpace == kLg2HdrSpace) else kLgBitMark

    # Header Space + Data + Footer
    data = _matchGeneric(
        data_ptr=results.rawbuf[offset:],
        result_bits_ptr=None,
        result_bytes_ptr=None,
        use_bits=True,
        remaining=results.rawlen - offset,
        nbits=nbits,
        hdrmark=0,  # Already matched the Header mark.
        hdrspace=kHdrSpace,
        onemark=kBitmark,
        onespace=kLgOneSpace,
        zeromark=kBitmark,
        zerospace=kLgZeroSpace,
        footermark=kBitmark,
        footerspace=kLgMinGap,
        atleast=True,
        tolerance=25,
        excess=50,
        MSBfirst=True,
    )
    if not data:
        return False
    offset += _matchGeneric(  # Get the actual offset used
        data_ptr=results.rawbuf[offset:],
        result_bits_ptr=None,
        result_bytes_ptr=None,
        use_bits=False,
        remaining=results.rawlen - offset,
        nbits=nbits,
        hdrmark=0,
        hdrspace=kHdrSpace,
        onemark=kBitmark,
        onespace=kLgOneSpace,
        zeromark=kBitmark,
        zerospace=kLgZeroSpace,
        footermark=kBitmark,
        footerspace=kLgMinGap,
        atleast=True,
        tolerance=25,
        excess=50,
        MSBfirst=True,
    )

    # Repeat
    if nbits >= kLg32Bits:
        # If we are expecting the LG 32-bit protocol, there is always
        # a repeat message. So, check for it.
        if not _matchGeneric(
            data_ptr=results.rawbuf[offset:],
            result_bits_ptr=None,
            result_bytes_ptr=None,
            use_bits=True,
            remaining=results.rawlen - offset,
            nbits=0,  # No Data bits to match.
            hdrmark=kLg32RptHdrMark,
            hdrspace=kLgRptSpace,
            onemark=kBitmark,
            onespace=kLgOneSpace,
            zeromark=kBitmark,
            zerospace=kLgZeroSpace,
            footermark=kBitmark,
            footerspace=kLgMinGap,
            atleast=True,
            tolerance=25,
            excess=50,
            MSBfirst=True,
        ):
            return False

    # The 16 bits before the checksum.
    command = data >> kLgAcChecksumSize

    # Compliance
    if strict and (data & 0xF) != sumNibbles(command, 4):
        return False  # The last 4 bits sent are the expected checksum.

    # Success
    if kHdrSpace == kLg2HdrSpace:  # Was it an LG2 message?
        pass  # results.decode_type = LG2
    else:
        pass  # results.decode_type = LG
    results.bits = nbits
    results.value = data
    results.command = command
    results.address = data >> 20  # The bits before the command.
    return True


## Native representation of a LG A/C message.
## EXACT translation from IRremoteESP8266 ir_LG.h:40-51
class LGProtocol:
    def __init__(self):
        self.raw = 0  # The state of the IR remote in IR code form (32-bit).

    # Bit fields
    @property
    def Sum(self) -> int:
        return self.raw & 0x0F

    @Sum.setter
    def Sum(self, value: int) -> None:
        self.raw = (self.raw & 0xFFFFFFF0) | (value & 0x0F)

    @property
    def Fan(self) -> int:
        return (self.raw >> 4) & 0x0F

    @Fan.setter
    def Fan(self, value: int) -> None:
        self.raw = (self.raw & 0xFFFFFF0F) | ((value & 0x0F) << 4)

    @property
    def Temp(self) -> int:
        return (self.raw >> 8) & 0x0F

    @Temp.setter
    def Temp(self, value: int) -> None:
        self.raw = (self.raw & 0xFFFFF0FF) | ((value & 0x0F) << 8)

    @property
    def Mode(self) -> int:
        return (self.raw >> 12) & 0x07

    @Mode.setter
    def Mode(self, value: int) -> None:
        self.raw = (self.raw & 0xFFFF8FFF) | ((value & 0x07) << 12)

    @property
    def Power(self) -> int:
        return (self.raw >> 18) & 0x03

    @Power.setter
    def Power(self, value: int) -> None:
        self.raw = (self.raw & 0xFFF3FFFF) | ((value & 0x03) << 18)

    @property
    def Sign(self) -> int:
        return (self.raw >> 20) & 0xFF

    @Sign.setter
    def Sign(self, value: int) -> None:
        self.raw = (self.raw & 0xF00FFFFF) | ((value & 0xFF) << 20)


## Class for handling detailed LG A/C messages.
## EXACT translation from IRremoteESP8266 ir_LG.h and ir_LG.cpp
class IRLgAc:
    ## Class Constructor
    ## EXACT translation from IRremoteESP8266 ir_LG.cpp:228-234
    def __init__(self) -> None:
        self._: LGProtocol = LGProtocol()
        self._temp: int = 15
        self._light: bool = True
        self._swingv: int = kLgAcSwingVOff
        self._swingv_prev: int = 0
        self._vaneswingv: List[int] = [0] * kLgAcSwingVMaxVanes
        self._vaneswingv_prev: List[int] = [0] * kLgAcSwingVMaxVanes
        self._swingh: bool = False
        self._swingh_prev: bool = False
        self._protocol = 0  # decode_type_t::LG
        self._model: int = LG_GE6711AR2853M
        self.stateReset()

    ## Reset the internals of the object to a known good state.
    ## EXACT translation from IRremoteESP8266 ir_LG.cpp:236-246
    def stateReset(self) -> None:
        self.setRaw(kLgAcOffCommand)
        self.setModel(LG_GE6711AR2853M)
        self._light = True
        self._swingv = kLgAcSwingVOff
        self._swingh = False
        for i in range(kLgAcSwingVMaxVanes):
            self._vaneswingv[i] = 0  # Reset to an unused value.
        self.updateSwingPrev()

    ## Is the current message a normal (non-special) message?
    ## @return True, if it is a normal message, False, if it is special.
    ## EXACT translation from IRremoteESP8266 ir_LG.cpp:296-306
    def _isNormal(self) -> bool:
        if self._.raw in [kLgAcOffCommand, kLgAcLightToggle]:
            return False
        if self.isSwing():
            return False
        return True

    ## Set the model of the A/C to emulate.
    ## @param[in] model The enum of the appropriate model.
    ## EXACT translation from IRremoteESP8266 ir_LG.cpp:308-325
    def setModel(self, model: int) -> None:
        if model in [LG_AKB75215403, LG_AKB74955603, LG_AKB73757604]:
            self._protocol = 1  # decode_type_t::LG2
        elif model in [LG_GE6711AR2853M, LG_LG6711A20083V]:
            self._protocol = 0  # decode_type_t::LG
        else:
            return
        self._model = model

    ## Get the model of the A/C.
    ## @return The enum of the compatible model.
    ## EXACT translation from IRremoteESP8266 ir_LG.cpp:327-329
    def getModel(self) -> int:
        return self._model

    ## Check if the stored code must belong to a AKB74955603 model.
    ## @return true, if it is AKB74955603 message. Otherwise, false.
    ## @note Internal use only.
    ## EXACT translation from IRremoteESP8266 ir_LG.cpp:331-337
    def _isAKB74955603(self) -> bool:
        return (
            ((self._.raw & kLgAcAKB74955603DetectionMask) and self._isNormal())
            or (self.isSwingV() and not self.isSwingVToggle())
            or self.isLightToggle()
        )

    ## Check if the stored code must belong to a AKB73757604 model.
    ## @return true, if it is AKB73757604 message. Otherwise, false.
    ## @note Internal use only.
    ## EXACT translation from IRremoteESP8266 ir_LG.cpp:339-342
    def _isAKB73757604(self) -> bool:
        return self.isSwingH() or self.isVaneSwingV()

    ## Check if the stored code must belong to a LG6711A20083V model.
    ## @return true, if it is LG6711A20083V message. Otherwise, false.
    ## @note Internal use only.
    ## EXACT translation from IRremoteESP8266 ir_LG.cpp:344-347
    def _isLG6711A20083V(self) -> bool:
        return self.isSwingVToggle()

    ## Get a copy of the internal state/code for this protocol.
    ## @return The code for this protocol based on the current internal state.
    ## EXACT translation from IRremoteESP8266 ir_LG.cpp:349-354
    def getRaw(self) -> int:
        self.checksum()
        return self._.raw

    ## Set the internal state from a valid code for this protocol.
    ## @param[in] new_code A valid code for this protocol.
    ## @param[in] protocol A valid decode protocol type to use.
    ## EXACT translation from IRremoteESP8266 ir_LG.cpp:356-393
    def setRaw(self, new_code: int, protocol: int = -1) -> None:
        self._.raw = new_code
        # Set the default model for this protocol, if the protocol is supplied.
        if protocol == 0:  # decode_type_t::LG
            if self.isSwingVToggle():  # This model uses a swingv toggle message.
                self.setModel(LG_LG6711A20083V)
            else:  # Assume others are a different model.
                self.setModel(LG_GE6711AR2853M)
        elif protocol == 1:  # decode_type_t::LG2
            self.setModel(LG_AKB75215403)
        else:
            # Don't change anything if it isn't an expected protocol.
            pass

        # Look for model specific settings/features to improve model detection.
        if self._isAKB74955603():
            self.setModel(LG_AKB74955603)
            if self.isSwingV():
                self._swingv = new_code
        if self._isAKB73757604():
            self.setModel(LG_AKB73757604)
            if self.isVaneSwingV():
                # Extract just the vane nr and position part of the message.
                vanecode = self.getVaneCode(self._.raw)
                self._vaneswingv[vanecode // kLgAcVaneSwingVSize] = vanecode % kLgAcVaneSwingVSize
            elif self.isSwingH():
                self._swingh = self._.raw == kLgAcSwingHAuto
        self._temp = 15  # Ensure there is a "sane" previous temp.
        self._temp = self.getTemp()

    ## Calculate the checksum for a given state.
    ## @param[in] state The value to calc the checksum of.
    ## @return The calculated checksum value.
    ## EXACT translation from IRremoteESP8266 ir_LG.cpp:395-400
    @staticmethod
    def calcChecksum(state: int) -> int:
        def sumNibbles(data, nibbles):
            """Sum nibbles (4-bit chunks)"""
            total = 0
            for _ in range(nibbles):
                total += data & 0xF
                data >>= 4
            return total & 0xF

        return sumNibbles(state >> kLgAcChecksumSize, 4)

    ## Verify the checksum is valid for a given state.
    ## @param[in] state The value to verify the checksum of.
    ## @return true, if the state has a valid checksum. Otherwise, false.
    ## EXACT translation from IRremoteESP8266 ir_LG.cpp:402-409
    @staticmethod
    def validChecksum(state: int) -> bool:
        LGp = LGProtocol()
        LGp.raw = state
        return IRLgAc.calcChecksum(state) == LGp.Sum

    ## Calculate and set the checksum values for the internal state.
    ## EXACT translation from IRremoteESP8266 ir_LG.cpp:411-414
    def checksum(self) -> None:
        self._.Sum = self.calcChecksum(self._.raw)

    ## Change the power setting to On.
    ## EXACT translation from IRremoteESP8266 ir_LG.cpp:416-417
    def on(self) -> None:
        self.setPower(True)

    ## Change the power setting to Off.
    ## EXACT translation from IRremoteESP8266 ir_LG.cpp:419-420
    def off(self) -> None:
        self.setPower(False)

    ## Change the power setting.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## EXACT translation from IRremoteESP8266 ir_LG.cpp:422-430
    def setPower(self, on: bool) -> None:
        self._.Power = kLgAcPowerOn if on else kLgAcPowerOff
        if on:
            self.setTemp(self._temp)  # Reset the temp if we are on.
        else:
            self._setTemp(0)  # Off clears the temp.

    ## Get the value of the current power setting.
    ## @return true, the setting is on. false, the setting is off.
    ## EXACT translation from IRremoteESP8266 ir_LG.cpp:432-436
    def getPower(self) -> bool:
        return self._.Power == kLgAcPowerOn

    ## Is the message a Power Off message?
    ## @return true, if it is. false, if not.
    ## EXACT translation from IRremoteESP8266 ir_LG.cpp:438-440
    def isOffCommand(self) -> bool:
        return self._.raw == kLgAcOffCommand

    ## Change the light/led/display setting.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## EXACT translation from IRremoteESP8266 ir_LG.cpp:442-444
    def setLight(self, on: bool) -> None:
        self._light = on

    ## Get the value of the current light setting.
    ## @return true, the setting is on. false, the setting is off.
    ## EXACT translation from IRremoteESP8266 ir_LG.cpp:446-448
    def getLight(self) -> bool:
        return self._light

    ## Is the message a Light Toggle message?
    ## @return true, if it is. false, if not.
    ## EXACT translation from IRremoteESP8266 ir_LG.cpp:450-452
    def isLightToggle(self) -> bool:
        return self._.raw == kLgAcLightToggle

    ## Set the temperature.
    ## @param[in] value The native temperature.
    ## @note Internal use only.
    ## EXACT translation from IRremoteESP8266 ir_LG.cpp:454-457
    def _setTemp(self, value: int) -> None:
        self._.Temp = value

    ## Set the temperature.
    ## @param[in] degrees The temperature in degrees celsius.
    ## EXACT translation from IRremoteESP8266 ir_LG.cpp:459-466
    def setTemp(self, degrees: int) -> None:
        temp = max(kLgAcMinTemp, degrees)
        temp = min(kLgAcMaxTemp, temp)
        self._temp = temp
        self._setTemp(temp - kLgAcTempAdjust)

    ## Get the current temperature setting.
    ## @return The current setting for temp. in degrees celsius.
    ## EXACT translation from IRremoteESP8266 ir_LG.cpp:468-472
    def getTemp(self) -> int:
        return self._.Temp + kLgAcTempAdjust if self._isNormal() else self._temp

    ## Set the speed of the fan.
    ## @param[in] speed The desired setting.
    ## EXACT translation from IRremoteESP8266 ir_LG.cpp:474-509
    def setFan(self, speed: int) -> None:
        _speed = speed
        # Only model AKB74955603 has these speeds, so convert if we have to.
        if self.getModel() != LG_AKB74955603:
            if speed == kLgAcFanLowAlt:
                self._.Fan = kLgAcFanLow
                return
            elif speed == kLgAcFanHigh:
                self._.Fan = kLgAcFanMax
                return

        if speed in [kLgAcFanLow, kLgAcFanLowAlt]:
            _speed = kLgAcFanLowAlt if (self.getModel() == LG_AKB74955603) else kLgAcFanLow
        elif speed == kLgAcFanHigh:
            _speed = speed if (self.getModel() == LG_AKB74955603) else kLgAcFanMax
        elif speed in [kLgAcFanAuto, kLgAcFanLowest, kLgAcFanMedium, kLgAcFanMax]:
            _speed = speed
        else:
            _speed = kLgAcFanAuto
        self._.Fan = _speed

    ## Get the current fan speed setting.
    ## @return The current fan speed.
    ## EXACT translation from IRremoteESP8266 ir_LG.cpp:511-513
    def getFan(self) -> int:
        return self._.Fan

    ## Get the operating mode setting of the A/C.
    ## @return The current operating mode setting.
    ## EXACT translation from IRremoteESP8266 ir_LG.cpp:515-517
    def getMode(self) -> int:
        return self._.Mode

    ## Set the operating mode of the A/C.
    ## @param[in] mode The desired operating mode.
    ## EXACT translation from IRremoteESP8266 ir_LG.cpp:519-533
    def setMode(self, mode: int) -> None:
        if mode in [kLgAcAuto, kLgAcDry, kLgAcHeat, kLgAcCool, kLgAcFan]:
            self._.Mode = mode
        else:
            self._.Mode = kLgAcAuto

    ## Check if the stored code is a SwingV Toggle message.
    ## @return true, if it is. Otherwise, false.
    ## EXACT translation from IRremoteESP8266 ir_LG.cpp:535-537
    def isSwingVToggle(self) -> bool:
        return self._.raw == kLgAcSwingVToggle

    ## Check if the stored code is a Swing message.
    ## @return true, if it is. Otherwise, false.
    ## EXACT translation from IRremoteESP8266 ir_LG.cpp:539-543
    def isSwing(self) -> bool:
        return ((self._.raw >> 12) == kLgAcSwingSignature) or self.isSwingVToggle()

    ## Check if the stored code is a non-vane SwingV message.
    ## @return true, if it is. Otherwise, false.
    ## EXACT translation from IRremoteESP8266 ir_LG.cpp:545-551
    def isSwingV(self) -> bool:
        code = self._.raw >> kLgAcChecksumSize
        return (
            code >= (kLgAcSwingVLowest >> kLgAcChecksumSize)
            and code < (kLgAcSwingHAuto >> kLgAcChecksumSize)
        ) or self.isSwingVToggle()

    ## Check if the stored code is a SwingH message.
    ## @return true, if it is. Otherwise, false.
    ## EXACT translation from IRremoteESP8266 ir_LG.cpp:553-557
    def isSwingH(self) -> bool:
        return (self._.raw >> kLgAcSwingHOffsetSize) == kLgAcSwingHSignature

    ## Get the Horizontal Swing position setting of the A/C.
    ## @return true, if it is. Otherwise, false.
    ## EXACT translation from IRremoteESP8266 ir_LG.cpp:559-561
    def getSwingH(self) -> bool:
        return self._swingh

    ## Set the Horizontal Swing mode of the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## EXACT translation from IRremoteESP8266 ir_LG.cpp:563-565
    def setSwingH(self, on: bool) -> None:
        self._swingh = on

    ## Check if the stored code is a vane specific SwingV message.
    ## @return true, if it is. Otherwise, false.
    ## EXACT translation from IRremoteESP8266 ir_LG.cpp:567-574
    def isVaneSwingV(self) -> bool:
        return self._.raw > kLgAcVaneSwingVBase and self._.raw < (
            kLgAcVaneSwingVBase + ((kLgAcSwingVMaxVanes * kLgAcVaneSwingVSize) << kLgAcChecksumSize)
        )

    ## Set the Vertical Swing mode of the A/C.
    ## @param[in] position The position/mode to set the vanes to.
    ## EXACT translation from IRremoteESP8266 ir_LG.cpp:576-589
    def setSwingV(self, position: int) -> None:
        # Is it a valid position code?
        if position in [kLgAcSwingVOff, kLgAcSwingVToggle]:
            pass
        elif position <= 0xFF:  # It's a short code, convert it.
            self._swingv = (kLgAcSwingSignature << 8 | position) << kLgAcChecksumSize
            self._swingv |= self.calcChecksum(self._swingv)
            return
        else:
            self._swingv = position
            return

        if position <= 0xFF:  # It's a short code, convert it.
            self._swingv = (kLgAcSwingSignature << 8 | position) << kLgAcChecksumSize
            self._swingv |= self.calcChecksum(self._swingv)
        else:
            self._swingv = position

    ## Copy the previous swing settings from the current ones.
    ## EXACT translation from IRremoteESP8266 ir_LG.cpp:591-596
    def updateSwingPrev(self) -> None:
        self._swingv_prev = self._swingv
        for i in range(kLgAcSwingVMaxVanes):
            self._vaneswingv_prev[i] = self._vaneswingv[i]

    ## Get the Vertical Swing position setting of the A/C.
    ## @return The native position/mode.
    ## EXACT translation from IRremoteESP8266 ir_LG.cpp:598-600
    def getSwingV(self) -> int:
        return self._swingv

    ## Set the per Vane Vertical Swing mode of the A/C.
    ## @param[in] vane The nr. of the vane to control.
    ## @param[in] position The position/mode to set the vanes to.
    ## EXACT translation from IRremoteESP8266 ir_LG.cpp:602-609
    def setVaneSwingV(self, vane: int, position: int) -> None:
        if vane < kLgAcSwingVMaxVanes:  # It's a valid vane nr.
            if position and position <= kLgAcVaneSwingVLowest:  # Valid position
                self._vaneswingv[vane] = position

    ## Get the Vertical Swing position for the given vane of the A/C.
    ## @return The native position/mode.
    ## EXACT translation from IRremoteESP8266 ir_LG.cpp:611-615
    def getVaneSwingV(self, vane: int) -> int:
        return self._vaneswingv[vane] if (vane < kLgAcSwingVMaxVanes) else 0

    ## Get the vane code of a Vane Vertical Swing message.
    ## @param[in] raw A raw number representing a native LG message.
    ## @return A number containing just the vane nr, and the position.
    ## EXACT translation from IRremoteESP8266 ir_LG.cpp:617-622
    @staticmethod
    def getVaneCode(raw: int) -> int:
        return (raw - kLgAcVaneSwingVBase) >> kLgAcChecksumSize

    ## Calculate the Vane specific Vertical Swing code for the A/C.
    ## @return The native raw code.
    ## EXACT translation from IRremoteESP8266 ir_LG.cpp:624-632
    @staticmethod
    def calcVaneSwingV(vane: int, position: int) -> int:
        result = kLgAcVaneSwingVBase
        if vane < kLgAcSwingVMaxVanes:  # It's a valid vane nr.
            if position and position <= kLgAcVaneSwingVLowest:  # Valid position
                result += (vane * kLgAcVaneSwingVSize + position) << kLgAcChecksumSize
        return result | IRLgAc.calcChecksum(result)

    ## Check if the internal state looks like a valid LG A/C message.
    ## @return true, the internal state is a valid LG A/C mesg. Otherwise, false.
    ## EXACT translation from IRremoteESP8266 ir_LG.cpp:858-862
    def isValidLgAc(self) -> bool:
        return self.validChecksum(self._.raw) and (self._.Sign == kLgAcSignature)
