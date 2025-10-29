# Copyright 2009 Ken Shirriff
# Copyright 2017-2021 David Conran
# Python translation: Direct conversion from C++ with NO optimizations

## @file
## @brief Support for Samsung protocols.
## Samsung originally added from https://github.com/shirriff/Arduino-IRremote/
## @see https://github.com/crankyoldgit/IRremoteESP8266/issues/505
## @see https://github.com/crankyoldgit/IRremoteESP8266/issues/621
## @see https://github.com/crankyoldgit/IRremoteESP8266/issues/1062
## @see http://elektrolab.wz.cz/katalog/samsung_protocol.pdf
## @see https://github.com/crankyoldgit/IRremoteESP8266/issues/1538 (Checksum)
## Direct translation from IRremoteESP8266 ir_Samsung.cpp and ir_Samsung.h

from typing import List

# Supports:
#   Brand: Samsung,  Model: UA55H6300 TV (SAMSUNG)
#   Brand: Samsung,  Model: BN59-01178B TV remote (SAMSUNG)
#   Brand: Samsung,  Model: UE40K5510AUXRU TV (SAMSUNG)
#   Brand: Samsung,  Model: DB63-03556X003 remote
#   Brand: Samsung,  Model: DB93-16761C remote
#   Brand: Samsung,  Model: IEC-R03 remote
#   Brand: Samsung,  Model: AK59-00167A Bluray remote (SAMSUNG36)
#   Brand: Samsung,  Model: AH59-02692E Soundbar remote (SAMSUNG36)
#   Brand: Samsung,  Model: HW-J551 Soundbar (SAMSUNG36)
#   Brand: Samsung,  Model: AR09FSSDAWKNFA A/C (SAMSUNG_AC)
#   Brand: Samsung,  Model: AR09HSFSBWKN A/C (SAMSUNG_AC)
#   Brand: Samsung,  Model: AR12KSFPEWQNET A/C (SAMSUNG_AC)
#   Brand: Samsung,  Model: AR12HSSDBWKNEU A/C (SAMSUNG_AC)
#   Brand: Samsung,  Model: AR12NXCXAWKXEU A/C (SAMSUNG_AC)
#   Brand: Samsung,  Model: AR12TXEAAWKNEU A/C (SAMSUNG_AC)
#   Brand: Samsung,  Model: DB93-14195A remote (SAMSUNG_AC)
#   Brand: Samsung,  Model: DB96-24901C remote (SAMSUNG_AC)

# Constants
# EXACT translation from IRremoteESP8266 ir_Samsung.cpp:24-45
kSamsungTick = 560
kSamsungHdrMarkTicks = 8
kSamsungHdrMark = kSamsungHdrMarkTicks * kSamsungTick
kSamsungHdrSpaceTicks = 8
kSamsungHdrSpace = kSamsungHdrSpaceTicks * kSamsungTick
kSamsungBitMarkTicks = 1
kSamsungBitMark = kSamsungBitMarkTicks * kSamsungTick
kSamsungOneSpaceTicks = 3
kSamsungOneSpace = kSamsungOneSpaceTicks * kSamsungTick
kSamsungZeroSpaceTicks = 1
kSamsungZeroSpace = kSamsungZeroSpaceTicks * kSamsungTick
kSamsungRptSpaceTicks = 4
kSamsungRptSpace = kSamsungRptSpaceTicks * kSamsungTick
kSamsungMinMessageLengthTicks = 193
kSamsungMinMessageLength = kSamsungMinMessageLengthTicks * kSamsungTick
kSamsungMinGapTicks = kSamsungMinMessageLengthTicks - (
    kSamsungHdrMarkTicks
    + kSamsungHdrSpaceTicks
    + 32 * (kSamsungBitMarkTicks + kSamsungOneSpaceTicks)  # kSamsungBits = 32
    + kSamsungBitMarkTicks
)
kSamsungMinGap = kSamsungMinGapTicks * kSamsungTick

# EXACT translation from IRremoteESP8266 ir_Samsung.cpp:47-55
kSamsungAcHdrMark = 690
kSamsungAcHdrSpace = 17844
kSamsungAcSections = 2
kSamsungAcSectionMark = 3086
kSamsungAcSectionSpace = 8864
kSamsungAcSectionGap = 2886
kSamsungAcBitMark = 586
kSamsungAcOneSpace = 1432
kSamsungAcZeroSpace = 436

# EXACT translation from IRremoteESP8266 ir_Samsung.cpp:57-63
# Data from https://github.com/crankyoldgit/IRremoteESP8266/issues/1220
# Values calculated based on the average of ten messages.
kSamsung36HdrMark = 4515  # uSeconds
kSamsung36HdrSpace = 4438  # uSeconds
kSamsung36BitMark = 512  # uSeconds
kSamsung36OneSpace = 1468  # uSeconds
kSamsung36ZeroSpace = 490  # uSeconds

# EXACT translation from IRremoteESP8266 ir_Samsung.cpp:65-74
# _.Swing
kSamsungAcSwingV = 0b010
kSamsungAcSwingH = 0b011
kSamsungAcSwingBoth = 0b100
kSamsungAcSwingOff = 0b111
# _.FanSpecial
kSamsungAcFanSpecialOff = 0b000
kSamsungAcPowerfulOn = 0b011
kSamsungAcBreezeOn = 0b101
kSamsungAcEconoOn = 0b111

# EXACT translation from IRremoteESP8266 ir_Samsung.h:167-183
kSamsungAcMinTemp = 16  # C   Mask 0b11110000
kSamsungAcMaxTemp = 30  # C   Mask 0b11110000
kSamsungAcAutoTemp = 25  # C   Mask 0b11110000
kSamsungAcAuto = 0
kSamsungAcCool = 1
kSamsungAcDry = 2
kSamsungAcFan = 3
kSamsungAcHeat = 4
kSamsungAcFanAuto = 0
kSamsungAcFanLow = 2
kSamsungAcFanMed = 4
kSamsungAcFanHigh = 5
kSamsungAcFanAuto2 = 6
kSamsungAcFanTurbo = 7
kSamsungAcSectionLength = 7
kSamsungAcPowerSection = 0x1D20F00000000

# State length constants (from IRremoteESP8266.h)
kSamsungAcStateLength = 14
kSamsungAcExtendedStateLength = 21
kSamsungBits = 32
kSamsung36Bits = 36


