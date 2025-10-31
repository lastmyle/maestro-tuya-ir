# Copyright 2018 David Conran
# Copyright bakrus
# Python translation: Direct conversion from C++ with NO optimizations

## @file
## @brief Support for Coolix A/C protocols (COOLIX and COOLIX48).
## Direct translation from IRremoteESP8266 ir_Coolix.cpp and ir_Coolix.h

from typing import List
import copy

# Constants - Timing values (from ir_Coolix.cpp lines 22-35)
kCoolixTick = 276  # Approximately 10.5 cycles at 38kHz
kCoolixBitMarkTicks = 2
kCoolixBitMark = kCoolixBitMarkTicks * kCoolixTick  # 552us
kCoolixOneSpaceTicks = 6
kCoolixOneSpace = kCoolixOneSpaceTicks * kCoolixTick  # 1656us
kCoolixZeroSpaceTicks = 2
kCoolixZeroSpace = kCoolixZeroSpaceTicks * kCoolixTick  # 552us
kCoolixHdrMarkTicks = 17
kCoolixHdrMark = kCoolixHdrMarkTicks * kCoolixTick  # 4692us
kCoolixHdrSpaceTicks = 16
kCoolixHdrSpace = kCoolixHdrSpaceTicks * kCoolixTick  # 4416us
kCoolixMinGapTicks = kCoolixHdrMarkTicks + kCoolixZeroSpaceTicks
kCoolixMinGap = kCoolixMinGapTicks * kCoolixTick  # 5244us
kCoolixExtraTolerance = 5  # Percent

# State length constants
kCoolixBits = 24
kCoolix48Bits = 48
kCoolixDefaultRepeat = 1

# Mode constants (from ir_Coolix.h lines 46-50)
kCoolixCool = 0b000
kCoolixDry = 0b001
kCoolixAuto = 0b010
kCoolixHeat = 0b011
kCoolixFan = 0b100  # Synthetic

# Fan speed constants (from ir_Coolix.h lines 54-60)
kCoolixFanMin = 0b100
kCoolixFanMed = 0b010
kCoolixFanMax = 0b001
kCoolixFanAuto = 0b101
kCoolixFanAuto0 = 0b000
kCoolixFanZoneFollow = 0b110
kCoolixFanFixed = 0b111

# Temperature constants (from ir_Coolix.h lines 62-82)
kCoolixTempMin = 17  # Celsius
kCoolixTempMax = 30  # Celsius
kCoolixTempRange = kCoolixTempMax - kCoolixTempMin + 1
kCoolixFanTempCode = 0b1110  # Part of Fan Mode
kCoolixTempMap = [
    0b0000,  # 17C
    0b0001,  # 18c
    0b0011,  # 19C
    0b0010,  # 20C
    0b0110,  # 21C
    0b0111,  # 22C
    0b0101,  # 23C
    0b0100,  # 24C
    0b1100,  # 25C
    0b1101,  # 26C
    0b1001,  # 27C
    0b1000,  # 28C
    0b1010,  # 29C
    0b1011,  # 30C
]

kCoolixSensorTempMax = 30  # Celsius
kCoolixSensorTempIgnoreCode = 0b11111  # 0x1F / 31 (DEC)

# Fixed states/messages (from ir_Coolix.h lines 86-96)
kCoolixOff = 0xB27BE0
kCoolixSwing = 0xB26BE0
kCoolixSwingH = 0xB5F5A2
kCoolixSwingV = 0xB20FE0
kCoolixSleep = 0xB2E003
kCoolixTurbo = 0xB5F5A2
kCoolixLed = 0xB5F5A5
kCoolixClean = 0xB5F5AA
kCoolixCmdFan = 0xB2BFE4
# On, 25C, Mode: Auto, Fan: Auto, Zone Follow: Off, Sensor Temp: Ignore
kCoolixDefaultState = 0xB21FC8


