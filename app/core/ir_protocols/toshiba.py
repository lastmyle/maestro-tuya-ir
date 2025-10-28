# Copyright 2017 David Conran
# Python translation: Direct conversion from C++ with NO optimizations

## @file
## @brief Support for Toshiba A/C protocols.
## Direct translation from IRremoteESP8266 ir_Toshiba.cpp and ir_Toshiba.h

from typing import List
import copy

# Constants - Timing values (from ir_Toshiba.cpp lines 25-33)
kToshibaAcHdrMark = 4400
kToshibaAcHdrSpace = 4300
kToshibaAcBitMark = 580
kToshibaAcOneSpace = 1600
kToshibaAcZeroSpace = 490
kToshibaAcMinGap = 4600     # WH-UB03NJ remote
kToshibaAcUsualGap = 7400   # Others

# State length constants (from ir_Toshiba.h)
kToshibaACStateLengthShort = 6   # Short message (56 bits)
kToshibaACStateLength = 9        # Normal message (72 bits)
kToshibaACStateLengthLong = 10   # Long message (80 bits)
kToshibaAcLengthByte = 2
kToshibaAcMinLength = 6
kToshibaAcInvertedLength = 4

# Swing constants (from ir_Toshiba.h lines 96-99)
kToshibaAcSwingStep = 0      # 0b000
kToshibaAcSwingOn = 1        # 0b001
kToshibaAcSwingOff = 2       # 0b010
kToshibaAcSwingToggle = 4    # 0b100

# Temperature constants (from ir_Toshiba.h lines 101-102)
kToshibaAcMinTemp = 17  # Celsius
kToshibaAcMaxTemp = 30  # Celsius

# Mode constants (from ir_Toshiba.h lines 104-109)
kToshibaAcAuto = 0  # 0b000
kToshibaAcCool = 1  # 0b001
kToshibaAcDry = 2   # 0b010
kToshibaAcHeat = 3  # 0b011
kToshibaAcFan = 4   # 0b100
kToshibaAcOff = 7   # 0b111

# Fan speed constants (from ir_Toshiba.h lines 110-113)
kToshibaAcFanAuto = 0  # 0b000
kToshibaAcFanMin = 1   # 0b001
kToshibaAcFanMed = 3   # 0b011
kToshibaAcFanMax = 5   # 0b101

# Special mode constants (from ir_Toshiba.h lines 115-116)
kToshibaAcTurboOn = 1   # 0b01
kToshibaAcEconoOn = 3   # 0b11

# Model constants (from ir_Toshiba.h lines 118-119)
kToshibaAcRemoteA = 0  # 0b0000
kToshibaAcRemoteB = 1  # 0b0001


def xorBytes(data: List[int], length: int) -> int:
    """XOR all bytes in array. EXACT translation from IRutils."""
    result = 0
    for i in range(length):
        result ^= data[i]
    return result & 0xFF


def invertBytePairs(data: List[int], length: int) -> None:
    """
    Invert byte pairs in-place.
    EXACT translation from IRutils::invertBytePairs
    """
    for i in range(1, length, 2):
        data[i] = data[i - 1] ^ 0xFF


def checkInvertedBytePairs(data: List[int], length: int) -> bool:
    """
    Check if byte pairs are inverted.
    EXACT translation from IRutils::checkInvertedBytePairs
    """
    for i in range(1, length, 2):
        if data[i] != (data[i - 1] ^ 0xFF):
            return False
    return True


