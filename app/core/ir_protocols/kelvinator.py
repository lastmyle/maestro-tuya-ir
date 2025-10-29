# Copyright 2016 David Conran
# Python translation: Direct conversion from C++ with NO optimizations

## @file
## @brief Support for Kelvinator A/C protocols.
## Direct translation from IRremoteESP8266 ir_Kelvinator.cpp and ir_Kelvinator.h

from typing import List

# Ref: ir_Kelvinator.cpp lines 29-48

# Constants - Timing values
kKelvinatorTick = 85
kKelvinatorHdrMarkTicks = 106
kKelvinatorHdrMark = kKelvinatorHdrMarkTicks * kKelvinatorTick
kKelvinatorHdrSpaceTicks = 53
kKelvinatorHdrSpace = kKelvinatorHdrSpaceTicks * kKelvinatorTick
kKelvinatorBitMarkTicks = 8
kKelvinatorBitMark = kKelvinatorBitMarkTicks * kKelvinatorTick
kKelvinatorOneSpaceTicks = 18
kKelvinatorOneSpace = kKelvinatorOneSpaceTicks * kKelvinatorTick
kKelvinatorZeroSpaceTicks = 6
kKelvinatorZeroSpace = kKelvinatorZeroSpaceTicks * kKelvinatorTick
kKelvinatorGapSpaceTicks = 235
kKelvinatorGapSpace = kKelvinatorGapSpaceTicks * kKelvinatorTick

kKelvinatorCmdFooter = 2
kKelvinatorCmdFooterBits = 3

kKelvinatorChecksumStart = 10

# State length constants (from IRremoteESP8266.h)
kKelvinatorStateLength = 16

# Mode constants (from ir_Kelvinator.h lines 93-97)
kKelvinatorAuto = 0
kKelvinatorCool = 1
kKelvinatorDry = 2  # (temp = 25C, but not shown)
kKelvinatorFan = 3
kKelvinatorHeat = 4

# Fan speed constants (from ir_Kelvinator.h lines 98-101)
kKelvinatorBasicFanMax = 3
kKelvinatorFanAuto = 0
kKelvinatorFanMin = 1
kKelvinatorFanMax = 5

# Temperature constants (from ir_Kelvinator.h lines 102-104)
kKelvinatorMinTemp = 16  # 16C
kKelvinatorMaxTemp = 30  # 30C
kKelvinatorAutoTemp = 25  # 25C

# Vertical swing constants (from ir_Kelvinator.h lines 106-115)
kKelvinatorSwingVOff = 0b0000  # 0
kKelvinatorSwingVAuto = 0b0001  # 1
kKelvinatorSwingVHighest = 0b0010  # 2
kKelvinatorSwingVUpperMiddle = 0b0011  # 3
kKelvinatorSwingVMiddle = 0b0100  # 4
kKelvinatorSwingVLowerMiddle = 0b0101  # 5
kKelvinatorSwingVLowest = 0b0110  # 6
kKelvinatorSwingVLowAuto = 0b0111  # 7
kKelvinatorSwingVMiddleAuto = 0b1001  # 9
kKelvinatorSwingVHighAuto = 0b1011  # 11


## Calculate block checksum for Kelvinator protocol
## EXACT translation from IRKelvinatorAC::calcBlockChecksum (ir_Kelvinator.cpp lines 163-173)
def calcBlockChecksum(block: List[int], length: int = 8) -> int:
    """
    Calculate checksum for a block of state.
    EXACT translation from IRremoteESP8266 IRKelvinatorAC::calcBlockChecksum

    Many Bothans died to bring us this information.
    """
    sum_val = kKelvinatorChecksumStart
    # Sum the lower half of the first 4 bytes of this block.
    for i in range(min(4, length - 1)):
        sum_val += block[i] & 0b1111
    # then sum the upper half of the next 3 bytes.
    for i in range(4, length - 1):
        sum_val += block[i] >> 4
    # Trim it down to fit into the 4 bits allowed. i.e. Mod 16.
    return sum_val & 0b1111


