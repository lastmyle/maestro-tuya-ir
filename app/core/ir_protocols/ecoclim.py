# Copyright 2021 David Conran
# Python translation: Direct conversion from C++ with NO optimizations

## @file
## @brief EcoClim A/C protocol.
## @see https://github.com/crankyoldgit/IRremoteESP8266/issues/1397
## Direct translation from IRremoteESP8266 ir_Ecoclim.cpp and ir_Ecoclim.h

from typing import List

# Supports:
#   Brand: EcoClim,  Model: HYSFR-P348 remote
#   Brand: EcoClim,  Model: ZC200DPO A/C

# Constants (from ir_Ecoclim.cpp lines 17-25)
kEcoclimSections = 3
kEcoclimExtraTolerance = 5  # Percentage (extra)
kEcoclimHdrMark = 5730  # uSeconds
kEcoclimHdrSpace = 1935  # uSeconds
kEcoclimBitMark = 440  # uSeconds
kEcoclimOneSpace = 1739  # uSeconds
kEcoclimZeroSpace = 637  # uSeconds
kEcoclimFooterMark = 7820  # uSeconds
kEcoclimGap = 100000  # kDefaultMessageGap - Just a guess.

# State length constants (from IRremoteESP8266.h lines 1240-1241)
kEcoclimBits = 56
kEcoclimShortBits = 15

# Modes (from ir_Ecoclim.h lines 27-33)
kEcoclimAuto = 0b000  # 0. a.k.a Slave
kEcoclimCool = 0b001  # 1
kEcoclimDry = 0b010  # 2
kEcoclimRecycle = 0b011  # 3
kEcoclimFan = 0b100  # 4
kEcoclimHeat = 0b101  # 5
kEcoclimSleep = 0b111  # 7

# Fan Control (from ir_Ecoclim.h lines 35-38)
kEcoclimFanMin = 0b00  # 0
kEcoclimFanMed = 0b01  # 1
kEcoclimFanMax = 0b10  # 2
kEcoclimFanAuto = 0b11  # 3

# DIP settings (from ir_Ecoclim.h lines 40-41)
kEcoclimDipMaster = 0b0000
kEcoclimDipSlave = 0b0111

# Temperature (from ir_Ecoclim.h lines 43-44)
kEcoclimTempMin = 5  # Celsius
kEcoclimTempMax = kEcoclimTempMin + 31  # Celsius (36)

# Timer (from ir_Ecoclim.h line 46)
kEcoclimTimerDisable = 0x1F * 60 + 7 * 10  # 4774

# Power: Off, Mode: Auto, Temp: 11C, Sensor: 22C, Fan: Auto, Clock: 00:00
# (from ir_Ecoclim.h line 49)
kEcoclimDefaultState = 0x11063000FFFF02