## Native representation of a Toshiba A/C message.
## Direct translation of the C++ union/struct (ir_Toshiba.h lines 44-86)
class ToshibaProtocol:
    def __init__(self):
        # The state array
        self.raw = [0] * kToshibaACStateLengthLong

    # Byte 2 - Length field (bits 0-3)
    @property
    def Length(self) -> int:
        return self.raw[2] & 0x0F

    @Length.setter
    def Length(self, value: int) -> None:
        self.raw[2] = (self.raw[2] & 0xF0) | (value & 0x0F)

    # Byte 2 - Model field (bits 4-7)
    @property
    def Model(self) -> int:
        return (self.raw[2] >> 4) & 0x0F

    @Model.setter
    def Model(self, value: int) -> None:
        self.raw[2] = (self.raw[2] & 0x0F) | ((value & 0x0F) << 4)

    # Byte 4 - LongMsg bit (bit 3)
    @property
    def LongMsg(self) -> int:
        return (self.raw[4] >> 3) & 0x01

    @LongMsg.setter
    def LongMsg(self, value: bool) -> None:
        if value:
            self.raw[4] |= 0x08
        else:
            self.raw[4] &= 0xF7

    # Byte 4 - ShortMsg bit (bit 5)
    @property
    def ShortMsg(self) -> int:
        return (self.raw[4] >> 5) & 0x01

    @ShortMsg.setter
    def ShortMsg(self, value: bool) -> None:
        if value:
            self.raw[4] |= 0x20
        else:
            self.raw[4] &= 0xDF

    # Byte 5 - Swing field (bits 0-2)
    @property
    def Swing(self) -> int:
        return self.raw[5] & 0x07

    @Swing.setter
    def Swing(self, value: int) -> None:
        self.raw[5] = (self.raw[5] & 0xF8) | (value & 0x07)

    # Byte 5 - Temp field (bits 4-7)
    @property
    def Temp(self) -> int:
        return (self.raw[5] >> 4) & 0x0F

    @Temp.setter
    def Temp(self, value: int) -> None:
        self.raw[5] = (self.raw[5] & 0x0F) | ((value & 0x0F) << 4)

    # Byte 6 - Mode field (bits 0-2)
    @property
    def Mode(self) -> int:
        return self.raw[6] & 0x07

    @Mode.setter
    def Mode(self, value: int) -> None:
        self.raw[6] = (self.raw[6] & 0xF8) | (value & 0x07)

    # Byte 6 - Fan field (bits 5-7)
    @property
    def Fan(self) -> int:
        return (self.raw[6] >> 5) & 0x07

    @Fan.setter
    def Fan(self, value: int) -> None:
        self.raw[6] = (self.raw[6] & 0x1F) | ((value & 0x07) << 5)

    # Byte 7 - Filter bit (bit 4)
    @property
    def Filter(self) -> int:
        return (self.raw[7] >> 4) & 0x01

    @Filter.setter
    def Filter(self, value: bool) -> None:
        if value:
            self.raw[7] |= 0x10
        else:
            self.raw[7] &= 0xEF

    # Byte 8 - EcoTurbo field (all 8 bits)
    @property
    def EcoTurbo(self) -> int:
        return self.raw[8] & 0xFF

    @EcoTurbo.setter
    def EcoTurbo(self, value: int) -> None:
        self.raw[8] = value & 0xFF


## Send a Toshiba A/C message.
## Status: STABLE / Working.
## Direct translation from IRremoteESP8266 IRsend::sendToshibaAC (ir_Toshiba.cpp lines 46-57)
def sendToshibaAC(data: List[int], nbytes: int, repeat: int = 0) -> List[int]:
    """
    Send a Toshiba A/C formatted message.
    EXACT translation from IRremoteESP8266 IRsend::sendToshibaAC

    Returns timing array instead of transmitting via hardware.
    """
    from app.core.ir_protocols.ir_send import sendGeneric

    return sendGeneric(
        headermark=kToshibaAcHdrMark,
        headerspace=kToshibaAcHdrSpace,
        onemark=kToshibaAcBitMark,
        onespace=kToshibaAcOneSpace,
        zeromark=kToshibaAcBitMark,
        zerospace=kToshibaAcZeroSpace,
        footermark=kToshibaAcBitMark,
        gap=kToshibaAcUsualGap,
        dataptr=data,
        nbytes=nbytes,
        frequency=38,
        MSBfirst=True,
        repeat=repeat,
        dutycycle=50
    )


