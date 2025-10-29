# Copyright 2020 David Conran
# Python translation: Direct conversion from C++ with NO optimizations

## @file
## @brief Delonghi A/C
## @note Kudos to TheMaxxz For the breakdown and mapping of the bit values.
## Direct translation from IRremoteESP8266 ir_Delonghi.cpp and ir_Delonghi.h

from typing import List

# Supports:
#   Brand: Delonghi,  Model: PAC A95

# Ref: https://github.com/crankyoldgit/IRremoteESP8266/issues/1096

# Constants - Timing values (from ir_Delonghi.cpp lines 19-26)
kDelonghiAcHdrMark = 8984
kDelonghiAcBitMark = 572
kDelonghiAcHdrSpace = 4200
kDelonghiAcOneSpace = 1558
kDelonghiAcZeroSpace = 510
kDelonghiAcGap = 100000  # kDefaultMessageGap - A totally made-up guess.
kDelonghiAcFreq = 38000  # Hz. (Guess: most common frequency.)
kDelonghiAcOverhead = 3

# State length constants
kDelonghiAcBits = 64
kDelonghiAcStateLength = 8  # 64 bits / 8 = 8 bytes

# Constants (from ir_Delonghi.h lines 52-68)
kDelonghiAcTempMinC = 18  # Deg C
kDelonghiAcTempMaxC = 32  # Deg C
kDelonghiAcTempMinF = 64  # Deg F
kDelonghiAcTempMaxF = 90  # Deg F
kDelonghiAcTempAutoDryMode = 0
kDelonghiAcTempFanMode = 0b00110
kDelonghiAcFanAuto = 0b00
kDelonghiAcFanHigh = 0b01
kDelonghiAcFanMedium = 0b10
kDelonghiAcFanLow = 0b11
kDelonghiAcCool = 0b000
kDelonghiAcDry = 0b001
kDelonghiAcFan = 0b010
kDelonghiAcAuto = 0b100
kDelonghiAcTimerMax = 23 * 60 + 59
kDelonghiAcChecksumOffset = 56

# Default repeat count
kDelonghiAcDefaultRepeat = 0


def GETBITS64(value: int, offset: int, nbits: int) -> int:
    """
    Extract bits from a 64-bit value.
    Helper function for bit manipulation.
    """
    return (value >> offset) & ((1 << nbits) - 1)


