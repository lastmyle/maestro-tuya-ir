# Copyright 2017 bwze, crankyoldgit
# Python translation: Direct conversion from C++ with NO optimizations

## @file
## @brief Support for Midea A/C protocols (MIDEA and MIDEA24).
## Direct translation from IRremoteESP8266 ir_Midea.cpp and ir_Midea.h

from typing import List

# Constants - Timing values for MIDEA protocol (from ir_Midea.cpp lines 22-36)
kMideaTick = 80
kMideaBitMarkTicks = 7
kMideaBitMark = kMideaBitMarkTicks * kMideaTick  # 560us
kMideaOneSpaceTicks = 21
kMideaOneSpace = kMideaOneSpaceTicks * kMideaTick  # 1680us
kMideaZeroSpaceTicks = 7
kMideaZeroSpace = kMideaZeroSpaceTicks * kMideaTick  # 560us
kMideaHdrMarkTicks = 56
kMideaHdrMark = kMideaHdrMarkTicks * kMideaTick  # 4480us
kMideaHdrSpaceTicks = 56
kMideaHdrSpace = kMideaHdrSpaceTicks * kMideaTick  # 4480us
kMideaMinGapTicks = kMideaHdrMarkTicks + kMideaZeroSpaceTicks + kMideaBitMarkTicks
kMideaMinGap = kMideaMinGapTicks * kMideaTick  # 5040us
kMideaTolerance = 30  # Percent
kMidea24MinGap = 13000  # uSecs

# State length constants
kMideaBits = 48
kMidea24Bits = 24

# Temperature constants (from ir_Midea.h lines 110-118)
kMideaACMinTempF = 62        # Fahrenheit
kMideaACMaxTempF = 86        # Fahrenheit
kMideaACMinTempC = 17        # Celsius
kMideaACMaxTempC = 30        # Celsius
kMideaACMinSensorTempC = 0   # Celsius
kMideaACMaxSensorTempC = 37  # Celsius
kMideaACMinSensorTempF = 32  # Fahrenheit
kMideaACMaxSensorTempF = 99  # Fahrenheit (Guess only!)
kMideaACSensorTempOnTimerOff = 0b1111111
kMideaACTimerOff = 0b111111

# Mode constants (from ir_Midea.h lines 120-124)
kMideaACCool = 0  # 0b000
kMideaACDry = 1   # 0b001
kMideaACAuto = 2  # 0b010
kMideaACHeat = 3  # 0b011
kMideaACFan = 4   # 0b100

# Fan speed constants (from ir_Midea.h lines 125-128)
kMideaACFanAuto = 0  # 0b00
kMideaACFanLow = 1   # 0b01
kMideaACFanMed = 2   # 0b10
kMideaACFanHigh = 3  # 0b11

# Special toggle commands (from ir_Midea.h lines 131-150)
kMideaACToggleSwingV = 0xA201FFFFFF7C
kMideaACToggleEcono = 0xA202FFFFFF7E
kMideaACToggleLight = 0xA208FFFFFF75
kMideaACToggleTurbo = 0xA209FFFFFF74
kMideaACToggleSelfClean = 0xA20DFFFFFF70
kMideaACToggle8CHeat = 0xA20FFFFFFF73
kMideaACQuietOn = 0xA212FFFFFF6E
kMideaACQuietOff = 0xA213FFFFFF6F

# Message type constants (from ir_Midea.h lines 151-153)
kMideaACTypeCommand = 0b001
kMideaACTypeSpecial = 0b010
kMideaACTypeFollow = 0b100


def reverseBits(data: int, nbits: int) -> int:
    """Reverse bits in a value. EXACT translation from IRutils."""
    result = 0
    for i in range(nbits):
        result <<= 1
        result |= (data & 1)
        data >>= 1
    return result & ((1 << nbits) - 1)


def GETBITS64(data: int, offset: int, nbits: int) -> int:
    """Extract bits from uint64. EXACT translation from IRutils."""
    mask = (1 << nbits) - 1
    return (data >> offset) & mask


def fahrenheitToCelsius(temp: float) -> float:
    """Convert Fahrenheit to Celsius"""
    return (temp - 32.0) / 1.8


