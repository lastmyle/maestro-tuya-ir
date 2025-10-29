# Copyright 2020 Quentin Briollant
# Python translation: Direct conversion from C++ with NO optimizations

## @file
## @brief Support for Technibel protocol.
## Direct translation from IRremoteESP8266 ir_Technibel.cpp and ir_Technibel.h

from typing import List

# Supports:
#   Brand: Technibel,  Model: IRO PLUS

# Constants (from ir_Technibel.cpp lines 20-26)
kTechnibelAcHdrMark = 8836
kTechnibelAcHdrSpace = 4380
kTechnibelAcBitMark = 523
kTechnibelAcOneSpace = 1696
kTechnibelAcZeroSpace = 564
kTechnibelAcGap = 100000  # kDefaultMessageGap
kTechnibelAcFreq = 38000

# State length constants (from IRremoteESP8266.h lines 1232-1233)
kTechnibelAcBits = 56
kTechnibelAcDefaultRepeat = 0  # kNoRepeat

# Constants from ir_Technibel.h
kTechnibelAcTimerHoursOffset = 16
kTechnibelAcTimerMax = 24

kTechnibelAcTempMinC = 16  # Deg C
kTechnibelAcTempMaxC = 31  # Deg C
kTechnibelAcTempMinF = 61  # Deg F
kTechnibelAcTempMaxF = 88  # Deg F

kTechnibelAcFanSize = 4
kTechnibelAcFanLow = 0b0001
kTechnibelAcFanMedium = 0b0010
kTechnibelAcFanHigh = 0b0100

kTechnibelAcCool = 0b0001
kTechnibelAcDry = 0b0010
kTechnibelAcFan = 0b0100
kTechnibelAcHeat = 0b1000

kTechnibelAcHeaderOffset = 48
kTechnibelAcHeader = 0b00011000

# Mode:Cool, Power:Off, fan:Low, temp:20, swing:Off, sleep:Off
kTechnibelAcResetState = 0x180101140000EA


## Native representation of a Technibel A/C message.
## Direct translation of C++ union/struct (from ir_Technibel.h lines 24-46)
class TechnibelProtocol:
    def __init__(self):
        self.raw = kTechnibelAcResetState  # uint64_t

    # Byte 0
    @property
    def Sum(self) -> int:
        return self.raw & 0xFF

    @Sum.setter
    def Sum(self, value: int) -> None:
        self.raw = (self.raw & ~0xFF) | (value & 0xFF)

    # Byte 1
    @property
    def Footer(self) -> int:
        return (self.raw >> 8) & 0xFF

    @Footer.setter
    def Footer(self, value: int) -> None:
        self.raw = (self.raw & ~(0xFF << 8)) | ((value & 0xFF) << 8)

    # Byte 2
    @property
    def TimerHours(self) -> int:
        return (self.raw >> 16) & 0x1F

    @TimerHours.setter
    def TimerHours(self, value: int) -> None:
        self.raw = (self.raw & ~(0x1F << 16)) | ((value & 0x1F) << 16)

    # :3 bits (21-23)

    # Byte 3
    @property
    def Temp(self) -> int:
        return (self.raw >> 24) & 0x7F

    @Temp.setter
    def Temp(self, value: int) -> None:
        self.raw = (self.raw & ~(0x7F << 24)) | ((value & 0x7F) << 24)

    # :1 bit (31)

    # Byte 4
    @property
    def Fan(self) -> int:
        return (self.raw >> 32) & 0x07

    @Fan.setter
    def Fan(self, value: int) -> None:
        self.raw = (self.raw & ~(0x07 << 32)) | ((value & 0x07) << 32)

    # :1 bit (35)

    @property
    def Sleep(self) -> int:
        return (self.raw >> 36) & 0x01

    @Sleep.setter
    def Sleep(self, value: bool) -> None:
        if value:
            self.raw |= 1 << 36
        else:
            self.raw &= ~(1 << 36)

    @property
    def Swing(self) -> int:
        return (self.raw >> 37) & 0x01

    @Swing.setter
    def Swing(self, value: bool) -> None:
        if value:
            self.raw |= 1 << 37
        else:
            self.raw &= ~(1 << 37)

    @property
    def UseFah(self) -> int:
        return (self.raw >> 38) & 0x01

    @UseFah.setter
    def UseFah(self, value: bool) -> None:
        if value:
            self.raw |= 1 << 38
        else:
            self.raw &= ~(1 << 38)

    @property
    def TimerEnable(self) -> int:
        return (self.raw >> 39) & 0x01

    @TimerEnable.setter
    def TimerEnable(self, value: bool) -> None:
        if value:
            self.raw |= 1 << 39
        else:
            self.raw &= ~(1 << 39)

    # Byte 5
    @property
    def Mode(self) -> int:
        return (self.raw >> 40) & 0x0F

    @Mode.setter
    def Mode(self, value: int) -> None:
        self.raw = (self.raw & ~(0x0F << 40)) | ((value & 0x0F) << 40)

    @property
    def FanChange(self) -> int:
        return (self.raw >> 44) & 0x01

    @FanChange.setter
    def FanChange(self, value: bool) -> None:
        if value:
            self.raw |= 1 << 44
        else:
            self.raw &= ~(1 << 44)

    @property
    def TempChange(self) -> int:
        return (self.raw >> 45) & 0x01

    @TempChange.setter
    def TempChange(self, value: bool) -> None:
        if value:
            self.raw |= 1 << 45
        else:
            self.raw &= ~(1 << 45)

    @property
    def TimerChange(self) -> int:
        return (self.raw >> 46) & 0x01

    @TimerChange.setter
    def TimerChange(self, value: bool) -> None:
        if value:
            self.raw |= 1 << 46
        else:
            self.raw &= ~(1 << 46)

    @property
    def Power(self) -> int:
        return (self.raw >> 47) & 0x01

    @Power.setter
    def Power(self, value: bool) -> None:
        if value:
            self.raw |= 1 << 47
        else:
            self.raw &= ~(1 << 47)

    # Byte 6
    @property
    def Header(self) -> int:
        return (self.raw >> 48) & 0xFF

    @Header.setter
    def Header(self, value: int) -> None:
        self.raw = (self.raw & ~(0xFF << 48)) | ((value & 0xFF) << 48)


