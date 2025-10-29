# Copyright 2020 David Conran
# Python translation: Direct conversion from C++ with NO optimizations

## @file
## @brief Support for Airwell "Manchester code" based protocol.
## Direct translation from IRremoteESP8266 ir_Airwell.cpp and ir_Airwell.h
## Some other Airwell products use the COOLIX protocol.

from typing import List, Optional

# Supports:
#   Brand: Airwell,  Model: RC08W remote
#   Brand: Airwell,  Model: RC04 remote
#   Brand: Airwell,  Model: DLS 21 DCI R410 AW A/C

# Constants - Timing values (from ir_Airwell.cpp lines 13-17)
kAirwellOverhead = 4
kAirwellHalfClockPeriod = 950  # uSeconds
kAirwellHdrMark = 3 * kAirwellHalfClockPeriod  # uSeconds
kAirwellHdrSpace = 3 * kAirwellHalfClockPeriod  # uSeconds
kAirwellFooterMark = 5 * kAirwellHalfClockPeriod  # uSeconds

# State length constants (from IRremoteESP8266.h)
kAirwellBits = 34
kAirwellMinRepeats = 2

# Known good state (from ir_Airwell.h line 41)
kAirwellKnownGoodState = 0x140500002  # Mode Fan, Speed 1, 25C

# Temperature constants (from ir_Airwell.h lines 43-44)
kAirwellMinTemp = 16  # Celsius
kAirwellMaxTemp = 30  # Celsius

# Fan constants (from ir_Airwell.h lines 46-49)
kAirwellFanLow = 0  # 0b00
kAirwellFanMedium = 1  # 0b01
kAirwellFanHigh = 2  # 0b10
kAirwellFanAuto = 3  # 0b11

# Mode constants (from ir_Airwell.h lines 51-55)
kAirwellCool = 1  # 0b001
kAirwellHeat = 2  # 0b010
kAirwellAuto = 3  # 0b011
kAirwellDry = 4  # 0b100
kAirwellFan = 5  # 0b101


## Native representation of a Airwell A/C message.
## This is a direct translation of the C++ union/struct (from ir_Airwell.h lines 26-38)
class AirwellProtocol:
    def __init__(self):
        # 64-bit raw value
        self.raw = 0

    # Temp - bits 19-22 (from ir_Airwell.h line 31)
    @property
    def Temp(self) -> int:
        return (self.raw >> 19) & 0x0F

    @Temp.setter
    def Temp(self, value: int) -> None:
        mask = 0x0F << 19
        self.raw = (self.raw & ~mask) | ((value & 0x0F) << 19)

    # Fan - bits 28-29 (from ir_Airwell.h line 33)
    @property
    def Fan(self) -> int:
        return (self.raw >> 28) & 0x03

    @Fan.setter
    def Fan(self, value: int) -> None:
        mask = 0x03 << 28
        self.raw = (self.raw & ~mask) | ((value & 0x03) << 28)

    # Mode - bits 30-32 (from ir_Airwell.h line 34)
    @property
    def Mode(self) -> int:
        return (self.raw >> 30) & 0x07

    @Mode.setter
    def Mode(self, value: int) -> None:
        mask = 0x07 << 30
        self.raw = (self.raw & ~mask) | ((value & 0x07) << 30)

    # PowerToggle - bit 33 (from ir_Airwell.h line 35)
    @property
    def PowerToggle(self) -> int:
        return (self.raw >> 33) & 0x01

    @PowerToggle.setter
    def PowerToggle(self, value: bool) -> None:
        if value:
            self.raw |= 1 << 33
        else:
            self.raw &= ~(1 << 33)


## Send an Airwell Manchester Code formatted message.
## Status: BETA / Appears to be working.
## @param[in] data The message to be sent.
## @param[in] nbits The number of bits of the message to be sent.
## @param[in] repeat The number of times the command is to be repeated.
## @see https://github.com/crankyoldgit/IRremoteESP8266/issues/1069
## Direct translation from IRremoteESP8266 IRsend::sendAirwell (ir_Airwell.cpp lines 24-38)
def sendAirwell(
    data: int, nbits: int = kAirwellBits, repeat: int = kAirwellMinRepeats
) -> List[int]:
    """
    Send an Airwell Manchester Code formatted message.
    EXACT translation from IRremoteESP8266 IRsend::sendAirwell

    Returns timing array instead of transmitting via hardware.
    """
    # Import here to avoid circular import
    from app.core.ir_protocols.ir_send import sendManchester64

    all_timings = []

    for r in range(repeat + 1):
        # Header + Data
        timings = sendManchester64(
            headermark=kAirwellHdrMark,
            headerspace=kAirwellHdrMark,
            half_clock_period=kAirwellHalfClockPeriod,
            footermark=0,
            footerspace=0,
            data=data,
            nbits=nbits,
            frequency=38000,
            MSBfirst=True,
            dutycycle=50,
            leadingzero=False,
        )
        all_timings.extend(timings)

        # Footer
        all_timings.append(kAirwellHdrMark + kAirwellHalfClockPeriod)
        all_timings.append(100000)  # kDefaultMessageGap - A guess.

    return all_timings