def celsiusToFahrenheit(temp: float) -> float:
    """Convert Celsius to Fahrenheit"""
    return temp * 1.8 + 32.0


## Native representation of a Midea A/C message.
## Direct translation of the C++ union/struct (ir_Midea.h lines 71-107)
class MideaProtocol:
    def __init__(self):
        # The state in native IR code form (64-bit, only 48 bits used)
        self.remote_state = 0

    # Byte 0 - Sum (checksum)
    @property
    def Sum(self) -> int:
        return self.remote_state & 0xFF

    @Sum.setter
    def Sum(self, value: int) -> None:
        self.remote_state = (self.remote_state & ~0xFF) | (value & 0xFF)

    # Byte 1 - SensorTemp / OnTimer (bits 0-6)
    @property
    def SensorTemp(self) -> int:
        return (self.remote_state >> 8) & 0x7F

    @SensorTemp.setter
    def SensorTemp(self, value: int) -> None:
        self.remote_state = (self.remote_state & ~(0x7F << 8)) | ((value & 0x7F) << 8)

    # Byte 1 - disableSensor (bit 7)
    @property
    def disableSensor(self) -> int:
        return (self.remote_state >> 15) & 0x01

    @disableSensor.setter
    def disableSensor(self, value: bool) -> None:
        if value:
            self.remote_state |= (1 << 15)
        else:
            self.remote_state &= ~(1 << 15)

    # Byte 2 - OffTimer (bits 1-6)
    @property
    def OffTimer(self) -> int:
        return (self.remote_state >> 17) & 0x3F

    @OffTimer.setter
    def OffTimer(self, value: int) -> None:
        self.remote_state = (self.remote_state & ~(0x3F << 17)) | ((value & 0x3F) << 17)

    # Byte 2 - BeepDisable (bit 7)
    @property
    def BeepDisable(self) -> int:
        return (self.remote_state >> 23) & 0x01

    @BeepDisable.setter
    def BeepDisable(self, value: bool) -> None:
        if value:
            self.remote_state |= (1 << 23)
        else:
            self.remote_state &= ~(1 << 23)

    # Byte 3 - Temp (bits 0-4)
    @property
    def Temp(self) -> int:
        return (self.remote_state >> 24) & 0x1F

    @Temp.setter
    def Temp(self, value: int) -> None:
        self.remote_state = (self.remote_state & ~(0x1F << 24)) | ((value & 0x1F) << 24)

    # Byte 3 - useFahrenheit (bit 5)
    @property
    def useFahrenheit(self) -> int:
        return (self.remote_state >> 29) & 0x01

    @useFahrenheit.setter
    def useFahrenheit(self, value: bool) -> None:
        if value:
            self.remote_state |= (1 << 29)
        else:
            self.remote_state &= ~(1 << 29)

    # Byte 4 - Mode (bits 0-2)
    @property
    def Mode(self) -> int:
        return (self.remote_state >> 32) & 0x07

    @Mode.setter
    def Mode(self, value: int) -> None:
        self.remote_state = (self.remote_state & ~(0x07 << 32)) | ((value & 0x07) << 32)

    # Byte 4 - Fan (bits 3-4)
    @property
    def Fan(self) -> int:
        return (self.remote_state >> 35) & 0x03

    @Fan.setter
    def Fan(self, value: int) -> None:
        self.remote_state = (self.remote_state & ~(0x03 << 35)) | ((value & 0x03) << 35)

    # Byte 4 - Sleep (bit 6)
    @property
    def Sleep(self) -> int:
        return (self.remote_state >> 38) & 0x01

    @Sleep.setter
    def Sleep(self, value: bool) -> None:
        if value:
            self.remote_state |= (1 << 38)
        else:
            self.remote_state &= ~(1 << 38)

    # Byte 4 - Power (bit 7)
    @property
    def Power(self) -> int:
        return (self.remote_state >> 39) & 0x01

    @Power.setter
    def Power(self, value: bool) -> None:
        if value:
            self.remote_state |= (1 << 39)
        else:
            self.remote_state &= ~(1 << 39)

    # Byte 5 - Type (bits 0-2)
    @property
    def Type(self) -> int:
        return (self.remote_state >> 40) & 0x07

    @Type.setter
    def Type(self, value: int) -> None:
        self.remote_state = (self.remote_state & ~(0x07 << 40)) | ((value & 0x07) << 40)

    # Byte 5 - Header (bits 3-7)
    @property
    def Header(self) -> int:
        return (self.remote_state >> 43) & 0x1F

    @Header.setter
    def Header(self, value: int) -> None:
        self.remote_state = (self.remote_state & ~(0x1F << 43)) | ((value & 0x1F) << 43)