## This sending protocol is used by some other protocols. e.g. LG.
## Send a 32-bit Samsung formatted message.
## Status: STABLE / Should be working.
## @param[in] data The message to be sent.
## @param[in] nbits The number of bits of message to be sent.
## @param[in] repeat The number of times the command is to be repeated.
## @see http://elektrolab.wz.cz/katalog/samsung_protocol.pdf
## @note Samsung has a separate message to indicate a repeat, like NEC does.
## EXACT translation from IRremoteESP8266 ir_Samsung.cpp:87-102
def sendSAMSUNG(data: int, nbits: int = kSamsungBits, repeat: int = 0) -> List[int]:
    """
    Send a 32-bit Samsung formatted message.
    EXACT translation from IRremoteESP8266 IRsend::sendSAMSUNG (ir_Samsung.cpp:96-102)

    Returns timing array instead of transmitting via hardware.
    """
    from app.core.ir_protocols.ir_send import sendGeneric, sendGenericUint64

    return sendGenericUint64(
        headermark=kSamsungHdrMark,
        headerspace=kSamsungHdrSpace,
        onemark=kSamsungBitMark,
        onespace=kSamsungOneSpace,
        zeromark=kSamsungBitMark,
        zerospace=kSamsungZeroSpace,
        footermark=kSamsungBitMark,
        data=data,
        nbits=nbits,
        MSBfirst=True,
    )


## Construct a raw Samsung message from the supplied customer(address) & command.
## Status: STABLE / Should be working.
## @param[in] customer The customer code. (aka. Address)
## @param[in] command The command code.
## @return A raw 32-bit Samsung message suitable for `sendSAMSUNG()`.
## EXACT translation from IRremoteESP8266 ir_Samsung.cpp:104-115
def encodeSAMSUNG(customer: int, command: int) -> int:
    """
    Construct a raw Samsung message from the supplied customer(address) & command.
    EXACT translation from IRremoteESP8266 IRsend::encodeSAMSUNG (ir_Samsung.cpp:110-115)
    """
    from app.core.ir_protocols.ir_recv import reverseBits

    revcustomer = reverseBits(customer, 8)
    revcommand = reverseBits(command, 8)
    return (revcommand ^ 0xFF) | (revcommand << 8) | (revcustomer << 16) | (revcustomer << 24)


## Decode the supplied Samsung 32-bit message.
## Status: STABLE
## @param[in,out] results Ptr to the data to decode & where to store the result
## @param[in] offset The starting index to use when attempting to decode the
##   raw data. Typically/Defaults to kStartOffset.
## @param[in] nbits The number of data bits to expect.
## @param[in] strict Flag indicating if we should perform strict matching.
## @return True if it can decode it, false if it can't.
## @note Samsung messages whilst 32 bits in size, only contain 16 bits of
##   distinct data. e.g. In transmition order:
##   customer_byte + customer_byte(same) + address_byte + invert(address_byte)
## @note LG 32bit protocol appears near identical to the Samsung protocol.
##   They differ on their compliance criteria and how they repeat.
## @see http://elektrolab.wz.cz/katalog/samsung_protocol.pdf
## EXACT translation from IRremoteESP8266 ir_Samsung.cpp:118-166
def decodeSAMSUNG(results, offset: int = 1, nbits: int = kSamsungBits, strict: bool = True) -> bool:
    """
    Decode the supplied Samsung 32-bit message.
    EXACT translation from IRremoteESP8266 IRrecv::decodeSAMSUNG (ir_Samsung.cpp:133-165)
    """
    from app.core.ir_protocols.ir_recv import _matchGeneric, reverseBits

    if strict and nbits != kSamsungBits:
        return False  # We expect Samsung to be 32 bits of message.

    data = 0

    # Match Header + Data + Footer
    used = _matchGeneric(
        data_ptr=results.rawbuf[offset:],
        result_bits_ptr=None,
        result_bytes_ptr=None,
        use_bits=True,
        remaining=results.rawlen - offset,
        nbits=nbits,
        hdrmark=kSamsungHdrMark,
        hdrspace=kSamsungHdrSpace,
        onemark=kSamsungBitMark,
        onespace=kSamsungOneSpace,
        zeromark=kSamsungBitMark,
        zerospace=kSamsungZeroSpace,
        footermark=kSamsungBitMark,
        footerspace=kSamsungMinGap,
        atleast=True,
        tolerance=25,
        excess=50,
        MSBfirst=True,
    )
    if not used:
        return False
    data = used  # _matchGeneric returns the data value when use_bits=True

    # Compliance
    # According to the spec, the customer (address) code is the first 8
    # transmitted bits. It's then repeated. Check for that.
    address = data >> 24
    if strict and address != ((data >> 16) & 0xFF):
        return False
    # Spec says the command code is the 3rd block of transmitted 8-bits,
    # followed by the inverted command code.
    command = (data & 0xFF00) >> 8
    if strict and command != ((data & 0xFF) ^ 0xFF):
        return False

    # Success
    results.bits = nbits
    results.value = data
    # results.decode_type = SAMSUNG
    # command & address need to be reversed as they are transmitted LSB first,
    results.command = reverseBits(command, 8)
    results.address = reverseBits(address, 8)
    return True


## Send a Samsung 36-bit formatted message.
## Status: STABLE / Works on real devices.
## @param[in] data The message to be sent.
## @param[in] nbits The number of bits of message to be sent.
## @param[in] repeat The number of times the command is to be repeated.
## @see https://github.com/crankyoldgit/IRremoteESP8266/issues/621
## EXACT translation from IRremoteESP8266 ir_Samsung.cpp:168-195
def sendSamsung36(data: int, nbits: int = kSamsung36Bits, repeat: int = 0) -> List[int]:
    """
    Send a Samsung 36-bit formatted message.
    EXACT translation from IRremoteESP8266 IRsend::sendSamsung36 (ir_Samsung.cpp:175-194)

    Returns timing array instead of transmitting via hardware.
    """
    from app.core.ir_protocols.ir_send import sendGeneric, sendGenericUint64

    if nbits < 16:
        return []  # To small to send.

    all_timings = []

    for r in range(repeat + 1):
        # Block #1 (16 bits)
        block1_timings = sendGenericUint64(
            headermark=kSamsung36HdrMark,
            headerspace=kSamsung36HdrSpace,
            onemark=kSamsung36BitMark,
            onespace=kSamsung36OneSpace,
            zeromark=kSamsung36BitMark,
            zerospace=kSamsung36ZeroSpace,
            footermark=kSamsung36BitMark,
            data=data >> (nbits - 16),
            nbits=16,
            MSBfirst=True,
        )
        all_timings.extend(block1_timings)

        # Block #2 (The rest, typically 20 bits)
        block2_timings = sendGenericUint64(
            headermark=0,
            headerspace=0,  # No header
            onemark=kSamsung36BitMark,
            onespace=kSamsung36OneSpace,
            zeromark=kSamsung36BitMark,
            zerospace=kSamsung36ZeroSpace,
            footermark=kSamsung36BitMark,
            # Mask off the rest of the bits.
            data=data & ((1 << (nbits - 16)) - 1),
            nbits=nbits - 16,
            MSBfirst=True,
        )
        all_timings.extend(block2_timings)

    return all_timings