## Native representation of a Delonghi A/C message.
## This is a direct translation of the C++ union/struct (from ir_Delonghi.h lines 26-50)
class DelonghiProtocol:
    def __init__(self):
        self.raw = 0  # 64-bit value

    # Byte 0 - Header (bits 0-7)

    # Byte 1 (bits 8-15)
    @property
    def Temp(self) -> int:
        return (self.raw >> 8) & 0x1F

    @Temp.setter
    def Temp(self, value: int) -> None:
        self.raw = (self.raw & ~(0x1F << 8)) | ((value & 0x1F) << 8)

    @property
    def Fan(self) -> int:
        return (self.raw >> 13) & 0x03

    @Fan.setter
    def Fan(self, value: int) -> None:
        self.raw = (self.raw & ~(0x03 << 13)) | ((value & 0x03) << 13)

    @property
    def Fahrenheit(self) -> int:
        return (self.raw >> 15) & 0x01

    @Fahrenheit.setter
    def Fahrenheit(self, value: bool) -> None:
        if value:
            self.raw |= 1 << 15
        else:
            self.raw &= ~(1 << 15)

    # Byte 2 (bits 16-23)
    @property
    def Power(self) -> int:
        return (self.raw >> 16) & 0x01

    @Power.setter
    def Power(self, value: bool) -> None:
        if value:
            self.raw |= 1 << 16
        else:
            self.raw &= ~(1 << 16)

    @property
    def Mode(self) -> int:
        return (self.raw >> 17) & 0x07

    @Mode.setter
    def Mode(self, value: int) -> None:
        self.raw = (self.raw & ~(0x07 << 17)) | ((value & 0x07) << 17)

    @property
    def Boost(self) -> int:
        return (self.raw >> 20) & 0x01

    @Boost.setter
    def Boost(self, value: bool) -> None:
        if value:
            self.raw |= 1 << 20
        else:
            self.raw &= ~(1 << 20)

    @property
    def Sleep(self) -> int:
        return (self.raw >> 21) & 0x01

    @Sleep.setter
    def Sleep(self, value: bool) -> None:
        if value:
            self.raw |= 1 << 21
        else:
            self.raw &= ~(1 << 21)

    # Byte 3 (bits 24-31)
    @property
    def OnTimer(self) -> int:
        return (self.raw >> 24) & 0x01

    @OnTimer.setter
    def OnTimer(self, value: bool) -> None:
        if value:
            self.raw |= 1 << 24
        else:
            self.raw &= ~(1 << 24)

    @property
    def OnHours(self) -> int:
        return (self.raw >> 25) & 0x1F

    @OnHours.setter
    def OnHours(self, value: int) -> None:
        self.raw = (self.raw & ~(0x1F << 25)) | ((value & 0x1F) << 25)

    # Byte 4 (bits 32-39)
    @property
    def OnMins(self) -> int:
        return (self.raw >> 32) & 0x3F

    @OnMins.setter
    def OnMins(self, value: int) -> None:
        self.raw = (self.raw & ~(0x3F << 32)) | ((value & 0x3F) << 32)

    # Byte 5 (bits 40-47)
    @property
    def OffTimer(self) -> int:
        return (self.raw >> 40) & 0x01

    @OffTimer.setter
    def OffTimer(self, value: bool) -> None:
        if value:
            self.raw |= 1 << 40
        else:
            self.raw &= ~(1 << 40)

    @property
    def OffHours(self) -> int:
        return (self.raw >> 41) & 0x1F

    @OffHours.setter
    def OffHours(self, value: int) -> None:
        self.raw = (self.raw & ~(0x1F << 41)) | ((value & 0x1F) << 41)

    # Byte 6 (bits 48-55)
    @property
    def OffMins(self) -> int:
        return (self.raw >> 48) & 0x3F

    @OffMins.setter
    def OffMins(self, value: int) -> None:
        self.raw = (self.raw & ~(0x3F << 48)) | ((value & 0x3F) << 48)

    # Byte 7 (bits 56-63)
    @property
    def Sum(self) -> int:
        return (self.raw >> 56) & 0xFF

    @Sum.setter
    def Sum(self, value: int) -> None:
        self.raw = (self.raw & ~(0xFF << 56)) | ((value & 0xFF) << 56)


## Send a Delonghi A/C formatted message.
## Status: STABLE / Reported as working on a real device.
## @param[in] data The message to be sent.
## @param[in] nbits The number of bits of message to be sent.
## @param[in] repeat The number of times the command is to be repeated.
## Direct translation from IRremoteESP8266 IRsend::sendDelonghiAc (ir_Delonghi.cpp lines 29-44)
def sendDelonghiAc(data: int, nbits: int = kDelonghiAcBits, repeat: int = 0) -> List[int]:
    """
    Send a Delonghi A/C formatted message.
    EXACT translation from IRremoteESP8266 IRsend::sendDelonghiAc

    Returns timing array instead of transmitting via hardware.
    """
    # Import here to avoid circular import
    from app.core.ir_protocols.ir_send import sendGeneric

    timings = sendGeneric(
        headermark=kDelonghiAcHdrMark,
        headerspace=kDelonghiAcHdrSpace,
        onemark=kDelonghiAcBitMark,
        onespace=kDelonghiAcOneSpace,
        zeromark=kDelonghiAcBitMark,
        zerospace=kDelonghiAcZeroSpace,
        footermark=kDelonghiAcBitMark,
        gap=kDelonghiAcGap,
        data=data,
        nbits=nbits,
        frequency=kDelonghiAcFreq,
        MSBfirst=False,  # LSB First
        repeat=repeat,
        dutycycle=50,
    )
    return timings