## Send an Technibel AC formatted message.
## Status: STABLE / Reported as working on a real device.
## @param[in] data containing the IR command.
## @param[in] nbits Nr. of bits to send. usually kTechnibelAcBits
## @param[in] repeat Nr. of times the message is to be repeated.
## Direct translation from IRremoteESP8266 IRsend::sendTechnibelAc (ir_Technibel.cpp lines 30-43)
def sendTechnibelAc(data: int, nbits: int, repeat: int = kTechnibelAcDefaultRepeat) -> List[int]:
    """
    Send a Technibel AC formatted message.
    EXACT translation from IRremoteESP8266 IRsend::sendTechnibelAc

    Returns timing array instead of transmitting via hardware.
    """
    # Import here to avoid circular import
    from app.core.ir_protocols.ir_send import sendGeneric

    return sendGeneric(
        headermark=kTechnibelAcHdrMark,
        headerspace=kTechnibelAcHdrSpace,
        onemark=kTechnibelAcBitMark,
        onespace=kTechnibelAcOneSpace,
        zeromark=kTechnibelAcBitMark,
        zerospace=kTechnibelAcZeroSpace,
        footermark=kTechnibelAcBitMark,
        dataptr=data,
        nbytes=0,  # Using nbits instead
        nbits=nbits,
        MSBfirst=True,  # LSB First in C++
    )


## Helper function to get bits from uint64
## EXACT translation from C++ GETBITS64 macro
def GETBITS64(value: int, offset: int, nbits: int) -> int:
    """Extract nbits from value starting at offset"""
    return (value >> offset) & ((1 << nbits) - 1)


