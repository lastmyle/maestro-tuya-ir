# Copyright 2017 Schmolders
# Copyright 2019 crankyoldgit
# Copyright 2022 Mateusz Bronk (mbronk)
# Python translation: Direct conversion from C++ with NO optimizations

## @file
## @brief Argo A/C protocol.
## Direct translation from IRremoteESP8266 ir_Argo.cpp and ir_Argo.h
## @note This translation focuses on WREM-2 protocol (simpler variant)
## @note WREM-3 protocol is extremely complex with templates and would require
##       significant additional work to translate properly

from typing import List

# Constants - Timing values
kArgoHdrMark = 6400
kArgoHdrSpace = 3300
kArgoBitMark = 400
kArgoOneSpace = 2200
kArgoZeroSpace = 900
kArgoGap = 100000  # kDefaultMessageGap

# Sensor constants
kArgoSensorCheck = 52
kArgoSensorFixed = 0b011

# State length constants (from IRremoteESP8266.h)
kArgoStateLength = 12
kArgoShortStateLength = 4
kArgoBits = kArgoStateLength * 8  # 96 bits

# Preamble constants (WREM-2)
kArgoPreamble1 = 0b10101100
kArgoPreamble2 = 0b11110101
kArgoPost = 0b00000010

# Temperature constants
kArgoTempDelta = 4
kArgoMaxRoomTemp = 35  # Celsius
kArgoMinTemp = 10  # Celsius (delta +4)
kArgoMaxTemp = 32  # Celsius

# Mode constants (WREM-2 raw values)
kArgoCool = 0b000
kArgoDry = 0b001
kArgoAuto = 0b010
kArgoOff = 0b011
kArgoHeat = 0b100
kArgoHeatAuto = 0b101

# Fan speed constants (WREM-2 raw values)
kArgoFanAuto = 0
kArgoFan1 = 1
kArgoFan2 = 2
kArgoFan3 = 3

# Flap/SwingV constants (WREM-2 raw values)
kArgoFlapAuto = 0
kArgoFlap1 = 1
kArgoFlap2 = 2
kArgoFlap3 = 3
kArgoFlap4 = 4
kArgoFlap5 = 5
kArgoFlap6 = 6
kArgoFlapFull = 7