## Decode the supplied Samsung36 message.
## Status: STABLE / Expected to work.
## @param[in,out] results Ptr to the data to decode & where to store the result
## @param[in] offset The starting index to use when attempting to decode the
##   raw data. Typically/Defaults to kStartOffset.
## @param[in] nbits The number of data bits to expect.
## @param[in] strict Flag indicating if we should perform strict matching.
## @return True if it can decode it, false if it can't.
## @see https://github.com/crankyoldgit/IRremoteESP8266/issues/621
## EXACT translation from IRremoteESP8266 ir_Samsung.cpp:197-247
def decodeSamsung36(
    results, offset: int = 1, nbits: int = kSamsung36Bits, strict: bool = True
) -> bool:
    """
    Decode the supplied Samsung36 message.
    EXACT translation from IRremoteESP8266 IRrecv::decodeSamsung36 (ir_Samsung.cpp:207-246)
    """
    from app.core.ir_protocols.ir_recv import _matchGeneric, kHeader, kFooter

    if results.rawlen < 2 * nbits + kHeader + kFooter * 2 - 1 + offset:
        return False  # Can't possibly be a valid Samsung message.
    # We need to be looking for > 16 bits to make sense.
    if nbits <= 16:
        return False
    if strict and nbits != kSamsung36Bits:
        return False  # We expect nbits to be 36 bits of message.

    data = 0

    # Match Header + Data + Footer
    used = _matchGeneric(
        data_ptr=results.rawbuf[offset:],
        result_bits_ptr=None,
        result_bytes_ptr=None,
        use_bits=True,
        remaining=results.rawlen - offset,
        nbits=16,
        hdrmark=kSamsung36HdrMark,
        hdrspace=kSamsung36HdrSpace,
        onemark=kSamsung36BitMark,
        onespace=kSamsung36OneSpace,
        zeromark=kSamsung36BitMark,
        zerospace=kSamsung36ZeroSpace,
        footermark=kSamsung36BitMark,
        footerspace=kSamsung36HdrSpace,
        atleast=False,
        tolerance=25,
        excess=50,
        MSBfirst=True,
    )
    if not used:
        return False
    data = used  # First 16 bits
    offset += _matchGeneric(  # Get the actual offset used
        data_ptr=results.rawbuf[offset:],
        result_bits_ptr=None,
        result_bytes_ptr=None,
        use_bits=False,
        remaining=results.rawlen - offset,
        nbits=16,
        hdrmark=kSamsung36HdrMark,
        hdrspace=kSamsung36HdrSpace,
        onemark=kSamsung36BitMark,
        onespace=kSamsung36OneSpace,
        zeromark=kSamsung36BitMark,
        zerospace=kSamsung36ZeroSpace,
        footermark=kSamsung36BitMark,
        footerspace=kSamsung36HdrSpace,
        atleast=False,
        tolerance=25,
        excess=50,
        MSBfirst=True,
    )

    # Data (Block #2)
    data2 = _matchGeneric(
        data_ptr=results.rawbuf[offset:],
        result_bits_ptr=None,
        result_bytes_ptr=None,
        use_bits=True,
        remaining=results.rawlen - offset,
        nbits=nbits - 16,
        hdrmark=0,
        hdrspace=0,
        onemark=kSamsung36BitMark,
        onespace=kSamsung36OneSpace,
        zeromark=kSamsung36BitMark,
        zerospace=kSamsung36ZeroSpace,
        footermark=kSamsung36BitMark,
        footerspace=kSamsungMinGap,
        atleast=True,
        tolerance=25,
        excess=50,
        MSBfirst=True,
    )
    if not data2:
        return False
    data <<= nbits - 16
    data += data2

    # Success
    results.bits = nbits
    results.value = data
    # results.decode_type = SAMSUNG36
    results.command = data & ((1 << (nbits - 16)) - 1)
    results.address = data >> (nbits - 16)
    return True


## Send a Samsung A/C message.
## Status: Stable / Known working.
## @see https://github.com/crankyoldgit/IRremoteESP8266/issues/505
## @param[in] data The message to be sent.
## @param[in] nbytes The number of bytes of message to be sent.
## @param[in] repeat The number of times the command is to be repeated.
## EXACT translation from IRremoteESP8266 ir_Samsung.cpp:249-279
def sendSamsungAC(data: List[int], nbytes: int, repeat: int = 0) -> List[int]:
    """
    Send a Samsung A/C message.
    EXACT translation from IRremoteESP8266 IRsend::sendSamsungAC (ir_Samsung.cpp:256-278)

    Returns timing array instead of transmitting via hardware.
    """
    from app.core.ir_protocols.ir_send import sendGeneric, sendGenericUint64

    if nbytes < kSamsungAcStateLength and nbytes % kSamsungAcSectionLength:
        return []  # Not an appropriate number of bytes to send a proper message.

    all_timings = []

    for r in range(repeat + 1):
        # Header
        all_timings.append(kSamsungAcHdrMark)
        all_timings.append(kSamsungAcHdrSpace)
        # Send in 7 byte sections.
        for offset in range(0, nbytes, kSamsungAcSectionLength):
            section_timings = sendGeneric(
                headermark=kSamsungAcSectionMark,
                headerspace=kSamsungAcSectionSpace,
                onemark=kSamsungAcBitMark,
                onespace=kSamsungAcOneSpace,
                zeromark=kSamsungAcBitMark,
                zerospace=kSamsungAcZeroSpace,
                footermark=kSamsungAcBitMark,
                dataptr=data[offset:],
                nbytes=kSamsungAcSectionLength,  # 7 bytes == 56 bits
                MSBfirst=False,
            )
            all_timings.extend(section_timings)
        # Complete made up guess at inter-message gap.
        # kDefaultMessageGap - kSamsungAcSectionGap
        all_timings.append(100000 - kSamsungAcSectionGap)

    return all_timings