## Decode the supplied Technibel A/C message.
## Status: STABLE / Reported as working on a real device
## @param[in,out] results Ptr to data to decode & where to store the decode
## @param[in] offset The starting index to use when attempting to decode the raw data.
## @param[in] nbits The number of data bits to expect (kTechnibelAcBits).
## @param[in] strict Flag indicating if we should perform strict matching.
## @return A boolean. True if it can decode it, false if it can't.
## Direct translation from IRremoteESP8266 IRrecv::decodeTechnibelAc (ir_Technibel.cpp lines 46-83)
def decodeTechnibelAc(
    results, offset: int = 1, nbits: int = kTechnibelAcBits, strict: bool = True
) -> bool:
    """
    Decode a Technibel AC IR message.
    EXACT translation from IRremoteESP8266 IRrecv::decodeTechnibelAc

    This is the ACTUAL C++ decoder function, not a wrapper.
    """
    # Import here to avoid circular imports
    from app.core.ir_protocols.ir_recv import kMarkExcess, _matchGeneric

    # Compliance
    if strict and nbits != kTechnibelAcBits:
        return False

    # Header + Data + Footer
    if not _matchGeneric(
        data_ptr=results.rawbuf[offset:],
        result_bits_ptr=None,
        result_bytes_ptr=results.state,
        use_bits=True,
        remaining=results.rawlen - offset,
        nbits=nbits,
        hdrmark=kTechnibelAcHdrMark,
        hdrspace=kTechnibelAcHdrSpace,
        onemark=kTechnibelAcBitMark,
        onespace=kTechnibelAcOneSpace,
        zeromark=kTechnibelAcBitMark,
        zerospace=kTechnibelAcZeroSpace,
        footermark=kTechnibelAcBitMark,
        footerspace=kTechnibelAcGap,
        atleast=True,
        tolerance=25,
        excess=kMarkExcess,
        MSBfirst=True,
    ):
        return False

    # Compliance
    if strict and not IRTechnibelAc.validChecksum(results.value):
        return False

    # Success
    # results.decode_type = decode_type_t::TECHNIBEL_AC  # Would set protocol type in C++
    results.bits = nbits
    # results.value and results.state already set by _matchGeneric
    results.command = 0
    results.address = 0
    return True


