# Copyright 2009 Ken Shirriff
# Copyright 2017, 2019 David Conran
# Python translation: Direct conversion from C++ with NO optimizations

## @file
## @brief Support for Sharp protocols.
## Direct translation from IRremoteESP8266 ir_Sharp.cpp and ir_Sharp.h

from typing import List, Optional

# Ref: http://www.sbprojects.net/knowledge/ir/sharp.htm
# Ref: http://lirc.sourceforge.net/remotes/sharp/GA538WJSA
# Ref: http://www.mwftr.com/ucF08/LEC14%20PIC%20IR.pdf
# Ref: http://www.hifi-remote.com/johnsfine/DecodeIR.html#Sharp
# Ref: GlobalCache's IR Control Tower data.
# Ref: https://github.com/crankyoldgit/IRremoteESP8266/issues/638
# Ref: https://github.com/ToniA/arduino-heatpumpir/blob/master/SharpHeatpumpIR.cpp

# Constants - Sharp (basic protocol)
# period time = 1/38000Hz = 26.316 microseconds.
kSharpTick = 26
kSharpBitMarkTicks = 10
kSharpBitMark = kSharpBitMarkTicks * kSharpTick
kSharpOneSpaceTicks = 70
kSharpOneSpace = kSharpOneSpaceTicks * kSharpTick
kSharpZeroSpaceTicks = 30
kSharpZeroSpace = kSharpZeroSpaceTicks * kSharpTick
kSharpGapTicks = 1677
kSharpGap = kSharpGapTicks * kSharpTick

# Bit size constants
kSharpAddressBits = 5
kSharpCommandBits = 8
kSharpBits = 15

# Address(5) + Command(8) + Expansion(1) + Check(1)
kSharpToggleMask = (1 << (kSharpBits - kSharpAddressBits)) - 1
kSharpAddressMask = (1 << kSharpAddressBits) - 1
kSharpCommandMask = (1 << kSharpCommandBits) - 1

# Constants - Sharp AC
kSharpAcHdrMark = 3800
kSharpAcHdrSpace = 1900
kSharpAcBitMark = 470
kSharpAcZeroSpace = 500
kSharpAcOneSpace = 1400
kSharpAcGap = 43000  # kDefaultMessageGap
kSharpAcStateLength = 13
kSharpAcBits = kSharpAcStateLength * 8

kSharpAcByteTemp = 4
kSharpAcMinTemp = 15  # Celsius
kSharpAcMaxTemp = 30  # Celsius

# Power constants
kSharpAcPowerUnknown = 0  # 0b0000
kSharpAcPowerOnFromOff = 1  # 0b0001
kSharpAcPowerOff = 2  # 0b0010
kSharpAcPowerOn = 3  # 0b0011 (Normal)
kSharpAcPowerSetSpecialOn = 6  # 0b0110
kSharpAcPowerSetSpecialOff = 7  # 0b0111
kSharpAcPowerTimerSetting = 8  # 0b1000

# Mode constants
kSharpAcAuto = 0b00  # A907 only
kSharpAcFan = 0b00  # A705 only
kSharpAcDry = 0b11
kSharpAcCool = 0b10
kSharpAcHeat = 0b01  # A907 only

# Fan constants
kSharpAcFanAuto = 0b010  # 2
kSharpAcFanMin = 0b100  # 4 (FAN1)
kSharpAcFanMed = 0b011  # 3 (FAN2)
kSharpAcFanA705Low = 0b011  # 3 (A903 too)
kSharpAcFanHigh = 0b101  # 5 (FAN3)
kSharpAcFanA705Med = 0b101  # 5 (A903 too)
kSharpAcFanMax = 0b111  # 7 (FAN4)

# Timer constants
kSharpAcTimerIncrement = 30  # Mins
kSharpAcTimerHoursOff = 0b0000
kSharpAcTimerHoursMax = 0b1100  # 12
kSharpAcOffTimerType = 0b0
kSharpAcOnTimerType = 0b1

# Swing constants
# Ref: https://github.com/crankyoldgit/IRremoteESP8266/discussions/1590#discussioncomment-1260213
kSharpAcSwingVIgnore = 0b000  # Don't change the swing setting.
kSharpAcSwingVHigh = 0b001  # 0° down. Similar to Cool Coanda.
kSharpAcSwingVOff = 0b010  # Stop & Go to last fixed pos.
kSharpAcSwingVMid = 0b011  # 30° down
kSharpAcSwingVLow = 0b100  # 45° down
kSharpAcSwingVLast = 0b101  # Same as kSharpAcSwingVOff.
kSharpAcSwingVLowest = 0b110
kSharpAcSwingVCoanda = kSharpAcSwingVLowest
kSharpAcSwingVToggle = 0b111  # Toggle Constant swinging on/off.