## Native representation of a Kelvinator A/C message.
## This is a direct translation of the C++ union/struct (ir_Kelvinator.h lines 36-90)
class KelvinatorProtocol:
    def __init__(self):
        # The state array (16 bytes for Kelvinator)
        self.remote_state = [0] * 16

    # Byte 0
    @property
    def Mode(self) -> int:
        return self.remote_state[0] & 0x07

    @Mode.setter
    def Mode(self, value: int) -> None:
        self.remote_state[0] = (self.remote_state[0] & 0xF8) | (value & 0x07)

    @property
    def Power(self) -> int:
        return (self.remote_state[0] >> 3) & 0x01

    @Power.setter
    def Power(self, value: bool) -> None:
        if value:
            self.remote_state[0] |= 0x08
        else:
            self.remote_state[0] &= 0xF7

    @property
    def BasicFan(self) -> int:
        return (self.remote_state[0] >> 4) & 0x03

    @BasicFan.setter
    def BasicFan(self, value: int) -> None:
        self.remote_state[0] = (self.remote_state[0] & 0xCF) | ((value & 0x03) << 4)

    @property
    def SwingAuto(self) -> int:
        return (self.remote_state[0] >> 6) & 0x01

    @SwingAuto.setter
    def SwingAuto(self, value: bool) -> None:
        if value:
            self.remote_state[0] |= 0x40
        else:
            self.remote_state[0] &= 0xBF

    # Byte 1
    @property
    def Temp(self) -> int:
        return self.remote_state[1] & 0x0F

    @Temp.setter
    def Temp(self, value: int) -> None:
        self.remote_state[1] = (self.remote_state[1] & 0xF0) | (value & 0x0F)

    # Byte 2
    @property
    def Turbo(self) -> int:
        return (self.remote_state[2] >> 4) & 0x01

    @Turbo.setter
    def Turbo(self, value: bool) -> None:
        if value:
            self.remote_state[2] |= 0x10
        else:
            self.remote_state[2] &= 0xEF

    @property
    def Light(self) -> int:
        return (self.remote_state[2] >> 5) & 0x01

    @Light.setter
    def Light(self, value: bool) -> None:
        if value:
            self.remote_state[2] |= 0x20
        else:
            self.remote_state[2] &= 0xDF

    @property
    def IonFilter(self) -> int:
        return (self.remote_state[2] >> 6) & 0x01

    @IonFilter.setter
    def IonFilter(self, value: bool) -> None:
        if value:
            self.remote_state[2] |= 0x40
        else:
            self.remote_state[2] &= 0xBF

    @property
    def XFan(self) -> int:
        return (self.remote_state[2] >> 7) & 0x01

    @XFan.setter
    def XFan(self, value: bool) -> None:
        if value:
            self.remote_state[2] |= 0x80
        else:
            self.remote_state[2] &= 0x7F

    # Byte 4
    @property
    def SwingV(self) -> int:
        return self.remote_state[4] & 0x0F

    @SwingV.setter
    def SwingV(self, value: int) -> None:
        self.remote_state[4] = (self.remote_state[4] & 0xF0) | (value & 0x0F)

    @property
    def SwingH(self) -> int:
        return (self.remote_state[4] >> 4) & 0x01

    @SwingH.setter
    def SwingH(self, value: bool) -> None:
        if value:
            self.remote_state[4] |= 0x10
        else:
            self.remote_state[4] &= 0xEF

    # Byte 7
    @property
    def Sum1(self) -> int:
        return (self.remote_state[7] >> 4) & 0x0F

    @Sum1.setter
    def Sum1(self, value: int) -> None:
        self.remote_state[7] = (self.remote_state[7] & 0x0F) | ((value & 0x0F) << 4)

    # Byte 12
    @property
    def Quiet(self) -> int:
        return (self.remote_state[12] >> 7) & 0x01

    @Quiet.setter
    def Quiet(self, value: bool) -> None:
        if value:
            self.remote_state[12] |= 0x80
        else:
            self.remote_state[12] &= 0x7F

    # Byte 14
    @property
    def Fan(self) -> int:
        return (self.remote_state[14] >> 4) & 0x07

    @Fan.setter
    def Fan(self, value: int) -> None:
        self.remote_state[14] = (self.remote_state[14] & 0x8F) | ((value & 0x07) << 4)

    # Byte 15
    @property
    def Sum2(self) -> int:
        return (self.remote_state[15] >> 4) & 0x0F

    @Sum2.setter
    def Sum2(self, value: int) -> None:
        self.remote_state[15] = (self.remote_state[15] & 0x0F) | ((value & 0x0F) << 4)