## Class for handling detailed Toshiba A/C messages.
## Direct translation from C++ IRToshibaAC class (ir_Toshiba.h lines 134-202)
class IRToshibaAC:
    ## Class Constructor
    def __init__(self) -> None:
        self._: ToshibaProtocol = ToshibaProtocol()
        self.backup = [0] * kToshibaACStateLengthLong
        self._prev_mode = kToshibaAcAuto
        self._send_swing = False
        self._swing_mode = kToshibaAcSwingOff
        self.stateReset()

    ## Reset the state of the remote to a known good state/sequence.
    ## Direct translation from ir_Toshiba.cpp lines 69-77
    def stateReset(self) -> None:
        # Reset state (ir_Toshiba.cpp lines 71-73)
        kReset = [0xF2, 0x0D, 0x03, 0xFC, 0x01]
        for i in range(len(kReset)):
            self._.raw[i] = kReset[i]
        # Clear remaining bytes
        for i in range(len(kReset), len(self._.raw)):
            self._.raw[i] = 0
        self.setTemp(22)  # Remote defaults to 22C
        self.setSwing(kToshibaAcSwingOff)
        self._prev_mode = self.getMode()

    ## Get the length of the supplied Toshiba state per it's protocol structure.
    ## Direct translation from ir_Toshiba.cpp lines 105-111
    @staticmethod
    def getInternalStateLength(state: List[int], size: int) -> int:
        if size < kToshibaAcLengthByte:
            return 0
        # Extract the last 4 bits (ir_Toshiba.cpp line 109)
        return min((state[kToshibaAcLengthByte] & 0xF) + kToshibaAcMinLength,
                   kToshibaACStateLengthLong)

    ## Get the length of the current internal state per the protocol structure.
    ## Direct translation from ir_Toshiba.cpp lines 115-117
    def getStateLength(self) -> int:
        return self.getInternalStateLength(self._.raw, kToshibaACStateLengthLong)

    ## Set the internal length of the current internal state per the protocol.
    ## Direct translation from ir_Toshiba.cpp lines 121-124
    def setStateLength(self, size: int) -> None:
        if size < kToshibaAcMinLength:
            return
        self._.Length = size - kToshibaAcMinLength

    ## Make a copy of the internal code-form A/C state.
    ## Direct translation from ir_Toshiba.cpp lines 127-129
    def _backupState(self) -> None:
        self.backup = self._.raw[:]

    ## Recover the internal code-form A/C state from the backup.
    ## Direct translation from ir_Toshiba.cpp lines 132-134
    def _restoreState(self) -> None:
        self._.raw = self.backup[:]

    ## Calculate the checksum for a given state.
    ## Direct translation from ir_Toshiba.cpp lines 157-160
    @staticmethod
    def calcChecksum(state: List[int], length: int) -> int:
        return xorBytes(state, length - 1) if length else 0

    ## Verify the checksum is valid for a given state.
    ## Direct translation from ir_Toshiba.cpp lines 166-171
    @staticmethod
    def validChecksum(state: List[int], length: int) -> bool:
        return (length >= kToshibaAcMinLength and
                state[length - 1] == IRToshibaAC.calcChecksum(state, length) and
                checkInvertedBytePairs(state, kToshibaAcInvertedLength) and
                IRToshibaAC.getInternalStateLength(state, length) == length)

    ## Calculate & set the checksum for the current internal state.
    ## Direct translation from ir_Toshiba.cpp lines 175-186
    def checksum(self, length: int = kToshibaACStateLength) -> None:
        if length >= kToshibaAcMinLength:
            # Set/clear the short msg bit (ir_Toshiba.cpp line 179)
            self._.ShortMsg = (self.getStateLength() == kToshibaACStateLengthShort)
            # Set/clear the long msg bit (ir_Toshiba.cpp line 181)
            self._.LongMsg = (self.getStateLength() == kToshibaACStateLengthLong)
            invertBytePairs(self._.raw, kToshibaAcInvertedLength)
            # Always do the Xor checksum LAST! (ir_Toshiba.cpp line 184)
            self._.raw[length - 1] = self.calcChecksum(self._.raw, length)

    ## Set the requested power state of the A/C to on.
    ## Direct translation from ir_Toshiba.cpp line 189
    def on(self) -> None:
        self.setPower(True)

    ## Set the requested power state of the A/C to off.
    ## Direct translation from ir_Toshiba.cpp line 192
    def off(self) -> None:
        self.setPower(False)

    ## Change the power setting.
    ## Direct translation from ir_Toshiba.cpp lines 196-203
    def setPower(self, on: bool) -> None:
        if on:  # On
            # If not already on, pick the last non-off mode used
            if not self.getPower():
                self.setMode(self._prev_mode)
        else:  # Off
            self.setMode(kToshibaAcOff)

    ## Get the value of the current power setting.
    ## Direct translation from ir_Toshiba.cpp lines 207-209
    def getPower(self) -> bool:
        return self.getMode(True) != kToshibaAcOff

    ## Set the temperature.
    ## Direct translation from ir_Toshiba.cpp lines 213-217
    def setTemp(self, degrees: int) -> None:
        temp = max(kToshibaAcMinTemp, degrees)
        temp = min(kToshibaAcMaxTemp, temp)
        self._.Temp = temp - kToshibaAcMinTemp

    ## Get the current temperature setting.
    ## Direct translation from ir_Toshiba.cpp line 221
    def getTemp(self) -> int:
        return self._.Temp + kToshibaAcMinTemp

    ## Set the speed of the fan.
    ## Direct translation from ir_Toshiba.cpp lines 225-232
    def setFan(self, speed: int) -> None:
        fan = speed
        # Bounds check
        if fan > kToshibaAcFanMax:
            fan = kToshibaAcFanMax  # Set the fan to maximum if out of range
        if fan > kToshibaAcFanAuto:
            fan += 1
        self._.Fan = fan

    ## Get the current fan speed setting.
    ## Direct translation from ir_Toshiba.cpp lines 236-240
    def getFan(self) -> int:
        fan = self._.Fan
        if fan == kToshibaAcFanAuto:
            return kToshibaAcFanAuto
        return fan - 1

    ## Get the swing setting of the A/C.
    ## Direct translation from ir_Toshiba.cpp lines 245-247
    def getSwing(self, raw: bool = True) -> int:
        return self._.Swing if raw else self._swing_mode

    ## Set the swing setting of the A/C.
    ## Direct translation from ir_Toshiba.cpp lines 251-261
    def setSwing(self, setting: int) -> None:
        if setting in [kToshibaAcSwingStep, kToshibaAcSwingOn,
                      kToshibaAcSwingOff, kToshibaAcSwingToggle]:
            self._send_swing = True
            self._swing_mode = setting
            if self.getStateLength() == kToshibaACStateLengthShort:
                self._.Swing = setting

    ## Get the operating mode setting of the A/C.
    ## Direct translation from ir_Toshiba.cpp lines 267-274
    def getMode(self, raw: bool = False) -> int:
        mode = self._.Mode
        if raw:
            return mode
        if mode == kToshibaAcOff:
            return self._prev_mode
        return mode

    ## Set the operating mode of the A/C.
    ## Direct translation from ir_Toshiba.cpp lines 280-300
    def setMode(self, mode: int) -> None:
        if mode != self._prev_mode:
            # Changing mode or power turns Econo & Turbo to off
            # Setting the internal message length to "normal" will do that
            self.setStateLength(kToshibaACStateLength)
        if mode in [kToshibaAcAuto, kToshibaAcCool, kToshibaAcDry,
                   kToshibaAcHeat, kToshibaAcFan]:
            self._prev_mode = mode
            self._.Mode = mode
        elif mode == kToshibaAcOff:
            self._.Mode = mode
        else:
            # Default to AUTO
            self._prev_mode = kToshibaAcAuto
            self._.Mode = kToshibaAcAuto

    ## Get the Turbo (Powerful) setting of the A/C.
    ## Direct translation from ir_Toshiba.cpp lines 304-308
    def getTurbo(self) -> bool:
        if self.getStateLength() == kToshibaACStateLengthLong:
            return self._.EcoTurbo == kToshibaAcTurboOn
        return False

    ## Set the Turbo (Powerful) setting of the A/C.
    ## Direct translation from ir_Toshiba.cpp lines 313-320
    def setTurbo(self, on: bool) -> None:
        if on:
            self._.EcoTurbo = kToshibaAcTurboOn
            self.setStateLength(kToshibaACStateLengthLong)
        else:
            if not self.getEcono():
                self.setStateLength(kToshibaACStateLength)

    ## Get the Economy mode setting of the A/C.
    ## Direct translation from ir_Toshiba.cpp lines 324-328
    def getEcono(self) -> bool:
        if self.getStateLength() == kToshibaACStateLengthLong:
            return self._.EcoTurbo == kToshibaAcEconoOn
        return False

    ## Set the Economy mode setting of the A/C.
    ## Direct translation from ir_Toshiba.cpp lines 333-340
    def setEcono(self, on: bool) -> None:
        if on:
            self._.EcoTurbo = kToshibaAcEconoOn
            self.setStateLength(kToshibaACStateLengthLong)
        else:
            if not self.getTurbo():
                self.setStateLength(kToshibaACStateLength)

    ## Get the filter (Pure/Ion Filter) setting of the A/C.
    ## Direct translation from ir_Toshiba.cpp lines 344-346
    def getFilter(self) -> bool:
        return bool(self._.Filter) if (self.getStateLength() >= kToshibaACStateLength) else False

    ## Set the filter (Pure/Ion Filter) setting of the A/C.
    ## Direct translation from ir_Toshiba.cpp lines 350-353
    def setFilter(self, on: bool) -> None:
        self._.Filter = on
        if on:
            self.setStateLength(min(kToshibaACStateLength, self.getStateLength()))

    ## Get a PTR to the internal state/code for this protocol.
    ## Direct translation from ir_Toshiba.cpp lines 139-142
    def getRaw(self) -> List[int]:
        self.checksum(self.getStateLength())
        return self._.raw

    ## Set the internal state from a valid code for this protocol.
    ## Direct translation from ir_Toshiba.cpp lines 147-151
    def setRaw(self, newState: List[int], length: int = kToshibaACStateLength) -> None:
        for i in range(min(length, len(self._.raw))):
            self._.raw[i] = newState[i]
        self._prev_mode = self.getMode()
        self._send_swing = True

    ## Get the model information currently known.
    ## Direct translation from ir_Toshiba.cpp lines 501-507
    def getModel(self) -> int:
        if self._.Model == kToshibaAcRemoteB:
            return 1  # kToshibaGenericRemote_B
        else:
            return 0  # kToshibaGenericRemote_A

    ## Set the current model for the remote.
    ## Direct translation from ir_Toshiba.cpp lines 512-521
    def setModel(self, model: int) -> None:
        if model == 1:  # kToshibaGenericRemote_B
            self._.Model = kToshibaAcRemoteB
        else:
            self._.Model = kToshibaAcRemoteA