## Class for handling detailed Technibel A/C messages.
## Direct translation from C++ IRTechnibelAc class
class IRTechnibelAc:
    ## Class Constructor
    ## @param[in] pin GPIO to be used when sending.
    ## @param[in] inverted Is the output signal to be inverted?
    ## @param[in] use_modulation Is frequency modulation to be used?
    ## Direct translation from ir_Technibel.cpp lines 85-91
    def __init__(self, pin: int = 0, inverted: bool = False, use_modulation: bool = True) -> None:
        self._: TechnibelProtocol = TechnibelProtocol()
        self._saved_temp: int = 20  # DegC (Random reasonable default value)
        self._saved_temp_units: int = 0  # Celsius
        # _irsend not needed for Python implementation
        self.stateReset()

    ## Compute the checksum of the supplied state.
    ## @param[in] state A valid code for this protocol.
    ## @return The calculated checksum of the supplied state.
    ## Direct translation from ir_Technibel.cpp lines 107-114
    @staticmethod
    def calcChecksum(state: int) -> int:
        sum_val = 0
        # Add up all the 8 bit data chunks.
        for offset in range(kTechnibelAcTimerHoursOffset, kTechnibelAcHeaderOffset, 8):
            sum_val += GETBITS64(state, offset, 8)
        return (~sum_val + 1) & 0xFF

    ## Confirm the checksum of the supplied state is valid.
    ## @param[in] state A valid code for this protocol.
    ## @return `true` if the checksum is correct, otherwise `false`.
    ## Direct translation from ir_Technibel.cpp lines 119-122
    @staticmethod
    def validChecksum(state: int) -> bool:
        p = TechnibelProtocol()
        p.raw = state
        return IRTechnibelAc.calcChecksum(state) == p.Sum

    ## Set the checksum of the internal state.
    ## Direct translation from ir_Technibel.cpp lines 125-127
    def checksum(self) -> None:
        self._.Sum = IRTechnibelAc.calcChecksum(self._.raw)

    ## Reset the internal state of the emulation.
    ## @note Mode:Cool, Power:Off, fan:Low, temp:20, swing:Off, sleep:Off
    ## Direct translation from ir_Technibel.cpp lines 130-135
    def stateReset(self) -> None:
        self._.raw = kTechnibelAcResetState
        self._saved_temp = 20  # DegC  (Random reasonable default value)
        self._saved_temp_units = 0  # Celsius

    ## Get a copy of the internal state/code for this protocol.
    ## @return A code for this protocol based on the current internal state.
    ## Direct translation from ir_Technibel.cpp lines 139-142
    def getRaw(self) -> int:
        self.checksum()
        return self._.raw

    ## Set the internal state from a valid code for this protocol.
    ## @param[in] state A valid code for this protocol.
    ## Direct translation from ir_Technibel.cpp lines 146-148
    def setRaw(self, state: int) -> None:
        self._.raw = state

    ## Set the requested power state of the A/C to on.
    ## Direct translation from ir_Technibel.cpp line 151
    def on(self) -> None:
        self.setPower(True)

    ## Set the requested power state of the A/C to off.
    ## Direct translation from ir_Technibel.cpp line 154
    def off(self) -> None:
        self.setPower(False)

    ## Change the power setting.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Technibel.cpp lines 158-160
    def setPower(self, on: bool) -> None:
        self._.Power = on

    ## Get the value of the current power setting.
    ## @return true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Technibel.cpp lines 164-166
    def getPower(self) -> bool:
        return bool(self._.Power)

    ## Set the temperature unit setting.
    ## @param[in] fahrenheit true, the unit is °F. false, the unit is °C.
    ## Direct translation from ir_Technibel.cpp lines 170-173
    def setTempUnit(self, fahrenheit: bool) -> None:
        self._saved_temp_units = fahrenheit
        self._.UseFah = fahrenheit

    ## Get the temperature unit setting.
    ## @return true, the unit is °F. false, the unit is °C.
    ## Direct translation from ir_Technibel.cpp lines 177-179
    def getTempUnit(self) -> bool:
        return bool(self._.UseFah)

    ## Set the temperature.
    ## @param[in] degrees The temperature in degrees.
    ## @param[in] fahrenheit The temperature unit: true=°F, false(default)=°C.
    ## Direct translation from ir_Technibel.cpp lines 184-190
    def setTemp(self, degrees: int, fahrenheit: bool = False) -> None:
        self.setTempUnit(fahrenheit)
        temp_min = kTechnibelAcTempMinF if fahrenheit else kTechnibelAcTempMinC
        temp_max = kTechnibelAcTempMaxF if fahrenheit else kTechnibelAcTempMaxC
        self._saved_temp = min(temp_max, max(temp_min, degrees))
        self._.Temp = self._saved_temp

    ## Get the current temperature setting.
    ## @return The current setting for temp. in degrees.
    ## Direct translation from ir_Technibel.cpp lines 194-196
    def getTemp(self) -> int:
        return self._.Temp

    ## Set the speed of the fan.
    ## @param[in] speed The desired setting.
    ## Direct translation from ir_Technibel.cpp lines 200-215
    def setFan(self, speed: int) -> None:
        # Mode fan speed rules.
        if self._.Mode == kTechnibelAcDry and speed != kTechnibelAcFanLow:
            self._.Fan = kTechnibelAcFanLow
            return
        if speed in [kTechnibelAcFanHigh, kTechnibelAcFanMedium, kTechnibelAcFanLow]:
            self._.Fan = speed
        else:
            self._.Fan = kTechnibelAcFanLow

    ## Get the current fan speed setting.
    ## @return The current fan speed/mode.
    ## Direct translation from ir_Technibel.cpp lines 219-221
    def getFan(self) -> int:
        return self._.Fan

    ## Convert a stdAc::fanspeed_t enum into it's native speed.
    ## @param[in] speed The enum to be converted.
    ## @return The native equivalent of the enum.
    ## Direct translation from ir_Technibel.cpp lines 226-235
    @staticmethod
    def convertFan(speed: int) -> int:
        # Note: Using int instead of stdAc::fanspeed_t enum
        # kMin=0, kLow=1, kMedium=2, kHigh=3, kMax=4
        if speed in [0, 1]:  # kMin, kLow
            return kTechnibelAcFanLow
        elif speed == 2:  # kMedium
            return kTechnibelAcFanMedium
        elif speed in [3, 4]:  # kHigh, kMax
            return kTechnibelAcFanHigh
        else:
            return kTechnibelAcFanLow

    ## Convert a native fan speed into its stdAc equivalent.
    ## @param[in] speed The native setting to be converted.
    ## @return The stdAc equivalent of the native setting.
    ## Direct translation from ir_Technibel.cpp lines 240-246
    @staticmethod
    def toCommonFanSpeed(speed: int) -> int:
        # Returns int instead of stdAc::fanspeed_t enum
        if speed == kTechnibelAcFanHigh:
            return 3  # stdAc::fanspeed_t::kHigh
        elif speed == kTechnibelAcFanMedium:
            return 2  # stdAc::fanspeed_t::kMedium
        else:
            return 1  # stdAc::fanspeed_t::kLow

    ## Get the operating mode setting of the A/C.
    ## @return The current operating mode setting.
    ## Direct translation from ir_Technibel.cpp lines 250-252
    def getMode(self) -> int:
        return self._.Mode

    ## Set the operating mode of the A/C.
    ## @param[in] mode The desired operating mode.
    ## Direct translation from ir_Technibel.cpp lines 256-270
    def setMode(self, mode: int) -> None:
        self._.Mode = mode
        if mode in [kTechnibelAcHeat, kTechnibelAcFan, kTechnibelAcDry, kTechnibelAcCool]:
            pass
        else:
            self._.Mode = kTechnibelAcCool
        self.setFan(self._.Fan)  # Re-force any fan speed constraints.
        # Restore previous temp settings for cool mode.
        self.setTemp(self._saved_temp, self._saved_temp_units)

    ## Convert a stdAc::opmode_t enum into its native mode.
    ## @param[in] mode The enum to be converted.
    ## @return The native equivalent of the enum.
    ## Direct translation from ir_Technibel.cpp lines 275-282
    @staticmethod
    def convertMode(mode: int) -> int:
        # Note: Using int instead of stdAc::opmode_t enum
        # kCool=1, kHeat=2, kDry=3, kFan=4
        if mode == 2:  # kHeat
            return kTechnibelAcHeat
        elif mode == 3:  # kDry
            return kTechnibelAcDry
        elif mode == 4:  # kFan
            return kTechnibelAcFan
        else:
            return kTechnibelAcCool

    ## Convert a native mode into its stdAc equivalent.
    ## @param[in] mode The native setting to be converted.
    ## @return The stdAc equivalent of the native setting.
    ## Direct translation from ir_Technibel.cpp lines 287-294
    @staticmethod
    def toCommonMode(mode: int) -> int:
        # Returns int instead of stdAc::opmode_t enum
        if mode == kTechnibelAcHeat:
            return 2  # stdAc::opmode_t::kHeat
        elif mode == kTechnibelAcDry:
            return 3  # stdAc::opmode_t::kDry
        elif mode == kTechnibelAcFan:
            return 4  # stdAc::opmode_t::kFan
        else:
            return 1  # stdAc::opmode_t::kCool

    ## Set the (vertical) swing setting of the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Technibel.cpp lines 298-300
    def setSwing(self, on: bool) -> None:
        self._.Swing = on

    ## Get the (vertical) swing setting of the A/C.
    ## @return true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Technibel.cpp lines 304-306
    def getSwing(self) -> bool:
        return bool(self._.Swing)

    ## Convert a stdAc::swingv_t enum into it's native swing.
    ## @param[in] swing The enum to be converted.
    ## @return true, the swing is on. false, the swing is off.
    ## Direct translation from ir_Technibel.cpp lines 311-313
    @staticmethod
    def convertSwing(swing: int) -> bool:
        # Note: Using int instead of stdAc::swingv_t enum
        # kOff=0, kAuto=1, etc.
        return swing != 0  # swing != stdAc::swingv_t::kOff

    ## Convert a native swing into its stdAc equivalent.
    ## @param[in] swing true, the swing is on. false, the swing is off.
    ## @return The stdAc equivalent of the native setting.
    ## Direct translation from ir_Technibel.cpp lines 318-320
    @staticmethod
    def toCommonSwing(swing: bool) -> int:
        # Returns int instead of stdAc::swingv_t enum
        return 1 if swing else 0  # stdAc::swingv_t::kAuto : stdAc::swingv_t::kOff

    ## Set the Sleep setting of the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Technibel.cpp lines 324-326
    def setSleep(self, on: bool) -> None:
        self._.Sleep = on

    ## Get the Sleep setting of the A/C.
    ## @return true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Technibel.cpp lines 330-332
    def getSleep(self) -> bool:
        return bool(self._.Sleep)

    ## Set the enable timer setting.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Technibel.cpp lines 336-338
    def setTimerEnabled(self, on: bool) -> None:
        self._.TimerEnable = on

    ## Is the timer function enabled?
    ## @return true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Technibel.cpp lines 342-344
    def getTimerEnabled(self) -> bool:
        return bool(self._.TimerEnable)

    ## Set the timer for when the A/C unit will switch off.
    ## @param[in] nr_of_mins Number of minutes before power off.
    ##   `0` will clear the timer. Max is 24 hrs (1440 mins).
    ## @note Time is stored internally in hours.
    ## Direct translation from ir_Technibel.cpp lines 350-355
    def setTimer(self, nr_of_mins: int) -> None:
        hours = nr_of_mins // 60
        self._.TimerHours = min(kTechnibelAcTimerMax, hours)
        # Enable or not?
        self.setTimerEnabled(hours > 0)

    ## Get the timer time for when the A/C unit will switch power state.
    ## @return The number of minutes left on the timer. `0` means off.
    ## Direct translation from ir_Technibel.cpp lines 359-361
    def getTimer(self) -> int:
        return self._.TimerHours * 60 if self._.TimerEnable else 0