## Native representation of an Argo A/C message (WREM-2).
## This is a direct translation of the C++ union/struct
class ArgoProtocol:
    def __init__(self):
        # The state array (12 bytes for Argo WREM-2)
        self.raw = [0] * kArgoStateLength

    # Byte 0
    @property
    def Pre1(self) -> int:
        return self.raw[0]

    @Pre1.setter
    def Pre1(self, value: int) -> None:
        self.raw[0] = value & 0xFF

    # Byte 1
    @property
    def Pre2(self) -> int:
        return self.raw[1]

    @Pre2.setter
    def Pre2(self, value: int) -> None:
        self.raw[1] = value & 0xFF

    # Byte 2 (straddles into byte 3)
    @property
    def Mode(self) -> int:
        return (self.raw[2] >> 3) & 0x07

    @Mode.setter
    def Mode(self, value: int) -> None:
        self.raw[2] = (self.raw[2] & 0xC7) | ((value & 0x07) << 3)

    @property
    def Temp(self) -> int:
        return ((self.raw[2] & 0x07) << 2) | (self.raw[3] >> 6)

    @Temp.setter
    def Temp(self, value: int) -> None:
        self.raw[2] = (self.raw[2] & 0xF8) | ((value >> 2) & 0x07)
        self.raw[3] = (self.raw[3] & 0x3F) | ((value & 0x03) << 6)

    # Byte 3 (straddles into byte 4)
    @property
    def Fan(self) -> int:
        return (self.raw[3] >> 4) & 0x03

    @Fan.setter
    def Fan(self, value: int) -> None:
        self.raw[3] = (self.raw[3] & 0xCF) | ((value & 0x03) << 4)

    @property
    def RoomTemp(self) -> int:
        return ((self.raw[3] & 0x0F) << 1) | (self.raw[4] >> 7)

    @RoomTemp.setter
    def RoomTemp(self, value: int) -> None:
        self.raw[3] = (self.raw[3] & 0xF0) | ((value >> 1) & 0x0F)
        self.raw[4] = (self.raw[4] & 0x7F) | ((value & 0x01) << 7)

    @property
    def Flap(self) -> int:
        return (self.raw[4] >> 4) & 0x07

    @Flap.setter
    def Flap(self, value: int) -> None:
        self.raw[4] = (self.raw[4] & 0x8F) | ((value & 0x07) << 4)

    # Byte 9
    @property
    def Night(self) -> int:
        return (self.raw[9] >> 2) & 0x01

    @Night.setter
    def Night(self, value: bool) -> None:
        if value:
            self.raw[9] |= 0x04
        else:
            self.raw[9] &= 0xFB

    @property
    def Max(self) -> int:
        return (self.raw[9] >> 3) & 0x01

    @Max.setter
    def Max(self, value: bool) -> None:
        if value:
            self.raw[9] |= 0x08
        else:
            self.raw[9] &= 0xF7

    @property
    def Power(self) -> int:
        return (self.raw[9] >> 5) & 0x01

    @Power.setter
    def Power(self, value: bool) -> None:
        if value:
            self.raw[9] |= 0x20
        else:
            self.raw[9] &= 0xDF

    @property
    def iFeel(self) -> int:
        return (self.raw[9] >> 7) & 0x01

    @iFeel.setter
    def iFeel(self, value: bool) -> None:
        if value:
            self.raw[9] |= 0x80
        else:
            self.raw[9] &= 0x7F

    # Byte 10 (straddles into byte 11)
    @property
    def Post(self) -> int:
        return self.raw[10] & 0x03

    @Post.setter
    def Post(self, value: int) -> None:
        self.raw[10] = (self.raw[10] & 0xFC) | (value & 0x03)

    @property
    def Sum(self) -> int:
        return ((self.raw[10] & 0xFC) >> 2) | ((self.raw[11] & 0x3F) << 6)

    @Sum.setter
    def Sum(self, value: int) -> None:
        self.raw[10] = (self.raw[10] & 0x03) | ((value & 0x3F) << 2)
        self.raw[11] = (self.raw[11] & 0xC0) | ((value >> 6) & 0x3F)

    # Short message (iFeel) format
    @property
    def SensorT(self) -> int:
        return (self.raw[2] >> 3) & 0x1F

    @SensorT.setter
    def SensorT(self, value: int) -> None:
        self.raw[2] = (self.raw[2] & 0x07) | ((value & 0x1F) << 3)

    @property
    def CheckHi(self) -> int:
        return self.raw[2] & 0x07

    @CheckHi.setter
    def CheckHi(self, value: int) -> None:
        self.raw[2] = (self.raw[2] & 0xF8) | (value & 0x07)

    @property
    def Fixed(self) -> int:
        return self.raw[3] & 0x07

    @Fixed.setter
    def Fixed(self, value: int) -> None:
        self.raw[3] = (self.raw[3] & 0xF8) | (value & 0x07)

    @property
    def CheckLo(self) -> int:
        return (self.raw[3] >> 3) & 0x1F

    @CheckLo.setter
    def CheckLo(self, value: int) -> None:
        self.raw[3] = (self.raw[3] & 0x07) | ((value & 0x1F) << 3)


## Calculate the checksum for a given state (WREM-2).
## EXACT translation from IRremoteESP8266 IRArgoACBase<ArgoProtocol>::calcChecksum
## (ir_Argo.cpp lines 277-283)
def calcChecksum(state: List[int], length: int = kArgoStateLength) -> int:
    """
    Calculate checksum for Argo WREM-2 protocol.
    EXACT translation from IRremoteESP8266 IRArgoACBase<ArgoProtocol>::calcChecksum
    """
    # Corresponds to byte 11 being constant 0b01
    # Only add up bytes to 9. byte 10 is 0b01 constant anyway.
    # Assume that argo array is MSB first (left)
    from app.core.ir_protocols.ir_recv import sumBytes

    return sumBytes(state, length - 2, 2)


## Verify the checksum is valid for a given state.
## EXACT translation from IRremoteESP8266 (ir_Argo.cpp lines 479-483)
def validChecksum(state: List[int], length: int = kArgoStateLength) -> bool:
    """
    Verify the checksum is valid for a given state.
    EXACT translation from IRremoteESP8266
    """
    return getChecksum(state, length) == calcChecksum(state, length)


## Retrieve the checksum value from transmitted state
## EXACT translation from IRremoteESP8266 IRArgoACBase<ArgoProtocol>::getChecksum
## (ir_Argo.cpp lines 441-447)
def getChecksum(state: List[int], length: int = kArgoStateLength) -> int:
    """
    Retrieve the checksum value from transmitted state (WREM-2).
    EXACT translation from IRremoteESP8266
    """
    if length < 1:
        return -1
    return (state[length - 2] >> 2) + (state[length - 1] << 6)


