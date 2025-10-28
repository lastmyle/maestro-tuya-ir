# Copyright 2019 ribeirodanielf
# Copyright 2019 David Conran
# Python translation: Direct conversion from C++ with NO optimizations

## @file
## @brief Support for Goodweather compatible HVAC protocols.
## Direct translation from IRremoteESP8266 ir_Goodweather.cpp and ir_Goodweather.h

from typing import List

# Ref: https://github.com/crankyoldgit/IRremoteESP8266/issues/697

# Constants - Timing values
kGoodweatherBitMark = 580
kGoodweatherOneSpace = 580
kGoodweatherZeroSpace = 1860
kGoodweatherHdrMark = 6820
kGoodweatherHdrSpace = 6820
kGoodweatherExtraTolerance = 12  # +12% extra

# State length constants
kGoodweatherBits = 64
kGoodweatherStateLength = kGoodweatherBits // 8  # 8 bytes

# Modes
kGoodweatherAuto = 0b000
kGoodweatherCool = 0b001
kGoodweatherDry =  0b010
kGoodweatherFan =  0b011
kGoodweatherHeat = 0b100

# Swing
kGoodweatherSwingFast = 0b00
kGoodweatherSwingSlow = 0b01
kGoodweatherSwingOff =  0b10

# Fan Control
kGoodweatherFanAuto = 0b00
kGoodweatherFanHigh = 0b01
kGoodweatherFanMed =  0b10
kGoodweatherFanLow =  0b11

# Temperature
kGoodweatherTempMin = 16  # Celsius
kGoodweatherTempMax = 31  # Celsius

# Commands
kGoodweatherCmdPower    = 0x00
kGoodweatherCmdMode     = 0x01
kGoodweatherCmdUpTemp   = 0x02
kGoodweatherCmdDownTemp = 0x03
kGoodweatherCmdSwing    = 0x04
kGoodweatherCmdFan      = 0x05
kGoodweatherCmdTimer    = 0x06
kGoodweatherCmdAirFlow  = 0x07
kGoodweatherCmdHold     = 0x08
kGoodweatherCmdSleep    = 0x09
kGoodweatherCmdTurbo    = 0x0A
kGoodweatherCmdLight    = 0x0B

# Default state
kGoodweatherStateInit = 0xD50000000000


## Native representation of a Goodweather A/C message.
## This is a direct translation of the C++ union/struct
class GoodweatherProtocol:
    def __init__(self):
        self.raw = 0  # 64-bit state

    # Byte 0 (bits 0-7) - always 0

    # Byte 1 (bits 8-15)
    @property
    def Light(self) -> int:
        return (self.raw >> 8) & 0x01

    @Light.setter
    def Light(self, value: bool) -> None:
        if value:
            self.raw |= (0x01 << 8)
        else:
            self.raw &= ~(0x01 << 8)

    @property
    def Turbo(self) -> int:
        return (self.raw >> 11) & 0x01

    @Turbo.setter
    def Turbo(self, value: bool) -> None:
        if value:
            self.raw |= (0x01 << 11)
        else:
            self.raw &= ~(0x01 << 11)

    # Byte 2 (bits 16-23)
    @property
    def Command(self) -> int:
        return (self.raw >> 16) & 0x0F

    @Command.setter
    def Command(self, value: int) -> None:
        self.raw = (self.raw & ~(0x0F << 16)) | ((value & 0x0F) << 16)

    # Byte 3 (bits 24-31)
    @property
    def Sleep(self) -> int:
        return (self.raw >> 24) & 0x01

    @Sleep.setter
    def Sleep(self, value: bool) -> None:
        if value:
            self.raw |= (0x01 << 24)
        else:
            self.raw &= ~(0x01 << 24)

    @property
    def Power(self) -> int:
        return (self.raw >> 25) & 0x01

    @Power.setter
    def Power(self, value: bool) -> None:
        if value:
            self.raw |= (0x01 << 25)
        else:
            self.raw &= ~(0x01 << 25)

    @property
    def Swing(self) -> int:
        return (self.raw >> 26) & 0x03

    @Swing.setter
    def Swing(self, value: int) -> None:
        self.raw = (self.raw & ~(0x03 << 26)) | ((value & 0x03) << 26)

    @property
    def AirFlow(self) -> int:
        return (self.raw >> 28) & 0x01

    @AirFlow.setter
    def AirFlow(self, value: bool) -> None:
        if value:
            self.raw |= (0x01 << 28)
        else:
            self.raw &= ~(0x01 << 28)

    @property
    def Fan(self) -> int:
        return (self.raw >> 29) & 0x03

    @Fan.setter
    def Fan(self, value: int) -> None:
        self.raw = (self.raw & ~(0x03 << 29)) | ((value & 0x03) << 29)

    # Byte 4 (bits 32-39)
    @property
    def Temp(self) -> int:
        return (self.raw >> 32) & 0x0F

    @Temp.setter
    def Temp(self, value: int) -> None:
        self.raw = (self.raw & ~(0x0F << 32)) | ((value & 0x0F) << 32)

    @property
    def Mode(self) -> int:
        return (self.raw >> 37) & 0x07

    @Mode.setter
    def Mode(self, value: int) -> None:
        self.raw = (self.raw & ~(0x07 << 37)) | ((value & 0x07) << 37)