## Native representation of a Samsung A/C message.
## EXACT translation from IRremoteESP8266 ir_Samsung.h:46-164
class SamsungProtocol:
    def __init__(self):
        # The state array (14 or 21 bytes for Samsung AC)
        self.raw = [0] * kSamsungAcExtendedStateLength

    # Standard message map (first 14 bytes)
    # Byte 0 - no bitfields

    # Byte 1
    @property
    def Sum1Lower(self) -> int:
        return (self.raw[1] >> 4) & 0x0F

    @Sum1Lower.setter
    def Sum1Lower(self, value: int) -> None:
        self.raw[1] = (self.raw[1] & 0x0F) | ((value & 0x0F) << 4)

    # Byte 2
    @property
    def Sum1Upper(self) -> int:
        return self.raw[2] & 0x0F

    @Sum1Upper.setter
    def Sum1Upper(self, value: int) -> None:
        self.raw[2] = (self.raw[2] & 0xF0) | (value & 0x0F)

    # Byte 5
    @property
    def Sleep5(self) -> int:
        return (self.raw[5] >> 4) & 0x01

    @Sleep5.setter
    def Sleep5(self, value: bool) -> None:
        if value:
            self.raw[5] |= 0x10
        else:
            self.raw[5] &= 0xEF

    @property
    def Quiet(self) -> int:
        return (self.raw[5] >> 5) & 0x01

    @Quiet.setter
    def Quiet(self, value: bool) -> None:
        if value:
            self.raw[5] |= 0x20
        else:
            self.raw[5] &= 0xDF

    # Byte 6
    @property
    def Power1(self) -> int:
        return (self.raw[6] >> 4) & 0x03

    @Power1.setter
    def Power1(self, value: int) -> None:
        self.raw[6] = (self.raw[6] & 0xCF) | ((value & 0x03) << 4)

    # Byte 8
    @property
    def Sum2Lower(self) -> int:
        return (self.raw[8] >> 4) & 0x0F

    @Sum2Lower.setter
    def Sum2Lower(self, value: int) -> None:
        self.raw[8] = (self.raw[8] & 0x0F) | ((value & 0x0F) << 4)

    # Byte 9
    @property
    def Sum2Upper(self) -> int:
        return self.raw[9] & 0x0F

    @Sum2Upper.setter
    def Sum2Upper(self, value: int) -> None:
        self.raw[9] = (self.raw[9] & 0xF0) | (value & 0x0F)

    @property
    def Swing(self) -> int:
        return (self.raw[9] >> 4) & 0x07

    @Swing.setter
    def Swing(self, value: int) -> None:
        self.raw[9] = (self.raw[9] & 0x8F) | ((value & 0x07) << 4)

    # Byte 10
    @property
    def FanSpecial(self) -> int:
        return (self.raw[10] >> 1) & 0x07

    @FanSpecial.setter
    def FanSpecial(self, value: int) -> None:
        self.raw[10] = (self.raw[10] & 0xF1) | ((value & 0x07) << 1)

    @property
    def Display(self) -> int:
        return (self.raw[10] >> 4) & 0x01

    @Display.setter
    def Display(self, value: bool) -> None:
        if value:
            self.raw[10] |= 0x10
        else:
            self.raw[10] &= 0xEF

    @property
    def CleanToggle10(self) -> int:
        return (self.raw[10] >> 7) & 0x01

    @CleanToggle10.setter
    def CleanToggle10(self, value: bool) -> None:
        if value:
            self.raw[10] |= 0x80
        else:
            self.raw[10] &= 0x7F

    # Byte 11
    @property
    def Ion(self) -> int:
        return self.raw[11] & 0x01

    @Ion.setter
    def Ion(self, value: bool) -> None:
        if value:
            self.raw[11] |= 0x01
        else:
            self.raw[11] &= 0xFE

    @property
    def CleanToggle11(self) -> int:
        return (self.raw[11] >> 1) & 0x01

    @CleanToggle11.setter
    def CleanToggle11(self, value: bool) -> None:
        if value:
            self.raw[11] |= 0x02
        else:
            self.raw[11] &= 0xFD

    @property
    def Temp(self) -> int:
        return (self.raw[11] >> 4) & 0x0F

    @Temp.setter
    def Temp(self, value: int) -> None:
        self.raw[11] = (self.raw[11] & 0x0F) | ((value & 0x0F) << 4)

    # Byte 12
    @property
    def Fan(self) -> int:
        return (self.raw[12] >> 1) & 0x07

    @Fan.setter
    def Fan(self, value: int) -> None:
        self.raw[12] = (self.raw[12] & 0xF1) | ((value & 0x07) << 1)

    @property
    def Mode(self) -> int:
        return (self.raw[12] >> 4) & 0x07

    @Mode.setter
    def Mode(self, value: int) -> None:
        self.raw[12] = (self.raw[12] & 0x8F) | ((value & 0x07) << 4)

    # Byte 13
    @property
    def BeepToggle(self) -> int:
        return (self.raw[13] >> 2) & 0x01

    @BeepToggle.setter
    def BeepToggle(self, value: bool) -> None:
        if value:
            self.raw[13] |= 0x04
        else:
            self.raw[13] &= 0xFB

    @property
    def Power2(self) -> int:
        return (self.raw[13] >> 4) & 0x03

    @Power2.setter
    def Power2(self, value: int) -> None:
        self.raw[13] = (self.raw[13] & 0xCF) | ((value & 0x03) << 4)

    # Extended message map (bytes 7-20)
    # Byte 9 (extended)
    @property
    def OffTimeMins(self) -> int:
        return (self.raw[9] >> 4) & 0x07

    @OffTimeMins.setter
    def OffTimeMins(self, value: int) -> None:
        self.raw[9] = (self.raw[9] & 0x8F) | ((value & 0x07) << 4)

    @property
    def OffTimeHrs1(self) -> int:
        return (self.raw[9] >> 7) & 0x01

    @OffTimeHrs1.setter
    def OffTimeHrs1(self, value: bool) -> None:
        if value:
            self.raw[9] |= 0x80
        else:
            self.raw[9] &= 0x7F

    # Byte 10 (extended)
    @property
    def OffTimeHrs2(self) -> int:
        return self.raw[10] & 0x0F

    @OffTimeHrs2.setter
    def OffTimeHrs2(self, value: int) -> None:
        self.raw[10] = (self.raw[10] & 0xF0) | (value & 0x0F)

    @property
    def OnTimeMins(self) -> int:
        return (self.raw[10] >> 4) & 0x07

    @OnTimeMins.setter
    def OnTimeMins(self, value: int) -> None:
        self.raw[10] = (self.raw[10] & 0x8F) | ((value & 0x07) << 4)

    @property
    def OnTimeHrs1(self) -> int:
        return (self.raw[10] >> 7) & 0x01

    @OnTimeHrs1.setter
    def OnTimeHrs1(self, value: bool) -> None:
        if value:
            self.raw[10] |= 0x80
        else:
            self.raw[10] &= 0x7F

    # Byte 11 (extended)
    @property
    def OnTimeHrs2(self) -> int:
        return self.raw[11] & 0x0F

    @OnTimeHrs2.setter
    def OnTimeHrs2(self, value: int) -> None:
        self.raw[11] = (self.raw[11] & 0xF0) | (value & 0x0F)

    # Byte 12 (extended)
    @property
    def OffTimeDay(self) -> int:
        return self.raw[12] & 0x01

    @OffTimeDay.setter
    def OffTimeDay(self, value: bool) -> None:
        if value:
            self.raw[12] |= 0x01
        else:
            self.raw[12] &= 0xFE

    @property
    def OnTimerEnable(self) -> int:
        return (self.raw[12] >> 1) & 0x01

    @OnTimerEnable.setter
    def OnTimerEnable(self, value: bool) -> None:
        if value:
            self.raw[12] |= 0x02
        else:
            self.raw[12] &= 0xFD

    @property
    def OffTimerEnable(self) -> int:
        return (self.raw[12] >> 2) & 0x01

    @OffTimerEnable.setter
    def OffTimerEnable(self, value: bool) -> None:
        if value:
            self.raw[12] |= 0x04
        else:
            self.raw[12] &= 0xFB

    @property
    def Sleep12(self) -> int:
        return (self.raw[12] >> 3) & 0x01

    @Sleep12.setter
    def Sleep12(self, value: bool) -> None:
        if value:
            self.raw[12] |= 0x08
        else:
            self.raw[12] &= 0xF7

    @property
    def OnTimeDay(self) -> int:
        return (self.raw[12] >> 4) & 0x01

    @OnTimeDay.setter
    def OnTimeDay(self, value: bool) -> None:
        if value:
            self.raw[12] |= 0x10
        else:
            self.raw[12] &= 0xEF

    # Byte 15 (extended)
    @property
    def Sum3Lower(self) -> int:
        return (self.raw[15] >> 4) & 0x0F

    @Sum3Lower.setter
    def Sum3Lower(self, value: int) -> None:
        self.raw[15] = (self.raw[15] & 0x0F) | ((value & 0x0F) << 4)

    # Byte 16 (extended)
    @property
    def Sum3Upper(self) -> int:
        return self.raw[16] & 0x0F

    @Sum3Upper.setter
    def Sum3Upper(self, value: int) -> None:
        self.raw[16] = (self.raw[16] & 0xF0) | (value & 0x0F)