## Send an Argo A/C formatted message (WREM-2).
## Status: BETA / Probably works.
## EXACT translation from IRremoteESP8266 IRsend::sendArgo (ir_Argo.cpp lines 65-83)
def sendArgo(data: List[int], nbytes: int, repeat: int = 0, sendFooter: bool = False) -> List[int]:
    """
    Send an Argo A/C formatted message (WREM-2).
    EXACT translation from IRremoteESP8266 IRsend::sendArgo

    Returns timing array instead of transmitting via hardware.
    """
    min_length = min(kArgoShortStateLength, kArgoStateLength)
    if nbytes < min_length:
        return []  # Not enough bytes to send a proper message.

    # Import here to avoid circular import
    from app.core.ir_protocols.ir_send import sendGeneric

    footermark = kArgoBitMark if sendFooter else 0
    gap = kArgoGap if sendFooter else 0

    return sendGeneric(
        headermark=kArgoHdrMark,
        headerspace=kArgoHdrSpace,
        onemark=kArgoBitMark,
        onespace=kArgoOneSpace,
        zeromark=kArgoBitMark,
        zerospace=kArgoZeroSpace,
        footermark=footermark,
        gap=gap,
        dataptr=data,
        nbytes=nbytes,
        frequency=38,
        MSBfirst=False,
        repeat=repeat,
        dutycycle=50,
    )


## Class for handling detailed Argo A/C messages (WREM-2).
## Direct translation from C++ IRArgoAC class
class IRArgoAC:
    ## Class Constructor
    def __init__(self) -> None:
        self._: ArgoProtocol = ArgoProtocol()
        self.stateReset()

    ## Reset the state of the remote to a known good state/sequence.
    ## Direct translation from ir_Argo.cpp lines 381-387
    def stateReset(self) -> None:
        for i in range(2, kArgoStateLength):
            self._.raw[i] = 0x0
        self._.Pre1 = kArgoPreamble1  # LSB first (as sent) 0b00110101
        self._.Pre2 = kArgoPreamble2  # LSB first: 0b10101111
        self._.Post = kArgoPost
        # Set defaults
        self.off()
        self.setTemp(20)
        self.setSensorTemp(25)
        self.setMode(kArgoAuto)
        self.setFan(kArgoFanAuto)

    ## Calculate & update the checksum for the internal state.
    ## Direct translation from ir_Argo.cpp lines 330-336
    def checksum(self) -> None:
        sum_val = calcChecksum(self._.raw, kArgoStateLength)
        # Append sum to end of array
        # Set const part of checksum bit 10
        self._.Post = kArgoPost
        self._.Sum = sum_val

    ## Get a PTR to the internal state/code for this protocol.
    ## Direct translation from ir_Argo.cpp lines 553-556
    def getRaw(self) -> List[int]:
        self.checksum()  # Ensure correct bit array before returning
        return self._.raw

    ## Set the internal state from a valid code for this protocol.
    ## Direct translation from ir_Argo.cpp lines 562-567
    def setRaw(self, state: List[int], length: int = kArgoStateLength) -> None:
        for i in range(min(len(state), length)):
            self._.raw[i] = state[i]

    ## Set the internal state to have the power on.
    ## Direct translation from ir_Argo.cpp line 571
    def on(self) -> None:
        self.setPower(True)

    ## Set the internal state to have the power off.
    ## Direct translation from ir_Argo.cpp line 575
    def off(self) -> None:
        self.setPower(False)

    ## Set the internal state to have the desired power.
    ## Direct translation from ir_Argo.cpp lines 585-587
    def setPower(self, on: bool) -> None:
        self._.Power = on

    ## Get the power setting from the internal state.
    ## Direct translation from ir_Argo.cpp line 612
    def getPower(self) -> bool:
        return bool(self._.Power)

    ## Control the current Max setting. (i.e. Turbo)
    ## Direct translation from ir_Argo.cpp lines 631-633
    def setMax(self, on: bool) -> None:
        self._.Max = on

    ## Is the Max (i.e. Turbo) setting on?
    ## Direct translation from ir_Argo.cpp line 638
    def getMax(self) -> bool:
        return bool(self._.Max)

    ## Set the temperature.
    ## Direct translation from ir_Argo.cpp lines 644-650
    def setTemp(self, degrees: int) -> None:
        temp = max(kArgoMinTemp, degrees)
        # delta 4 degrees. "If I want 12 degrees, I need to send 8"
        temp = min(kArgoMaxTemp, temp) - kArgoTempDelta
        # mask out bits
        self._.Temp = temp

    ## Get the current temperature setting.
    ## Direct translation from ir_Argo.cpp lines 655-657
    def getTemp(self) -> int:
        return self._.Temp + kArgoTempDelta

    ## Set the desired fan mode.
    ## Direct translation from ir_Argo.cpp lines 760-762
    def setFan(self, fan: int) -> None:
        self._.Fan = min(fan, kArgoFan3)

    ## Get the current fan speed setting.
    ## Direct translation from ir_Argo.cpp lines 767-769
    def getFan(self) -> int:
        return self._.Fan

    ## Set the flap position. i.e. Swing.
    ## Direct translation from ir_Argo.cpp lines 798-801
    def setFlap(self, flap: int) -> None:
        # Bounds check
        self._.Flap = min(flap, kArgoFlapFull)

    ## Get the flap position. i.e. Swing.
    ## Direct translation from ir_Argo.cpp lines 807-809
    def getFlap(self) -> int:
        return self._.Flap

    ## Set the desired operation mode.
    ## Direct translation from ir_Argo.cpp lines 915-927
    def setMode(self, mode: int) -> None:
        if mode in [kArgoCool, kArgoDry, kArgoAuto, kArgoOff, kArgoHeat, kArgoHeatAuto]:
            self._.Mode = mode
        else:
            self._.Mode = kArgoAuto

    ## Get the current operation mode
    ## Direct translation from ir_Argo.cpp line 934
    def getMode(self) -> int:
        return self._.Mode

    ## Turn on/off the Night mode. i.e. Sleep.
    ## Direct translation from ir_Argo.cpp line 943
    def setNight(self, on: bool) -> None:
        self._.Night = on

    ## Get the status of Night mode. i.e. Sleep.
    ## Direct translation from ir_Argo.cpp line 948
    def getNight(self) -> bool:
        return bool(self._.Night)

    ## Turn on/off the iFeel mode.
    ## Direct translation from ir_Argo.cpp line 1003
    def setiFeel(self, on: bool) -> None:
        self._.iFeel = on

    ## Get the status of iFeel mode.
    ## Direct translation from ir_Argo.cpp line 1008
    def getiFeel(self) -> bool:
        return bool(self._.iFeel)

    ## Set the value for the current room temperature.
    ## Direct translation from ir_Argo.cpp lines 1028-1036
    def setSensorTemp(self, degrees: int) -> None:
        temp = min(degrees, kArgoMaxRoomTemp)
        temp = max(temp, kArgoTempDelta) - kArgoTempDelta
        self._.RoomTemp = temp

    ## Get the currently stored value for the room temperature setting.
    ## Direct translation from ir_Argo.cpp line 1046
    def getSensorTemp(self) -> int:
        return self._.RoomTemp + kArgoTempDelta