# Special constants
kSharpAcSpecialPower = 0x00
kSharpAcSpecialTurbo = 0x01
kSharpAcSpecialTempEcono = 0x04
kSharpAcSpecialFan = 0x05
kSharpAcSpecialSwing = 0x06
kSharpAcSpecialTimer = 0xC0
kSharpAcSpecialTimerHalfHour = 0xDE

# Model enums
SHARP_A907 = 0
SHARP_A705 = 1
SHARP_A903 = 2


# Bit manipulation helpers
def GETBITS8(data: int, offset: int, size: int) -> int:
    """Extract bits from uint8"""
    mask = (1 << size) - 1
    return (data >> offset) & mask


def GETBITS16(data: int, offset: int, size: int) -> int:
    """Extract bits from uint16"""
    mask = (1 << size) - 1
    return (data >> offset) & mask


def reverseBits(data: int, nbits: int) -> int:
    """Reverse the order of bits in an integer"""
    result = 0
    for i in range(nbits):
        result = (result << 1) | (data & 1)
        data >>= 1
    return result


def xorBytes(data: List[int], length: int) -> int:
    """XOR all bytes in data array"""
    result = 0
    for i in range(length):
        result ^= data[i]
    return result


## Native representation of a Sharp A/C message.
## This is a direct translation of the C++ union/struct
class SharpProtocol:
    def __init__(self):
        # The state array (13 bytes for Sharp AC)
        self.raw = [0] * kSharpAcStateLength

    # Byte 4
    @property
    def Temp(self) -> int:
        return self.raw[4] & 0x0F

    @Temp.setter
    def Temp(self, value: int) -> None:
        self.raw[4] = (self.raw[4] & 0xF0) | (value & 0x0F)

    @property
    def Model(self) -> int:
        return (self.raw[4] >> 4) & 0x01

    @Model.setter
    def Model(self, value: bool) -> None:
        if value:
            self.raw[4] |= 0x10
        else:
            self.raw[4] &= 0xEF

    # Byte 5
    @property
    def PowerSpecial(self) -> int:
        return (self.raw[5] >> 4) & 0x0F

    @PowerSpecial.setter
    def PowerSpecial(self, value: int) -> None:
        self.raw[5] = (self.raw[5] & 0x0F) | ((value & 0x0F) << 4)

    # Byte 6
    @property
    def Mode(self) -> int:
        return self.raw[6] & 0x03

    @Mode.setter
    def Mode(self, value: int) -> None:
        self.raw[6] = (self.raw[6] & 0xFC) | (value & 0x03)

    @property
    def Clean(self) -> int:
        return (self.raw[6] >> 3) & 0x01

    @Clean.setter
    def Clean(self, value: bool) -> None:
        if value:
            self.raw[6] |= 0x08
        else:
            self.raw[6] &= 0xF7

    @property
    def Fan(self) -> int:
        return (self.raw[6] >> 4) & 0x07

    @Fan.setter
    def Fan(self, value: int) -> None:
        self.raw[6] = (self.raw[6] & 0x8F) | ((value & 0x07) << 4)

    # Byte 7
    @property
    def TimerHours(self) -> int:
        return self.raw[7] & 0x0F

    @TimerHours.setter
    def TimerHours(self, value: int) -> None:
        self.raw[7] = (self.raw[7] & 0xF0) | (value & 0x0F)

    @property
    def TimerType(self) -> int:
        return (self.raw[7] >> 6) & 0x01

    @TimerType.setter
    def TimerType(self, value: bool) -> None:
        if value:
            self.raw[7] |= 0x40
        else:
            self.raw[7] &= 0xBF

    @property
    def TimerEnabled(self) -> int:
        return (self.raw[7] >> 7) & 0x01

    @TimerEnabled.setter
    def TimerEnabled(self, value: bool) -> None:
        if value:
            self.raw[7] |= 0x80
        else:
            self.raw[7] &= 0x7F

    # Byte 8
    @property
    def Swing(self) -> int:
        return self.raw[8] & 0x07

    @Swing.setter
    def Swing(self, value: int) -> None:
        self.raw[8] = (self.raw[8] & 0xF8) | (value & 0x07)

    # Byte 10
    @property
    def Special(self) -> int:
        return self.raw[10]

    @Special.setter
    def Special(self, value: int) -> None:
        self.raw[10] = value & 0xFF

    # Byte 11
    @property
    def Ion(self) -> int:
        return (self.raw[11] >> 2) & 0x01

    @Ion.setter
    def Ion(self, value: bool) -> None:
        if value:
            self.raw[11] |= 0x04
        else:
            self.raw[11] &= 0xFB

    @property
    def Model2(self) -> int:
        return (self.raw[11] >> 4) & 0x01

    @Model2.setter
    def Model2(self, value: bool) -> None:
        if value:
            self.raw[11] |= 0x10
        else:
            self.raw[11] &= 0xEF

    # Byte 12
    @property
    def Sum(self) -> int:
        return (self.raw[12] >> 4) & 0x0F

    @Sum.setter
    def Sum(self, value: int) -> None:
        self.raw[12] = (self.raw[12] & 0x0F) | ((value & 0x0F) << 4)