## Native representation of a Coolix A/C message.
## Direct translation of the C++ union/struct (ir_Coolix.h lines 99-115)
class CoolixProtocol:
    def __init__(self):
        # The state in IR code form (32-bit, only 24 bits used)
        self.raw = 0

    # Byte 0 - ZoneFollow1 (bit 1)
    @property
    def ZoneFollow1(self) -> int:
        return (self.raw >> 1) & 0x01

    @ZoneFollow1.setter
    def ZoneFollow1(self, value: bool) -> None:
        if value:
            self.raw |= 1 << 1
        else:
            self.raw &= ~(1 << 1)

    # Byte 0 - Mode (bits 2-3)
    @property
    def Mode(self) -> int:
        return (self.raw >> 2) & 0x03

    @Mode.setter
    def Mode(self, value: int) -> None:
        self.raw = (self.raw & ~(0x03 << 2)) | ((value & 0x03) << 2)

    # Byte 0 - Temp (bits 4-7)
    @property
    def Temp(self) -> int:
        return (self.raw >> 4) & 0x0F

    @Temp.setter
    def Temp(self, value: int) -> None:
        self.raw = (self.raw & ~(0x0F << 4)) | ((value & 0x0F) << 4)

    # Byte 1 - SensorTemp (bits 8-12)
    @property
    def SensorTemp(self) -> int:
        return (self.raw >> 8) & 0x1F

    @SensorTemp.setter
    def SensorTemp(self, value: int) -> None:
        self.raw = (self.raw & ~(0x1F << 8)) | ((value & 0x1F) << 8)

    # Byte 1 - Fan (bits 13-15)
    @property
    def Fan(self) -> int:
        return (self.raw >> 13) & 0x07

    @Fan.setter
    def Fan(self, value: int) -> None:
        self.raw = (self.raw & ~(0x07 << 13)) | ((value & 0x07) << 13)

    # Byte 2 - ZoneFollow2 (bit 19)
    @property
    def ZoneFollow2(self) -> int:
        return (self.raw >> 19) & 0x01

    @ZoneFollow2.setter
    def ZoneFollow2(self, value: bool) -> None:
        if value:
            self.raw |= 1 << 19
        else:
            self.raw &= ~(1 << 19)


## Send a Coolix 24-bit message
## Status: STABLE / Confirmed Working.
## Direct translation from IRremoteESP8266 IRsend::sendCOOLIX (ir_Coolix.cpp lines 50-80)
def sendCOOLIX(data: int, nbits: int = kCoolixBits, repeat: int = 0) -> List[int]:
    """
    Send a Coolix formatted message.
    EXACT translation from IRremoteESP8266 IRsend::sendCOOLIX

    Returns timing array instead of transmitting via hardware.
    """
    if nbits % 8 != 0:
        return []  # nbits is required to be a multiple of 8

    from app.core.ir_protocols.ir_send import sendData

    all_timings = []

    for r in range(repeat + 1):
        # Header
        all_timings.append(kCoolixHdrMark)
        all_timings.append(kCoolixHdrSpace)

        # Data - Break data into byte segments, starting at the Most Significant
        # Byte. Each byte then being sent normal, then followed inverted.
        for i in range(8, nbits + 1, 8):
            # Grab a bytes worth of data
            segment = (data >> (nbits - i)) & 0xFF
            # Normal
            normal_timings = sendData(
                onemark=kCoolixBitMark,
                onespace=kCoolixOneSpace,
                zeromark=kCoolixBitMark,
                zerospace=kCoolixZeroSpace,
                data=segment,
                nbits=8,
                MSBfirst=True,
            )
            all_timings.extend(normal_timings)
            # Inverted
            inverted_timings = sendData(
                onemark=kCoolixBitMark,
                onespace=kCoolixOneSpace,
                zeromark=kCoolixBitMark,
                zerospace=kCoolixZeroSpace,
                data=segment ^ 0xFF,
                nbits=8,
                MSBfirst=True,
            )
            all_timings.extend(inverted_timings)

        # Footer
        all_timings.append(kCoolixBitMark)
        all_timings.append(kCoolixMinGap)

    return all_timings


