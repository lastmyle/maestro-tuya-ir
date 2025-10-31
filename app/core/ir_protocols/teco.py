# Copyright 2019 Fabien Valthier
# Python translation: Direct conversion from C++ with NO optimizations

## @file
## @brief Support for Teco protocols.
## Direct translation from IRremoteESP8266 ir_Teco.cpp and ir_Teco.h

from typing import List

# Constants - Timing values (from ir_Teco.cpp lines 15-22)
# using SPACE modulation.
kTecoHdrMark = 9000
kTecoHdrSpace = 4440
kTecoBitMark = 620
kTecoOneSpace = 1650
kTecoZeroSpace = 580
kTecoGap = 100000  # kDefaultMessageGap - Made-up value. Just a guess.

# State length constants (from IRremoteESP8266.h)
# Teco uses a 64-bit (8 byte) protocol but stored as uint64
kTecoBits = 35

# Mode constants (from ir_Teco.h lines 46-50)
kTecoAuto = 0  # temp = 25C
kTecoCool = 1
kTecoDry = 2  # temp = 25C, but not shown
kTecoFan = 3
kTecoHeat = 4

# Fan speed constants (from ir_Teco.h lines 51-54)
kTecoFanAuto = 0  # 0b00
kTecoFanLow = 1  # 0b01
kTecoFanMed = 2  # 0b10
kTecoFanHigh = 3  # 0b11

# Temperature constants (from ir_Teco.h lines 55-56)
kTecoMinTemp = 16  # 16C
kTecoMaxTemp = 30  # 30C

# Reset state constant (from ir_Teco.h line 58)
kTecoReset = 0b01001010000000000000010000000000000


## Native representation of a Teco A/C message.
## This is a direct translation of the C++ union/struct (ir_Teco.h lines 23-43)
## Note: In C++, this is stored as a uint64_t, but we use properties to access bitfields
class TecoProtocol:
    def __init__(self):
        # The state as a single 64-bit value (35 bits used)
        self.raw = 0

    # Bits 0-2: Mode
    @property
    def Mode(self) -> int:
        return self.raw & 0x07

    @Mode.setter
    def Mode(self, value: int) -> None:
        self.raw = (self.raw & ~0x07) | (value & 0x07)

    # Bit 3: Power
    @property
    def Power(self) -> int:
        return (self.raw >> 3) & 0x01

    @Power.setter
    def Power(self, value: bool) -> None:
        if value:
            self.raw |= 1 << 3
        else:
            self.raw &= ~(1 << 3)

    # Bits 4-5: Fan
    @property
    def Fan(self) -> int:
        return (self.raw >> 4) & 0x03

    @Fan.setter
    def Fan(self, value: int) -> None:
        self.raw = (self.raw & ~(0x03 << 4)) | ((value & 0x03) << 4)

    # Bit 6: Swing
    @property
    def Swing(self) -> int:
        return (self.raw >> 6) & 0x01

    @Swing.setter
    def Swing(self, value: bool) -> None:
        if value:
            self.raw |= 1 << 6
        else:
            self.raw &= ~(1 << 6)

    # Bit 7: Sleep
    @property
    def Sleep(self) -> int:
        return (self.raw >> 7) & 0x01

    @Sleep.setter
    def Sleep(self, value: bool) -> None:
        if value:
            self.raw |= 1 << 7
        else:
            self.raw &= ~(1 << 7)

    # Bits 8-11: Temp
    @property
    def Temp(self) -> int:
        return (self.raw >> 8) & 0x0F

    @Temp.setter
    def Temp(self, value: int) -> None:
        self.raw = (self.raw & ~(0x0F << 8)) | ((value & 0x0F) << 8)

    # Bit 12: HalfHour
    @property
    def HalfHour(self) -> int:
        return (self.raw >> 12) & 0x01

    @HalfHour.setter
    def HalfHour(self, value: bool) -> None:
        if value:
            self.raw |= 1 << 12
        else:
            self.raw &= ~(1 << 12)

    # Bits 13-14: TensHours
    @property
    def TensHours(self) -> int:
        return (self.raw >> 13) & 0x03

    @TensHours.setter
    def TensHours(self, value: int) -> None:
        self.raw = (self.raw & ~(0x03 << 13)) | ((value & 0x03) << 13)

    # Bit 15: TimerOn
    @property
    def TimerOn(self) -> int:
        return (self.raw >> 15) & 0x01

    @TimerOn.setter
    def TimerOn(self, value: bool) -> None:
        if value:
            self.raw |= 1 << 15
        else:
            self.raw &= ~(1 << 15)

    # Bits 16-19: UnitHours
    @property
    def UnitHours(self) -> int:
        return (self.raw >> 16) & 0x0F

    @UnitHours.setter
    def UnitHours(self, value: int) -> None:
        self.raw = (self.raw & ~(0x0F << 16)) | ((value & 0x0F) << 16)

    # Bit 20: Humid
    @property
    def Humid(self) -> int:
        return (self.raw >> 20) & 0x01

    @Humid.setter
    def Humid(self, value: bool) -> None:
        if value:
            self.raw |= 1 << 20
        else:
            self.raw &= ~(1 << 20)

    # Bit 21: Light
    @property
    def Light(self) -> int:
        return (self.raw >> 21) & 0x01

    @Light.setter
    def Light(self, value: bool) -> None:
        if value:
            self.raw |= 1 << 21
        else:
            self.raw &= ~(1 << 21)

    # Bit 23: Save
    @property
    def Save(self) -> int:
        return (self.raw >> 23) & 0x01

    @Save.setter
    def Save(self, value: bool) -> None:
        if value:
            self.raw |= 1 << 23
        else:
            self.raw &= ~(1 << 23)


