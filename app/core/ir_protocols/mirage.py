# Copyright 2020-2021 David Conran (crankyoldgit)
# Python translation: Direct conversion from C++ with NO optimizations

## @file
## @brief Support for Mirage protocol
## @see https://github.com/crankyoldgit/IRremoteESP8266/issues/1289
## @see https://github.com/crankyoldgit/IRremoteESP8266/issues/1573
## Direct translation from IRremoteESP8266 ir_Mirage.cpp and ir_Mirage.h

from typing import List

# Supports:
#   Brand: Mirage,  Model: VLU series A/C
#   Brand: Maxell,  Model: MX-CH18CF A/C
#   Brand: Maxell,  Model: KKG9A-C1 remote
#   Brand: Tronitechnik,  Model: Reykir 9000 A/C
#   Brand: Tronitechnik,  Model: KKG29A-C1 remote

# Constants - Timing values (from ir_Mirage.cpp lines 35-41)
kMirageHdrMark = 8360  # uSeconds
kMirageBitMark = 554  # uSeconds
kMirageHdrSpace = 4248  # uSeconds
kMirageOneSpace = 1592  # uSeconds
kMirageZeroSpace = 545  # uSeconds
kMirageGap = 20000  # kDefaultMessageGap uSeconds (just a guess)
kMirageFreq = 38000  # Hz. (Just a guess)

# State length constants (from IRremoteESP8266.h)
kMirageStateLength = 15
kMirageBits = kMirageStateLength * 8  # 120 bits
kMirageMinRepeat = 0  # kNoRepeat

# Power constants (from ir_Mirage.cpp lines 43-44)
kMirageAcKKG29AC1PowerOn = 0b00  # 0
kMirageAcKKG29AC1PowerOff = 0b11  # 3

# Mode constants (from ir_Mirage.h lines 162-166)
kMirageAcHeat = 0b001  # 1
kMirageAcCool = 0b010  # 2
kMirageAcDry = 0b011  # 3
kMirageAcRecycle = 0b100  # 4
kMirageAcFan = 0b101  # 5

# Fan speed constants (from ir_Mirage.h lines 168-176)
kMirageAcFanAuto = 0b00  # 0
kMirageAcFanHigh = 0b01  # 1
kMirageAcFanMed = 0b10  # 2
kMirageAcFanLow = 0b11  # 3
kMirageAcKKG29AC1FanAuto = 0b00  # 0
kMirageAcKKG29AC1FanHigh = 0b01  # 1
kMirageAcKKG29AC1FanLow = 0b10  # 2
kMirageAcKKG29AC1FanMed = 0b11  # 3

# Temperature constants (from ir_Mirage.h lines 178-182)
kMirageAcMinTemp = 16  # 16C
kMirageAcMaxTemp = 32  # 32C
kMirageAcTempOffset = 0x5C
kMirageAcSensorTempOffset = 20
kMirageAcSensorTempMax = 43  # Celsius

# Power and swing constants (from ir_Mirage.h lines 184-191)
kMirageAcPowerOff = 0x5F
kMirageAcSwingVOff = 0b0000  # 0
kMirageAcSwingVLowest = 0b0011  # 3
kMirageAcSwingVLow = 0b0101  # 5
kMirageAcSwingVMiddle = 0b0111  # 7
kMirageAcSwingVHigh = 0b1001  # 9
kMirageAcSwingVHighest = 0b1011  # 11
kMirageAcSwingVAuto = 0b1101  # 13

# Model enums
MIRAGE_KKG9AC1 = 0
MIRAGE_KKG29AC1 = 1

# Temperature value constant
kNoTempValue = 255


## Helper function for sumNibbles (array version)
## EXACT translation from IRremoteESP8266 IRutils.cpp sumNibbles
def sumNibbles_array(data: List[int], length: int, init: int = 0) -> int:
    """
    Sum all the nibbles together in an array.
    EXACT translation from IRremoteESP8266 IRutils.cpp sumNibbles
    """
    sum_val = init
    for i in range(length):
        sum_val += (data[i] >> 4) + (data[i] & 0xF)
    return sum_val & 0xFF


## Helper function for bcdToUint8
## EXACT translation from IRremoteESP8266 IRutils.cpp bcdToUint8
def bcdToUint8(bcd: int) -> int:
    """
    Convert a BCD value to a regular integer.
    EXACT translation from IRremoteESP8266 IRutils.cpp bcdToUint8
    """
    if bcd > 0x99:
        return 255  # Too big.
    return (bcd >> 4) * 10 + (bcd & 0xF)