## Send a Goodweather HVAC formatted message.
## Status: BETA / Needs testing on real device.
## EXACT translation from IRremoteESP8266 IRsend::sendGoodweather (lines 32-58)
def sendGoodweather(data: int, nbits: int = kGoodweatherBits, repeat: int = 0) -> List[int]:
    """
    Send a Goodweather HVAC formatted message.
    EXACT translation from IRremoteESP8266 IRsend::sendGoodweather

    Returns timing array instead of transmitting via hardware.
    """
    if nbits != kGoodweatherBits:
        return []  # Wrong nr. of bits to send a proper message.

    from app.core.ir_protocols.ir_send import sendGeneric, sendData

    all_timings = []

    for r in range(repeat + 1):
        # Header
        all_timings.append(kGoodweatherHdrMark)
        all_timings.append(kGoodweatherHdrSpace)

        # Data - send in chunks of 8 bits (1 byte at a time)
        for i in range(0, nbits, 8):
            chunk = (data >> i) & 0xFF  # Grab a byte at a time
            chunk = (~chunk & 0xFF) << 8 | chunk  # Prepend inverted copy

            # Send 16 bits (byte + inverted byte)
            chunk_timings = sendData(
                onemark=kGoodweatherBitMark,
                onespace=kGoodweatherOneSpace,
                zeromark=kGoodweatherBitMark,
                zerospace=kGoodweatherZeroSpace,
                data=chunk,
                nbits=16,
                MSBfirst=False
            )
            all_timings.extend(chunk_timings)

        # Footer
        all_timings.append(kGoodweatherBitMark)
        all_timings.append(kGoodweatherHdrSpace)
        all_timings.append(kGoodweatherBitMark)

        if r < repeat:
            all_timings.append(0)  # Default message gap

    return all_timings


