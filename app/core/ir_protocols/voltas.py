# Copyright 2020 David Conran (crankyoldgit)
# Copyright 2020 manj9501
# Python translation: Direct conversion from C++ with NO optimizations

## @file
## @brief Support for Voltas A/C protocol
## Direct translation from IRremoteESP8266 ir_Voltas.cpp and ir_Voltas.h

from typing import List

# Supports:
#   Brand: Voltas,  Model: 122LZF 4011252 Window A/C

# Ref: https://github.com/crankyoldgit/IRremoteESP8266/issues/1238
# Ref: https://docs.google.com/spreadsheets/d/1zzDEUQ52y7MZ7_xCU3pdjdqbRXOwZLsbTGvKWcicqCI/
# Ref: https://www.corona.co.jp/box/download.php?id=145060636229

# Constants - Timing values (from ir_Voltas.cpp lines 24-27)
kVoltasBitMark = 1026  # uSeconds.
kVoltasOneSpace = 2553  # uSeconds.
kVoltasZeroSpace = 554  # uSeconds.
kVoltasFreq = 38000  # Hz.

# State length constants
kVoltasStateLength = 10  # 10 bytes
kVoltasBits = kVoltasStateLength * 8  # 80 bits

# Constants (from ir_Voltas.h lines 75-87)
kVoltasFan = 0b0001  # 1
kVoltasHeat = 0b0010  # 2
kVoltasDry = 0b0100  # 4
kVoltasCool = 0b1000  # 8
kVoltasMinTemp = 16  # Celsius
kVoltasDryTemp = 24  # Celsius
kVoltasMaxTemp = 30  # Celsius
kVoltasFanHigh = 0b001  # 1
kVoltasFanMed = 0b010  # 2
kVoltasFanLow = 0b100  # 4
kVoltasFanAuto = 0b111  # 7
kVoltasSwingHChange = 0b1111100  # 0x7D
kVoltasSwingHNoChange = 0b0011001  # 0x19

# Model enums (from IRsend.h lines 205-208)
kVoltasUnknown = 0  # Full Function
kVoltas122LZF = 1  # (1) 122LZF (No SwingH support) (Default)

# Repeat constants
kNoRepeat = 0
kDefaultMessageGap = 100000


def sumBytes(data: List[int], length: int) -> int:
    """
    Sum all bytes in the array up to length.
    Helper function for checksum calculation.
    """
    result = 0
    for i in range(length):
        result += data[i]
    return result & 0xFF