## Send a (raw) Sharp message
## Status: STABLE / Working fine.
## EXACT translation from IRremoteESP8266 IRsend::sendSharpRaw (ir_Sharp.cpp lines 67-86)
def sendSharpRaw(data: int, nbits: int = kSharpBits, repeat: int = 0) -> List[int]:
    """
    Send a (raw) Sharp message.
    EXACT translation from IRremoteESP8266 IRsend::sendSharpRaw

    Returns timing array instead of transmitting via hardware.
    """
    from app.core.ir_protocols.ir_send import sendGeneric

    all_timings = []
    tempdata = data

    for i in range(repeat + 1):
        # Protocol demands that the data be sent twice; once normally,
        # then with all but the address bits inverted.
        for n in range(2):
            timings = sendGeneric(
                headermark=0,
                headerspace=0,  # No Header
                onemark=kSharpBitMark,
                onespace=kSharpOneSpace,
                zeromark=kSharpBitMark,
                zerospace=kSharpZeroSpace,
                footermark=kSharpBitMark,
                gap=kSharpGap,
                dataptr=[tempdata],
                nbytes=0,
                nbits=nbits,
                frequency=38,
                MSBfirst=True,
                repeat=0,
                dutycycle=33,
            )
            all_timings.extend(timings)
            # Invert the data per protocol. This is always called twice, so it's
            # returned to original upon exiting the inner loop.
            tempdata ^= kSharpToggleMask

    return all_timings


## Encode a (raw) Sharp message from its components.
## Status: STABLE / Works okay.
## EXACT translation from IRremoteESP8266 IRsend::encodeSharp (ir_Sharp.cpp lines 102-118)
def encodeSharp(
    address: int, command: int, expansion: int = 1, check: int = 0, MSBfirst: bool = True
) -> int:
    """
    Encode a (raw) Sharp message from its components.
    EXACT translation from IRremoteESP8266 IRsend::encodeSharp
    """
    # Mask any unexpected bits.
    tempaddress = GETBITS16(address, 0, kSharpAddressBits)
    tempcommand = GETBITS16(command, 0, kSharpCommandBits)
    tempexpansion = GETBITS16(expansion, 0, 1)
    tempcheck = GETBITS16(check, 0, 1)

    if not MSBfirst:  # Correct bit order if needed.
        tempaddress = reverseBits(tempaddress, kSharpAddressBits)
        tempcommand = reverseBits(tempcommand, kSharpCommandBits)

    # Concatenate all the bits.
    return (
        (tempaddress << (kSharpCommandBits + 2))
        | (tempcommand << 2)
        | (tempexpansion << 1)
        | tempcheck
    )


## Send a Sharp message
## Status: DEPRECATED / Previously working fine.
## EXACT translation from IRremoteESP8266 IRsend::sendSharp (ir_Sharp.cpp lines 137-140)
def sendSharp(address: int, command: int, nbits: int = kSharpBits, repeat: int = 0) -> List[int]:
    """
    Send a Sharp message.
    EXACT translation from IRremoteESP8266 IRsend::sendSharp
    """
    return sendSharpRaw(encodeSharp(address, command, 1, 0, True), nbits, repeat)