## Decode the supplied Argo message (WREM-2).
## Status: BETA / Probably works.
## EXACT translation from IRremoteESP8266 IRrecv::decodeArgo (ir_Argo.cpp lines 1694-1720)
def decodeArgo(results, offset: int = 1, nbits: int = kArgoBits, strict: bool = True) -> bool:
    """
    Decode an Argo HVAC IR message (WREM-2).
    EXACT translation from IRremoteESP8266 IRrecv::decodeArgo

    This is the ACTUAL C++ decoder function, not a wrapper.
    """
    # Import here to avoid circular imports
    from app.core.ir_protocols.ir_recv import _matchGeneric

    if strict and nbits != kArgoBits:
        return False

    # Match Header + Data
    if not _matchGeneric(
        data_ptr=results.rawbuf[offset:],
        result_bits_ptr=None,
        result_bytes_ptr=results.state,
        use_bits=False,
        remaining=results.rawlen - offset,
        nbits=nbits,
        hdrmark=kArgoHdrMark,
        hdrspace=kArgoHdrSpace,
        onemark=kArgoBitMark,
        onespace=kArgoOneSpace,
        zeromark=kArgoBitMark,
        zerospace=kArgoZeroSpace,
        footermark=0,
        footerspace=0,  # Footer (None, allegedly. This seems very wrong.)
        atleast=False,
        tolerance=25,
        excess=0,
        MSBfirst=False,
    ):
        return False

    # Compliance
    # Verify we got a valid checksum.
    if strict and not validChecksum(results.state, kArgoStateLength):
        return False

    # Success
    results.bits = nbits
    # No need to record the state as we stored it as we decoded it.
    # As we use result->state, we don't record value, address, or command as it
    # is a union data type.
    return True