## Class for handling detailed Samsung A/C messages.
## EXACT translation from IRremoteESP8266 ir_Samsung.h and ir_Samsung.cpp
class IRSamsungAc:
    ## Class Constructor
    ## EXACT translation from IRremoteESP8266 ir_Samsung.cpp:281-289
    def __init__(self) -> None:
        self._: SamsungProtocol = SamsungProtocol()
        self._forceextended: bool = False
        self._lastsentpowerstate: bool = False
        self._OnTimerEnable: bool = False
        self._OffTimerEnable: bool = False
        self._Sleep: bool = False
        self._lastSleep: bool = False
        self._OnTimer: int = 0
        self._OffTimer: int = 0
        self._lastOnTimer: int = 0
        self._lastOffTimer: int = 0
        self.stateReset()

    ## Reset the internal state of the emulation.
    ## @param[in] extended A flag indicating if force sending a special extended
    ##   message with the first `send()` call.
    ## @param[in] initialPower Set the initial power state. True, on. False, off.
    ## EXACT translation from IRremoteESP8266 ir_Samsung.cpp:291-308
    def stateReset(self, extended: bool = True, initialPower: bool = True) -> None:
        kReset = [
            0x02,
            0x92,
            0x0F,
            0x00,
            0x00,
            0x00,
            0xF0,
            0x01,
            0x02,
            0xAE,
            0x71,
            0x00,
            0x15,
            0xF0,
        ]
        for i in range(kSamsungAcExtendedStateLength):
            if i < len(kReset):
                self._.raw[i] = kReset[i]
            else:
                self._.raw[i] = 0
        self._forceextended = extended
        self._lastsentpowerstate = initialPower
        self.setPower(initialPower)
        self._OnTimerEnable = False
        self._OffTimerEnable = False
        self._Sleep = False
        self._lastSleep = False
        self._OnTimer = self._OffTimer = self._lastOnTimer = self._lastOffTimer = 0

    ## Get the existing checksum for a given state section.
    ## @param[in] section The array to extract the checksum from.
    ## @return The existing checksum value.
    ## @see https://github.com/crankyoldgit/IRremoteESP8266/issues/1538#issuecomment-894645947
    ## EXACT translation from IRremoteESP8266 ir_Samsung.cpp:313-320
    @staticmethod
    def getSectionChecksum(section: List[int]) -> int:
        kLowNibble = 0
        kNibbleSize = 4
        kHighNibble = 4
        return (((section[2] >> kLowNibble) & 0x0F) << kNibbleSize) + (
            (section[1] >> kHighNibble) & 0x0F
        )

    ## Calculate the checksum for a given state section.
    ## @param[in] section The array to calc the checksum of.
    ## @return The calculated checksum value.
    ## @see https://github.com/crankyoldgit/IRremoteESP8266/issues/1538#issuecomment-894645947
    ## EXACT translation from IRremoteESP8266 ir_Samsung.cpp:322-338
    @staticmethod
    def calcSectionChecksum(section: List[int]) -> int:
        def countBits(data, bits):
            """Count the number of bits set"""
            count = 0
            for i in range(bits):
                if data & (1 << i):
                    count += 1
            return count

        kLowNibble = 0
        kNibbleSize = 4
        kHighNibble = 4

        sum_val = 0

        sum_val += countBits(section[0], 8)  # Include the entire first byte
        # The lower half of the second byte.
        sum_val += countBits((section[1] >> kLowNibble) & 0x0F, 8)
        # The upper half of the third byte.
        sum_val += countBits((section[2] >> kHighNibble) & 0x0F, 8)
        # The next 4 bytes.
        for i in range(3, 7):
            sum_val += countBits(section[i], 8)
        # Bitwise invert the result.
        return sum_val ^ 0xFF

    ## Verify the checksum is valid for a given state.
    ## @param[in] state The array to verify the checksum of.
    ## @param[in] length The length/size of the array.
    ## @return true, if the state has a valid checksum. Otherwise, false.
    ## EXACT translation from IRremoteESP8266 ir_Samsung.cpp:340-355
    @staticmethod
    def validChecksum(state: List[int], length: int = kSamsungAcStateLength) -> bool:
        result = True
        maxlength = (
            kSamsungAcExtendedStateLength if length > kSamsungAcExtendedStateLength else length
        )
        offset = 0
        while offset + kSamsungAcSectionLength <= maxlength:
            result &= IRSamsungAc.getSectionChecksum(
                state[offset:]
            ) == IRSamsungAc.calcSectionChecksum(state[offset:])
            offset += kSamsungAcSectionLength
        return result

    ## Update the checksum for the internal state.
    ## EXACT translation from IRremoteESP8266 ir_Samsung.cpp:357-368
    def checksum(self) -> None:
        kHighNibble = 4
        kNibbleSize = 4
        kLowNibble = 0

        sectionsum = self.calcSectionChecksum(self._.raw)
        self._.Sum1Upper = (sectionsum >> kHighNibble) & 0x0F
        self._.Sum1Lower = (sectionsum >> kLowNibble) & 0x0F
        sectionsum = self.calcSectionChecksum(self._.raw[kSamsungAcSectionLength:])
        self._.Sum2Upper = (sectionsum >> kHighNibble) & 0x0F
        self._.Sum2Lower = (sectionsum >> kLowNibble) & 0x0F
        sectionsum = self.calcSectionChecksum(self._.raw[kSamsungAcSectionLength * 2 :])
        self._.Sum3Upper = (sectionsum >> kHighNibble) & 0x0F
        self._.Sum3Lower = (sectionsum >> kLowNibble) & 0x0F

    ## Get a PTR to the internal state/code for this protocol.
    ## @return PTR to a code for this protocol based on the current internal state.
    ## EXACT translation from IRremoteESP8266 ir_Samsung.cpp:442-447
    def getRaw(self) -> List[int]:
        self.checksum()
        return self._.raw

    ## Set the internal state from a valid code for this protocol.
    ## @param[in] new_code A valid code for this protocol.
    ## @param[in] length The length/size of the new_code array.
    ## EXACT translation from IRremoteESP8266 ir_Samsung.cpp:449-465
    def setRaw(self, new_code: List[int], length: int = kSamsungAcStateLength) -> None:
        for i in range(min(length, kSamsungAcExtendedStateLength)):
            self._.raw[i] = new_code[i]
        # Shrink the extended state into a normal state.
        if length > kSamsungAcStateLength:
            self._OnTimerEnable = bool(self._.OnTimerEnable)
            self._OffTimerEnable = bool(self._.OffTimerEnable)
            self._Sleep = bool(self._.Sleep5 and self._.Sleep12)
            self._OnTimer = self._getOnTimer()
            self._OffTimer = self._getOffTimer()
            for i in range(kSamsungAcStateLength, length):
                self._.raw[i - kSamsungAcSectionLength] = self._.raw[i]

    ## Set the requested power state of the A/C to on.
    ## EXACT translation from IRremoteESP8266 ir_Samsung.cpp:467-468
    def on(self) -> None:
        self.setPower(True)

    ## Set the requested power state of the A/C to off.
    ## EXACT translation from IRremoteESP8266 ir_Samsung.cpp:470-471
    def off(self) -> None:
        self.setPower(False)

    ## Change the power setting.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## EXACT translation from IRremoteESP8266 ir_Samsung.cpp:473-477
    def setPower(self, on: bool) -> None:
        self._.Power1 = 0b11 if on else 0b00
        self._.Power2 = 0b11 if on else 0b00

    ## Get the value of the current power setting.
    ## @return true, the setting is on. false, the setting is off.
    ## EXACT translation from IRremoteESP8266 ir_Samsung.cpp:479-483
    def getPower(self) -> bool:
        return self._.Power1 == 0b11 and self._.Power2 == 0b11

    ## Set the temperature.
    ## @param[in] temp The temperature in degrees celsius.
    ## EXACT translation from IRremoteESP8266 ir_Samsung.cpp:485-492
    def setTemp(self, temp: int) -> None:
        newtemp = max(kSamsungAcMinTemp, temp)
        newtemp = min(kSamsungAcMaxTemp, newtemp)
        self._.Temp = newtemp - kSamsungAcMinTemp

    ## Get the current temperature setting.
    ## @return The current setting for temp. in degrees celsius.
    ## EXACT translation from IRremoteESP8266 ir_Samsung.cpp:494-497
    def getTemp(self) -> int:
        return self._.Temp + kSamsungAcMinTemp

    ## Set the operating mode of the A/C.
    ## @param[in] mode The desired operating mode.
    ## EXACT translation from IRremoteESP8266 ir_Samsung.cpp:499-515
    def setMode(self, mode: int) -> None:
        # If we get an unexpected mode, default to AUTO.
        newmode = mode
        if newmode > kSamsungAcHeat:
            newmode = kSamsungAcAuto
        self._.Mode = newmode

        # Auto mode has a special fan setting valid only in auto mode.
        if newmode == kSamsungAcAuto:
            self._.Fan = kSamsungAcFanAuto2
        else:
            # Non-Auto can't have this fan setting
            if self._.Fan == kSamsungAcFanAuto2:
                self._.Fan = kSamsungAcFanAuto  # Default to something safe.

    ## Get the operating mode setting of the A/C.
    ## @return The current operating mode setting.
    ## EXACT translation from IRremoteESP8266 ir_Samsung.cpp:517-521
    def getMode(self) -> int:
        return self._.Mode

    ## Set the speed of the fan.
    ## @param[in] speed The desired setting.
    ## EXACT translation from IRremoteESP8266 ir_Samsung.cpp:523-541
    def setFan(self, speed: int) -> None:
        if speed in [
            kSamsungAcFanAuto,
            kSamsungAcFanLow,
            kSamsungAcFanMed,
            kSamsungAcFanHigh,
            kSamsungAcFanTurbo,
        ]:
            if self._.Mode == kSamsungAcAuto:
                return  # Not valid in Auto mode.
        elif speed == kSamsungAcFanAuto2:  # Special fan setting for when in Auto mode.
            if self._.Mode != kSamsungAcAuto:
                return
        else:
            return
        self._.Fan = speed

    ## Get the current fan speed setting.
    ## @return The current fan speed/mode.
    ## EXACT translation from IRremoteESP8266 ir_Samsung.cpp:543-547
    def getFan(self) -> int:
        return self._.Fan

    ## Get the vertical swing setting of the A/C.
    ## @return true, the setting is on. false, the setting is off.
    ## EXACT translation from IRremoteESP8266 ir_Samsung.cpp:549-557
    def getSwing(self) -> bool:
        if self._.Swing in [kSamsungAcSwingV, kSamsungAcSwingBoth]:
            return True
        return False

    ## Set the vertical swing setting of the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## EXACT translation from IRremoteESP8266 ir_Samsung.cpp:559-570
    def setSwing(self, on: bool) -> None:
        if self._.Swing in [kSamsungAcSwingBoth, kSamsungAcSwingH]:
            self._.Swing = kSamsungAcSwingBoth if on else kSamsungAcSwingH
        else:
            self._.Swing = kSamsungAcSwingV if on else kSamsungAcSwingOff

    ## Get the horizontal swing setting of the A/C.
    ## @return true, the setting is on. false, the setting is off.
    ## EXACT translation from IRremoteESP8266 ir_Samsung.cpp:572-580
    def getSwingH(self) -> bool:
        if self._.Swing in [kSamsungAcSwingH, kSamsungAcSwingBoth]:
            return True
        return False

    ## Set the horizontal swing setting of the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## EXACT translation from IRremoteESP8266 ir_Samsung.cpp:582-593
    def setSwingH(self, on: bool) -> None:
        if self._.Swing in [kSamsungAcSwingV, kSamsungAcSwingBoth]:
            self._.Swing = kSamsungAcSwingBoth if on else kSamsungAcSwingV
        else:
            self._.Swing = kSamsungAcSwingH if on else kSamsungAcSwingOff

    ## Get the Beep toggle setting of the A/C.
    ## @return true, the setting is on. false, the setting is off.
    ## EXACT translation from IRremoteESP8266 ir_Samsung.cpp:595-597
    def getBeep(self) -> bool:
        return bool(self._.BeepToggle)

    ## Set the Beep toggle setting of the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## EXACT translation from IRremoteESP8266 ir_Samsung.cpp:599-601
    def setBeep(self, on: bool) -> None:
        self._.BeepToggle = on

    ## Get the Clean toggle setting of the A/C.
    ## @return true, the setting is on. false, the setting is off.
    ## EXACT translation from IRremoteESP8266 ir_Samsung.cpp:603-607
    def getClean(self) -> bool:
        return bool(self._.CleanToggle10 and self._.CleanToggle11)

    ## Set the Clean toggle setting of the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## EXACT translation from IRremoteESP8266 ir_Samsung.cpp:609-614
    def setClean(self, on: bool) -> None:
        self._.CleanToggle10 = on
        self._.CleanToggle11 = on

    ## Get the Quiet setting of the A/C.
    ## @return true, the setting is on. false, the setting is off.
    ## EXACT translation from IRremoteESP8266 ir_Samsung.cpp:616-618
    def getQuiet(self) -> bool:
        return bool(self._.Quiet)

    ## Set the Quiet setting of the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## EXACT translation from IRremoteESP8266 ir_Samsung.cpp:620-629
    def setQuiet(self, on: bool) -> None:
        self._.Quiet = on
        if on:
            # Quiet mode seems to set fan speed to auto.
            self.setFan(kSamsungAcFanAuto)
            self.setPowerful(False)  # Quiet 'on' is mutually exclusive to Powerful.

    ## Get the Powerful (Turbo) setting of the A/C.
    ## @return true, the setting is on. false, the setting is off.
    ## EXACT translation from IRremoteESP8266 ir_Samsung.cpp:631-636
    def getPowerful(self) -> bool:
        return (self._.FanSpecial == kSamsungAcPowerfulOn) and (self._.Fan == kSamsungAcFanTurbo)

    ## Set the Powerful (Turbo) setting of the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## EXACT translation from IRremoteESP8266 ir_Samsung.cpp:638-649
    def setPowerful(self, on: bool) -> None:
        off_value = (
            self._.FanSpecial if (self.getBreeze() or self.getEcono()) else kSamsungAcFanSpecialOff
        )
        self._.FanSpecial = kSamsungAcPowerfulOn if on else off_value
        if on:
            # Powerful mode sets fan speed to Turbo.
            self.setFan(kSamsungAcFanTurbo)
            self.setQuiet(False)  # Powerful 'on' is mutually exclusive to Quiet.

    ## Are the vanes closed over the fan outlet, to stop direct wind? Aka. WindFree
    ## @return true, the setting is on. false, the setting is off.
    ## @see https://github.com/crankyoldgit/IRremoteESP8266/issues/1062
    ## EXACT translation from IRremoteESP8266 ir_Samsung.cpp:651-657
    def getBreeze(self) -> bool:
        return (self._.FanSpecial == kSamsungAcBreezeOn) and (
            self._.Fan == kSamsungAcFanAuto and not self.getSwing()
        )

    ## Closes the vanes over the fan outlet, to stop direct wind. Aka. WindFree
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## @see https://github.com/crankyoldgit/IRremoteESP8266/issues/1062
    ## EXACT translation from IRremoteESP8266 ir_Samsung.cpp:659-671
    def setBreeze(self, on: bool) -> None:
        off_value = (
            self._.FanSpecial
            if (self.getPowerful() or self.getEcono())
            else kSamsungAcFanSpecialOff
        )
        self._.FanSpecial = kSamsungAcBreezeOn if on else off_value
        if on:
            self.setFan(kSamsungAcFanAuto)
            self.setSwing(False)

    ## Get the current Economy (Eco) setting of the A/C.
    ## @return true, the setting is on. false, the setting is off.
    ## EXACT translation from IRremoteESP8266 ir_Samsung.cpp:673-678
    def getEcono(self) -> bool:
        return (self._.FanSpecial == kSamsungAcEconoOn) and (
            self._.Fan == kSamsungAcFanAuto and self.getSwing()
        )

    ## Set the current Economy (Eco) setting of the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## EXACT translation from IRremoteESP8266 ir_Samsung.cpp:680-691
    def setEcono(self, on: bool) -> None:
        off_value = (
            self._.FanSpecial
            if (self.getBreeze() or self.getPowerful())
            else kSamsungAcFanSpecialOff
        )
        self._.FanSpecial = kSamsungAcEconoOn if on else off_value
        if on:
            self.setFan(kSamsungAcFanAuto)
            self.setSwing(True)

    ## Get the Display (Light/LED) setting of the A/C.
    ## @return true, the setting is on. false, the setting is off.
    ## EXACT translation from IRremoteESP8266 ir_Samsung.cpp:693-695
    def getDisplay(self) -> bool:
        return bool(self._.Display)

    ## Set the Display (Light/LED) setting of the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## EXACT translation from IRremoteESP8266 ir_Samsung.cpp:697-699
    def setDisplay(self, on: bool) -> None:
        self._.Display = on

    ## Get the Ion (Filter) setting of the A/C.
    ## @return true, the setting is on. false, the setting is off.
    ## EXACT translation from IRremoteESP8266 ir_Samsung.cpp:701-703
    def getIon(self) -> bool:
        return bool(self._.Ion)

    ## Set the Ion (Filter) setting of the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## EXACT translation from IRremoteESP8266 ir_Samsung.cpp:705-707
    def setIon(self, on: bool) -> None:
        self._.Ion = on

    ## Get the On Timer setting of the A/C from a raw extended state.
    ## @return The Nr. of minutes the On Timer is set for.
    ## EXACT translation from IRremoteESP8266 ir_Samsung.cpp:709-714
    def _getOnTimer(self) -> int:
        if self._.OnTimeDay:
            return 24 * 60
        return (self._.OnTimeHrs2 * 2 + self._.OnTimeHrs1) * 60 + self._.OnTimeMins * 10

    ## Set the current On Timer value of the A/C into the raw extended state.
    ## EXACT translation from IRremoteESP8266 ir_Samsung.cpp:716-728
    def _setOnTimer(self) -> None:
        self._.OnTimerEnable = self._OnTimerEnable = self._OnTimer > 0
        self._.OnTimeDay = self._OnTimer >= 24 * 60
        if self._.OnTimeDay:
            self._.OnTimeHrs2 = self._.OnTimeHrs1 = self._.OnTimeMins = 0
            return
        self._.OnTimeMins = (self._OnTimer % 60) // 10
        hours = self._OnTimer // 60
        self._.OnTimeHrs1 = hours & 0b1
        self._.OnTimeHrs2 = hours >> 1

    ## Get the Off Timer setting of the A/C from a raw extended state.
    ## @return The Nr. of minutes the Off Timer is set for.
    ## EXACT translation from IRremoteESP8266 ir_Samsung.cpp:730-735
    def _getOffTimer(self) -> int:
        if self._.OffTimeDay:
            return 24 * 60
        return (self._.OffTimeHrs2 * 2 + self._.OffTimeHrs1) * 60 + self._.OffTimeMins * 10

    ## Set the current Off Timer value of the A/C into the raw extended state.
    ## EXACT translation from IRremoteESP8266 ir_Samsung.cpp:737-749
    def _setOffTimer(self) -> None:
        self._.OffTimerEnable = self._OffTimerEnable = self._OffTimer > 0
        self._.OffTimeDay = self._OffTimer >= 24 * 60
        if self._.OffTimeDay:
            self._.OffTimeHrs2 = self._.OffTimeHrs1 = self._.OffTimeMins = 0
            return
        self._.OffTimeMins = (self._OffTimer % 60) // 10
        hours = self._OffTimer // 60
        self._.OffTimeHrs1 = hours & 0b1
        self._.OffTimeHrs2 = hours >> 1

    ## Set the current Sleep Timer value of the A/C into the raw extended state.
    ## EXACT translation from IRremoteESP8266 ir_Samsung.cpp:751-757
    def _setSleepTimer(self) -> None:
        self._setOffTimer()
        # The Sleep mode/timer should only be engaged if an off time has been set.
        self._.Sleep5 = self._Sleep and self._OffTimerEnable
        self._.Sleep12 = self._.Sleep5

    ## Get the On Timer setting of the A/C.
    ## @return The Nr. of minutes the On Timer is set for.
    ## EXACT translation from IRremoteESP8266 ir_Samsung.cpp:759-761
    def getOnTimer(self) -> int:
        return self._OnTimer

    ## Get the Off Timer setting of the A/C.
    ## @return The Nr. of minutes the Off Timer is set for.
    ## @note Sleep & Off Timer share the same timer.
    ## EXACT translation from IRremoteESP8266 ir_Samsung.cpp:763-768
    def getOffTimer(self) -> int:
        return 0 if self._Sleep else self._OffTimer

    ## Get the Sleep Timer setting of the A/C.
    ## @return The Nr. of minutes the Off Timer is set for.
    ## @note Sleep & Off Timer share the same timer.
    ## EXACT translation from IRremoteESP8266 ir_Samsung.cpp:770-775
    def getSleepTimer(self) -> int:
        return self._OffTimer if self._Sleep else 0

    ## Set the On Timer value of the A/C.
    ## @param[in] nr_of_mins The number of minutes the timer should be.
    ## @note The timer time only has a resolution of 10 mins.
    ## @note Setting the On Timer active will cancel the Sleep timer/setting.
    ## EXACT translation from IRremoteESP8266 ir_Samsung.cpp:777-789
    def setOnTimer(self, nr_of_mins: int) -> None:
        # Limit to one day, and round down to nearest 10 min increment.
        self._OnTimer = (min(nr_of_mins, 24 * 60) // 10) * 10
        self._OnTimerEnable = self._OnTimer > 0
        if self._OnTimer:
            self._Sleep = False

    ## Set the Off Timer value of the A/C.
    ## @param[in] nr_of_mins The number of minutes the timer should be.
    ## @note The timer time only has a resolution of 10 mins.
    ## @note Setting the Off Timer active will cancel the Sleep timer/setting.
    ## EXACT translation from IRremoteESP8266 ir_Samsung.cpp:791-800
    def setOffTimer(self, nr_of_mins: int) -> None:
        # Limit to one day, and round down to nearest 10 min increment.
        self._OffTimer = (min(nr_of_mins, 24 * 60) // 10) * 10
        self._OffTimerEnable = self._OffTimer > 0
        if self._OffTimer:
            self._Sleep = False

    ## Set the Sleep Timer value of the A/C.
    ## @param[in] nr_of_mins The number of minutes the timer should be.
    ## @note The timer time only has a resolution of 10 mins.
    ## @note Sleep timer acts as an Off timer, and cancels any On Timer.
    ## EXACT translation from IRremoteESP8266 ir_Samsung.cpp:802-812
    def setSleepTimer(self, nr_of_mins: int) -> None:
        # Limit to one day, and round down to nearest 10 min increment.
        self._OffTimer = (min(nr_of_mins, 24 * 60) // 10) * 10
        if self._OffTimer:
            self.setOnTimer(0)  # Clear the on timer if set.
        self._Sleep = self._OffTimer > 0
        self._OffTimerEnable = self._Sleep


## Decode the supplied Samsung A/C message.
## Status: Stable / Known to be working.
## @param[in,out] results Ptr to the data to decode & where to store the result
## @param[in] offset The starting index to use when attempting to decode the
##   raw data. Typically/Defaults to kStartOffset.
## @param[in] nbits The number of data bits to expect.
## @param[in] strict Flag indicating if we should perform strict matching.
## @return True if it can decode it, false if it can't.
## @see https://github.com/crankyoldgit/IRremoteESP8266/issues/505
## EXACT translation from IRremoteESP8266 ir_Samsung.cpp:945-996
def decodeSamsungAC(
    results, offset: int = 1, nbits: int = kSamsungAcStateLength * 8, strict: bool = True
) -> bool:
    """
    Decode the supplied Samsung A/C message.
    EXACT translation from IRremoteESP8266 IRrecv::decodeSamsungAC (ir_Samsung.cpp:955-995)
    """
    from app.core.ir_protocols.ir_recv import _matchGeneric, matchMark, matchSpace, kHeader, kFooter

    if results.rawlen < 2 * nbits + kHeader * 3 + kFooter * 2 - 1 + offset:
        return False  # Can't possibly be a valid Samsung A/C message.
    if nbits != kSamsungAcStateLength * 8 and nbits != kSamsungAcExtendedStateLength * 8:
        return False

    # Message Header
    if not matchMark(results.rawbuf[offset], kSamsungAcBitMark, 25, 50):
        return False
    offset += 1
    if not matchSpace(results.rawbuf[offset], kSamsungAcHdrSpace, 25, 50):
        return False
    offset += 1

    # Section(s)
    pos = 0
    while pos <= (nbits // 8) - kSamsungAcSectionLength:
        # Section Header + Section Data (7 bytes) + Section Footer
        used = _matchGeneric(
            data_ptr=results.rawbuf[offset:],
            result_bits_ptr=None,
            result_bytes_ptr=results.state[pos:],
            use_bits=False,
            remaining=results.rawlen - offset,
            nbits=kSamsungAcSectionLength * 8,
            hdrmark=kSamsungAcSectionMark,
            hdrspace=kSamsungAcSectionSpace,
            onemark=kSamsungAcBitMark,
            onespace=kSamsungAcOneSpace,
            zeromark=kSamsungAcBitMark,
            zerospace=kSamsungAcZeroSpace,
            footermark=kSamsungAcBitMark,
            footerspace=kSamsungAcSectionGap,
            atleast=pos + kSamsungAcSectionLength >= nbits // 8,
            tolerance=25,
            excess=0,
            MSBfirst=False,
        )
        if used == 0:
            return False
        offset += used
        pos += kSamsungAcSectionLength

    # Compliance
    if strict:
        # Is the checksum valid?
        if not IRSamsungAc.validChecksum(results.state, nbits // 8):
            return False

    # Success
    # results.decode_type = SAMSUNG_AC
    results.bits = nbits
    # No need to record the state as we stored it as we decoded it.
    # As we use result->state, we don't record value, address, or command as it
    # is a union data type.
    return True