## Native representation of a Voltas A/C message.
## This is a direct translation of the C++ union/struct (from ir_Voltas.h lines 29-72)
class VoltasProtocol:
    def __init__(self):
        # The state array (10 bytes for Voltas)
        self.raw = [0] * kVoltasStateLength

    # Byte 0
    @property
    def SwingH(self) -> int:
        return self.raw[0] & 0x01

    @SwingH.setter
    def SwingH(self, value: bool) -> None:
        if value:
            self.raw[0] |= 0x01
        else:
            self.raw[0] &= 0xFE

    @property
    def SwingHChange(self) -> int:
        return (self.raw[0] >> 1) & 0x7F

    @SwingHChange.setter
    def SwingHChange(self, value: int) -> None:
        self.raw[0] = (self.raw[0] & 0x01) | ((value & 0x7F) << 1)

    # Byte 1
    @property
    def Mode(self) -> int:
        return self.raw[1] & 0x0F

    @Mode.setter
    def Mode(self, value: int) -> None:
        self.raw[1] = (self.raw[1] & 0xF0) | (value & 0x0F)

    @property
    def FanSpeed(self) -> int:
        return (self.raw[1] >> 5) & 0x07

    @FanSpeed.setter
    def FanSpeed(self, value: int) -> None:
        self.raw[1] = (self.raw[1] & 0x1F) | ((value & 0x07) << 5)

    # Byte 2
    @property
    def SwingV(self) -> int:
        return self.raw[2] & 0x07

    @SwingV.setter
    def SwingV(self, value: int) -> None:
        self.raw[2] = (self.raw[2] & 0xF8) | (value & 0x07)

    @property
    def Wifi(self) -> int:
        return (self.raw[2] >> 3) & 0x01

    @Wifi.setter
    def Wifi(self, value: bool) -> None:
        if value:
            self.raw[2] |= 0x08
        else:
            self.raw[2] &= 0xF7

    @property
    def Turbo(self) -> int:
        return (self.raw[2] >> 5) & 0x01

    @Turbo.setter
    def Turbo(self, value: bool) -> None:
        if value:
            self.raw[2] |= 0x20
        else:
            self.raw[2] &= 0xDF

    @property
    def Sleep(self) -> int:
        return (self.raw[2] >> 6) & 0x01

    @Sleep.setter
    def Sleep(self, value: bool) -> None:
        if value:
            self.raw[2] |= 0x40
        else:
            self.raw[2] &= 0xBF

    @property
    def Power(self) -> int:
        return (self.raw[2] >> 7) & 0x01

    @Power.setter
    def Power(self, value: bool) -> None:
        if value:
            self.raw[2] |= 0x80
        else:
            self.raw[2] &= 0x7F

    # Byte 3
    @property
    def Temp(self) -> int:
        return self.raw[3] & 0x0F

    @Temp.setter
    def Temp(self, value: int) -> None:
        self.raw[3] = (self.raw[3] & 0xF0) | (value & 0x0F)

    @property
    def Econo(self) -> int:
        return (self.raw[3] >> 6) & 0x01

    @Econo.setter
    def Econo(self, value: bool) -> None:
        if value:
            self.raw[3] |= 0x40
        else:
            self.raw[3] &= 0xBF

    @property
    def TempSet(self) -> int:
        return (self.raw[3] >> 7) & 0x01

    @TempSet.setter
    def TempSet(self, value: bool) -> None:
        if value:
            self.raw[3] |= 0x80
        else:
            self.raw[3] &= 0x7F

    # Byte 4
    @property
    def OnTimerMins(self) -> int:
        return self.raw[4] & 0x3F

    @OnTimerMins.setter
    def OnTimerMins(self, value: int) -> None:
        self.raw[4] = (self.raw[4] & 0xC0) | (value & 0x3F)

    @property
    def OnTimer12Hr(self) -> int:
        return (self.raw[4] >> 7) & 0x01

    @OnTimer12Hr.setter
    def OnTimer12Hr(self, value: int) -> None:
        if value:
            self.raw[4] |= 0x80
        else:
            self.raw[4] &= 0x7F

    # Byte 5
    @property
    def OffTimerMins(self) -> int:
        return self.raw[5] & 0x3F

    @OffTimerMins.setter
    def OffTimerMins(self, value: int) -> None:
        self.raw[5] = (self.raw[5] & 0xC0) | (value & 0x3F)

    @property
    def OffTimer12Hr(self) -> int:
        return (self.raw[5] >> 7) & 0x01

    @OffTimer12Hr.setter
    def OffTimer12Hr(self, value: int) -> None:
        if value:
            self.raw[5] |= 0x80
        else:
            self.raw[5] &= 0x7F

    # Byte 6 - Typically 0b00111011(0x3B)

    # Byte 7
    @property
    def OnTimerHrs(self) -> int:
        return self.raw[7] & 0x0F

    @OnTimerHrs.setter
    def OnTimerHrs(self, value: int) -> None:
        self.raw[7] = (self.raw[7] & 0xF0) | (value & 0x0F)

    @property
    def OffTimerHrs(self) -> int:
        return (self.raw[7] >> 4) & 0x0F

    @OffTimerHrs.setter
    def OffTimerHrs(self, value: int) -> None:
        self.raw[7] = (self.raw[7] & 0x0F) | ((value & 0x0F) << 4)

    # Byte 8
    @property
    def Light(self) -> int:
        return (self.raw[8] >> 5) & 0x01

    @Light.setter
    def Light(self, value: bool) -> None:
        if value:
            self.raw[8] |= 0x20
        else:
            self.raw[8] &= 0xDF

    @property
    def OffTimerEnable(self) -> int:
        return (self.raw[8] >> 6) & 0x01

    @OffTimerEnable.setter
    def OffTimerEnable(self, value: bool) -> None:
        if value:
            self.raw[8] |= 0x40
        else:
            self.raw[8] &= 0xBF

    @property
    def OnTimerEnable(self) -> int:
        return (self.raw[8] >> 7) & 0x01

    @OnTimerEnable.setter
    def OnTimerEnable(self, value: bool) -> None:
        if value:
            self.raw[8] |= 0x80
        else:
            self.raw[8] &= 0x7F

    # Byte 9
    @property
    def Checksum(self) -> int:
        return self.raw[9]

    @Checksum.setter
    def Checksum(self, value: int) -> None:
        self.raw[9] = value & 0xFF