## Class for handling detailed Coolix A/C messages.
## Direct translation from C++ IRCoolixAC class (ir_Coolix.h lines 121-199)
class IRCoolixAC:
    ## Class Constructor
    def __init__(self) -> None:
        self._: CoolixProtocol = CoolixProtocol()
        self._saved: CoolixProtocol = CoolixProtocol()
        # Internal State settings
        self.powerFlag = False
        self.turboFlag = False
        self.ledFlag = False
        self.cleanFlag = False
        self.sleepFlag = False
        self.swingFlag = False
        self.savedFan = kCoolixFanAuto
        self.stateReset()

    ## Reset the internal state to a fixed known good state.
    ## Direct translation from ir_Coolix.cpp lines 92-102
    def stateReset(self) -> None:
        self.setRaw(kCoolixDefaultState)
        self.savedFan = self.getFan()
        self.clearSensorTemp()
        self.powerFlag = False
        self.turboFlag = False
        self.ledFlag = False
        self.cleanFlag = False
        self.sleepFlag = False
        self.swingFlag = False

    ## Get a copy of the internal state as a valid code for this protocol.
    ## Direct translation from ir_Coolix.cpp line 125
    def getRaw(self) -> int:
        return self._.raw

    ## Set the internal state from a valid code for this protocol.
    ## Direct translation from ir_Coolix.cpp lines 129-141
    def setRaw(self, new_code: int) -> None:
        self.powerFlag = True  # Everything that is not the special power off mesg is On
        if not self.handleSpecialState(new_code):
            # it isn`t special so might affect Temp|mode|Fan
            if new_code == kCoolixCmdFan:
                self.setMode(kCoolixFan)
                return
        # must be a command changing Temp|Mode|Fan
        # it is safe to just copy to remote var
        self._.raw = new_code

    ## Is the current state is a special state?
    ## Direct translation from ir_Coolix.cpp lines 145-155
    def isSpecialState(self) -> bool:
        return self._.raw in [
            kCoolixClean,
            kCoolixLed,
            kCoolixOff,
            kCoolixSwing,
            kCoolixSwingV,
            kCoolixSleep,
            kCoolixTurbo,
        ]

    ## Adjust any internal settings based on the type of special state.
    ## Direct translation from ir_Coolix.cpp lines 165-189
    def handleSpecialState(self, data: int) -> bool:
        if data == kCoolixClean:
            self.cleanFlag = not self.cleanFlag
        elif data == kCoolixLed:
            self.ledFlag = not self.ledFlag
        elif data == kCoolixOff:
            self.powerFlag = False
        elif data == kCoolixSwing:
            self.swingFlag = not self.swingFlag
        elif data == kCoolixSleep:
            self.sleepFlag = not self.sleepFlag
        elif data == kCoolixTurbo:
            self.turboFlag = not self.turboFlag
        else:
            return False
        return True

    ## Backup the current internal state.
    ## Direct translation from ir_Coolix.cpp lines 196-199
    def updateAndSaveState(self, raw_state: int) -> None:
        if not self.isSpecialState():
            self._saved.raw = self._.raw
        self._.raw = raw_state

    ## Restore the current internal state from backup.
    ## Direct translation from ir_Coolix.cpp lines 203-209
    def recoverSavedState(self) -> None:
        # If the current state is a special one, use last known normal one
        if self.isSpecialState():
            self._.raw = self._saved.raw
        # If the saved state was also a special state, reset
        if self.isSpecialState():
            self.stateReset()

    ## Set the raw (native) temperature value.
    ## Direct translation from ir_Coolix.cpp line 214
    def setTempRaw(self, code: int) -> None:
        self._.Temp = code

    ## Get the raw (native) temperature value.
    ## Direct translation from ir_Coolix.cpp line 218
    def getTempRaw(self) -> int:
        return self._.Temp

    ## Set the temperature.
    ## Direct translation from ir_Coolix.cpp lines 222-227
    def setTemp(self, desired: int) -> None:
        # Range check
        temp = min(desired, kCoolixTempMax)
        temp = max(temp, kCoolixTempMin)
        self.setTempRaw(kCoolixTempMap[temp - kCoolixTempMin])

    ## Get the current temperature setting.
    ## Direct translation from ir_Coolix.cpp lines 231-236
    def getTemp(self) -> int:
        code = self.getTempRaw()
        for i in range(kCoolixTempRange):
            if kCoolixTempMap[i] == code:
                return kCoolixTempMin + i
        return kCoolixTempMax  # Not a temp we expected

    ## Set the raw (native) sensor temperature value.
    ## Direct translation from ir_Coolix.cpp line 241
    def setSensorTempRaw(self, code: int) -> None:
        self._.SensorTemp = code

    ## Set the sensor temperature.
    ## Direct translation from ir_Coolix.cpp lines 247-250
    def setSensorTemp(self, temp: int) -> None:
        self.setSensorTempRaw(min(temp, kCoolixSensorTempMax))
        self.setZoneFollow(True)  # Setting a Sensor temp means you want to Zone Follow

    ## Get the sensor temperature setting.
    ## Direct translation from ir_Coolix.cpp line 254
    def getSensorTemp(self) -> int:
        return self._.SensorTemp

    ## Get the value of the current power setting.
    ## Direct translation from ir_Coolix.cpp line 259
    def getPower(self) -> bool:
        return self.powerFlag

    ## Change the power setting.
    ## Direct translation from ir_Coolix.cpp lines 263-271
    def setPower(self, on: bool) -> None:
        if not on:
            self.updateAndSaveState(kCoolixOff)
        elif not self.powerFlag:
            # at this point state must be ready to be transmitted
            self.recoverSavedState()
        self.powerFlag = on

    ## Change the power setting to On.
    ## Direct translation from ir_Coolix.cpp line 274
    def on(self) -> None:
        self.setPower(True)

    ## Change the power setting to Off.
    ## Direct translation from ir_Coolix.cpp line 277
    def off(self) -> None:
        self.setPower(False)

    ## Get the Swing setting of the A/C.
    ## Direct translation from ir_Coolix.cpp line 281
    def getSwing(self) -> bool:
        return self.swingFlag

    ## Toggle the Swing mode of the A/C.
    ## Direct translation from ir_Coolix.cpp lines 284-288
    def setSwing(self) -> None:
        # Assumes that repeated sending "swing" toggles the action on the device
        self.updateAndSaveState(kCoolixSwing)
        self.swingFlag = not self.swingFlag

    ## Get the Vertical Swing Step setting of the A/C.
    ## Direct translation from ir_Coolix.cpp line 292
    def getSwingVStep(self) -> bool:
        return self._.raw == kCoolixSwingV

    ## Set the Vertical Swing Step setting of the A/C.
    ## Direct translation from ir_Coolix.cpp lines 295-297
    def setSwingVStep(self) -> None:
        self.updateAndSaveState(kCoolixSwingV)

    ## Get the Sleep setting of the A/C.
    ## Direct translation from ir_Coolix.cpp line 301
    def getSleep(self) -> bool:
        return self.sleepFlag

    ## Toggle the Sleep mode of the A/C.
    ## Direct translation from ir_Coolix.cpp lines 304-307
    def setSleep(self) -> None:
        self.updateAndSaveState(kCoolixSleep)
        self.sleepFlag = not self.sleepFlag

    ## Get the Turbo setting of the A/C.
    ## Direct translation from ir_Coolix.cpp line 311
    def getTurbo(self) -> bool:
        return self.turboFlag

    ## Toggle the Turbo mode of the A/C.
    ## Direct translation from ir_Coolix.cpp lines 314-318
    def setTurbo(self) -> None:
        # Assumes that repeated sending "turbo" toggles the action on the device
        self.updateAndSaveState(kCoolixTurbo)
        self.turboFlag = not self.turboFlag

    ## Get the Led (light) setting of the A/C.
    ## Direct translation from ir_Coolix.cpp line 322
    def getLed(self) -> bool:
        return self.ledFlag

    ## Toggle the Led (light) mode of the A/C.
    ## Direct translation from ir_Coolix.cpp lines 325-329
    def setLed(self) -> None:
        # Assumes that repeated sending "Led" toggles the action on the device
        self.updateAndSaveState(kCoolixLed)
        self.ledFlag = not self.ledFlag

    ## Get the Clean setting of the A/C.
    ## Direct translation from ir_Coolix.cpp line 333
    def getClean(self) -> bool:
        return self.cleanFlag

    ## Toggle the Clean mode of the A/C.
    ## Direct translation from ir_Coolix.cpp lines 336-339
    def setClean(self) -> None:
        self.updateAndSaveState(kCoolixClean)
        self.cleanFlag = not self.cleanFlag

    ## Get the Zone Follow setting of the A/C.
    ## Direct translation from ir_Coolix.cpp lines 343-345
    def getZoneFollow(self) -> bool:
        return bool(self._.ZoneFollow1) and bool(self._.ZoneFollow2)

    ## Change the Zone Follow setting.
    ## Direct translation from ir_Coolix.cpp lines 350-354
    def setZoneFollow(self, on: bool) -> None:
        self._.ZoneFollow1 = on
        self._.ZoneFollow2 = on
        self.setFan(kCoolixFanZoneFollow if on else self.savedFan)

    ## Clear the Sensor Temperature setting.
    ## Direct translation from ir_Coolix.cpp lines 357-360
    def clearSensorTemp(self) -> None:
        self.setZoneFollow(False)
        self.setSensorTempRaw(kCoolixSensorTempIgnoreCode)

    ## Set the operating mode of the A/C.
    ## Direct translation from ir_Coolix.cpp lines 364-388
    def setMode(self, mode: int) -> None:
        actualmode = mode
        if mode in [kCoolixAuto, kCoolixDry]:
            self.setFan(kCoolixFanAuto0, False)
        elif mode in [kCoolixCool, kCoolixHeat, kCoolixFan]:
            self.setFan(kCoolixFanAuto, False)
        else:  # Anything else, go with Auto mode
            self.setMode(kCoolixAuto)
            self.setFan(kCoolixFanAuto0, False)
            return
        self.setTemp(self.getTemp())
        # Fan mode is a special case of Dry
        if mode == kCoolixFan:
            actualmode = kCoolixDry
            self.setTempRaw(kCoolixFanTempCode)
        self._.Mode = actualmode

    ## Get the operating mode setting of the A/C.
    ## Direct translation from ir_Coolix.cpp lines 392-397
    def getMode(self) -> int:
        mode = self._.Mode
        if mode == kCoolixDry:
            if self.getTempRaw() == kCoolixFanTempCode:
                return kCoolixFan
        return mode

    ## Get the current fan speed setting.
    ## Direct translation from ir_Coolix.cpp line 401
    def getFan(self) -> int:
        return self._.Fan

    ## Set the speed of the fan.
    ## Direct translation from ir_Coolix.cpp lines 406-441
    def setFan(self, speed: int, modecheck: bool = True) -> None:
        newspeed = speed
        if speed == kCoolixFanAuto:  # Dry & Auto mode can't have this speed
            if modecheck:
                if self.getMode() in [kCoolixAuto, kCoolixDry]:
                    newspeed = kCoolixFanAuto0
        elif speed == kCoolixFanAuto0:  # Only Dry & Auto mode can have this speed
            if modecheck:
                if self.getMode() not in [kCoolixAuto, kCoolixDry]:
                    newspeed = kCoolixFanAuto
        elif speed in [
            kCoolixFanMin,
            kCoolixFanMed,
            kCoolixFanMax,
            kCoolixFanZoneFollow,
            kCoolixFanFixed,
        ]:
            pass
        else:  # Unknown speed requested
            newspeed = kCoolixFanAuto
        # Keep a copy of the last non-ZoneFollow fan setting
        self.savedFan = self.savedFan if (self._.Fan == kCoolixFanZoneFollow) else self._.Fan
        self._.Fan = newspeed