## Native representation of a Ecoclim A/C message.
## Direct translation of C++ union/struct (from ir_Ecoclim.h lines 51-78)
class EcoclimProtocol:
    def __init__(self):
        self.raw = kEcoclimDefaultState  # uint64_t

    # Byte 0
    # :3 bits - Fixed 0b010
    # :1 bit - Unknown
    @property
    def DipConfig(self) -> int:
        return (self.raw >> 4) & 0x0F

    @DipConfig.setter
    def DipConfig(self, value: int) -> None:
        self.raw = (self.raw & ~(0x0F << 4)) | ((value & 0x0F) << 4)

    # Byte 1
    @property
    def OffTenMins(self) -> int:
        return (self.raw >> 8) & 0x07

    @OffTenMins.setter
    def OffTenMins(self, value: int) -> None:
        self.raw = (self.raw & ~(0x07 << 8)) | ((value & 0x07) << 8)

    @property
    def OffHours(self) -> int:
        return (self.raw >> 11) & 0x1F

    @OffHours.setter
    def OffHours(self, value: int) -> None:
        self.raw = (self.raw & ~(0x1F << 11)) | ((value & 0x1F) << 11)

    # Byte 2
    @property
    def OnTenMins(self) -> int:
        return (self.raw >> 16) & 0x07

    @OnTenMins.setter
    def OnTenMins(self, value: int) -> None:
        self.raw = (self.raw & ~(0x07 << 16)) | ((value & 0x07) << 16)

    @property
    def OnHours(self) -> int:
        return (self.raw >> 19) & 0x1F

    @OnHours.setter
    def OnHours(self, value: int) -> None:
        self.raw = (self.raw & ~(0x1F << 19)) | ((value & 0x1F) << 19)

    # Byte 3+4
    @property
    def Clock(self) -> int:
        return (self.raw >> 24) & 0x7FF

    @Clock.setter
    def Clock(self, value: int) -> None:
        self.raw = (self.raw & ~(0x7FF << 24)) | ((value & 0x7FF) << 24)

    # :1 bit - Unknown (bit 35)

    @property
    def Fan(self) -> int:
        return (self.raw >> 36) & 0x03

    @Fan.setter
    def Fan(self, value: int) -> None:
        self.raw = (self.raw & ~(0x03 << 36)) | ((value & 0x03) << 36)

    @property
    def Power(self) -> int:
        return (self.raw >> 38) & 0x01

    @Power.setter
    def Power(self, value: bool) -> None:
        if value:
            self.raw |= 1 << 38
        else:
            self.raw &= ~(1 << 38)

    @property
    def Clear(self) -> int:
        return (self.raw >> 39) & 0x01

    @Clear.setter
    def Clear(self, value: bool) -> None:
        if value:
            self.raw |= 1 << 39
        else:
            self.raw &= ~(1 << 39)

    # Byte 5
    @property
    def Temp(self) -> int:
        return (self.raw >> 40) & 0x1F

    @Temp.setter
    def Temp(self, value: int) -> None:
        self.raw = (self.raw & ~(0x1F << 40)) | ((value & 0x1F) << 40)

    @property
    def Mode(self) -> int:
        return (self.raw >> 45) & 0x07

    @Mode.setter
    def Mode(self, value: int) -> None:
        self.raw = (self.raw & ~(0x07 << 45)) | ((value & 0x07) << 45)

    # Byte 6
    @property
    def SensorTemp(self) -> int:
        return (self.raw >> 48) & 0x1F

    @SensorTemp.setter
    def SensorTemp(self, value: int) -> None:
        self.raw = (self.raw & ~(0x1F << 48)) | ((value & 0x1F) << 48)

    # :3 bits - Fixed (bits 53-55)


## Send a EcoClim A/C formatted message.
## Status: STABLE / Confirmed working on real device.
## @param[in] data The message to be sent (uint64).
## @param[in] nbits The number of bits of message to be sent.
## @param[in] repeat The number of times the command is to be repeated.
## Direct translation from IRremoteESP8266 IRsend::sendEcoclim (ir_Ecoclim.cpp lines 36-55)
def sendEcoclim(data: int, nbits: int, repeat: int = 0) -> List[int]:
    """
    Send a EcoClim A/C formatted message.
    EXACT translation from IRremoteESP8266 IRsend::sendEcoclim

    Returns timing array instead of transmitting via hardware.
    """
    # Import here to avoid circular import
    from app.core.ir_protocols.ir_send import sendGeneric

    all_timings = []

    for r in range(repeat + 1):
        for section in range(kEcoclimSections):
            # Header + Data
            section_timings = sendGeneric(
                headermark=kEcoclimHdrMark,
                headerspace=kEcoclimHdrSpace,
                onemark=kEcoclimBitMark,
                onespace=kEcoclimOneSpace,
                zeromark=kEcoclimBitMark,
                zerospace=kEcoclimZeroSpace,
                footermark=0,
                gap=0,
                dataptr=data,
                nbytes=0,  # Using nbits instead
                nbits=nbits,
                frequency=38,
                MSBfirst=True,
                repeat=0,
                dutycycle=50,
            )
            all_timings.extend(section_timings)

        # Footer
        all_timings.append(kEcoclimFooterMark)
        all_timings.append(kEcoclimGap)

    return all_timings