## Helper function for uint8ToBcd
## EXACT translation from IRremoteESP8266 IRutils.cpp uint8ToBcd
def uint8ToBcd(integer: int) -> int:
    """
    Convert an Integer into a byte of Binary Coded Decimal(BCD).
    EXACT translation from IRremoteESP8266 IRutils.cpp uint8ToBcd
    """
    if integer > 99:
        return 255  # Too big.
    return ((integer // 10) << 4) + (integer % 10)


## Helper function for fahrenheitToCelsius
def fahrenheitToCelsius(temp: float) -> float:
    """Convert Fahrenheit to Celsius"""
    return (temp - 32.0) / 1.8


## Native representation of a Mirage 120-bit A/C message.
## This is a direct translation of the C++ union/struct
## @see https://docs.google.com/spreadsheets/d/1Ucu9mOOIIJoWQjUJq_VCvwgV3EwKaRk8K2AuZgccYEk/edit#gid=0
class Mirage120Protocol:
    def __init__(self):
        # The state array (15 bytes for Mirage)
        self.raw = [0] * kMirageStateLength

    # Common fields (from ir_Mirage.h lines 34-65)
    # Byte 0
    @property
    def Header(self) -> int:
        return self.raw[0]

    @Header.setter
    def Header(self, value: int) -> None:
        self.raw[0] = value & 0xFF

    # Byte 1
    @property
    def Temp(self) -> int:
        return self.raw[1]

    @Temp.setter
    def Temp(self, value: int) -> None:
        self.raw[1] = value & 0xFF

    # Byte 4
    @property
    def Fan(self) -> int:
        return self.raw[4] & 0x03

    @Fan.setter
    def Fan(self, value: int) -> None:
        self.raw[4] = (self.raw[4] & 0xFC) | (value & 0x03)

    @property
    def Mode(self) -> int:
        return (self.raw[4] >> 4) & 0x0F

    @Mode.setter
    def Mode(self, value: int) -> None:
        self.raw[4] = (self.raw[4] & 0x0F) | ((value & 0x0F) << 4)

    # Byte 14
    @property
    def Sum(self) -> int:
        return self.raw[14]

    @Sum.setter
    def Sum(self, value: int) -> None:
        self.raw[14] = value & 0xFF

    # KKG9AC1 remote fields (from ir_Mirage.h lines 67-103)
    # Byte 3
    @property
    def Light_Kkg9ac1(self) -> int:
        return (self.raw[3] >> 3) & 0x01

    @Light_Kkg9ac1.setter
    def Light_Kkg9ac1(self, value: bool) -> None:
        if value:
            self.raw[3] |= 0x08
        else:
            self.raw[3] &= 0xF7

    # Byte 5
    @property
    def SwingAndPower(self) -> int:
        return (self.raw[5] >> 1) & 0x7F

    @SwingAndPower.setter
    def SwingAndPower(self, value: int) -> None:
        self.raw[5] = (self.raw[5] & 0x01) | ((value & 0x7F) << 1)

    # Byte 6
    @property
    def Sleep_Kkg9ac1(self) -> int:
        return (self.raw[6] >> 7) & 0x01

    @Sleep_Kkg9ac1.setter
    def Sleep_Kkg9ac1(self, value: bool) -> None:
        if value:
            self.raw[6] |= 0x80
        else:
            self.raw[6] &= 0x7F

    # Byte 7
    @property
    def Turbo_Kkg9ac1(self) -> int:
        return (self.raw[7] >> 3) & 0x01

    @Turbo_Kkg9ac1.setter
    def Turbo_Kkg9ac1(self, value: bool) -> None:
        if value:
            self.raw[7] |= 0x08
        else:
            self.raw[7] &= 0xF7

    # Byte 11
    @property
    def Seconds(self) -> int:
        return self.raw[11]

    @Seconds.setter
    def Seconds(self, value: int) -> None:
        self.raw[11] = value & 0xFF

    # Byte 12
    @property
    def Minutes(self) -> int:
        return self.raw[12]

    @Minutes.setter
    def Minutes(self, value: int) -> None:
        self.raw[12] = value & 0xFF

    # Byte 13
    @property
    def Hours(self) -> int:
        return self.raw[13]

    @Hours.setter
    def Hours(self, value: int) -> None:
        self.raw[13] = value & 0xFF

    # KKG29A-C1 remote fields (from ir_Mirage.h lines 105-158)
    # Byte 3
    @property
    def Quiet(self) -> int:
        return self.raw[3] & 0x01

    @Quiet.setter
    def Quiet(self, value: bool) -> None:
        if value:
            self.raw[3] |= 0x01
        else:
            self.raw[3] &= 0xFE

    # Byte 4
    @property
    def OffTimerEnable(self) -> int:
        return (self.raw[4] >> 2) & 0x01

    @OffTimerEnable.setter
    def OffTimerEnable(self, value: bool) -> None:
        if value:
            self.raw[4] |= 0x04
        else:
            self.raw[4] &= 0xFB

    @property
    def OnTimerEnable(self) -> int:
        return (self.raw[4] >> 3) & 0x01

    @OnTimerEnable.setter
    def OnTimerEnable(self, value: bool) -> None:
        if value:
            self.raw[4] |= 0x08
        else:
            self.raw[4] &= 0xF7

    # Byte 5
    @property
    def SwingH(self) -> int:
        return self.raw[5] & 0x01

    @SwingH.setter
    def SwingH(self, value: bool) -> None:
        if value:
            self.raw[5] |= 0x01
        else:
            self.raw[5] &= 0xFE

    @property
    def SwingV(self) -> int:
        return (self.raw[5] >> 1) & 0x01

    @SwingV.setter
    def SwingV(self, value: bool) -> None:
        if value:
            self.raw[5] |= 0x02
        else:
            self.raw[5] &= 0xFD

    @property
    def LightToggle_Kkg29ac1(self) -> int:
        return (self.raw[5] >> 2) & 0x01

    @LightToggle_Kkg29ac1.setter
    def LightToggle_Kkg29ac1(self, value: bool) -> None:
        if value:
            self.raw[5] |= 0x04
        else:
            self.raw[5] &= 0xFB

    @property
    def Power(self) -> int:
        return (self.raw[5] >> 6) & 0x03

    @Power.setter
    def Power(self, value: int) -> None:
        self.raw[5] = (self.raw[5] & 0x3F) | ((value & 0x03) << 6)

    # Byte 6
    @property
    def Filter(self) -> int:
        return (self.raw[6] >> 1) & 0x01

    @Filter.setter
    def Filter(self, value: bool) -> None:
        if value:
            self.raw[6] |= 0x02
        else:
            self.raw[6] &= 0xFD

    @property
    def Sleep_Kkg29ac1(self) -> int:
        return (self.raw[6] >> 3) & 0x01

    @Sleep_Kkg29ac1.setter
    def Sleep_Kkg29ac1(self, value: bool) -> None:
        if value:
            self.raw[6] |= 0x08
        else:
            self.raw[6] &= 0xF7

    @property
    def RecycleHeat(self) -> int:
        return (self.raw[6] >> 6) & 0x01

    @RecycleHeat.setter
    def RecycleHeat(self, value: bool) -> None:
        if value:
            self.raw[6] |= 0x40
        else:
            self.raw[6] &= 0xBF

    # Byte 7
    @property
    def SensorTemp(self) -> int:
        return self.raw[7] & 0x3F

    @SensorTemp.setter
    def SensorTemp(self, value: int) -> None:
        self.raw[7] = (self.raw[7] & 0xC0) | (value & 0x3F)

    @property
    def CleanToggle(self) -> int:
        return (self.raw[7] >> 6) & 0x01

    @CleanToggle.setter
    def CleanToggle(self, value: bool) -> None:
        if value:
            self.raw[7] |= 0x40
        else:
            self.raw[7] &= 0xBF

    @property
    def IFeel(self) -> int:
        return (self.raw[7] >> 7) & 0x01

    @IFeel.setter
    def IFeel(self, value: bool) -> None:
        if value:
            self.raw[7] |= 0x80
        else:
            self.raw[7] &= 0x7F

    # Byte 8
    @property
    def OnTimerHours(self) -> int:
        return self.raw[8] & 0x1F

    @OnTimerHours.setter
    def OnTimerHours(self, value: int) -> None:
        self.raw[8] = (self.raw[8] & 0xE0) | (value & 0x1F)

    @property
    def Turbo_Kkg29ac1(self) -> int:
        return (self.raw[8] >> 7) & 0x01

    @Turbo_Kkg29ac1.setter
    def Turbo_Kkg29ac1(self, value: bool) -> None:
        if value:
            self.raw[8] |= 0x80
        else:
            self.raw[8] &= 0x7F

    # Byte 9
    @property
    def OnTimerMins(self) -> int:
        return self.raw[9] & 0x3F

    @OnTimerMins.setter
    def OnTimerMins(self, value: int) -> None:
        self.raw[9] = (self.raw[9] & 0xC0) | (value & 0x3F)

    # Byte 10
    @property
    def OffTimerHours(self) -> int:
        return self.raw[10] & 0x1F

    @OffTimerHours.setter
    def OffTimerHours(self, value: int) -> None:
        self.raw[10] = (self.raw[10] & 0xE0) | (value & 0x1F)

    # Byte 11
    @property
    def OffTimerMins(self) -> int:
        return self.raw[11] & 0x3F

    @OffTimerMins.setter
    def OffTimerMins(self, value: int) -> None:
        self.raw[11] = (self.raw[11] & 0xC0) | (value & 0x3F)


## Send a Mirage formatted message.
## Status: STABLE / Reported as working.
## @param[in] data An array of bytes containing the IR command.
## @param[in] nbytes Nr. of bytes of data in the array. (>=kMirageStateLength)
## @param[in] repeat Nr. of times the message is to be repeated.
## Direct translation from IRremoteESP8266 IRsend::sendMirage (ir_Mirage.cpp lines 47-62)
def sendMirage(
    data: List[int], nbytes: int = kMirageStateLength, repeat: int = kMirageMinRepeat
) -> List[int]:
    """
    Send a Mirage formatted message.
    EXACT translation from IRremoteESP8266 IRsend::sendMirage

    Returns timing array instead of transmitting via hardware.
    """
    # Import here to avoid circular import
    from app.core.ir_protocols.ir_send import sendGeneric

    return sendGeneric(
        headermark=kMirageHdrMark,
        headerspace=kMirageHdrSpace,
        onemark=kMirageBitMark,
        onespace=kMirageOneSpace,
        zeromark=kMirageBitMark,
        zerospace=kMirageZeroSpace,
        footermark=kMirageBitMark,
        dataptr=data,
        nbytes=nbytes,
        MSBfirst=False,
    )


## Decode the supplied Mirage message.
## Status: STABLE / Reported as working.
## @param[in,out] results Ptr to the data to decode & where to store the decode
## @param[in] offset The starting index to use when attempting to decode the
##   raw data. Typically/Defaults to kStartOffset.
## @param[in] nbits The number of data bits to expect.
## @param[in] strict Flag indicating if we should perform strict matching.
## @return A boolean. True if it can decode it, false if it can't.
## Direct translation from IRremoteESP8266 IRrecv::decodeMirage (ir_Mirage.cpp lines 64-94)
def decodeMirage(results, offset: int = 1, nbits: int = kMirageBits, strict: bool = True) -> bool:
    """
    Decode a Mirage HVAC IR message.
    EXACT translation from IRremoteESP8266 IRrecv::decodeMirage

    This is the ACTUAL C++ decoder function, not a wrapper.
    """
    # Import here to avoid circular imports
    from app.core.ir_protocols.ir_recv import matchGeneric

    if strict and nbits != kMirageBits:
        return False  # Compliance.

    if not matchGeneric(
        data_ptr=results.rawbuf[offset:],
        result_ptr=results.state,
        remaining=results.rawlen - offset,
        nbits=nbits,
        hdrmark=kMirageHdrMark,
        hdrspace=kMirageHdrSpace,
        onemark=kMirageBitMark,
        onespace=kMirageOneSpace,
        zeromark=kMirageBitMark,
        zerospace=kMirageZeroSpace,
        footermark=kMirageBitMark,
        footerspace=kMirageGap,
        atleast=True,
        tolerance=25,  # kUseDefTol
        excess=50,  # kMarkExcess
        MSBfirst=False,
    ):
        return False

    # Compliance
    if strict and not IRMirageAc.validChecksum(results.state):
        return False

    # Success
    results.decode_type = "MIRAGE"
    results.bits = nbits
    # No need to record the state as we stored it as we decoded it.
    # As we use result->state, we don't record value, address, or command as it
    # is a union data type.
    return True


## Class for handling detailed Mirage A/C messages.
## Direct translation from C++ IRMirageAc class
## @note Inspired and derived from the work done at: https://github.com/r45635/HVAC-IR-Control
## @warning Consider this very alpha code. Seems to work, but not validated.
class IRMirageAc:
    ## Class constructor
    ## @param[in] pin GPIO to be used when sending.
    ## @param[in] inverted Is the output signal to be inverted?
    ## @param[in] use_modulation Is frequency modulation to be used?
    ## Direct translation from ir_Mirage.cpp lines 98-104
    def __init__(self) -> None:
        self._: Mirage120Protocol = Mirage120Protocol()
        self._model: int = MIRAGE_KKG9AC1
        self.stateReset()

    ## Reset the state of the remote to a known good state/sequence.
    ## Direct translation from ir_Mirage.cpp lines 106-114
    def stateReset(self) -> None:
        # The state of the IR remote in IR code form.
        kReset = [
            0x56,
            0x6C,
            0x00,
            0x00,
            0x20,
            0x1A,
            0x00,
            0x00,
            0x0C,
            0x00,
            0x0C,
            0x00,
            0x00,
            0x00,
            0x42,
        ]
        self.setRaw(kReset)
        self._model = MIRAGE_KKG9AC1

    ## Get a PTR to the internal state/code for this protocol.
    ## @return PTR to a code for this protocol based on the current internal state.
    ## Direct translation from ir_Mirage.cpp lines 136-141
    def getRaw(self) -> List[int]:
        self.checksum()
        return self._.raw

    ## Set the internal state from a valid code for this protocol.
    ## @param[in] data A valid code for this protocol.
    ## Direct translation from ir_Mirage.cpp lines 143-148
    def setRaw(self, data: List[int]) -> None:
        for i in range(min(len(data), kMirageStateLength)):
            self._.raw[i] = data[i]
        self._model = self.getModel(True)

    ## Guess the Mirage remote model from the supplied state code.
    ## @param[in] state A valid state code for this protocol.
    ## @return The model code.
    ## @note This result isn't perfect. Both protocols can look the same but have
    ##       wildly different settings.
    ## Direct translation from ir_Mirage.cpp lines 150-172
    @staticmethod
    def getModel_static(state: List[int]) -> int:
        p = Mirage120Protocol()
        for i in range(min(len(state), kMirageStateLength)):
            p.raw[i] = state[i]
        # Check for KKG29AC1 specific settings.
        if (
            p.RecycleHeat
            or p.Filter
            or p.Sleep_Kkg29ac1
            or p.CleanToggle
            or p.IFeel
            or p.OffTimerEnable
            or p.OnTimerEnable
        ):
            return MIRAGE_KKG29AC1
        # Check for things specific to KKG9AC1
        if (
            (p.Minutes or p.Seconds)
            or (p.OffTimerHours or p.OffTimerMins)
            or (p.OnTimerHours or p.OnTimerMins)
        ):
            return MIRAGE_KKG9AC1
        # As the above test has a 1 in 3600+ (for 1 second an hour) chance of a false
        # negative in theory, we are going assume that anything left should be a
        # KKG29AC1 model.
        return MIRAGE_KKG29AC1  # Default.

    ## Get the model code of the interal message state.
    ## @param[in] useRaw If set, we try to get the model info from just the state.
    ## @return The model code.
    ## Direct translation from ir_Mirage.cpp lines 174-179
    def getModel(self, useRaw: bool = False) -> int:
        return IRMirageAc.getModel_static(self._.raw) if useRaw else self._model

    ## Set the model code of the interal message state.
    ## @param[in] model The desired model to use for the settings.
    ## Direct translation from ir_Mirage.cpp lines 181-200
    def setModel(self, model: int) -> None:
        if model != self._model:  # Only change things if we need to.
            # Save the old settings.
            state = self.toCommon()
            ontimer = self.getOnTimer()
            offtimer = self.getOffTimer()
            ifeel = self.getIFeel()
            sensor = self.getSensorTemp()
            # Change the model.
            state["model"] = model
            # Restore/Convert the settings.
            self.fromCommon(state)
            self.setOnTimer(ontimer)
            self.setOffTimer(offtimer)
            self.setIFeel(ifeel)
            self.setSensorTemp(sensor)

    ## Calculate and set the checksum values for the internal state.
    ## Direct translation from ir_Mirage.cpp line 203
    def checksum(self) -> None:
        self._.Sum = IRMirageAc.calculateChecksum(self._.raw)

    ## Verify the checksum is valid for a given state.
    ## @param[in] data The array to verify the checksum of.
    ## @return true, if the state has a valid checksum. Otherwise, false.
    ## Direct translation from ir_Mirage.cpp lines 205-210
    @staticmethod
    def validChecksum(data: List[int]) -> bool:
        return IRMirageAc.calculateChecksum(data) == data[kMirageStateLength - 1]

    ## Calculate the checksum for a given state.
    ## @param[in] data The value to calc the checksum of.
    ## @return The calculated checksum value.
    ## Direct translation from ir_Mirage.cpp lines 212-217
    @staticmethod
    def calculateChecksum(data: List[int]) -> int:
        return sumNibbles_array(data, kMirageStateLength - 1)

    ## Set the requested power state of the A/C to on.
    ## Direct translation from ir_Mirage.cpp line 220
    def on(self) -> None:
        self.setPower(True)

    ## Set the requested power state of the A/C to off.
    ## Direct translation from ir_Mirage.cpp line 223
    def off(self) -> None:
        self.setPower(False)

    ## Change the power setting.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Mirage.cpp lines 225-249
    def setPower(self, on: bool) -> None:
        if self._model == MIRAGE_KKG29AC1:
            self._.Power = kMirageAcKKG29AC1PowerOn if on else kMirageAcKKG29AC1PowerOff
        else:
            # In order to change the power setting, it seems must be less than
            # kMirageAcPowerOff. kMirageAcPowerOff is larger than half of the
            # possible value stored in the allocated bit space.
            # Thus if the value is larger than kMirageAcPowerOff the power is off.
            # Less than, then power is on.
            # We can't just aribitarily add or subtract the value (which analysis
            # indicates is how the power status changes. Very weird, I know!) as that
            # is not an idempotent action, we must check if the addition or
            # substraction is needed first. e.g. via getPower()
            # i.e. If we added or subtracted twice, we would cause a wrap of the
            # integer and not get the desired result.
            if on:
                self._.SwingAndPower -= 0 if self.getPower() else kMirageAcPowerOff
            else:
                self._.SwingAndPower += kMirageAcPowerOff if self.getPower() else 0

    ## Get the value of the current power setting.
    ## @return true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Mirage.cpp lines 251-260
    def getPower(self) -> bool:
        if self._model == MIRAGE_KKG29AC1:
            return self._.Power == kMirageAcKKG29AC1PowerOn
        else:
            return self._.SwingAndPower < kMirageAcPowerOff

    ## Get the operating mode setting of the A/C.
    ## @return The current operating mode setting.
    ## Direct translation from ir_Mirage.cpp line 264
    def getMode(self) -> int:
        return self._.Mode

    ## Set the operating mode of the A/C.
    ## @param[in] mode The desired operating mode.
    ## Direct translation from ir_Mirage.cpp lines 266-282
    def setMode(self, mode: int) -> None:
        if mode in [kMirageAcCool, kMirageAcDry, kMirageAcHeat, kMirageAcFan, kMirageAcRecycle]:
            self._.Mode = mode
            # Reset turbo if we have to.
            self.setTurbo(self.getTurbo())
        else:
            # Default to cool mode for anything else.
            self.setMode(kMirageAcCool)

    ## Set the temperature.
    ## @param[in] degrees The temperature in degrees celsius.
    ## Direct translation from ir_Mirage.cpp lines 284-290
    def setTemp(self, degrees: int) -> None:
        # Make sure we have desired temp in the correct range.
        celsius = max(degrees, kMirageAcMinTemp)
        self._.Temp = min(celsius, kMirageAcMaxTemp) + kMirageAcTempOffset

    ## Get the current temperature setting.
    ## @return The current setting for temp. in degrees celsius.
    ## Direct translation from ir_Mirage.cpp line 294
    def getTemp(self) -> int:
        return self._.Temp - kMirageAcTempOffset

    ## Set the speed of the fan.
    ## @param[in] speed The desired setting.
    ## Direct translation from ir_Mirage.cpp lines 296-300
    def setFan(self, speed: int) -> None:
        self._.Fan = speed if speed <= kMirageAcFanLow else kMirageAcFanAuto

    ## Get the current fan speed setting.
    ## @return The current fan speed/mode.
    ## Direct translation from ir_Mirage.cpp line 304
    def getFan(self) -> int:
        return self._.Fan

    ## Change the Turbo setting.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Mirage.cpp lines 306-317
    def setTurbo(self, on: bool) -> None:
        value = on and (self.getMode() == kMirageAcCool)
        if self._model == MIRAGE_KKG29AC1:
            self._.Turbo_Kkg29ac1 = value
        else:
            self._.Turbo_Kkg9ac1 = value

    ## Get the value of the current Turbo setting.
    ## @return true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Mirage.cpp lines 319-326
    def getTurbo(self) -> bool:
        if self._model == MIRAGE_KKG29AC1:
            return bool(self._.Turbo_Kkg29ac1)
        else:
            return bool(self._.Turbo_Kkg9ac1)

    ## Change the Sleep setting.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Mirage.cpp lines 328-338
    def setSleep(self, on: bool) -> None:
        if self._model == MIRAGE_KKG29AC1:
            self._.Sleep_Kkg29ac1 = on
        else:
            self._.Sleep_Kkg9ac1 = on

    ## Get the value of the current Sleep setting.
    ## @return true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Mirage.cpp lines 340-347
    def getSleep(self) -> bool:
        if self._model == MIRAGE_KKG29AC1:
            return bool(self._.Sleep_Kkg29ac1)
        else:
            return bool(self._.Sleep_Kkg9ac1)

    ## Change the Light/Display setting.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## @note Light is a toggle on the KKG29AC1 model.
    ## Direct translation from ir_Mirage.cpp lines 349-360
    def setLight(self, on: bool) -> None:
        if self._model == MIRAGE_KKG29AC1:
            self._.LightToggle_Kkg29ac1 = on
        else:
            self._.Light_Kkg9ac1 = on

    ## Get the value of the current Light/Display setting.
    ## @return true, the setting is on. false, the setting is off.
    ## @note Light is a toggle on the KKG29AC1 model.
    ## Direct translation from ir_Mirage.cpp lines 362-370
    def getLight(self) -> bool:
        if self._model == MIRAGE_KKG29AC1:
            return bool(self._.LightToggle_Kkg29ac1)
        else:
            return bool(self._.Light_Kkg9ac1)

    ## Get the clock time of the A/C unit.
    ## @return Nr. of seconds past midnight.
    ## Direct translation from ir_Mirage.cpp lines 372-382
    def getClock(self) -> int:
        if self._model == MIRAGE_KKG29AC1:
            return 0
        else:
            return ((bcdToUint8(self._.Hours) * 60) + bcdToUint8(self._.Minutes)) * 60 + bcdToUint8(
                self._.Seconds
            )

    ## Set the clock time on the A/C unit.
    ## @param[in] nr_of_seconds Nr. of seconds past midnight.
    ## Direct translation from ir_Mirage.cpp lines 384-401
    def setClock(self, nr_of_seconds: int) -> None:
        if self._model == MIRAGE_KKG29AC1:
            self._.Minutes = self._.Seconds = 0  # No clock setting. Clear it just in case.
        else:
            # Limit to 23:59:59
            remaining = min(nr_of_seconds, 24 * 60 * 60 - 1)
            self._.Seconds = uint8ToBcd(remaining % 60)
            remaining //= 60
            self._.Minutes = uint8ToBcd(remaining % 60)
            remaining //= 60
            self._.Hours = uint8ToBcd(remaining)

    ## Set the Vertical Swing setting/position of the A/C.
    ## @param[in] position The desired swing setting.
    ## Direct translation from ir_Mirage.cpp lines 403-428
    def setSwingV(self, position: int) -> None:
        if position in [
            kMirageAcSwingVOff,
            kMirageAcSwingVLowest,
            kMirageAcSwingVLow,
            kMirageAcSwingVMiddle,
            kMirageAcSwingVHigh,
            kMirageAcSwingVHighest,
            kMirageAcSwingVAuto,
        ]:
            if self._model == MIRAGE_KKG29AC1:
                self._.SwingV = position != kMirageAcSwingVOff
            else:
                power = self.getPower()
                self._.SwingAndPower = position
                # Power needs to be reapplied after overwriting SwingAndPower
                self.setPower(power)
        else:
            # Default to Auto for anything else.
            self.setSwingV(kMirageAcSwingVAuto)

    ## Get the Vertical Swing setting/position of the A/C.
    ## @return The desired Vertical Swing setting/position.
    ## Direct translation from ir_Mirage.cpp lines 430-439
    def getSwingV(self) -> int:
        if self._model == MIRAGE_KKG29AC1:
            return kMirageAcSwingVAuto if self._.SwingV else kMirageAcSwingVOff
        else:
            return self._.SwingAndPower - (0 if self.getPower() else kMirageAcPowerOff)

    ## Set the Horizontal Swing setting of the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Mirage.cpp lines 441-451
    def setSwingH(self, on: bool) -> None:
        if self._model == MIRAGE_KKG29AC1:
            self._.SwingH = on

    ## Get the Horizontal Swing setting of the A/C.
    ## @return on true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Mirage.cpp lines 453-460
    def getSwingH(self) -> bool:
        if self._model == MIRAGE_KKG29AC1:
            return bool(self._.SwingH)
        else:
            return False

    ## Set the Quiet setting of the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Mirage.cpp lines 462-472
    def setQuiet(self, on: bool) -> None:
        if self._model == MIRAGE_KKG29AC1:
            self._.Quiet = on

    ## Get the Quiet setting of the A/C.
    ## @return on true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Mirage.cpp lines 474-481
    def getQuiet(self) -> bool:
        if self._model == MIRAGE_KKG29AC1:
            return bool(self._.Quiet)
        else:
            return False

    ## Set the CleanToggle setting of the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Mirage.cpp lines 483-493
    def setCleanToggle(self, on: bool) -> None:
        if self._model == MIRAGE_KKG29AC1:
            self._.CleanToggle = on

    ## Get the Clean Toggle setting of the A/C.
    ## @return on true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Mirage.cpp lines 495-502
    def getCleanToggle(self) -> bool:
        if self._model == MIRAGE_KKG29AC1:
            return bool(self._.CleanToggle)
        else:
            return False

    ## Set the Filter setting of the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Mirage.cpp lines 504-514
    def setFilter(self, on: bool) -> None:
        if self._model == MIRAGE_KKG29AC1:
            self._.Filter = on

    ## Get the Filter setting of the A/C.
    ## @return on true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Mirage.cpp lines 516-523
    def getFilter(self) -> bool:
        if self._model == MIRAGE_KKG29AC1:
            return bool(self._.Filter)
        else:
            return False

    ## Set the IFeel setting of the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Mirage.cpp lines 525-541
    def setIFeel(self, on: bool) -> None:
        if self._model == MIRAGE_KKG29AC1:
            self._.IFeel = on
            if on:
                # If no previous sensor temp, default to currently desired temp.
                if not self._.SensorTemp:
                    self._.SensorTemp = self.getTemp()
            else:
                self._.SensorTemp = 0  # When turning it off, clear the Sensor Temp.

    ## Get the IFeel setting of the A/C.
    ## @return on true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Mirage.cpp lines 543-550
    def getIFeel(self) -> bool:
        if self._model == MIRAGE_KKG29AC1:
            return bool(self._.IFeel)
        else:
            return False

    ## Set the Sensor Temp setting of the A/C's remote.
    ## @param[in] degrees The desired sensor temp. in degrees celsius.
    ## Direct translation from ir_Mirage.cpp lines 552-563
    def setSensorTemp(self, degrees: int) -> None:
        if self._model == MIRAGE_KKG29AC1:
            self._.SensorTemp = min(kMirageAcSensorTempMax, degrees) + kMirageAcSensorTempOffset

    ## Get the Sensor Temp setting of the A/C's remote.
    ## @return The current setting for the sensor temp. in degrees celsius.
    ## Direct translation from ir_Mirage.cpp lines 565-574
    def getSensorTemp(self) -> int:
        if self._model == MIRAGE_KKG29AC1:
            return self._.SensorTemp - kMirageAcSensorTempOffset
        else:
            return 0

    ## Get the number of minutes the On Timer is currently set for.
    ## @return Nr. of Minutes the timer is set for. 0, is the timer is not in use.
    ## Direct translation from ir_Mirage.cpp lines 576-585
    def getOnTimer(self) -> int:
        if self._model == MIRAGE_KKG29AC1:
            return self._.OnTimerHours * 60 + self._.OnTimerMins if self._.OnTimerEnable else 0
        else:
            return 0

    ## Set the number of minutes for the On Timer.
    ## @param[in] nr_of_mins How long to set the timer for. 0 disables the timer.
    ## Direct translation from ir_Mirage.cpp lines 587-600
    def setOnTimer(self, nr_of_mins: int) -> None:
        mins = min(nr_of_mins, 24 * 60)
        if self._model == MIRAGE_KKG29AC1:
            self._.OnTimerEnable = mins > 0
            self._.OnTimerHours = mins // 60
            self._.OnTimerMins = mins % 60

    ## Get the number of minutes the Off Timer is currently set for.
    ## @return Nr. of Minutes the timer is set for. 0, is the timer is not in use.
    ## Direct translation from ir_Mirage.cpp lines 602-611
    def getOffTimer(self) -> int:
        if self._model == MIRAGE_KKG29AC1:
            return self._.OffTimerHours * 60 + self._.OffTimerMins if self._.OffTimerEnable else 0
        else:
            return 0

    ## Set the number of minutes for the Off Timer.
    ## @param[in] nr_of_mins How long to set the timer for. 0 disables the timer.
    ## Direct translation from ir_Mirage.cpp lines 613-626
    def setOffTimer(self, nr_of_mins: int) -> None:
        mins = min(nr_of_mins, 24 * 60)
        if self._model == MIRAGE_KKG29AC1:
            self._.OffTimerEnable = mins > 0
            self._.OffTimerHours = mins // 60
            self._.OffTimerMins = mins % 60

    ## Convert a native mode into its stdAc equivalent.
    ## @param[in] mode The native setting to be converted.
    ## @return The stdAc equivalent of the native setting.
    ## Direct translation from ir_Mirage.cpp lines 628-638
    @staticmethod
    def toCommonMode(mode: int) -> str:
        # Returns stdAc::opmode_t equivalent (string)
        if mode == kMirageAcHeat:
            return "kHeat"
        elif mode == kMirageAcDry:
            return "kDry"
        elif mode == kMirageAcFan:
            return "kFan"
        else:
            return "kCool"

    ## Convert a native fan speed into its stdAc equivalent.
    ## @param[in] speed The native setting to be converted.
    ## @param[in] model The model type to use to influence the conversion.
    ## @return The stdAc equivalent of the native setting.
    ## Direct translation from ir_Mirage.cpp lines 640-663
    @staticmethod
    def toCommonFanSpeed(speed: int, model: int = MIRAGE_KKG9AC1) -> str:
        # Returns stdAc::fanspeed_t equivalent (string)
        if model == MIRAGE_KKG29AC1:
            if speed == kMirageAcKKG29AC1FanHigh:
                return "kHigh"
            elif speed == kMirageAcKKG29AC1FanMed:
                return "kMedium"
            elif speed == kMirageAcKKG29AC1FanLow:
                return "kLow"
            else:
                return "kAuto"
        else:
            if speed == kMirageAcFanHigh:
                return "kHigh"
            elif speed == kMirageAcFanMed:
                return "kMedium"
            elif speed == kMirageAcFanLow:
                return "kLow"
            else:
                return "kAuto"

    ## Convert a stdAc::opmode_t enum into its native mode.
    ## @param[in] mode The enum to be converted.
    ## @return The native equivalent of the enum.
    ## Direct translation from ir_Mirage.cpp lines 665-675
    @staticmethod
    def convertMode(mode: str) -> int:
        # mode is stdAc::opmode_t equivalent (string)
        if mode == "kHeat":
            return kMirageAcHeat
        elif mode == "kDry":
            return kMirageAcDry
        elif mode == "kFan":
            return kMirageAcFan
        else:
            return kMirageAcCool

    ## Convert a stdAc::fanspeed_t enum into it's native speed.
    ## @param[in] speed The enum to be converted.
    ## @param[in] model The model type to use to influence the conversion.
    ## @return The native equivalent of the enum.
    ## Direct translation from ir_Mirage.cpp lines 677-702
    @staticmethod
    def convertFan(speed: str, model: int = MIRAGE_KKG9AC1) -> int:
        # speed is stdAc::fanspeed_t equivalent (string)
        if model == MIRAGE_KKG29AC1:
            low = kMirageAcKKG29AC1FanLow
            med = kMirageAcKKG29AC1FanMed
        else:
            low = kMirageAcFanLow
            med = kMirageAcFanMed

        if speed in ["kMin", "kLow"]:
            return low
        elif speed == "kMedium":
            return med
        elif speed in ["kHigh", "kMax"]:
            return kMirageAcFanHigh
        else:
            return kMirageAcFanAuto

    ## Convert a stdAc::swingv_t enum into it's native setting.
    ## @param[in] position The enum to be converted.
    ## @return The native equivalent of the enum.
    ## Direct translation from ir_Mirage.cpp lines 704-717
    @staticmethod
    def convertSwingV(position: str) -> int:
        # position is stdAc::swingv_t equivalent (string)
        if position == "kHighest":
            return kMirageAcSwingVHighest
        elif position == "kHigh":
            return kMirageAcSwingVHigh
        elif position == "kMiddle":
            return kMirageAcSwingVMiddle
        elif position == "kLow":
            return kMirageAcSwingVLow
        elif position == "kLowest":
            return kMirageAcSwingVLowest
        elif position == "kOff":
            return kMirageAcSwingVOff
        else:
            return kMirageAcSwingVAuto

    ## Convert a native vertical swing postion to it's common equivalent.
    ## @param[in] pos A native position to convert.
    ## @return The common vertical swing position.
    ## Direct translation from ir_Mirage.cpp lines 719-732
    @staticmethod
    def toCommonSwingV(pos: int) -> str:
        # Returns stdAc::swingv_t equivalent (string)
        if pos == kMirageAcSwingVHighest:
            return "kHighest"
        elif pos == kMirageAcSwingVHigh:
            return "kHigh"
        elif pos == kMirageAcSwingVMiddle:
            return "kMiddle"
        elif pos == kMirageAcSwingVLow:
            return "kLow"
        elif pos == kMirageAcSwingVLowest:
            return "kLowest"
        elif pos == kMirageAcSwingVAuto:
            return "kAuto"
        else:
            return "kOff"

    ## Convert the current internal state into its stdAc::state_t equivalent.
    ## @return The stdAc equivalent of the native settings.
    ## Direct translation from ir_Mirage.cpp lines 734-760
    def toCommon(self) -> dict:
        # Returns stdAc::state_t equivalent (dict)
        result = {}
        result["protocol"] = "MIRAGE"
        result["model"] = self._model
        result["power"] = self.getPower()
        result["mode"] = IRMirageAc.toCommonMode(self._.Mode)
        result["celsius"] = True
        result["degrees"] = self.getTemp()
        result["sensorTemperature"] = self.getSensorTemp()
        result["fanspeed"] = IRMirageAc.toCommonFanSpeed(self.getFan(), self._model)
        result["swingv"] = IRMirageAc.toCommonSwingV(self.getSwingV())
        result["swingh"] = "kAuto" if self.getSwingH() else "kOff"
        result["turbo"] = self.getTurbo()
        result["light"] = self.getLight()
        result["clean"] = self.getCleanToggle()
        result["filter"] = self.getFilter()
        result["sleep"] = 0 if self.getSleep() else -1
        result["quiet"] = self.getQuiet()
        result["clock"] = self.getClock() // 60
        result["iFeel"] = self.getIFeel()
        # Not supported.
        result["econo"] = False
        result["beep"] = False
        return result

    ## Convert & set a stdAc::state_t to its equivalent internal settings.
    ## @param[in] state The desired state in stdAc::state_t form.
    ## Direct translation from ir_Mirage.cpp lines 762-789
    def fromCommon(self, state: dict) -> None:
        self.stateReset()
        self._model = state.get("model", MIRAGE_KKG9AC1)  # Set directly to avoid loop
        self.setPower(state.get("power", False))
        degrees = state.get("degrees", 25)
        if not state.get("celsius", True):
            degrees = fahrenheitToCelsius(degrees)
        self.setTemp(degrees)
        self.setMode(IRMirageAc.convertMode(state.get("mode", "kCool")))
        self.setFan(IRMirageAc.convertFan(state.get("fanspeed", "kAuto"), self._model))
        self.setTurbo(state.get("turbo", False))
        self.setSleep(state.get("sleep", -1) >= 0)
        self.setLight(state.get("light", False))
        self.setSwingV(IRMirageAc.convertSwingV(state.get("swingv", "kOff")))
        self.setSwingH(state.get("swingh", "kOff") != "kOff")
        self.setQuiet(state.get("quiet", False))
        self.setCleanToggle(state.get("clean", False))
        self.setFilter(state.get("filter", False))
        # setClock() expects seconds, not minutes.
        clock = state.get("clock", 0)
        self.setClock(clock * 60 if clock > 0 else 0)
        self.setIFeel(state.get("iFeel", False))
        sensorTemp = state.get("sensorTemperature", kNoTempValue)
        if sensorTemp != kNoTempValue:
            if not state.get("celsius", True):
                sensorTemp = fahrenheitToCelsius(sensorTemp)
            self.setSensorTemp(sensorTemp)
        # Non-common settings.
        self.setOnTimer(0)
        self.setOffTimer(0)