## Send a Midea message
## Status: Alpha / Needs testing against a real device.
## Direct translation from IRremoteESP8266 IRsend::sendMidea (ir_Midea.cpp lines 54-87)
def sendMidea(data: int, nbits: int = kMideaBits, repeat: int = 0) -> List[int]:
    """
    Send a Midea formatted message.
    EXACT translation from IRremoteESP8266 IRsend::sendMidea

    Returns timing array instead of transmitting via hardware.
    """
    if nbits % 8 != 0:
        return []  # nbits is required to be a multiple of 8

    from app.core.ir_protocols.ir_send import sendData

    all_timings = []

    for r in range(repeat + 1):
        # The protocol sends the message, then follows up with an entirely
        # inverted payload (ir_Midea.cpp lines 63-84)
        for inner_loop in range(2):
            # Header
            all_timings.append(kMideaHdrMark)
            all_timings.append(kMideaHdrSpace)

            # Data - Break data into byte segments, starting at the Most Significant
            # Byte. Each byte then being sent normal, then followed inverted.
            for i in range(8, nbits + 1, 8):
                # Grab a bytes worth of data
                segment = (data >> (nbits - i)) & 0xFF
                segment_timings = sendData(
                    onemark=kMideaBitMark,
                    onespace=kMideaOneSpace,
                    zeromark=kMideaBitMark,
                    zerospace=kMideaZeroSpace,
                    data=segment,
                    nbits=8,
                    MSBfirst=True
                )
                all_timings.extend(segment_timings)

            # Footer
            all_timings.append(kMideaBitMark)
            all_timings.append(kMideaMinGap)

            # Invert the data for the 2nd phase of the message
            data = ~data & ((1 << nbits) - 1)

    return all_timings


