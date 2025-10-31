# Copyright 2017 Ville Skyttä (scop)
# Copyright 2017, 2018 David Conran
# Python translation: Direct conversion from C++ with NO optimizations

## @file
## @brief Support for Gree A/C protocols.
## Direct translation from IRremoteESP8266 ir_Gree.cpp and ir_Gree.h

from typing import List

# Ref: https://github.com/ToniA/arduino-heatpumpir/blob/master/GreeHeatpumpIR.h

# Constants - Timing values
kGreeHdrMark = 9000
kGreeHdrSpace = 4500
kGreeBitMark = 620
kGreeOneSpace = 1600
kGreeZeroSpace = 540
kGreeMsgSpace = 19980
kGreeBlockFooter = 0b010
kGreeBlockFooterBits = 3

# State length constants (from IRremoteESP8266.h lines 1259-1260)
kGreeStateLength = 8
kGreeBits = kGreeStateLength * 8  # 64 bits

# Mode constants
kGreeAuto = 0
kGreeCool = 1
kGreeDry = 2
kGreeFan = 3
kGreeHeat = 4
kGreeEcono = 5

# Fan speed constants
kGreeFanAuto = 0
kGreeFanMin = 1
kGreeFanMed = 2
kGreeFanMax = 3

# Temperature constants
kGreeMinTempC = 16  # Celsius
kGreeMaxTempC = 30  # Celsius
kGreeMinTempF = 61  # Fahrenheit
kGreeMaxTempF = 86  # Fahrenheit
kGreeTimerMax = 24 * 60  # Minutes

# Vertical swing constants
kGreeSwingLastPos = 0b0000  # 0
kGreeSwingAuto = 0b0001  # 1
kGreeSwingUp = 0b0010  # 2
kGreeSwingMiddleUp = 0b0011  # 3
kGreeSwingMiddle = 0b0100  # 4
kGreeSwingMiddleDown = 0b0101  # 5
kGreeSwingDown = 0b0110  # 6
kGreeSwingDownAuto = 0b0111  # 7
kGreeSwingMiddleAuto = 0b1001  # 9
kGreeSwingUpAuto = 0b1011  # 11

# Horizontal swing constants
kGreeSwingHOff = 0b000  # 0
kGreeSwingHAuto = 0b001  # 1
kGreeSwingHMaxLeft = 0b010  # 2
kGreeSwingHLeft = 0b011  # 3
kGreeSwingHMiddle = 0b100  # 4
kGreeSwingHRight = 0b101  # 5
kGreeSwingHMaxRight = 0b110  # 6

# Display temperature source constants
kGreeDisplayTempOff = 0b00  # 0
kGreeDisplayTempSet = 0b01  # 1
kGreeDisplayTempInside = 0b10  # 2
kGreeDisplayTempOutside = 0b11  # 3

# Model enums
GREE_YAW1F = 0
GREE_YBOFB = 1
GREE_YX1FSF = 2

# Kelvinator checksum start value (used by Gree)
kKelvinatorChecksumStart = 10