## Class for handling detailed Goodweather A/C messages.
## Direct translation from C++ IRGoodweatherAc class
class IRGoodweatherAc:
    ## Class Constructor
    def __init__(self) -> None:
        self._: GoodweatherProtocol = GoodweatherProtocol()
        self.stateReset()

    ## Reset the internal state to a fixed known good state.
    ## Direct translation from ir_Goodweather.cpp line 70
    def stateReset(self) -> None:
        self._.raw = kGoodweatherStateInit

    ## Get a copy of the internal state as a valid code for this protocol.
    ## Direct translation from ir_Goodweather.cpp line 85
    def getRaw(self) -> int:
        return self._.raw

    ## Set the internal state from a valid code for this protocol.
    ## Direct translation from ir_Goodweather.cpp line 89
    def setRaw(self, state: int) -> None:
        self._.raw = state

    ## Change the power setting to On.
    ## Direct translation from ir_Goodweather.cpp line 92
    def on(self) -> None:
        self.setPower(True)

    ## Change the power setting to Off.
    ## Direct translation from ir_Goodweather.cpp line 95
    def off(self) -> None:
        self.setPower(False)

    ## Change the power setting.
    ## Direct translation from ir_Goodweather.cpp lines 99-102
    def setPower(self, on: bool) -> None:
        self._.Command = kGoodweatherCmdPower
        self._.Power = on

    ## Get the value of the current power setting.
    ## Direct translation from ir_Goodweather.cpp lines 106-108
    def getPower(self) -> bool:
        return bool(self._.Power)

    ## Set the temperature.
    ## Direct translation from ir_Goodweather.cpp lines 112-118
    def setTemp(self, temp: int) -> None:
        new_temp = max(kGoodweatherTempMin, temp)
        new_temp = min(kGoodweatherTempMax, new_temp)
        if new_temp > self.getTemp():
            self._.Command = kGoodweatherCmdUpTemp
        if new_temp < self.getTemp():
            self._.Command = kGoodweatherCmdDownTemp
        self._.Temp = new_temp - kGoodweatherTempMin

    ## Get the current temperature setting.
    ## Direct translation from ir_Goodweather.cpp lines 122-124
    def getTemp(self) -> int:
        return self._.Temp + kGoodweatherTempMin

    ## Set the speed of the fan.
    ## Direct translation from ir_Goodweather.cpp lines 128-140
    def setFan(self, speed: int) -> None:
        self._.Command = kGoodweatherCmdFan
        if speed in [kGoodweatherFanAuto, kGoodweatherFanLow,
                     kGoodweatherFanMed, kGoodweatherFanHigh]:
            self._.Fan = speed
        else:
            self._.Fan = kGoodweatherFanAuto

    ## Get the current fan speed setting.
    ## Direct translation from ir_Goodweather.cpp lines 144-146
    def getFan(self) -> int:
        return self._.Fan

    ## Set the operating mode of the A/C.
    ## Direct translation from ir_Goodweather.cpp lines 150-163
    def setMode(self, mode: int) -> None:
        self._.Command = kGoodweatherCmdMode
        if mode in [kGoodweatherAuto, kGoodweatherDry, kGoodweatherCool,
                    kGoodweatherFan, kGoodweatherHeat]:
            self._.Mode = mode
        else:
            self._.Mode = kGoodweatherAuto

    ## Get the operating mode setting of the A/C.
    ## Direct translation from ir_Goodweather.cpp lines 167-169
    def getMode(self) -> int:
        return self._.Mode

    ## Set the Light (LED) Toggle setting of the A/C.
    ## Direct translation from ir_Goodweather.cpp lines 173-176
    def setLight(self, toggle: bool) -> None:
        self._.Command = kGoodweatherCmdLight
        self._.Light = toggle

    ## Get the Light (LED) Toggle setting of the A/C.
    ## Direct translation from ir_Goodweather.cpp lines 180-182
    def getLight(self) -> bool:
        return bool(self._.Light)

    ## Set the Sleep Toggle setting of the A/C.
    ## Direct translation from ir_Goodweather.cpp lines 186-189
    def setSleep(self, toggle: bool) -> None:
        self._.Command = kGoodweatherCmdSleep
        self._.Sleep = toggle

    ## Get the Sleep Toggle setting of the A/C.
    ## Direct translation from ir_Goodweather.cpp lines 193-195
    def getSleep(self) -> bool:
        return bool(self._.Sleep)

    ## Set the Turbo Toggle setting of the A/C.
    ## Direct translation from ir_Goodweather.cpp lines 199-202
    def setTurbo(self, toggle: bool) -> None:
        self._.Command = kGoodweatherCmdTurbo
        self._.Turbo = toggle

    ## Get the Turbo Toggle setting of the A/C.
    ## Direct translation from ir_Goodweather.cpp lines 206-208
    def getTurbo(self) -> bool:
        return bool(self._.Turbo)

    ## Set the Vertical Swing speed of the A/C.
    ## Direct translation from ir_Goodweather.cpp lines 212-223
    def setSwing(self, speed: int) -> None:
        self._.Command = kGoodweatherCmdSwing
        if speed in [kGoodweatherSwingOff, kGoodweatherSwingSlow, kGoodweatherSwingFast]:
            self._.Swing = speed
        else:
            self._.Swing = kGoodweatherSwingOff

    ## Get the Vertical Swing speed of the A/C.
    ## Direct translation from ir_Goodweather.cpp lines 227-229
    def getSwing(self) -> int:
        return self._.Swing

    ## Set the remote Command type/button pressed.
    ## Direct translation from ir_Goodweather.cpp lines 233-236
    def setCommand(self, cmd: int) -> None:
        if cmd <= kGoodweatherCmdLight:
            self._.Command = cmd

    ## Get the Command type/button pressed from the current settings
    ## Direct translation from ir_Goodweather.cpp lines 240-242
    def getCommand(self) -> int:
        return self._.Command