## Decode the supplied Sharp message.
## Status: STABLE / Working fine.
## EXACT translation from IRremoteESP8266 IRrecv::decodeSharp (ir_Sharp.cpp lines 159-219)
def decodeSharp(
    results, offset: int = 1, nbits: int = kSharpBits, strict: bool = True, expansion: bool = True
) -> bool:
    """
    Decode the supplied Sharp message.
    EXACT translation from IRremoteESP8266 IRrecv::decodeSharp
    """
    from app.core.ir_protocols.ir_recv import kHeader, kFooter, kMarkExcess, _matchGeneric

    if results.rawlen <= 2 * nbits + kFooter - 1 + offset:
        return False  # Not enough entries to be a Sharp message.

    # Compliance
    if strict:
        if nbits != kSharpBits:
            return False  # Request is out of spec.

    data = 0

    # Match Data + Footer
    used = _matchGeneric(
        data_ptr=results.rawbuf[offset:],
        result_bits_ptr=None,
        result_bytes_ptr=None,
        use_bits=True,
        result_value=data,
        remaining=results.rawlen - offset,
        nbits=nbits,
        hdrmark=0,
        hdrspace=0,  # No Header
        onemark=kSharpBitMark,
        onespace=kSharpOneSpace,
        zeromark=kSharpBitMark,
        zerospace=kSharpZeroSpace,
        footermark=kSharpBitMark,
        footerspace=kSharpGap,
        atleast=True,
        tolerance=35,
        excess=kMarkExcess,
        MSBfirst=True,
    )
    if used == 0:
        return False

    offset += used

    # Compliance
    if strict:
        # Check the state of the expansion bit is what we expect.
        if ((data & 0b10) >> 1) != expansion:
            return False
        # The check bit should be cleared in a normal message.
        if data & 0b1:
            return False

    # Success
    results.decode_type = "SHARP"
    results.bits = nbits
    results.value = data
    # Address & command are actually transmitted in LSB first order.
    results.address = reverseBits(data, nbits) & kSharpAddressMask
    results.command = reverseBits((data >> 2) & kSharpCommandMask, kSharpCommandBits)
    return True


## Send a Sharp A/C message.
## Status: Alpha / Untested.
## EXACT translation from IRremoteESP8266 IRsend::sendSharpAc (ir_Sharp.cpp lines 230-240)
def sendSharpAc(data: List[int], nbytes: int = kSharpAcStateLength, repeat: int = 0) -> List[int]:
    """
    Send a Sharp A/C message.
    EXACT translation from IRremoteESP8266 IRsend::sendSharpAc

    Returns timing array instead of transmitting via hardware.
    """
    if nbytes < kSharpAcStateLength:
        return []  # Not enough bytes to send a proper message.

    from app.core.ir_protocols.ir_send import sendGeneric

    return sendGeneric(
        headermark=kSharpAcHdrMark,
        headerspace=kSharpAcHdrSpace,
        onemark=kSharpAcBitMark,
        onespace=kSharpAcOneSpace,
        zeromark=kSharpAcBitMark,
        zerospace=kSharpAcZeroSpace,
        footermark=kSharpAcBitMark,
        gap=kSharpAcGap,
        dataptr=data,
        nbytes=nbytes,
        frequency=38000,
        MSBfirst=False,
        repeat=repeat,
        dutycycle=50,
    )


## Calculate the checksum for a given state.
## EXACT translation from IRremoteESP8266 IRSharpAc::calcChecksum (ir_Sharp.cpp lines 266-271)
def calcChecksumSharpAc(state: List[int], length: int = kSharpAcStateLength) -> int:
    """
    Calculate the checksum for a given state.
    EXACT translation from IRremoteESP8266 IRSharpAc::calcChecksum
    """
    xorsum = xorBytes(state, length - 1)
    xorsum ^= GETBITS8(state[length - 1], 0, 4)  # kLowNibble, kNibbleSize
    xorsum ^= GETBITS8(xorsum, 4, 4)  # kHighNibble, kNibbleSize
    return GETBITS8(xorsum, 0, 4)  # kLowNibble, kNibbleSize


## Verify the checksum is valid for a given state.
## EXACT translation from IRremoteESP8266 IRSharpAc::validChecksum (ir_Sharp.cpp lines 277-280)
def validChecksumSharpAc(state: List[int], length: int = kSharpAcStateLength) -> bool:
    """
    Verify the checksum is valid for a given state.
    EXACT translation from IRremoteESP8266 IRSharpAc::validChecksum
    """
    return GETBITS8(state[length - 1], 4, 4) == calcChecksumSharpAc(state, length)