## Class for handling detailed Delonghi A/C messages.
## Direct translation from C++ IRDelonghiAc class (from ir_Delonghi.h lines 73-135)
class IRDelonghiAc:
    ## Class Constructor
    ## @param[in] pin GPIO to be used when sending. (Not used in Python)
    ## @param[in] inverted Is the output signal to be inverted? (Not used in Python)
    ## @param[in] use_modulation Is frequency modulation to be used? (Not used in Python)
    ## Direct translation from ir_Delonghi.cpp lines 89-95
    def __init__(self) -> None:
        self._: DelonghiProtocol = DelonghiProtocol()
        self._saved_temp: int = 23  # DegC  (Random reasonable default value)
        self._saved_temp_units: int = 0  # Celsius
        self.stateReset()

    ## Reset the internal state to a fixed known good state.
    ## Direct translation from ir_Delonghi.cpp lines 134-139
    def stateReset(self) -> None:
        self._.raw = 0x5400000000000153
        self._saved_temp = 23  # DegC  (Random reasonable default value)
        self._saved_temp_units = 0  # Celsius

    ## Calculate the checksum for a given state.
    ## @param[in] state The value to calc the checksum of.
    ## @return A valid checksum value.
    ## Direct translation from ir_Delonghi.cpp lines 108-118
    @staticmethod
    def calcChecksum(state: int) -> int:
        sum_val = 0
        # Add up all the 8 bit chunks except for Most-significant 8 bits.
        for offset in range(0, kDelonghiAcChecksumOffset, 8):
            sum_val += GETBITS64(state, offset, 8)
        return sum_val & 0xFF

    ## Verify the checksum is valid for a given state.
    ## @param[in] state The state to verify the checksum of.
    ## @return true, if the state has a valid checksum. Otherwise, false.
    ## Direct translation from ir_Delonghi.cpp lines 120-127
    @staticmethod
    def validChecksum(state: int) -> bool:
        dp = DelonghiProtocol()
        dp.raw = state
        return dp.Sum == IRDelonghiAc.calcChecksum(state)

    ## Calculate and set the checksum values for the internal state.
    ## Direct translation from ir_Delonghi.cpp lines 129-132
    def checksum(self) -> None:
        self._.Sum = self.calcChecksum(self._.raw)

    ## Get a copy of the internal state as a valid code for this protocol.
    ## @return A valid code for this protocol based on the current internal state.
    ## Direct translation from ir_Delonghi.cpp lines 141-146
    def getRaw(self) -> int:
        self.checksum()  # Ensure correct bit array before returning
        return self._.raw

    ## Set the internal state from a valid code for this protocol.
    ## @param[in] state A valid code for this protocol.
    ## Direct translation from ir_Delonghi.cpp line 150
    def setRaw(self, state: int) -> None:
        self._.raw = state

    ## Change the power setting to On.
    ## Direct translation from ir_Delonghi.cpp line 153
    def on(self) -> None:
        self.setPower(True)

    ## Change the power setting to Off.
    ## Direct translation from ir_Delonghi.cpp line 156
    def off(self) -> None:
        self.setPower(False)

    ## Change the power setting.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Delonghi.cpp lines 159-162
    def setPower(self, on: bool) -> None:
        self._.Power = on

    ## Get the value of the current power setting.
    ## @return true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Delonghi.cpp lines 164-168
    def getPower(self) -> bool:
        return bool(self._.Power)

    ## Change the temperature scale units.
    ## @param[in] fahrenheit true, use Fahrenheit. false, use Celsius.
    ## Direct translation from ir_Delonghi.cpp lines 170-174
    def setTempUnit(self, fahrenheit: bool) -> None:
        self._.Fahrenheit = fahrenheit

    ## Get the temperature scale unit of measure currently in use.
    ## @return true, is Fahrenheit. false, is Celsius.
    ## Direct translation from ir_Delonghi.cpp lines 176-180
    def getTempUnit(self) -> bool:
        return bool(self._.Fahrenheit)

    ## Set the temperature.
    ## @param[in] degrees The temperature in degrees.
    ## @param[in] fahrenheit Use Fahrenheit as the temperature scale.
    ## @param[in] force Do we ignore any sanity checks?
    ## Direct translation from ir_Delonghi.cpp lines 182-206
    def setTemp(self, degrees: int, fahrenheit: bool = False, force: bool = False) -> None:
        if force:
            temp = degrees  # We've been asked to force set this value.
        else:
            temp_min = kDelonghiAcTempMinC
            temp_max = kDelonghiAcTempMaxC
            self.setTempUnit(fahrenheit)
            if fahrenheit:
                temp_min = kDelonghiAcTempMinF
                temp_max = kDelonghiAcTempMaxF
            temp = max(temp_min, degrees)
            temp = min(temp_max, temp)
            self._saved_temp = temp
            self._saved_temp_units = fahrenheit
            temp = temp - temp_min + 1
        self._.Temp = temp

    ## Get the current temperature setting.
    ## @return The current setting for temp. in currently configured units/scale.
    ## Direct translation from ir_Delonghi.cpp lines 208-213
    def getTemp(self) -> int:
        return self._.Temp + (kDelonghiAcTempMinF if self._.Fahrenheit else kDelonghiAcTempMinC) - 1

    ## Set the speed of the fan.
    ## @param[in] speed The desired native setting.
    ## Direct translation from ir_Delonghi.cpp lines 215-241
    def setFan(self, speed: int) -> None:
        # Mode fan speed rules.
        if self._.Mode == kDelonghiAcFan:
            # Fan mode can't have auto fan speed.
            if speed == kDelonghiAcFanAuto:
                if self._.Fan == kDelonghiAcFanAuto:
                    self._.Fan = kDelonghiAcFanHigh
                return
        elif self._.Mode == kDelonghiAcAuto or self._.Mode == kDelonghiAcDry:
            # Auto & Dry modes only allows auto fan speed.
            if speed != kDelonghiAcFanAuto:
                self._.Fan = kDelonghiAcFanAuto
                return
        # Bounds check enforcement
        if speed > kDelonghiAcFanLow:
            self._.Fan = kDelonghiAcFanAuto
        else:
            self._.Fan = speed

    ## Get the current native fan speed setting.
    ## @return The current fan speed.
    ## Direct translation from ir_Delonghi.cpp lines 243-247
    def getFan(self) -> int:
        return self._.Fan

    ## Convert a stdAc::fanspeed_t enum into it's native speed.
    ## @param[in] speed The enum to be converted.
    ## @return The native equivalent of the enum.
    ## Direct translation from ir_Delonghi.cpp lines 249-265
    @staticmethod
    def convertFan(speed: int) -> int:
        # stdAc::fanspeed_t values (approximated):
        # kMin = 1, kLow = 2, kMedium = 3, kHigh = 4, kMax = 5, kAuto = 0
        if speed in [1, 2]:  # kMin, kLow
            return kDelonghiAcFanLow
        elif speed == 3:  # kMedium
            return kDelonghiAcFanMedium
        elif speed in [4, 5]:  # kHigh, kMax
            return kDelonghiAcFanHigh
        else:
            return kDelonghiAcFanAuto

    ## Convert a native fan speed into its stdAc equivalent.
    ## @param[in] speed The native setting to be converted.
    ## @return The stdAc equivalent of the native setting.
    ## Direct translation from ir_Delonghi.cpp lines 267-277
    @staticmethod
    def toCommonFanSpeed(speed: int) -> int:
        if speed == kDelonghiAcFanHigh:
            return 5  # stdAc::fanspeed_t::kMax
        elif speed == kDelonghiAcFanMedium:
            return 3  # stdAc::fanspeed_t::kMedium
        elif speed == kDelonghiAcFanLow:
            return 1  # stdAc::fanspeed_t::kMin
        else:
            return 0  # stdAc::fanspeed_t::kAuto

    ## Get the operating mode setting of the A/C.
    ## @return The current operating mode setting.
    ## Direct translation from ir_Delonghi.cpp lines 279-283
    def getMode(self) -> int:
        return self._.Mode

    ## Set the operating mode of the A/C.
    ## @param[in] mode The desired native operating mode.
    ## Direct translation from ir_Delonghi.cpp lines 285-309
    def setMode(self, mode: int) -> None:
        self._.Mode = mode
        if mode == kDelonghiAcAuto or mode == kDelonghiAcDry:
            # Set special temp for these modes.
            self.setTemp(kDelonghiAcTempAutoDryMode, self._.Fahrenheit, True)
        elif mode == kDelonghiAcFan:
            # Set special temp for this mode.
            self.setTemp(kDelonghiAcTempFanMode, self._.Fahrenheit, True)
        elif mode == kDelonghiAcCool:
            # Restore previous temp settings for cool mode.
            self.setTemp(self._saved_temp, self._saved_temp_units)
        else:
            self._.Mode = kDelonghiAcAuto
            self.setTemp(kDelonghiAcTempAutoDryMode, self._.Fahrenheit, True)
        self.setFan(self._.Fan)  # Re-force any fan speed constraints.

    ## Convert a stdAc::opmode_t enum into its native mode.
    ## @param[in] mode The enum to be converted.
    ## @return The native equivalent of the enum.
    ## Direct translation from ir_Delonghi.cpp lines 311-325
    @staticmethod
    def convertMode(mode: int) -> int:
        # stdAc::opmode_t values (approximated):
        # kCool = 1, kDry = 3, kFan = 4, kAuto = 0
        if mode == 1:  # kCool
            return kDelonghiAcCool
        elif mode == 3:  # kDry
            return kDelonghiAcDry
        elif mode == 4:  # kFan
            return kDelonghiAcFan
        else:
            return kDelonghiAcAuto

    ## Convert a native mode into its stdAc equivalent.
    ## @param[in] mode The native setting to be converted.
    ## @return The stdAc equivalent of the native setting.
    ## Direct translation from ir_Delonghi.cpp lines 327-337
    @staticmethod
    def toCommonMode(mode: int) -> int:
        if mode == kDelonghiAcCool:
            return 1  # stdAc::opmode_t::kCool
        elif mode == kDelonghiAcDry:
            return 3  # stdAc::opmode_t::kDry
        elif mode == kDelonghiAcFan:
            return 4  # stdAc::opmode_t::kFan
        else:
            return 0  # stdAc::opmode_t::kAuto

    ## Set the Boost (Turbo) mode of the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Delonghi.cpp lines 339-343
    def setBoost(self, on: bool) -> None:
        self._.Boost = on

    ## Get the Boost (Turbo) mode of the A/C.
    ## @return true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Delonghi.cpp lines 345-349
    def getBoost(self) -> bool:
        return bool(self._.Boost)

    ## Set the Sleep mode of the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Delonghi.cpp lines 351-355
    def setSleep(self, on: bool) -> None:
        self._.Sleep = on

    ## Get the Sleep mode status of the A/C.
    ## @return true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Delonghi.cpp lines 357-361
    def getSleep(self) -> bool:
        return bool(self._.Sleep)

    ## Set the enable status of the On Timer.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Delonghi.cpp lines 363-367
    def setOnTimerEnabled(self, on: bool) -> None:
        self._.OnTimer = on

    ## Get the enable status of the On Timer.
    ## @return true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Delonghi.cpp lines 369-373
    def getOnTimerEnabled(self) -> bool:
        return bool(self._.OnTimer)

    ## Set the On timer to activate in nr of minutes.
    ## @param[in] nr_of_mins Total nr of mins to wait before waking the device.
    ## @note Max 23 hrs and 59 minutes. i.e. 1439 mins.
    ## Direct translation from ir_Delonghi.cpp lines 375-384
    def setOnTimer(self, nr_of_mins: int) -> None:
        value = min(kDelonghiAcTimerMax, nr_of_mins)
        self._.OnMins = value % 60
        self._.OnHours = value // 60
        # Enable or not?
        self.setOnTimerEnabled(value > 0)

    ## Get the On timer time.
    ## @return Total nr of mins before the device turns on.
    ## Direct translation from ir_Delonghi.cpp lines 386-390
    def getOnTimer(self) -> int:
        return self._.OnHours * 60 + self._.OnMins

    ## Set the enable status of the Off Timer.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Delonghi.cpp lines 392-396
    def setOffTimerEnabled(self, on: bool) -> None:
        self._.OffTimer = on

    ## Get the enable status of the Off Timer.
    ## @return true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Delonghi.cpp lines 398-402
    def getOffTimerEnabled(self) -> bool:
        return bool(self._.OffTimer)

    ## Set the Off timer to activate in nr of minutes.
    ## @param[in] nr_of_mins Total nr of mins to wait before turning off the device
    ## @note Max 23 hrs and 59 minutes. i.e. 1439 mins.
    ## Direct translation from ir_Delonghi.cpp lines 404-413
    def setOffTimer(self, nr_of_mins: int) -> None:
        value = min(kDelonghiAcTimerMax, nr_of_mins)
        self._.OffMins = value % 60
        self._.OffHours = value // 60
        # Enable or not?
        self.setOffTimerEnabled(value > 0)

    ## Get the Off timer time.
    ## @return Total nr of mins before the device turns off.
    ## Direct translation from ir_Delonghi.cpp lines 415-419
    def getOffTimer(self) -> int:
        return self._.OffHours * 60 + self._.OffMins

    ## Convert the current internal state into its stdAc::state_t equivalent.
    ## @return The stdAc equivalent of the native settings.
    ## Direct translation from ir_Delonghi.cpp lines 421-445
    def toCommon(self) -> dict:
        result = {}
        result["protocol"] = "DELONGHI_AC"
        result["power"] = bool(self._.Power)
        # result['mode'] = self.toCommonMode(self.getMode())
        result["celsius"] = not bool(self._.Fahrenheit)
        result["degrees"] = self.getTemp()
        result["fanspeed"] = self.toCommonFanSpeed(self._.Fan)
        result["turbo"] = bool(self._.Boost)
        result["sleep"] = 0 if self._.Sleep else -1
        # Not supported.
        result["model"] = -1
        result["swingv"] = 0  # stdAc::swingv_t::kOff
        result["swingh"] = 0  # stdAc::swingh_t::kOff
        result["light"] = False
        result["filter"] = False
        result["econo"] = False
        result["quiet"] = False
        result["clean"] = False
        result["beep"] = False
        result["clock"] = -1
        return result

    ## Convert the current internal state into a human readable string.
    ## @return A human readable string.
    ## Direct translation from ir_Delonghi.cpp lines 447-470
    def toString(self) -> str:
        result = ""
        result += "Power: " + ("On" if self._.Power else "Off") + ", "
        result += "Mode: " + str(self._.Mode) + ", "
        result += "Fan: " + str(self._.Fan) + ", "
        result += "Temp: " + str(self.getTemp())
        result += ("F" if self._.Fahrenheit else "C") + ", "
        result += "Turbo: " + ("On" if self._.Boost else "Off") + ", "
        result += "Sleep: " + ("On" if self._.Sleep else "Off") + ", "
        mins = self.getOnTimer()
        result += "On Timer: " + (str(mins) + "m" if (mins and self._.OnTimer) else "Off") + ", "
        mins = self.getOffTimer()
        result += "Off Timer: " + (str(mins) + "m" if (mins and self._.OffTimer) else "Off")
        return result