## Decode the supplied Goodweather message.
## Status: BETA / Probably works.
## EXACT translation from IRremoteESP8266 IRrecv::decodeGoodweather (lines 426-498)
def decodeGoodweather(results, offset: int = 1, nbits: int = kGoodweatherBits,
                      strict: bool = True, _tolerance: int = 25) -> bool:
    """
    Decode a Goodweather HVAC IR message.
    EXACT translation from IRremoteESP8266 IRrecv::decodeGoodweather
    """
    from app.core.ir_protocols.ir_recv import (
        kHeader, kFooter, kMarkExcess, matchMark, matchSpace,
        matchData, matchAtLeast, match_result_t
    )

    if results.rawlen < 2 * (2 * nbits) + kHeader + 2 * kFooter - 1 + offset:
        return False  # Can't possibly be a valid Goodweather message.
    if strict and nbits != kGoodweatherBits:
        return False  # Not strictly a Goodweather message.

    dataSoFar = 0
    dataBitsSoFar = 0

    # Header
    if not matchMark(results.rawbuf[offset], kGoodweatherHdrMark, _tolerance):
        return False
    offset += 1
    if not matchSpace(results.rawbuf[offset], kGoodweatherHdrSpace, _tolerance):
        return False
    offset += 1

    # Data
    while offset <= results.rawlen - 32 and dataBitsSoFar < nbits:
        # Read in a byte at a time.
        # Normal first.
        data_result = matchData(
            data_ptr=results.rawbuf,
            offset=offset,
            nbits=8,
            onemark=kGoodweatherBitMark,
            onespace=kGoodweatherOneSpace,
            zeromark=kGoodweatherBitMark,
            zerospace=kGoodweatherZeroSpace,
            tolerance=_tolerance + kGoodweatherExtraTolerance,
            excess=kMarkExcess,
            MSBfirst=False,
            expectlastspace=True
        )
        if data_result.success == False:
            return False
        offset += data_result.used
        data = data_result.data & 0xFF

        # Then inverted.
        data_result = matchData(
            data_ptr=results.rawbuf,
            offset=offset,
            nbits=8,
            onemark=kGoodweatherBitMark,
            onespace=kGoodweatherOneSpace,
            zeromark=kGoodweatherBitMark,
            zerospace=kGoodweatherZeroSpace,
            tolerance=_tolerance + kGoodweatherExtraTolerance,
            excess=kMarkExcess,
            MSBfirst=False,
            expectlastspace=True
        )
        if data_result.success == False:
            return False
        offset += data_result.used
        inverted = data_result.data & 0xFF

        if data != (inverted ^ 0xFF):
            return False  # Data integrity failed.
        dataSoFar |= data << dataBitsSoFar
        dataBitsSoFar += 8

    # Footer.
    if not matchMark(results.rawbuf[offset], kGoodweatherBitMark,
                    _tolerance + kGoodweatherExtraTolerance):
        return False
    offset += 1
    if not matchSpace(results.rawbuf[offset], kGoodweatherHdrSpace, _tolerance):
        return False
    offset += 1
    if not matchMark(results.rawbuf[offset], kGoodweatherBitMark,
                    _tolerance + kGoodweatherExtraTolerance):
        return False
    offset += 1
    if offset <= results.rawlen:
        if not matchAtLeast(results.rawbuf[offset], kGoodweatherHdrSpace, _tolerance):
            return False

    # Compliance
    if strict and (dataBitsSoFar != kGoodweatherBits):
        return False

    # Success
    results.bits = dataBitsSoFar
    results.value = dataSoFar
    results.address = 0
    results.command = 0
    return True