## Class for handling detailed Sharp A/C messages.
## Direct translation from C++ IRSharpAc class
class IRSharpAc:
    ## Class Constructor
    def __init__(self, model: int = SHARP_A907) -> None:
        self._: SharpProtocol = SharpProtocol()
        self._temp: int = 0
        self._mode: int = 0
        self._fan: int = 0
        self._model: int = model
        self.stateReset()

    ## Reset the internal state to a fixed known good state.
    ## EXACT translation from ir_Sharp.cpp lines 288-297
    def stateReset(self) -> None:
        reset = [0xAA, 0x5A, 0xCF, 0x10, 0x00, 0x01, 0x00, 0x00, 0x08, 0x80, 0x00, 0xE0, 0x01]
        for i in range(kSharpAcStateLength):
            self._.raw[i] = reset[i]
        self._temp = self.getTemp()
        self._mode = self._.Mode
        self._fan = self._.Fan
        self._model = self.getModel(True)

    ## Calculate and set the checksum values for the internal state.
    ## EXACT translation from ir_Sharp.cpp lines 283-285
    def checksum(self) -> None:
        self._.Sum = calcChecksumSharpAc(self._.raw)

    ## Get a PTR to the internal state/code for this protocol.
    ## EXACT translation from ir_Sharp.cpp lines 301-304
    def getRaw(self) -> List[int]:
        self.checksum()  # Ensure correct settings before sending.
        return self._.raw

    ## Set the internal state from a valid code for this protocol.
    ## EXACT translation from ir_Sharp.cpp lines 309-312
    def setRaw(self, new_code: List[int], length: int = kSharpAcStateLength) -> None:
        for i in range(min(length, kSharpAcStateLength)):
            self._.raw[i] = new_code[i]
        self._model = self.getModel(True)

    ## Set the model of the A/C to emulate.
    ## EXACT translation from ir_Sharp.cpp lines 316-330
    def setModel(self, model: int) -> None:
        if model == SHARP_A705 or model == SHARP_A903:
            self._model = model
            self._.Model = True
        else:
            self._model = SHARP_A907
            self._.Model = False

        self._.Model2 = self._model != SHARP_A907
        # Redo the operating mode as some models don't support all modes.
        self.setMode(self._.Mode)

    ## Get/Detect the model of the A/C.
    ## EXACT translation from ir_Sharp.cpp lines 335-347
    def getModel(self, raw: bool = False) -> int:
        if raw:
            if self._.Model2:
                if self._.Model:
                    return SHARP_A705
                else:
                    return SHARP_A903
            else:
                return SHARP_A907
        return self._model

    ## Set the value of the Power Special setting without any checks.
    ## EXACT translation from ir_Sharp.cpp lines 351-353
    def setPowerSpecial(self, value: int) -> None:
        self._.PowerSpecial = value

    ## Get the value of the Power Special setting.
    ## EXACT translation from ir_Sharp.cpp lines 357-359
    def getPowerSpecial(self) -> int:
        return self._.PowerSpecial

    ## Clear the "special"/non-normal bits in the power section.
    ## EXACT translation from ir_Sharp.cpp lines 363-365
    def clearPowerSpecial(self) -> None:
        self.setPowerSpecial(self._.PowerSpecial & kSharpAcPowerOn)

    ## Is one of the special power states in use?
    ## EXACT translation from ir_Sharp.cpp lines 369-376
    def isPowerSpecial(self) -> bool:
        if self._.PowerSpecial in [
            kSharpAcPowerSetSpecialOff,
            kSharpAcPowerSetSpecialOn,
            kSharpAcPowerTimerSetting,
        ]:
            return True
        return False

    ## Set the requested power state of the A/C to on.
    ## EXACT translation from ir_Sharp.cpp line 379
    def on(self) -> None:
        self.setPower(True)

    ## Set the requested power state of the A/C to off.
    ## EXACT translation from ir_Sharp.cpp line 382
    def off(self) -> None:
        self.setPower(False)

    ## Change the power setting, including the previous power state.
    ## EXACT translation from ir_Sharp.cpp lines 387-393
    def setPower(self, on: bool, prev_on: bool = True) -> None:
        if on:
            self.setPowerSpecial(kSharpAcPowerOn if prev_on else kSharpAcPowerOnFromOff)
        else:
            self.setPowerSpecial(kSharpAcPowerOff)

        # Power operations are incompatible with clean mode.
        if self._.Clean:
            self.setClean(False)
        self._.Special = kSharpAcSpecialPower

    ## Get the value of the current power setting.
    ## EXACT translation from ir_Sharp.cpp lines 397-403
    def getPower(self) -> bool:
        if self._.PowerSpecial in [kSharpAcPowerUnknown, kSharpAcPowerOff]:
            return False
        return True  # Everything else is "probably" on.

    ## Set the value of the Special (button/command?) setting.
    ## EXACT translation from ir_Sharp.cpp lines 407-421
    def setSpecial(self, mode: int) -> None:
        if mode in [
            kSharpAcSpecialPower,
            kSharpAcSpecialTurbo,
            kSharpAcSpecialTempEcono,
            kSharpAcSpecialFan,
            kSharpAcSpecialSwing,
            kSharpAcSpecialTimer,
            kSharpAcSpecialTimerHalfHour,
        ]:
            self._.Special = mode
        else:
            self._.Special = kSharpAcSpecialPower

    ## Get the value of the Special (button/command?) setting.
    ## EXACT translation from ir_Sharp.cpp line 425
    def getSpecial(self) -> int:
        return self._.Special

    ## Set the temperature.
    ## EXACT translation from ir_Sharp.cpp lines 430-452
    def setTemp(self, temp: int, save: bool = True) -> None:
        # Auto & Dry don't allow temp changes and have a special temp.
        if self._.Mode in [kSharpAcAuto, kSharpAcDry]:
            self._.raw[kSharpAcByteTemp] = 0
            return

        if self.getModel() == SHARP_A705:
            self._.raw[kSharpAcByteTemp] = 0xD0
        else:
            self._.raw[kSharpAcByteTemp] = 0xC0

        degrees = max(temp, kSharpAcMinTemp)
        degrees = min(degrees, kSharpAcMaxTemp)
        if save:
            self._temp = degrees
        self._.Temp = degrees - kSharpAcMinTemp
        self._.Special = kSharpAcSpecialTempEcono
        self.clearPowerSpecial()

    ## Get the current temperature setting.
    ## EXACT translation from ir_Sharp.cpp lines 456-458
    def getTemp(self) -> int:
        return self._.Temp + kSharpAcMinTemp

    ## Get the operating mode setting of the A/C.
    ## EXACT translation from ir_Sharp.cpp lines 462-464
    def getMode(self) -> int:
        return self._.Mode

    ## Set the operating mode of the A/C.
    ## EXACT translation from ir_Sharp.cpp lines 469-504
    def setMode(self, mode: int, save: bool = True) -> None:
        realMode = mode
        if mode == kSharpAcHeat:
            if self.getModel() in [SHARP_A705, SHARP_A903]:
                # These models have no heat mode, use Fan mode instead.
                realMode = kSharpAcFan

        if realMode in [kSharpAcAuto, kSharpAcDry]:
            # When Dry or Auto, Fan always 2(Auto)
            self.setFan(kSharpAcFanAuto, False)
            self._.Mode = realMode
        elif realMode in [kSharpAcCool, kSharpAcHeat]:
            self._.Mode = realMode
        else:
            self.setFan(kSharpAcFanAuto, False)
            self._.Mode = kSharpAcAuto

        # Dry/Auto have no temp setting. This step will enforce it.
        self.setTemp(self._temp, False)
        # Save the mode in case we need to revert to it. eg. Clean
        if save:
            self._mode = self._.Mode

        self._.Special = kSharpAcSpecialPower
        self.clearPowerSpecial()

    ## Set the speed of the fan.
    ## EXACT translation from ir_Sharp.cpp lines 509-525
    def setFan(self, speed: int, save: bool = True) -> None:
        if speed in [
            kSharpAcFanAuto,
            kSharpAcFanMin,
            kSharpAcFanMed,
            kSharpAcFanHigh,
            kSharpAcFanMax,
        ]:
            self._.Fan = speed
            if save:
                self._fan = speed
        else:
            self._.Fan = kSharpAcFanAuto
            self._fan = kSharpAcFanAuto

        self._.Special = kSharpAcSpecialFan
        self.clearPowerSpecial()

    ## Get the current fan speed setting.
    ## EXACT translation from ir_Sharp.cpp lines 529-531
    def getFan(self) -> int:
        return self._.Fan

    ## Get the Turbo setting of the A/C.
    ## EXACT translation from ir_Sharp.cpp lines 535-538
    def getTurbo(self) -> bool:
        return (self._.PowerSpecial == kSharpAcPowerSetSpecialOn) and (
            self._.Special == kSharpAcSpecialTurbo
        )

    ## Set the Turbo setting of the A/C.
    ## EXACT translation from ir_Sharp.cpp lines 545-549
    def setTurbo(self, on: bool) -> None:
        if on:
            self.setFan(kSharpAcFanMax)
        self.setPowerSpecial(kSharpAcPowerSetSpecialOn if on else kSharpAcPowerSetSpecialOff)
        self._.Special = kSharpAcSpecialTurbo

    ## Get the Vertical Swing setting of the A/C.
    ## EXACT translation from ir_Sharp.cpp line 553
    def getSwingV(self) -> int:
        return self._.Swing

    ## Set the Vertical Swing setting of the A/C.
    ## EXACT translation from ir_Sharp.cpp lines 563-584
    def setSwingV(self, position: int, force: bool = False) -> None:
        if position == kSharpAcSwingVCoanda:
            # Only allowed in Heat mode.
            if not force and self.getMode() != kSharpAcHeat:
                self.setSwingV(kSharpAcSwingVLow)  # Use the next lowest setting.
                return

        if position in [
            kSharpAcSwingVHigh,
            kSharpAcSwingVMid,
            kSharpAcSwingVLow,
            kSharpAcSwingVToggle,
            kSharpAcSwingVOff,
            kSharpAcSwingVLast,
            kSharpAcSwingVCoanda,
        ]:
            # All expected non-positions set the special bits.
            self._.Special = kSharpAcSpecialSwing

        if position in [
            kSharpAcSwingVIgnore,
            kSharpAcSwingVHigh,
            kSharpAcSwingVMid,
            kSharpAcSwingVLow,
            kSharpAcSwingVToggle,
            kSharpAcSwingVOff,
            kSharpAcSwingVLast,
            kSharpAcSwingVCoanda,
        ]:
            self._.Swing = position

    ## Get the (vertical) Swing Toggle setting of the A/C.
    ## EXACT translation from ir_Sharp.cpp lines 604-606
    def getSwingToggle(self) -> bool:
        return self.getSwingV() == kSharpAcSwingVToggle

    ## Set the (vertical) Swing Toggle setting of the A/C.
    ## EXACT translation from ir_Sharp.cpp lines 610-613
    def setSwingToggle(self, on: bool) -> None:
        self.setSwingV(kSharpAcSwingVToggle if on else kSharpAcSwingVIgnore)
        if on:
            self._.Special = kSharpAcSpecialSwing

    ## Get the Ion (Filter) setting of the A/C.
    ## EXACT translation from ir_Sharp.cpp line 617
    def getIon(self) -> bool:
        return bool(self._.Ion)

    ## Set the Ion (Filter) setting of the A/C.
    ## EXACT translation from ir_Sharp.cpp lines 621-625
    def setIon(self, on: bool) -> None:
        self._.Ion = on
        self.clearPowerSpecial()
        if on:
            self._.Special = kSharpAcSpecialSwing

    ## Get the Economical mode toggle setting of the A/C.
    ## EXACT translation from ir_Sharp.cpp lines 630-633
    def _getEconoToggle(self) -> bool:
        return (self._.PowerSpecial == kSharpAcPowerSetSpecialOn) and (
            self._.Special == kSharpAcSpecialTempEcono
        )

    ## Set the Economical mode toggle setting of the A/C.
    ## EXACT translation from ir_Sharp.cpp lines 639-642
    def _setEconoToggle(self, on: bool) -> None:
        if on:
            self._.Special = kSharpAcSpecialTempEcono
        self.setPowerSpecial(kSharpAcPowerSetSpecialOn if on else kSharpAcPowerSetSpecialOff)

    ## Set the Economical mode toggle setting of the A/C (A907 only).
    ## EXACT translation from ir_Sharp.cpp lines 648-650
    def setEconoToggle(self, on: bool) -> None:
        if self._model == SHARP_A907:
            self._setEconoToggle(on)

    ## Get the Economical mode toggle setting of the A/C (A907 only).
    ## EXACT translation from ir_Sharp.cpp lines 655-657
    def getEconoToggle(self) -> bool:
        return self._model == SHARP_A907 and self._getEconoToggle()

    ## Set the Light mode toggle setting of the A/C (not A907).
    ## EXACT translation from ir_Sharp.cpp lines 663-665
    def setLightToggle(self, on: bool) -> None:
        if self._model != SHARP_A907:
            self._setEconoToggle(on)

    ## Get the Light toggle setting of the A/C (not A907).
    ## EXACT translation from ir_Sharp.cpp lines 670-672
    def getLightToggle(self) -> bool:
        return self._model != SHARP_A907 and self._getEconoToggle()

    ## Get how long the timer is set for, in minutes.
    ## EXACT translation from ir_Sharp.cpp lines 676-680
    def getTimerTime(self) -> int:
        return self._.TimerHours * kSharpAcTimerIncrement * 2 + (
            kSharpAcTimerIncrement if self._.Special == kSharpAcSpecialTimerHalfHour else 0
        )

    ## Is the Timer enabled?
    ## EXACT translation from ir_Sharp.cpp line 684
    def getTimerEnabled(self) -> bool:
        return bool(self._.TimerEnabled)

    ## Get the current timer type.
    ## EXACT translation from ir_Sharp.cpp line 688
    def getTimerType(self) -> bool:
        return bool(self._.TimerType)

    ## Set or cancel the timer function.
    ## EXACT translation from ir_Sharp.cpp lines 695-710
    def setTimer(self, enable: bool, timer_type: bool, mins: int) -> None:
        half_hours = min(mins // kSharpAcTimerIncrement, kSharpAcTimerHoursMax * 2)
        if half_hours == 0:
            enable = False
        if not enable:
            half_hours = 0
            timer_type = kSharpAcOffTimerType

        self._.TimerEnabled = enable
        self._.TimerType = timer_type
        self._.TimerHours = half_hours // 2
        # Handle non-round hours.
        self._.Special = kSharpAcSpecialTimerHalfHour if (half_hours % 2) else kSharpAcSpecialTimer
        self.setPowerSpecial(kSharpAcPowerTimerSetting)

    ## Get the Clean setting of the A/C.
    ## EXACT translation from ir_Sharp.cpp lines 714-716
    def getClean(self) -> bool:
        return bool(self._.Clean)

    ## Set the Economical mode toggle setting of the A/C.
    ## EXACT translation from ir_Sharp.cpp lines 721-733
    def setClean(self, on: bool) -> None:
        # Clean mode appears to be just default dry mode, with an extra bit set.
        if on:
            self.setMode(kSharpAcDry, False)
            self.setPower(True, False)
        else:
            # Restore the previous operation mode & fan speed.
            self.setMode(self._mode, False)
            self.setFan(self._fan, False)

        self._.Clean = on
        self.clearPowerSpecial()


## Decode the supplied Sharp A/C message.
## Status: STABLE / Known working.
## EXACT translation from IRremoteESP8266 IRrecv::decodeSharpAc (ir_Sharp.cpp lines 949-977)
def decodeSharpAc(results, offset: int = 1, nbits: int = kSharpAcBits, strict: bool = True) -> bool:
    """
    Decode the supplied Sharp A/C message.
    EXACT translation from IRremoteESP8266 IRrecv::decodeSharpAc
    """
    from app.core.ir_protocols.ir_recv import kMarkExcess, _matchGeneric

    # Compliance
    if strict and nbits != kSharpAcBits:
        return False

    # Match Header + Data + Footer
    used = _matchGeneric(
        data_ptr=results.rawbuf[offset:],
        result_bits_ptr=None,
        result_bytes_ptr=results.state,
        use_bits=False,
        remaining=results.rawlen - offset,
        nbits=nbits,
        hdrmark=kSharpAcHdrMark,
        hdrspace=kSharpAcHdrSpace,
        onemark=kSharpAcBitMark,
        onespace=kSharpAcOneSpace,
        zeromark=kSharpAcBitMark,
        zerospace=kSharpAcZeroSpace,
        footermark=kSharpAcBitMark,
        footerspace=kSharpAcGap,
        atleast=True,
        tolerance=25,
        excess=kMarkExcess,
        MSBfirst=False,
    )
    if used == 0:
        return False

    offset += used

    # Compliance
    if strict:
        if not validChecksumSharpAc(results.state):
            return False

    # Success
    results.decode_type = "SHARP_AC"
    results.bits = nbits
    # No need to record the state as we stored it as we decoded it.
    return True