## Decode the supplied Airwell "Manchester code" message.
##
## Status: BETA / Appears to be working.
## @param[in,out] results Ptr to the data to decode & where to store the decode
##   result.
## @param[in] offset The starting index to use when attempting to decode the
##   raw data. Typically/Defaults to kStartOffset.
## @param[in] nbits The number of data bits to expect.
## @param[in] strict Flag indicating if we should perform strict matching.
## @return A boolean. True if it can decode it, false if it can't.
## @see https://github.com/crankyoldgit/IRremoteESP8266/issues/1069
## Direct translation from IRremoteESP8266 IRrecv::decodeAirwell (ir_Airwell.cpp lines 41-78)
def decodeAirwell(
    results, offset: int = 1, nbits: int = kAirwellBits, strict: bool = True, _tolerance: int = 25
) -> bool:
    """
    Decode an Airwell "Manchester code" HVAC IR message.
    EXACT translation from IRremoteESP8266 IRrecv::decodeAirwell

    This is the ACTUAL C++ decoder function, not a wrapper.
    """
    # Import here to avoid circular imports
    from app.core.ir_protocols.ir_recv import kMarkExcess, matchManchester

    if results.rawlen < nbits + kAirwellOverhead - offset:
        return False  # Too short a message to match.

    # Compliance
    if strict and nbits != kAirwellBits:
        return False  # Doesn't match our protocol defn.

    # Header #1 + Data #1 + Footer #1 (There are total of 3 sections)
    match_result = matchManchester(
        data_ptr=results.rawbuf[offset:],
        result=results.value,
        remaining=results.rawlen - offset,
        nbits=nbits,
        hdrmark=kAirwellHdrMark,
        hdrspace=kAirwellHdrMark,
        half_clock_period=kAirwellHalfClockPeriod,
        footermark=kAirwellHdrMark,
        footerspace=kAirwellHdrSpace,
        atleast=True,
        tolerance=_tolerance,
        excess=kMarkExcess,
        MSBfirst=True,
        GEThomas=False,
    )
    if match_result.used == 0:
        return False
    offset += match_result.used

    # Success
    # results.decode_type = AIRWELL
    results.bits = nbits
    results.address = 0
    results.command = 0
    return True