## Send a Teco A/C message.
## Status: Beta / Probably working.
## @param[in] data The message to be sent (as uint64).
## @param[in] nbits The number of bits of message to be sent.
## @param[in] repeat The number of times the command is to be repeated.
## Direct translation from IRremoteESP8266 IRsend::sendTeco (ir_Teco.cpp lines 37-42)
def sendTeco(data: int, nbits: int = kTecoBits, repeat: int = 0) -> List[int]:
    """
    Send a Teco A/C formatted message.
    EXACT translation from IRremoteESP8266 IRsend::sendTeco

    Returns timing array instead of transmitting via hardware.
    """
    # Import here to avoid circular import
    from app.core.ir_protocols.ir_send import sendGeneric

    all_timings = []

    for r in range(repeat + 1):
        # Convert uint64 to byte array for sendGeneric
        # Note: sendGeneric expects LSB first per byte
        data_bytes = []
        temp_data = data
        for i in range((nbits + 7) // 8):
            data_bytes.append(temp_data & 0xFF)
            temp_data >>= 8

        timings = sendGeneric(
            headermark=kTecoHdrMark,
            headerspace=kTecoHdrSpace,
            onemark=kTecoBitMark,
            onespace=kTecoOneSpace,
            zeromark=kTecoBitMark,
            zerospace=kTecoZeroSpace,
            footermark=kTecoBitMark,
            gap=kTecoGap,
            dataptr=data_bytes,
            nbytes=len(data_bytes),
            nbits=nbits,
            MSBfirst=False,
        )
        all_timings.extend(timings)

    return all_timings


## Class for handling detailed Teco A/C messages.
## Direct translation from C++ IRTecoAc class
class IRTecoAc:
    ## Class Constructor
    def __init__(self) -> None:
        self._: TecoProtocol = TecoProtocol()
        self.stateReset()

    ## Reset the internal state of the emulation.
    ## @note Mode:auto, Power:Off, fan:auto, temp:16, swing:off, sleep:off
    ## Direct translation from ir_Teco.cpp lines 66-68
    def stateReset(self) -> None:
        self._.raw = kTecoReset

    ## Get a copy of the internal state/code for this protocol.
    ## @return A code for this protocol based on the current internal state.
    ## Direct translation from ir_Teco.cpp line 72
    def getRaw(self) -> int:
        return self._.raw

    ## Set the internal state from a valid code for this protocol.
    ## @param[in] new_code A valid code for this protocol.
    ## Direct translation from ir_Teco.cpp line 76
    def setRaw(self, new_code: int) -> None:
        self._.raw = new_code

    ## Set the requested power state of the A/C to on.
    ## Direct translation from ir_Teco.cpp line 79
    def on(self) -> None:
        self.setPower(True)

    ## Set the requested power state of the A/C to off.
    ## Direct translation from ir_Teco.cpp line 82
    def off(self) -> None:
        self.setPower(False)

    ## Change the power setting.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Teco.cpp lines 86-88
    def setPower(self, on: bool) -> None:
        self._.Power = on

    ## Get the value of the current power setting.
    ## @return true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Teco.cpp lines 92-94
    def getPower(self) -> bool:
        return bool(self._.Power)

    ## Set the temperature.
    ## @param[in] temp The temperature in degrees celsius.
    ## Direct translation from ir_Teco.cpp lines 98-103
    def setTemp(self, temp: int) -> None:
        newtemp = temp
        newtemp = min(newtemp, kTecoMaxTemp)
        newtemp = max(newtemp, kTecoMinTemp)
        self._.Temp = newtemp - kTecoMinTemp

    ## Get the current temperature setting.
    ## @return The current setting for temp. in degrees celsius.
    ## Direct translation from ir_Teco.cpp lines 107-109
    def getTemp(self) -> int:
        return self._.Temp + kTecoMinTemp

    ## Set the speed of the fan.
    ## @param[in] speed The desired setting.
    ## Direct translation from ir_Teco.cpp lines 113-123
    def setFan(self, speed: int) -> None:
        newspeed = speed
        if speed in [kTecoFanAuto, kTecoFanHigh, kTecoFanMed, kTecoFanLow]:
            pass
        else:
            newspeed = kTecoFanAuto
        self._.Fan = newspeed

    ## Get the current fan speed setting.
    ## @return The current fan speed/mode.
    ## Direct translation from ir_Teco.cpp lines 127-129
    def getFan(self) -> int:
        return self._.Fan

    ## Set the operating mode of the A/C.
    ## @param[in] mode The desired operating mode.
    ## Direct translation from ir_Teco.cpp lines 133-144
    def setMode(self, mode: int) -> None:
        newmode = mode
        if mode in [kTecoAuto, kTecoCool, kTecoDry, kTecoFan, kTecoHeat]:
            pass
        else:
            newmode = kTecoAuto
        self._.Mode = newmode

    ## Get the operating mode setting of the A/C.
    ## @return The current operating mode setting.
    ## Direct translation from ir_Teco.cpp lines 148-150
    def getMode(self) -> int:
        return self._.Mode

    ## Set the (vertical) swing setting of the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Teco.cpp lines 154-156
    def setSwing(self, on: bool) -> None:
        self._.Swing = on

    ## Get the (vertical) swing setting of the A/C.
    ## @return true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Teco.cpp lines 160-162
    def getSwing(self) -> bool:
        return bool(self._.Swing)

    ## Set the Sleep setting of the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Teco.cpp lines 166-168
    def setSleep(self, on: bool) -> None:
        self._.Sleep = on

    ## Get the Sleep setting of the A/C.
    ## @return true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Teco.cpp lines 172-174
    def getSleep(self) -> bool:
        return bool(self._.Sleep)

    ## Set the Light (LED/Display) setting of the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Teco.cpp lines 178-180
    def setLight(self, on: bool) -> None:
        self._.Light = on

    ## Get the Light (LED/Display) setting of the A/C.
    ## @return true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Teco.cpp lines 184-186
    def getLight(self) -> bool:
        return bool(self._.Light)

    ## Set the Humid setting of the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Teco.cpp lines 190-192
    def setHumid(self, on: bool) -> None:
        self._.Humid = on

    ## Get the Humid setting of the A/C.
    ## @return true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Teco.cpp lines 196-198
    def getHumid(self) -> bool:
        return bool(self._.Humid)

    ## Set the Save setting of the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Teco.cpp lines 202-204
    def setSave(self, on: bool) -> None:
        self._.Save = on

    ## Get the Save setting of the A/C.
    ## @return true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Teco.cpp lines 208-210
    def getSave(self) -> bool:
        return bool(self._.Save)

    ## Is the timer function enabled?
    ## @return true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Teco.cpp lines 214-216
    def getTimerEnabled(self) -> bool:
        return bool(self._.TimerOn)

    ## Get the timer time for when the A/C unit will switch power state.
    ## @return The number of minutes left on the timer. `0` means off.
    ## Direct translation from ir_Teco.cpp lines 220-227
    def getTimer(self) -> int:
        mins = 0
        if self.getTimerEnabled():
            mins = (self._.TensHours * 10 + self._.UnitHours) * 60
            if self._.HalfHour:
                mins += 30
        return mins

    ## Set the timer for when the A/C unit will switch power state.
    ## @param[in] nr_mins Number of minutes before power state change.
    ##   `0` will clear the timer. Max is 24 hrs.
    ## @note Time is stored internally in increments of 30 mins.
    ## Direct translation from ir_Teco.cpp lines 233-241
    def setTimer(self, nr_mins: int) -> None:
        # Limit to 24 hrs
        mins = min(nr_mins, 24 * 60)
        hours = mins // 60
        self._.TimerOn = mins > 0  # Set the timer flag.
        self._.HalfHour = (mins % 60) >= 30
        self._.UnitHours = hours % 10
        self._.TensHours = hours // 10


## Decode the supplied Teco message.
## Status: STABLE / Tested.
## @param[in,out] results Ptr to the data to decode & where to store the result
## @param[in] offset The starting index to use when attempting to decode the raw data.
## @param[in] nbits The number of data bits to expect.
## @param[in] strict Flag indicating if we should perform strict matching.
## @return True if it can decode it, false if it can't.
## Direct translation from IRremoteESP8266 IRrecv::decodeTeco (ir_Teco.cpp lines 354-375)
def decodeTeco(results, offset: int = 1, nbits: int = kTecoBits, strict: bool = True) -> bool:
    """
    Decode a Teco HVAC IR message.
    EXACT translation from IRremoteESP8266 IRrecv::decodeTeco

    This is the ACTUAL C++ decoder function, not a wrapper.
    """
    # Import here to avoid circular imports
    from app.core.ir_protocols.ir_recv import matchGeneric, kMarkExcess

    if strict and nbits != kTecoBits:
        return False  # Not what is expected

    data = 0
    # Match Header + Data + Footer
    if not matchGeneric(
        data_ptr=results.rawbuf[offset:],
        result_ptr=None,  # We'll get data as uint64
        remaining=results.rawlen - offset,
        nbits=nbits,
        hdrmark=kTecoHdrMark,
        hdrspace=kTecoHdrSpace,
        onemark=kTecoBitMark,
        onespace=kTecoOneSpace,
        zeromark=kTecoBitMark,
        zerospace=kTecoZeroSpace,
        footermark=kTecoBitMark,
        footerspace=kTecoGap,
        atleast=True,
        tolerance=25,
        excess=kMarkExcess,
        MSBfirst=False,
        get_value=True,  # Special flag to get uint64 value
    ):
        return False

    # Success
    # results.decode_type = TECO  # Would set protocol type in C++
    results.bits = nbits
    results.value = data
    results.address = 0
    results.command = 0
    return True