## Decode the supplied Toshiba A/C message.
## Status:  STABLE / Working.
## Direct translation from IRremoteESP8266 IRrecv::decodeToshibaAC (ir_Toshiba.cpp lines 532-567)
def decodeToshibaAC(results, offset: int = 1, nbits: int = kToshibaACStateLength * 8,
                    strict: bool = True, _tolerance: int = 25) -> bool:
    """
    Decode a Toshiba A/C IR message.
    EXACT translation from IRremoteESP8266 IRrecv::decodeToshibaAC
    """
    from app.core.ir_protocols.ir_recv import kHeader, kFooter, kMarkExcess, _matchGeneric

    # Compliance
    if strict:
        # Must be called with the correct nr. of bits (ir_Toshiba.cpp lines 536-543)
        kToshibaACBits = kToshibaACStateLength * 8  # 72
        kToshibaACBitsShort = kToshibaACStateLengthShort * 8  # 48
        kToshibaACBitsLong = kToshibaACStateLengthLong * 8  # 80
        if nbits not in [kToshibaACBits, kToshibaACBitsShort, kToshibaACBitsLong]:
            return False

    # Match Header + Data + Footer (ir_Toshiba.cpp lines 546-553)
    used = _matchGeneric(
        data_ptr=results.rawbuf[offset:],
        result_bits_ptr=None,
        result_bytes_ptr=results.state,
        use_bits=False,
        remaining=results.rawlen - offset,
        nbits=nbits,
        hdrmark=kToshibaAcHdrMark,
        hdrspace=kToshibaAcHdrSpace,
        onemark=kToshibaAcBitMark,
        onespace=kToshibaAcOneSpace,
        zeromark=kToshibaAcBitMark,
        zerospace=kToshibaAcZeroSpace,
        footermark=kToshibaAcBitMark,
        footerspace=kToshibaAcMinGap,
        atleast=True,
        tolerance=_tolerance,
        excess=kMarkExcess,
        MSBfirst=True
    )
    if used == 0:
        return False

    # Compliance
    if strict:
        # Check that the checksum of the message is correct (ir_Toshiba.cpp line 557)
        if not IRToshibaAC.validChecksum(results.state, nbits // 8):
            return False

    # Success (ir_Toshiba.cpp lines 560-566)
    results.bits = nbits
    return True