## Class for handling detailed Midea A/C messages.
## Direct translation from C++ IRMideaAC class (ir_Midea.h lines 175-274)
class IRMideaAC:
    ## Class Constructor
    def __init__(self) -> None:
        self._: MideaProtocol = MideaProtocol()
        self._CleanToggle = False
        self._EconoToggle = False
        self._8CHeatToggle = False
        self._LightToggle = False
        self._Quiet = False
        self._Quiet_prev = False
        self._SwingVToggle = False
        self._TurboToggle = False
        self.stateReset()

    ## Reset the state of the remote to a known good state/sequence.
    ## Direct translation from ir_Midea.cpp lines 101-114
    def stateReset(self) -> None:
        # Power On, Mode Auto, Fan Auto, Temp = 25C/77F
        self._.remote_state = 0xA1826FFFFF62
        self._CleanToggle = False
        self._EconoToggle = False
        self._8CHeatToggle = False
        self._LightToggle = False
        self._Quiet = self._Quiet_prev = False
        self._SwingVToggle = False
        self._TurboToggle = False

    ## Calculate the checksum for a given state.
    ## Direct translation from ir_Midea.cpp lines 502-512
    @staticmethod
    def calcChecksum(state: int) -> int:
        sum_val = 0
        temp_state = state

        for i in range(5):
            temp_state >>= 8
            sum_val += reverseBits((temp_state & 0xFF), 8)
        sum_val = 256 - sum_val
        return reverseBits(sum_val & 0xFF, 8)

    ## Verify the checksum is valid for a given state.
    ## Direct translation from ir_Midea.cpp lines 517-519
    @staticmethod
    def validChecksum(state: int) -> bool:
        return GETBITS64(state, 0, 8) == IRMideaAC.calcChecksum(state)

    ## Calculate & set the checksum for the current internal state.
    ## Direct translation from ir_Midea.cpp lines 522-525
    def checksum(self) -> None:
        self._.Sum = self.calcChecksum(self._.remote_state)

    ## Set the requested power state of the A/C to on.
    ## Direct translation from ir_Midea.cpp line 170
    def on(self) -> None:
        self.setPower(True)

    ## Set the requested power state of the A/C to off.
    ## Direct translation from ir_Midea.cpp line 173
    def off(self) -> None:
        self.setPower(False)

    ## Change the power setting.
    ## Direct translation from ir_Midea.cpp lines 177-179
    def setPower(self, on: bool) -> None:
        self._.Power = on

    ## Get the value of the current power setting.
    ## Direct translation from ir_Midea.cpp lines 183-185
    def getPower(self) -> bool:
        return bool(self._.Power)

    ## Is the device currently using Celsius or the Fahrenheit temp scale?
    ## Direct translation from ir_Midea.cpp lines 189-191
    def getUseCelsius(self) -> bool:
        return not bool(self._.useFahrenheit)

    ## Set the A/C unit to use Celsius natively.
    ## Direct translation from ir_Midea.cpp lines 195-201
    def setUseCelsius(self, on: bool) -> None:
        if on == bool(self._.useFahrenheit):  # We need to change
            native_temp = self.getTemp(not on)  # Get the old native temp
            self._.useFahrenheit = not on  # Cleared is on
            self.setTemp(native_temp, not on)  # Reset temp using the old native temp

    ## Set the temperature.
    ## Direct translation from ir_Midea.cpp lines 206-222
    def setTemp(self, temp: int, useCelsius: bool = False) -> None:
        max_temp = kMideaACMaxTempF
        min_temp = kMideaACMinTempF
        if useCelsius:
            max_temp = kMideaACMaxTempC
            min_temp = kMideaACMinTempC
        new_temp = min(max_temp, max(min_temp, temp))
        if not self._.useFahrenheit and not useCelsius:  # Native is in C, new_temp is in F
            new_temp = int(fahrenheitToCelsius(new_temp)) - kMideaACMinTempC
        elif self._.useFahrenheit and useCelsius:  # Native is in F, new_temp is in C
            new_temp = int(celsiusToFahrenheit(new_temp)) - kMideaACMinTempF
        else:  # Native and desired are the same units
            new_temp -= min_temp
        # Set the actual data
        self._.Temp = new_temp

    ## Get the current temperature setting.
    ## Direct translation from ir_Midea.cpp lines 227-236
    def getTemp(self, celsius: bool = False) -> int:
        temp = self._.Temp
        if not self._.useFahrenheit:
            temp += kMideaACMinTempC
        else:
            temp += kMideaACMinTempF
        if celsius and self._.useFahrenheit:
            temp = int(fahrenheitToCelsius(temp) + 0.5)
        if not celsius and not self._.useFahrenheit:
            temp = int(celsiusToFahrenheit(temp))
        return temp

    ## Set the Sensor temperature.
    ## Direct translation from ir_Midea.cpp lines 242-259
    def setSensorTemp(self, temp: int, useCelsius: bool = False) -> None:
        max_temp = kMideaACMaxSensorTempF
        min_temp = kMideaACMinSensorTempF
        if useCelsius:
            max_temp = kMideaACMaxSensorTempC
            min_temp = kMideaACMinSensorTempC
        new_temp = min(max_temp, max(min_temp, temp))
        if not self._.useFahrenheit and not useCelsius:  # Native is in C, new_temp is in F
            new_temp = int(fahrenheitToCelsius(new_temp)) - kMideaACMinSensorTempC
        elif self._.useFahrenheit and useCelsius:  # Native is in F, new_temp is in C
            new_temp = int(celsiusToFahrenheit(new_temp)) - kMideaACMinSensorTempF
        else:  # Native and desired are the same units
            new_temp -= min_temp
        # Set the actual data
        self._.SensorTemp = new_temp + 1
        self.setEnableSensorTemp(True)

    ## Get the current Sensor temperature setting.
    ## Direct translation from ir_Midea.cpp lines 265-274
    def getSensorTemp(self, celsius: bool = False) -> int:
        temp = self._.SensorTemp - 1
        if not self._.useFahrenheit:
            temp += kMideaACMinSensorTempC
        else:
            temp += kMideaACMinSensorTempF
        if celsius and self._.useFahrenheit:
            temp = int(fahrenheitToCelsius(temp) + 0.5)
        if not celsius and not self._.useFahrenheit:
            temp = int(celsiusToFahrenheit(temp))
        return temp

    ## Get the message type setting of the A/C message.
    ## Direct translation from ir_Midea.cpp line 529
    def getType(self) -> int:
        return self._.Type

    ## Set the message type setting of the A/C message.
    ## Direct translation from ir_Midea.cpp lines 533-545
    def setType(self, setting: int) -> None:
        if setting == kMideaACTypeFollow:
            self._.BeepDisable = False
            self._.Type = setting
        elif setting == kMideaACTypeSpecial:
            self._.Type = setting
        else:
            self._.Type = kMideaACTypeCommand
            self._.BeepDisable = True

    ## Enable the remote's Sensor temperature.
    ## Direct translation from ir_Midea.cpp lines 279-287
    def setEnableSensorTemp(self, on: bool) -> None:
        self._.disableSensor = not on
        if on:
            self.setType(kMideaACTypeFollow)
        else:
            self.setType(kMideaACTypeCommand)
            self._.SensorTemp = kMideaACSensorTempOnTimerOff  # Apply special value if off

    ## Is the remote temperature sensor enabled?
    ## Direct translation from ir_Midea.cpp line 292
    def getEnableSensorTemp(self) -> bool:
        return not bool(self._.disableSensor)

    ## Set the speed of the fan.
    ## Direct translation from ir_Midea.cpp lines 296-298
    def setFan(self, fan: int) -> None:
        self._.Fan = kMideaACFanAuto if (fan > kMideaACFanHigh) else fan

    ## Get the current fan speed setting.
    ## Direct translation from ir_Midea.cpp lines 302-304
    def getFan(self) -> int:
        return self._.Fan

    ## Get the operating mode setting of the A/C.
    ## Direct translation from ir_Midea.cpp lines 308-310
    def getMode(self) -> int:
        return self._.Mode

    ## Set the operating mode of the A/C.
    ## Direct translation from ir_Midea.cpp lines 314-326
    def setMode(self, mode: int) -> None:
        if mode in [kMideaACAuto, kMideaACCool, kMideaACHeat, kMideaACDry, kMideaACFan]:
            self._.Mode = mode
        else:
            self._.Mode = kMideaACAuto

    ## Set the Sleep setting of the A/C.
    ## Direct translation from ir_Midea.cpp lines 330-332
    def setSleep(self, on: bool) -> None:
        self._.Sleep = on

    ## Get the Sleep setting of the A/C.
    ## Direct translation from ir_Midea.cpp lines 336-338
    def getSleep(self) -> bool:
        return bool(self._.Sleep)

    ## Set the A/C to toggle the vertical swing toggle for the next send.
    ## Direct translation from ir_Midea.cpp line 343
    def setSwingVToggle(self, on: bool) -> None:
        self._SwingVToggle = on

    ## Is the current state a vertical swing toggle message?
    ## Direct translation from ir_Midea.cpp lines 348-350
    def isSwingVToggle(self) -> bool:
        return self._.remote_state == kMideaACToggleSwingV

    ## Get the vertical swing toggle state of the A/C.
    ## Direct translation from ir_Midea.cpp lines 355-358
    def getSwingVToggle(self) -> bool:
        self._SwingVToggle |= self.isSwingVToggle()
        return self._SwingVToggle

    ## Set the A/C to toggle the Econo (energy saver) mode for the next send.
    ## Direct translation from ir_Midea.cpp line 381
    def setEconoToggle(self, on: bool) -> None:
        self._EconoToggle = on

    ## Is the current state an Econo (energy saver) toggle message?
    ## Direct translation from ir_Midea.cpp lines 385-387
    def isEconoToggle(self) -> bool:
        return self._.remote_state == kMideaACToggleEcono

    ## Get the Econo (energy saver) toggle state of the A/C.
    ## Direct translation from ir_Midea.cpp lines 391-394
    def getEconoToggle(self) -> bool:
        self._EconoToggle |= self.isEconoToggle()
        return self._EconoToggle

    ## Set the A/C to toggle the Turbo mode for the next send.
    ## Direct translation from ir_Midea.cpp line 398
    def setTurboToggle(self, on: bool) -> None:
        self._TurboToggle = on

    ## Is the current state a Turbo toggle message?
    ## Direct translation from ir_Midea.cpp lines 402-404
    def isTurboToggle(self) -> bool:
        return self._.remote_state == kMideaACToggleTurbo

    ## Get the Turbo toggle state of the A/C.
    ## Direct translation from ir_Midea.cpp lines 408-411
    def getTurboToggle(self) -> bool:
        self._TurboToggle |= self.isTurboToggle()
        return self._TurboToggle

    ## Set the A/C to toggle the Light (LED) mode for the next send.
    ## Direct translation from ir_Midea.cpp line 415
    def setLightToggle(self, on: bool) -> None:
        self._LightToggle = on

    ## Is the current state a Light (LED) toggle message?
    ## Direct translation from ir_Midea.cpp lines 419-421
    def isLightToggle(self) -> bool:
        return self._.remote_state == kMideaACToggleLight

    ## Get the Light (LED) toggle state of the A/C.
    ## Direct translation from ir_Midea.cpp lines 425-428
    def getLightToggle(self) -> bool:
        self._LightToggle |= self.isLightToggle()
        return self._LightToggle

    ## Is the current state a Self-Clean toggle message?
    ## Direct translation from ir_Midea.cpp lines 432-434
    def isCleanToggle(self) -> bool:
        return self._.remote_state == kMideaACToggleSelfClean

    ## Set the A/C to toggle the Self Clean mode for the next send.
    ## Direct translation from ir_Midea.cpp lines 439-441
    def setCleanToggle(self, on: bool) -> None:
        self._CleanToggle = on and self.getMode() <= kMideaACAuto

    ## Get the Self-Clean toggle state of the A/C.
    ## Direct translation from ir_Midea.cpp lines 445-448
    def getCleanToggle(self) -> bool:
        self._CleanToggle |= self.isCleanToggle()
        return self._CleanToggle

    ## Is the current state a 8C Heat (Freeze Protect) toggle message?
    ## Direct translation from ir_Midea.cpp lines 453-455
    def is8CHeatToggle(self) -> bool:
        return self._.remote_state == kMideaACToggle8CHeat

    ## Set the A/C to toggle the 8C Heat (Freeze Protect) mode for the next send.
    ## Direct translation from ir_Midea.cpp lines 460-462
    def set8CHeatToggle(self, on: bool) -> None:
        self._8CHeatToggle = on and self.getMode() == kMideaACHeat

    ## Get the 8C Heat (Freeze Protect) toggle state of the A/C.
    ## Direct translation from ir_Midea.cpp lines 466-469
    def get8CHeatToggle(self) -> bool:
        self._8CHeatToggle |= self.is8CHeatToggle()
        return self._8CHeatToggle

    ## Is the current state a Quiet(Silent) message?
    ## Direct translation from ir_Midea.cpp lines 473-476
    def isQuiet(self) -> bool:
        return (self._.remote_state == kMideaACQuietOff or
                self._.remote_state == kMideaACQuietOn)

    ## Set the Quiet (Silent) mode for the next send.
    ## Direct translation from ir_Midea.cpp line 480
    def setQuiet(self, on: bool) -> None:
        self._Quiet = on

    ## Get the Quiet (Silent) mode state of the A/C.
    ## Direct translation from ir_Midea.cpp lines 492-497
    def getQuiet(self) -> bool:
        if self.isQuiet():
            return self._.remote_state == kMideaACQuietOn
        else:
            return self._Quiet

    ## Is the OnTimer enabled?
    ## Direct translation from ir_Midea.cpp lines 549-552
    def isOnTimerEnabled(self) -> bool:
        return (self.getType() == kMideaACTypeCommand and
                self._.SensorTemp != kMideaACSensorTempOnTimerOff)

    ## Get the value of the OnTimer is currently set to.
    ## Direct translation from ir_Midea.cpp lines 556-558
    def getOnTimer(self) -> int:
        return (self._.SensorTemp >> 1) * 30 + 30

    ## Set the value of the On Timer.
    ## Direct translation from ir_Midea.cpp lines 567-574
    def setOnTimer(self, mins: int) -> None:
        self.setEnableSensorTemp(False)
        halfhours = min(24 * 60, mins) // 30
        if halfhours:
            self._.SensorTemp = ((halfhours - 1) << 1) | 1
        else:
            self._.SensorTemp = kMideaACSensorTempOnTimerOff

    ## Is the OffTimer enabled?
    ## Direct translation from ir_Midea.cpp lines 578-580
    def isOffTimerEnabled(self) -> bool:
        return self._.OffTimer != kMideaACTimerOff

    ## Get the value of the OffTimer is currently set to.
    ## Direct translation from ir_Midea.cpp line 584
    def getOffTimer(self) -> int:
        return self._.OffTimer * 30 + 30

    ## Set the value of the Off Timer.
    ## Direct translation from ir_Midea.cpp lines 591-597
    def setOffTimer(self, mins: int) -> None:
        halfhours = min(24 * 60, mins) // 30
        if halfhours:
            self._.OffTimer = halfhours - 1
        else:
            self._.OffTimer = kMideaACTimerOff

    ## Get a copy of the internal state/code for this protocol.
    ## Direct translation from ir_Midea.cpp lines 160-163
    def getRaw(self) -> int:
        self.checksum()  # Ensure correct checksum before sending
        return self._.remote_state

    ## Set the internal state from a valid code for this protocol.
    ## Direct translation from ir_Midea.cpp line 167
    def setRaw(self, newState: int) -> None:
        self._.remote_state = newState