## Send a Kelvinator A/C message.
## Status: STABLE / Known working.
## @param[in] data The message to be sent.
## @param[in] nbytes The number of bytes of message to be sent.
## @param[in] repeat The number of times the command is to be repeated.
## Direct translation from IRremoteESP8266 IRsend::sendKelvinator (ir_Kelvinator.cpp lines 64-103)
def sendKelvinator(data: List[int], nbytes: int, repeat: int = 0) -> List[int]:
    """
    Send a Kelvinator A/C formatted message.
    EXACT translation from IRremoteESP8266 IRsend::sendKelvinator

    Returns timing array instead of transmitting via hardware.
    """
    if nbytes < kKelvinatorStateLength:
        return []  # Not enough bytes to send a proper message.

    # Import here to avoid circular import
    from app.core.ir_protocols.ir_send import sendGeneric

    all_timings = []

    for r in range(repeat + 1):
        # Command Block #1 (4 bytes)
        block1_timings = sendGeneric(
            headermark=kKelvinatorHdrMark,
            headerspace=kKelvinatorHdrSpace,
            onemark=kKelvinatorBitMark,
            onespace=kKelvinatorOneSpace,
            zeromark=kKelvinatorBitMark,
            zerospace=kKelvinatorZeroSpace,
            footermark=0,
            gap=0,  # No Footer yet
            dataptr=data[:4],
            nbytes=4,
            frequency=38,
            MSBfirst=False,
            repeat=0,
            dutycycle=50,
        )
        all_timings.extend(block1_timings)

        # Send Footer for the command block (3 bits (b010))
        footer1_timings = sendGeneric(
            headermark=0,
            headerspace=0,  # No Header
            onemark=kKelvinatorBitMark,
            onespace=kKelvinatorOneSpace,
            zeromark=kKelvinatorBitMark,
            zerospace=kKelvinatorZeroSpace,
            footermark=kKelvinatorBitMark,
            gap=kKelvinatorGapSpace,
            dataptr=[kKelvinatorCmdFooter],
            nbytes=0,
            nbits=kKelvinatorCmdFooterBits,
            frequency=38,
            MSBfirst=False,
            repeat=0,
            dutycycle=50,
        )
        all_timings.extend(footer1_timings)

        # Data Block #1 (4 bytes)
        data1_timings = sendGeneric(
            headermark=0,
            headerspace=0,  # No header
            onemark=kKelvinatorBitMark,
            onespace=kKelvinatorOneSpace,
            zeromark=kKelvinatorBitMark,
            zerospace=kKelvinatorZeroSpace,
            footermark=kKelvinatorBitMark,
            gap=kKelvinatorGapSpace * 2,
            dataptr=data[4:8],
            nbytes=4,
            frequency=38,
            MSBfirst=False,
            repeat=0,
            dutycycle=50,
        )
        all_timings.extend(data1_timings)

        # Command Block #2 (4 bytes)
        block2_timings = sendGeneric(
            headermark=kKelvinatorHdrMark,
            headerspace=kKelvinatorHdrSpace,
            onemark=kKelvinatorBitMark,
            onespace=kKelvinatorOneSpace,
            zeromark=kKelvinatorBitMark,
            zerospace=kKelvinatorZeroSpace,
            footermark=0,
            gap=0,  # No Footer yet
            dataptr=data[8:12],
            nbytes=4,
            frequency=38,
            MSBfirst=False,
            repeat=0,
            dutycycle=50,
        )
        all_timings.extend(block2_timings)

        # Send Footer for the command block (3 bits (B010))
        footer2_timings = sendGeneric(
            headermark=0,
            headerspace=0,  # No Header
            onemark=kKelvinatorBitMark,
            onespace=kKelvinatorOneSpace,
            zeromark=kKelvinatorBitMark,
            zerospace=kKelvinatorZeroSpace,
            footermark=kKelvinatorBitMark,
            gap=kKelvinatorGapSpace,
            dataptr=[kKelvinatorCmdFooter],
            nbytes=0,
            nbits=kKelvinatorCmdFooterBits,
            frequency=38,
            MSBfirst=False,
            repeat=0,
            dutycycle=50,
        )
        all_timings.extend(footer2_timings)

        # Data Block #2 (4 bytes)
        data2_timings = sendGeneric(
            headermark=0,
            headerspace=0,  # No header
            onemark=kKelvinatorBitMark,
            onespace=kKelvinatorOneSpace,
            zeromark=kKelvinatorBitMark,
            zerospace=kKelvinatorZeroSpace,
            footermark=kKelvinatorBitMark,
            gap=kKelvinatorGapSpace * 2,
            dataptr=data[12:16],
            nbytes=4,
            frequency=38,
            MSBfirst=False,
            repeat=0,
            dutycycle=50,
        )
        all_timings.extend(data2_timings)

    return all_timings