## Decode the supplied EcoClim A/C message.
## Status: STABLE / Confirmed working on real remote.
## @param[in,out] results Ptr to the data to decode & where to store the decode result.
## @param[in] offset The starting index to use when attempting to decode the raw data.
## @param[in] nbits The number of data bits to expect.
## @param[in] strict Flag indicating if we should perform strict matching.
## Direct translation from IRremoteESP8266 IRrecv::decodeEcoclim (ir_Ecoclim.cpp lines 58-119)
def decodeEcoclim(results, offset: int = 1, nbits: int = kEcoclimBits, strict: bool = True) -> bool:
    """
    Decode a Ecoclim A/C IR message.
    EXACT translation from IRremoteESP8266 IRrecv::decodeEcoclim

    This is the ACTUAL C++ decoder function, not a wrapper.
    """
    # Import here to avoid circular imports
    from app.core.ir_protocols.ir_recv import kHeader, kFooter, kMarkExcess, _matchGeneric

    if results.rawlen < (2 * nbits + kHeader) * kEcoclimSections + kFooter - 1 + offset:
        return False  # Can't possibly be a valid Ecoclim message.

    if strict:
        if nbits not in [kEcoclimShortBits, kEcoclimBits]:
            return False  # Unexpected bit size.

    for section in range(kEcoclimSections):
        # Header + Data Block
        used = _matchGeneric(
            data_ptr=results.rawbuf[offset:],
            result_bits_ptr=None,
            result_bytes_ptr=results.state if section == 0 else None,
            use_bits=True,
            remaining=results.rawlen - offset,
            nbits=nbits,
            hdrmark=kEcoclimHdrMark,
            hdrspace=kEcoclimHdrSpace,
            onemark=kEcoclimBitMark,
            onespace=kEcoclimOneSpace,
            zeromark=kEcoclimBitMark,
            zerospace=kEcoclimZeroSpace,
            footermark=0,
            footerspace=0,
            atleast=False,
            tolerance=25 + kEcoclimExtraTolerance,
            excess=kMarkExcess,
            MSBfirst=True,
        )
        if used == 0:
            return False
        offset += used

        # Compliance - Each section should contain the same data.
        if strict and section > 0:
            # Compare with first section data
            if results.value != results.state:
                return False
        elif section == 0:
            results.value = results.state

    # Footer
    from app.core.ir_protocols.ir_recv import matchMark, matchAtLeast

    if not matchMark(results.rawbuf[offset], kEcoclimFooterMark, 25 + kEcoclimExtraTolerance):
        offset += 1
        return False
    offset += 1
    if results.rawlen <= offset and not matchAtLeast(results.rawbuf[offset], kEcoclimGap):
        return False

    # Success
    results.bits = nbits
    # results.decode_type = ECOCLIM  # Would set protocol type in C++
    # No need to record the value as we stored it as we decoded it.
    return True