## Decode the supplied Midea message.
## Status: Alpha / Needs testing against a real device.
## Direct translation from IRremoteESP8266 IRrecv::decodeMidea (ir_Midea.cpp lines 756-808)
def decodeMidea(results, offset: int = 1, nbits: int = kMideaBits,
                strict: bool = True, _tolerance: int = 25) -> bool:
    """
    Decode a Midea IR message.
    EXACT translation from IRremoteESP8266 IRrecv::decodeMidea
    """
    from app.core.ir_protocols.ir_recv import kHeader, kFooter, kMarkExcess, _matchGeneric

    min_nr_of_messages = 1
    if strict:
        if nbits != kMideaBits:
            return False  # Not strictly a MIDEA message
        min_nr_of_messages = 2

    # The protocol sends the data normal + inverted, alternating on
    # each byte. Hence twice the number of expected data bits.
    if results.rawlen < min_nr_of_messages * (2 * nbits + kHeader + kFooter) - 1 + offset:
        return False  # Can't possibly be a valid MIDEA message

    data = 0
    inverted = 0

    if nbits > 64:
        return False  # We can't possibly capture a Midea packet that big

    for i in range(min_nr_of_messages):
        # Match Header + Data + Footer
        result_ptr = inverted if (i % 2) else data
        used = _matchGeneric(
            data_ptr=results.rawbuf[offset:],
            result_bits_ptr=result_ptr if isinstance(result_ptr, list) else None,
            result_bytes_ptr=None,
            use_bits=True,
            remaining=results.rawlen - offset,
            nbits=nbits,
            hdrmark=kMideaHdrMark,
            hdrspace=kMideaHdrSpace,
            onemark=kMideaBitMark,
            onespace=kMideaOneSpace,
            zeromark=kMideaBitMark,
            zerospace=kMideaZeroSpace,
            footermark=kMideaBitMark,
            footerspace=kMideaMinGap,
            atleast=(i % 2 == 1),  # No "atleast" on 1st part, but yes on the 2nd
            tolerance=_tolerance,
            excess=kMarkExcess,
            MSBfirst=True
        )
        if used == 0:
            return False
        offset += used
        # Store the result
        if i % 2:
            inverted = result_ptr if isinstance(result_ptr, int) else 0
        else:
            data = result_ptr if isinstance(result_ptr, int) else 0

    # Compliance
    if strict:
        # Protocol requires a second message with all the data bits inverted
        mask = (1 << kMideaBits) - 1
        if (data & mask) != ((inverted ^ mask) & mask):
            return False
        if not IRMideaAC.validChecksum(data):
            return False

    # Success
    results.bits = nbits
    results.value = data
    results.address = 0
    results.command = 0
    return True