## Class for handling detailed Kelvinator A/C messages.
## Direct translation from C++ IRKelvinatorAC class
class IRKelvinatorAC:
    ## Class Constructor
    def __init__(self) -> None:
        self._: KelvinatorProtocol = KelvinatorProtocol()
        self.stateReset()

    ## Reset the internal state to a fixed known good state.
    ## Direct translation from ir_Kelvinator.cpp lines 115-119
    def stateReset(self) -> None:
        for i in range(kKelvinatorStateLength):
            self._.remote_state[i] = 0x0
        self._.remote_state[3] = 0x50
        self._.remote_state[11] = 0x70

    ## Fix up any odd conditions for the current state.
    ## Direct translation from ir_Kelvinator.cpp lines 125-134
    def fixup(self) -> None:
        # X-Fan mode is only valid in COOL or DRY modes.
        if self._.Mode != kKelvinatorCool and self._.Mode != kKelvinatorDry:
            self.setXFan(False)
        # Duplicate to the 2nd command chunk.
        self._.remote_state[8] = self._.remote_state[0]
        self._.remote_state[9] = self._.remote_state[1]
        self._.remote_state[10] = self._.remote_state[2]
        self.checksum()  # Calculate the checksums

    ## Calculate the checksum for the internal state.
    ## Direct translation from ir_Kelvinator.cpp lines 176-179
    def checksum(self) -> None:
        self._.Sum1 = calcBlockChecksum(self._.remote_state[:8])
        self._.Sum2 = calcBlockChecksum(self._.remote_state[8:16])

    ## Verify the checksum is valid for a given state.
    ## @param[in] state The array to verify the checksum of.
    ## @param[in] length The size of the state.
    ## @return A boolean indicating if it is valid.
    ## Direct translation from ir_Kelvinator.cpp lines 185-194
    @staticmethod
    def validChecksum(state: List[int], length: int = kKelvinatorStateLength) -> bool:
        for offset in range(0, length, 8):
            if offset + 7 < length:
                # Top 4 bits of the last byte in the block is the block's checksum.
                if ((state[offset + 7] >> 4) & 0x0F) != calcBlockChecksum(
                    state[offset : offset + 8]
                ):
                    return False
        return True

    ## Set the internal state to have the power on.
    ## Direct translation from ir_Kelvinator.cpp line 197
    def on(self) -> None:
        self.setPower(True)

    ## Set the internal state to have the power off.
    ## Direct translation from ir_Kelvinator.cpp line 200
    def off(self) -> None:
        self.setPower(False)

    ## Set the internal state to have the desired power.
    ## @param[in] on The desired power state.
    ## Direct translation from ir_Kelvinator.cpp lines 204-206
    def setPower(self, on: bool) -> None:
        self._.Power = on

    ## Get the power setting from the internal state.
    ## @return A boolean indicating if the power setting.
    ## Direct translation from ir_Kelvinator.cpp lines 210-212
    def getPower(self) -> bool:
        return bool(self._.Power)

    ## Set the temperature setting.
    ## @param[in] degrees The temperature in degrees celsius.
    ## Direct translation from ir_Kelvinator.cpp lines 216-220
    def setTemp(self, degrees: int) -> None:
        temp = max(kKelvinatorMinTemp, degrees)
        temp = min(kKelvinatorMaxTemp, temp)
        self._.Temp = temp - kKelvinatorMinTemp

    ## Get the current temperature setting.
    ## @return Get current setting for temp. in degrees celsius.
    ## Direct translation from ir_Kelvinator.cpp lines 224-226
    def getTemp(self) -> int:
        return self._.Temp + kKelvinatorMinTemp

    ## Set the speed of the fan.
    ## @param[in] speed 0 is auto, 1-5 is the speed
    ## Direct translation from ir_Kelvinator.cpp lines 230-242
    def setFan(self, speed: int) -> None:
        fan = min(kKelvinatorFanMax, speed)  # Bounds check

        # Only change things if we need to.
        if fan != self._.Fan:
            # Set the basic fan values.
            self._.BasicFan = min(kKelvinatorBasicFanMax, fan)
            # Set the advanced(?) fan value.
            self._.Fan = fan
            # Turbo mode is turned off if we change the fan settings.
            self.setTurbo(False)

    ## Get the current fan speed setting.
    ## @return The current fan speed.
    ## Direct translation from ir_Kelvinator.cpp lines 246-248
    def getFan(self) -> int:
        return self._.Fan

    ## Get the current operation mode setting.
    ## @return The current operation mode.
    ## Direct translation from ir_Kelvinator.cpp lines 252-254
    def getMode(self) -> int:
        return self._.Mode

    ## Set the desired operation mode.
    ## @param[in] mode The desired operation mode.
    ## Direct translation from ir_Kelvinator.cpp lines 258-276
    def setMode(self, mode: int) -> None:
        if mode == kKelvinatorAuto or mode == kKelvinatorDry:
            # When the remote is set to Auto or Dry, it defaults to 25C and doesn't show it.
            self.setTemp(kKelvinatorAutoTemp)
            self._.Mode = mode
        elif mode in [kKelvinatorHeat, kKelvinatorCool, kKelvinatorFan]:
            self._.Mode = mode
        else:
            self.setTemp(kKelvinatorAutoTemp)
            self._.Mode = kKelvinatorAuto

    ## Set the Vertical Swing mode of the A/C.
    ## @param[in] automatic Do we use the automatic setting?
    ## @param[in] position The position/mode to set the vanes to.
    ## Direct translation from ir_Kelvinator.cpp lines 281-308
    def setSwingVertical(self, automatic: bool, position: int) -> None:
        self._.SwingAuto = automatic or self._.SwingH
        new_position = position
        if not automatic:
            if position in [
                kKelvinatorSwingVHighest,
                kKelvinatorSwingVUpperMiddle,
                kKelvinatorSwingVMiddle,
                kKelvinatorSwingVLowerMiddle,
                kKelvinatorSwingVLowest,
            ]:
                pass
            else:
                new_position = kKelvinatorSwingVOff
        else:
            if position in [
                kKelvinatorSwingVAuto,
                kKelvinatorSwingVLowAuto,
                kKelvinatorSwingVMiddleAuto,
                kKelvinatorSwingVHighAuto,
            ]:
                pass
            else:
                new_position = kKelvinatorSwingVAuto
        self._.SwingV = new_position

    ## Get the Vertical Swing Automatic mode setting of the A/C.
    ## @return true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Kelvinator.cpp lines 312-314
    def getSwingVerticalAuto(self) -> bool:
        return bool(self._.SwingV & 0b0001)

    ## Get the Vertical Swing position setting of the A/C.
    ## @return The native position/mode.
    ## Direct translation from ir_Kelvinator.cpp lines 318-320
    def getSwingVerticalPosition(self) -> int:
        return self._.SwingV

    ## Control the current horizontal swing setting.
    ## @param[in] on The desired setting.
    ## Direct translation from ir_Kelvinator.cpp lines 324-327
    def setSwingHorizontal(self, on: bool) -> None:
        self._.SwingH = on
        self._.SwingAuto = on or (self._.SwingV & 0b0001)

    ## Is the horizontal swing setting on?
    ## @return The current value.
    ## Direct translation from ir_Kelvinator.cpp lines 331-333
    def getSwingHorizontal(self) -> bool:
        return bool(self._.SwingH)

    ## Control the current Quiet setting.
    ## @param[in] on The desired setting.
    ## Direct translation from ir_Kelvinator.cpp lines 337-339
    def setQuiet(self, on: bool) -> None:
        self._.Quiet = on

    ## Is the Quiet setting on?
    ## @return The current value.
    ## Direct translation from ir_Kelvinator.cpp lines 343-345
    def getQuiet(self) -> bool:
        return bool(self._.Quiet)

    ## Control the current Ion Filter setting.
    ## @param[in] on The desired setting.
    ## Direct translation from ir_Kelvinator.cpp lines 349-351
    def setIonFilter(self, on: bool) -> None:
        self._.IonFilter = on

    ## Is the Ion Filter setting on?
    ## @return The current value.
    ## Direct translation from ir_Kelvinator.cpp lines 355-357
    def getIonFilter(self) -> bool:
        return bool(self._.IonFilter)

    ## Control the current Light setting.
    ## i.e. The LED display on the A/C unit that shows the basic settings.
    ## @param[in] on The desired setting.
    ## Direct translation from ir_Kelvinator.cpp lines 362-364
    def setLight(self, on: bool) -> None:
        self._.Light = on

    ## Is the Light (Display) setting on?
    ## @return The current value.
    ## Direct translation from ir_Kelvinator.cpp lines 368-370
    def getLight(self) -> bool:
        return bool(self._.Light)

    ## Control the current XFan setting.
    ## This setting will cause the unit blow air after power off to dry out the A/C device.
    ## @note XFan mode is only valid in Cool or Dry mode.
    ## @param[in] on The desired setting.
    ## Direct translation from ir_Kelvinator.cpp lines 377-379
    def setXFan(self, on: bool) -> None:
        self._.XFan = on

    ## Is the XFan setting on?
    ## @return The current value.
    ## Direct translation from ir_Kelvinator.cpp lines 383-385
    def getXFan(self) -> bool:
        return bool(self._.XFan)

    ## Control the current Turbo setting.
    ## @note Turbo mode is turned off if the fan speed is changed.
    ## @param[in] on The desired setting.
    ## Direct translation from ir_Kelvinator.cpp lines 390-392
    def setTurbo(self, on: bool) -> None:
        self._.Turbo = on

    ## Is the Turbo setting on?
    ## @return The current value.
    ## Direct translation from ir_Kelvinator.cpp lines 396-398
    def getTurbo(self) -> bool:
        return bool(self._.Turbo)

    ## Get a PTR to the internal state/code for this protocol.
    ## @return PTR to a code for this protocol based on the current internal state.
    ## Direct translation from ir_Kelvinator.cpp lines 147-150
    def getRaw(self) -> List[int]:
        self.fixup()  # Ensure correct settings before sending.
        return self._.remote_state

    ## Set the raw state of the object.
    ## @param[in] new_code The raw state from the native IR message.
    ## Direct translation from ir_Kelvinator.cpp lines 154-156
    def setRaw(self, new_code: List[int]) -> None:
        for i in range(min(len(new_code), kKelvinatorStateLength)):
            self._.remote_state[i] = new_code[i]