## Class for handling detailed EcoClim A/C 56 bit messages.
## @see https://github.com/crankyoldgit/IRremoteESP8266/issues/1397
## Direct translation from C++ IREcoclimAc class
class IREcoclimAc:
    ## Class Constructor
    ## @param[in] pin GPIO to be used when sending.
    ## @param[in] inverted Is the output signal to be inverted?
    ## @param[in] use_modulation Is frequency modulation to be used?
    ## Direct translation from ir_Ecoclim.cpp lines 122-128
    def __init__(self, pin: int = 0, inverted: bool = False, use_modulation: bool = True) -> None:
        self._: EcoclimProtocol = EcoclimProtocol()
        # _irsend not needed for Python implementation
        self.stateReset()

    ## Reset the internal state to a fixed known good state.
    ## Direct translation from ir_Ecoclim.cpp line 131
    def stateReset(self) -> None:
        self._.raw = kEcoclimDefaultState

    ## Get a copy of the internal state as a valid code for this protocol.
    ## @return A valid code for this protocol based on the current internal state.
    ## Direct translation from ir_Ecoclim.cpp line 146
    def getRaw(self) -> int:
        return self._.raw

    ## Set the internal state from a valid code for this protocol.
    ## @param[in] new_code A valid code for this protocol.
    ## Direct translation from ir_Ecoclim.cpp line 150
    def setRaw(self, new_code: int) -> None:
        self._.raw = new_code

    ## Set the temperature.
    ## @param[in] celsius The temperature in degrees celsius.
    ## Direct translation from ir_Ecoclim.cpp lines 153-159
    def setTemp(self, celsius: int) -> None:
        # Range check.
        temp = min(celsius, kEcoclimTempMax)
        temp = max(temp, kEcoclimTempMin)
        self._.Temp = temp - kEcoclimTempMin

    ## Get the current temperature setting.
    ## @return The current setting for temp. in degrees celsius.
    ## Direct translation from ir_Ecoclim.cpp line 163
    def getTemp(self) -> int:
        return self._.Temp + kEcoclimTempMin

    ## Set the sensor temperature.
    ## @param[in] celsius The temperature in degrees celsius.
    ## Direct translation from ir_Ecoclim.cpp lines 166-172
    def setSensorTemp(self, celsius: int) -> None:
        # Range check.
        temp = min(celsius, kEcoclimTempMax)
        temp = max(temp, kEcoclimTempMin)
        self._.SensorTemp = temp - kEcoclimTempMin

    ## Get the sensor temperature setting.
    ## @return The current setting for sensor temp. in degrees celsius.
    ## Direct translation from ir_Ecoclim.cpp lines 176-178
    def getSensorTemp(self) -> int:
        return self._.SensorTemp + kEcoclimTempMin

    ## Get the value of the current power setting.
    ## @return true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Ecoclim.cpp line 182
    def getPower(self) -> bool:
        return bool(self._.Power)

    ## Change the power setting.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Ecoclim.cpp line 186
    def setPower(self, on: bool) -> None:
        self._.Power = on

    ## Change the power setting to On.
    ## Direct translation from ir_Ecoclim.cpp line 189
    def on(self) -> None:
        self.setPower(True)

    ## Change the power setting to Off.
    ## Direct translation from ir_Ecoclim.cpp line 192
    def off(self) -> None:
        self.setPower(False)

    ## Get the current fan speed setting.
    ## @return The current fan speed.
    ## Direct translation from ir_Ecoclim.cpp line 196
    def getFan(self) -> int:
        return self._.Fan

    ## Set the speed of the fan.
    ## @param[in] speed The desired setting.
    ## Direct translation from ir_Ecoclim.cpp lines 200-202
    def setFan(self, speed: int) -> None:
        self._.Fan = min(speed, kEcoclimFanAuto)

    ## Convert a stdAc::fanspeed_t enum into it's native speed.
    ## @param[in] speed The enum to be converted.
    ## @return The native equivalent of the enum.
    ## Direct translation from ir_Ecoclim.cpp lines 207-216
    @staticmethod
    def convertFan(speed: int) -> int:
        # Note: Using int instead of stdAc::fanspeed_t enum
        # kMin=0, kLow=1, kMedium=2, kHigh=3, kMax=4
        if speed in [0, 1]:  # kMin, kLow
            return kEcoclimFanMin
        elif speed == 2:  # kMedium
            return kEcoclimFanMed
        elif speed in [3, 4]:  # kHigh, kMax
            return kEcoclimFanMax
        else:
            return kEcoclimFanAuto  # Note: Line 214 has typo kCoolixFanAuto

    ## Convert a native fan speed into its stdAc equivalent.
    ## @param[in] speed The native setting to be converted.
    ## @return The stdAc equivalent of the native setting.
    ## Direct translation from ir_Ecoclim.cpp lines 221-228
    @staticmethod
    def toCommonFanSpeed(speed: int) -> int:
        # Returns int instead of stdAc::fanspeed_t enum
        if speed == kEcoclimFanMax:
            return 4  # stdAc::fanspeed_t::kMax
        elif speed == kEcoclimFanMed:
            return 2  # stdAc::fanspeed_t::kMedium
        elif speed == kEcoclimFanMin:
            return 0  # stdAc::fanspeed_t::kMin
        else:
            return 5  # stdAc::fanspeed_t::kAuto

    ## Get the operating mode setting of the A/C.
    ## @return The current operating mode setting.
    ## Direct translation from ir_Ecoclim.cpp line 232
    def getMode(self) -> int:
        return self._.Mode

    ## Set the operating mode of the A/C.
    ## @param[in] mode The desired operating mode.
    ## Direct translation from ir_Ecoclim.cpp lines 236-250
    def setMode(self, mode: int) -> None:
        if mode in [
            kEcoclimAuto,
            kEcoclimCool,
            kEcoclimDry,
            kEcoclimRecycle,
            kEcoclimFan,
            kEcoclimHeat,
            kEcoclimSleep,
        ]:
            self._.Mode = mode
        else:
            # Anything else, go with Auto mode.
            self.setMode(kEcoclimAuto)

    ## Convert a standard A/C mode into its native mode.
    ## @param[in] mode A stdAc::opmode_t to be converted to it's native equivalent.
    ## @return The corresponding native mode.
    ## Direct translation from ir_Ecoclim.cpp lines 255-263
    @staticmethod
    def convertMode(mode: int) -> int:
        # Note: Using int instead of stdAc::opmode_t enum
        # kCool=1, kHeat=2, kDry=3, kFan=4, kAuto=0
        if mode == 1:  # kCool
            return kEcoclimCool
        elif mode == 2:  # kHeat
            return kEcoclimHeat
        elif mode == 3:  # kDry
            return kEcoclimDry
        elif mode == 4:  # kFan
            return kEcoclimFan
        else:
            return kEcoclimAuto

    ## Convert a native mode to it's common stdAc::opmode_t equivalent.
    ## @param[in] mode A native operation mode to be converted.
    ## @return The corresponding common stdAc::opmode_t mode.
    ## Direct translation from ir_Ecoclim.cpp lines 268-276
    @staticmethod
    def toCommonMode(mode: int) -> int:
        # Returns int instead of stdAc::opmode_t enum
        if mode == kEcoclimCool:
            return 1  # stdAc::opmode_t::kCool
        elif mode == kEcoclimHeat:
            return 2  # stdAc::opmode_t::kHeat
        elif mode == kEcoclimDry:
            return 3  # stdAc::opmode_t::kDry
        elif mode == kEcoclimFan:
            return 4  # stdAc::opmode_t::kFan
        else:
            return 0  # stdAc::opmode_t::kAuto

    ## Get the clock time of the A/C unit.
    ## @return Nr. of minutes past midnight.
    ## Direct translation from ir_Ecoclim.cpp line 280
    def getClock(self) -> int:
        return self._.Clock

    ## Set the clock time on the A/C unit.
    ## @param[in] nr_of_mins Nr. of minutes past midnight.
    ## Direct translation from ir_Ecoclim.cpp lines 284-286
    def setClock(self, nr_of_mins: int) -> None:
        self._.Clock = min(nr_of_mins, 24 * 60 - 1)

    ## Get the Unit type/DIP switch settings of the remote.
    ## @return The binary representation of the 4 DIP switches on the remote.
    ## Direct translation from ir_Ecoclim.cpp line 290
    def getType(self) -> int:
        return self._.DipConfig

    ## Set the Unit type/DIP switch settings for the remote.
    ## @param[in] code The binary representation of the remote's 4 DIP switches.
    ## Direct translation from ir_Ecoclim.cpp lines 294-303
    def setType(self, code: int) -> None:
        if code in [kEcoclimDipMaster, kEcoclimDipSlave]:
            self._.DipConfig = code
        else:
            self.setType(kEcoclimDipMaster)

    ## Set & enable the On Timer for the A/C.
    ## @param[in] nr_of_mins The time, in minutes since midnight.
    ## Direct translation from ir_Ecoclim.cpp lines 307-312
    def setOnTimer(self, nr_of_mins: int) -> None:
        if nr_of_mins < 24 * 60:
            self._.OnHours = nr_of_mins // 60
            self._.OnTenMins = (nr_of_mins % 60) // 10  # Store in tens of mins resolution.

    ## Get the On Timer for the A/C.
    ## @return The On Time, in minutes since midnight.
    ## Direct translation from ir_Ecoclim.cpp lines 316-318
    def getOnTimer(self) -> int:
        return self._.OnHours * 60 + self._.OnTenMins * 10

    ## Check if the On Timer is enabled.
    ## @return true, if the timer is enabled, otherwise false.
    ## Direct translation from ir_Ecoclim.cpp lines 322-324
    def isOnTimerEnabled(self) -> bool:
        return self.getOnTimer() != kEcoclimTimerDisable

    ## Disable & clear the On Timer.
    ## Direct translation from ir_Ecoclim.cpp lines 327-330
    def disableOnTimer(self) -> None:
        self._.OnHours = 0x1F
        self._.OnTenMins = 0x7

    ## Set & enable the Off Timer for the A/C.
    ## @param[in] nr_of_mins The time, in minutes since midnight.
    ## Direct translation from ir_Ecoclim.cpp lines 334-339
    def setOffTimer(self, nr_of_mins: int) -> None:
        if nr_of_mins < 24 * 60:
            self._.OffHours = nr_of_mins // 60
            self._.OffTenMins = (nr_of_mins % 60) // 10  # Store in tens of mins resolution.

    ## Get the Off Timer for the A/C.
    ## @return The Off Time, in minutes since midnight.
    ## Direct translation from ir_Ecoclim.cpp lines 343-345
    def getOffTimer(self) -> int:
        return self._.OffHours * 60 + self._.OffTenMins * 10

    ## Check if the Off Timer is enabled.
    ## @return true, if the timer is enabled, otherwise false.
    ## Direct translation from ir_Ecoclim.cpp lines 349-351
    def isOffTimerEnabled(self) -> bool:
        return self.getOffTimer() != kEcoclimTimerDisable

    ## Disable & clear the Off Timer.
    ## Direct translation from ir_Ecoclim.cpp lines 354-357
    def disableOffTimer(self) -> None:
        self._.OffHours = 0x1F
        self._.OffTenMins = 0x7