## Class for handling detailed Airwell A/C messages.
## Direct translation from C++ IRAirwellAc class (ir_Airwell.h lines 59-100, ir_Airwell.cpp lines 81-286)
class IRAirwellAc:
    ## Class Constructor
    ## @param[in] pin GPIO to be used when sending.
    ## @param[in] inverted Is the output signal to be inverted?
    ## @param[in] use_modulation Is frequency modulation to be used?
    ## Direct translation from ir_Airwell.cpp lines 81-87
    def __init__(self) -> None:
        self._: AirwellProtocol = AirwellProtocol()
        self.stateReset()

    ## Reset the internals of the object to a known good state.
    ## Direct translation from ir_Airwell.cpp lines 113-116
    def stateReset(self) -> None:
        self._.raw = kAirwellKnownGoodState

    ## Get the raw state of the object, suitable to be sent with the appropriate
    ## IRsend object method.
    ## @return A copy of the internal state.
    ## Direct translation from ir_Airwell.cpp lines 92-97
    def getRaw(self) -> int:
        return self._.raw

    ## Set the raw state of the object.
    ## @param[in] state The raw state from the native IR message.
    ## Direct translation from ir_Airwell.cpp lines 99-103
    def setRaw(self, state: int) -> None:
        self._.raw = state

    ## Turn on/off the Power Airwell setting.
    ## @param[in] on The desired setting state.
    ## Direct translation from ir_Airwell.cpp lines 118-122
    def setPowerToggle(self, on: bool) -> None:
        self._.PowerToggle = on

    ## Get the power toggle setting from the internal state.
    ## @return A boolean indicating the setting.
    ## Direct translation from ir_Airwell.cpp lines 124-128
    def getPowerToggle(self) -> bool:
        return bool(self._.PowerToggle)

    ## Get the current operation mode setting.
    ## @return The current operation mode.
    ## Direct translation from ir_Airwell.cpp lines 130-134
    def getMode(self) -> int:
        return self._.Mode

    ## Set the desired operation mode.
    ## @param[in] mode The desired operation mode.
    ## Direct translation from ir_Airwell.cpp lines 136-151
    def setMode(self, mode: int) -> None:
        if mode in [kAirwellFan, kAirwellCool, kAirwellHeat, kAirwellDry, kAirwellAuto]:
            self._.Mode = mode
        else:
            self._.Mode = kAirwellAuto
        self.setFan(self.getFan())  # Ensure the fan is at the correct speed for the new mode.

    ## Convert a stdAc::opmode_t enum into its native mode.
    ## @param[in] mode The enum to be converted.
    ## @return The native equivalent of the enum.
    ## Direct translation from ir_Airwell.cpp lines 153-164
    @staticmethod
    def convertMode(mode: str) -> int:
        """Convert common mode to Airwell mode"""
        if mode == "cool":
            return kAirwellCool
        elif mode == "heat":
            return kAirwellHeat
        elif mode == "dry":
            return kAirwellDry
        elif mode == "fan":
            return kAirwellFan
        else:
            return kAirwellAuto

    ## Convert a native mode into its stdAc equivalent.
    ## @param[in] mode The native setting to be converted.
    ## @return The stdAc equivalent of the native setting.
    ## Direct translation from ir_Airwell.cpp lines 166-177
    @staticmethod
    def toCommonMode(mode: int) -> str:
        """Convert Airwell mode to common mode"""
        if mode == kAirwellCool:
            return "cool"
        elif mode == kAirwellHeat:
            return "heat"
        elif mode == kAirwellDry:
            return "dry"
        elif mode == kAirwellFan:
            return "fan"
        else:
            return "auto"

    ## Set the speed of the fan.
    ## @param[in] speed The desired setting.
    ## @note The speed is locked to Low when in Dry mode.
    ## Direct translation from ir_Airwell.cpp lines 179-185
    def setFan(self, speed: int) -> None:
        if self._.Mode == kAirwellDry:
            self._.Fan = kAirwellFanLow
        else:
            self._.Fan = min(speed, kAirwellFanAuto)

    ## Get the current fan speed setting.
    ## @return The current fan speed.
    ## Direct translation from ir_Airwell.cpp lines 187-191
    def getFan(self) -> int:
        return self._.Fan

    ## Convert a stdAc::fanspeed_t enum into it's native speed.
    ## @param[in] speed The enum to be converted.
    ## @return The native equivalent of the enum.
    ## Direct translation from ir_Airwell.cpp lines 193-209
    @staticmethod
    def convertFan(speed: str) -> int:
        """Convert common fan speed to Airwell fan speed"""
        if speed in ["min", "low"]:
            return kAirwellFanLow
        elif speed == "medium":
            return kAirwellFanMedium
        elif speed in ["high", "max"]:
            return kAirwellFanHigh
        else:
            return kAirwellFanAuto

    ## Convert a native fan speed into its stdAc equivalent.
    ## @param[in] speed The native setting to be converted.
    ## @return The stdAc equivalent of the native setting.
    ## Direct translation from ir_Airwell.cpp lines 211-221
    @staticmethod
    def toCommonFanSpeed(speed: int) -> str:
        """Convert Airwell fan speed to common fan speed"""
        if speed == kAirwellFanHigh:
            return "max"
        elif speed == kAirwellFanMedium:
            return "medium"
        elif speed == kAirwellFanLow:
            return "min"
        else:
            return "auto"

    ## Set the temperature.
    ## @param[in] degrees The temperature in degrees celsius.
    ## Direct translation from ir_Airwell.cpp lines 223-229
    def setTemp(self, degrees: int) -> None:
        temp = max(kAirwellMinTemp, degrees)
        temp = min(kAirwellMaxTemp, temp)
        self._.Temp = temp - kAirwellMinTemp + 1

    ## Get the current temperature setting.
    ## @return Get current setting for temp. in degrees celsius.
    ## Direct translation from ir_Airwell.cpp lines 231-235
    def getTemp(self) -> int:
        return self._.Temp + kAirwellMinTemp - 1

    ## Convert the current internal state into its stdAc::state_t equivalent.
    ## @param[in] prev Ptr to the previous state if required.
    ## @return The stdAc equivalent of the native settings.
    ## Direct translation from ir_Airwell.cpp lines 237-271
    def toCommon(self, prev: Optional[dict] = None) -> dict:
        """Convert to common A/C state format"""
        result = {}
        # Start with the previous state if given it.
        if prev is not None:
            result = prev.copy()
        else:
            # Set defaults for non-zero values that are not implicitly set for when
            # there is no previous state.
            # e.g. Any setting that toggles should probably go here.
            result["power"] = False

        result["protocol"] = "AIRWELL"
        if self._.PowerToggle:
            result["power"] = not result["power"]
        result["mode"] = self.toCommonMode(self._.Mode)
        result["celsius"] = True
        result["degrees"] = self.getTemp()
        result["fanspeed"] = self.toCommonFanSpeed(self._.Fan)
        # Not supported.
        result["model"] = -1
        result["turbo"] = False
        result["swingv"] = "off"
        result["swingh"] = "off"
        result["light"] = False
        result["filter"] = False
        result["econo"] = False
        result["quiet"] = False
        result["clean"] = False
        result["beep"] = False
        result["sleep"] = -1
        result["clock"] = -1
        return result

    ## Convert the current internal state into a human readable string.
    ## @return A human readable string.
    ## Direct translation from ir_Airwell.cpp lines 273-286
    def toString(self) -> str:
        """Convert current state to human readable string"""
        result = ""
        result += f"PowerToggle: {bool(self._.PowerToggle)}, "
        result += f"Mode: {self.toCommonMode(self._.Mode)}, "
        result += f"Fan: {self.toCommonFanSpeed(self._.Fan)}, "
        result += f"Temp: {self.getTemp()}C"
        return result