## Send a Midea24 formatted message.
## Status: STABLE / Confirmed working on a real device.
## Direct translation from IRremoteESP8266 IRsend::sendMidea24 (ir_Midea.cpp lines 822-833)
def sendMidea24(data: int, nbits: int = kMidea24Bits, repeat: int = 0) -> List[int]:
    """
    Send a Midea24 formatted message (48-bit NEC with inverted byte pairs).
    EXACT translation from IRremoteESP8266 IRsend::sendMidea24

    Returns timing array instead of transmitting via hardware.
    """
    # Construct the data into byte & inverted byte pairs
    newdata = 0
    for i in range(nbits - 8, -1, -8):
        # Shuffle the data to be sent so far
        newdata <<= 16
        next_byte = GETBITS64(data, i, 8)
        newdata |= ((next_byte << 8) | (next_byte ^ 0xFF))

    # Use NEC protocol for sending
    from app.core.ir_protocols.nec import sendNEC
    return sendNEC(newdata, nbits * 2, repeat)


## Decode the supplied Midea24 message.
## Status: STABLE / Confirmed working on a real device.
## Direct translation from IRremoteESP8266 IRrecv::decodeMidea24 (ir_Midea.cpp lines 849-885)
def decodeMidea24(results, offset: int = 1, nbits: int = kMidea24Bits,
                  strict: bool = True, _tolerance: int = 25) -> bool:
    """
    Decode a Midea24 IR message (48-bit NEC with inverted byte pairs).
    EXACT translation from IRremoteESP8266 IRrecv::decodeMidea24
    """
    from app.core.ir_protocols.ir_recv import kMarkExcess, _matchGeneric

    # Not strictly a MIDEA24 message
    if strict and nbits != kMidea24Bits:
        return False
    if nbits > 32:
        return False  # Can't successfully match something that big

    # NEC timing values (from ir_NEC.cpp)
    kNecHdrMark = 9000
    kNecHdrSpace = 4500
    kNecBitMark = 560
    kNecOneSpace = 1690
    kNecZeroSpace = 560

    longdata = 0
    used = _matchGeneric(
        data_ptr=results.rawbuf[offset:],
        result_bits_ptr=[longdata],
        result_bytes_ptr=None,
        use_bits=True,
        remaining=results.rawlen - offset,
        nbits=nbits * 2,
        hdrmark=kNecHdrMark,
        hdrspace=kNecHdrSpace,
        onemark=kNecBitMark,
        onespace=kNecOneSpace,
        zeromark=kNecBitMark,
        zerospace=kNecZeroSpace,
        footermark=kNecBitMark,
        footerspace=kMidea24MinGap,
        atleast=True,
        tolerance=_tolerance,
        excess=kMarkExcess,
        MSBfirst=True
    )
    if used == 0:
        return False
    longdata = longdata if isinstance(longdata, int) else 0

    # Build the result by checking every second byte is a complement(inversion)
    # of the previous one
    data = 0
    i = nbits * 2
    while i >= 16:
        # Shuffle the data collected so far
        data <<= 8
        i -= 8
        current = GETBITS64(longdata, i, 8)
        i -= 8
        next_byte = GETBITS64(longdata, i, 8)
        # Check they are an inverted pair
        if current != (next_byte ^ 0xFF):
            return False  # They are not, so abort
        data |= current

    # Success
    results.bits = nbits
    results.value = data
    results.address = 0
    results.command = 0
    return True