## Send a Voltas formatted message.
## Status: STABLE / Working on real device.
## @param[in] data An array of bytes containing the IR command.
## @param[in] nbytes Nr. of bytes of data in the array. (>=kVoltasStateLength)
## @param[in] repeat Nr. of times the message is to be repeated.
## Direct translation from IRremoteESP8266 IRsend::sendVoltas (ir_Voltas.cpp lines 29-49)
def sendVoltas(data: List[int], nbytes: int = kVoltasStateLength, repeat: int = 0) -> List[int]:
    """
    Send a Voltas formatted message.
    EXACT translation from IRremoteESP8266 IRsend::sendVoltas

    Returns timing array instead of transmitting via hardware.
    """
    # Import here to avoid circular import
    from app.core.ir_protocols.ir_send import sendGeneric

    timings = sendGeneric(
        headermark=0,
        headerspace=0,  # No header
        onemark=kVoltasBitMark,
        onespace=kVoltasOneSpace,
        zeromark=kVoltasBitMark,
        zerospace=kVoltasZeroSpace,
        footermark=kVoltasBitMark,
        gap=kDefaultMessageGap,
        dataptr=data,
        nbytes=nbytes,
        frequency=kVoltasFreq,
        MSBfirst=True,
        repeat=repeat,
        dutycycle=50
    )
    return timings