## Decode the supplied Kelvinator message.
## Status: STABLE / Known working.
## @param[in,out] results Ptr to the data to decode & where to store the decode result.
## @param[in] offset The starting index to use when attempting to decode the raw data.
## @param[in] nbits The number of data bits to expect.
## @param[in] strict Flag indicating if we should perform strict matching.
## @return A boolean. True if it can decode it, false if it can't.
## Direct translation from IRremoteESP8266 IRrecv::decodeKelvinator (ir_Kelvinator.cpp lines 515-580)
def decodeKelvinator(results, offset: int = 1, nbits: int = 128, strict: bool = True) -> bool:
    """
    Decode a Kelvinator HVAC IR message.
    EXACT translation from IRremoteESP8266 IRrecv::decodeKelvinator

    This is the ACTUAL C++ decoder function, not a wrapper.
    """
    # Import here to avoid circular imports
    from app.core.ir_protocols.ir_recv import (
        kHeader,
        kFooter,
        kMarkExcess,
        matchGeneric,
        matchData,
        match_result_t,
    )

    if (
        results.rawlen
        <= 2 * (nbits + kKelvinatorCmdFooterBits) + (kHeader + kFooter + 1) * 2 - 1 + offset
    ):
        return False  # Can't possibly be a valid Kelvinator message.
    if strict and nbits != 128:
        return False  # Not strictly a Kelvinator message.

    # There are two messages back-to-back in a full Kelvinator IR message sequence.
    pos = 0
    for s in range(2):
        # Header + Data Block #1 (32 bits)
        used = matchGeneric(
            data_ptr=results.rawbuf[offset:],
            result_ptr=results.state[pos:],
            remaining=results.rawlen - offset,
            nbits=32,
            hdrmark=kKelvinatorHdrMark,
            hdrspace=kKelvinatorHdrSpace,
            onemark=kKelvinatorBitMark,
            onespace=kKelvinatorOneSpace,
            zeromark=kKelvinatorBitMark,
            zerospace=kKelvinatorZeroSpace,
            footermark=0,
            footerspace=0,
            atleast=False,
            tolerance=25,
            excess=kMarkExcess,
            MSBfirst=False,
        )
        if used == 0:
            return False
        offset += used
        pos += 4

        # Command data footer (3 bits, B010)
        data_result = matchData(
            data_ptr=results.rawbuf[offset:],
            offset=0,
            nbits=kKelvinatorCmdFooterBits,
            onemark=kKelvinatorBitMark,
            onespace=kKelvinatorOneSpace,
            zeromark=kKelvinatorBitMark,
            zerospace=kKelvinatorZeroSpace,
            tolerance=25,
            excess=kMarkExcess,
            MSBfirst=False,
            expectlastspace=False,
        )
        if data_result.success == False:
            return False
        if data_result.data != kKelvinatorCmdFooter:
            return False
        offset += data_result.used

        # Gap + Data (Options) (32 bits)
        used = matchGeneric(
            data_ptr=results.rawbuf[offset:],
            result_ptr=results.state[pos:],
            remaining=results.rawlen - offset,
            nbits=32,
            hdrmark=kKelvinatorBitMark,
            hdrspace=kKelvinatorGapSpace,
            onemark=kKelvinatorBitMark,
            onespace=kKelvinatorOneSpace,
            zeromark=kKelvinatorBitMark,
            zerospace=kKelvinatorZeroSpace,
            footermark=kKelvinatorBitMark,
            footerspace=kKelvinatorGapSpace * 2,
            atleast=(s > 0),
            tolerance=25,
            excess=kMarkExcess,
            MSBfirst=False,
        )
        if used == 0:
            return False
        offset += used
        pos += 4

    # Compliance
    if strict:
        # Verify the message's checksum is correct.
        if not IRKelvinatorAC.validChecksum(results.state):
            return False

    # Success
    # results.decode_type = KELVINATOR  # Would set protocol type in C++
    results.bits = nbits
    # No need to record the state as we stored it as we decoded it.
    # As we use result->state, we don't record value, address, or command as it
    # is a union data type.
    return True