## Calculate block checksum for Gree protocol
## Uses the same algorithm as Kelvinator
## EXACT translation from IRKelvinatorAC::calcBlockChecksum (ir_Kelvinator.cpp lines 163-173)
def calcBlockChecksum(block: List[int], length: int = 8) -> int:
    """
    Calculate checksum for a block of state.
    EXACT translation from IRremoteESP8266 IRKelvinatorAC::calcBlockChecksum
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


def fahrenheitToCelsius(temp: float) -> float:
    """Convert Fahrenheit to Celsius"""
    return (temp - 32.0) / 1.8


def celsiusToFahrenheit(temp: float) -> float:
    """Convert Celsius to Fahrenheit"""
    return temp * 1.8 + 32.0


## Native representation of a Gree A/C message.
## This is a direct translation of the C++ union/struct
class GreeProtocol:
    def __init__(self):
        # The state array (8 bytes for Gree)
        self.remote_state = [0] * 8

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
    def Fan(self) -> int:
        return (self.remote_state[0] >> 4) & 0x03

    @Fan.setter
    def Fan(self, value: int) -> None:
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

    @property
    def Sleep(self) -> int:
        return (self.remote_state[0] >> 7) & 0x01

    @Sleep.setter
    def Sleep(self, value: bool) -> None:
        if value:
            self.remote_state[0] |= 0x80
        else:
            self.remote_state[0] &= 0x7F

    # Byte 1
    @property
    def Temp(self) -> int:
        return self.remote_state[1] & 0x0F

    @Temp.setter
    def Temp(self, value: int) -> None:
        self.remote_state[1] = (self.remote_state[1] & 0xF0) | (value & 0x0F)

    @property
    def TimerHalfHr(self) -> int:
        return (self.remote_state[1] >> 4) & 0x01

    @TimerHalfHr.setter
    def TimerHalfHr(self, value: bool) -> None:
        if value:
            self.remote_state[1] |= 0x10
        else:
            self.remote_state[1] &= 0xEF

    @property
    def TimerTensHr(self) -> int:
        return (self.remote_state[1] >> 5) & 0x03

    @TimerTensHr.setter
    def TimerTensHr(self, value: int) -> None:
        self.remote_state[1] = (self.remote_state[1] & 0x9F) | ((value & 0x03) << 5)

    @property
    def TimerEnabled(self) -> int:
        return (self.remote_state[1] >> 7) & 0x01

    @TimerEnabled.setter
    def TimerEnabled(self, value: bool) -> None:
        if value:
            self.remote_state[1] |= 0x80
        else:
            self.remote_state[1] &= 0x7F

    # Byte 2
    @property
    def TimerHours(self) -> int:
        return self.remote_state[2] & 0x0F

    @TimerHours.setter
    def TimerHours(self, value: int) -> None:
        self.remote_state[2] = (self.remote_state[2] & 0xF0) | (value & 0x0F)

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
    def ModelA(self) -> int:
        return (self.remote_state[2] >> 6) & 0x01

    @ModelA.setter
    def ModelA(self, value: bool) -> None:
        if value:
            self.remote_state[2] |= 0x40
        else:
            self.remote_state[2] &= 0xBF

    @property
    def Xfan(self) -> int:
        return (self.remote_state[2] >> 7) & 0x01

    @Xfan.setter
    def Xfan(self, value: bool) -> None:
        if value:
            self.remote_state[2] |= 0x80
        else:
            self.remote_state[2] &= 0x7F

    # Byte 3
    @property
    def TempExtraDegreeF(self) -> int:
        return (self.remote_state[3] >> 2) & 0x01

    @TempExtraDegreeF.setter
    def TempExtraDegreeF(self, value: bool) -> None:
        if value:
            self.remote_state[3] |= 0x04
        else:
            self.remote_state[3] &= 0xFB

    @property
    def UseFahrenheit(self) -> int:
        return (self.remote_state[3] >> 3) & 0x01

    @UseFahrenheit.setter
    def UseFahrenheit(self, value: bool) -> None:
        if value:
            self.remote_state[3] |= 0x08
        else:
            self.remote_state[3] &= 0xF7

    @property
    def unknown1(self) -> int:
        return (self.remote_state[3] >> 4) & 0x0F

    @unknown1.setter
    def unknown1(self, value: int) -> None:
        self.remote_state[3] = (self.remote_state[3] & 0x0F) | ((value & 0x0F) << 4)

    # Byte 4
    @property
    def SwingV(self) -> int:
        return self.remote_state[4] & 0x0F

    @SwingV.setter
    def SwingV(self, value: int) -> None:
        self.remote_state[4] = (self.remote_state[4] & 0xF0) | (value & 0x0F)

    @property
    def SwingH(self) -> int:
        return (self.remote_state[4] >> 4) & 0x07

    @SwingH.setter
    def SwingH(self, value: int) -> None:
        self.remote_state[4] = (self.remote_state[4] & 0x8F) | ((value & 0x07) << 4)

    # Byte 5
    @property
    def DisplayTemp(self) -> int:
        return self.remote_state[5] & 0x03

    @DisplayTemp.setter
    def DisplayTemp(self, value: int) -> None:
        self.remote_state[5] = (self.remote_state[5] & 0xFC) | (value & 0x03)

    @property
    def IFeel(self) -> int:
        return (self.remote_state[5] >> 2) & 0x01

    @IFeel.setter
    def IFeel(self, value: bool) -> None:
        if value:
            self.remote_state[5] |= 0x04
        else:
            self.remote_state[5] &= 0xFB

    @property
    def unknown2(self) -> int:
        return (self.remote_state[5] >> 3) & 0x07

    @unknown2.setter
    def unknown2(self, value: int) -> None:
        self.remote_state[5] = (self.remote_state[5] & 0xC7) | ((value & 0x07) << 3)

    @property
    def WiFi(self) -> int:
        return (self.remote_state[5] >> 6) & 0x01

    @WiFi.setter
    def WiFi(self, value: bool) -> None:
        if value:
            self.remote_state[5] |= 0x40
        else:
            self.remote_state[5] &= 0xBF

    # Byte 6 - unused

    # Byte 7
    @property
    def Econo(self) -> int:
        return (self.remote_state[7] >> 2) & 0x01

    @Econo.setter
    def Econo(self, value: bool) -> None:
        if value:
            self.remote_state[7] |= 0x04
        else:
            self.remote_state[7] &= 0xFB

    @property
    def Sum(self) -> int:
        return (self.remote_state[7] >> 4) & 0x0F

    @Sum.setter
    def Sum(self, value: int) -> None:
        self.remote_state[7] = (self.remote_state[7] & 0x0F) | ((value & 0x0F) << 4)


## Send a Gree Heat Pump formatted message.
## Status: STABLE / Working.
## @param[in] data The message to be sent.
## @param[in] nbytes The number of bytes of message to be sent.
## @param[in] repeat The number of times the command is to be repeated.
## Direct translation from IRremoteESP8266 IRsend::sendGree (lines 48-69)
def sendGree(data: List[int], nbytes: int, repeat: int = 0) -> List[int]:
    """
    Send a Gree Heat Pump formatted message.
    EXACT translation from IRremoteESP8266 IRsend::sendGree

    Returns timing array instead of transmitting via hardware.
    """
    if nbytes < 8:  # kGreeStateLength
        return []  # Not enough bytes to send a proper message.

    # Import here to avoid circular import
    from app.core.ir_protocols.ir_send import sendGeneric, sendData

    all_timings = []

    for r in range(repeat + 1):
        # Block #1 (4 bytes)
        block1_timings = sendGeneric(
            headermark=kGreeHdrMark,
            headerspace=kGreeHdrSpace,
            onemark=kGreeBitMark,
            onespace=kGreeOneSpace,
            zeromark=kGreeBitMark,
            zerospace=kGreeZeroSpace,
            footermark=0,
            gap=0,  # No Footer yet
            dataptr=data,
            nbytes=4,
            MSBfirst=False,
        )
        all_timings.extend(block1_timings)

        # Footer #1 (3 bits, B010)
        footer1_timings = sendData(
            onemark=kGreeBitMark,
            onespace=kGreeOneSpace,
            zeromark=kGreeBitMark,
            zerospace=kGreeZeroSpace,
            data=kGreeBlockFooter,
            nbits=kGreeBlockFooterBits,
            MSBfirst=False,
        )
        all_timings.extend(footer1_timings)
        all_timings.append(kGreeBitMark)
        all_timings.append(kGreeMsgSpace)

        # Block #2 (remaining bytes)
        block2_timings = sendGeneric(
            headermark=0,
            headerspace=0,  # No Header for Block #2
            onemark=kGreeBitMark,
            onespace=kGreeOneSpace,
            zeromark=kGreeBitMark,
            zerospace=kGreeZeroSpace,
            footermark=kGreeBitMark,
            gap=kGreeMsgSpace,
            dataptr=data[4:],
            nbytes=nbytes - 4,
            MSBfirst=False,
        )
        all_timings.extend(block2_timings)

    return all_timings


## Class for handling detailed Gree A/C messages.
## Direct translation from C++ IRGreeAC class
class IRGreeAC:
    ## Class Constructor
    ## @param[in] model The enum for the model of A/C to be emulated.
    def __init__(self, model: int = GREE_YAW1F) -> None:
        self._: GreeProtocol = GreeProtocol()
        self._model: int = model
        self.setModel(model)
        self.stateReset()

    ## Reset the internal state to a fixed known good state.
    ## Direct translation from ir_Gree.cpp lines 120-127
    def stateReset(self) -> None:
        # This resets to a known-good state to Power Off, Fan Auto, Mode Auto, 25C.
        for i in range(len(self._.remote_state)):
            self._.remote_state[i] = 0
        self._.Temp = 9
        self._.Light = True
        self._.unknown1 = 5
        self._.unknown2 = 4

    ## Fix up the internal state so it is correct.
    ## @note Internal use only.
    ## Direct translation from ir_Gree.cpp lines 131-134
    def fixup(self) -> None:
        self.setPower(self.getPower())  # Redo the power bits as they differ between models.
        self.checksum()  # Calculate the checksums

    ## Calculate and set the checksum values for the internal state.
    ## @param[in] length The size/length of the state array to fix the checksum of.
    ## Direct translation from ir_Gree.cpp lines 170-173
    def checksum(self, length: int = 8) -> None:
        # Gree uses the same checksum alg. as Kelvinator's block checksum.
        self._.Sum = calcBlockChecksum(self._.remote_state, length)

    ## Verify the checksum is valid for a given state.
    ## @param[in] state The array to verify the checksum of.
    ## @param[in] length The length of the state array.
    ## @return true, if the state has a valid checksum. Otherwise, false.
    ## Direct translation from ir_Gree.cpp lines 179-183
    @staticmethod
    def validChecksum(state: List[int], length: int = 8) -> bool:
        # Top 4 bits of the last byte in the state is the state's checksum.
        return ((state[length - 1] >> 4) & 0x0F) == calcBlockChecksum(state, length)

    ## Set the model of the A/C to emulate.
    ## @param[in] model The enum of the appropriate model.
    ## Direct translation from ir_Gree.cpp lines 187-194
    def setModel(self, model: int) -> None:
        if model in [GREE_YAW1F, GREE_YBOFB, GREE_YX1FSF]:
            self._model = model
        else:
            self._model = GREE_YAW1F

    ## Get/Detect the model of the A/C.
    ## @return The enum of the compatible model.
    ## Direct translation from ir_Gree.cpp line 198
    def getModel(self) -> int:
        return self._model

    ## Change the power setting to On.
    ## Direct translation from ir_Gree.cpp line 201
    def on(self) -> None:
        self.setPower(True)

    ## Change the power setting to Off.
    ## Direct translation from ir_Gree.cpp line 204
    def off(self) -> None:
        self.setPower(False)

    ## Change the power setting.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Gree.cpp lines 209-213
    def setPower(self, on: bool) -> None:
        self._.Power = on
        # May not be needed. See #814
        self._.ModelA = on and self._model == GREE_YAW1F

    ## Get the value of the current power setting.
    ## @return true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Gree.cpp lines 218-221
    def getPower(self) -> bool:
        return bool(self._.Power)

    ## Set the default temperature units to use.
    ## @param[in] on Use Fahrenheit as the units.
    ##   true is Fahrenheit, false is Celsius.
    ## Direct translation from ir_Gree.cpp line 226
    def setUseFahrenheit(self, on: bool) -> None:
        self._.UseFahrenheit = on

    ## Get the default temperature units in use.
    ## @return true is Fahrenheit, false is Celsius.
    ## Direct translation from ir_Gree.cpp line 230
    def getUseFahrenheit(self) -> bool:
        return bool(self._.UseFahrenheit)

    ## Set the temp. in degrees
    ## @param[in] temp Desired temperature in Degrees.
    ## @param[in] fahrenheit Use units of Fahrenheit and set that as units used.
    ##   false is Celsius (Default), true is Fahrenheit.
    ## Direct translation from ir_Gree.cpp lines 238-257
    def setTemp(self, temp: int, fahrenheit: bool = False) -> None:
        safecelsius = float(temp)
        if fahrenheit:
            # Convert to F, and add a fudge factor to round to the expected degree.
            safecelsius = fahrenheitToCelsius(temp + 0.6)
        self.setUseFahrenheit(fahrenheit)  # Set the correct Temp units.

        # Make sure we have desired temp in the correct range.
        safecelsius = max(float(kGreeMinTempC), safecelsius)
        safecelsius = min(float(kGreeMaxTempC), safecelsius)
        # An operating mode of Auto locks the temp to a specific value. Do so.
        if self._.Mode == kGreeAuto:
            safecelsius = 25.0

        # Set the "main" Celsius degrees.
        self._.Temp = int(safecelsius - kGreeMinTempC)
        # Deal with the extra degree fahrenheit difference.
        self._.TempExtraDegreeF = int(safecelsius * 2) & 1

    ## Get the set temperature
    ## @return The temperature in degrees in the current units (C/F) set.
    ## Direct translation from ir_Gree.cpp lines 261-270
    def getTemp(self) -> int:
        deg = kGreeMinTempC + self._.Temp
        if self._.UseFahrenheit:
            deg = int(celsiusToFahrenheit(deg))
            # Retrieve the "extra" fahrenheit from elsewhere in the code.
            if self._.TempExtraDegreeF:
                deg += 1
            deg = max(deg, kGreeMinTempF)  # Cover the fact that 61F is < 16C
        return deg

    ## Set the speed of the fan.
    ## @param[in] speed The desired setting. 0 is auto, 1-3 is the speed.
    ## Direct translation from ir_Gree.cpp lines 274-279
    def setFan(self, speed: int) -> None:
        fan = min(kGreeFanMax, speed)  # Bounds check
        if self._.Mode == kGreeDry:
            fan = 1  # DRY mode is always locked to fan 1.
        # Set the basic fan values.
        self._.Fan = fan

    ## Get the current fan speed setting.
    ## @return The current fan speed.
    ## Direct translation from ir_Gree.cpp line 283
    def getFan(self) -> int:
        return self._.Fan

    ## Set the operating mode of the A/C.
    ## @param[in] new_mode The desired operating mode.
    ## Direct translation from ir_Gree.cpp lines 287-302
    def setMode(self, new_mode: int) -> None:
        mode = new_mode
        if mode == kGreeAuto:
            # AUTO is locked to 25C
            self.setTemp(25)
        elif mode == kGreeDry:
            # DRY always sets the fan to 1.
            self.setFan(1)
        elif mode in [kGreeCool, kGreeFan, kGreeEcono, kGreeHeat]:
            pass
        else:
            # If we get an unexpected mode, default to AUTO.
            mode = kGreeAuto
        self._.Mode = mode

    ## Get the operating mode setting of the A/C.
    ## @return The current operating mode setting.
    ## Direct translation from ir_Gree.cpp line 306
    def getMode(self) -> int:
        return self._.Mode

    ## Set the Light (LED) setting of the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Gree.cpp line 310
    def setLight(self, on: bool) -> None:
        self._.Light = on

    ## Get the Light (LED) setting of the A/C.
    ## @return true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Gree.cpp line 314
    def getLight(self) -> bool:
        return bool(self._.Light)

    ## Set the IFeel setting of the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Gree.cpp line 318
    def setIFeel(self, on: bool) -> None:
        self._.IFeel = on

    ## Get the IFeel setting of the A/C.
    ## @return true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Gree.cpp line 322
    def getIFeel(self) -> bool:
        return bool(self._.IFeel)

    ## Set the Wifi (enabled) setting of the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Gree.cpp line 326
    def setWiFi(self, on: bool) -> None:
        self._.WiFi = on

    ## Get the Wifi (enabled) setting of the A/C.
    ## @return true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Gree.cpp line 330
    def getWiFi(self) -> bool:
        return bool(self._.WiFi)

    ## Set the XFan (Mould) setting of the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Gree.cpp line 334
    def setXFan(self, on: bool) -> None:
        self._.Xfan = on

    ## Get the XFan (Mould) setting of the A/C.
    ## @return true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Gree.cpp line 338
    def getXFan(self) -> bool:
        return bool(self._.Xfan)

    ## Set the Sleep setting of the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Gree.cpp line 342
    def setSleep(self, on: bool) -> None:
        self._.Sleep = on

    ## Get the Sleep setting of the A/C.
    ## @return true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Gree.cpp line 346
    def getSleep(self) -> bool:
        return bool(self._.Sleep)

    ## Set the Turbo setting of the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Gree.cpp line 350
    def setTurbo(self, on: bool) -> None:
        self._.Turbo = on

    ## Get the Turbo setting of the A/C.
    ## @return true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Gree.cpp line 354
    def getTurbo(self) -> bool:
        return bool(self._.Turbo)

    ## Set the Econo setting of the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Gree.cpp lines 358-362
    def setEcono(self, on: bool) -> None:
        self._.Econo = on
        if on and self.getModel() == GREE_YX1FSF:
            self.setMode(kGreeEcono)

    ## Get the Econo setting of the A/C.
    ## @return true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Gree.cpp lines 366-368
    def getEcono(self) -> bool:
        return bool(self._.Econo) or self.getMode() == kGreeEcono

    ## Set the Vertical Swing mode of the A/C.
    ## @param[in] automatic Do we use the automatic setting?
    ## @param[in] position The position/mode to set the vanes to.
    ## Direct translation from ir_Gree.cpp lines 373-400
    def setSwingVertical(self, automatic: bool, position: int) -> None:
        self._.SwingAuto = automatic
        new_position = position
        if not automatic:
            if position in [
                kGreeSwingLastPos,
                kGreeSwingUp,
                kGreeSwingMiddleUp,
                kGreeSwingMiddle,
                kGreeSwingMiddleDown,
                kGreeSwingDown,
            ]:
                pass
            else:
                new_position = kGreeSwingLastPos
        else:
            if position in [
                kGreeSwingAuto,
                kGreeSwingDownAuto,
                kGreeSwingMiddleAuto,
                kGreeSwingUpAuto,
            ]:
                pass
            else:
                new_position = kGreeSwingAuto
        self._.SwingV = new_position

    ## Get the Vertical Swing Automatic mode setting of the A/C.
    ## @return true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Gree.cpp line 404
    def getSwingVerticalAuto(self) -> bool:
        return bool(self._.SwingAuto)

    ## Get the Vertical Swing position setting of the A/C.
    ## @return The native position/mode.
    ## Direct translation from ir_Gree.cpp line 408
    def getSwingVerticalPosition(self) -> int:
        return self._.SwingV

    ## Get the Horizontal Swing position setting of the A/C.
    ## @return The native position/mode.
    ## Direct translation from ir_Gree.cpp line 412
    def getSwingHorizontal(self) -> int:
        return self._.SwingH

    ## Set the Horizontal Swing mode of the A/C.
    ## @param[in] position The position/mode to set the vanes to.
    ## Direct translation from ir_Gree.cpp lines 416-421
    def setSwingHorizontal(self, position: int) -> None:
        if position <= kGreeSwingHMaxRight:
            self._.SwingH = position
        else:
            self._.SwingH = kGreeSwingHOff

    ## Set the timer enable setting of the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Gree.cpp line 425
    def setTimerEnabled(self, on: bool) -> None:
        self._.TimerEnabled = on

    ## Get the timer enabled setting of the A/C.
    ## @return true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Gree.cpp line 429
    def getTimerEnabled(self) -> bool:
        return bool(self._.TimerEnabled)

    ## Get the timer time value from the A/C.
    ## @return The number of minutes the timer is set for.
    ## Direct translation from ir_Gree.cpp lines 433-437
    def getTimer(self) -> int:
        # Convert BCD to uint8
        hrs = (self._.TimerTensHr * 10) + self._.TimerHours
        return hrs * 60 + (30 if self._.TimerHalfHr else 0)

    ## Set the A/C's timer to turn off in X many minutes.
    ## @param[in] minutes The number of minutes the timer should be set for.
    ## Direct translation from ir_Gree.cpp lines 443-453
    def setTimer(self, minutes: int) -> None:
        mins = min(kGreeTimerMax, minutes)  # Bounds check.
        self.setTimerEnabled(mins >= 30)  # Timer is enabled when >= 30 mins.
        hours = mins // 60
        # Set the half hour bit.
        self._.TimerHalfHr = (mins % 60) >= 30
        # Set the "tens" digit of hours.
        self._.TimerTensHr = hours // 10
        # Set the "units" digit of hours.
        self._.TimerHours = hours % 10

    ## Set temperature display mode.
    ## @param[in] mode The desired temp source to display.
    ## Direct translation from ir_Gree.cpp line 467
    def setDisplayTempSource(self, mode: int) -> None:
        self._.DisplayTemp = mode

    ## Get the temperature display mode.
    ## @return The current temp source being displayed.
    ## Direct translation from ir_Gree.cpp line 473
    def getDisplayTempSource(self) -> int:
        return self._.DisplayTemp

    ## Get a PTR to the internal state/code for this protocol.
    ## @return PTR to a code for this protocol based on the current internal state.
    ## Direct translation from ir_Gree.cpp lines 149-152
    def getRaw(self) -> List[int]:
        self.fixup()  # Ensure correct settings before sending.
        return self._.remote_state

    ## Set the internal state from a valid code for this protocol.
    ## @param[in] new_code A valid code for this protocol.
    ## Direct translation from ir_Gree.cpp lines 156-166
    def setRaw(self, new_code: List[int]) -> None:
        for i in range(min(len(new_code), len(self._.remote_state))):
            self._.remote_state[i] = new_code[i]
        # We can only detect the difference between models when the power is on.
        if self._.Power:
            if self._.ModelA:
                self._model = GREE_YAW1F
            else:
                self._model = GREE_YBOFB
        if self._.Mode == kGreeEcono:
            self._model = GREE_YX1FSF


## Decode the supplied Gree HVAC message.
## Status: STABLE / Working.
## @param[in,out] results Ptr to the data to decode & where to store the decode result.
## @param[in] offset The starting index to use when attempting to decode the raw data.
## @param[in] nbits The number of data bits to expect.
## @param[in] strict Flag indicating if we should perform strict matching.
## @param[in] _tolerance The tolerance percentage for matching (default 25%)
## @return A boolean. True if it can decode it, false if it can't.
## Direct translation from IRremoteESP8266 IRrecv::decodeGree (ir_Gree.cpp lines 697-751)
def decodeGree(
    results, offset: int = 1, nbits: int = kGreeBits, strict: bool = True, _tolerance: int = 25
) -> bool:
    """
    Decode a Gree HVAC IR message.
    EXACT translation from IRremoteESP8266 IRrecv::decodeGree

    This is the ACTUAL C++ decoder function, not a wrapper.
    """
    # Import here to avoid circular imports
    from app.core.ir_protocols.ir_recv import (
        kHeader,
        kFooter,
        kMarkExcess,
        _matchGeneric,
        matchData,
        match_result_t,
    )

    if results.rawlen <= 2 * (nbits + kGreeBlockFooterBits) + (kHeader + kFooter + 1) - 1 + offset:
        return False  # Can't possibly be a valid Gree message.
    if strict and nbits != kGreeBits:
        return False  # Not strictly a Gree message.

    # There are two blocks back-to-back in a full Gree IR message sequence.

    # Header + Data Block #1 (32 bits)
    used = _matchGeneric(
        data_ptr=results.rawbuf[offset:],
        result_bits_ptr=None,
        result_bytes_ptr=results.state,
        use_bits=False,
        remaining=results.rawlen - offset,
        nbits=nbits // 2,  # 32 bits for first block
        hdrmark=kGreeHdrMark,
        hdrspace=kGreeHdrSpace,
        onemark=kGreeBitMark,
        onespace=kGreeOneSpace,
        zeromark=kGreeBitMark,
        zerospace=kGreeZeroSpace,
        footermark=0,
        footerspace=0,
        atleast=False,
        tolerance=_tolerance,
        excess=kMarkExcess,
        MSBfirst=False,
    )
    if used == 0:
        return False
    offset += used

    # Block #1 footer (3 bits, B010)
    data_result = matchData(
        data_ptr=results.rawbuf[offset:],
        offset=0,
        nbits=kGreeBlockFooterBits,
        onemark=kGreeBitMark,
        onespace=kGreeOneSpace,
        zeromark=kGreeBitMark,
        zerospace=kGreeZeroSpace,
        tolerance=_tolerance,
        excess=kMarkExcess,
        MSBfirst=False,
        expectlastspace=True,
    )
    if data_result.success == False:
        return False
    if data_result.data != kGreeBlockFooter:
        return False
    offset += data_result.used

    # Inter-block gap + Data Block #2 (32 bits) + Footer
    if not _matchGeneric(
        data_ptr=results.rawbuf[offset:],
        result_bits_ptr=None,
        result_bytes_ptr=results.state[4:],  # Start at byte 4
        use_bits=False,
        remaining=results.rawlen - offset,
        nbits=nbits // 2,  # 32 bits for second block
        hdrmark=kGreeBitMark,
        hdrspace=kGreeMsgSpace,
        onemark=kGreeBitMark,
        onespace=kGreeOneSpace,
        zeromark=kGreeBitMark,
        zerospace=kGreeZeroSpace,
        footermark=kGreeBitMark,
        footerspace=kGreeMsgSpace,
        atleast=True,
        tolerance=_tolerance,
        excess=kMarkExcess,
        MSBfirst=False,
    ):
        return False

    # Compliance
    if strict:
        # Verify the message's checksum is correct.
        if not IRGreeAC.validChecksum(results.state):
            return False

    # Success
    # results.decode_type = GREE  # Would set protocol type in C++
    results.bits = nbits
    # No need to record the state as we stored it as we decoded it.
    # As we use result->state, we don't record value, address, or command as it
    # is a union data type.
    return True