## Class for handling detailed Voltas A/C messages.
## Direct translation from C++ IRVoltas class (from ir_Voltas.h lines 91-161)
class IRVoltas:
    ## Class Constructor
    ## @param[in] pin GPIO to be used when sending. (Not used in Python)
    ## @param[in] inverted Is the output signal to be inverted? (Not used in Python)
    ## @param[in] use_modulation Is frequency modulation to be used? (Not used in Python)
    ## Direct translation from ir_Voltas.cpp lines 83-91
    def __init__(self) -> None:
        self._: VoltasProtocol = VoltasProtocol()
        self._model: int = kVoltas122LZF
        self.stateReset()

    ## Reset the internal state to a fixed known good state.
    ## Direct translation from ir_Voltas.cpp lines 93-100
    def stateReset(self) -> None:
        # This resets to a known-good state.
        # ref: https://github.com/crankyoldgit/IRremoteESP8266/issues/1238#issuecomment-674699746
        kReset = [0x33, 0x28, 0x00, 0x17, 0x3B, 0x3B, 0x3B, 0x11, 0x00, 0xCB]
        self.setRaw(kReset)

    ## Get the model information currently known.
    ## @param[in] raw Work out the model info from the current raw state.
    ## @return The known model number.
    ## Direct translation from ir_Voltas.cpp lines 113-127
    def getModel(self, raw: bool = False) -> int:
        if raw:
            if self._.SwingHChange == kVoltasSwingHNoChange:
                return kVoltas122LZF
            else:
                return kVoltasUnknown
        else:
            return self._model

    ## Set the current model for the remote.
    ## @param[in] model The model number.
    ## Direct translation from ir_Voltas.cpp lines 129-139
    def setModel(self, model: int) -> None:
        if model == kVoltas122LZF:
            self._model = model
            self.setSwingHChange(False)
        else:
            self._model = kVoltasUnknown

    ## Get a PTR to the internal state/code for this protocol.
    ## @return PTR to a code for this protocol based on the current internal state.
    ## Direct translation from ir_Voltas.cpp lines 141-146
    def getRaw(self) -> List[int]:
        self.checksum()  # Ensure correct settings before sending.
        return self._.raw

    ## Set the internal state from a valid code for this protocol.
    ## @param[in] new_code A valid code for this protocol.
    ## Direct translation from ir_Voltas.cpp lines 148-153
    def setRaw(self, new_code: List[int]) -> None:
        for i in range(min(len(new_code), kVoltasStateLength)):
            self._.raw[i] = new_code[i]
        self.setModel(self.getModel(True))

    ## Calculate and set the checksum values for the internal state.
    ## Direct translation from ir_Voltas.cpp lines 155-158
    def checksum(self) -> None:
        self._.Checksum = self.calcChecksum(self._.raw)

    ## Verify the checksum is valid for a given state.
    ## @param[in] state The array to verify the checksum of.
    ## @param[in] length The length of the state array.
    ## @return true, if the state has a valid checksum. Otherwise, false.
    ## Direct translation from ir_Voltas.cpp lines 160-167
    @staticmethod
    def validChecksum(state: List[int], length: int = kVoltasStateLength) -> bool:
        if length:
            return state[length - 1] == IRVoltas.calcChecksum(state, length)
        return True

    ## Calculate the checksum is valid for a given state.
    ## @param[in] state The array to calculate the checksum of.
    ## @param[in] length The length of the state array.
    ## @return The valid checksum value for the state.
    ## Direct translation from ir_Voltas.cpp lines 169-178
    @staticmethod
    def calcChecksum(state: List[int], length: int = kVoltasStateLength) -> int:
        result = 0
        if length:
            result = sumBytes(state, length - 1)
        return (~result) & 0xFF

    ## Change the power setting to On.
    ## Direct translation from ir_Voltas.cpp line 181
    def on(self) -> None:
        self.setPower(True)

    ## Change the power setting to Off.
    ## Direct translation from ir_Voltas.cpp line 184
    def off(self) -> None:
        self.setPower(False)

    ## Change the power setting.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Voltas.cpp line 188
    def setPower(self, on: bool) -> None:
        self._.Power = on

    ## Get the value of the current power setting.
    ## @return true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Voltas.cpp line 192
    def getPower(self) -> bool:
        return bool(self._.Power)

    ## Set the operating mode of the A/C.
    ## @param[in] mode The desired operating mode.
    ## @note If we get an unexpected mode, default to AUTO.
    ## Direct translation from ir_Voltas.cpp lines 194-218
    def setMode(self, mode: int) -> None:
        self._.Mode = mode
        if mode == kVoltasFan:
            self.setFan(self.getFan())  # Force the fan speed to a correct one fo the mode.
        elif mode == kVoltasDry:
            self.setFan(kVoltasFanLow)
            self.setTemp(kVoltasDryTemp)
        elif mode == kVoltasHeat or mode == kVoltasCool:
            pass
        else:
            self.setMode(kVoltasCool)
            return
        # Reset some settings if needed.
        self.setEcono(self.getEcono())
        self.setTurbo(self.getTurbo())
        self.setSleep(self.getSleep())

    ## Get the operating mode setting of the A/C.
    ## @return The current operating mode setting.
    ## Direct translation from ir_Voltas.cpp line 222
    def getMode(self) -> int:
        return self._.Mode

    ## Convert a stdAc::opmode_t enum into its native mode.
    ## @param[in] mode The enum to be converted.
    ## @return The native equivalent of the enum.
    ## Direct translation from ir_Voltas.cpp lines 224-234
    def convertMode(self, mode: int) -> int:
        # stdAc::opmode_t values (approximated):
        # kHeat = 2, kDry = 3, kFan = 4, kCool = 1
        if mode == 2:  # kHeat
            return kVoltasHeat
        elif mode == 3:  # kDry
            return kVoltasDry
        elif mode == 4:  # kFan
            return kVoltasFan
        else:
            return kVoltasCool

    ## Convert a native mode into its stdAc equivalent.
    ## @param[in] mode The native setting to be converted.
    ## @return The stdAc equivalent of the native setting.
    ## Direct translation from ir_Voltas.cpp lines 236-246
    @staticmethod
    def toCommonMode(mode: int) -> int:
        if mode == kVoltasHeat:
            return 2  # stdAc::opmode_t::kHeat
        elif mode == kVoltasDry:
            return 3  # stdAc::opmode_t::kDry
        elif mode == kVoltasFan:
            return 4  # stdAc::opmode_t::kFan
        else:
            return 1  # stdAc::opmode_t::kCool

    ## Set the temperature.
    ## @param[in] temp The temperature in degrees celsius.
    ## Direct translation from ir_Voltas.cpp lines 248-254
    def setTemp(self, temp: int) -> None:
        new_temp = max(kVoltasMinTemp, temp)
        new_temp = min(kVoltasMaxTemp, new_temp)
        self._.Temp = new_temp - kVoltasMinTemp

    ## Get the current temperature setting.
    ## @return The current setting for temp. in degrees celsius.
    ## Direct translation from ir_Voltas.cpp line 258
    def getTemp(self) -> int:
        return self._.Temp + kVoltasMinTemp

    ## Set the speed of the fan.
    ## @param[in] fan The desired setting.
    ## Direct translation from ir_Voltas.cpp lines 260-278
    def setFan(self, fan: int) -> None:
        if fan == kVoltasFanAuto:
            if self._.Mode == kVoltasFan:  # Auto speed is not available in fan mode.
                self.setFan(kVoltasFanHigh)
                return
            # FALL-THRU
        if fan in [kVoltasFanAuto, kVoltasFanLow, kVoltasFanMed, kVoltasFanHigh]:
            self._.FanSpeed = fan
        else:
            self.setFan(kVoltasFanAuto)

    ## Get the current fan speed setting.
    ## @return The current fan speed/mode.
    ## Direct translation from ir_Voltas.cpp line 282
    def getFan(self) -> int:
        return self._.FanSpeed

    ## Convert a stdAc::fanspeed_t enum into it's native speed.
    ## @param[in] speed The enum to be converted.
    ## @return The native equivalent of the enum.
    ## Direct translation from ir_Voltas.cpp lines 284-296
    def convertFan(self, speed: int) -> int:
        # stdAc::fanspeed_t values (approximated):
        # kMin = 1, kLow = 2, kMedium = 3, kHigh = 4, kMax = 5, kAuto = 0
        if speed in [1, 2]:  # kMin, kLow
            return kVoltasFanLow
        elif speed == 3:  # kMedium
            return kVoltasFanMed
        elif speed in [4, 5]:  # kHigh, kMax
            return kVoltasFanHigh
        else:
            return kVoltasFanAuto

    ## Convert a native fan speed into its stdAc equivalent.
    ## @param[in] spd The native setting to be converted.
    ## @return The stdAc equivalent of the native setting.
    ## Direct translation from ir_Voltas.cpp lines 298-308
    @staticmethod
    def toCommonFanSpeed(spd: int) -> int:
        if spd == kVoltasFanHigh:
            return 5  # stdAc::fanspeed_t::kMax
        elif spd == kVoltasFanMed:
            return 3  # stdAc::fanspeed_t::kMedium
        elif spd == kVoltasFanLow:
            return 1  # stdAc::fanspeed_t::kMin
        else:
            return 0  # stdAc::fanspeed_t::kAuto

    ## Set the Vertical Swing setting of the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Voltas.cpp line 312
    def setSwingV(self, on: bool) -> None:
        self._.SwingV = 0b111 if on else 0b000

    ## Get the Vertical Swing setting of the A/C.
    ## @return true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Voltas.cpp line 316
    def getSwingV(self) -> bool:
        return self._.SwingV == 0b111

    ## Set the Horizontal Swing setting of the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Voltas.cpp lines 318-328
    def setSwingH(self, on: bool) -> None:
        if self._model == kVoltas122LZF:
            pass  # unsupported on these models.
        else:
            self._.SwingH = on
            self.setSwingHChange(True)

    ## Get the Horizontal Swing setting of the A/C.
    ## @return true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Voltas.cpp lines 330-339
    def getSwingH(self) -> bool:
        if self._model == kVoltas122LZF:
            return False  # unsupported on these models.
        else:
            return bool(self._.SwingH)

    ## Set the bits for changing the Horizontal Swing setting of the A/C.
    ## @param[in] on true, the change bits are set. false, the "no change" bits are set.
    ## Direct translation from ir_Voltas.cpp lines 341-347
    def setSwingHChange(self, on: bool) -> None:
        self._.SwingHChange = kVoltasSwingHChange if on else kVoltasSwingHNoChange
        if not on:
            self._.SwingH = True  # "No Change" also sets SwingH to 1.

    ## Are the Horizontal Swing change bits set in the message?
    ## @return true, the correct bits are set. false, the correct bits are not set.
    ## Direct translation from ir_Voltas.cpp lines 349-353
    def getSwingHChange(self) -> bool:
        return self._.SwingHChange == kVoltasSwingHChange

    ## Change the Wifi setting.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Voltas.cpp line 357
    def setWifi(self, on: bool) -> None:
        self._.Wifi = on

    ## Get the value of the current Wifi setting.
    ## @return true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Voltas.cpp line 361
    def getWifi(self) -> bool:
        return bool(self._.Wifi)

    ## Change the Turbo setting.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## @note The Turbo setting is only available in Cool mode.
    ## Direct translation from ir_Voltas.cpp lines 363-371
    def setTurbo(self, on: bool) -> None:
        if on and self._.Mode == kVoltasCool:
            self._.Turbo = True
        else:
            self._.Turbo = False

    ## Get the value of the current Turbo setting.
    ## @return true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Voltas.cpp line 375
    def getTurbo(self) -> bool:
        return bool(self._.Turbo)

    ## Change the Economy setting.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## @note The Economy setting is only available in Cool mode.
    ## Direct translation from ir_Voltas.cpp lines 377-385
    def setEcono(self, on: bool) -> None:
        if on and self._.Mode == kVoltasCool:
            self._.Econo = True
        else:
            self._.Econo = False

    ## Get the value of the current Econo setting.
    ## @return true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Voltas.cpp line 389
    def getEcono(self) -> bool:
        return bool(self._.Econo)

    ## Change the Light setting.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Voltas.cpp line 393
    def setLight(self, on: bool) -> None:
        self._.Light = on

    ## Get the value of the current Light setting.
    ## @return true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Voltas.cpp line 397
    def getLight(self) -> bool:
        return bool(self._.Light)

    ## Change the Sleep setting.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## @note The Sleep setting is only available in Cool mode.
    ## Direct translation from ir_Voltas.cpp lines 399-407
    def setSleep(self, on: bool) -> None:
        if on and self._.Mode == kVoltasCool:
            self._.Sleep = True
        else:
            self._.Sleep = False

    ## Get the value of the current Sleep setting.
    ## @return true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Voltas.cpp line 411
    def getSleep(self) -> bool:
        return bool(self._.Sleep)

    ## Get the value of the On Timer time.
    ## @return Number of minutes before the timer activates.
    ## Direct translation from ir_Voltas.cpp lines 413-418
    def getOnTime(self) -> int:
        return min(12 * self._.OnTimer12Hr + self._.OnTimerHrs - 1, 23) * 60 + self._.OnTimerMins

    ## Set the value of the On Timer time.
    ## @param[in] nr_of_mins Number of minutes before the timer activates.
    ## 0 disables the timer. Max is 23 hrs & 59 mins (1439 mins)
    ## Direct translation from ir_Voltas.cpp lines 420-431
    def setOnTime(self, nr_of_mins: int) -> None:
        # Cap the total number of mins.
        mins = min(nr_of_mins, 23 * 60 + 59)
        hrs = (mins // 60) + 1
        self._.OnTimerMins = mins % 60
        self._.OnTimer12Hr = hrs // 12
        self._.OnTimerHrs = hrs % 12
        self._.OnTimerEnable = (mins > 0)  # Is the timer is to be enabled?

    ## Get the value of the On Timer time.
    ## @return Number of minutes before the timer activates.
    ## Direct translation from ir_Voltas.cpp lines 433-438
    def getOffTime(self) -> int:
        return min(12 * self._.OffTimer12Hr + self._.OffTimerHrs - 1, 23) * 60 + self._.OffTimerMins

    ## Set the value of the Off Timer time.
    ## @param[in] nr_of_mins Number of minutes before the timer activates.
    ## 0 disables the timer. Max is 23 hrs & 59 mins (1439 mins)
    ## Direct translation from ir_Voltas.cpp lines 440-451
    def setOffTime(self, nr_of_mins: int) -> None:
        # Cap the total number of mins.
        mins = min(nr_of_mins, 23 * 60 + 59)
        hrs = (mins // 60) + 1
        self._.OffTimerMins = mins % 60
        self._.OffTimer12Hr = hrs // 12
        self._.OffTimerHrs = hrs % 12
        self._.OffTimerEnable = (mins > 0)  # Is the timer is to be enabled?

    ## Convert the current internal state into its stdAc::state_t equivalent.
    ## @param[in] prev Ptr to the previous state if available.
    ## @return The stdAc equivalent of the native settings.
    ## Direct translation from ir_Voltas.cpp lines 453-487
    def toCommon(self, prev: dict = None) -> dict:
        result = {}
        # Start with the previous state if given it.
        if prev is not None:
            result = prev.copy()
        else:
            # Set defaults for non-zero values that are not implicitly set for when
            # there is no previous state.
            result['swingh'] = 0  # stdAc::swingh_t::kOff
        result['model'] = self.getModel()
        result['protocol'] = 'VOLTAS'
        result['power'] = bool(self._.Power)
        result['mode'] = self.toCommonMode(self._.Mode)
        result['celsius'] = True
        result['degrees'] = self.getTemp()
        result['fanspeed'] = self.toCommonFanSpeed(self._.FanSpeed)
        result['swingv'] = 1 if self.getSwingV() else 0  # kAuto : kOff
        if self.getSwingHChange():
            result['swingh'] = 1 if self._.SwingH else 0  # kAuto : kOff
        result['turbo'] = bool(self._.Turbo)
        result['econo'] = bool(self._.Econo)
        result['light'] = bool(self._.Light)
        result['sleep'] = 0 if self._.Sleep else -1
        # Not supported.
        result['quiet'] = False
        result['filter'] = False
        result['clean'] = False
        result['beep'] = False
        result['clock'] = -1
        return result

    ## Convert the current internal state into a human readable string.
    ## @return A human readable string.
    ## Direct translation from ir_Voltas.cpp lines 489-516
    def toString(self) -> str:
        result = ""
        result += "Model: " + str(self.getModel()) + ", "
        result += "Power: " + ("On" if self._.Power else "Off") + ", "
        result += "Mode: " + str(self._.Mode) + ", "
        result += "Temp: " + str(self.getTemp()) + "C, "
        result += "Fan: " + str(self._.FanSpeed) + ", "
        result += "SwingV: " + ("On" if self.getSwingV() else "Off") + ", "
        if self.getSwingHChange():
            result += "SwingH: " + ("On" if self._.SwingH else "Off") + ", "
        else:
            result += "SwingH: N/A, "
        result += "Turbo: " + ("On" if self._.Turbo else "Off") + ", "
        result += "Econo: " + ("On" if self._.Econo else "Off") + ", "
        result += "Wifi: " + ("On" if self._.Wifi else "Off") + ", "
        result += "Light: " + ("On" if self._.Light else "Off") + ", "
        result += "Sleep: " + ("On" if self._.Sleep else "Off") + ", "
        result += "On Timer: " + (str(self.getOnTime()) + "m" if self._.OnTimerEnable else "Off") + ", "
        result += "Off Timer: " + (str(self.getOffTime()) + "m" if self._.OffTimerEnable else "Off")
        return result


## Decode the supplied Voltas message.
## Status: STABLE / Working on real device.
## @param[in,out] results Ptr to the data to decode & where to store the decode
## @param[in] offset The starting index to use when attempting to decode the raw data.
## @param[in] nbits The number of data bits to expect.
## @param[in] strict Flag indicating if we should perform strict matching.
## @return A boolean. True if it can decode it, false if it can't.
## Direct translation from IRremoteESP8266 IRrecv::decodeVoltas (ir_Voltas.cpp lines 52-81)
def decodeVoltas(results, offset: int = 1, nbits: int = kVoltasBits,
                 strict: bool = True) -> bool:
    """
    Decode a Voltas IR message.
    EXACT translation from IRremoteESP8266 IRrecv::decodeVoltas

    This is the ACTUAL C++ decoder function, not a wrapper.
    """
    # Import here to avoid circular imports
    from app.core.ir_protocols.ir_recv import kMarkExcess, _matchGeneric

    if strict and nbits != kVoltasBits:
        return False

    # Data + Footer (from ir_Voltas.cpp lines 65-71)
    if not _matchGeneric(
        data_ptr=results.rawbuf[offset:],
        result_bits_ptr=None,
        result_bytes_ptr=results.state,
        use_bits=False,
        remaining=results.rawlen - offset,
        nbits=nbits,
        hdrmark=0,
        hdrspace=0,  # No header
        onemark=kVoltasBitMark,
        onespace=kVoltasOneSpace,
        zeromark=kVoltasBitMark,
        zerospace=kVoltasZeroSpace,
        footermark=kVoltasBitMark,
        footerspace=kDefaultMessageGap,
        atleast=True,
        tolerance=25,
        excess=kMarkExcess,
        MSBfirst=True
    ):
        return False

    # Compliance (from ir_Voltas.cpp lines 73-75)
    if strict and not IRVoltas.validChecksum(results.state, nbits // 8):
        return False

    # Success (from ir_Voltas.cpp lines 76-79)
    # results.decode_type = decode_type_t::VOLTAS;
    results.bits = nbits
    return True