## Decode the supplied Delonghi A/C message.
## Status: STABLE / Expected to be working.
## @param[in,out] results Ptr to the data to decode & where to store the decode result.
## @param[in] offset The starting index to use when attempting to decode the raw data.
## @param[in] nbits The number of data bits to expect.
## @param[in] strict Flag indicating if we should perform strict matching.
## @return A boolean. True if it can decode it, false if it can't.
## Direct translation from IRremoteESP8266 IRrecv::decodeDelonghiAc (ir_Delonghi.cpp lines 47-86)
def decodeDelonghiAc(
    results, offset: int = 1, nbits: int = kDelonghiAcBits, strict: bool = True
) -> bool:
    """
    Decode a Delonghi A/C IR message.
    EXACT translation from IRremoteESP8266 IRrecv::decodeDelonghiAc

    This is the ACTUAL C++ decoder function, not a wrapper.
    """
    # Import here to avoid circular imports
    from app.core.ir_protocols.ir_recv import kMarkExcess, _matchGeneric

    # Too short a message to match. (from ir_Delonghi.cpp lines 60-61)
    if results.rawlen < 2 * nbits + kDelonghiAcOverhead - offset:
        return False
    if strict and nbits != kDelonghiAcBits:
        return False

    data = 0

    # Header + Data + Footer (from ir_Delonghi.cpp lines 67-74)
    if not _matchGeneric(
        data_ptr=results.rawbuf[offset:],
        result_bits_ptr=None,
        result_bytes_ptr=None,
        use_bits=True,
        remaining=results.rawlen - offset,
        nbits=nbits,
        hdrmark=kDelonghiAcHdrMark,
        hdrspace=kDelonghiAcHdrSpace,
        onemark=kDelonghiAcBitMark,
        onespace=kDelonghiAcOneSpace,
        zeromark=kDelonghiAcBitMark,
        zerospace=kDelonghiAcZeroSpace,
        footermark=kDelonghiAcBitMark,
        footerspace=kDelonghiAcGap,
        atleast=True,
        tolerance=25,
        excess=kMarkExcess,
        MSBfirst=False,
    ):
        return False

    # Compliance (from ir_Delonghi.cpp lines 76-77)
    if strict and not IRDelonghiAc.validChecksum(data):
        return False

    # Success (from ir_Delonghi.cpp lines 79-85)
    # results.decode_type = decode_type_t::DELONGHI_AC;
    results.bits = nbits
    results.value = data
    results.command = 0
    results.address = 0
    return True