def GETBITS64(data: int, offset: int, nbits: int) -> int:
    """Extract bits from uint64. EXACT translation from IRutils."""
    mask = (1 << nbits) - 1
    return (data >> offset) & mask


## Decode the supplied Coolix 24-bit A/C message.
## Status: STABLE / Known Working.
## Direct translation from IRremoteESP8266 IRrecv::decodeCOOLIX (ir_Coolix.cpp lines 638-704)
def decodeCOOLIX(
    results, offset: int = 1, nbits: int = kCoolixBits, strict: bool = True, _tolerance: int = 25
) -> bool:
    """
    Decode a Coolix IR message.
    EXACT translation from IRremoteESP8266 IRrecv::decodeCOOLIX
    """
    from app.core.ir_protocols.ir_recv import (
        kHeader,
        kFooter,
        kMarkExcess,
        matchMark,
        matchSpace,
        matchAtLeast,
        _matchGeneric,
    )

    # The protocol sends the data normal + inverted, alternating on
    # each byte. Hence twice the number of expected data bits.
    if results.rawlen < 2 * 2 * nbits + kHeader + kFooter - 1 + offset:
        return False  # Can't possibly be a valid COOLIX message
    if strict and nbits != kCoolixBits:
        return False  # Not strictly a COOLIX message
    if nbits % 8 != 0:  # nbits has to be a multiple of nr. of bits in a byte
        return False

    data = 0
    inverted = 0

    if nbits > 64:
        return False  # We can't possibly capture a Coolix packet that big

    # Header
    if not matchMark(results.rawbuf[offset], kCoolixHdrMark, _tolerance + kCoolixExtraTolerance):
        return False
    offset += 1
    if not matchSpace(results.rawbuf[offset], kCoolixHdrSpace, _tolerance + kCoolixExtraTolerance):
        return False
    offset += 1

    # Data - Twice as many bits as there are normal plus inverted bits
    for i in range(0, nbits * 2, 8):
        flip = ((i // 8) % 2) != 0
        result = 0
        # Read the next byte of data
        used = _matchGeneric(
            data_ptr=results.rawbuf[offset:],
            result_bits_ptr=[result],
            result_bytes_ptr=None,
            use_bits=True,
            remaining=results.rawlen - offset,
            nbits=8,
            hdrmark=0,
            hdrspace=0,  # No Header
            onemark=kCoolixBitMark,
            onespace=kCoolixOneSpace,
            zeromark=kCoolixBitMark,
            zerospace=kCoolixZeroSpace,
            footermark=0,
            footerspace=0,  # No Footer
            atleast=False,
            tolerance=_tolerance + kCoolixExtraTolerance,
            excess=0,
            MSBfirst=True,
        )
        if used == 0:
            return False  # Didn't match a bytes worth of data
        offset += used
        result = result if isinstance(result, int) else 0
        if flip:  # The inverted byte
            inverted <<= 8
            inverted |= result
        else:
            data <<= 8
            data |= result

    # Footer
    if not matchMark(results.rawbuf[offset], kCoolixBitMark, _tolerance + kCoolixExtraTolerance):
        return False
    offset += 1
    if offset < results.rawlen:
        if not matchAtLeast(
            results.rawbuf[offset], kCoolixMinGap, _tolerance + kCoolixExtraTolerance
        ):
            return False

    # Compliance
    orig = data  # Save a copy of the data
    if strict:
        for i in range(0, nbits, 8):
            if (data & 0xFF) != ((inverted & 0xFF) ^ 0xFF):
                return False
            data >>= 8
            inverted >>= 8

    # Success
    results.bits = nbits
    results.value = orig
    results.address = 0
    results.command = 0
    return True


## Send a Coolix 48-bit message.
## Status: ALPHA / Untested.
## Direct translation from IRremoteESP8266 IRsend::sendCoolix48 (ir_Coolix.cpp lines 716-724)
def sendCoolix48(data: int, nbits: int = kCoolix48Bits, repeat: int = 0) -> List[int]:
    """
    Send a Coolix48 formatted message.
    EXACT translation from IRremoteESP8266 IRsend::sendCoolix48

    Returns timing array instead of transmitting via hardware.
    """
    from app.core.ir_protocols.ir_send import sendGeneric

    return sendGeneric(
        headermark=kCoolixHdrMark,
        headerspace=kCoolixHdrSpace,
        onemark=kCoolixBitMark,
        onespace=kCoolixOneSpace,
        zeromark=kCoolixBitMark,
        zerospace=kCoolixZeroSpace,
        footermark=kCoolixBitMark,
        gap=kCoolixMinGap,
        dataptr=data
        if isinstance(data, list)
        else [(data >> i) & 0xFF for i in range(0, nbits, 8)][::-1],
        nbytes=nbits // 8,
        MSBfirst=True,
    )


## Decode the supplied Coolix 48-bit A/C message.
## Status: BETA / Probably Working.
## Direct translation from IRremoteESP8266 IRrecv::decodeCoolix48 (ir_Coolix.cpp lines 738-759)
def decodeCoolix48(
    results, offset: int = 1, nbits: int = kCoolix48Bits, strict: bool = True, _tolerance: int = 25
) -> bool:
    """
    Decode a Coolix48 IR message.
    EXACT translation from IRremoteESP8266 IRrecv::decodeCoolix48
    """
    from app.core.ir_protocols.ir_recv import kMarkExcess, _matchGeneric

    if strict and nbits != kCoolix48Bits:
        return False  # Not strictly a COOLIX48 message

    # Header + Data + Footer
    used = _matchGeneric(
        data_ptr=results.rawbuf[offset:],
        result_bits_ptr=[results.value] if hasattr(results, "value") else None,
        result_bytes_ptr=None,
        use_bits=True,
        remaining=results.rawlen - offset,
        nbits=nbits,
        hdrmark=kCoolixHdrMark,
        hdrspace=kCoolixHdrSpace,
        onemark=kCoolixBitMark,
        onespace=kCoolixOneSpace,
        zeromark=kCoolixBitMark,
        zerospace=kCoolixZeroSpace,
        footermark=kCoolixBitMark,
        footerspace=kCoolixMinGap,
        atleast=True,
        tolerance=_tolerance + kCoolixExtraTolerance,
        excess=0,
        MSBfirst=True,
    )
    if used == 0:
        return False

    # Success
    results.bits = nbits
    results.address = 0
    results.command = 0
    return True
